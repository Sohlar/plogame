import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque


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
        self.fc3 = nn.Linear(64, action_size)

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
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        """
        Choose an action using an epsilon-greedy policy.

        Args:
            state: The current state.

        Returns:
            int: The chosen action.
        """
        if np.random.rand() <= self.epsilon:
            # Exploration: randomly try actions to discover new poker strategies
            return random.randrange(self.action_size)
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        act_values = self.model(state)
        # Exploitation: choose best action based on learned Q-values
        return np.argmax(act_values.cpu().data.numpy())

    def replay(self, batch_size):
        """
        Train the model using experiences from the replay memory.

        Args:
            batch_size (int): The number of samples to use for training.
        """
        minibatch = random.sample(self.memory, batch_size)  # Random sampling breaks correlation between consecutive hands
        states, actions, rewards, next_states, dones = zip(*minibatch)

        # Convert to tensors for batch processing
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
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

    def update_target_model(self):
        """
        Update the target model with the weights of the main model.
        """
        # Periodically update target network to stabilize training
        self.target_model.load_state_dict(self.model.state_dict())

def train_dqn_poker(env, episodes, batch_size=32):
    """
    Train the DQN agent to play poker.

    Args:
        env: The poker environment.
        episodes (int): The number of episodes to train for.
        batch_size (int): The batch size for training. Defaults to 32.

    Returns:
        DQNAgent: The trained agent.
    """
    state_size = env.get_state().shape[0]  # Get the size of the poker game state
    action_size = 3  # Typically fold, call, raise in poker
    agent = DQNAgent(state_size, action_size)
    
    for e in range(episodes):
        state = env.reset()  # Start a new poker hand
        total_reward = 0
        done = False
        
        while not done:
            action = agent.act(state)  # Choose action (fold, call, or raise)
            next_state, reward, done, _ = env.step(action)  # Play the chosen action
            agent.remember(state, action, reward, next_state, done)  # Store the experience
            state = next_state
            total_reward += reward

            if len(agent.memory) > batch_size:
                agent.replay(batch_size)  # Train on past experiences

        if e % 10 == 0:
            agent.update_target_model()  # Periodically update target network for stable learning

        if e % 100 == 0:
            print(f"Episode: {e}/{episodes}, Total Reward: {total_reward}, Epsilon: {agent.epsilon:.2f}")

    return agent

# Assuming we have our PokerEnvironment class from the previous example
env = PokerEnvironment()
trained_agent = train_dqn_poker(env, episodes=100000)  # Train over many poker hands

# Save the trained model for later use
torch.save(trained_agent.model.state_dict(), "poker_dqn_model.pth")
