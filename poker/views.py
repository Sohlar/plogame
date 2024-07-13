from django.shortcuts import render
from django.views.d

# Create your views here.
from .game import PokerGame

game = PokerGame()


@app.route("/start", methods=["POST"])
def start_game():
    game.play_hand()
    return jsonify(game.get_game_state())


@app.route("/state", methods=["GET"])
def get_state():
    return jsonify(game.get_game_state())


app.route("/action", methods=["POST"])


def player_action():
    action = request.json.get("action")
    if not action:
        return jsonify({"error": "Invalid action"}), 400

    valid_actions = game.get_player_action(game.get_valid_preflop_actions())
    if action not in valid_actions:
        return jsonify({"error": "Invalid action"}), 400

    game_state = game.process_preflop_action(action)
    return jsonify(game_state)


if __name__ == "__main__":
    app.run(debug=True)
