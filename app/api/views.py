from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from .models import TelegramUser
import datetime
import json
from django.views.decorators.csrf import csrf_exempt
import dotenv
from os import environ as env


from .request_to_gpt import request_to_gpt

dotenv.load_dotenv()

DEFAULT_GPT_MODE = env.get('DEFAULT_GPT_MODE', 'theb')
AES_SECRET_KEY = env['AES_SECRET_KEY']

@csrf_exempt
def status(request):
    user = __Service._get_or_create_user(request)
    data = {
        'extra_messages': user.extra_messages,
        'day_limit_of_messages': user.day_limit_of_messages,
        'username': user.username,
    }
    return JsonResponse(data)

@csrf_exempt
def payments(request):
    if request.method == 'POST':
        user = __Service._get_or_create_user(request)
        data = {
            'extra_messages': user.extra_messages,
            'day_limit_of_messages': user.day_limit_of_messages,
            'username': user.username,
        }
        return JsonResponse(data)

@csrf_exempt
def answer(request):
    if request.method == 'POST':
        user = __Service._get_or_create_user(request)
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

class __Service:
    
    @staticmethod
    def _get_or_create_user(request, crypto=False):
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
        if crypto:
            user.save()
            return (user, __Service._validator)
        else:
            user.save()
            return user
    
    @staticmethod
    def _validator(all_data, crypto_text):
        pass
