from django.shortcuts import render

# Create your views here.
from .game_logic import PokerGame


def poker_table(request):
    return render(request, "poker.html")
