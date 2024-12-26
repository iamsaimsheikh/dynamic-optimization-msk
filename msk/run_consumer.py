from kafka_utils import create_consumer

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
