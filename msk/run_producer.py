import time
import json
import threading
from kafka_utils import create_producer
from helpers.logging_utils import log_producer_operation
from kafka_config import (
    DEFAULT_BATCH_SIZE, DEFAULT_LINGER_MS, DEFAULT_COMPRESSION_TYPE,
    DEFAULT_MAX_REQUEST_SIZE, DEFAULT_ACKS
)

def run_producer(brokers, topic_name, unique_id):
    """
    Run a Kafka producer in a thread to send periodic messages.
    """
    try:
        # Create producer
        producer = create_producer(brokers, unique_id)
        if not producer:
            error_message = "Producer initialization failed."
            log_producer_operation(unique_id, "Failed", error_message, success=False)
            return

        producer_id = producer.config['client_id']
        thread_id = threading.get_ident()
        log_producer_operation(producer_id, "Initialized", f"Producer initialized in thread {thread_id}", success=True)

        while True:
            message = {
                "producer_id": producer_id,
                "batch_size": DEFAULT_BATCH_SIZE,
                "linger_ms": DEFAULT_LINGER_MS,
                "compression_type": DEFAULT_COMPRESSION_TYPE,
                "max_request_size": DEFAULT_MAX_REQUEST_SIZE,
                "acks": DEFAULT_ACKS
            }

            try:
                message_bytes = json.dumps(message).encode('utf-8')
                producer.send(topic_name, value=message_bytes)
                producer.flush()
                log_producer_operation(producer_id, "Sent", message, success=True)
            except Exception as e:
                error_message = str(e)
                log_producer_operation(producer_id, "Failed", error_message, success=False)

            # Control the message frequency
            time.sleep(2)

    except Exception as e:
        log_producer_operation(unique_id, "Failed", str(e), success=False)

def run_producer_cluster(brokers, topic_name, num_producers=5):
    """
    Run multiple producer threads concurrently.
    """
    threads = []
    for i in range(num_producers):
        unique_id = f"producer_{i+1}"
        thread = threading.Thread(target=run_producer, args=(brokers, topic_name, unique_id))
        thread.daemon = True  # Daemon thread runs in the background
        threads.append(thread)
        thread.start()

    # Threads are running in the background; main thread can continue with other work
    print("Producer cluster is running in the background.")
