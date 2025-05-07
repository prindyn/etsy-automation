from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ET_SY_API_KEY: str
    REDIS_URL: str
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
