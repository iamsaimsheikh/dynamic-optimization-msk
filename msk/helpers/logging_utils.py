import json
import logging
import os
import time
import threading
from kafka_config import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_LINGER_MS,
    DEFAULT_COMPRESSION_TYPE,
    DEFAULT_MAX_REQUEST_SIZE,
    DEFAULT_ACKS,
)
from helpers.log_handler import LogHandler, CleanJSONFormatter

list_handler = LogHandler()
list_handler.setFormatter(
    CleanJSONFormatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "thread_id": "%(thread)d", "case_id": "%(thread)d", "entity_name": "%(name)s", "action": "%(message)s"}'
    )
)

json_log_file_path = "log_files/sys_logs.json"
os.makedirs(os.path.dirname(json_log_file_path), exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "thread_id": "%(thread)d", "case_id": "%(thread)d", "entity_name": "%(name)s", "action": "%(message)s"},',
    datefmt="%Y-%m-%d %H:%M:%S.%f",
    handlers=[logging.FileHandler(json_log_file_path, mode="a"), list_handler],
)


def log_producer_operation(
    producer_id, action, message, success=True, buffer=None, message_id=None
):
    """
    Log producer actions to a unified JSON log file, Excel file, and console.
    """
    thread_id = threading.get_ident()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    # If success is False, capture the error message (if any)
    message_details = message if success else f"Error: {message}"

    # If message is a dictionary, convert it to JSON string before logging it
    if isinstance(message, dict):
        message_details = json.dumps(message)

    log_entry = {
        "timestamp": timestamp,
        "case_id": thread_id,
        "action": action,
        "producer_id": producer_id,
        "batch_size": DEFAULT_BATCH_SIZE,
        "linger_ms": DEFAULT_LINGER_MS,
        "compression_type": DEFAULT_COMPRESSION_TYPE,
        "max_request_size": DEFAULT_MAX_REQUEST_SIZE,
        "acks": DEFAULT_ACKS,
        "message_details": message_details,
        "message_id": message_id if isinstance(message_id, str) else "none",
    }

    if buffer is not None:
        buffer.add_log(log_entry)


def log_consumer_operation(
    consumer_id, action, message, success=True, buffer=None, message_id="None"
):
    """
    Log consumer actions to a unified JSON log file, Excel file, and console.
    """
    thread_id = threading.get_ident()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    # If success is False, capture the error message (if any)
    message_details = message if success else f"Error: {message}"

    # If message is a dictionary, convert it to JSON string before logging it
    if isinstance(message, dict):
        message_details = json.loads(message)
        
    log_entry = {
        "timestamp": timestamp,
        "case_id": thread_id,
        "action": action,
        "consumer_id": consumer_id,
        "batch_size": DEFAULT_BATCH_SIZE,
        "linger_ms": DEFAULT_LINGER_MS,
        "compression_type": DEFAULT_COMPRESSION_TYPE,
        "max_request_size": DEFAULT_MAX_REQUEST_SIZE,
        "acks": DEFAULT_ACKS,
        "message_details": message_details,
        "message_id": message_id
    }
    
    if buffer is not None:
        buffer.add_log(log_entry)
