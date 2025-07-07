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
        .limit(50)
        .all()
    )
    return list(reversed(records))

def moving_average(data, window_size=7):
    return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

def plot_cpu(records):
    cpu = [record.avg_cpu_usage for record in records]
    smoothed_cpu = moving_average(cpu, window_size=7)

    plt.figure(figsize=(12, 6))
    plt.plot(smoothed_cpu, label="Avg CPU Usage %", color='green', linewidth=2)
    plt.title("CPU Usage / Episode (50 Episodes)")
    plt.xlabel("Episode")
    plt.ylabel("CPU Usage (%)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    records = get_last_500_records()
    print(f"Retrieved {len(records)} records.")
    if records:
        plot_cpu(records)
    else:
        print("No records to plot.")
