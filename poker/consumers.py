import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .game_logic import PokerGame


class PokerConsumer(AsyncWebsocketConsumer):
    games = {}
    player_to_consumer = {}

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"poker_{self.room_name}"
        self.player_id = self.scope["user"].id if self.scope["user"].id else "anonymous"

        if self.room_name not in self.games:
            self.games[self.room_name] = PokerGame()
        self.game = self.games[self.room_name]

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        self.player_to_consumer[self.player_id] = self
        await self.accept()

        print(
            f"Connection Accepted for player {self.player_id} in room {self.room_name}"
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if self.player_id in self.player_to_consumer:
            del self.player_to_consumer[self.player_id]
        print(f"Player {self.player_id} disconnected from room {self.room_name}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data["action"]

        if action == "start_hand":
            await self.start_new_hand()
        elif action in ["check", "bet", "fold", "call"]:
            await self.process_action(action)
        else:
            await self.send(text_data=json.dumps({"error": "Invalid action"}))

    async def start_new_hand(self):
        game_state = self.game.start_new_hand()
        await self.send_game_update(game_state)

    async def process_action(self, action):
        self.game.state["action"] = action
        if self.game.state["street"] == "preflop":
            valid_actions = self.game.get_valid_preflop_actions()
            if action in valid_actions:
                self.game.process_preflop_action(action)
                game_state = self.game.state
                await self.send_game_update(game_state)
            else:
                await self.send(
                    text_data=json.dumps({"error": "Invalid preflop action"})
                )
        else:
            valid_actions = self.game.get_valid_postflop_actions()
            if action in valid_actions:
                self.game.process_postflop_action(action)
                game_state = self.game.state
                await self.send_game_update(game_state)
            else:
                await self.send(
                    text_data=json.dumps({"error": "Invalid postflop action"})
                )

    async def send_game_update(self, game_state):
        await self.send_private_hands(game_state)
        await self.send_public_game_state(game_state)

    async def send_private_hands(self, game_state):
        for player in [game_state["oop_player"], game_state["ip_player"]]:
            if player["name"] in self.player_to_consumer:
                consumer = self.player_to_consumer[player["name"]]
                await consumer.send(
                    text_data=json.dumps(
                        {
                            "type": "private_hand",
                            "player": player["name"],
                            "hand": player["hand"],
                        }
                    )
                )

    async def send_public_game_state(self, game_state):
        public_state = game_state.copy()
        public_state["oop_player"] = {
            k: v for k, v in public_state["oop_player"].items() if k != "hand"
        }
        public_state["ip_player"] = {
            k: v for k, v in public_state["ip_player"].items() if k != "hand"
        }

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "game_state_update", "game_state": public_state},
        )

    async def game_state_update(self, event):
        game_state = event["game_state"]
        await self.send(
            text_data=json.dumps(
                {
                    "type": "game_state",
                    "oop_player": game_state["oop_player"],
                    "ip_player": game_state["ip_player"],
                    "pot": game_state["pot"],
                    "community_cards": game_state["community_cards"],
                    "current_player": game_state["current_player"],
                    "current_bet": game_state["current_bet"],
                    "last_action": game_state.get("last_action"),
                }
            )
        )
