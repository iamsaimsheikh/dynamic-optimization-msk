import sys
import os

# Automatically add the project root to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db import get_db
from database.models.kafka_batch_stats_model import KafkaBatchStatsModel

def serialize_model(model_instance):
    """Convert SQLAlchemy model instance to dictionary, excluding internal keys."""
    return {
        key: value
        for key, value in model_instance.__dict__.items()
        if not key.startswith("_")
    }

if __name__ == "__main__":
    db = get_db()

    initial_config = (
        db.query(KafkaBatchStatsModel)
        .filter(KafkaBatchStatsModel.is_rl_processed.is_(False))
        .limit(1)
        .all()
    )

    if not initial_config:
        print("No unprocessed config found.")
    else:
        for row in initial_config:
            print(serialize_model(row))
