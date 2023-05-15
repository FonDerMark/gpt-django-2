from django.urls import path
from .views import status, answer, payment, precheckout


urlpatterns = [
    path('status/', status, name='status'),
    path('payment/', payment, name='payment'),
    path('precheckout/', precheckout, name='precheckout'),
    path('request/', answer, name='answer'),
]
