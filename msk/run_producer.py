from kafka_utils import create_producer
from kafka_config import (  
    DEFAULT_BATCH_SIZE, DEFAULT_LINGER_MS, DEFAULT_COMPRESSION_TYPE,
    DEFAULT_MAX_REQUEST_SIZE, DEFAULT_ACKS,
)

def run_producer(brokers, topic_name):
    """
    Execute the Kafka producer to send current configurations as messages.
    """
    producer = create_producer(brokers)  

    if producer:
        producer_id = producer.config['client_id']
        print(f"[Producer-{producer_id}] Kafka Producer initialized.")

        
        message = {
            "producer_id": producer_id,
            "batch_size": DEFAULT_BATCH_SIZE,
            "linger_ms": DEFAULT_LINGER_MS,
            "compression_type": DEFAULT_COMPRESSION_TYPE,
            "max_request_size": DEFAULT_MAX_REQUEST_SIZE,
            "acks": DEFAULT_ACKS,
        }

        try:
            
            producer.send(topic_name, value=message)
            producer.flush()
            print(f"[Producer-{producer_id}] Sent message: {message}")
        except Exception as e:
            print(f"[Producer-{producer_id}] Failed to send message: {e}")
    else:
        print("Failed to initialize Kafka Producer.")

