import sys
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path='../kafka.env')

# Dynamically add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
import json
from config import MSK_CLUSTER_ARN, BROKER_ONE, BROKER_TWO, BROKERS, NUM_BROKERS
from msk_utils import create_kafka_cluster_with_default_access, list_running_kafka_clusters, get_bootstrap_brokers
from kafka_utils import create_kafka_topic, create_producer, create_consumer, list_kafka_topics
from run_consumer import run_consumer_cluster
from run_producer import run_producer_cluster
import threading
import argparse

parser = argparse.ArgumentParser(description="Kafka Config Runner")

# Producer configs
parser.add_argument("--batch-size", type=int, default=int(os.getenv("DEFAULT_BATCH_SIZE", 16384)))
parser.add_argument("--linger-ms", type=int, default=int(os.getenv("DEFAULT_LINGER_MS", 5)))
parser.add_argument("--compression-type", type=str, default=os.getenv("DEFAULT_COMPRESSION_TYPE", "gzip"))
parser.add_argument("--max-request-size", type=int, default=int(os.getenv("DEFAULT_MAX_REQUEST_SIZE", 1048576)))
parser.add_argument("--acks", type=str, default=os.getenv("DEFAULT_ACKS", "all"))

# Consumer configs
parser.add_argument("--fetch-max-bytes", type=int, default=int(os.getenv("DEFAULT_FETCH_MAX_BYTES", 52428800)))
parser.add_argument("--max-poll-records", type=int, default=int(os.getenv("DEFAULT_MAX_POLL_RECORDS", 500)))
parser.add_argument("--session-timeout-ms", type=int, default=int(os.getenv("DEFAULT_SESSION_TIMEOUT_MS", 30000)))
parser.add_argument("--heartbeat-interval-ms", type=int, default=int(os.getenv("DEFAULT_HEARTBEAT_INTERVAL_MS", 30000)))

args = parser.parse_args()

# Store producer and consumer configs as dictionaries
producer_config = {
    "batch_size": args.batch_size,
    "linger_ms": args.linger_ms,
    "compression_type": args.compression_type,
    "max_request_size": args.max_request_size,
    "acks": args.acks,
}

consumer_config = {
    "fetch_max_bytes": args.fetch_max_bytes,
    "max_poll_records": args.max_poll_records,
    "session_timeout_ms": args.session_timeout_ms,
    "heartbeat_interval_ms": args.heartbeat_interval_ms,
}

topic_name = 'iot_topic'

def main():
    if not BROKERS:
        # Step 1: Create Kafka Cluster
        running_kafka_clusters = list_running_kafka_clusters()

        brokers = [BROKER_ONE, BROKER_TWO]
        if not running_kafka_clusters:
            print("No running Kafka clusters found. Creating a new cluster...")
            cluster_arn = create_kafka_cluster_with_default_access()
            print(f"Cluster creation initiated: {cluster_arn}")

            # Wait for the cluster to become active
            while True:
                print("Waiting for the cluster to appear as active...")
                time.sleep(300)  # Wait 5 minutes before checking again
                running_kafka_clusters = list_running_kafka_clusters()

                if running_kafka_clusters:
                    print("Cluster is now active!")
                    break
        else:
            print("Kafka clusters are already running.")
            for cluster in running_kafka_clusters:
                print(f" - Cluster ARN: {cluster['ClusterArn']}")

        # Step 2: Get Brokers and Create Topic
        if not brokers:
            brokers = get_bootstrap_brokers(MSK_CLUSTER_ARN)
        
        print(f' - brokers: {brokers}')
        
        topics = list_kafka_topics(brokers)
        if topic_name not in topics:
            create_kafka_topic(brokers, topic_name)
        else:
            print(f' - topic selected: {topic_name}')
        
        # Run producer and consumer clusters concurrently in background threads
        producer_thread = threading.Thread(target=run_producer_cluster, args=(brokers, topic_name, 5))
        consumer_thread = threading.Thread(target=run_consumer_cluster, args=(brokers, topic_name, 5))

        producer_thread.daemon = True
        consumer_thread.daemon = True

        producer_thread.start()
        consumer_thread.start()

        # Main thread can continue doing other tasks or exit
        print("Producer and Consumer clusters are running in the background.")
        while True:
            time.sleep(10)  # Keep the main thread alive if necessary

    else:
        # If brokers are already provided, run the producer and consumer clusters concurrently
        producer_thread = threading.Thread(target=run_producer_cluster, args=(BROKERS, topic_name, 10, producer_config))
        consumer_thread = threading.Thread(target=run_consumer_cluster, args=(BROKERS, topic_name, 2, consumer_config))

        producer_thread.daemon = True
        consumer_thread.daemon = True

        producer_thread.start()
        consumer_thread.start()

        # Main thread can continue doing other tasks or exit
        print("Producer and Consumer clusters are running in the background.")
        while True:
            time.sleep(10)  # Keep the main thread alive if necessary

if __name__ == "__main__":
    main()
