import secrets
from phevaluator import evaluate_omaha_cards


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
        # fmt: on

    def shuffle(self):
        secrets.SystemRandom().shuffle(self.cards)


class PokerGame:
    def __init__(self):
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.oop_player = Player(name="OOP", chips=200)
        self.ip_player = Player(name="IP", chips=200)
        self.hand_over = False

    def deal_cards(self):
        for player in [self.oop_player, self.ip_player]:
            player.hand = [self.deck.cards.pop() for _ in range(4)]

    def start_new_hand(self):
        self.reset_hands()
        self.deck.shuffle()
        self.pot = 3
        self.oop_player.chips = 198
        self.ip_player.chips = 199
        self.deal_cards()

    def play_hand(self):
        self.start_new_hand()
        game_state = self.preflop_betting()
        if game_state["hand_over"]:
            return game_state

        print("Entering flop")
        game_state = self.deal_flop()
        if game_state["hand_over"]:
            return game_state

        game_state = self.deal_turn()
        if game_state["hand_over"]:
            return game_state

        game_state = self.deal_river()
        if game_state["hand_over"]:
            return game_state

        return self.determine_showdown_winner()

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
        self.community_cards = []
        self.pot = 0
        self.oop_player.hand = []
        self.ip_player.hand = []
        self.current_bet = []
        self.num_actions = 0
        self.last_action = None
        self.hand_over = False

    def determine_showdown_winner(self):
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
        result = {
            "ip_hand": self.ip_player.hand,
            "oop_hand": self.oop_player.hand,
            "community_cards": self.community_cards,
            "pot": self.pot,
        }

        if ip_rank < oop_rank:
            result["winner"] = "IP Player"
            result["winning hand"] = self.ip_player.hand
        elif oop_rank < ip_rank:
            result["winner"] = "OOP Player"
            result["winning hand"] = self.oop_player.hand
        else:
            result["winner"] = "chop"
            result["winning hand"] = None

        return result

    def get_game_state(self):
        return {
            "pot": self.pot,
            "community_cards": self.community_cards,
            "current_player": self.current_player.name,
            "current_bet": self.current_bet,
            "last_action": self.last_action,
            "num_actions": self.num_actions,
            "hand_over": self.hand_over,
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

    def get_player_action(self, valid_actions):
        while True:
            print(f"\nCurrent player: {self.current_player.name}")
            print(f"Pot: ${self.pot}")
            print(f"Current bet: ${self.current_bet}")
            print(f"IP committed: ${self.ip_committed}")
            print(f"OOP committed: ${self.oop_committed}")
            print(f"Your chips: ${self.current_player.chips}")
            print(f"Valid actions: {', '.join(valid_actions)}")

            action = input(f"{self.current_player.name}, choose an action: ").lower()

            if action in valid_actions:
                return action
            else:
                print("Invalid action. Please try again.")

    def preflop_betting(self):
        self.num_active_players = len(
            [p for p in [self.oop_player, self.ip_player] if p.chips > 0]
        )
        self.ip_committed, self.oop_committed = 1, 2
        self.current_bet, self.num_actions = 2, 0
        self.last_action = "bet"
        self.current_player = self.ip_player
        self.hand_over = False

        while True:
            game_state = self.get_game_state()

            if self.hand_over or self.num_active_players == 1:
                self.current_player.chips += self.pot
                game_state["message"] = f"{self.current_player.name} wins ${self.pot}"
                game_state["hand_over"] = True
                return game_state

            all_players_acted = self.num_actions >= self.num_active_players
            all_bets_settled = self.oop_player.chips == self.ip_player.chips
            print(f"\n{all_players_acted}{all_bets_settled}\n")
            if all_players_acted and all_bets_settled:
                print("Preflop betting complete")
                game_state["message"] = "Preflop betting complete"
                return game_state

            # Instead of prompting for input, we'll return the game state
            valid_actions = self.get_valid_preflop_actions()
            action = self.get_player_action(valid_actions)
            self.process_preflop_action(action)
        return game_state

    def postflop_betting(self, street):
        self.num_active_players = len(
            [p for p in [self.oop_player, self.ip_player] if p.chips > 0]
        )
        self.ip_committed = 0
        self.oop_committed = 0
        self.current_bet = 0
        self.num_actions = 0
        self.current_player = self.oop_player
        self.hand_over = False

        while True:
            game_state = self.get_game_state()
            game_state["street"] = street

            if self.hand_over or self.num_active_players == 1:
                self.current_player.chips += self.pot
                return {
                    "message": f"{self.current_player.name} wins ${self.pot}",
                    "hand_over": True,
                }

            all_players_acted = self.num_actions >= self.num_active_players
            all_bets_settled = self.oop_player.chips == self.ip_player.chips
            if all_players_acted and all_bets_settled:
                game_state["message"] = f"{street.capitalize()} betting complete"
                return game_state

            valid_actions = self.get_valid_postflop_actions()
            action = self.get_player_action(valid_actions)
            self.process_postflop_action(action)
        return game_state

    def process_preflop_action(self, action):
        # This method will be called from the server to process each action
        if action not in self.get_valid_preflop_actions():
            return {"error: Invalid Action"}

        if action == "bet":
            self.handle_preflop_bet()
        if action == "call":
            self.handle_preflop_call()
        if action == "check":
            self.handle_preflop_check()
        if action == "fold":
            self.handle_fold()

        self.switch_players()

    def process_postflop_action(self, action):
        if action not in self.get_valid_postflop_actions():
            return {"error": "Invalid Action"}

        if action == "check":
            self.handle_postflop_check()
        elif action == "bet":
            self.handle_postflop_bet()
        elif action == "call":
            self.handle_postflop_call()
        elif action == "fold":
            self.handle_fold()

        print("switching players")
        self.switch_players()

    def get_valid_preflop_actions(self):
        # fmt: off
        if self.oop_player.chips == 0 or self.ip_player.chips == 0: #Facing All in
            return ["call", "fold"]
        if self.current_player == self.ip_player and self.num_actions == 0: #Preflop Open
            return ["call", "bet", "fold"]
        elif self.current_player == self.oop_player and self.last_action == "call": #Facing Open limp
            return ["check", "bet"]
        else:
            return ["call", "bet", "fold"]
        # fmt: on

    def get_valid_postflop_actions(self):
        if self.oop_player.chips == 0 or self.ip_player.chips == 0:
            return ["call", "fold"]
        if self.current_bet == 0:
            return ["check", "bet", "fold"]
        else:
            return ["call", "bet", "fold"]

    def handle_preflop_bet(self):
        is_allin, bet_amount = self.calculate_preflop_bet_size()
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
            if self.current_player.name == self.ip_player.name:
                self.ip_committed += self.current_player.chips
            else:
                self.oop_committed += self.current_player.chips
            self.pot += self.current_player.chips
            self.current_player.chips = 0
        self.num_actions += 1
        self.last_action = "bet"

    def handle_postflop_bet(self):
        is_allin, bet_amount = self.calculate_postflop_bet_size()
        self.current_player.chips -= bet_amount
        self.pot += bet_amount
        self.current_bet = bet_amount
        if self.current_player == self.ip_player:
            self.ip_committed += bet_amount
        else:
            self.oop_committed += bet_amount
        self.num_actions += 1
        self.last_action = "bet"

    def handle_preflop_call(self):
        if self.current_player == self.ip_player and self.num_actions == 0:
            self.current_player.chips -= 1
            self.pot += 1
        else:
            if self.current_player.name == self.oop_player.name:
                diff = self.ip_committed - self.oop_committed
                print(f"\n{diff}")
                self.oop_committed += diff
                print(f"\n{self.oop_committed}")
            else:
                diff = self.oop_committed - self.ip_committed
                print(f"\n{diff}")
                self.ip_committed += diff
                print(f"\n{self.ip_committed}")
            self.current_player.chips -= diff
            self.pot += diff
        self.num_actions += 1
        self.last_action = "call"

    def handle_postflop_call(self):
        call_amount = self.current_bet
        if call_amount <= self.current_player.chips:
            self.current_player.chips -= call_amount
            self.pot += call_amount
        else:
            all_in_amount = self.current_player.chips
            self.current_player.chips = 0
            self.pot += all_in_amount
            difference = call_amount - all_in_amount
            other_player = (
                self.ip_player
                if self.current_player == self.oop_player
                else self.oop_player
            )
            other_player.chips += difference
            self.pot -= difference
        self.num_actions += 1
        self.last_action = "call"

    def handle_preflop_check(self):
        if self.current_player == self.oop_player and self.last_action == "call":
            self.num_actions += 1
            self.last_action = "check"

    def handle_postflop_check(self):
        self.num_actions += 1
        self.last_action = "check"

    def handle_fold(self):
        self.num_active_players -= 1
        self.hand_over = True

    def switch_players(self):
        self.current_player = (
            self.oop_player if self.current_player == self.ip_player else self.ip_player
        )

    def calculate_preflop_bet_size(self):
        all_in = False
        is_raise = True
        if is_raise:
            # If it's a raise, the bet size is 3 times the last raise plus the current pot size
            bet_size = 3 * self.current_bet
        print(f"\n{self.current_player.chips} betsize: {bet_size}")
        if self.current_player.chips < bet_size:
            bet_size = self.current_player.chips
            all_in = True

        return all_in, bet_size

    def calculate_postflop_bet_size(self):
        all_in = False
        if self.last_action == "bet":
            # If it's a raise, the bet size is 3 times the last raise plus the current pot size
            bet_size = 2 * self.current_bet + self.pot
        else:
            # If it's a standard bet, the bet size is equal to the current pot size
            bet_size = self.pot

        if self.current_player.chips < bet_size:
            bet_size = self.current_player.chips
            all_in = True

        return all_in, bet_size


def main():
    game = PokerGame()

    print("Welcome to the Poker Game!")
    print("Players: OOP (Out of Position) and IP (In Position)")
    print("Starting chips: 200 each")
    print("Blinds: 1/2\n")

    while True:
        print("\n--- New Hand ---")
        result = game.play_hand()

        if "message" in result:
            print(result["message"])
        else:
            print("Showdown!")
            print(f"Community cards: {', '.join(result['community_cards'])}")
            print(f"OOP hand: {', '.join(result['oop_hand'])}")
            print(f"IP hand: {', '.join(result['ip_hand'])}")
            print(f"Winner: {result['winner']}")
            if result["winner"] != "chop":
                print(f"Winning hand: {', '.join(result['winning hand'])}")
            print(f"Pot: ${result['pot']}")

        print("\nCurrent chip counts:")
        print(f"OOP: ${game.oop_player.chips}")
        print(f"IP: ${game.ip_player.chips}")

        play_again = input("\nPlay another hand? (y/n): ").lower()
        if play_again != "y":
            break

    print("\nThanks for playing!")


if __name__ == "__main__":
    main()
