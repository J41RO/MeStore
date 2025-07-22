from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "postgresql+asyncpg://mestocker_user:secure_password@localhost:5432/mestocker_dev"
    )
    REDIS_URL: str = "redis://:dev-redis-password@localhost:6379/0"

    # Redis Database Configuration (múltiples DBs para separación de concerns)
    REDIS_CACHE_DB: int = 0  # Database 0 para cache general
    REDIS_SESSION_DB: int = 1  # Database 1 para sesiones de usuario
    REDIS_QUEUE_DB: int = 2  # Database 2 para message queues

    # URLs específicas por tipo de operación
    REDIS_CACHE_URL: str = "redis://:dev-redis-password@localhost:6379/0"
    REDIS_SESSION_URL: str = "redis://:dev-redis-password@localhost:6379/1"
    REDIS_QUEUE_URL: str = "redis://:dev-redis-password@localhost:6379/2"

    # TTL Configuration (Time To Live) - valores por defecto en segundos
    REDIS_CACHE_TTL: int = 3600  # 1 hora para cache general
    REDIS_SESSION_TTL: int = 86400  # 24 horas para sesiones
    REDIS_TEMP_CACHE_TTL: int = 300  # 5 minutos para cache temporal
    REDIS_LONG_CACHE_TTL: int = 604800  # 7 días para cache de larga duración

    # ChromaDB Configuration
    CHROMA_PERSIST_DIR: str = "./data/chroma"

    # Rate Limiting Configuration
    RATE_LIMIT_AUTHENTICATED_PER_MINUTE: int = 100
    RATE_LIMIT_ANONYMOUS_PER_MINUTE: int = 30

    # Suspicious IP Detection Configuration
    SUSPICIOUS_IPS: list = []  # Se carga desde variable de entorno
    ENABLE_IP_BLACKLIST: bool = True

    @field_validator('SUSPICIOUS_IPS', mode='before')
    @classmethod
    def parse_suspicious_ips(cls, v):
        """Parse SUSPICIOUS_IPS from environment variable string to list."""
        if isinstance(v, str):
            if not v.strip():
                return []
            return [ip.strip() for ip in v.split(',') if ip.strip()]
        return v or []

    # Redis Connection Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    DEBUG: bool = True
    ENVIRONMENT: str = "development"  # development, production, testing

    # Logging Configuration - Tarea 0.2.6.5
    LOG_LEVEL: str = "DEBUG"
    LOG_DIR: str = "logs"
    LOG_FILE_PREFIX: str = "mestocker"
    LOG_ROTATION_SIZE: str = "10MB"
    LOG_ROTATION_COUNT: int = 5
    LOG_ROTATION_TIME: str = "midnight"
    LOG_ROTATION_INTERVAL: int = 1
    TESTING: bool = False
    SECRET_KEY: str = "dev-secret-key-change-in-production"

    # JWT Configuration - Tarea 1.1.2.1
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días

    # CORS Configuration - Tarea 1.1.4.1
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://192.168.1.137:5173,https://mestocker.com"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "GET,POST,PUT,DELETE,PATCH,OPTIONS"
    CORS_ALLOW_HEADERS: str = "*"

    class Config:
        env_file = ".env"


settings = Settings()