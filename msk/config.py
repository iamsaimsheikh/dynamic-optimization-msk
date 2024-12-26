import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path='../.env')

# Environment Configuration
ENV = os.getenv('ENV', 'production')  # Default to 'production'

if ENV == 'local':
    NUM_BROKERS = 3
    BROKERS = 'localhost:9092,localhost:9093,localhost:9094'
    BROKER_ONE = os.getenv('BROKER_ONE')
    BROKER_TWO = os.getenv('BROKER_TWO')
else:
    NUM_BROKERS = os.getenv('NUM_BROKERS')
    BROKER_ONE = os.getenv('BROKER_ONE')
    BROKER_TWO = os.getenv('BROKER_TWO')
    BROKERS = f"{BROKER_ONE},{BROKER_TWO}"

# Shared Configuration
SECURITY_GROUP_ID = os.getenv('SECURITY_GROUP_ID')
SUBNET_ID_ONE = os.getenv('SUBNET_ID_ONE')
SUBNET_ID_TWO = os.getenv('SUBNET_ID_TWO')
MSK_CLUSTER_ARN = os.getenv('MSK_CLUSTER_ARN')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_REGION = os.getenv('AWS_REGION')
MSK_USERNAME = os.getenv('MSK_USERNAME')
MSK_PASSWORD = os.getenv('MSK_PASSWORD')

# Debug Output
print(f"Environment: {ENV}")
print(f"Number of Brokers: {NUM_BROKERS}")
print(f"Brokers: {BROKERS}")
if ENV != 'local':
    print(f"MSK Cluster ARN: {MSK_CLUSTER_ARN}")
