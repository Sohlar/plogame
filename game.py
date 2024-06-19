import secrets
from typing import Tuple
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

def calculate_preflop_bet_size(
    pot: int, current_bet: int, player_chips: int
) -> Tuple[bool, int]:
    all_in = False
    is_raise = True
    if is_raise:
        # If it's a raise, the bet size is 3 times the last raise plus the current pot size
        bet_size = 3 * current_bet
    else:
        # If it's a standard bet, the bet size is equal to the current pot size
        bet_size = pot

    if player_chips < bet_size:
        bet_size = player_chips
        all_in = True

    return all_in, bet_size


def calculate_bet_size(
    pot: int, current_bet: int, is_raise: bool, player_chips: int
) -> Tuple[bool, int]:
    all_in = False
    if is_raise:
        # If it's a raise, the bet size is 3 times the last raise plus the current pot size
        bet_size = 3 * current_bet + pot
    else:
        # If it's a standard bet, the bet size is equal to the current pot size
        bet_size = pot

    if player_chips < bet_size:
        bet_size = player_chips
        all_in = True

    return all_in, bet_size


def preflop_betting_round2(
    pot: int, oop_player: Player, ip_player: Player
) -> Tuple[int, Player, Player, bool]:

    num_active_players = len(
        [player for player in Player.get_players() if player.chips > 0]
    )

    ip_committed = 1
    oop_committed = 2
    current_bet = 2
    num_actions = 0
    last_action = "bet"
    current_player = ip_player
    hand_over = False

    while True:
        if hand_over:
            current_player.chips += pot
            print(f"{current_player.name} wins ${pot}")
            return 
        if num_active_players == 1:
            current_player.chips += pot
            print(f"{current_player.name} wins ${pot}")
            pot = 0
            break
        all_players_acted = num_actions >= num_active_players
        all_bets_settled = all(
            player.chips == oop_player.chips for player in Player.get_players()
        )
        if all_players_acted and all_bets_settled:
            break

        # Prompt player for action
        # All in Scenario
        if oop_player.chips == 0 or ip_player.chips == 0:
            valid_actions = ["call", "fold"]
            action = input(f"\n{current_player.name}, enter your action (call, fold): ")
            while action not in valid_actions:
                action = input(
                    f"\n{current_player.name}, enter your action (call, fold): "
                )
            if action.lower() == "call":
                print(f"{current_player.name} calls")
                num_actions += 1
                pot += current_player.chips
                current_player.chips -= current_player.chips
            break

        if current_player == ip_player and num_actions == 0:
            valid_actions = ["call", "bet", "fold"]
            action = input(
                f"\n{current_player.name}, enter your action (call, bet, fold): "
            )
            while action not in valid_actions:
                action = input(
                    f"\n{current_player.name}, enter your action (call, bet, fold): "
                )

        elif current_player == oop_player and last_action == "call":
            valid_actions = ["check", "bet"]
            action = input(f"{current_player.name}, enter your action (check, bet): ")
            while action not in valid_actions:
                action = input(
                    f"\n{current_player.name}, enter your action (check, bet): "
                )
        else:
            valid_actions = ["call", "bet", "fold"]
            action = input(
                f"\n{current_player.name}, enter your action (call, bet, fold): "
            )
            while action not in valid_actions:
                action = input(
                    f"\n{current_player.name}, enter your action (call, bet, fold): "
                )

        if action.lower() == "bet":
            # Player bets or raises
            is_raise = True
            is_allin, bet_amount = calculate_preflop_bet_size(
                pot,
                current_bet,
                player_chips=current_player.chips,
            )
            if not is_allin:
                if current_player.name == ip_player.name:
                    current_player.chips -= bet_amount - ip_committed
                    pot += bet_amount - ip_committed
                    ip_committed = bet_amount
                    current_bet = bet_amount
                    num_actions += 1
                    last_action = "bet"
                else:
                    current_player.chips -= bet_amount - oop_committed
                    pot += bet_amount - oop_committed
                    oop_committed = bet_amount
                    current_bet = bet_amount
                    num_actions += 1
                    last_action = "bet"

                if is_raise:
                    print(f"{current_player.name} raises to {bet_amount}.")
                else:
                    print(f"{current_player.name} bets {bet_amount}.")
            else:
                if current_player.name == ip_player.name:
                    current_player.chips -= bet_amount
                    pot += bet_amount
                    num_actions += 1
                    last_action = "bet"
                else:
                    current_player.chips -= bet_amount
                    pot += bet_amount
                    num_actions += 1
                    last_action = "bet"
                print(f"{current_player.name} is all in for {bet_amount}")

        elif action.lower() == "call":
            if current_player == ip_player and num_actions == 0:
                print(f"{current_player.name} calls")
                num_actions += 1
                last_action = "call"
                current_player.chips -= 1
                pot += 1
            else:
                print(f"{current_player.name} calls")
                num_actions += 1
                if current_player.name == oop_player.name:
                    diff = ip_committed - oop_committed
                    current_player.chips -= diff
                    pot += diff

                else:
                    diff = oop_committed - ip_committed
                    current_player.chips -= diff
                    pot += diff

        elif action.lower() == "check":
            if current_player == oop_player and last_action == "call":
                print(f"{current_player.name} checks")
                num_actions += 1
                last_action = "check"
            else:
                print("Invalid action. You cannot check at this point.")
        elif action.lower() == "fold":
            # Player folds
            num_active_players -= 1
            hand_over = True
            print(f"{current_player.name} folds.")
        else:
            print("Invalid action. Please enter a valid action.")
            continue

        # Switch to the next player
        current_player = oop_player if current_player == ip_player else ip_player
    return pot, ip_player, oop_player, hand_over


