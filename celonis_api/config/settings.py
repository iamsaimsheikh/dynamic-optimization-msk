from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

# Get absolute path of the .env file
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Adjust to your root
ENV_PATH = BASE_DIR / "celonis.env"

class Settings(BaseSettings):
    CELO_API_KEY: str
    CELO_BASE_URL: str
    DATA_PUSH_API_KEY: str
    DATA_POOL_ID: str  # Added Pool ID

    class Config:
        env_file = str(ENV_PATH)  # Convert Path object to string

@lru_cache
def get_settings():
    return Settings()
