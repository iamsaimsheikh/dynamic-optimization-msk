import threading
import time
from kafka_utils import create_consumer
from helpers.logging_utils import log_consumer_operation
from kafka_config import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_LINGER_MS,
    DEFAULT_COMPRESSION_TYPE,
    DEFAULT_MAX_REQUEST_SIZE,
    DEFAULT_ACKS,
)
from helpers.log_buffer import LogBuffer
from database.db import get_db
from database.models.consumer_log_model import ConsumerLogModel

db_session = get_db()
consumer_log_buffer = LogBuffer(
    db=db_session, log_type="consumer", buffer_size=100
)


def consume_messages(brokers, topic_name, consumer_id):
    """
    Consume messages from Kafka topic for a given consumer.
    """
    consumer = create_consumer(brokers, topic_name)

    if consumer:
        log_consumer_operation(
            consumer_id,
            "Initialized",
            "Consumer initialized",
            success=True,
            buffer=consumer_log_buffer,
        )

        try:
            # Listen for messages
            for message in consumer:
                # Simulate processing the message (you can replace this with your own logic)
                time.sleep(2)
                log_consumer_operation(
                    consumer_id,
                    "Received",
                    f"Received message: {message.value}",
                    success=True,
                    buffer=consumer_log_buffer,
                )

        except Exception as e:
            log_consumer_operation(
                consumer_id,
                "Failed",
                f"Failed to consume messages: {str(e)}",
                success=False,
                buffer=consumer_log_buffer,
            )
    else:
        log_consumer_operation(
            consumer_id,
            "Failed",
            "Failed to initialize Kafka Consumer",
            success=False,
            buffer=consumer_log_buffer,
        )


def run_consumer_cluster(brokers, topic_name, num_consumers=5):
    """
    Run multiple consumer threads concurrently.
    """
    threads = []

    # Create and start the consumer threads
    for i in range(num_consumers):
        consumer_id = i + 1  # Each consumer gets a unique ID
        thread = threading.Thread(
            target=consume_messages, args=(brokers, topic_name, consumer_id)
        )
        thread.daemon = True  # Daemon thread runs in the background
        threads.append(thread)
        thread.start()

    # Threads are running in the background; main thread can continue with other work
    print("Consumer cluster is running in the background.")
