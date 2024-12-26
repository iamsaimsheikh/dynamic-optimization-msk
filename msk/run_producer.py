from kafka_utils import create_producer
from kafka_config import (  
    DEFAULT_BATCH_SIZE, DEFAULT_LINGER_MS, DEFAULT_COMPRESSION_TYPE,
    DEFAULT_MAX_REQUEST_SIZE, DEFAULT_ACKS,
)
import threading
import time
import json
import os
import signal

def run_producer(brokers, topic_name, unique_id):
    """
    Execute the Kafka producer to send current configurations as messages periodically.
    """
    try:
        producer = create_producer(brokers, unique_id)

        if not producer:
            print(f"[Producer-{unique_id}] Initialization failed.")
            return

        producer_id = producer.config['client_id']
        thread_id = threading.get_ident()  # Get the current thread's ID
        print(f"[Producer-{producer_id}] Kafka Producer initialized. Thread ID: {thread_id}")

        while True:
            # Create the message payload
            message = {
                "producer_id": producer_id,
                "batch_size": DEFAULT_BATCH_SIZE,
                "linger_ms": DEFAULT_LINGER_MS,
                "compression_type": DEFAULT_COMPRESSION_TYPE,
                "max_request_size": DEFAULT_MAX_REQUEST_SIZE,
                "acks": DEFAULT_ACKS,
            }

            try:
                # Serialize the message to JSON and send it
                message_bytes = json.dumps(message).encode('utf-8')
                producer.send(topic_name, value=message_bytes)
                producer.flush()
                print(f"[Producer-{producer_id}] Sent message: {message}")
            except Exception as e:
                print(f"[Producer-{producer_id}] Failed to send message: {e}")

            time.sleep(2)  # Send messages every 2 seconds

    except Exception as e:
        print(f"[Producer-{unique_id}] Encountered an error: {e}")

def run_producer_cluster(brokers, topic_name, num_producers=5):
    """
    Run a cluster of producers, each sending messages to the specified topic.
    """
    threads = []

    for i in range(num_producers):
        unique_id = f"producer_{i+1}"
        thread = threading.Thread(target=run_producer, args=(brokers, topic_name, unique_id))
        thread.daemon = True  # Allows the program to exit even if threads are still running
        threads.append(thread)
        thread.start()

    print("Producer cluster is running in the background.")
