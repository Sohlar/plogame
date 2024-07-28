import json
from django.core.management.base import BaseCommand
from decision_tree.models import PotType, Position, Player, FlopTexture, BetSize, BetFrequency

class Command(BaseCommand):
    help = 'Load poker data from JSON file'

    def handle(self, *args, **options):
        with open('tree_data.json', 'r') as file:
            data = json.load(file)

        # Create PotTypes
        for pot_type_name in data['bet_sizes'].keys():
            PotType.objects.get_or_create(name=pot_type_name)

        # Create Positions and Players
        for pot_type_data in data['bet_sizes'].values():
            for position_name in pot_type_data.keys():
                Position.objects.get_or_create(name=position_name)
                for player_name in pot_type_data[position_name].keys():
                    Player.objects.get_or_create(name=player_name)

        # Create FlopTextures
        for pot_type_data in data['bet_sizes'].values():
            for position_data in pot_type_data.values():
                for player_data in position_data.values():
                    for flop_texture_name in player_data.keys():
                        FlopTexture.objects.get_or_create(name=flop_texture_name)

        # Create BetSizes
        for pot_type_name, pot_type_data in data['bet_sizes'].items():
            pot_type = PotType.objects.get(name=pot_type_name)
            for position_name, position_data in pot_type_data.items():
                position = Position.objects.get(name=position_name)
                for player_name, player_data in position_data.items():
                    player = Player.objects.get(name=player_name)
                    for flop_texture_name, size in player_data.items():
                        flop_texture = FlopTexture.objects.get(name=flop_texture_name)
                        BetSize.objects.get_or_create(
                            pot_type=pot_type,
                            position=position,
                            player=player,
                            flop_texture=flop_texture,
                            size=size
                        )

        # Create BetFrequencies
        for pot_type_name, pot_type_data in data['bet_frequencies'].items():
            pot_type = PotType.objects.get(name=pot_type_name)
            for position_name, position_data in pot_type_data.items():
                position = Position.objects.get(name=position_name)
                for flop_texture_name, frequency_data in position_data.items():
                    flop_texture = FlopTexture.objects.get(name=flop_texture_name)
                    for hand_data in frequency_data:
                        hand = hand_data['name']
                        player1_name, player2_name = list(hand_data.keys())[1:]
                        player1 = Player.objects.get(name=player1_name)
                        player2 = Player.objects.get(name=player2_name)
                        BetFrequency.objects.get_or_create(
                            pot_type=pot_type,
                            position=position,
                            flop_texture=flop_texture,
                            hand=hand,
                            player1=player1,
                            player1_frequency=hand_data[player1_name],
                            player2=player2,
                            player2_frequency=hand_data[player2_name]
                        )

        self.stdout.write(self.style.SUCCESS('Successfully loaded poker data'))