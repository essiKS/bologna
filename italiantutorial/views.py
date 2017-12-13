from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants, Player, Group
import time
import random


class Error(Page):
    def is_displayed(self):
        if self.player.ROWS == self.group.rows:
            return False
        else:
            return True


class Welcome0(Page):
    pass


class Welcome(Page):
    pass


class OverallStructure(Page):
    pass


class AllInstructions(Page):

    def vars_for_template(self):
        return {'default_page': 'hiring_stage'}

    def before_next_page(self):
        now = time.time()
        self.player.auctionenddate = now + 120


class AuctionTryOut(Page):
    form_model = models.Player
    form_fields = ["wage_offer"]

    def vars_for_template(self):
        return {'time_left': self.player.time_left()}


class AllInstructions2(Page):
    pass


class WorkTryOut(Page):
    timer_text = "Tempo rimanente per completare questa parte:"
    timeout_seconds = 300


class InstructionsWithQuestionnaire(Page):
    form_model = models.Player
    form_fields = ['trueorfalse']


class Results(Page):
    pass


page_sequence = [
    Error,
    Welcome0,
    Welcome,
    OverallStructure,
    AllInstructions,
    AuctionTryOut,
    AllInstructions2,
    WorkTryOut,
    InstructionsWithQuestionnaire,
    Results,
]
