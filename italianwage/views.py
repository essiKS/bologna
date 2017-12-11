from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants, Group, Subsession, JobContract
import time


# HELPFUL PAGE TYPES
class EmployerPage(Page):
    def is_displayed(self):
        return self.player.role() == 'employer' and self.extra_is_displayed()

    def extra_is_displayed(self):
        return True


class WorkerPage(Page):
    def is_displayed(self):
        return self.player.role() == 'worker' and self.extra_is_displayed()

    def extra_is_displayed(self):
        return True


class ActiveWorkerPage(Page):
    def is_displayed(self):
        return self.player.role() == 'worker' and self.player.matched and self.extra_is_displayed()

    def extra_is_displayed(self):
        return True


# ########### #THE REAL PAGES START HERE # ############# #
class Role(Page):
    def is_displayed(self):
        if self.subsession.round_number == 1:
            return True


class WP(WaitPage):
    title_text = "Attendere prego"
    body_text = "Un nuovo round sta per cominciare, per favore attendi gli altri partecipanti."

    wait_for_all_groups = True

    def after_all_players_arrive(self):
        for bunch in self.subsession.get_groups():
            bunch.auctionenddate = time.time() + Constants.starting_time + 5


class CountDown(Page):
    timeout_seconds = 5
    timer_text = "La prossima fase inizierà tra 5 secondi:  "


class Auction(EmployerPage):
    def extra_is_displayed(self):
        closed_contract = self.player.contract.filter(accepted=True).exists()
        return not any([self.group.day_over, closed_contract])

    def vars_for_template(self):
        active_contracts = JobContract.objects.filter(accepted=False, employer__group=self.group).values('pk', 'amount')
        return {'time_left': self.group.time_left(),
                'active_contracts': active_contracts,}

    def before_next_page(self):
        closed_contract = self.player.contract.filter(accepted=True)
        if closed_contract:
            self.player.wage_offer = closed_contract.first().amount
            self.player.matched = closed_contract
        else:
            self.player.matched = 0
        self.player.offers_dump = self.player.offers.values()


class Accept(WorkerPage):
    def extra_is_displayed(self):
        closed_contract = self.player.work_to_do.filter(accepted=True).exists()
        return not any([self.group.day_over, closed_contract])

    def vars_for_template(self):
        active_contracts = JobContract.objects.filter(accepted=False, employer__group=self.group).values('pk', 'amount')
        return {'time_left': self.group.time_left(),
                'active_contracts': active_contracts}

    def before_next_page(self):
        closed_contract = self.player.work_to_do.filter(accepted=True).exists()
        self.player.matched = closed_contract


class WPage(WaitPage):
    title_text = "Attendere prego"
    body_text = "La tua decisione è stata registrata... stiamo aspettando gli altri partecipanti."

    def after_all_players_arrive(self):
        for g in self.subsession.get_groups():
            wages = []
            for p in g.get_players():
                if g.get_player_by_id(p.id_in_group).wage_offer:
                    wages.append(g.get_player_by_id(p.id_in_group).wage_offer)
            g.wage_list = str(wages)[1:-1]



class AfterAuctionDecision(EmployerPage):
    def extra_is_displayed(self):
        if self.player.matched == 1:
            return True

    form_model = models.Player
    form_fields = ["wage_adjustment"]

    def before_next_page(self):
        closed_contract = self.player.contract.get(accepted=True)
        closed_contract.amount_updated = self.player.wage_offer + self.player.wage_adjustment
        closed_contract.save()
        closed_contract.worker.job_to_do_updated = True


class AuctionResultsWait(WaitPage):
    title_text = "Attendere prego"
    template_name = 'italianwage/AuctionResultsWait.html'
    wait_for_all_groups = True


class AuctionResultsEmployer(EmployerPage):
    def vars_for_template(self):
        if self.player.matched == 1:
            if self.player.role() == "employer":
                closed_contract = self.player.contract.get(accepted=True)
            return {'initial_wage': closed_contract.amount,
                    'final_wage': closed_contract.amount_updated,}
        # Something goes really wrong here if matched is missing the value.


class AuctionResultsWorker(WorkerPage):
    def vars_for_template(self):
        if self.player.matched == 1:
            if self.player.role() == "worker":
                closed_contract = self.player.work_to_do.get(accepted=True)
            return {'initial_wage': closed_contract.amount,
                    'final_wage': closed_contract.amount_updated, }


class Start(ActiveWorkerPage):
    pass


class WorkPage(ActiveWorkerPage):
    timer_text = "Tempo rimanente per completare questa parte:"
    timeout_seconds = Constants.task_time

    def vars_for_template(self):
        if self.player.matched == 1:
            if self.player.role() == "worker":
                closed_contract = self.player.work_to_do.get(accepted=True)
            elif self.player.role() == "employer":
                closed_contract = self.player.contract.get(accepted=True)
        return {'final_wage': closed_contract.amount_updated, }

    def before_next_page(self):
        closed_contract = self.player.work_to_do.get(accepted=True)
        closed_contract.tasks_corr = self.player.tasks_correct
        closed_contract.tasks_att = self.player.tasks_attempted
        closed_contract.save()
        self.group.work_end_date = time.time() + Constants.task_time


class WaitP(WaitPage):
    title_text = "Attendere prego"
    template_name = 'italianwage/WaitP.html'

    def vars_for_template(self):
        return {'time_left': self.group.time_work()}

    def after_all_players_arrive(self):
        self.group.set_pay()
        self.group.set_payoffs()


class Results(Page):
    def vars_for_template(self):
        if self.player.matched == 1:
            if self.player.role() == "employer":
                closed_contract = self.player.contract.get(accepted=True)
                worker_pk = closed_contract.worker
                partner_payoff = worker_pk.pay
                self.player.job_contract_dump = self.player.contract.values()
            if self.player.role() == "worker":
                closed_contract = self.player.work_to_do.get(accepted=True)
                employer_pk = closed_contract.employer
                partner_payoff = employer_pk.pay
                self.player.job_contract_dump = self.player.work_to_do.values()
            return {'initial_wage': closed_contract.amount,
                    'final_wage': closed_contract.amount_updated,
                    'tasks_attempted': closed_contract.tasks_att,
                    'tasks_correct': closed_contract.tasks_corr,
                    'partner_payoff': partner_payoff,}
        else:
            return {}


class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        self.player.total_payoff = 50
        for piar in self.player.in_all_rounds():
            self.player.total_payoff += piar.payoff
        rounds = self.session.vars['paying_rounds']
        rounds.sort()

        return {"paying_rounds": str(rounds)[1:-4],
                "last_round": str(rounds)[7:-1],
                'player_in_all_rounds': self.player.in_all_rounds(),
                'total_payoff': self.player.total_payoff,
                'in_euros': self.participant.payoff_plus_participation_fee()}


page_sequence = [
    Role,
    WP, CountDown,
    Auction, Accept,
    WPage,
    AfterAuctionDecision, AuctionResultsWait,
    AuctionResultsEmployer, AuctionResultsWorker,
    Start, WorkPage,
    WaitP,
    Results,
    FinalResults,
]
