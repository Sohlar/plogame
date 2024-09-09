# PLO AI Training and CLI Game

This project contains the AI components for a Pot Limit Omaha (PLO) poker trainer, including a command-line interface (CLI) game, a Deep Q-Network (DQN) agent, a training script, and metrics collection.

## Files

1. cli_game.py: Implements the PLO game logic and CLI interface.
2. agent.py: Defines the DQN agent for AI decision-making.
3. train.py: Provides functionality to train the AI and play against it.
4. metrics.py: Sets up metrics collection for monitoring AI performance and system resources.

## Setup

1. Ensure you have Python 3.x installed.
2. Install the required dependencies:
    ```
   pip install torch numpy psutil prometheus_client
    ```

## Usage

### Training the AI

Run the training script:
    ```
    python train.py
    ```

Follow the prompts to:
- Choose the number of hands to train
- Decide whether to train the OOP (out of position) model, IP (in position) model, or both
- Select existing models for positions you're not training

### Playing Against the AI

Run the training script and choose the 'play' option:
    ```
    python train.py
    ```
Follow the prompts to:
- Choose your position (OOP or IP)
- Select an AI model to play against

## Key Components

### PokerGame (cli_game.py)

- Implements the core game logic for PLO
- Handles betting rounds, card dealing, and determining winners
- Provides both AI and human player interfaces

### DQNAgent (agent.py)

- Implements a Deep Q-Network for AI decision making
- Uses experience replay and target networks for stable learning
- Supports both CPU and GPU training

### Training (train.py)

- Allows training of AI models for both OOP and IP positions
- Supports playing against trained AI models
- Handles model saving and loading

### Metrics (metrics.py)

- Sets up Prometheus metrics for monitoring:
  - AI performance (rewards, Q-values, loss)
  - Game state (pot size, player chips)
  - System resources (CPU, memory, GPU usage)
  - Training progress

## Customization

- Adjust hyperparameters in agent.py to optimize AI performance
- Modify the network architecture in the DQN class for different model complexities
- Add or remove metrics in metrics.py as needed for your monitoring setup

## Note

This project is designed for educational and research purposes. It demonstrates the application of reinforcement learning to poker strategy but may not be suitable for production use without further refinement and testing.