import json
from django.core.management.base import BaseCommand
from your_app.models import PotType, Position, Player, FlopTexture, BetSize, BetFrequency

class Command(BaseCommand):
    help = 'Load initial poker data from JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing poker data')

    def handle(self, *args, **options):
        json_file_path = options['json_file']

        with open(json_file_path, 'r') as file:
            data = json.load(file)

        # Create PotTypes
        pot_types = {name: PotType.objects.create(name=name) for name in data['bet_sizes']}

        # Create Positions and Players
        positions = set()
        players = set()
        for pot_type_data in data['bet_sizes'].values():
            positions.update(pot_type_data.keys())
            for position_data in pot_type_data.values():
                players.update(position_data.keys())

        positions = {name: Position.objects.create(name=name) for name in positions}
        players = {name: Player.objects.create(name=name) for name in players}

        # Create FlopTextures
        flop_textures = set()
        for pot_type_data in data['bet_sizes'].values():
            for position_data in pot_type_data.values():
                for player_data in position_data.values():
                    flop_textures.update(player_data.keys())

        flop_textures = {name: FlopTexture.objects.create(name=name) for name in flop_textures}

        # Create BetSizes
        for pot_type_name, pot_type_data in data['bet_sizes'].items():
            for position_name, position_data in pot_type_data.items():
                for player_name, player_data in position_data.items():
                    for flop_texture_name, size in player_data.items():
                        BetSize.objects.create(
                            pot_type=pot_types[pot_type_name],
                            position=positions[position_name],
                            player=players[player_name],
                            flop_texture=flop_textures[flop_texture_name],
                            size=str(size)
                        )

        # Create BetFrequencies
        for pot_type_name, pot_type_data in data['bet_frequencies'].items():
            for position_name, position_data in pot_type_data.items():
                for flop_texture_name, frequency_data in position_data.items():
                    for hand_data in frequency_data:
                        player_names = [name for name in hand_data.keys() if name != 'name']
                        BetFrequency.objects.create(
                            pot_type=pot_types[pot_type_name],
                            position=positions[position_name],
                            flop_texture=flop_textures[flop_texture_name],
                            hand=hand_data['name'],
                            player1=players[player_names[0]],
                            player1_frequency=hand_data[player_names[0]],
                            player2=players[player_names[1]],
                            player2_frequency=hand_data[player_names[1]]
                        )

        self.stdout.write(self.style.SUCCESS('Successfully loaded poker data into the database'))