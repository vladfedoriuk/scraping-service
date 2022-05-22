from enum import Enum
from functools import lru_cache

from pydantic import BaseSettings


class Environment(Enum):
    DEV = "development"
    PROD = "production"


class Settings(BaseSettings):
    telegram_bot_token: str
    channel_name: str
    environment: str = Environment.DEV
    testing: bool = False

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
