from sqlalchemy import Column, Integer, Float, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from database.db import Base
import uuid
from datetime import datetime

class KafkaRLTrainingLogModel(Base):
    __tablename__ = "kafka_rl_training_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    episode = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    # Current configuration parameters
    conf_linger_ms = Column(Integer, nullable=False)
    conf_max_request_size = Column(Integer, nullable=False)
    conf_fetch_max_bytes = Column(Integer, nullable=False)
    conf_max_poll_records = Column(Integer, nullable=False)
    conf_session_timeout_ms = Column(Integer, nullable=False)
    conf_heartbeat_interval_ms = Column(Integer, nullable=False)

    # Performance metrics
    average_throughput_mps = Column(Float, nullable=False)
    average_latency_ms = Column(Float, nullable=False)
    total_cost_usd = Column(Float, nullable=False)
    batch_size = Column(Integer, nullable=False)

    # Reinforcement learning related fields
    reward = Column(Float, nullable=False)
    action_taken = Column(Integer, nullable=False)

    # Next configuration parameters after RL action
    next_conf_linger_ms = Column(Integer, nullable=False)
    next_conf_max_request_size = Column(Integer, nullable=False)
    next_conf_fetch_max_bytes = Column(Integer, nullable=False)
    next_conf_max_poll_records = Column(Integer, nullable=False)
    next_conf_session_timeout_ms = Column(Integer, nullable=False)
    next_conf_heartbeat_interval_ms = Column(Integer, nullable=False)

    # Optional loss value from training step
    loss = Column(Float, nullable=True)
