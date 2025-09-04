from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017/"
    DB_NAME: str = "scraping_db"
    SECRET_KEY: str = "bu_bir_sir_degil_ama_degistirilmeli_cunku_guvensiz"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # .env dosyasından okumak için (opsiyonel ama önerilir)
    # model_config = SettingsConfigDict(env_file=".env")

settings = Settings()