def postflop_betting_round(
    street: str, pot: int, oop_player: Player, ip_player: Player
) -> Tuple[int, Player, Player, bool]:
    # Initialize variables
    num_active_players = len(
        [player for player in Player.get_players() if player.chips > 0]
    )
    last_bet = 0
    current_bet = 0
    num_actions = 0

    # Determine the initial player based on the street
    current_player = oop_player

    # Betting loop
    while True:
        # Conditional checks to end betting round
        if num_active_players == 1:
            current_player.chips += pot
            pot = 0
            break
        all_players_acted = num_actions >= num_active_players
        all_bets_settled = all(
            player.chips == oop_player.chips
            for player in Player.get_players()
            if player.chips > 0
        )
        if all_players_acted and all_bets_settled:
            break

        if oop_player.chips == 0 or ip_player.chips == 0:
            valid_actions = ["call", "fold"]
            action = input(f"\n{current_player.name}, enter your action (call, fold): ")
            while action not in valid_actions:
                action = input(
                    f"\n{current_player.name}, enter your action (call, fold): "
                )
            if action.lower() == "call":
                print(f"{current_player.name} calls")
                num_actions += 1
                pot += current_player.chips
                current_player.chips -= current_player.chips
            break

        # Display player's hand
        print(f"{current_player.name}'s hand: {current_player.hand}")

        # Prompt player for action
        if current_bet == 0:
            action = input(
                f"{current_player.name}, enter your action (check, bet, fold): "
            )
        else:
            action = input(
                f"{current_player.name}, enter your action (call, bet, fold): "
            )

        if action.lower() == "check":
            # Player checks
            if current_bet == 0:
                print(f"{current_player.name} checks.")
                num_actions += 1
            else:
                print("Invalid action. You cannot check when there is a bet.")

        elif action.lower() == "call":
            # Player calls
            call_amount = current_bet
            if call_amount <= current_player.chips:
                current_player.chips -= call_amount
                pot += call_amount
                num_actions += 1
                print(f"{current_player.name} calls {call_amount}.")
            else:
                # Player goes all-in with less chips than the call amount
                all_in_amount = current_player.chips
                current_player.chips = 0
                pot += all_in_amount
                num_actions += 1
                print(f"{current_player.name} goes all-in with {all_in_amount}.")
                # Return the difference from the pot back to the original bettor
                difference = call_amount - all_in_amount
                if current_player == oop_player:
                    ip_player.chips += difference
                else:
                    oop_player.chips += difference
                pot -= difference

        elif action.lower() == "bet":
            # Player bets
            is_raise = last_bet > 0
            is_allin, bet_amount = calculate_bet_size(
                pot,
                current_bet,
                is_raise=is_raise,
                player_chips=current_player.chips,
            )
            current_player.chips -= bet_amount
            pot += bet_amount
            current_bet = bet_amount
            num_actions += 1
            if is_raise:
                print(f"{current_player.name} raises to {bet_amount}.")
            else:
                print(f"{current_player.name} bets {bet_amount}")

        elif action.lower() == "fold":
            # Player folds
            num_active_players -= 1
            print(f"{current_player.name} folds.")
        else:
            print("Invalid action. Please enter 'check', 'bet', 'raise', or 'fold'.")
            continue

        # Switch to the next player
        current_player = oop_player if current_player == ip_player else ip_player

    return pot, oop_player, ip_player, hand_over






