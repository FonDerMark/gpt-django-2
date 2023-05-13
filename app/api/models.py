from django.db import models

class TelegramUser(models.Model):
    user_id = models.IntegerField()
    username = models.CharField(max_length=100, null=True, blank=True)
    firstname = models.CharField(max_length=100, null=True, blank=True)
    lastname = models.CharField(max_length=100, null=True, blank=True)
    extra_messages = models.IntegerField(null=True)
    day_limit_of_messages = models.IntegerField(null=True)
    day_limit = models.DateField(null=True)
    premium_status = models.DateTimeField(null=True, blank=True)
    banned = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.username}({self.user_id})/limit:{self.day_limit_of_messages}'