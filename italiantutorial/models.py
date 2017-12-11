from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import time
import datetime
from radiogrid import RadioGridField

author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'italiantutorial'
    players_per_group = None
    num_rounds = 1
    lower_bound = 30
    upper_bound = 101
    step = 5
    offer_range = list(range(lower_bound, upper_bound, step))

COMMON_ROWS = (
    (1, "Se un lavoratore è disoccupato in un dato round, non guadagnerà niente."),
    (2, "Se un datore di lavoro non è riuscito ad assumere un lavoratore in un dato round, "
        "il datore non guadagnerà niente."),
    (3, "Accettando un'offerta, il lavoratore si impegna a lavorare per quel datore di lavoro per quel round."),
    (4, "Un datore di lavoro che ha assunto qualcuno ottiene 40 punti."),
    (5, "In generale, il salario viene dedotto dal guadagno del datore di lavoro e dato al lavoratore."),
    (6, "Il numero di compiti che il lavoratore può svolgere è illimitato."),
    (7, "I lavoratori ottengono un salario più alto se portano a termine un maggior numero di compiti."),
    (8, "Oltre al lavoratore, solo il datore di lavoro viene a conoscenza del numero di compiti "
        "che il lavoratore ha tentato e completato correttamente."),
    (9, "Verrai ricompensato per tutti e 8 i round."),
)

DIRECT_ROWS = (
    (10, "Ci sono sempre dei lavoratori disoccupati."),
)

INDIRECT_ROWS = (
    (10, "I datori di lavoro possono cambiare il salario offerto dopo la fase di assunzione."),
)

NO_TAXES_ROWS = (
    (11, "Il tuo guadagno dipende dalle tue decisioni e da quelle degli altri partecipanti."),
    (12, "Il guadagno in un dato round non può essere negativo."),
)
EMPLOYER_TAX_ROWS = (
    (11,
     "Il 20 % di 20 punti equivale a 4 punti. Quindi, quando abbiamo una tassa sui ricavi del datore di lavoro, "
     "il guadagno per ogni compito è 16 invece di 20 punti."),
    (12, "Il guadagno di un dato round non può essere negativo."),
)
WORKER_TAX_ROWS = (
    (11, "Il guadagno di un datore di lavoro in un dato round può essere negativo."),
    (12, "La tassa sul reddito del lavoratore è sempre di 20 punti."),
)
ALL_TAXES_ROWS = (
    (11, "Il 20 % di 20 punti equivale a 4 punti. Quindi, quando abbiamo una tassa sui ricavi del datore di lavoro, "
         "il guadagno per ogni compito è 16 invece di 20 punti."),
    (12, "La tassa sul reddito del lavoratore è sempre di 20 punti."),
)

VALUES = (
    (1, "Vero"),
    (2, "Falso"),
)
########################################################################################################################
########################################################################################################################
########################################################################################################################
ROWSS = COMMON_ROWS + DIRECT_ROWS + NO_TAXES_ROWS
########################################################################################################################
########################################################################################################################
########################################################################################################################
class Subsession(BaseSubsession):
    def creating_session(self):
        if self.session.config['timeline'] == "direct":
            for p in self.get_players():
                p.timeline = "direct"
                if self.session.config['treatment'] == "no_taxes":
                    p.treatment = "no_taxes"
                    for g in self.get_groups():
                        g.rows = COMMON_ROWS + DIRECT_ROWS + NO_TAXES_ROWS
                elif self.session.config['treatment'] == "worker_tax":
                    p.treatment = "worker_tax"
                    for g in self.get_groups():
                        g.rows = COMMON_ROWS + DIRECT_ROWS + WORKER_TAX_ROWS
                elif self.session.config['treatment'] == "employer_tax":
                    p.treatment = "employer_tax"
                    for g in self.get_groups():
                        g.rows = COMMON_ROWS + DIRECT_ROWS + EMPLOYER_TAX_ROWS
                elif self.session.config['treatment'] == "all_taxes":
                    p.treatment = "all_taxes"
                    for g in self.get_groups():
                        g.rows = COMMON_ROWS + DIRECT_ROWS + ALL_TAXES_ROWS
        elif self.session.config['timeline'] == "wage":
            for p in self.get_players():
                p.timeline = "indirect"
                if self.session.config['treatment'] == "no_taxes":
                    p.treatment = "no_taxes"
                    for g in self.get_groups():
                        g.rows = COMMON_ROWS + INDIRECT_ROWS + NO_TAXES_ROWS
                elif self.session.config['treatment'] == "worker_tax":
                    p.treatment = "worker_tax"
                    for g in self.get_groups():
                        g.rows = COMMON_ROWS + INDIRECT_ROWS + WORKER_TAX_ROWS
                elif self.session.config['treatment'] == "employer_tax":
                    p.treatment = "employer_tax"
                    for g in self.get_groups():
                        g.rows = COMMON_ROWS + INDIRECT_ROWS + EMPLOYER_TAX_ROWS
                elif self.session.config['treatment'] == "all_taxes":
                    p.treatment = "all_taxes"
                    for g in self.get_groups():
                        g.rows = COMMON_ROWS + INDIRECT_ROWS + ALL_TAXES_ROWS

    def vars_for_admin_report(self):
        total_payoffs = sorted([p.total_payoff for p in self.get_players()])
        return {'total_payoffs_in_eur': total_payoffs}

class Group(BaseGroup):
    rows = models.CharField()


class Player(BasePlayer):

    treatment = models.CharField()
    timeline = models.CharField()
    auctionenddate = models.FloatField()
    wage_offer = models.PositiveIntegerField()
    last_correct_answer = models.IntegerField()
    tasks_correct = models.IntegerField(default=0)
    tasks_attempted = models.IntegerField(default=0)
    ROWS = models.CharField(default=ROWSS)
    # THIS HAS TO BE CHANGED MANUALLY ### - MAKE A THING THAT ERRORS IF NOT THE CASE!
    trueorfalse = RadioGridField(rows=ROWSS, values=VALUES, require_all_fields=True,
                             verbose_name='Vero o falso?', )

    def time_left(self):
        now = time.time()
        time_left = self.auctionenddate - now
        time_left = round(time_left) if time_left > 0 else 0
        return time_left
