from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str
    ETSY_API_KEY: str
    ETSY_API_BASE: str
    ETSY_WEB_BASE: str
    GUMROAD_API_KEY: str
    GUMROAD_API_BASE: str
    GUMROAD_WEB_BASE: str
    LOG_LEVEL: str = "DEBUG"

    class Config:
        env_file = ".env"


settings = Settings()
