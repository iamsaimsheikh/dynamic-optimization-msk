from sqlalchemy.orm import Session
from database.models.consumer_log_model import ConsumerLogModel
from database.models.producer_log_model import ProducerLogModel
from database.models.sys_event_log_model import SysEventLogModel

class LogBuffer:
    def __init__(self, db: Session, log_type: str, buffer_size: int):
        self.db = db
        self.log_type = log_type
        self.buffer_size = buffer_size
        self.buffer = []

    def fix_timestamp(self, timestamp: str) -> str:
        return timestamp.replace(',', '.') if ',' in timestamp else timestamp

    def add_log(self, log_entry: dict):
        if 'timestamp' in log_entry:
            log_entry['timestamp'] = self.fix_timestamp(log_entry['timestamp'])

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
            elif self.log_type == "sys_event":
                log_objects = [SysEventLogModel(**log) for log in self.buffer]
            elif self.log_type == "urllib3.connectionpool":
                log_objects = [SysEventLogModel(**log) for log in self.buffer]
            else:
                raise ValueError("Invalid log type. Must be 'consumer', 'producer', or 'sys_event'.")

            self.db.bulk_save_objects(log_objects)
            self.db.commit()
            self.buffer.clear()

        except Exception as e:
            print('rollback was called in log_buffer')
            print(e)
            return
            # self.db.rollback()

    def __del__(self):
        self.flush()
