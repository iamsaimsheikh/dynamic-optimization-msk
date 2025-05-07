import json
import socket
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError
from msk_token_provider import MSKTokenProvider
from kafka_config import ( 
    DEFAULT_BATCH_SIZE, DEFAULT_LINGER_MS, DEFAULT_COMPRESSION_TYPE,
    DEFAULT_MAX_REQUEST_SIZE, DEFAULT_ACKS,
    DEFAULT_FETCH_MAX_BYTES, DEFAULT_MAX_POLL_RECORDS,
    DEFAULT_SESSION_TIMEOUT_MS, DEFAULT_HEARTBEAT_INTERVAL_MS,
)
from config import BROKERS

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


def create_producer(brokers, unique_id, producer_config={}):
    """
    Create a Kafka producer with SASL/OAUTHBEARER authentication and either provided or default performance configurations.
    """
    try:
        # Use configs from input or fallback to defaults
        batch_size = producer_config.get("batch_size", DEFAULT_BATCH_SIZE)
        linger_ms = producer_config.get("linger_ms", DEFAULT_LINGER_MS)
        compression_type = producer_config.get("compression_type", DEFAULT_COMPRESSION_TYPE)
        max_request_size = producer_config.get("max_request_size", DEFAULT_MAX_REQUEST_SIZE)
        acks = producer_config.get("acks", DEFAULT_ACKS)

        if not BROKERS:
            producer = KafkaProducer(
                bootstrap_servers=','.join(brokers),
                security_protocol='SASL_SSL',
                sasl_mechanism='OAUTHBEARER',
                sasl_oauth_token_provider=tp,
                client_id=f"{socket.gethostname()}_{unique_id}",
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                batch_size=batch_size,
                linger_ms=linger_ms,
                compression_type=compression_type,
                max_request_size=max_request_size,
                acks=acks,
            )
        else:
            producer = KafkaProducer(bootstrap_servers=BROKERS)

        print(f"Kafka Producer {unique_id} created successfully with configurations.")
        return producer

    except Exception as e:
        print(f"Failed to create Kafka Producer {unique_id}: {e}")
        return None


def create_consumer(brokers, topic_name, consumer_config=None):
    """
    Create a Kafka consumer with SASL/OAUTHBEARER authentication and either provided or default performance configurations.
    """
    try:
        # Use configs from input or fallback to defaults
        fetch_max_bytes = consumer_config.get("fetch_max_bytes") if consumer_config else DEFAULT_FETCH_MAX_BYTES
        max_poll_records = consumer_config.get("max_poll_records") if consumer_config else DEFAULT_MAX_POLL_RECORDS
        session_timeout_ms = consumer_config.get("session_timeout_ms") if consumer_config else DEFAULT_SESSION_TIMEOUT_MS
        heartbeat_interval_ms = consumer_config.get("heartbeat_interval_ms") if consumer_config else DEFAULT_HEARTBEAT_INTERVAL_MS

        if not BROKERS:
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
                fetch_max_bytes=fetch_max_bytes,
                max_poll_records=max_poll_records,
                session_timeout_ms=session_timeout_ms,
                heartbeat_interval_ms=heartbeat_interval_ms,
            )
        else:
            consumer = KafkaConsumer(
                topic_name,
                bootstrap_servers=BROKERS,
                group_id='my-kafka-group',
                auto_offset_reset='earliest'
            )

        print("Kafka Consumer created successfully with configurations.")
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
