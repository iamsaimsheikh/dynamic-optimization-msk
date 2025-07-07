import os
import sys
import time
import random
import itertools
import subprocess
import numpy as np
from collections import deque, namedtuple
from uuid import UUID

import torch
import torch.nn as nn
import torch.optim as optim

# Set up path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_ROOT)

from database.db import get_db
from database.models.kafka_batch_stats_model import KafkaBatchStatsModel
from database.models.kafka_rl_training_log_model import KafkaRLTrainingLogModel

import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Replay Buffer ---
Transition = namedtuple("Transition", ("state", "action", "reward", "next_state", "done"))

class ReplayBuffer:
    def __init__(self, capacity=100):
        self.buffer = deque(maxlen=capacity)

    def push(self, *args):
        self.buffer.append(Transition(*args))

    def sample(self, batch_size):
        return Transition(*zip(*random.sample(self.buffer, batch_size)))

    def __len__(self):
        return len(self.buffer)

# --- DQN Model ---
class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim),
        )

    def forward(self, x):
        return self.net(x)

# --- Utilities ---
def serialize_model(model_instance):
    return {k: v for k, v in model_instance.__dict__.items() if not k.startswith("_")}

def get_latest_unprocessed_config(db):
    return (
        db.query(KafkaBatchStatsModel)
        .filter(KafkaBatchStatsModel.is_rl_processed.is_(False))
        .order_by(KafkaBatchStatsModel.created_at.desc())
        .first()
    )

def reward_fn(curr, prev=None, threshold=0.01, clip_min=-1.0, clip_max=1.0):
    """
    Reward function for Kafka optimization:
    - Increases reward when throughput improves.
    - Penalizes when latency increases.
    - Handles edge cases and smooths out minor changes (noise).
    """

    def diff_ratio(a, b):
        if abs(b) < 1e-6:
            return 0.0
        return (a - b) / b

    def filter_noise(v):
        return v if abs(v) > threshold else 0.0

    if prev is None:
        # Initial run: reward based on current normalized performance
        throughput_score = curr["average_throughput_mps"] / 1000.0  # Normalize to [0,1]
        latency_penalty = curr["average_latency_ms"] / 500.0        # Normalize to [0,1]
        reward = throughput_score - latency_penalty
    else:
        # Compute relative changes
        throughput_change = filter_noise(diff_ratio(curr["average_throughput_mps"], prev["average_throughput_mps"]))
        latency_change = filter_noise(diff_ratio(curr["average_latency_ms"], prev["average_latency_ms"]))

        # Reward policy
        reward = 0.0

        # Reward throughput increases (double weight), punish decrease (lighter penalty)
        if throughput_change > 0:
            reward += 2.0 * throughput_change
        elif throughput_change < 0:
            reward += 0.5 * throughput_change  # less punishment

        # Penalize latency increases, reward decreases slightly
        if latency_change > 0:
            reward -= 1.0 * latency_change  # stronger penalty
        elif latency_change < 0:
            reward += 0.5 * abs(latency_change)  # reward for decrease

    # Clip final reward
    reward = max(clip_min, min(clip_max, reward))

    # Optional exploration nudge if reward is zero
    if reward == 0.0:
        reward = random.uniform(0.0001, 0.01)

    return reward




def run_main_with_config(config, epsilon):
    args = [
        "python", os.path.join(PROJECT_ROOT, "msk", "main.py"),
        "--batch-size", str(16000),
        "--linger-ms", str(config["conf_linger_ms"]),
        "--acks", "all",
        "--max-request-size", str(config["conf_max_request_size"]),
        "--fetch-max-bytes", str(config["conf_fetch_max_bytes"]),
        "--max-poll-records", str(config["conf_max_poll_records"]),
        "--session-timeout-ms", str(config["conf_session_timeout_ms"]),
        "--heartbeat-interval-ms", str(config["conf_heartbeat_interval_ms"]),
        "--epsilon", str(epsilon)
    ]
    subprocess.run(args, check=True)


def wait_for_new_record(db, last_id, timeout=300, poll_interval=3):
    start = time.time()
    while time.time() - start < timeout:
        latest = get_latest_unprocessed_config(db)
        if latest and str(latest.id) != str(last_id):
            return serialize_model(latest)
        time.sleep(poll_interval)
    raise TimeoutError("Timeout waiting for new KafkaBatchStatsModel record")

def mark_record_processed(db, record_id):
    db.query(KafkaBatchStatsModel).filter(KafkaBatchStatsModel.id == UUID(str(record_id))).update({"is_rl_processed": True})
    db.commit()

def config_to_vector(config, param_space):
    def find_nearest_index(val, options):
        if val in options:
            return options.index(val)
        # If value is not found, get the closest one
        return np.argmin([abs(val - o) for o in options])

    return np.array([find_nearest_index(config[k], param_space[k]) for k in param_space], dtype=np.float32)


def compose_state(config, metrics, param_space):
    config_vec = config_to_vector(config, param_space)
    perf_vec = np.array([
        metrics["average_throughput_mps"] / 20000.0,
        metrics["average_latency_ms"] / 2000.0,
        metrics["total_cost_usd"] / 10.0
    ], dtype=np.float32)
    return np.concatenate([config_vec, perf_vec])

