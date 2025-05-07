from sqlalchemy import Column, Integer, String, TIMESTAMP, BigInteger, Boolean
from database.db import Base

class ProducerLogModel(Base):
    __tablename__ = "producer_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP, nullable=False)
    case_id = Column(BigInteger, nullable=False)
    action = Column(String, nullable=False)
    producer_id = Column(String, nullable=False)
    batch_size = Column(Integer, nullable=False)
    linger_ms = Column(Integer, nullable=False)
    compression_type = Column(String, nullable=False)
    max_request_size = Column(Integer, nullable=False)
    acks = Column(String, nullable=False)
    message_details = Column(String, nullable=True)
    message_id = Column(String, nullable=False)
    is_analytics_processed = Column(Boolean, nullable=False, default=False)
