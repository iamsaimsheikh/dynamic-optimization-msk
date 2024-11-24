import time
import json
from config import MSK_CLUSTER_ARN, BROKER_ONE, BROKER_TWO
from msk_utils import create_kafka_cluster_with_default_access, list_running_kafka_clusters, get_bootstrap_brokers
from kafka_utils import create_kafka_topic, create_producer, create_consumer, list_kafka_topics

topic_name = "topic_dynamic_configurations"

def main():
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

    # # Step 3: Create Kafka Producer and Send Data
    # producer = create_producer(brokers)
    # for i in range(10):
    #     message = {'message_number': i}
    #     producer.send(topic_name, json.dumps(message).encode('utf-8'))
    #     print(f"Sent: {message}")
    # producer.flush()

    # # Step 4: Create Kafka Consumer and Read Data
    # consumer = create_consumer(brokers, topic_name)
    # for message in consumer:
    #     print(f"Received: {json.loads(message.value.decode('utf-8'))}")
    #     if message.offset == 9:
    #         break  # Stop after 10 messages for this example

if __name__ == "__main__":
    main()
