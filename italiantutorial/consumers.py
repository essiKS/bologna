from .models import Player, Subsession, ROWSS, Constants
import json
from random import randint
import time


def slicelist(l,n):
    return [l[i:i + n] for i in range(0,len(l),n)]


def get_random_list():
    random_upper_boundary = randint(50, 99)
    max_len=100
    return [randint(10, random_upper_boundary) for i in range(max_len)]


def get_task():
    string_len = 10
    listx = get_random_list()
    listy = get_random_list()
    answer = max(listx) + max(listy)
    listx = slicelist(listx, string_len)
    listy = slicelist(listy, string_len)
    return {
        "mat1": listx,
        "mat2": listy,
        "correct_answer": answer,
    }


def tut_work_connect(message, worker_code, player_pk):
    print('worker connected')
    new_task = get_task()
    player = Player.objects.get(participant__code__exact=worker_code, pk=player_pk)
    player.last_correct_answer = new_task['correct_answer']
    player.save()
    message.reply_channel.send({'text': json.dumps(new_task)})


def tut_work_disconnect(message, worker_code, player_pk):
    print('worker disconnected')


def tut_work_message(message, worker_code, player_pk):
    print('TASK: ', get_task())
    jsonmessage = json.loads(message.content['text'])
    answer = jsonmessage.get('answer')
    player = Player.objects.get(participant__code__exact=worker_code, pk=player_pk)
    player.tasks_attempted += 1
    if int(answer) == int(player.last_correct_answer):
        player.tasks_correct += 1
        feedback = "La precedente risposta era corretta."
    else:
        feedback = "La precedente risposta " + str(answer) + " era sbagliata, la risposta corretta era " + str(player.last_correct_answer) + "."
    new_task = get_task()
    new_task['tasks_correct'] = player.tasks_correct
    new_task['tasks_attempted'] = player.tasks_attempted
    new_task['feedback'] = feedback
    player.last_correct_answer = new_task['correct_answer']
    player.save()
    time.sleep(0.01)
    if int(new_task['tasks_attempted']) < Constants.max_task_amount:
        message.reply_channel.send({'text': json.dumps(new_task)})
    if int(new_task['tasks_attempted']) >= Constants.max_task_amount:
        new_task['task_over'] = True
        message.reply_channel.send({'text': json.dumps(new_task)})

def big_connect(message, participant_code):
    print('connected')


def big_message(message, participant_code):
    jsonmessage = json.loads(message.content['text'])
    print("json:::", jsonmessage)

    dictionary = jsonmessage['answers']
    answer_vector = []
    x = 0
    for i in range(0, len(ROWSS)):
        try:
            answer_vector.append(dictionary[str(i)])
        except KeyError:
            answer_vector.append("0")
            x += 1
    print('ANSWERS;;;::', answer_vector, jsonmessage['answers'])
    if answer_vector == ['2', '1', '1', '1', '1', '2', '2', '1', '2', '1', '1', '2']:
        text = "Correct"
        message.reply_channel.send({'text': json.dumps(text)})
    elif x == 0:
        text = "Incorrect"
        message.reply_channel.send({'text': json.dumps(text)})
        feedback = []
        if answer_vector[0] == '1' or answer_vector[1] == '2':
            feedback.append("Se il partecipante non ha un contratto in un round, il suo payoff è il seguente: "
                            "Il payoff del datore di lavoro è di 0 punti, quello del lavoratore è di 20 punti")
        if answer_vector[2] == '2':
            feedback.append("<br> Accettare un'offerta di un datore di lavoro significa che il lavoratore lavorerà "
                            "per quel datore per questo round")
        if answer_vector[3] == '2' or answer_vector[4] == '2':
            feedback.append("<br> Generalmente, quando assume qualcuno, il datore di lavoro ottiene 40 punti. "
                            "A questi va tolto il salario dovuto al lavoratore, ed aggiunto il guadagno"
                            " proveniente dal lavoro del'assunto. Il guadagno di un lavoratore assunto, "
                            "invece, consiste nel suo salario")
        if answer_vector[5] == '1':
            feedback.append("<br> Un lavoratore può provare a completare un massimo di 10 compiti in 5 minuti")
        if answer_vector[6] == '1':
            feedback.append("<br> Il salario non dipende dal risultato del lavoro")
        if answer_vector[7] == '2':
            feedback.append("<br> Mentre i risultati (aggregati) della fase di assunzione sono pubblici, "
                            "i risultati della prestazione individuale sono resi noti solamente al rispettivo "
                            "lavoratore e datore di lavoro")
        if answer_vector[8] == '1':
            feedback.append("<br> L'ammontare del tuo premio verrà determinato solo alla fine dell'esperimento: "
                            "verranno scelti 2 round su 8 (casualmente) e sarai ricompensato per questi solamente")
        # next rounds depend on the treatment.
        player = Player.objects.get(participant__code__exact=participant_code)
        if answer_vector[9] == '2':
            if player.timeline == 'direct':
                feedback.append("<br> In ogni round ci sono almeno due lavoratori disoccupati")
            else:
                feedback.append("<br> I datori di lavoro possono cambiare il salario offerto dopo la fase di assunzione")
        if answer_vector[10] == '2':
            if player.treatment == 'employer_tax' or player.treatment == 'all_taxes':
                feedback.append("<br> Quando c'è una tassa sui ricavi del datore di lavoro, il suo guadagno è "
                                "di 16 punti per compito corretto, i 4 punti (20 % di 20) vanno in tasse") ##maybe rephrase?
            elif player.treatment == 'no_taxes':
                feedback.append("<br> Il tuo guadagno e quello degli altri dipendono dalle tue azioni")
            elif player.treatment == 'worker_tax':
                feedback.append("<br> Il guadagno di un datore di lavoro può essere negativo")
        if answer_vector[11] == '1':
            if player.treatment == 'worker_tax' or player.treatment == 'all_taxes':
                feedback.append("<br> La tassa sul reddito del lavoratore è del 20 % ed il suo ammontare finale dipende "
                                "dal salario: il 20 % di 30 punti equivale a 6 punti, il 20 % di 65 punti è 13 punti "
                                "e il 20 % di 100 punti è 20 punti")
            if player.treatment == 'no_taxes' or player.treatment == 'employer_tax':
                feedback.append("<br> Il guadagno di un datore di lavoro può essere negativo")
        print(feedback)
        message.reply_channel.send({'text': json.dumps(feedback)})
    else:
        text = "Incomplete"


def big_disconnect(message, participant_code):
    print('disconnected')