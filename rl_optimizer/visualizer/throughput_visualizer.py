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

def plot_throughput(records):
    # formula for total messages is to multiple the throughput is per messages
    throughput_per_sec = [
        record.average_throughput_mps * 5000 for record in records
    ]
    plt.figure(figsize=(12, 6))
    plt.plot(throughput_per_sec, label="Messages per Second", color='green', linewidth=2)
    plt.title("Messages Sent per Second (150 Episodes)")
    plt.xlabel("Episode")
    plt.ylabel("Throughput (messages/sec)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    records = get_last_500_records()
    print(f"Retrieved {len(records)} records.")
    if records:
        plot_throughput(records)
    else:
        print("No records to plot.")
