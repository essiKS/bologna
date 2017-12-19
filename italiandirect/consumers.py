from channels import Group
from channels.sessions import channel_session
from .models import Group as OtreeGroup, JobContract, Player, Constants
import json
import time
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from random import randint

def dir_ws_connect(message, group_name):
    Group(group_name).add(message.reply_channel)


def get_contracts(group):
    contracts = {}
    active_contracts = list(
        JobContract.objects.filter(accepted=False, employer__group=group).values('pk', 'amount'))
    active_contracts = json.dumps(active_contracts, cls=DjangoJSONEncoder)
    closed_contracts = list(
        JobContract.objects.filter(accepted=True, employer__group=group).values())
    closed_contracts = json.dumps(closed_contracts, cls=DjangoJSONEncoder)
    contracts['active_contracts'] = active_contracts
    contracts['closed_contracts'] = closed_contracts
    group.contracts_dump = contracts
    group.save()
    return contracts

def process_employer_request(jsonmessage, group):
    print('message from employer')
    employer = Player.objects.get(pk=jsonmessage['player_pk'])
    wage_offer = jsonmessage['wage_offer']
    employer.offers.create(amount=wage_offer)
    contract, created = employer.contract.get_or_create(defaults={'amount': wage_offer,
                                                                  'accepted': False, })
    if created:
        group.last_message = str("Nuova offerta salariale di " + str(wage_offer) + ".")
        group.save()
    if not created:
        group.last_message = str(
            "Un'offerta precedentemente di " + str(contract.amount) + " è ora di " + str(wage_offer) + ".")
        group.save()
        contract.amount = wage_offer
        contract.save()

    time.sleep(0.01)


def process_worker_request(jsonmessage, respondent, group):
    response = {}
    worker = Player.objects.get(pk=jsonmessage['player_pk'])
    accepted_contract = JobContract.objects.filter(accepted=True, employer__group=group, worker=worker).count()
    print("accepted contracts", accepted_contract)
    if accepted_contract > 0:
        response['last_message'] = False
        group.last_message = False
        group.save()
    else:
        contract = JobContract.objects.get(pk=jsonmessage['contract_to_accept'])
        wage_accepted = jsonmessage['wage_accepted']
        print("wage_accepted and contract.amount", wage_accepted, contract.amount)
        if contract.accepted:
            # check if there are alternative contracts with the identical wage offer
            time.sleep(0.01)
            alternative_contracts = list(
                JobContract.objects.filter(accepted=False, employer__group=group, amount=wage_accepted).values('pk', 'amount'))
            if len(alternative_contracts) == 0:
                print("len = 0")
                response['already_taken'] = True
                response['last_message'] = False
                group.last_message = False
                group.save()
            else:
                print("len > 0")
                contract_key = alternative_contracts[0]['pk']
                contract = JobContract.objects.get(pk=contract_key)
                # double-check, basically should be reduntant
                if contract.accepted:
                    print("accepted, gone")
                    response['already_taken'] = True
                    response['last_message'] = False
                    group.last_message = False
                    group.save()
                else:
                    print("to be accepted")
                    contract.worker = worker
                    contract.accepted = True
                    contract.save()
                    response['already_taken'] = False
                    group.last_message = str("È stata accettata un offerta di " + wage_accepted + ".")
                    group.save()
        elif int(wage_accepted) != contract.amount:
            response['already_taken'] = True
            response['last_message'] = False
        else:
            print("wage accepted and contract amount", wage_accepted, contract.accepted)
            contract.worker = worker
            contract.accepted = True
            contract.save()
            group.last_message = str("È stata accettata un offerta di " + wage_accepted + ".")
            group.save()
            response['already_taken'] = False

    time.sleep(0.01)
    response.update(get_contracts(group))
    respondent.send({'text': json.dumps(response)})


def dir_ws_message(message, group_name):
    group_id = group_name[5:]
    jsonmessage = json.loads(message.content['text'])
    print(jsonmessage)
    group = OtreeGroup.objects.get(id=group_id)

    # Messages from employers: wage offers
    if jsonmessage['role'] == "employer":
        process_employer_request(jsonmessage, group=group)
    # Messages from the workers: acceptances
    elif jsonmessage['role'] == "worker":
        process_worker_request(jsonmessage, respondent=message.reply_channel, group=group)

    textforgroup = get_contracts(group)

    closed_contracts_num = JobContract.objects.filter(accepted=True, employer__group=group).count()
    group.num_contracts_closed = closed_contracts_num
    group.save()
    if closed_contracts_num >= Constants.num_employers:
        group.day_over = True
        group.save()
        textforgroup['day_over'] = group.day_over
    textforgroup['last_message'] = group.last_message
    textforgroup['contracts_closed'] = group.num_contracts_closed
    Group(group_name).send({
        "text": json.dumps(textforgroup),
    })
    print(textforgroup)

# Connected to websocket.disconnect
def dir_ws_disconnect(message, group_name):
    Group(group_name).discard(message.reply_channel)


# ==========


def slicelist(l,n):
    return [l[i:i + n] for i in range(0,len(l),n)]


def get_random_list():
    random_upper_boundary = randint(50,99)
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



def dir_work_connect(message, worker_code, player_pk):
    print('worker connected')
    new_task = get_task()
    player = Player.objects.get(participant__code__exact=worker_code, pk=player_pk)
    player.last_correct_answer = new_task['correct_answer']
    player.save()
    message.reply_channel.send({'text': json.dumps(new_task)})


def dir_work_disconnect(message, worker_code, player_pk):
    print('worker disconnected')


def dir_work_message(message, worker_code, player_pk):
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
    player.last_correct_answer = new_task['correct_answer']
    player.save()
    new_task['tasks_correct'] = player.tasks_correct
    new_task['tasks_attempted'] = player.tasks_attempted
    new_task['feedback'] = feedback

    if int(new_task['tasks_attempted']) < Constants.max_task_amount:
        message.reply_channel.send({'text': json.dumps(new_task)})
    if int(new_task['tasks_attempted']) >= Constants.max_task_amount:
        new_task['task_over'] = True
        message.reply_channel.send({'text': json.dumps(new_task)})