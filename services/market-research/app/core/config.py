from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str
    LOG_LEVEL: str = "INFO"
    ETSY_API_KEY: str
    ETSY_API_BASE: str
    ETSY_WEB_BASE: str

    class Config:
        env_file = ".env"


settings = Settings()
