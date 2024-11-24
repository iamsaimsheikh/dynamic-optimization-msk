import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')

# Load environment variables
SECURITY_GROUP_ID = os.getenv('SECURITY_GROUP_ID')
SUBNET_ID_ONE = os.getenv('SUBNET_ID_ONE')
SUBNET_ID_TWO = os.getenv('SUBNET_ID_TWO')
NUM_BROKERS = os.getenv('NUM_BROKERS')
MSK_CLUSTER_ARN = os.getenv('MSK_CLUSTER_ARN')
BROKER_ONE = os.getenv('BROKER_ONE')
BROKER_TWO = os.getenv('BROKER_TWO')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_REGION = os.getenv('AWS_REGION')
MSK_USERNAME = os.getenv('MSK_USERNAME')
MSK_PASSWORD = os.getenv('MSK_PASSWORD')
