from sqlalchemy import Column, Integer, String, TIMESTAMP
from database.db import Base

class SysEventLogModel(Base):
    __tablename__ = "sys_event_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP, nullable=False)
    level = Column(String(10), nullable=False)  # Log level (DEBUG, INFO, etc.)
    thread_id = Column(String, nullable=False)
    case_id = Column(String, nullable=False)
    entity_name = Column(String, nullable=False)  # e.g., kafka.conn
    action = Column(String, nullable=False)  # Generalized event description
