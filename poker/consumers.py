import json
import asyncio
import logging
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
        logging.info("CONSUMER Starting new hand")
        async for state in self.game.play_hand():
            logging.info(f"CONSUMER Received game state")
            await self.send_game_update(state)
            logging.info("CONSUMER Sent Game Update")
            await asyncio.sleep(0.1)

    async def get_player_action(self, valid_actions):
        # Send a message to the client requesting an action
        await self.send(
            text_data=json.dumps(
                {"type": "request_action", "valid_actions": valid_actions}
            )
        )
        # Wait for the client's response
        response = await self.receive()
        return json.loads(response)["action"]

    async def send_game_update(self, game_state):
        logging.info(f"CONSUMER Sending Game Update: {game_state}")
        # await self.send_total_game_state(game_state)
        await self.send(
            text_data=json.dumps({"type": "game_state", "game_state": game_state})
        )
        logging.info("CONSUMER Game Update Sent")
        # add small delay
        await asyncio.sleep(0.1)

    async def send_total_game_state(self, game_state):
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "game_state_update", "game_state": game_state},
        )
        # wait for update
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "sync_marker", "id": id(game_state)},
        )

    async def sync_marker(self, event):
        await self.send(text_data=json.dumps({"type": "sync", "id": event["id"]}))

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
