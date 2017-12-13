from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)


author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'endsurvey'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.PositiveIntegerField(verbose_name="Età")
    # something wrong?!

    sex = models.PositiveIntegerField(verbose_name="Sesso",
    choices=[
        [1, "Uomo"],
        [2, "Donna"],
    ]
    , widget=widgets.RadioSelectHorizontal)
    year_of_study = models.PositiveIntegerField(verbose_name="Anno di Studio (0 se non sei uno studente, 1 se sei al primo anno di università etc)", min=0, max=15)
    area_of_study = models.CharField(verbose_name="Campo di studio (nessuno se non sei uno studente)")
    nationality = models.CharField(verbose_name="Nazionalità")
    tell_earnings = models.PositiveIntegerField(verbose_name="Hai intenzione di dire ad altre persone "
                                                     "(partecipanti) quanto hai guadagnato?", choices=[
        [1, "Sì"],
        [2, "No"],
    ],
                                                     widget=widgets.RadioSelectHorizontal)
    heard_before = models.PositiveIntegerField(verbose_name="Eri già a conoscenza di questo esperimento prima di "
                                                    "venire al laboratorio?", choices=[
        [1, "Sì"],
        [2, "No"],
    ],
                                                    widget=widgets.RadioSelectHorizontal)
    first_experiment = models.PositiveIntegerField(verbose_name="Avevi già partecipato a un esperimento in precedenza?",
                                                   choices=[
                                                       [1, "Sì"],
                                                       [2, "No"],
                                                   ], widget=widgets.RadioSelectHorizontal)
    similar_experiment = models.PositiveIntegerField(verbose_name="Avevi già partecipato ad un esperimento simile in precedenza?"
                                                     , choices=[
        [1, "Sì"],
        [2, "No"],
    ], widget=widgets.RadioSelectHorizontal)
