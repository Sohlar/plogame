from django.urls import path
from . import views

urlpatterns = [
    path('poker/', views.poker_table, name='poker_table'),
]
