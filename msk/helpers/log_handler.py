import logging
import json
import re
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

# Formatter to escape problematic characters
class CleanJSONFormatter(logging.Formatter):
    def format(self, record):
        clean_msg = self._sanitize_message(record.getMessage())
        record.message = clean_msg
        return super().format(record)

    def _sanitize_message(self, msg):
        # Replace known binary patterns or malformed structures
        msg = re.sub(r"(messages|value)=b'(.*?)'", r"\1='<BINARY>'", msg)
        msg = msg.replace('\\', '\\\\')  # Escape backslashes
        msg = msg.replace('"', '\\"')    # Escape double quotes in values
        return msg

class LogHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)

        # Fix common broken structures before parsing JSON
        # Fix b'' and escape sequences
        log_entry = re.sub(r"(messages|value)=b'(.*?)'", r"\1='<BINARY>'", log_entry)

        try:
            log_data = json.loads(log_entry)
        except json.JSONDecodeError as e:
            return

        # Preprocess and parse template
        log_data["action"] = preprocess_log(log_data["action"])
        result = template_miner.add_log_message(log_data["action"])
        log_data["action"] = result["template_mined"]

        # Store and forward
        log_records.append(log_data)
        sys_log_buffer.add_log(log_data)
