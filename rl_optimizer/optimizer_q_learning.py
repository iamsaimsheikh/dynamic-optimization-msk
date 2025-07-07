import sys
import os
import time
import subprocess
import random
import itertools
import numpy as np
from uuid import UUID
import logging

# Automatically add the project root to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db import get_db
from database.models.kafka_batch_stats_model import KafkaBatchStatsModel

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def serialize_model(model_instance):
    return {
        key: value
        for key, value in model_instance.__dict__.items()
        if not key.startswith("_")
    }

def get_latest_unprocessed_config(db):
    return (
        db.query(KafkaBatchStatsModel)
        .filter(KafkaBatchStatsModel.is_rl_processed.is_(False))
        .order_by(KafkaBatchStatsModel.created_at.desc())
        .first()
    )

def reward_fn(stats):
    throughput = stats['average_throughput_mps']
    latency = stats['average_latency_ms']
    cost = stats['total_cost_usd']
    batch_size = stats['batch_size']

    # Avoid division by zero
    latency = latency if latency > 0 else 1
    cost = cost if cost > 0 else 1
    throughput = throughput if throughput > 0 else 0.01

    # Normalized metrics (scale values to a comparable range)
    normalized_throughput = throughput / 100  # Assuming 100 mps is a decent upper bound
    normalized_latency = latency / 1000       # ms to sec scale
    normalized_cost = cost * 100              # convert to cents

    # Weighted reward formula
    reward = (
        3.0 * normalized_throughput -   # High throughput helps
        2.0 * normalized_latency -      # Lower latency is better
        1.5 * normalized_cost           # Lower cost preferred
    )

    # Emphasize larger batch size slightly
    scaled_reward = reward * (batch_size / 16000.0)

    logger.debug(f"Reward components -> throughput: {throughput}, latency: {latency}, cost: {cost}, batch_size: {batch_size}")
    logger.debug(f"Normalized -> t: {normalized_throughput}, l: {normalized_latency}, c: {normalized_cost}")
    logger.debug(f"Calculated reward: {scaled_reward}")
    return scaled_reward


def run_main_with_config(config):
    args = [
        "python", "main.py",
        f"--batch-size", str(16000),
        f"--linger-ms", str(config['conf_linger_ms']),
        f"--acks", "all",
        f"--max-request-size", str(config['conf_max_request_size']),
        f"--fetch-max-bytes", str(config['conf_fetch_max_bytes']),
        f"--max-poll-records", str(config['conf_max_poll_records']),
        f"--session-timeout-ms", str(config['conf_session_timeout_ms']),
        f"--heartbeat-interval-ms", str(config['conf_heartbeat_interval_ms']),
    ]
    logger.debug(f"Running command: {' '.join(args)}")
    subprocess.run(args)

def wait_for_new_record(db, last_id):
    logger.debug("Waiting for new unprocessed record...")
    while True:
        latest = get_latest_unprocessed_config(db)
        if latest and str(latest.id) != str(last_id):
            logger.debug(f"New record found with ID: {latest.id}")
            return serialize_model(latest)
        time.sleep(2)

def q_learning():
    db = get_db()

    param_space = {
        'conf_linger_ms': [1, 2, 3, 4, 5],
        'conf_max_request_size': [174762,349525,699051],
        'conf_fetch_max_bytes': [32768,65536,262144,524288],
        'conf_max_poll_records': [15, 30, 45, 65, 90],
        'conf_session_timeout_ms': [500,1000,2500,5000,10000],
        'conf_heartbeat_interval_ms': [1000,3000, 10000, 20000],
    }

    actions = list(itertools.product(*param_space.values()))
    action_index = {i: a for i, a in enumerate(actions)}
    index_action = {v: i for i, v in action_index.items()}

    Q = np.zeros(len(actions))
    alpha = 0.1
    gamma = 0.9
    epsilon = 0.2

    for episode in range(50):
        logger.info(f"\n=== Episode {episode+1} ===")
        if random.random() < epsilon:
            action_idx = random.randint(0, len(actions)-1)
            logger.debug("Exploring new configuration")
        else:
            action_idx = int(np.argmax(Q))
            logger.debug("Exploiting best known configuration")

        action = action_index[action_idx]
        config = dict(zip(param_space.keys(), action))
        logger.debug(f"Selected configuration: {config}")

        run_main_with_config(config)

        latest_record = wait_for_new_record(db, last_id=None)
        reward = reward_fn(latest_record)
        logger.info(f"Reward: {reward:.4f}")

        Q[action_idx] = Q[action_idx] + alpha * (reward - Q[action_idx])
        logger.debug(f"Updated Q[{action_idx}]: {Q[action_idx]:.4f}")

        db.query(KafkaBatchStatsModel).filter(KafkaBatchStatsModel.id == UUID(str(latest_record['id']))).update({"is_rl_processed": True})
        db.commit()
        logger.debug("Marked record as processed")

if __name__ == "__main__":
    q_learning()
