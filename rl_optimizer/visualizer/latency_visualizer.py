import os
import sys
import matplotlib.pyplot as plt

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

def plot_latency(records):
    latencies_in_hours = [
        record.average_latency_ms / (60 * 60 * 1000)
        for record in records
    ]
    
    plt.figure(figsize=(12, 6))
    plt.plot(latencies_in_hours, label="Latency (seconds)", color='red', linewidth=2)
    plt.title("Average Latency per Episode (seconds / 50 Episodes)")
    plt.xlabel("Episode")
    plt.ylabel("Latency (seconds)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    records = get_last_500_records()
    print(f"Retrieved {len(records)} records.")
    if records:
        plot_latency(records)
    else:
        print("No records to plot.")
