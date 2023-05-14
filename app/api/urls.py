from django.urls import path
from .views import status, answer, payments


urlpatterns = [
    path('status/', status, name='status'),
    path('payments/', payments, name='payments'),
    path('request/', answer, name='answer'),
]
