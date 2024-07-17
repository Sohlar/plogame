import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PokerConsumer(AsyncWebsocketConsumer):
    #Game instances
    games = {}
    #player id to consumer instance maps
    player_to_consumer = {}
    
    async def connect(self):
        print("Attempting to connect")
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'poker_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print("Connection Accepted")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        user_id = text_data_json['user_id']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'poker_action',
                'action': action,
                'user_id': user_id
            }
        )

    async def start_new_hand(self):
        game_state = self.game.start_new_hand()
        await self.send_private_hands(game_state)
        await self.send_public_game_state(game_state)

    async def process_action(self, action):
        if self.game.street == 'preflop':
            valid_actions = self.game.get_valid_preflop_actions()
            if action in valid_actions:
                self.game.process_preflop_action(action)
        else:
            valid_actions = self.game.get_valid_postflop_actions()
            if action in valid_actions:
                self.game.process_postflop_action(action)

        game_state = self.game.get_game_state()

        if game_state['hand_over']:
            result = self.game.determine_showdown_winner()
            game_state.update(result)

    async def send_private_hands(self, game_state):
        for player in [game_state['oop_player'], game_state['ip_player']]:
            if player['id'] in self.player_to_consumer:
                consumer = self.player_to_consumer[player['id']]
                await consumer.send(text_data=json.dumps({
                    'type': 'private_hand',
                    'hand': player['hand']    
                }))

    async def send_public_game_state(self, game_state):
        #Remove hands from game_state
        public_state = game_state.copy()
        public_state['oop_player'] = {k: v for k, v in public_state['oop_player'].items() if k != 'hand'}
        public_state['ip_player'] = {k: v for k, v in public_state['ip_player'].items() if k != 'hand'}

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_state_update',
                'game_state': public_state
            }
        )

    async def game_state_update(self, event):
        game_state = event['game_state']
        await self.send(text_data=json.dumps(game_state))