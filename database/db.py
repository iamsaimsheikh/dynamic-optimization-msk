from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from database.config import Config
import threading

# Database URL from the configuration
DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI

# Create the database engine
engine = create_engine(DATABASE_URL)

# Session local configuration
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for ORM models
Base = declarative_base()

# Thread-local storage for sessions
_thread_local = threading.local()

def get_db():
    """
    Retrieve a session for the current thread using thread-local storage.
    If the session already exists for the current thread, it will be reused.
    """
    if not hasattr(_thread_local, "session"):
        _thread_local.session = SessionLocal()
    return _thread_local.session

def close_db_session():
    """
    Close the session for the current thread.
    """
    if hasattr(_thread_local, "session"):
        _thread_local.session.close()
        del _thread_local.session

def init_db():
    """
    Initialize the database by creating all tables based on the models.
    """
    from models.checkpoint_model import CheckpointModel
    from models.consumer_log_model import ConsumerLogModel
    from models.producer_log_model import ProducerLogModel
    from models.sys_event_log_model import SysEventLogModel
    from models.kafka_batch_stats_model import KafkaBatchStatsModel
    Base.metadata.create_all(bind=engine)
