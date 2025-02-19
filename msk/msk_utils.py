import boto3
import time
from config import NUM_BROKERS, SECURITY_GROUP_ID, SUBNET_ID_ONE, SUBNET_ID_TWO

msk_client = boto3.client('kafka', region_name='eu-north-1')

def create_kafka_cluster_with_default_access():
    """
    Create an Amazon MSK cluster without public access initially.
    """
    response = msk_client.create_cluster(
        ClusterName='MyKafkaCluster',
        KafkaVersion='2.8.2.tiered', 
        NumberOfBrokerNodes=int(NUM_BROKERS),
        BrokerNodeGroupInfo={
            'InstanceType': 'kafka.t3.small',
            'ClientSubnets': [SUBNET_ID_ONE, SUBNET_ID_TWO],
            'SecurityGroups': [SECURITY_GROUP_ID],
        },
        ClientAuthentication={
            'Sasl': {
                'Iam': {
                    'Enabled': True 
                }
            }
        },
        EncryptionInfo={
            'EncryptionInTransit': {'ClientBroker': 'TLS'},
        }
    )

    cluster_arn = response['ClusterArn']
    print(f"Created Kafka cluster with ARN: {cluster_arn}")
    return cluster_arn

def get_bootstrap_brokers(cluster_arn):
    response = msk_client.get_bootstrap_brokers(ClusterArn=cluster_arn)
    brokers = response['BootstrapBrokerStringSaslIam']
    print(f"Bootstrap brokers: {brokers}")
    return brokers

def list_running_kafka_clusters():
    return msk_client.list_clusters_v2()['ClusterInfoList']
