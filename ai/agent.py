import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.cuda
import random
from collections import deque
from metrics import q_value, epsilon, action_taken


class DQN(nn.Module):
    def __init__(self, state_size, action_size):
        """
        Initialize the Deep Q-Network.

        Args:
            state_size (int): The size of the input state.
            action_size (int): The number of possible actions.
        """
        super(DQN, self).__init__()
        # Three-layer network: complex enough to capture poker strategies, not too large to overfit
        self.fc1 = nn.Linear(state_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_size + 1)

    def forward(self, x):
        """
        Perform a forward pass through the network.

        Args:
            x (torch.Tensor): The input tensor.

        Returns:
            torch.Tensor: The output tensor.
        """
        # ReLU activations allow the network to learn non-linear poker strategies
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        # No activation on output layer to allow for positive and negative Q-values
        return self.fc3(x)


# fmt: off
class DQNAgent:
    def __init__(self, state_size, action_size):
        """
        Initialize the DQN Agent.

        Args:
            state_size (int): The size of the state space.
            action_size (int): The number of possible actions.
        """
        if torch.cuda.is_available():
            print("Cuda is Available. GPU will be used")
            print(f"GPU name: {torch.cuda.get_device_name(0)}")
            device = torch.device("cuda")
        self.name = None
        self.state_size = state_size  # Dimension of poker game state (cards, pot, etc.)
        self.action_size = action_size  # Number of possible actions (fold, call, raise)
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

    def remember(self, state, action, reward, next_state, done):
        """
        Store a transition in the replay memory.

        Args:
            state: The current state.
            action: The action taken.
            reward: The reward received.
            next_state: The resulting state.
            done: Whether the episode has ended.
        """
        # Store experiences to learn from diverse poker situations
        if not isinstance(state, torch.Tensor):
            state = torch.FloatTensor(state).to(self.device)
        if not isinstance(next_state, torch.Tensor):
            next_state = torch.FloatTensor(next_state).to(self.device)

        self.memory.append((state, action, reward, next_state, done))

    def act(self, state, valid_actions, max_bet):
        """
        Choose an action using an epsilon-greedy policy.

        Args:
            state: The current state.

        Returns:
            int: The chosen action.
        """
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.model(state_tensor)

        action_map = {"fold": 0, "check": 1, "call": 2, "bet": 3}
        valid_action_indices = [action_map[action] for action in valid_actions]

        if np.random.rand() <= self.epsilon:
            # Exploration: randomly try actions to discover new poker strategies
            action = random.choice(valid_action_indices)
        else:
            valid_q_values = q_values[0, valid_action_indices]
            action = valid_action_indices[valid_q_values.argmax().item()]

        bet_size = None
        if action == 3 and "bet" in valid_actions:
            bet_size = min(q_values[0][4] * max_bet, max_bet)


        max_q_values = q_values[0, valid_action_indices].max().item()
        q_value.labels(player='oop' if self.name == 'OOP' else 'ip').set(max_q_values)
        epsilon.labels(player='oop' if self.name == 'OOP' else 'ip').set(self.epsilon)
        # Exploitation: choose best action based on learned Q-values
        return action, bet_size

    def replay(self, batch_size):
        """
        Train the model using experiences from the replay memory.

        Args:
            batch_size (int): The number of samples to use for training.
        """

        if len(self.memory) < batch_size:
            return

        minibatch = random.sample(self.memory, batch_size)  # Random sampling breaks correlation between consecutive hands
        states, actions, rewards, next_states, dones = zip(*minibatch)

        # Convert to tensors for batch processing
        states = torch.stack(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.stack(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        # Compute current Q-values and target Q-values
        current_q = self.model(states).gather(1, actions.unsqueeze(1))
        max_next_q = self.target_model(next_states).detach().max(1)[0]
        target_q = rewards + (self.gamma * max_next_q * (1 - dones))

        # MSE loss helps the model learn to accurately predict action values in poker
        loss = nn.MSELoss()(current_q.squeeze(), target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Decay epsilon to gradually shift from exploration to exploitation
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        loss_value = loss.item()

        return loss_value

    def update_target_model(self):
        """
        Update the target model with the weights of the main model.
        """
        # Periodically update target network to stabilize training
        self.target_model.load_state_dict(self.model.state_dict())
