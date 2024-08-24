from django.urls import path
from . import views

urlpatterns = [
    path("", views.poker_table, name='poker_table'),
]
