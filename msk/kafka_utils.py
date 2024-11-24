import json
import socket
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError
from msk_token_provider import MSKTokenProvider

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
    Create a Kafka producer with SASL/OAUTHBEARER authentication.
    """
    try:
        producer = KafkaProducer(
            bootstrap_servers=','.join(brokers),
            security_protocol='SASL_SSL',
            sasl_mechanism='OAUTHBEARER',
            sasl_oauth_token_provider=tp,
            client_id=socket.gethostname(),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        )
        print("Kafka Producer created successfully.")
        return producer
    except Exception as e:
        print(f"Failed to create Kafka Producer: {e}")
        return None

def create_consumer(brokers, topic_name):
    """
    Create a Kafka consumer with SASL/OAUTHBEARER authentication.
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
        )
        print("Kafka Consumer created successfully.")
        return consumer
    except Exception as e:
        print(f"Failed to create Kafka Consumer: {e}")
        return None

def list_kafka_topics(brokers):
    """
    List all Kafka topics in the specified brokers.
    """
    try:
        consumer = KafkaConsumer(
            bootstrap_servers=','.join(brokers),
            security_protocol='SASL_SSL',
            sasl_mechanism='OAUTHBEARER',
            sasl_oauth_token_provider=tp,
            client_id=socket.gethostname(),
            group_id="kafka-topic-list-group",
            auto_offset_reset="earliest",
        )
        topics = consumer.topics()
        return topics
    except KafkaError as e:
        print(f"Error while listing Kafka topics: {e}")
        return []