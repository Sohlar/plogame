import torch
from cli_game import PokerGame
from agent import DQNAgent

def train_dqn_poker(game, episodes, batch_size=32):
    print("Starting DQN training for PLO...")

    for e in range(episodes):
        game_state = game.play_hand()

        # Train every hand
        if len(game.oop_agent.memory) > batch_size:
            oop_loss = game.oop_agent.replay(batch_size)
        if len(game.ip_agent.memory) > batch_size:
            ip_loss = game.ip_agent.replay(batch_size)

        #Update target models
        if e % 10 == 0:
            game.oop_agent.update_target_model()
            game.ip_agent.update_target_model()
        # Progress Report
        if e % 100 == 0:
            print(f"Episode: {e}/{episodes}, OOP Chips: {game.oop_player.chips}, IP Chips: {game.ip_player.chips}")
            if 'oop_loss' in locals() and 'ip_loss' in locals():
                print(f"OOP Loss: {oop_loss:.4f}, IP Loss: {ip_loss:.4f}")

    print("\nTraining Complete!")
    print("Final Chip Counts:")
    print(f"OOP Player chips: {game.oop_player.chips}")
    print(f"IP Player chips: {game.ip_player.chips}")

    torch.save(game.oop_agent.model.state_dict(), "oop_dqn_model.pth")
    torch.save(game.ip_agent.model.state_dict(), "ip_dqn_model.pth")

def main():
    game = PokerGame()
    num_episodes = 10000
    batch_size = 32

    train_dqn_poker(game, num_episodes, batch_size)


if __name__ == "__main__":
    main()