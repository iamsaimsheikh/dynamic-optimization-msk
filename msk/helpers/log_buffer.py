from sqlalchemy.orm import Session
from database.models.consumer_log_model import ConsumerLogModel
from database.models.producer_log_model import ProducerLogModel

class LogBuffer:
    def __init__(self, db: Session, log_type: str, buffer_size: int):
        self.db = db
        self.log_type = log_type
        self.buffer_size = buffer_size
        self.buffer = []  # Stores logs before flushing

    def add_log(self, log_entry: dict):
        self.buffer.append(log_entry)

        if len(self.buffer) >= self.buffer_size:
            self.flush()

    def flush(self):
        if not self.buffer:
            return

        try:
            if self.log_type == "consumer":
                log_objects = [ConsumerLogModel(**log) for log in self.buffer]
            elif self.log_type == "producer":
                log_objects = [ProducerLogModel(**log) for log in self.buffer]
            else:
                raise ValueError("Invalid log type. Must be 'consumer' or 'producer'.")

            self.db.bulk_save_objects(log_objects)
            self.db.commit()
            self.buffer.clear()

        except Exception as e:
            self.db.rollback()
            print(f"Error saving logs to DB: {e}")

    def __del__(self):
        self.flush()
