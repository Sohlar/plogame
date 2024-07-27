# views.py

from rest_framework import viewsets
from rest_framework.response import Response
from .models import BetSize, BetFrequency, PotType, Position, FlopTexture
from .serializers import BetSizeSerializer, BetFrequencySerializer

class PokerDataViewSet(viewsets.ViewSet):
    def list(self, request):
        pot_type = request.query_params.get('pot_type')
        position = request.query_params.get('position')
        flop_texture = request.query_params.get('flop_texture')

        if not all([pot_type, position, flop_texture]):
            return Response({"error": "Missing required parameters"}, status=400)

        try:
            pot_type_obj = PotType.objects.get(name=pot_type)
            position_obj = Position.objects.get(name=position)
            flop_texture_obj = FlopTexture.objects.get(name=flop_texture)
        except (PotType.DoesNotExist, Position.DoesNotExist, FlopTexture.DoesNotExist):
            return Response({"error": "Invalid parameters"}, status=400)

        bet_sizes = BetSize.objects.filter(
            pot_type=pot_type_obj,
            position=position_obj,
            flop_texture=flop_texture_obj
        )

        bet_frequencies = BetFrequency.objects.filter(
            pot_type=pot_type_obj,
            position=position_obj,
            flop_texture=flop_texture_obj
        )

        bet_sizes_data = BetSizeSerializer(bet_sizes, many=True).data
        bet_frequencies_data = BetFrequencySerializer(bet_frequencies, many=True).data

        # Format the data to match the expected structure in the frontend
        formatted_bet_sizes = {
            size['player']['name']: size['size'] for size in bet_sizes_data
        }

        formatted_bet_frequencies = [
            {
                "name": freq['hand'],
                freq['player1']['name']: freq['player1_frequency'],
                freq['player2']['name']: freq['player2_frequency']
            } for freq in bet_frequencies_data
        ]

        return Response({
            'bet_sizes': formatted_bet_sizes,
            'bet_frequencies': formatted_bet_frequencies
        })