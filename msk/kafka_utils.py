import json
import socket
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError
from msk_token_provider import MSKTokenProvider
from kafka_config import (  # Import the default configurations
    DEFAULT_BATCH_SIZE, DEFAULT_LINGER_MS, DEFAULT_COMPRESSION_TYPE,
    DEFAULT_MAX_REQUEST_SIZE, DEFAULT_ACKS,
    DEFAULT_FETCH_MAX_BYTES, DEFAULT_MAX_POLL_RECORDS,
    DEFAULT_SESSION_TIMEOUT_MS, DEFAULT_HEARTBEAT_INTERVAL_MS,
)

tp = MSKTokenProvider()

def create_kafka_topic(brokers, topic_name):
    """
    Create a Kafka topic using Kafka Admin Client with SASL/OAUTHBEARER authentication.
    """
    try:
        # Initialize the Kafka Admin Client
        admin_client = KafkaAdminClient(
            bootstrap_servers=','.join(brokers),
            security_protocol='SASL_SSL',
            sasl_mechanism='OAUTHBEARER',
            sasl_oauth_token_provider=tp,
            client_id=socket.gethostname(),
        )

        # Define the new topic
        topic = NewTopic(name=topic_name, num_partitions=1, replication_factor=2)

        # Create the topic
        response = admin_client.create_topics(new_topics=[topic], validate_only=False)

        # Check for errors in the response
        for topic, error in response.topic_errors.items():
            if error.code == 0:
                print(f"Kafka topic '{topic}' created successfully.")
            else:
                print(f"Failed to create topic '{topic}': {error.message}")
    except Exception as e:
        print(f"An error occurred: {e}")


def create_producer(brokers):
    """
    Create a Kafka producer with SASL/OAUTHBEARER authentication and default performance configurations.
    """
    try:
        producer = KafkaProducer(
            bootstrap_servers=','.join(brokers),
            security_protocol='SASL_SSL',
            sasl_mechanism='OAUTHBEARER',
            sasl_oauth_token_provider=tp,
            client_id=socket.gethostname(),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            batch_size=DEFAULT_BATCH_SIZE,
            linger_ms=DEFAULT_LINGER_MS,
            compression_type=DEFAULT_COMPRESSION_TYPE,
            max_request_size=DEFAULT_MAX_REQUEST_SIZE,
            acks=DEFAULT_ACKS,
        )
        print("Kafka Producer created successfully with default configurations.")
        return producer
    except Exception as e:
        print(f"Failed to create Kafka Producer: {e}")
        return None


def create_consumer(brokers, topic_name):
    """
    Create a Kafka consumer with SASL/OAUTHBEARER authentication and default performance configurations.
    """
    try:
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=','.join(brokers),
            security_protocol='SASL_SSL',
            sasl_mechanism='OAUTHBEARER',
            sasl_oauth_token_provider=tp,
            client_id=socket.gethostname(),
            group_id="my-group",
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            fetch_max_bytes=DEFAULT_FETCH_MAX_BYTES,
            max_poll_records=DEFAULT_MAX_POLL_RECORDS,
            session_timeout_ms=DEFAULT_SESSION_TIMEOUT_MS,
            heartbeat_interval_ms=DEFAULT_HEARTBEAT_INTERVAL_MS,
        )
        print("Kafka Consumer created successfully with default configurations.")
        return consumer
    except Exception as e:
        print(f"Failed to create Kafka Consumer: {e}")
        return None


def list_kafka_topics(brokers):
    """
    List Kafka topics using Kafka Admin Client with SASL/OAUTHBEARER authentication.
    """
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=','.join(brokers),
            security_protocol='SASL_SSL',
            sasl_mechanism='OAUTHBEARER',
            sasl_oauth_token_provider=tp,
            client_id=socket.gethostname(),
        )

        topics = admin_client.list_topics()
        print("Kafka topics available on the cluster:")
        for topic in topics:
            print(f" - {topic}")
        return topics
    except Exception as e:
        print(f"An error occurred while listing topics: {e}")
