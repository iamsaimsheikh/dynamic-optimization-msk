import time
import json
import threading
from uuid import uuid4
from database.db import get_db
from kafka_utils import create_producer
from helpers.logging_utils import log_producer_operation
from kafka_config import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_LINGER_MS,
    DEFAULT_COMPRESSION_TYPE,
    DEFAULT_MAX_REQUEST_SIZE,
    DEFAULT_ACKS,
)
from helpers.log_buffer import LogBuffer

# Shared counter and lock for total messages across all threads
total_messages_sent = 0
total_messages_lock = threading.Lock()


def run_producer(brokers, topic_name, unique_id, producer_config=None, stop_event=None, epsilon=1):
    """
    Run a single producer thread that sends messages with unique message_ids.
    Each thread has its own LogBuffer and DB session.
    """
    global total_messages_sent

    if producer_config is None:
        producer_config = {}

    if stop_event is None:
        stop_event = threading.Event()  # runs indefinitely if never set

    # Create DB session and LogBuffer per thread to avoid conflicts
    db_session = get_db()
    producer_log_buffer = LogBuffer(db=db_session, log_type="producer", buffer_size=2000)

    try:
        producer = create_producer(brokers, unique_id, producer_config)
        if not producer:
            log_producer_operation(
                unique_id,
                "Failed",
                "Producer initialization failed.",
                success=False,
                buffer=producer_log_buffer,
                message_id=None,
            )
            return

        producer_id = producer.config.get("client_id", unique_id)
        thread_id = threading.get_ident()
        log_producer_operation(
            producer_id,
            "Initialized",
            f"Producer initialized in thread {thread_id}",
            success=True,
            buffer=producer_log_buffer,
            message_id=None,
        )

        while not stop_event.is_set():
            # Generate unique message ID per message
            message_id = uuid4().hex

            batch_size = producer_config.get("batch_size", DEFAULT_BATCH_SIZE)
            linger_ms = producer_config.get("linger_ms", DEFAULT_LINGER_MS)
            compression_type = producer_config.get("compression_type", DEFAULT_COMPRESSION_TYPE)
            max_request_size = producer_config.get("max_request_size", DEFAULT_MAX_REQUEST_SIZE)
            acks = producer_config.get("acks", DEFAULT_ACKS)

            message = {
                "producer_id": producer_id,
                "batch_size": batch_size,
                "linger_ms": linger_ms,
                "compression_type": compression_type,
                "max_request_size": max_request_size,
                "acks": acks,
                "message_id": message_id,
            }

            try:
                message_bytes = json.dumps(message).encode("utf-8")
                producer.send(topic_name, value=message_bytes)
                producer.flush()
                
                # sleep_time = max(0.1, 1 * epsilon)
                # print(sleep_time)
                # time.sleep(sleep_time)

                log_producer_operation(
                    producer_id,
                    "Sent",
                    message,
                    success=True,
                    buffer=producer_log_buffer,
                    message_id=message_id,
                )

                # Debug print for message ID
                print(f"[DEBUG] Producer {producer_id} sent message_id: {message_id}")

                with total_messages_lock:
                    total_messages_sent += 1
                    # Optional: stop after 10 messages total
                    if stop_event and total_messages_sent >= 2000:
                        stop_event.set()

            except Exception as e:
                log_producer_operation(
                    producer_id,
                    "Failed",
                    str(e),
                    success=False,
                    buffer=producer_log_buffer,
                    message_id=message_id,
                )
            
            


    except Exception as e:
        log_producer_operation(
            unique_id,
            "Failed",
            str(e),
            success=False,
            buffer=producer_log_buffer,
            message_id=None,
        )


def run_producer_cluster(brokers, topic_name, num_producers=5, producer_config=None, stop_event=None, epsilon= 1):
    """
    Runs multiple producer threads to send messages concurrently.
    """
    if producer_config is None:
        producer_config = {}

    if stop_event is None:
        stop_event = threading.Event()  # never stops unless externally set

    threads = []

    for i in range(num_producers):
        unique_id = f"producer_{i + 1}"
        thread = threading.Thread(
            target=run_producer,
            args=(brokers, topic_name, unique_id, producer_config, stop_event, epsilon),
        )
        thread.daemon = True
        threads.append(thread)
        thread.start()

    print("Producer cluster is running.")

    for thread in threads:
        thread.join()

    print("All producer threads finished.")
