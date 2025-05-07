import threading
import time
import json
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
from helpers.analytics_buffer import AnalyticsBuffer
from database.db import get_db
from database.models.consumer_log_model import ConsumerLogModel


def consume_messages(
    brokers, topic_name, consumer_id, db_session, analytics_buffer, consumer_config
):
    consumer_log_buffer = LogBuffer(db=db_session, log_type="consumer", buffer_size=10)

    consumer = create_consumer(brokers, topic_name, consumer_config)

    if consumer:
        log_consumer_operation(
            consumer_id,
            "Initialized",
            "Consumer initialized",
            success=True,
            buffer=consumer_log_buffer,
        )

        try:
            for message in consumer:
                time.sleep(2)
                message_id = None

                try:
                    message_value = message.value.decode("utf-8")
                    parsed_value = json.loads(message_value)
                    message_id = parsed_value.get("message_id", "None")
                    print(f"[DEBUG] Message Payload (parsed): {parsed_value}")
                except Exception as e:
                    print(f"[DEBUG] Failed to parse message: {e}")
                    message_value = str(message.value)

                log_consumer_operation(
                    consumer_id,
                    "Received",
                    f"Received message: {message_value}",
                    success=True,
                    buffer=consumer_log_buffer,
                    message_id=message_id,
                )

                if message_id:
                    analytics_buffer.appendId(message_id)

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


def run_consumer_cluster(brokers, topic_name, num_consumers=5, consumer_config={}):
    threads = []
    db_session = get_db()
    analytics_buffer = AnalyticsBuffer(
        db=db_session, length=20, consumer_configs=consumer_config
    )

    for i in range(num_consumers):
        consumer_id = i + 1
        thread = threading.Thread(
            target=consume_messages,
            args=(
                brokers,
                topic_name,
                consumer_id,
                db_session,
                analytics_buffer,
                consumer_config,
            ),
        )
        thread.daemon = True
        threads.append(thread)
        thread.start()

    print("Consumer cluster is running in the background.")
