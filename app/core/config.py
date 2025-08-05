import os

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database Configuration - Unified source of truth
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://mestocker_user:secure_password@localhost:5432/mestocker_dev",
        description="PostgreSQL database URL with asyncpg driver",
    )
    DB_ECHO: bool = Field(
        default=False, description="Enable SQL statement logging for debugging"
    )

    # Additional Database Configuration
    DB_HOST: str = Field(default="localhost", description="Database host")
    DB_PORT: int = Field(default=5432, description="Database port")
    DB_USER: str = Field(default="mestocker_user", description="Database username")
    DB_PASSWORD: str = Field(default="secure_password", description="Database password")
    DB_NAME: str = Field(default="mestocker_dev", description="Database name")

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate DATABASE_URL format and driver compatibility."""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError(
                "DATABASE_URL must use postgresql or postgresql+asyncpg driver"
            )
        return v

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
    SUSPICIOUS_IPS: str = ""  # Se parsea a list en el validator
    ENABLE_IP_BLACKLIST: bool = True

    @field_validator("SUSPICIOUS_IPS", mode="before")
    @classmethod
    def parse_suspicious_ips(cls, v):
        """Parse SUSPICIOUS_IPS from environment variable string."""
        if isinstance(v, str):
            return v  # Mantener como string, el middleware lo parseará
        return ""  # Default string vacío

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

    # Twilio/SMS Configuration - Tarea 1.3.1.5
    TWILIO_ACCOUNT_SID: str = Field(
        default="", description="Twilio Account SID for SMS services"
    )
    TWILIO_AUTH_TOKEN: str = Field(
        default="", description="Twilio Authentication Token"
    )
    TWILIO_FROM_NUMBER: str = Field(
        default="", description="Twilio phone number for sending SMS"
    )
    TWILIO_VERIFY_SERVICE_SID: str = Field(
        default="", description="Twilio Verify Service SID for OTP verification"
    )

    # OTP Configuration - Tarea 1.3.1.5
    OTP_EXPIRATION_MINUTES: int = Field(
        default=5, description="OTP code expiration time in minutes"
    )
    OTP_MAX_ATTEMPTS: int = Field(
        default=3, description="Maximum number of OTP verification attempts"
    )
    SMS_ENABLED: bool = Field(default=True, description="Enable SMS OTP functionality")
    EMAIL_OTP_ENABLED: bool = Field(
        default=True, description="Enable Email OTP functionality"
    )

    # CORS Configuration - Tarea 1.1.4.1
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE")
    CORS_ALLOW_HEADERS: str = os.getenv(
        "CORS_ALLOW_HEADERS",
        "Authorization,Content-Type,Accept,X-Requested-With,Cache-Control,X-API-Key",
    )

    # Email Configuration for SendGrid
    SENDGRID_API_KEY: str = Field(
        default="your_sendgrid_api_key_here",
        description="SendGrid API key for email sending",
    )
    FROM_EMAIL: str = Field(
        default="noreply@mestore.com", description="Default from email address"
    )
    FROM_NAME: str = Field(
        default="MeStore", description="Default from name for emails"
    )

    # Password Reset Configuration
    RESET_TOKEN_EXPIRY_HOURS: int = Field(
        default=1, description="Password reset token expiry time in hours"
    )
    RESET_COOLDOWN_MINUTES: int = Field(
        default=5, description="Cooldown between password reset requests in minutes"
    )
    RESET_MAX_ATTEMPTS: int = Field(
        default=3, description="Maximum password reset attempts before blocking"
    )

    class Config:
        env_file = [".env.test", ".env.production", ".env"]



    # Configuración de uploads
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB por archivo
    MAX_FILES_PER_UPLOAD: int = 10  # Máximo 10 archivos por request
    ALLOWED_IMAGE_TYPES: set = {
        "image/jpeg",
        "image/png", 
        "image/webp",

    }
    ALLOWED_EXTENSIONS: set = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",

    }
    
    # URLs para servir archivos estáticos
    STATIC_URL: str = "/static"
    MEDIA_URL: str = "/media"
    
    # Configuración de thumbnails
    THUMBNAIL_SIZE: tuple = (300, 300)
    THUMBNAIL_QUALITY: int = 85
settings = Settings()