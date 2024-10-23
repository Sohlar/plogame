import torch
import argparse
import sys
import os
from ai_trainer import PokerGame, HumanPlayer
from agent import DQNAgent
import time
from logging_config import setup_logging
import logging
import torch.cuda
import datetime
from prometheus_client import start_http_server
from metrics import loss as loss_metric, winrate, episode_reward, cumulative_reward, player_chips, pot_size, community_cards, episodes_completed, action_taken, q_value, epsilon, update_system_metrics

setup_logging()

def load_model(model_path):
    """
    Load a pre-trained model from a file.

    Args:
        model_path (str): The path to the saved model file.

    Returns:
        DQNAgent: A DQNAgent instance with the loaded model.
    """
    state_size = 7 + (5*2) + 2*4*2
    action_size = 4
    agent = DQNAgent(state_size, action_size)
    agent.model.load_state_dict(torch.load(model_path))
    agent.model.eval()
    return agent

def list_available_models():
    """
    List all available model files in the models directory.

    Returns:
        list: A list of filenames of available models.
    """
    models_dir = "./models"
    models = [f for f in os.listdir(models_dir) if f.endswith('.pth')]
    return models

def train_dqn_poker(game, episodes, batch_size=32, train_ip=True, train_oop=True):
    """
    Train the DQN agents for poker.

    Args:
        game (PokerGame): The poker game instance.
        episodes (int): The number of episodes to train for.
        batch_size (int, optional): The batch size for training. Defaults to 32.
        train_ip (bool, optional): Whether to train the in-position agent. Defaults to True.
        train_oop (bool, optional): Whether to train the out-of-position agent. Defaults to True.
    """
    logging.info("Starting DQN training for PLO...")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    game.oop_agent.model.to(device)
    game.oop_agent.target_model.to(device)
    game.ip_agent.model.to(device)
    game.ip_agent.target_model.to(device)

    game.oop_agent.device = device
    game.ip_agent.device = device

    oop_cumulative_reward = 0
    ip_cumulative_reward = 0


    for e in range(episodes):
        game_state, oop_reward, ip_reward = game.play_hand()

        oop_cumulative_reward += oop_reward
        ip_cumulative_reward += ip_reward

        # Train every hand
        if train_oop and len(game.oop_agent.memory) > batch_size:
            oop_loss = game.oop_agent.replay(batch_size)
            if oop_loss is not None:
                game.oop_loss = oop_loss
                loss_metric.labels(player='oop').set(oop_loss)
        else:
            game.oop_loss = None

        if train_ip and len(game.ip_agent.memory) > batch_size:
            ip_loss = game.ip_agent.replay(batch_size)
            if ip_loss is not None:
                game.ip_loss = ip_loss
                loss_metric.labels(player='ip').set(ip_loss)
        else:
            game.ip_loss = None

        # Update target models
        if e % 10 == 0:
            if train_oop:
                game.oop_agent.update_target_model()
            if train_ip:
                game.ip_agent.update_target_model()

        # Update metrics
        cumulative_reward.labels(player='oop').set(oop_cumulative_reward)
        cumulative_reward.labels(player='ip').set(ip_cumulative_reward)
        player_chips.labels(player='oop').set(game_state['oop_player']['chips'])
        player_chips.labels(player='ip').set(game_state['ip_player']['chips'])
        pot_size.set(game_state['pot'])
        community_cards.set(len(game_state['community_cards']))


        # Progress Report
        if e % 100 == 0:

            episode_count = max(e/100, 1)
            oop_winrate = oop_cumulative_reward/episode_count
            ip_winrate = ip_cumulative_reward/episode_count
            winrate.labels(player='oop').set(oop_winrate)
            winrate.labels(player='ip').set(ip_winrate)
            logging.info(
                f"Episode: {e}/{episodes}"
            )
            if train_oop and game.oop_loss is not None:
                logging.info(f"OOP Loss: {game.oop_loss:.4f}")
            if train_ip and game.ip_loss is not None:
                logging.info(f"IP Loss: {game.ip_loss:.4f}")

            update_system_metrics()

    print("\nTraining Complete!")

    if train_oop:
        save_model(game.oop_agent, "oop")
    if train_ip:
        save_model(game.ip_agent, "ip")


