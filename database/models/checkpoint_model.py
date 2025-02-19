from sqlalchemy import Column, Integer, DateTime
from database.db import Base

class CheckpointModel(Base):
    __tablename__ = "checkpoint"
    
    id = Column(Integer, primary_key=True, index=True)
    last_checkpoint_timestamp = Column(DateTime)
