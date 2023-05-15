from django.contrib import admin
from .models import TelegramUser, Payments

admin.site.register(TelegramUser)
admin.site.register(Payments)
