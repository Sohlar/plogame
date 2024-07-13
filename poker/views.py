from django.shortcuts import render

# Create your views here.
from .game import PokerGame
def poker_table(request):
    return render(request, 'poker.html')
