import sys
import os

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
        producer_thread = threading.Thread(target=run_producer_cluster, args=(BROKERS, topic_name, 5))
        consumer_thread = threading.Thread(target=run_consumer_cluster, args=(BROKERS, topic_name, 2))

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
