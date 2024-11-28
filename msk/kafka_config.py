import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv(dotenv_path='../kafka.env')

# Kafka Producer Default Configurations
DEFAULT_BATCH_SIZE = int(os.getenv('DEFAULT_BATCH_SIZE', 16384))
DEFAULT_LINGER_MS = int(os.getenv('DEFAULT_LINGER_MS', 5))
DEFAULT_COMPRESSION_TYPE = os.getenv('DEFAULT_COMPRESSION_TYPE', 'gzip')
DEFAULT_MAX_REQUEST_SIZE = int(os.getenv('DEFAULT_MAX_REQUEST_SIZE', 1048576))
DEFAULT_ACKS = os.getenv('DEFAULT_ACKS', 'all')

# Kafka Consumer Default Configurations
DEFAULT_FETCH_MAX_BYTES = int(os.getenv('DEFAULT_FETCH_MAX_BYTES', 52428800))
DEFAULT_MAX_POLL_RECORDS = int(os.getenv('DEFAULT_MAX_POLL_RECORDS', 500))
DEFAULT_SESSION_TIMEOUT_MS = int(os.getenv('DEFAULT_SESSION_TIMEOUT_MS', 30000))
DEFAULT_HEARTBEAT_INTERVAL_MS = int(os.getenv('DEFAULT_HEARTBEAT_INTERVAL_MS', 3000))
