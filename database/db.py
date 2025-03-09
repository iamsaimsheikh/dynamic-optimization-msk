from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from database.config import Config

DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

_db_session = None

def get_db():
    global _db_session
    if _db_session is None:
        _db_session = SessionLocal()
    return _db_session

def init_db():
    from models.checkpoint_model import CheckpointModel
    from models.consumer_log_model import ConsumerLogModel
    from models.producer_log_model import ProducerLogModel
    from models.sys_event_log_model import SysEventLogModel
    Base.metadata.create_all(bind=engine)
