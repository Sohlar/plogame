import secrets
import logging
import sys
import numpy as np
from agent import DQNAgent
from phevaluator import evaluate_omaha_cards
from logging_config import setup_logging
import torch

CONST_100bb = 200
CONST_200bb = 400
CONST_300bb = 600
MINIMUM_BET_INCREMENT = 2

setup_logging()


#### Player Class ####
class Player:
    players = []

    def __init__(self, name: str, chips: int) -> None:
        Player.players.append(self)
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
            player.chips = CONST_100bb


class HumanPlayer(Player):
    def get_action(self, valid_actions, max_bet):
        print(f"Maximum Bet: {max_bet}")
        while True:
            action = input(f"Choose an action {valid_actions}: ")
            if action in valid_actions:
                if action == "bet":
                    bet_size = int(input("Enter the bet size: "))
                    return action, bet_size
                return action
            print("Invalid action. Please try again.")


class Deck:
    def __init__(self):
        # fmt: off
        self.cards = [
            "2c", "3c", "4c", "5c", "6c", "7c", "8c", "9c", "Tc", "Jc", "Qc", "Kc", "Ac", 
            "2d", "3d", "4d", "5d", "6d", "7d", "8d", "9d", "Td", "Jd", "Qd", "Kd", "Ad", 
            "2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th", "Jh", "Qh", "Kh", "Ah", 
            "2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s", "Ts", "Js", "Qs", "Ks", "As",
        ]
        # fmt: on

    def shuffle(self):
        secrets.SystemRandom().shuffle(self.cards)


