from kafka_utils import create_consumer
from kafka_config import (  # Import configurations
    DEFAULT_FETCH_MAX_BYTES, DEFAULT_MAX_POLL_RECORDS,
    DEFAULT_SESSION_TIMEOUT_MS, DEFAULT_HEARTBEAT_INTERVAL_MS,
)

def run_consumer(brokers, topic_name):
    """
    Execute the Kafka consumer to receive and log messages.
    """
    consumer = create_consumer(brokers, topic_name)  # Create consumer using imported function

    if consumer:
        consumer_id = consumer.config['client_id']
        print(f"[Consumer-{consumer_id}] Kafka Consumer initialized.")
        print(f"[Consumer-{consumer_id}] Waiting for messages...")

        try:
            # Listen for messages
            for message in consumer:
                print(f"[Consumer-{consumer_id}] Received message: {message.value}")
        except Exception as e:
            print(f"[Consumer-{consumer_id}] Failed to consume messages: {e}")
    else:
        print("Failed to initialize Kafka Consumer.")
