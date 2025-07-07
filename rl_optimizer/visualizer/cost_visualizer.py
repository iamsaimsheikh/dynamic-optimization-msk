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
    return list(reversed(records))

def plot_throughput(records):
    values = [record.total_cost_usd for record in records]
    max_val = max(values)
    throughputs = [max_val - v for v in values]

    plt.figure(figsize=(12, 6))
    plt.plot(throughputs, label="Batch Cost USD", color='red', linewidth=2)
    plt.title("Batch Cost / Episode (150 Episodes)")
    plt.xlabel("Episode")
    plt.ylabel("Batch Cost (USD)")
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
