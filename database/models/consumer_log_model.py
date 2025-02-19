from sqlalchemy import Column, Integer, BigInteger, String, TIMESTAMP
from database.db import Base

class ConsumerLogModel(Base):
    __tablename__ = "consumer_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP, nullable=False)
    case_id = Column(BigInteger, nullable=False)
    action = Column(String, nullable=False)
    consumer_id = Column(String, nullable=False)
    batch_size = Column(Integer, nullable=False)
    linger_ms = Column(Integer, nullable=False)
    compression_type = Column(String, nullable=False)
    max_request_size = Column(Integer, nullable=False)
    acks = Column(String, nullable=False)
    message_details = Column(String, nullable=True)
