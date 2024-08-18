import torch
import os
from cli_game import PokerGame, HumanPlayer
from agent import DQNAgent
import time
from logging_config import setup_logging
import logging
import torch.cuda

setup_logging()

def load_model(model_path):
    state_size = 7 + (5*2) + 2*4*2
    action_size = 4
    agent = DQNAgent(state_size, action_size)
    agent.model.load_state_dict(torch.load(model_path))
    agent.model.eval()
    return agent

def list_available_models():
    models_dir = "./ai/models"
    models = [f for f in os.listdir(models_dir) if f.endswith('.pth')]
    return models

def train_dqn_poker(game, episodes, batch_size=32):
    logging.info("Starting DQN training for PLO...")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    game.oop_agent.model.to(device)
    game.oop_agent.target_model.to(device)
    game.ip_agent.model.to(device)
    game.ip_agent.target_model.to(device)

    for e in range(episodes):
        game_state = game.play_hand()

        # Train every hand
        if len(game.oop_agent.memory) > batch_size:
            oop_loss = game.oop_agent.replay(batch_size)
        if len(game.ip_agent.memory) > batch_size:
            ip_loss = game.ip_agent.replay(batch_size)

        # Update target models
        if e % 10 == 0:
            game.oop_agent.update_target_model()
            game.ip_agent.update_target_model()
        # Progress Report
        if e % 100 == 0:
            logging.info(
                f"Episode: {e}/{episodes}"
            )
            if "oop_loss" in locals() and "ip_loss" in locals():
                logging.info(f"OOP Loss: {oop_loss:.4f}, IP Loss: {ip_loss:.4f}")

    print("\nTraining Complete!")
    print("Final Chip Counts:")
    print(f"OOP Player chips: {game.oop_player.chips}")
    print(f"IP Player chips: {game.ip_player.chips}")

    torch.save(game.oop_agent.model.state_dict(), "./ai/models/oop_dqn_model.pth")
    torch.save(game.ip_agent.model.state_dict(), "./ai/models/ip_dqn_model.pth")


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
        chosen_model = f"./ai/models/{models[model_choice-1]}"

        ai_agent = load_model(chosen_model)
        game = PokerGame(human_position=position, ai_agent=ai_agent)
        play_against_ai(game)
    else:
        episode_choice = int(input("\nEnter # of hands to train: "))
        game = PokerGame()
        num_episodes = episode_choice
        batch_size = 32
        train_dqn_poker(game, num_episodes, batch_size)

    end_time = time.time()
    print(end_time - start_time)

def play_against_ai(game):
    while True:
        game_state = game.play_hand()
        print("\nFinal Chip Counts:")
        print(f"OOP Player chips: {game_state['oop_player']['chips']}")
        print(f"IP Player chips: {game_state['ip_player']['chips']}")
         
        play_again = input("Do you want to play again (y/n)")
        if play_again != 'y':
            break

if __name__ == "__main__":
    main()

