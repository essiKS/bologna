from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random
from django import forms
import time
import datetime
from django.core.exceptions import ObjectDoesNotExist

from django.db import models as djmodels

author = 'Essi Kujansuu, EUI, essi.kujansuu@eui.eu, adapting work of Philipp Chapkovski, UZH, chapkovski@gmail.com'

doc = """
Adaptation of Fehr et al. 1993 auction.
"""

class Constants(BaseConstants):
    name_in_url = 'wageauction'
    players_per_group = 12
    num_rounds = 8
    starting_time = 120
    num_employers = 5
    num_workers = players_per_group - num_employers
    task_time = 300
    lower_bound = 30
    upper_bound = 101
    step = 5
    offer_range = list(range(lower_bound, upper_bound, step))
    max_task_amount = 10



class Subsession(BaseSubsession):
    def creating_session(self):
        taxes = [1, 2, 1, 3, 3, 1, 1, 1]
        tax_outcome = taxes[self.round_number - 1]
        if 'treatment' in self.session.config:
            if self.session.config['treatment'] == "no_taxes":
                tax_outcome = 1
                for p in self.get_players():
                    p.treatment = "no_taxes"
            if self.session.config['treatment'] == "worker_tax":
                if tax_outcome == 2:
                    tax_outcome = 3
                    for p in self.get_players():
                        p.treatment = "worker_tax"
            if self.session.config['treatment'] == "employer_tax":
                if tax_outcome == 3:
                    tax_outcome = 2
                    for p in self.get_players():
                        p.treatment = "employer_tax"
        for p in self.get_players():
            p.tax_outcome = tax_outcome
        for g in self.get_groups():
            g.num_contracts_closed = 0
        if self.round_number == 1:
            paying_rounds = random.sample(range(1, Constants.num_rounds), 2)
            self.session.vars['paying_rounds'] = paying_rounds
            random_list = random.sample(range(1, Constants.players_per_group), Constants.num_employers)
            self.session.vars['roles'] = random_list

    def vars_for_admin_report(self):
        total_payoffs = sorted([p.total_payoff for p in self.get_players()])
        return {'total_payoffs_in_eur': total_payoffs}


class Group(BaseGroup):
    auctionenddate = models.FloatField()
    work_end_date = models.FloatField()
    num_contracts_closed = models.IntegerField()
    day_over = models.BooleanField()
    last_message = models.CharField()
    wage_list = models.CharField()
    contracts_dump = models.CharField()

    def time_left(self):
            now = time.time()
            time_left = self.auctionenddate - now
            time_left = round(time_left) if time_left > 0 else 0
            return time_left

    def time_work(self):
            now = time.time()
            time_left = self.work_end_date - now
            time_left = round(time_left) if time_left > 0 else 0
            return time_left

    def set_pay(self):
        try:
            for person in self.get_players():
                if person.role() == 'employer':
                    if person.matched == 0:
                        person.pay = 0
                    else:
                        closed_contract = person.contract.get(accepted=True)
                        if person.tax_outcome == 2:
                            person.pay = 40 - closed_contract.amount_updated + 0.8 * 20 * closed_contract.tasks_corr
                        else:
                            person.pay = 40 - closed_contract.amount_updated + 20 * closed_contract.tasks_corr
                if person.role() == 'worker':
                    if person.matched == 0:
                        person.pay = 20
                    else:
                        try:
                            closed_contract = person.work_to_do.get(accepted=True)
                            if person.tax_outcome == 3:
                                person.pay = 0.8 * closed_contract.amount_updated
                            else:
                                person.pay = closed_contract.amount_updated
                        except ObjectDoesNotExist:
                            person.pay = 0

        # I don't know if this bit of code is necessary
        except TypeError:
            for person in self.get_players():
                person.pay = 0

    def set_payoffs(self):
        for person in self.get_players():
            for rounds in self.session.vars['paying_rounds']:
                if person.round_number == rounds:
                    person.payoff = person.pay


class Player(BasePlayer):
    treatment = models.CharField()
    wage_offer = models.IntegerField()
    tax_outcome = models.PositiveIntegerField()
    wage_adjustment = models.IntegerField()
    last_correct_answer = models.IntegerField()
    tasks_attempted = models.PositiveIntegerField(initial=0)
    tasks_correct = models.PositiveIntegerField(initial=0)
    matched = models.BooleanField()
    job_to_do_updated=models.BooleanField(initial=False)
    offers_dump = models.CharField()
    job_contract_dump = models.CharField()
    pay = models.CurrencyField()
    total_payoff = models.CurrencyField()

    def role(self):
        for each in self.session.vars['roles']:
            if self.id_in_group == each:
                return 'employer'
        if self.role != 'employer':
            return 'worker'


class Offer(djmodels.Model):
    employer = djmodels.ForeignKey(Player, related_name='offers')
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class JobContract(djmodels.Model):
    employer = djmodels.ForeignKey(Player, related_name='contract', unique=True)
    worker = djmodels.ForeignKey(Player, blank=True, null=True, related_name='work_to_do')
    amount = models.IntegerField()
    accepted = models.BooleanField()
    amount_updated = models.IntegerField(blank=True)
    tasks_corr = models.PositiveIntegerField(initial=0)
    tasks_att = models.PositiveIntegerField(initial=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    auctionenddate = models.FloatField()
    day_over = models.BooleanField()