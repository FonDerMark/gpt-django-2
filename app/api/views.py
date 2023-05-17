from django.http import JsonResponse
import datetime
import json
from django.views.decorators.csrf import csrf_exempt
import dotenv
from os import environ as env
from Crypto.Cipher import AES

from .models import TelegramUser, Payments
from .request_to_gpt import request_to_gpt


dotenv.load_dotenv()

DEFAULT_GPT_MODE = env['DEFAULT_GPT_MODE']
AES_SECRET_KEY = env['AES_SECRET_KEY'].encode('iso-8859-1')


@csrf_exempt
def status(request):
    user = Service.get_or_create_user(request)
    data = {
        'extra_messages': user.extra_messages,
        'day_limit_of_messages': user.day_limit_of_messages,
        'username': user.username,
    }
    return JsonResponse(data)


@csrf_exempt
def precheckout(request):
    return JsonResponse({'precheckout': True})
    

@csrf_exempt
def payment(request):
    user = Service.get_or_create_user(request)
    status = json.loads(Service.validator(request))['payment_ok']
    if status['status']:
        Payments.objects.create(
            product = '100',
            user = user.id,
            price = 5000,
            key = status['key']
        )
        user.extra_messages += 100
        user.save()
        return JsonResponse({'status': True})
    else:
        return JsonResponse({'status': False})
    # TODO 


@csrf_exempt
def payments(request):
    if request.method == 'POST':
        user = Service.get_or_create_user(request)
        data = {
            'extra_messages': user.extra_messages,
            'day_limit_of_messages': user.day_limit_of_messages,
            'username': user.username,
        }
        return JsonResponse(data)


@csrf_exempt
def answer(request):
    if request.method == 'POST':
        user = Service.get_or_create_user(request)
        # Если передан параметр 'gpt_mode', применить его
        gpt_mode = request.POST.get('gpt_mode', DEFAULT_GPT_MODE)
        question = json.loads(request.POST['all_data'])['text']
        # Проверка даты последнего начисления запросов
        if user.day_limit == datetime.date.today():
            # Если суточных запросов > 0:
            if user.day_limit_of_messages > 0:
                _answer = request_to_gpt(question, gpt_mode)
                user.day_limit_of_messages -= 1
                user.save()
            # Если остались экстразапросы
            elif user.extra_messages > 0:
                _answer = request_to_gpt(question, gpt_mode)
                user.extra_messages -= 1
                user.save()
            else:
                _answer = 'Вы исчерпали лимит сообщений'
        # В случае нового дня
        else:
            _answer = request_to_gpt(question, gpt_mode)
            user.extra_messages = 9
            user.day_limit = datetime.date.today()
            user.save()
        data = {
            'answer': _answer,
            'extra_messages': user.extra_messages,
            'day_limit_of_messages': user.day_limit_of_messages,
        }
        try:
            return JsonResponse(data)
        except:
            user.day_limit_of_messages += 1
            user.save()


class Service:
    
    @staticmethod
    def get_or_create_user(request):
        all_data = json.loads(request.POST['all_data'])
        user_data = all_data['from']
        user, created = TelegramUser.objects.get_or_create(user_id=user_data['id'])
        try:
            user.username = user_data['username']
            user.firstname = user_data['first_name']
            user.lastname = user_data['last_name']
        except:
            pass
        if created or user.day_limit == None:
            user.day_limit_of_messages = 10
            user.day_limit = datetime.date.today()
            user.extra_messages = 0
        user.save()
        return user
    
    @staticmethod
    def validator(request):
        key = json.loads(request.POST['key'])
        all_data = json.loads(request.POST['all_data'])
        nonce, tag, ciphertext = [x.encode('iso-8859-1') for x in key]
        cipher = AES.new(AES_SECRET_KEY, AES.MODE_EAX, nonce)
        encrypted_all_data = json.loads(cipher.decrypt_and_verify(ciphertext, tag))
        print(type(all_data))
        print(type(encrypted_all_data))
        # Если данный ключ уже использовался при покупке, присвоить переменной значение False
        try:
            Payments.objects.get(key=ciphertext)
            check = False
        except:
            check = True
        if all_data == encrypted_all_data and check:
            return {
                'status': True,
                'key': key
            }
        else:
            return {
                'status': False,
            }