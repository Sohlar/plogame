from prometheus_client import Gauge, Counter, Histogram
import psutil

# AI Performance Metrics
episode_reward = Gauge('episode_reward', 'Reward for the current episode', ['player'])
cumulative_reward = Gauge('cumulative_reward', 'Total reward across all episodes', ['player'])
q_value = Gauge('q_value', 'Current Q-value', ['player'])
loss = Gauge('loss', 'Current loss value', ['player'])
epsilon = Gauge('epsilon', 'Current epsilon value', ['player'])

# Game State Metrics
pot_size = Gauge('pot_size', 'Current pot size')
player_chips = Gauge('player_chips', 'Current player chips', ['player'])
community_cards = Gauge('community_cards', 'Number of community cards')

# Action Metrics
action_taken = Counter('action_taken', 'Number of times each action was taken', ['player_action'])

# System Resource Metrics
cpu_usage = Gauge('cpu_usage', 'Current CPU usage percentage')
memory_usage = Gauge('memory_usage', 'Current memory usage percentage')
gpu_usage = Gauge('gpu_usage', 'Current GPU usage percentage')

# Training Progress Metrics
episodes_completed = Counter('episodes_completed', 'Number of completed episodes')
training_time = Histogram('training_time', 'Time taken for training')

def update_system_metrics():
    cpu_usage.set(psutil.cpu_percent())
    memory_usage.set(psutil.virtual_memory().percent)
    # Note: GPU usage requires additional setup with libraries like pynvml
    # For simplicity, we'll leave it at 0 for now
    gpu_usage.set(0)