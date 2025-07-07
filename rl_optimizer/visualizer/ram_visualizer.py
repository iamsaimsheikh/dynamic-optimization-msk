import os
import sys
import matplotlib.pyplot as plt
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))
sys.path.insert(0, PROJECT_ROOT)

from database.db import get_db
from database.models.kafka_batch_stats_model import KafkaBatchStatsModel

def get_last_500_records():
    db = get_db()
    records = (
        db.query(KafkaBatchStatsModel)
        .order_by(KafkaBatchStatsModel.created_at.desc())
        .limit(150)
        .all()
    )
    return list(reversed(records))  # Oldest to newest

def moving_average(data, window_size=7):
    return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

def plot_ram(records):
    ram = [record.avg_ram_usage for record in records]
    smoothed_ram = moving_average(ram, window_size=7)

    plt.figure(figsize=(12, 6))
    plt.plot(smoothed_ram, label="Avg Memory Usage %", color='green', linewidth=2)
    plt.title("Memory Usage / Episode (50 Episodes)")
    plt.xlabel("Episode")
    plt.ylabel("Memory Usage (%)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    records = get_last_500_records()
    print(f"Retrieved {len(records)} records.")
    if records:
        plot_ram(records)
    else:
        print("No records to plot.")
