import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PokerConsumer(AsyncWebsocketConsumer):
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

    # Receive message from room group
    async def poker_action(self, event):
        action = event['action']
        user_id = event['user_id']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'action': action,
            'user_id': user_id
        }))
