import torch
import os
from cli_game import PokerGame, HumanPlayer
from agent import DQNAgent
import time
from logging_config import setup_logging
import logging
import torch.cuda
import datetime

setup_logging()

def load_model(model_path):
    state_size = 7 + (5*2) + 2*4*2
    action_size = 4
    agent = DQNAgent(state_size, action_size)
    agent.model.load_state_dict(torch.load(model_path))
    agent.model.eval()
    return agent

def list_available_models():
    models_dir = "/opt/ai/models"
    models = [f for f in os.listdir(models_dir) if f.endswith('.pth')]
    return models

def train_dqn_poker(game, episodes, batch_size=32, train_ip=True, train_oop=True):
    logging.info("Starting DQN training for PLO...")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    game.oop_agent.model.to(device)
    game.oop_agent.target_model.to(device)
    game.ip_agent.model.to(device)
    game.ip_agent.target_model.to(device)

    for e in range(episodes):
        game_state = game.play_hand()

        # Train every hand
        if train_oop and len(game.oop_agent.memory) > batch_size:
            oop_loss = game.oop_agent.replay(batch_size)
        if train_ip and len(game.ip_agent.memory) > batch_size:
            ip_loss = game.ip_agent.replay(batch_size)

        # Update target models
        if e % 10 == 0:
            if train_oop:
                game.oop_agent.update_target_model()
            if train_ip:
                game.ip_agent.update_target_model()
        # Progress Report
        if e % 100 == 0:
            logging.info(
                f"Episode: {e}/{episodes}"
            )
            if train_oop and"oop_loss" in locals():
                logging.info(f"OOP Loss: {oop_loss:.4f}")
            if train_ip and "ip_loss" in locals():
                logging.info(f"OOP Loss: {oop_loss:.4f}")

    print("\nTraining Complete!")
    print("Final Chip Counts:")
    print(f"OOP Player chips: {game.oop_player.chips}")
    print(f"IP Player chips: {game.ip_player.chips}")

    if train_oop:
        save_model(game.oop_agent, "oop")
    if train_ip:
        save_model(game.ip_agent, "ip")



def main():
    start_time = time.time()

    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        torch.cuda.empty_cache()

    mode = input("Enter 'play' to play against AI, or 'train' to train a new model: ")

    if mode == 'play':
        position = input("Enter 'oop' or 'ip': ")

        print("\nAvailable Models:")
        models = list_available_models()
        for i, model in enumerate(models):
            print(f"{i+1}. {model}")

        model_choice = int(input("\nEnter the number of the model: "))
        chosen_model = f"/opt/ai/models/{models[model_choice-1]}"

        ai_agent = load_model(chosen_model)
        game = PokerGame(human_position=position, 
                         oop_agent=ai_agent if position == 'ip' else None,
                         ip_agent=ai_agent if position == 'oop' else None)

        play_against_ai(game)
    else:
        episode_choice = int(input("\nEnter # of hands to train: "))
        train_oop = input("Train OOP model? (y/n): ").lower() == 'y'
        train_ip = input("Train IP model? (y/n): ").lower() == 'y'

        oop_agent = None
        ip_agent = None

        if not train_oop:
            print("\nAvailable OOP Models:")
            models = list_available_models()
            for i, model in enumerate(models):
                print(f"{i+1}. {model}")
            model_choice = int(input("\nEnter the number of the OOP model to use: "))
            oop_model_path = f"/opt/ai/models/{models[model_choice-1]}"
            oop_agent = load_model(oop_model_path)
            oop_agent.model.eval()

        if not train_ip:
            print("\nAvailable IP Models:")
            models = list_available_models()
            for i, model in enumerate(models):
                print(f"{i+1}. {model}")
            model_choice = int(input("\nEnter the number of the IP model to use: "))
            ip_model_path = f"/opt/ai/models/{models[model_choice-1]}"
            ip_agent = load_model(ip_model_path)
            ip_agent.model.eval()

        game = PokerGame()
        num_episodes = episode_choice
        batch_size = 32
        train_dqn_poker(game, num_episodes, batch_size)

    end_time = time.time()
    print(f"Total Time: {end_time - start_time:.2f} seconds")

def play_against_ai(game):
    while True:
        game_state = game.play_hand()
        print("\nFinal Chip Counts:")
        print(f"OOP Player chips: {game_state['oop_player']['chips']}")
        print(f"IP Player chips: {game_state['ip_player']['chips']}")
         
        play_again = input("Do you want to play again (y/n)")
        if play_again != 'y':
            break
        
def save_model(agent, position):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/opt/ai/models/{position}_dqn_model_{timestamp}.pth"
    torch.save(agent.model.state_dict(), filename)
    print(f"Saved {position} model: {filename}")

if __name__ == "__main__":
    main()

