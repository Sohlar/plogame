from django.contrib import admin
from .models import PotType, Position, Player, FlopTexture, BetSize, BetFrequency

admin.site.register(PotType)
admin.site.register(Position)
admin.site.register(Player)
admin.site.register(FlopTexture)
admin.site.register(BetSize)
admin.site.register(BetFrequency)