def update_config_from_action(action_idx, param_space):
    actions = list(itertools.product(*param_space.values()))
    return dict(zip(param_space.keys(), actions[min(action_idx, len(actions)-1)]))

def log_episode_to_db(db, ep, config, metrics, next_config, reward, action_idx, loss):
    db.add(KafkaRLTrainingLogModel(
        episode=ep, reward=reward, action_taken=action_idx, loss=loss,
        batch_size=metrics["batch_size"],
        average_throughput_mps=metrics["average_throughput_mps"],
        average_latency_ms=metrics["average_latency_ms"],
        total_cost_usd=metrics["total_cost_usd"],
        **{f"{k}": config[k] for k in config},
        **{f"next_{k}": next_config[k] for k in next_config}
    ))
    db.commit()

def soft_update(target, source, tau):
    for t_param, s_param in zip(target.parameters(), source.parameters()):
        t_param.data.copy_(tau * s_param.data + (1 - tau) * t_param.data)

def select_action(state, model, epsilon, n_actions, device):
    if random.random() < epsilon:
        return random.randint(0, n_actions - 1)
    with torch.no_grad():
        return model(torch.FloatTensor(state).unsqueeze(0).to(device)).argmax().item()

# --- Main Training Loop ---
def train_dqn():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")

    db = get_db()

    param_space = {
    "conf_linger_ms": [0, 2],                         # more responsive
    "conf_max_request_size": [1048576, 2097152],      # smaller size
    "conf_fetch_max_bytes": [5242880, 10485760],      # tighter control
    "conf_max_poll_records": [100, 300],              # smaller processing window
    "conf_session_timeout_ms": [10000, 15000],        # quicker failure detection
    "conf_heartbeat_interval_ms": [5000, 10000],      # slightly faster heartbeats
        }

    n_actions = np.prod([len(v) for v in param_space.values()])
    input_dim = len(param_space) + 3

    policy_net = DQN(input_dim, n_actions).to(device)
    target_net = DQN(input_dim, n_actions).to(device)
    target_net.load_state_dict(policy_net.state_dict())

    optimizer = optim.Adam(policy_net.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()

    buffer = ReplayBuffer()
    epsilon, epsilon_min, decay = 1, 0.2, 0.98
    gamma, tau = 0.9, 0.05
    batch_size, episodes = 32, 50

    first = get_latest_unprocessed_config(db)
    if not first:
        logger.error("No initial record found.")
        return

    last_id = str(first.id)
    current_config = {k: getattr(first, k) for k in param_space}
    current_metrics = serialize_model(first)
    current_state = compose_state(current_config, current_metrics, param_space)

    prev_metrics = None  # to hold metrics from previous step

    for ep in range(1, episodes + 1):
        logger.info(f"\n=== Episode {ep} | Epsilon: {epsilon:.3f} ===")

        action = select_action(current_state, policy_net, epsilon, n_actions, device)
        next_config = update_config_from_action(action, param_space)

        try:
            run_main_with_config(next_config, epsilon=epsilon)
            result = wait_for_new_record(db, last_id)
        except Exception as e:
            logger.error(f"Error in episode {ep}: {e}")
            break

        # Calculate reward using previous metrics if available
        reward = reward_fn(result, prev_metrics)

        next_state = compose_state({k: result[k] for k in param_space}, result, param_space)
        done = (ep == episodes)  # mark done at last episode

        buffer.push(current_state, action, reward, next_state, done)

        if len(buffer) >= batch_size:
            batch = buffer.sample(batch_size)
            states = torch.FloatTensor(batch.state).to(device)
            actions = torch.LongTensor(batch.action).unsqueeze(1).to(device)
            rewards = torch.FloatTensor(batch.reward).unsqueeze(1).to(device)
            next_states = torch.FloatTensor(batch.next_state).to(device)
            dones = torch.FloatTensor(batch.done).unsqueeze(1).to(device)

            q_values = policy_net(states).gather(1, actions)
            with torch.no_grad():
                max_next = target_net(next_states).max(1)[0].unsqueeze(1)
                target_q = rewards + gamma * max_next * (1 - dones)
            loss = loss_fn(q_values, target_q)

            logger.info(f"Episode {ep} | Reward: {reward:.4f} | Loss: {loss.item():.6f}")

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            soft_update(target_net, policy_net, tau)
        else:
            loss = torch.tensor(0.0)
            logger.info(f"Episode {ep} | Reward: {reward:.4f} | Loss: {loss.item():.6f} (Buffer not full yet)")

        log_episode_to_db(db, ep, current_config, result, next_config, reward, action, loss.item())
        mark_record_processed(db, result["id"])
        
        # Update for next iteration
        current_state = next_state
        current_config = {k: result[k] for k in param_space}
        prev_metrics = result  # Save current metrics as previous for next episode reward calculation
        last_id = result["id"]
        epsilon = max(epsilon * decay, epsilon_min)

    logger.info("Training complete.")


    logger.info("Training complete.")

if __name__ == "__main__":
    train_dqn()
