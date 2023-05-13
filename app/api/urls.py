from django.urls import path
from .views import status, answer


urlpatterns = [
    path('status/', status, name='status'),
    path('request/', answer, name='answer'),
]