def main(mode='train', hands=10, train_oop=True, train_ip=True):
    """
    Main function to either train the model or play against AI.

    Args:
        mode (str, optional): 'train' or 'play'. Defaults to 'train'.
        hands (int, optional): Number of hands to train on. Defaults to 10.
        train_oop (bool, optional): Whether to train the out-of-position agent. Defaults to True.
        train_ip (bool, optional): Whether to train the in-position agent. Defaults to True.
    """
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        torch.cuda.empty_cache()

    mode = mode

    if mode == 'play':
        position = input("Enter 'oop' or 'ip': ")

        print("\nAvailable Models:")
        models = list_available_models()
        for i, model in enumerate(models):
            print(f"{i+1}. {model}")

        model_choice = int(input("\nEnter the number of the model: "))
        chosen_model = f"./models/{models[model_choice-1]}"

        ai_agent = load_model(chosen_model)
        game = PokerGame(human_position=position, 
                         oop_agent=ai_agent if position == 'ip' else None,
                         ip_agent=ai_agent if position == 'oop' else None)

        play_against_ai(game)
    else:
        episode_choice = hands
        train_oop = train_oop
        train_ip = train_ip
        oop_agent = None
        ip_agent = None

        if not train_oop:
            print("\nAvailable OOP Models:")
            models = list_available_models()
            for i, model in enumerate(models):
                print(f"{i+1}. {model}")
            model_choice = int(input("\nEnter the number of the OOP model to use: "))
            oop_model_path = f"./models/{models[model_choice-1]}"
            oop_agent = load_model(oop_model_path)
            oop_agent.model.eval()

        if not train_ip:
            print("\nAvailable IP Models:")
            models = list_available_models()
            for i, model in enumerate(models):
                print(f"{i+1}. {model}")
            model_choice = int(input("\nEnter the number of the IP model to use: "))
            ip_model_path = f"./models/{models[model_choice-1]}"
            ip_agent = load_model(ip_model_path)
            ip_agent.model.eval()

        start_time = time.time()
        game = PokerGame()
        num_episodes = episode_choice
        batch_size = 128
        train_dqn_poker(game, num_episodes, batch_size)
        end_time = time.time()
        print(f"Total Time: {end_time - start_time:.2f} seconds")

def play_against_ai(game):
    """
    Play a series of hands against the AI.

    Args:
        game (PokerGame): The poker game instance.
    """
    while True:
        game_state = game.play_hand()
        print("\nFinal Chip Counts:")
        print(f"OOP Player chips: {game_state['oop_player']['chips']}")
        print(f"IP Player chips: {game_state['ip_player']['chips']}")
         
        play_again = input("Do you want to play again (y/n)")
        if play_again != 'y':
            break
        
def save_model(agent, position):
    """
    Save the trained model to a file.

    Args:
        agent (DQNAgent): The agent whose model is to be saved.
        position (str): The position of the agent ('oop' or 'ip').
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"./models/{position}_dqn_model_{timestamp}.pth"
    torch.save(agent.model.state_dict(), filename)
    print(f"Saved {position} model: {filename}")

if __name__ == "__main__":
    start_http_server(8000)
    #parser = argparse.ArgumentParser(description="PLO model DQN")
    #parser.add_argument("--mode", type=str, choices=['train', 'play'], required=True, help="'Play' or 'Train'")
    #parser.add_argument("--hands", type=int, required=True, help="Number of hands to train on")
    #parser.add_argument("--train_ip", action="store_true", help="Train an IP model")
    #parser.add_argument("--train_oop", action="store_true", help="Train an OOP model")

    #args = parser.parse_args()
     
    #if args.mode == 'train' and args.hands is None:
    #    parser.error("--hands is required in training mode.")
    main()

