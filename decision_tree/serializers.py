# serializers.py

from rest_framework import serializers
from .models import PotType, Position, Player, FlopTexture, BetSize, BetFrequency

class PotTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PotType
        fields = ['id', 'name']

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name']

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'name']

class FlopTextureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlopTexture
        fields = ['id', 'name']

class BetSizeSerializer(serializers.ModelSerializer):
    pot_type = PotTypeSerializer(read_only=True)
    position = PositionSerializer(read_only=True)
    player = PlayerSerializer(read_only=True)
    flop_texture = FlopTextureSerializer(read_only=True)

    class Meta:
        model = BetSize
        fields = ['id', 'pot_type', 'position', 'player', 'flop_texture', 'size']

class BetFrequencySerializer(serializers.ModelSerializer):
    pot_type = PotTypeSerializer(read_only=True)
    position = PositionSerializer(read_only=True)
    flop_texture = FlopTextureSerializer(read_only=True)
    player1 = PlayerSerializer(read_only=True)
    player2 = PlayerSerializer(read_only=True)

    class Meta:
        model = BetFrequency
        fields = ['id', 'pot_type', 'position', 'flop_texture', 'hand', 'player1', 'player1_frequency', 'player2', 'player2_frequency']