from typing import List, Tuple, Union, Dict, Optional
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.cuda
import random
from collections import deque
from metrics import q_value, epsilon, action_taken, bet_size_metric


class DQN(nn.Module):
    """
    Deep Q-Network (DQN) model for poker strategy.

    This neural network is designed to learn and represent complex poker strategies.
    It takes the game state as input and outputs Q-values for different actions,
    as well as a bet size and expected values for each action.
    """

    def __init__(self, state_size, action_size):
        """
        Initialize the Deep Q-Network.

        Args:
            state_size (int): The size of the input state.
            action_size (int): The number of possible actions.
        """
        super(DQN, self).__init__()
        # Three-layer network: complex enough to capture poker strategies, not too large to overfit
        self.fc1 = nn.Linear(state_size, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, action_size)
        self.fc_bet = nn.Linear(256, 1)
        self.fc_ev = nn.Linear(256, action_size)

    def forward(self, x):
        """
        Perform a forward pass through the network.

        Args:
            x (torch.Tensor): The input tensor representing the game state.

        Returns:
            torch.Tensor: The output tensor containing Q-values, bet size, and expected values.
        """
        # ReLU activations allow the network to learn non-linear poker strategies
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        actions = self.fc3(x)
        bet_size = torch.sigmoid(self.fc_bet(x))
        ev = self.fc_ev(x)
        return torch.cat([actions, bet_size, ev], dim=-1)



# fmt: off
class DQNAgent:
    """
    DQN Agent for playing poker.

    This agent uses a Deep Q-Network to learn and make decisions in a poker game.
    It implements experience replay, epsilon-greedy exploration, and target network
    for stable learning.
    """

    def __init__(self, state_size, action_size):
        """
        Initialize the DQN Agent.

        Args:
            state_size (int): The size of the state space.
            action_size (int): The number of possible actions.
        """
        self.name = ""
        self.state_size = state_size  # Dimension of poker game state (cards, pot, etc.)
        self.action_size = action_size  # Number of possible actions (fold, call, raise)
        self.batch_size = 128
        self.memory = deque(maxlen=10000)  # Experience replay buffer, crucial for stable learning in poker
        self.gamma = 0.95    # Discount rate for future rewards, important for long-term strategy
        self.epsilon = 1.0   # Start with 100% exploration to learn diverse poker situations
        self.epsilon_min = 0.01  # Minimum exploration to always adapt to opponent's strategy
        self.epsilon_decay = 0.995  # Gradually reduce exploration to exploit learned poker knowledge
        self.learning_rate = 0.001  # Small learning rate for stable improvement of poker strategy
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # GPU acceleration for faster learning
        self.model = DQN(state_size, action_size).to(self.device)  # Main network for action selection
        self.target_model = DQN(state_size, action_size).to(self.device)  # Target network for stable Q-learning
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)  # Adam optimizer works well for poker's noisy rewards
        self.min_bet = 2
        self.ev_weight = 0.5

    def remember(self, state, action, reward, next_state, done):
        """
        Store a transition in the replay memory.

        This method is used to collect experiences for later training.

        Args:
            state (torch.Tensor): The current state.
            action (int): The action taken.
            reward (float): The reward received.
            next_state (torch.Tensor): The resulting state.
            done (bool): Whether the episode has ended.
        """
        # Store experiences to learn from diverse poker situations
        state = torch.FloatTensor(state).to(self.device) if not isinstance(state, torch.Tensor) else state.to(self.device)
        next_state = torch.FloatTensor(next_state).to(self.device) if not isinstance(next_state, torch.Tensor) else next_state.to(self.device)
        action = torch.LongTensor([action]).to(self.device)
        reward = torch.FloatTensor([reward]).to(self.device)
        done = torch.FloatTensor([done]).to(self.device)

        self.memory.append((state, action, reward, next_state, done))

    def act(self, state, valid_actions, max_bet, min_bet):
        """
        Choose an action using an epsilon-greedy policy.

        This method balances exploration and exploitation in action selection.

        Args:
            state (torch.Tensor): The current state.
            valid_actions (List[str]): List of valid actions in the current state.
            max_bet (float): Maximum allowed bet size.
            min_bet (float): Minimum allowed bet size.

        Returns:
            Tuple[int, Optional[float]]: The chosen action and bet size (if applicable).
        """
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.model(state_tensor)

        action_map = {"fold": 0, "check": 1, "call": 2, "bet": 3}
        valid_action_indices = [action_map[action] for action in valid_actions]
        
        if not isinstance(state, torch.Tensor):
            state = torch.FloatTensor(state).to(self.device)
        elif state.device != self.device:
            state = state.to(self.device)
        if np.random.rand() <= self.epsilon:
            # Exploration: randomly try actions to discover new poker strategies
            action = random.choice(valid_action_indices)
        else:
            combined_values = q_values[0, self.action_size] + self.ev_weight * q_values[0, -self.action_size:]
            valid_values = combined_values[valid_action_indices]
            action = valid_action_indices[valid_values.argmax().item()]

        bet_size = None
        if action == 3 and "bet" in valid_actions:
            bet_fraction = q_values[0, self.action_size].item()
            bet_size = max(min_bet, min(min_bet + bet_fraction * (max_bet - min_bet), max_bet))
            bet_size = round(bet_size, 0)
            bet_size_metric.labels(player='oop' if self.name == 'OOP' else 'ip', street="agent_decision").observe(bet_size)  


        max_q_values = q_values[0, valid_action_indices].max().item()
        q_value.labels(player='oop' if self.name == 'OOP' else 'ip').set(max_q_values)
        epsilon.labels(player='oop' if self.name == 'OOP' else 'ip').set(self.epsilon)
        # Exploitation: choose best action based on learned Q-values
        ##print(f"ABOUT TO RETURN BET SIZE: {bet_size}")
        return action, bet_size

    def replay(self, batch_size):
        """
        Train the model using experiences from the replay memory.

        This method implements experience replay to break correlations between consecutive samples.

        Args:
            batch_size (int): The number of samples to use for training.

        Returns:
            float: The total loss from the training step.
        """

        if len(self.memory) < self.batch_size:
            return

        minibatch = random.sample(self.memory, self.batch_size)  # Random sampling breaks correlation between consecutive hands
        states, actions, rewards, next_states, dones = zip(*minibatch)

        # Convert to tensors for batch processing
        states = torch.stack(states)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.stack(next_states)
        dones = torch.FloatTensor(dones).to(self.device)

        # Compute current Q-values and target Q-values
        current_output = self.model(states)
        current_q = current_output[:, :self.action_size]
        current_ev = current_output[:, -self.action_size:]

        with torch.no_grad():
            next_output = self.target_model(next_states)
            next_q = next_output[:, :self.action_size]
            target_q = rewards + (1 - dones) * self.gamma * torch.max(next_q, dim=1)[0]

        # Compute Losses
        q_loss = nn.MSELoss()(current_q.gather(1, actions.unsqueeze(1)).squeeze(), target_q)
        ev_loss = nn.MSELoss()(current_ev.gather(1, actions.unsqueeze(1)).squeeze(), rewards)
        total_loss = q_loss + ev_loss

        # MSE loss helps the model learn to accurately predict action values in poker
        self.optimizer.zero_grad()
        total_loss.backward()
        self.optimizer.step()

        # Decay epsilon to gradually shift from exploration to exploitation
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        return total_loss.item()

    def update_target_model(self):
        """
        Update the target model with the weights of the main model.

        This method is used to stabilize training by periodically updating the target network.
        """
        # Periodically update target network to stabilize training
        self.target_model.load_state_dict(self.model.state_dict())