class PokerGame:
    def __init__(self, human_position=None, oop_agent=None, ip_agent=None):
        self.deck = Deck()

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if human_position == "oop":
            self.oop_player = HumanPlayer(name="OOP", chips=200)
            self.ip_player = Player(name="IP", chips=200)
        if human_position == "ip":
            self.oop_player = Player(name="OOP", chips=200)
            self.ip_player = HumanPlayer(name="IP", chips=200)
        else:
            self.oop_player = Player(name="OOP", chips=200)
            self.ip_player = Player(name="IP", chips=200)

        self.initialize_game_state()

        # Initialize DQN agents
        self.state_size = 7 + (5 * 2) + 2 * 4 * 2
        self.action_size = 4  # check, call, bet, fold

        if oop_agent:
            self.oop_agent = oop_agent
            self.oop_agent.name = "OOP"
        else:
            self.oop_agent = DQNAgent(self.state_size, self.action_size)
            self.oop_agent.name = "OOP"
        if ip_agent:
            self.ip_agent = ip_agent
            self.oop_agent.name = "IP"
        else:
            self.ip_agent = DQNAgent(self.state_size, self.action_size)
            self.oop_agent.name = "IP"

        self.oop_agent.model.to(self.device)
        self.ip_agent.model.to(self.device)

        self.oop_loss = None
        self.ip_loss = None
        self.oop_cumulative_reward = 0
        self.ip_cumulative_reward = 0

        logging.info("PokerGame initialized")

    def get_state_representation(self, state=None):
        # Convert the game state to a numerical representation for the DQN
        if state is None:
            state = self.get_game_state()
        representation = [
            float(state["pot"]),
            float(len(state["community_cards"])),
            float(state["current_bet"]),
            float(state["oop_player"]["chips"]),
            float(state["ip_player"]["chips"]),
            float(state["oop_player"]["committed"]),
            float(state["ip_player"]["committed"]),
        ]
        # Add encoded representations of community cards and player hands
        community_cards = state["community_cards"] + [""] * (
            5 - len(state["community_cards"])
        )
        for card in community_cards:
            representation.extend(self.encode_card(card))

        for card in state["oop_player"]["hand"]:
            representation.extend(self.encode_card(card))

        for card in state["ip_player"]["hand"]:
            representation.extend(self.encode_card(card))

        assert len(representation) == self.state_size, f"State size { self.state_size }"
        # representation.extend([0, 0] * (self.state_size - len(representation)))

        return torch.FloatTensor(representation)

    def encode_card(self, card):
        if not card:
            return [0, 0]
        # Simple encoding: rank (2-14) and suit (0-3)
        ranks = "23456789TJQKA"
        suits = "cdhs"
        return (ranks.index(card[0]) + 2, suits.index(card[1]))

    def initialize_game_state(self):
        self.community_cards = []
        self.pot = 3
        self.hand_over = False
        self.current_bet = 2
        self.num_actions = 0
        self.last_action = "bet"
        self.current_player = self.ip_player
        self.num_active_players = 2
        self.ip_committed = 1
        self.oop_committed = 2
        self.street = "preflop"
        self.waiting_for_action = False
        self.is_allin = False

    def deal_cards(self):
        for player in [self.oop_player, self.ip_player]:
            player.hand = [self.deck.cards.pop() for _ in range(4)]

    def start_new_hand(self):
        self.initialize_game_state()
        self.reset_hands()
        self.deck.shuffle()
        self.pot = 3
        self.oop_player.chips = 198
        self.ip_player.chips = 199
        self.deal_cards()
        return self.get_game_state()

    def play_hand(self):
        logging.info("Starting new hand")
        game_state = self.start_new_hand()

        print(f"Your hand: {self.get_player_hand()}")

        game_state = self.preflop_betting()
        if game_state["is_allin"]:
            self.deal_community_cards(5)
            game_state = self.determine_showdown_winner()
            game_state["hand_over"] = True

        if game_state["is_allin"]:
            self.deal_community_cards(5)
            game_state = self.determine_showdown_winner()
            game_state["hand_over"] = True

        if not game_state["hand_over"]:
            print("\nDEALING FLOP\n")
            game_state = self.deal_flop()

            if game_state["is_allin"]:
                self.deal_community_cards(2)
                game_state = self.determine_showdown_winner()
                game_state["hand_over"] = True

            if not game_state["hand_over"]:
                print("\nDEALING TURN\n")
                game_state = self.deal_turn()

                if game_state["is_allin"]:
                    self.deal_community_cards(1)
                    game_state = self.determine_showdown_winner()
                    game_state["hand_over"] = True

                if not game_state["hand_over"]:
                    print("\nDEALING RIVER\n")
                    game_state = self.deal_river()

                    if not game_state["hand_over"]:
                        game_state = self.determine_showdown_winner()

        return game_state

    def get_player_hand(self):
        if isinstance(self.oop_player, HumanPlayer):
            return self.oop_player.hand
        elif isinstance(self.ip_player, HumanPlayer):
            return self.ip_player.hand
        else:
            return None

    def determine_showdown_winner(self):
        logging.info("Determining Showdown Winner")
        print(f"\nIP Tables: {self.ip_player.hand}")
        print(f"\nOOP Tables: {self.oop_player.hand}\n")
        updated_state = self.get_game_state()
        # fmt: off
        ip_rank = evaluate_omaha_cards(
            self.community_cards[0], self.community_cards[1], self.community_cards[2], self.community_cards[3], self.community_cards[4],
            self.ip_player.hand[0], self.ip_player.hand[1], self.ip_player.hand[2], self.ip_player.hand[3],
        )
        oop_rank = evaluate_omaha_cards(
            self.community_cards[0], self.community_cards[1], self.community_cards[2], self.community_cards[3], self.community_cards[4],
            self.oop_player.hand[0], self.oop_player.hand[1], self.oop_player.hand[2], self.oop_player.hand[3],
        )
        # fmt: on

        if ip_rank < oop_rank:
            print(f"{updated_state['ip_player']['name']} wins {self.pot}")
            # print(f"{self.ip_player.hand}")
            updated_state["ip_player"]["chips"] += self.pot
        elif oop_rank < ip_rank:
            print(f"{updated_state['oop_player']['name']} wins {self.pot}")
            updated_state["oop_player"]["chips"] += self.pot
        else:
            updated_state["ip_player"]["chips"] += self.pot / 2
            updated_state["oop_player"]["chips"] += self.pot / 2
            print(f"Hand ends in a tie, split pot of {self.pot}")


        # print(f"\nCommunity Cards: {self.community_cards}")

        updated_state["hand_over"] = True

        return updated_state

    def calculate_rewards(self, game_state):
        oop_reward = game_state["oop_player"]["chips"] - CONST_100bb
        ip_reward = game_state["ip_player"]["chips"] - CONST_100bb

        total_reward = oop_reward + ip_reward
        oop_reward -= total_reward / 2
        ip_reward -= total_reward / 2

        return oop_reward, ip_reward

    def deal_flop(self):
        logging.info("Dealing flop")
        self.deal_community_cards(3)
        return self.postflop_betting(street="flop")

    def deal_turn(self):
        logging.info("Dealing Turn")
        self.deal_community_cards(1)
        return self.postflop_betting(street="turn")

    def deal_river(self):
        logging.info("Dealing River")
        self.deal_community_cards(1)
        return self.postflop_betting(street="river")

    def deal_community_cards(self, num_cards):
        self.community_cards.extend([self.deck.cards.pop() for _ in range(num_cards)])

    def reset_hands(self):
        logging.info("Resetting Hands")
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.oop_player.hand = []
        self.ip_player.hand = []
        self.current_bet = 2
        self.num_actions = 0
        self.last_action = None
        self.hand_over = False
        self.is_allin = False

    def get_game_state(self):
        return {
            "pot": self.pot,
            "community_cards": self.community_cards,
            "current_player": self.current_player.name,
            "current_bet": self.current_bet,
            "last_action": self.last_action,
            "num_actions": self.num_actions,
            "hand_over": self.hand_over,
            "waiting_for_action": self.waiting_for_action,
            "is_allin": self.is_allin,
            "oop_player": {
                "name": self.oop_player.name,
                "chips": self.oop_player.chips,
                "hand": self.oop_player.hand,
                "committed": self.oop_committed,
            },
            "ip_player": {
                "name": self.ip_player.name,
                "chips": self.ip_player.chips,
                "hand": self.ip_player.hand,
                "committed": self.ip_committed,
            },
        }

    def get_public_game_state(self):
        return {
            "pot": self.pot,
            "community_cards": self.community_cards,
            "current_player": self.current_player.name,
            "current_bet": self.current_bet,
            "last_action": self.last_action,
            "num_actions": self.num_actions,
            "hand_over": self.hand_over,
            "waiting_for_action": self.waiting_for_action,
            "oop_player": {
                "name": self.oop_player.name,
                "chips": self.oop_player.chips,
                "committed": self.oop_committed,
            },
            "ip_player": {
                "name": self.ip_player.name,
                "chips": self.ip_player.chips,
                "committed": self.ip_committed,
            },
        }

    def get_private_game_state(self):
        return {
            "oop_player": {
                "hand": self.oop_player.hand,
            },
            "ip_player": {
                "hand": self.ip_player.hand,
            },
        }

    def get_player_action(self, valid_actions, max_bet, min_bet):
        logging.info(f"Getting {self.current_player.name}'s Action: ({valid_actions})")
        if isinstance(self.current_player, HumanPlayer):
            return self.current_player.get_action(valid_actions, max_bet)
        else:
            state = self.get_state_representation()
            if self.current_player == self.oop_player:
                action, bet_size = self.oop_agent.act(state, valid_actions, max_bet, min_bet)
                player = "oop"
                agent = self.oop_agent
            else:
                action, bet_size = self.ip_agent.act(state, valid_actions, max_bet, min_bet)
                player = "ip"
                agent = self.ip_agent

            action_map = {0: "fold", 1: "check", 2: "call", 3: "bet"}
            chosen_action = action_map[action]

        if chosen_action == "bet":
            logging.info(f"Bet size: {bet_size}")
            logging.info(f"Bet Max: {max_bet}")
            return chosen_action, min(bet_size, max_bet)
        return chosen_action

    def preflop_betting(self):
        self.current_bet, self.num_actions = 2, 0

        logging.info("starting preflop betting")

        while True:
            game_state = self.get_game_state()
            state_representation = self.get_state_representation()

            if self.hand_over or self.num_active_players == 1:
                self.current_player.chips += self.pot
                game_state = self.get_game_state()
                game_state["message"] = f"{self.current_player.name} wins ${self.pot}"
                game_state["hand_over"] = True
                return game_state

            all_players_acted = self.num_actions >= self.num_active_players
            all_bets_settled = self.oop_player.chips == self.ip_player.chips
            if all_players_acted and all_bets_settled:
                game_state = self.get_game_state()
                game_state["message"] = "preflop betting complete"
                return game_state

            logging.info(f"current state: {game_state}")
            print(f"\ncommunity cards: {game_state['community_cards']}")
            print(f"pot: {game_state['pot']}")
            print(f"your hand: {self.get_player_hand()}")
            print( f"ip chips: {game_state[self.ip_player.name.lower() + '_player']['chips']}")
            print( f"oop chips: {game_state[self.oop_player.name.lower() + '_player']['chips']}")

            # instead of prompting for input, we'll return the game state
            valid_actions, max_bet, min_bet = self.get_valid_preflop_actions()
            # print(f"finished getting valid actions: {valid_actions}")
            action = self.get_player_action(valid_actions, max_bet, min_bet)

            # print(f"returned tuple: {action}")
            if isinstance(action, tuple):
                action, bet_size = action
            else:
                bet_size = None
            # print(f"finished getting action: {action}")
            # print(f"bet size: {bet_size}")

            action_int = self.action_to_int(action)

            self.process_preflop_action(action, bet_size)
        return game_state

    def action_to_int(self, action):
        action_map = {"fold": 0, "check": 1, "call": 2, "bet": 3}
        return action_map[action]

    def process_preflop_action(self, action, bet_size=None):
        logging.info(f"Processing preflop action: {action}")
        # This method will be called from the server to process each action
        # print(f"Processing action: {action}")

        if action == "bet":
            print("Handling Bet")
            self.handle_preflop_bet(bet_size)
        if action == "call":
            print("Handling Call")
            self.handle_preflop_call()
        if action == "check":
            self.handle_preflop_check()
            print("Handling Check")
        if action == "fold":
            print("handling Fold")
            self.handle_fold()

        self.switch_players()

    def get_valid_preflop_actions(self):
        # fmt: off
        valid_actions =[]
        if self.oop_player.chips == 0 or self.ip_player.chips == 0: #Facing All in
            valid_actions.extend(["call", "fold"])
        if self.current_player == self.ip_player and self.num_actions == 0: #Preflop Open
            valid_actions.extend(["call", "bet", "fold"])
        elif self.current_player == self.oop_player and self.last_action == "call": #Facing Open limp
            valid_actions.extend(["check", "bet"])
        else:
            valid_actions.extend(["call", "bet", "fold"])
        # fmt: on
        max_bet = self.calculate_max_preflop_bet_size()
        min_bet = max(MINIMUM_BET_INCREMENT, min(self.current_bet * 2, self.current_player.chips))
        return valid_actions, max_bet, min_bet

    def calculate_max_preflop_bet_size(self):
        max_bet = 0
        state = self.get_game_state()
        pot = state["pot"]
        current_bet = state["current_bet"]
        player_chips = self.current_player.chips
        player_committed = (
            self.oop_committed
            if self.current_player == self.oop_player
            else self.ip_committed
        )

        # print(f"{type(current_bet)}\n{type(pot)}\n{type(player_committed)}")

        if current_bet == 0:
            max_bet = pot
        else:
            max_raise = 3 * current_bet + pot - player_committed

            max_bet = min(max_raise, player_chips)

        max_bet = (max_bet // MINIMUM_BET_INCREMENT) * MINIMUM_BET_INCREMENT
        max_bet = min(self.current_player.chips, 3 * state["current_bet"])
        return max_bet

    def calculate_max_postflop_bet_size(self, initial_pot):
        max_bet = 0
        state = self.get_game_state()
        pot = state["pot"]
        print(f"POT: {pot}")
        current_bet = state["current_bet"]
        print(f"CURRENT_BET: {current_bet}")
        player_chips = self.current_player.chips
        player_committed = (
            self.oop_committed
            if self.current_player == self.oop_player
            else self.ip_committed
        )

        opponent_committed = (
            self.oop_committed
            if self.current_player == self.ip_player
            else self.ip_committed
        )

        # print(f"{type(current_bet)}\n{type(pot)}\n{type(player_committed)}")
        to_call = opponent_committed - player_committed


        if current_bet == 0:
            max_bet = min(initial_pot, player_chips)
        else:
            max_raise = 3 * current_bet + initial_pot 
            max_bet = min(max_raise, player_chips)

        #Could include the min bet to be set here as well
        return min(max_bet, player_chips)

    def handle_preflop_bet(self, bet_size=None):
        logging.info(f"Handling preflop bet for {self.current_player.name}")
        is_allin, bet_amount = self.calculate_preflop_bet_size()
        # logging.info(f"\n\nis_allin: {is_allin}  bet_amount: {bet_amount}\n\n")
        print(f"bet amount: {bet_amount}")
        if not is_allin:
            if self.current_player.name == self.ip_player.name:
                self.current_player.chips -= bet_amount - self.ip_committed
                self.pot += bet_amount - self.ip_committed
                self.ip_committed = bet_amount
                self.current_bet = bet_amount
            else:
                self.current_player.chips -= bet_amount - self.oop_committed
                self.pot += bet_amount - self.oop_committed
                self.oop_committed = bet_amount
                self.current_bet = bet_amount
        else:
            self.is_allin = True
            if self.current_player.name == self.ip_player.name:
                self.ip_committed += self.current_player.chips
            else:
                self.oop_committed += self.current_player.chips
            self.pot += self.current_player.chips
            self.current_player.chips = 0
        self.num_actions += 1
        self.last_action = "bet"

    def handle_preflop_call(self):
        logging.info(f"Handling preflop call for {self.current_player.name}")
        if self.current_player == self.ip_player and self.num_actions == 0:
            self.current_player.chips -= 1
            self.ip_committed += 1
            self.pot += 1
        else:
            if self.current_player.name == self.oop_player.name:
                diff = self.ip_committed - self.oop_committed
                self.oop_committed += diff
            else:
                diff = self.oop_committed - self.ip_committed
                self.ip_committed += diff
            self.current_player.chips -= diff
            self.pot += diff
        self.num_actions += 1
        self.last_action = "call"

    def handle_preflop_check(self):
        logging.info(f"Handling preflop check from {self.current_player.name}")
        if self.current_player == self.oop_player and self.last_action == "call":
            self.num_actions += 1
            self.last_action = "check"

    def calculate_preflop_bet_size(self, bet_size=None):
        state = self.get_game_state()
        all_in = False
        is_raise = True
        if is_raise:
            # If it's a raise, the bet size is 3 times the last raise plus the current pot size
            bet_size = 3 * state["current_bet"]
        if self.current_player.chips < bet_size:
            bet_size = self.current_player.chips
            all_in = True

        return all_in, bet_size

    def postflop_betting(self, street):
        state = self.get_game_state()
        initial_pot = state["pot"]
        logging.info("Starting Postflop Betting")
        self.current_bet = 0
        self.num_actions = 0
        self.current_player = self.oop_player

        oop_committed = 0
        ip_committed = 0
        print(f"Community Cards: {state['community_cards']}")

        while True:
            state = self.get_game_state()

            logging.info(f"Current State: {state}")

            if self.hand_over or self.num_active_players == 1:
                self.current_player.chips += self.pot
                game_state = self.get_game_state()
                game_state["message"] = f"{self.current_player.name} wins ${self.pot}"
                game_state["hand_over"] = True
                return game_state

            all_players_acted = self.num_actions >= self.num_active_players
            all_bets_settled = self.oop_committed == self.ip_committed
            if all_players_acted and all_bets_settled:
                game_state = self.get_game_state()
                game_state["message"] = f"{street.capitalize()} betting complete"
                return game_state

            valid_actions, min_bet = self.get_valid_postflop_actions()
            max_bet = self.calculate_max_postflop_bet_size(initial_pot)
            action = self.get_player_action(valid_actions, max_bet, min_bet)

            if isinstance(action, tuple):
                action, bet_size = action
                print(f"Received bet size: {bet_size}")
                logging.info(f"Received bet size: {bet_size}")
            else:
                bet_size = None
            action_int = self.action_to_int(action)


            self.process_postflop_action(action, bet_size)

            if self.last_action == "call" and self.oop_committed == self.ip_committed:
                game_state = self.get_game_state()
                game_state["message"] = f"{street.capitalize()} betting complete"
                return game_state
        return game_state

    def process_postflop_action(self, action, bet_size=None):
        logging.info(f"Processing Postflop Action: {action}")
        # print(f"Bet Size: {bet_size}")

        if action == "check":
            self.handle_postflop_check()
        elif action == "bet":
            self.handle_postflop_bet(bet_size)
        elif action == "call":
            self.handle_postflop_call()
        elif action == "fold":
            self.handle_fold()

        self.switch_players()

    def get_valid_postflop_actions(self):
        valid_actions = []
        min_bet = max(MINIMUM_BET_INCREMENT, min(self.current_bet * 2, self.current_player.chips))
        # print(f"GET VALID POSTFLOP ACTIONS max_bet {max_bet}")

        if self.oop_player.chips == 0 or self.ip_player.chips == 0:
            valid_actions = ["call", "fold"]
        if self.current_bet == 0:
            valid_actions = ["check", "bet"]
        else:
            valid_actions = ["call", "bet", "fold"]

        return valid_actions, min_bet

    def handle_postflop_bet(self, bet_size=MINIMUM_BET_INCREMENT):
        logging.info(
            f"Handling postflop bet of {bet_size} for {self.current_player.name}"
        )

        print(f"Handline postflop bet of {bet_size} for {self.current_player.name}")

        if self.current_player.name == self.ip_player.name:
            self.current_player.chips -= bet_size
            self.pot += bet_size
            self.ip_committed += bet_size
            self.current_bet = bet_size
        else:
            self.current_player.chips -= bet_size
            self.pot += bet_size
            self.oop_committed += bet_size
            self.current_bet = bet_size

    def handle_postflop_call(self):
        logging.info("Handling postflop CALL for {self.current_player.name}")
        print(f"Handling postflop CALL for {self.current_player.name}")
        if self.current_player.name == self.oop_player.name:
            call_amount = self.oop_committed - self.ip_committed
        else:
            call_amount = self.ip_committed - self.oop_committed
        if call_amount <= self.current_player.chips:
            self.current_player.chips += call_amount
            self.pot -= call_amount
            if self.current_player == self.oop_player:
                self.oop_committed = self.ip_committed
            else:
                self.ip_committed = self.oop_committed
        else:
            # This is prone to bug. Only works under equal starting stacks.
            all_in_amount = self.current_player.chips
            self.current_player.chips = 0
            self.pot += all_in_amount
            if self.current_player == self.oop_player:
                self.oop_committed += all_in_amount
            else:
                self.ip_committed += all_in_amount
            """
            other_player = (
                self.ip_player
                if self.current_player == self.oop_player
                else self.oop_player
            )
            other_player.chips += difference
            self.pot -= difference
            """
        self.num_actions += 1
        self.last_action = "call"

    def handle_postflop_check(self):
        logging.info(f"Handling postflop CHECK for {self.current_player.name}")
        print(f"Handling postflop CHECK for {self.current_player.name}")
        self.num_actions += 1
        self.last_action = "check"

    def handle_fold(self):
        logging.info(f"Handling postflop FOLD for {self.current_player.name}")
        print(f"Handling postflop FOLD for {self.current_player.name}")
        self.num_active_players -= 1
        self.hand_over = True

    def calculate_postflop_bet_size(self):
        all_in = False
        max_bet = self.calculate_max_postflop_bet_size()

        if bet_size is None:
            if self.last_action == "bet":
                # If it's a raise, the bet size is 3 times the last raise plus the current pot size
                bet_size = min(2 * self.current_bet + self.pot, max_bet)
            else:
                # If it's a standard bet, the bet size is equal to the current pot size
                bet_size = (self.pot, max_bet)

        if self.current_player.chips < bet_size:
            bet_size = self.current_player.chips
            all_in = True

        return all_in, bet_size

    def switch_players(self):
        self.current_player = (
            self.oop_player
            if self.current_player.name == self.ip_player.name
            else self.ip_player
        )

    def play_game(self):
        print("Welcome to Omaha Poker!")
        while True:
            print("\nStarting a new hand...")
            game_state = self.play_hand()

            play_again = input("Do you want to play another hand? (y/n): ").lower()
            if play_again != 'y':
                break

        print("Thanks for playing!")


def main():
    print("Welcome to Omaha Poker!")
    
    while True:
        human_position = input("Choose your position (oop/ip): ").lower()
        if human_position in ['oop', 'ip']:
            break
        print("Invalid position. Please choose 'oop' or 'ip'.")

    game = PokerGame(human_position)
    game.play_game()

if __name__ == "__main__":
    main()