import logging
import json
from drain3 import TemplateMiner
from datetime import datetime
from helpers.log_buffer import LogBuffer
from database.db import get_db
from helpers.utils import MASKING_RULES

template_miner = TemplateMiner()

db_session = get_db()
sys_log_buffer = LogBuffer(db=db_session, log_type="sys_event", buffer_size=100)

log_records = []

def preprocess_log(log):
    for pattern, replacement in MASKING_RULES:
        log = pattern.sub(replacement, log)
    return log

class LogHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        
        try:
            print("Raw Log Entry:", log_entry)
            log_data = json.loads(log_entry)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Problematic Log Entry: {log_entry}")
            return

        log_data["action"] = preprocess_log(log_data["action"])

        result = template_miner.add_log_message(log_data["action"])
        log_data["action"] = result["template_mined"]

        log_records.append(log_data)
        sys_log_buffer.add_log(log_data)