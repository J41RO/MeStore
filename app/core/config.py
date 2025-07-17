from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "postgresql+asyncpg://mestocker_user:secure_password@localhost:5432/mestocker_dev"
    )
    REDIS_URL: str = "redis://:dev-redis-password@localhost:6379/0"
    DEBUG: bool = True
    TESTING: bool = False
    SECRET_KEY: str = "dev-secret-key-change-in-production"

    class Config:
        env_file = ".env"


settings = Settings()