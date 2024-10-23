import secrets
from typing import List, Tuple, Dict, Optional, Union
import random
import logging
import numpy as np
from agent import DQNAgent
from phevaluator import evaluate_omaha_cards
from logging_config import setup_logging
import torch
from metrics import (
    episode_reward,
    cumulative_reward,
    player_chips,
    pot_size,
    community_cards,
    episodes_completed,
    action_taken,
    q_value,
    epsilon,
    loss,
    bet_size_metric,
    update_bet_size,
)

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
        self.hand: List[str] = []

    @classmethod
    def get_players(cls):
        return cls.players

    def reset_hands(self):
        [player.hand.clear() for player in Player.get_players()]

    def reset_chips(self):
        for player in Player.get_players():
            player.chips = CONST_100bb


class HumanPlayer(Player):
    def get_action(self, valid_actions, max_bet):
        print(f"Valid actions: {valid_actions}")
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

        self.state_size = 7 + (5 * 2) + (2 * 4 * 2)
        self.action_size = 4  # check, call, bet, fold

        # Initialize DQN agents
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

    def initialize_game_state(self):
        self.community_cards = []
        self.hand_over = False
        self.current_bet = 0
        self.num_actions = 0
        self.last_action = None
        self.current_player = self.oop_player
        self.num_active_players = 2
        self.street = "river"
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

    def start_new_river_scenario(self):
        self.initialize_game_state()
        self.reset_hands()
        self.deck.shuffle()
        self.pot = random.randrange(4,396, 4)
        player_chips = int((400 - self.pot) / 2)
        self.oop_player.chips = player_chips
        self.ip_player.chips = player_chips
        committed = self.pot / 2
        self.ip_committed = committed
        self.oop_committed = committed
        self.deal_cards()
        return self.get_game_state()

    def play_hand(self):
        logging.info("Starting new hand")
        print("Starting new hand")
        game_state = self.start_new_river_scenario()

        oop_experiences = []
        ip_experiences = []

        self.deal_community_cards(4)
        game_state, round_experiences = self.deal_river()
        game_state = self.determine_showdown_winner()
        game_state["hand_over"] = True

        oop_experiences.extend(round_experiences[0])
        ip_experiences.extend(round_experiences[1])

        print("\n" + "="*20)

        final_state = self.get_state_representation()
        oop_reward, ip_reward = self.calculate_rewards(game_state)
        logging.info(f"OOP Reward: {oop_reward}")
        logging.info(f"IP Reward: {ip_reward}")

        for state, action, valid_actions, bet_size, max_bet in oop_experiences:
            self.oop_agent.remember(state, action, oop_reward, final_state, True)
        for state, action, valid_actions, bet_size, max_bet in ip_experiences:
            self.ip_agent.remember(state, action, ip_reward, final_state, True)

        loss.labels(player="oop").set(self.oop_loss if self.oop_loss is not None else 0)
        loss.labels(player="ip").set(self.ip_loss if self.ip_loss is not None else 0)

        episode_reward.labels(player="oop").set(oop_reward)
        episode_reward.labels(player="ip").set(ip_reward)

        player_chips.labels(player="oop").set(self.oop_player.chips)
        player_chips.labels(player="ip").set(self.ip_player.chips)
        pot_size.set(self.pot)
        community_cards.set(len(self.community_cards))
        episodes_completed.inc()

        return game_state, oop_reward, ip_reward

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
            updated_state["ip_player"]["chips"] += self.pot
        elif oop_rank < ip_rank:
            updated_state["oop_player"]["chips"] += self.pot
        else:
            updated_state["ip_player"]["chips"] += self.pot / 2
            updated_state["oop_player"]["chips"] += self.pot / 2

        updated_state['pot'] = 0
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
        self.current_bet = 0
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
            state = self.get_state_representation(current_player=self.current_player)
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

            q_value.labels(player).set(np.max(agent.model(state.to(agent.device)).cpu().data.numpy()))
            epsilon.labels(player).set(agent.epsilon)
            print(f"Player: {player}\nAction: {chosen_action}")
            action_taken.labels(player_action=f"{player}_{chosen_action}").inc()

        if chosen_action == "bet":
            logging.info(f"Bet size: {bet_size}")
            logging.info(f"Bet Max: {max_bet}")
            return chosen_action, min(bet_size, max_bet)
        return chosen_action

    def action_to_int(self, action):
        action_map = {"fold": 0, "check": 1, "call": 2, "bet": 3}
        return action_map[action]

    def calculate_max_postflop_bet_size(self, initial_pot):
        max_bet = 0
        state = self.get_game_state()

        current_bet = state["current_bet"]
        player_chips = self.current_player.chips

        if current_bet == 0:
            max_bet = min(initial_pot, player_chips)
        else:
            max_raise = 3 * current_bet + initial_pot
            max_bet = min(max_raise, player_chips)

        #Could include the min bet to be set here as well
        return min(max_bet, player_chips)

    def postflop_betting(self, street):
        logging.info("Starting Postflop Betting")
        state = self.get_game_state()
        initial_pot = state["pot"]
        self.current_bet = 0
        self.num_actions = 0
        self.current_player = self.oop_player
        state['oop_player']['hand_strength'] = self.get_hand_strength(hand=self.oop_player.hand)
        state['ip_player']['hand_strength'] = self.get_hand_strength(hand=self.ip_player.hand)

        oop_experiences = []
        ip_experiences = []

        while True:
            state = self.get_game_state()
            state_representation = self.get_state_representation()

            logging.info(f"Current State: {state}")
            print(f"\nCommunity Cards: {state['community_cards']}")
            print(f"Your Hand: {self.get_player_hand()}")
            print( f"IP Chips: {state[self.ip_player.name.lower() + '_player']['chips']}")
            print( f"OOP Chips: {state[self.oop_player.name.lower() + '_player']['chips']}")
            print(f"Pot: {state['pot']}")

            if self.hand_over or self.num_active_players == 1:
                self.current_player.chips += self.pot
                game_state = self.get_game_state()
                game_state["message"] = f"{self.current_player.name} wins ${self.pot}"
                game_state["hand_over"] = True
                return game_state, (oop_experiences, ip_experiences)

            all_players_acted = self.num_actions >= self.num_active_players
            all_bets_settled = self.oop_committed == self.ip_committed
            if all_players_acted and all_bets_settled:
                game_state = self.get_game_state()
                game_state["message"] = f"{street.capitalize()} betting complete"
                return game_state, (oop_experiences, ip_experiences)

            valid_actions, min_bet = self.get_valid_postflop_actions()
            print(f"{state['current_player']} Valid Actions: {valid_actions}")
            max_bet = self.calculate_max_postflop_bet_size(initial_pot)
            print(f"{state['current_player']} max Bet: {max_bet}")
            action = self.get_player_action(valid_actions, max_bet, min_bet)

            if isinstance(action, tuple):
                action, bet_size = action
                print(f"Action: {action} Bet Size: {bet_size}")
                logging.info(f"Received bet size: {bet_size}")
            else:
                bet_size = None
            action_int = self.action_to_int(action)

            if self.current_player == self.oop_player:
                oop_experiences.append(
                    (state_representation, action_int, valid_actions, bet_size, max_bet)
                )
            else:
                ip_experiences.append(
                    (state_representation, action_int, valid_actions, bet_size, max_bet)
                )

            self.process_postflop_action(action, bet_size)

            if self.last_action == "call" and self.oop_committed == self.ip_committed:
                game_state = self.get_game_state()
                game_state["message"] = f"{street.capitalize()} betting complete"
                return game_state, (oop_experiences, ip_experiences)

    def process_postflop_action(self, action, bet_size: Optional[int] = 0):
        logging.info(f"Processing Postflop Action: {action}")

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

        if self.oop_player.chips == 0.0 or self.ip_player.chips == 0.0:
            valid_actions = ["call", "fold"]
        elif self.current_bet == 0:
            valid_actions = ["check", "bet"]
        else:
            valid_actions = ["call", "bet", "fold"]

        return valid_actions, min_bet

    def handle_postflop_bet(self, bet_size=MINIMUM_BET_INCREMENT):
        logging.info(
            f"Handling postflop bet of {bet_size} for {self.current_player.name}"
        )

        if self.current_player.name == self.ip_player.name:
            self.current_player.chips -= bet_size
            self.pot += bet_size
            self.ip_committed += bet_size
            self.current_bet = bet_size
            bet_size_metric.labels(player="ip", street="postflop").observe(bet_size)
            update_bet_size("ip", bet_size, self.pot)
        else:
            self.current_player.chips -= bet_size
            self.pot += bet_size
            self.oop_committed += bet_size
            self.current_bet = bet_size
            bet_size_metric.labels(player="oop", street="postflop").observe(bet_size)
            update_bet_size("oop", bet_size, self.pot)

    def handle_postflop_call(self):
        logging.info("Handling postflop CALL for {self.current_player.name}")
        if self.current_player.name == self.oop_player.name:
            call_amount = int(self.oop_committed - self.ip_committed)
        else:
            call_amount = int(self.ip_committed - self.oop_committed)
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
        self.num_actions += 1
        self.last_action = "call"

    def handle_postflop_check(self):
        logging.info(f"Handling postflop CHECK for {self.current_player.name}")
        self.num_actions += 1
        self.last_action = "check"

    def handle_fold(self):
        logging.info(f"Handling postflop FOLD for {self.current_player.name}")
        self.num_active_players -= 1
        self.hand_over = True

    def switch_players(self):
        self.current_player = (
            self.oop_player
            if self.current_player.name == self.ip_player.name
            else self.ip_player
        )

    def calculate_state_size(self):
        num_float_values = 7 #pot, current_bet, length of community_cards == street, chips * 2, and committed * 2
        num_community_cards = 5
        num_hand_cards = 4
        num_players = 2
        card_encoding_size = 2

        state_size = (
            num_float_values + (num_community_cards * card_encoding_size) +
            (num_hand_cards * num_players * card_encoding_size)
        )

        return state_size

    def get_state_representation(self, state=None, current_player=None):
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

        if current_player == self.oop_player:
            for card in state["oop_player"]["hand"]:
                representation.extend(self.encode_card(card))
            representation.extend([0, 0] * 4)
        else:
            for card in state["ip_player"]["hand"]:
                representation.extend(self.encode_card(card))
            representation.extend([0, 0] * 4)

        assert len(representation) == self.state_size, f"State size mismatch: expected { self.state_size }"

        return torch.FloatTensor(representation)

    def encode_card(self, card):
        if not card:
            return [0, 0]
        # Simple encoding: rank (2-14) and suit (0-3)
        ranks = "23456789TJQKA"
        suits = "cdhs"
        return (ranks.index(card[0]) + 2, suits.index(card[1]))

    def get_hand_strength(self, hand):
        hand_rank = evaluate_omaha_cards(
            self.community_cards[0], self.community_cards[1], self.community_cards[2], self.community_cards[3], self.community_cards[4],
            hand[0], hand[1], hand[2], hand[3]
        )

        return hand_rank


