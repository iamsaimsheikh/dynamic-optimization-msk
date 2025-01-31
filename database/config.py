import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://saim.sualeh:password1@localhost:5432/kafka_optimization')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
