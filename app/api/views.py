from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from .models import TelegramUser
import datetime
import json
from django.views.decorators.csrf import csrf_exempt


from .request_to_gpt import request_to_gpt

@csrf_exempt
def status(request):
    user = _get_or_create_user(request)
    data = {
        'extra_messages': user.extra_messages,
        'day_limit_of_messages': user.day_limit_of_messages,
        'username': user.username,
    }
    return JsonResponse(data)

@csrf_exempt
def answer(request):
    user = _get_or_create_user(request)
    question = json.loads(request.POST['all_data'])['text']
    # Проверка даты последнего начисления запросов
    if user.day_limit == datetime.date.today():
        # Если суточных запросов > 0:
        if user.day_limit_of_messages > 0:
            _answer = request_to_gpt(question)
            user.day_limit_of_messages -= 1
            user.save()
        # Если остались экстразапросы
        elif user.extra_messages > 0:
            _answer = request_to_gpt(question)
            user.extra_messages -= 1
            user.save()
        else:
            _answer = 'Вы исчерпали лимит сообщений'
    # В случае нового дня
    else:
        _answer = request_to_gpt(question)
        user.extra_messages = 9
        user.day_of_limit = datetime.date.today()
        user.save()
    data = {
        'answer': _answer,
        'extra_messages': user.extra_messages,
        'day_limit_of_messages': user.day_limit_of_messages,
    }
    try:
        return JsonResponse(data, encoder=DjangoJSONEncoder)
    except:
        user.day_limit_of_messages += 1
        user.save()
    
# Service functions
def _get_or_create_user(request):
    all_data = json.loads(request.POST['all_data'])
    user_data = all_data['from']
    user, created = TelegramUser.objects.get_or_create(user_id=user_data['id'])
    try:
        user.username = user_data['username']
        user.firstname = user_data['first_name']
        user.lastname = user_data['last_name']
    finally:
        if created:
            user.day_limit_of_messages = 10
            user.day_limit = datetime.date.today()
            user.extra_messages = 0
        user.save()
        return user


class MyJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, str):
            return obj.encode('cp1251').decode('cp1251')
        return super().default(obj)