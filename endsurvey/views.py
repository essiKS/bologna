from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants, Player


class MyPage(Page):
    form_model = models.Player
    form_fields = [
        'age',
        'sex',
        'year_of_study',
        'area_of_study',
        'nationality',
        'tell_earnings',
        'heard_before',
        'first_experiment',
        'similar_experiment',
    ]



class Results(Page):
    def vars_for_template(self):
        return {"your_payoff": self.participant.payoff_plus_participation_fee()}


page_sequence = [
    MyPage,
    Results
]
