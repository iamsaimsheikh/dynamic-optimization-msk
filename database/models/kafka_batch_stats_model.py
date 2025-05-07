from sqlalchemy import Column, Integer, Float, String, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import UUID
from database.db import Base
import uuid
from datetime import datetime

class KafkaBatchStatsModel(Base):
    __tablename__ = "kafka_batch_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_size = Column(Integer, nullable=True)
    average_latency_ms = Column(Float, nullable=True)
    average_throughput_mps = Column(Float, nullable=True)

    conf_linger_ms = Column(Float, nullable=True)
    conf_max_request_size = Column(Float, nullable=True)
    conf_acks = Column(Float, nullable=True)
    conf_batch_size = Column(Float, nullable=True)

    # Consumer Configurations
    conf_fetch_max_bytes = Column(Integer, nullable=True)
    conf_max_poll_records = Column(Integer, nullable=True)
    conf_session_timeout_ms = Column(Integer, nullable=True)
    conf_heartbeat_interval_ms = Column(Integer, nullable=True)

    total_messages = Column(Integer, nullable=True)
    total_cost_usd = Column(Float, nullable=True)
    cost_per_message_usd = Column(Float, nullable=True)
    msk_uptime_cost_usd = Column(Float, nullable=True)
    is_rl_processed = Column(Boolean, nullable=False, default=False)
    avg_cpu_usage = Column(Float, nullable=False)
    avg_ram_usage = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
