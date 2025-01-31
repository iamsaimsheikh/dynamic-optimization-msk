from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def init_db():
    from models.checkpoint_model import CheckpointModel
    Base.metadata.create_all(bind=engine)
        
