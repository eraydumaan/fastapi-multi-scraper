from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Scraping API"
    environment: str = "dev"
    host: str = "0.0.0.0"
    port: int = 8000

    # Mongo
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "scraping_db"

    # Security
    SECRET_KEY: str = "CHANGE_ME"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings:
    return Settings()
