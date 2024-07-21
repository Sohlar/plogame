import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .game_logic import PokerGame


class PokerConsumer(AsyncWebsocketConsumer):
    # Game instances
    games = {}
    # player id to consumer instance maps
    player_to_consumer = {}

    functions = {
        "start_hand": start_new_hand,
    }

    async def connect(self):
        print("Attempting to connect")
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"poker_{self.room_name}"
        self.game = PokerGame()
        self.player_id = self.scope["user"].id

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        self.player_to_consumer[self.player_id] = self
        await self.accept()

        print("Connection Accepted")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if self.player_id in self.player_to_consumer:
            del self.player_to_consumer[self.player_id]

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data["action"]

        if action == "start_hand":
            game_state = self.game.start_new_hand()
            print(f"New hand started. Game state: {game_state}")
            await self.send_private_hands(game_state)
            await self.send_public_game_state(game_state)

    async def start_new_hand(self):
        game_state = self.game.start_new_hand()
        await self.send_private_hands(game_state)
        await self.send_public_game_state(game_state)

    async def process_action(self, action):
        if self.game.street == "preflop":
            valid_actions = self.game.get_valid_preflop_actions()
            if action in valid_actions:
                self.game.process_preflop_action(action)
        else:
            valid_actions = self.game.get_valid_postflop_actions()
            if action in valid_actions:
                self.game.process_postflop_action(action)

        game_state = self.game.get_game_state()

        if game_state["hand_over"]:
            result = self.game.determine_showdown_winner()
            game_state.update(result)

    async def game_state_update(self, event):
        try:
            game_state = event["game_state"]
            player_id = self.scope["user"].id

            private_state = self.game.get_private_game_state()

            await self.send(
                text_data=json.dump(
                    {
                        "public_state": game_state,
                        "private_state": private_state,
                    }
                )
            )
            print(f"Sent game state update to player {player_id}")
        except Exception as e:
            print(f"Error in game_state_update: {str(e)}")
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Error updating game state"}
                )
            )

    async def send_private_hands(self, game_state):
        for player in [game_state["oop_player"], game_state["ip_player"]]:
            if player["name"] in self.player_to_consumer:
                consumer = self.player_to_consumer[player["name"]]
                await consumer.send(
                    text_data=json.dumps(
                        {"type": "private_hand", "hand": player["hand"]}
                    )
                )

    async def send_public_game_state(self, game_state):
        # Remove hands from game_state
        public_state = game_state.copy()
        public_state["oop_player"] = {
            k: v for k, v in public_state["oop_player"].items() if k != "hand"
        }
        public_state["ip_player"] = {
            k: v for k, v in public_state["ip_player"].items() if k != "hand"
        }

        print(f"Sending public game state: {public_state}")

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "game_state_update", "game_state": public_state},
        )
