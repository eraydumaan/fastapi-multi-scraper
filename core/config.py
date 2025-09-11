from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "scraping_db"   # <-- ENV ile aynı isim

    SECRET_KEY: str = "super_secret_key_123"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True   # ENV key isimleri büyük/küçük duyarlı olsun

settings = Settings()
