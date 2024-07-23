import secrets
import logging
from phevaluator import evaluate_omaha_cards


# fmt: off
#### Player Class ####
class Player:
    players = []
    last_id = 0

    def __init__(self, name: str, chips: int) -> None:
        Player.players.append(self)
        self.id = Player.last_id
        Player.last_id += 1
        self.name: str = name
        self.chips: int = chips
        self.hand = []

    @classmethod
    def get_players(cls):
        return cls.players

    def reset_hands():
        [player.hand.clear() for player in Player.get_players()]

    def reset_chips():
        for player in Player.get_players():
            player.chips = 200


class Deck:
    def __init__(self):
        # fmt: off
        self.cards = [
            "2c", "3c", "4c", "5c", "6c", "7c", "8c", "9c", "Tc", "Jc", "Qc", "Kc", "Ac", 
            "2d", "3d", "4d", "5d", "6d", "7d", "8d", "9d", "Td", "Jd", "Qd", "Kd", "Ad", 
            "2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th", "Jh", "Qh", "Kh", "Ah", 
            "2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s", "Ts", "Js", "Qs", "Ks", "As",
        ]

    def shuffle(self):
        secrets.SystemRandom().shuffle(self.cards)


class PokerGame:
    def __init__(self):
        self.state = {
            "pot": 0,
            "community_cards": [],
            "current_player": None,
            "current_bet": 0,
            "last_action": None,
            "num_actions": 0,
            "num_active_players": 2,
            "hand_over": False,
            "waiting_for_action": False,
            "valid_actions": None,
            "oop_player": {"name": "OOP", "chips": 200, "hand": [], "committed": 0},
            "ip_player": {
                "name": "IP",
                "chips": 200,
                "hand": [],
                "committed": 0,
            },
        }
        self.deck = Deck()

    def initialize_game_state(self):
        self.state.update(
            {
                "street": "preflop",
                "pot": 3,
                "community_cards": [],
                "current_bet": 2,
                "last_action": "bet",
                "num_actions": 0,
                "hand_over": False,
                "waiting_for_action": False,
                "num_active_players": 2,
                "valid_actions": None,
                "oop_player": {"name": "OOP", "chips": 198, "hand": [], "committed": 2},
                "ip_player": {
                    "name": "IP",
                    "chips": 199,
                    "hand": [],
                    "committed": 1,
                },
            }
        )

    def deal_cards(self):
        for player in [self.state["oop_player"], self.state["ip_player"]]:
            player["hand"] = [self.deck.cards.pop() for _ in range(4)]

    def start_new_hand(self):
        print("Starting init_game_state() \n")
        self.initialize_game_state()
        print("Finished init_game_state() \n")
        # send state to frontend
        # self.reset_hands()
        self.deck.shuffle()
        print("Starting deal_cards() \n")
        self.deal_cards()
        print("Finished deal_cards() \n")
        self.state["current_player"] = self.state["ip_player"]
        return self.get_game_state()

    # Returns Game state

    async def play_hand(self):
        logging.info("Starting play hand")
        init_state = self.start_new_hand()
        logging.info(f"Initial State: {init_state}")
        yield init_state

        logging.info("Entering preflop betting")
        async for state in self.preflop_betting():
            yield state

        if not self.state["hand_over"]:
           yield self.deal_flop()
           async for state in self.postflop_betting("flop"):
               yield state

        if not self.state["hand_over"]:
            yield self.deal_turn()
            async for state in self.postflop_betting("turn"):
                yield state

        if not self.state["hand_over"]:
            yield self.deal_river()
            async for state in self.postflop_betting("river"):
                yield state

        if not self.state["hand_over"]:
            yield self.determine_showdown_winner()

    def deal_flop(self):
        self.deal_community_cards(3)
        return self.postflop_betting(street="flop")

    def deal_turn(self):
        self.deal_community_cards(1)
        return self.postflop_betting(street="turn")

    def deal_river(self):
        self.deal_community_cards(1)
        return self.postflop_betting(street="river")

    def deal_community_cards(self, num_cards):
        self.community_cards.extend([self.deck.cards.pop() for _ in range(num_cards)])
        print(self.community_cards)

    def reset_hands(self):
        self.deck = Deck()
        self.state["community_cards"] = []
        self.state["pot"] = 0
        self.state["oop_player"]["hand"] = []
        self.state["ip_player"]["hand"] = []
        self.state["current_bet"] = []
        self.state["num_actions"] = 0
        self.state["last_action"] = None
        self.state["hand_over"] = False

    def get_game_state(self):
        return self.state

    def get_public_game_state(self):
        public_state = self.get_game_state().copy
        public_state["oop_player"] = {
            k: v for k, v in public_state["oop_player"] if k != "hand"
        }
        public_state["ip_player"] = {
            k: v for k, v in public_state["ip_player"] if k != "hand"
        }

    def get_private_game_state(self):
        return {
            "valid_actions": self.valid_actions,
            "oop_player": {
                "hand": self.oop_player.hand,
            },
            "ip_player": {
                "hand": self.ip_player.hand,
            },
        }

    def update_state(self, **kwargs):
        self.state.update(kwargs)

    def get_player_action(self, valid_actions):
        raise NotImplementedError("get_player_action must be implemented")

    async def preflop_betting(self):
        while True:
            game_state = self.get_game_state()

            if self.state["hand_over"] or self.state["num_active_players"] == 1:
                self.state["current_player"]["chips"] += self.state["pot"]
                self.state["message"] = (
                    f"{self.state['current_player']['name']} wins ${self.state['pot']}"
                )
                self.state["hand_over"] = True
                yield game_state
                game_state

            all_players_acted = (
                self.state["num_actions"] >= self.state["num_active_players"]
            )
            all_bets_settled = (
                self.state["oop_player"]["chips"] == self.state["ip_player"]["chips"]
            )
            yield self.get_game_state()
            if self.state["hand_over"] or all_players_acted and all_bets_settled:
                self.state["message"] = "Preflop betting complete"
                return

            self.state["valid_actions"] = self.get_valid_preflop_actions()
            yield self.state["valid_actions"]
            action = await self.get_player_action(self.state["valid_actions"])
            self.process_preflop_action(action)

    def process_preflop_action(self, action):
        if self.state["action"] not in self.get_valid_preflop_actions():
            return {"error: Invalid Action"}

        if self.state["action"] == "bet":
            self.handle_preflop_bet()
        if self.state["action"] == "call":
            self.handle_preflop_call()
        if self.state["action"] == "check":
            self.handle_preflop_check()
        if self.state["action"] == "fold":
            self.handle_fold()

        self.switch_players()

    def get_valid_preflop_actions(self):
        if self.state['oop_player']['chips'] == 0 or self.state['ip_player']['chips'] == 0: #Facing All in
            return ["call", "fold"]
        if self.state['current_player'] == self.state['ip_player'] and self.state['num_actions'] == 0: #Preflop Open
            return ["call", "bet", "fold"]
        elif self.state['current_player'] == self.state['oop_player'] and self.state['last_action'] == "call": #Facing Open limp
            return ["check", "bet"]
        else:
            return ["call", "bet", "fold"]
        #

    def handle_preflop_bet(self):
        self.calculate_preflop_bet_size()
        if not self.state["all_in"]:
            if self.state["current_player"]["name"] == self.state["ip_player"]["name"]:
                self.state["current_player"]["chips"] -= (
                    self.state["bet_amount"] - self.state["ip_player"]["committed"]
                )
                self.state["pot"] += (
                    self.state["bet_amount"] - self.state["ip_player"]["committed"]
                )
                self.state["ip_player"]["committed"] = self.state["bet_amount"]
                self.state["current_bet"] = self.state["bet_amount"]
            else:
                self.state["current_player"]["chips"] -= (
                    self.state["bet_amount"] - self.state["oop_player"]["committed"]
                )
                self.state["pot"] += (
                    self.state["bet_amount"] - self.state["oop_player"]["committed"]
                )
                self.state["oop_player"]["oop_committed"] = self.state["bet_amount"]
                self.state["current_bet"] = self.state["bet_amount"]
        else:
            if self.state["current_player"]["name"] == self.state["ip_player"]["name"]:
                self.state["ipp_player"]["committed"] += self.state["current_player"][
                    "chips"
                ]
            else:
                self.state["oop_player"]["committed"] += self.state["current_player"][
                    "chips"
                ]
            self.state["pot"] += self.state["current_player"]["chips"]
            self.state["current_player"]["chips"] = 0
        self.state["num_actions"] += 1
        self.state["last_action"] = "bet"

    def handle_preflop_call(self):
        if (
            self.state["current_player"] == self.state["ip_player"]
            and self.state["num_actions"] == 0
        ):
            self.state["current_player"]["chips"] -= 1
            self.state["pot"] += 1
        else:
            if self.state["current_player"]["name"] == self.state["oop_player"]["name"]:
                diff = self.state["ip_player"]["committed"] - self.state["oop_player"]["committed"]
                self.state["oop_player"]["committed"] += diff
            else:
                diff = self.state["oop_player"]["committed"] - self.state["ip_player"]["committed"]
                self.state["ip_player"]["committed"] += diff
            self.state["current_player"]["chips"] -= diff
            self.state["pot"] += diff
            self.state["street"] = "flop"
        self.state["num_actions"] += 1
        self.state["last_action"] = "call"

    def handle_preflop_check(self):
        if (
            self.state["current_player"] == self.state["oop_player"]
            and self.state["last_action"] == "call"
        ):
            self.state["num_actions"] += 1
            self.state["last_action"] = "check"

    def calculate_preflop_bet_size(self):
        self.state["all_in"] = False
        self.state["is_raise"] = True
        if self.state["is_raise"]:
            # If it's a raise, the bet size is 3 times the last raise plus the current pot size
            self.state["bet_amount"] = 3 * self.state["current_bet"]
        if self.state["current_player"]["chips"] < self.state["bet_amount"]:
            self.state["bet_amount"] = self.state["current_player"]["chips"]
            self.state["all_in"] = True

    def postflop_betting(self, street):
        self.state["num_active_players"] = len(
            [
                p
                for p in [self.state["oop_player"], self.state["ip_player"]]
                if p["chips"] > 0
            ]
        )
        self.state["ip_committed"] = 0
        self.state["oop_committed"] = 0
        self.state["current_bet"] = 0
        self.state["num_actions"] = 0
        self.state["current_player"] = self.state["oop_player"]
        self.state["hand_over"] = False
        while True:
            game_state = self.get_game_state()
            game_state["street"] = street
            if self.state["hand_over"] or self.state["num_active_players"] == 1:
                self.state["current_player"]["chips"] += self.state["pot"]
                return {
                    "message": f"{self.state['current_player']['name']} wins ${self.state['pot']}",
                    "hand_over": True,
                }
            all_players_acted = (
                self.state["num_actions"] >= self.state["num_active_players"]
            )
            all_bets_settled = (
                self.state["oop_player"]["chips"] == self.state["ip_player"]["chips"]
            )
            if all_players_acted and all_bets_settled:
                game_state["message"] = f"{street.capitalize()} betting complete"
                return game_state
            valid_actions = self.get_valid_postflop_actions()
            action = self.get_player_action(valid_actions)
            self.process_postflop_action(action)
        return game_state

    def process_postflop_action(self, action):
        if self.state["action"] not in self.get_valid_postflop_actions():
            return {"error": "Invalid Action"}
        if self.state["action"] == "check":
            self.handle_postflop_check()
        elif self.state["action"] == "bet":
            self.handle_postflop_bet()
        elif self.state["action"] == "call":
            self.handle_postflop_call()
        elif self.state["action"] == "fold":
            self.handle_fold()
        self.switch_players()

    def get_valid_postflop_actions(self):
        if (
            self.state["oop_player"]["chips"] == 0
            or self.state["ip_player"]["chips"] == 0
        ):
            return ["call", "fold"]
        if self.state["current_bet"] == 0:
            return ["check", "bet", "fold"]
        else:
            return ["call", "bet", "fold"]

    def handle_postflop_bet(self):
        self.state["is_allin"], self.state["bet_amount"] = (
            self.calculate_postflop_bet_size()
        )
        print(self.state["bet_amount"])
        if not self.state["is_allin"]:
            if self.state["current_player"]["name"] == self.state["ip_player"]["name"]:
                self.state["current_player"]["chips"] -= self.state["bet_amount"]
                self.state["pot"] += self.state["bet_amount"]
                self.state["ip_committed"] += self.state["bet_amount"]
                self.state["current_bet"] = self.state["bet_amount"]
            else:
                self.state["current_player"]["chips"] -= self.state["bet_amount"]
                self.state["pot"] += self.state["bet_amount"]
                self.state["oop_committed"] += self.state["bet_amount"]
                self.state["current_bet"] = self.state["bet_amount"]
        else:
            if self.state["current_player"] == self.state["ip_player"]:
                self.state["ip_committed"] += self.state["ip_player"]["chips"]
            else:
                self.state["oop_committed"] += self.state["oop_player"]["chips"]
            self.state["current_bet"] = self.state["bet_amount"]
            self.state["pot"] += self.state["current_player"]["chips"]
            self.state["current_player"]["chips"] = 0
        self.state["num_actions"] += 1
        self.state["last_action"] = "bet"

    def handle_postflop_call(self):
        call_amount = self.state["current_bet"]
        if call_amount <= self.state["current_player"]["chips"]:
            print("1")
            print(self.state["current_player"]["chips"])
            print(call_amount)
            self.state["current_player"]["chips"] -= call_amount
            self.state["pot"] += call_amount
        else:
            print("2")
            # This is prone to bug. Only works under equal starting stacks.
            all_in_amount = self.state["current_player"]["chips"]
            self.state["current_player"]["chips"] = 0
            self.state["pot"] += all_in_amount
            difference = call_amount - all_in_amount
            """
            other_player = (
                self.state['ip_player']
                if self.state['current_player'] == self.state['oop_player']
                else self.state['oop_player']
            )
            other_player.chips += difference
            self.state['pot'] -= difference
            """
        self.state["num_actions"] += 1
        self.state["last_action"] = "call"

    def handle_postflop_check(self):
        self.state["num_actions"] += 1
        self.state["last_action"] = "check"

    def handle_fold(self):
        self.state["num_active_players"] -= 1
        self.state["hand_over"] = True

    def calculate_postflop_bet_size(self):
        all_in = False
        if self.state["last_action"] == "bet":
            # If it's a raise, the bet size is 3 times the last raise plus the current pot size
            bet_size = 2 * self.state["current_bet"] + self.state["pot"]
        else:
            # If it's a standard bet, the bet size is equal to the current pot size
            bet_size = self.state["pot"]

        if self.state["current_player"]["chips"] < bet_size:
            bet_size = self.state["current_player"]["chips"]
            all_in = True

        return all_in, bet_size

    def switch_players(self):
        self.state["current_player"] = (
            self.state["oop_player"]
            if self.state["current_player"] == self.state["ip_player"]
            else self.state["ip_player"]
        )

    def determine_showdown_winner(self):
        ip_rank = evaluate_omaha_cards(
            self.state['community_cards'][0], self.state['community_cards'][1], self.state['community_cards'][2], self.state['community_cards'][3], self.state['community_cards'][4],
            self.state['ip_player']['hand'][0], self.state['ip_player']['hand'][1], self.state['ip_player']['hand'][2], self.state['ip_player']['hand'][3],
        )
        oop_rank = evaluate_omaha_cards(
            self.state['community_cards'][0], self.state['community_cards'][1], self.state['community_cards'][2], self.state['community_cards'][3], self.state['community_cards'][4],
            self.state['oop_player']['hand'][0], self.state['oop_player']['hand'][1], self.state['oop_player']['hand'][2], self.state['oop_player']['hand'][3],
        )
        result = {
            "ip_hand": self.state["ip_player"]["hand"],
            "oop_hand": self.state["oop_player"]["hand"],
            "community_cards": self.state["community_cards"],
            "pot": self.state["pot"],
        }
        if ip_rank < oop_rank:
            result["winner"] = "IP Player"
            result["winning hand"] = self.state["ip_player"]["hand"]
            self.state["ip_player"]["chips"] += self.state["pot"]
        elif oop_rank < ip_rank:
            result["winner"] = "OOP Player"
            result["winning hand"] = self.state["oop_player"]["hand"]
            self.state["oop_player"]["chips"] += self.state["pot"]
        else:
            result["winner"] = "chop"
            result["winning hand"] = None
            self.state["ip_player"]["chips"] += self.state["pot"] / 2
            self.state["oop_player"]["chips"] += self.state["pot"] / 2
        return result
