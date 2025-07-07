import threading
import time
import json
from kafka_utils import create_consumer
from helpers.logging_utils import log_consumer_operation
from helpers.log_buffer import LogBuffer
from helpers.analytics_buffer import AnalyticsBuffer
from database.db import get_db
from database.models.consumer_log_model import ConsumerLogModel


def consume_messages(
    brokers,
    topic_name,
    consumer_id,
    db_session,
    analytics_buffer,
    consumer_config,
    stop_event,
    epsilon
):
    consumer_log_buffer = LogBuffer(db=db_session, log_type="consumer", buffer_size=2000)
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
            while not stop_event.is_set():
                # Poll for up to 1 second
                records = consumer.poll(timeout_ms=1000)

                if not records:
                    continue  # No messages, keep polling

                for tp, messages in records.items():
                    for message in messages:
                        consumer.commit()
                        # sleep_time = max(0.01, 1.5 * epsilon)
                        # time.sleep(sleep_time)

                        message_id = None
                        try:
                            message_value = message.value.decode("utf-8")
                            parsed_value = json.loads(message_value)
                            message_id = parsed_value.get("message_id", "None")
                            print(f"[DEBUG] Message Payload (parsed): {parsed_value}")
                        except Exception as e:
                            print(f"[DEBUG] Failed to parse message: {e}")
                            message_value = str(message.value)

                        # sleep_time = max(0.0005, 0.05 * epsilon)
                        time.sleep(sleep_time)
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


def run_consumer_cluster(
    brokers, topic_name, num_consumers=5, consumer_config=None, stop_event=None, epsilon=1
):
    if consumer_config is None:
        consumer_config = {}

    if stop_event is None:
        stop_event = threading.Event()

    db_session = get_db()

    analytics_buffer = AnalyticsBuffer(
        db=db_session,
        length=2000,
        consumer_configs=consumer_config,
        consumer_stop_event=stop_event,
    )

    threads = []

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
                stop_event,
                epsilon
            ),
        )
        thread.daemon = True
        threads.append(thread)
        thread.start()

    print("Consumer cluster is running in the background.")
