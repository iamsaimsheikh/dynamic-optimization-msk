import os
import sys
import matplotlib.pyplot as plt
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))
sys.path.insert(0, PROJECT_ROOT)

from database.db import get_db
from database.models.kafka_rl_training_log_model import KafkaRLTrainingLogModel

def get_last_500_records():
    db = get_db()
    records = (
        db.query(KafkaRLTrainingLogModel)
        .order_by(KafkaRLTrainingLogModel.timestamp.desc())
        .limit(150)
        .all()
    )
    return list(reversed(records))  # Oldest to newest

def moving_average(data, window_size=5):
    return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

def plot_rewards(records):
    rewards = [record.reward for record in records]
    averaged_rewards = moving_average(rewards, window_size=5)

    plt.figure(figsize=(12, 6))
    plt.plot(averaged_rewards, label="Reward", color='blue', linewidth=2)
    plt.title("Reward Trend (50 Episodes)")
    plt.xlabel("Episode")
    plt.ylabel("Reward [-1,1]")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    records = get_last_500_records()
    print(f"Retrieved {len(records)} records.")
    if records:
        plot_rewards(records)
    else:
        print("No records to plot.")