community_cards = []

oop_player = Player(name="OOP", chips=200)
ip_player = Player(name="IP", chips=200)

while True:
    hand_over = False
    # Blinds in
    pot = 3
    oop_player.chips = 198
    ip_player.chips = 199
    # Deal the cards to the players
    [
        player.hand.append(deck.pop())
        for player in Player.get_players()
        for i in range(4)
    ]

    print("\nNew Hand\n")
    # Print the players' hands
    [
        print(f"{player.name}({player.chips}): {player.hand}")
        for player in Player.get_players()
    ]

    # Preflop
    print(f"OOP({oop_player.chips})\nIP({ip_player.chips})\n")
    print(f"\n-------PREFLOP------\n${pot}\nBoard: {community_cards}\n")
    pot, ip_player, oop_player, hand_over = preflop_betting_round2(
        pot=pot, oop_player=oop_player, ip_player=ip_player
    )

    if hand_over:
        [player.hand.clear() for player in Player.get_players()]
        community_cards = []
        continue

    if pot == 0:
        break
    # Deal the flop
    [community_cards.append(deck.pop()) for i in range(3)]
    print(f"OOP({oop_player.chips})\nIP({ip_player.chips})\n")
    print(f"\n-------FLOP------\n${pot}\nBoard: {community_cards}\n")
    pot, oop_player, ip_player, hand_over = postflop_betting_round(
        pot=pot, street="flop", oop_player=oop_player, ip_player=ip_player
    )

    if hand_over:
        [player.hand.clear() for player in Player.get_players()]
        community_cards = []
        continue

    # Deal the Turn
    community_cards.append(deck.pop())
    print(f"OOP({oop_player.chips})\nIP({ip_player.chips})\n")
    print(f"\n-------TURN------\n${ pot}\nBoard: {community_cards}\n")
    pot, oop_player, ip_player, hand_over = postflop_betting_round(
        pot=pot, street="turn", oop_player=oop_player, ip_player=ip_player
    )

    if hand_over:
        [player.hand.clear() for player in Player.get_players()]
        community_cards = []
        continue

    # Deal the River
    community_cards.append(deck.pop())
    print(f"OOP({oop_player.chips})\nIP({ip_player.chips})\n")
    print(f"\n-------RIVER------\n${pot}\nBoard: {community_cards}\n")
    pot, oop_player, ip_player, hand_over = postflop_betting_round(
        pot=pot, street="river", oop_player=oop_player, ip_player=ip_player
    )

def determine_showdown_winner(ip_player: Player, oop_player: Player):
    # fmt: off
    ip_rank = evaluate_omaha_cards(
        community_cards[0], community_cards[1], community_cards[2], community_cards[3], community_cards[4],
        ip_player.hand[0], ip_player.hand[1], ip_player.hand[2], ip_player.hand[3],
    )
    oop_rank = evaluate_omaha_cards(
        community_cards[0], community_cards[1], community_cards[2], community_cards[3], community_cards[4],
        oop_player.hand[0], oop_player.hand[1], oop_player.hand[2], oop_player.hand[3],
    )
    # fmt: on

    if ip_rank > oop_rank:
        print(f"IP Wins: {ip_player.hand}")
        return ip_player
    elif oop_rank > ip_rank:
        print(f"OOP Wins: {oop_player.hand}")
        return oop_player
    else:
        print(f"Chop")
        return None

    community_cards = []
