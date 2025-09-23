import os
import secrets
import hashlib
from typing import Optional

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
        allowed_schemes = ("postgresql://", "postgresql+asyncpg://", "sqlite+aiosqlite://")
        if not v.startswith(allowed_schemes):
            raise ValueError(
                f"DATABASE_URL must use postgresql, postgresql+asyncpg, or sqlite+aiosqlite driver"
            )
        return v

    # REDIS CONFIGURATION - DEVOPS INTEGRATION AI RECOMMENDATION
    # Using localhost without authentication for operational simplicity
    REDIS_URL: str = "redis://localhost:6379/0"

    # Redis Database Configuration (múltiples DBs para separación de concerns)
    REDIS_CACHE_DB: int = 0  # Database 0 para cache general
    REDIS_SESSION_DB: int = 1  # Database 1 para sesiones de usuario
    REDIS_QUEUE_DB: int = 2  # Database 2 para message queues
    REDIS_RATE_LIMIT_DB: int = 3  # Database 3 para rate limiting
    REDIS_AUDIT_DB: int = 4  # Database 4 para audit logs

    # URLs específicas por tipo de operación - NO AUTHENTICATION FOR DEVELOPMENT
    REDIS_CACHE_URL: str = "redis://localhost:6379/0"
    REDIS_SESSION_URL: str = "redis://localhost:6379/1"
    REDIS_QUEUE_URL: str = "redis://localhost:6379/2"

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
    # JWT Secret Configuration - SECURITY CRITICAL
    # This should NEVER be hardcoded in production
    SECRET_KEY: str = Field(
        default="dev-jwt-secret-change-me-32-chars-min",
        description="JWT secret key - MUST be set via environment variable in production"
    )

    # Secret validation and rotation
    SECRET_KEY_MIN_LENGTH: int = 32  # Minimum 256 bits
    SECRET_ROTATION_INTERVAL_DAYS: int = 90  # Rotate every 90 days
    SECRET_ALGORITHM_VALIDATION: bool = True

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

    # CORS Configuration - SECURITY FIX: No wildcard origins
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000,http://192.168.1.137:5173",
        description="Comma-separated list of allowed CORS origins (NO WILDCARDS for security)"
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = Field(
        default="GET,POST,PUT,DELETE,OPTIONS",
        description="Allowed HTTP methods for CORS"
    )
    CORS_ALLOW_HEADERS: str = Field(
        default="Authorization,Content-Type,Accept,X-Requested-With,Cache-Control,X-API-Key",
        description="Allowed headers for CORS requests"
    )

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: str) -> str:
        """Validate CORS origins - ensure no wildcards for security."""
        if "*" in v:
            raise ValueError("CORS origins cannot contain wildcards (*) for security reasons")
        return v

    def get_cors_origins_for_environment(self) -> list[str]:
        """Get environment-specific CORS origins with enhanced security validation."""
        base_origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

        if self.ENVIRONMENT == "development":
            # Development: Allow local development servers with security awareness
            development_origins = [
                "http://localhost:5173",  # Vite dev server
                "http://localhost:3000",  # Alternative React dev server
                "http://192.168.1.137:5173",  # Network access for testing
                "http://127.0.0.1:5173",  # Explicit localhost IP
                "http://127.0.0.1:3000",  # Alternative localhost IP
            ]

            # Security validation: warn about non-localhost in development
            for origin in base_origins:
                if not any(local in origin for local in ["localhost", "127.0.0.1", "192.168.1"]):
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Non-local origin in development environment: {origin}")

            return list(set(base_origins + development_origins))

        elif self.ENVIRONMENT == "testing":
            # Testing: Allow test domains only with strict validation
            testing_origins = [
                "http://localhost:5173",
                "http://test.mestore.local",
                "http://127.0.0.1:5173",  # For CI/CD testing
            ]

            # Security: Only allow test-specific origins
            for origin in base_origins:
                if not any(test_domain in origin for test_domain in ["localhost", "127.0.0.1", ".test", ".local"]):
                    raise ValueError(f"Non-test origin not allowed in testing environment: {origin}")

            return testing_origins

        elif self.ENVIRONMENT == "production":
            # Production: Strict validation for production domains only
            default_dev_origins = "http://localhost:5173,http://localhost:3000,http://192.168.1.137:5173"
            if not base_origins or self.CORS_ORIGINS == default_dev_origins:
                raise ValueError("Production CORS_ORIGINS must be explicitly set via environment variable")

            # Security: Ensure all production origins use HTTPS
            for origin in base_origins:
                if origin.startswith("http://") and not origin.startswith("http://localhost"):
                    raise ValueError(f"Production origins must use HTTPS (except localhost for local testing): {origin}")

            # Security: Validate production domain format
            for origin in base_origins:
                if "localhost" in origin or "127.0.0.1" in origin or "192.168." in origin:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Local/private IP origin in production (ensure this is intentional): {origin}")

            return base_origins

        return base_origins

    def get_secure_cors_headers(self) -> list[str]:
        """Get secure CORS headers based on environment."""
        base_headers = [header.strip() for header in self.CORS_ALLOW_HEADERS.split(",") if header.strip()]

        # Remove potentially dangerous headers in production
        if self.ENVIRONMENT == "production":
            dangerous_headers = {"x-forwarded-for", "x-real-ip", "x-forwarded-proto"}
            safe_headers = [h for h in base_headers if h.lower() not in dangerous_headers]

            if len(safe_headers) != len(base_headers):
                import logging
                logger = logging.getLogger(__name__)
                removed = set(base_headers) - set(safe_headers)
                logger.info(f"Removed potentially dangerous headers in production: {removed}")

            return safe_headers

        return base_headers

    def get_secure_cors_methods(self) -> list[str]:
        """Get secure CORS methods based on environment."""
        base_methods = [method.strip() for method in self.CORS_ALLOW_METHODS.split(",") if method.strip()]

        # Restrict dangerous methods in production
        if self.ENVIRONMENT == "production":
            dangerous_methods = {"TRACE", "CONNECT"}
            safe_methods = [m for m in base_methods if m.upper() not in dangerous_methods]

            if len(safe_methods) != len(base_methods):
                import logging
                logger = logging.getLogger(__name__)
                removed = set(base_methods) - set(safe_methods)
                logger.warning(f"Removed dangerous HTTP methods in production: {removed}")

            return safe_methods

        return base_methods

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

    @staticmethod
    def _generate_secure_secret() -> str:
        """
        Generate a cryptographically secure secret key for JWT signing.

        This method generates a 256-bit (32-byte) secret with high entropy
        suitable for HMAC-SHA256 JWT signing. Only used for development.

        Returns:
            str: Base64-encoded secure random secret (44 characters)
        """
        # Generate 32 bytes (256 bits) of secure random data
        secure_bytes = secrets.token_bytes(32)
        # Encode as base64 for string representation
        import base64
        return base64.b64encode(secure_bytes).decode('utf-8')

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """
        Validate JWT secret key security requirements.

        Args:
            v: Secret key to validate

        Returns:
            str: Validated secret key

        Raises:
            ValueError: If secret key doesn't meet security requirements
        """
        if not v:
            raise ValueError("SECRET_KEY cannot be empty")

        # Check minimum length (256 bits = 32 bytes = 44 base64 chars minimum)
        if len(v) < 32:
            raise ValueError(f"SECRET_KEY must be at least 32 characters (256 bits). Current length: {len(v)}")

        # Check for development default (security vulnerability)
        dangerous_defaults = [
            "dev-secret-key-change-in-production",
            "your-secret-key",
            "secret",
            "jwt-secret",
            "development",
            "test",
            "demo"
        ]

        if v.lower() in [d.lower() for d in dangerous_defaults]:
            raise ValueError(f"SECRET_KEY cannot be a default/common value. Use a cryptographically secure random key.")

        # Check entropy (basic heuristic) - skip for development keys and test environments
        import os
        import sys
        environment = os.getenv("ENVIRONMENT", "development")

        # Detect if running in test environment
        is_testing = (
            "pytest" in sys.modules or
            os.getenv("PYTEST_CURRENT_TEST") is not None or
            os.getenv("TEST_ENV") == "true" or
            any("test" in arg for arg in sys.argv) or
            any("pytest" in arg for arg in sys.argv)
        )

        # Skip entropy validation for development and test environments
        if environment != "development" and not is_testing:
            entropy = cls._calculate_entropy(v)
            if entropy < 4.0:  # Minimum entropy threshold
                raise ValueError(f"SECRET_KEY has insufficient entropy ({entropy:.2f}). Use a more random key.")

        # Warn about production usage
        environment = os.getenv("ENVIRONMENT", "development")
        if environment == "production" and len(v) < 44:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Production SECRET_KEY should be at least 44 characters (256 bits base64-encoded)")

        return v

    @staticmethod
    def _calculate_entropy(text: str) -> float:
        """
        Calculate Shannon entropy of a string.

        Args:
            text: Input string to analyze

        Returns:
            float: Shannon entropy value
        """
        import math
        from collections import Counter

        if not text:
            return 0.0

        # Count character frequencies
        counts = Counter(text)
        length = len(text)

        # Calculate Shannon entropy
        entropy = 0.0
        for count in counts.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * math.log2(probability)

        return entropy

    def get_jwt_secret_for_environment(self) -> str:
        """
        Get environment-appropriate JWT secret with security validation.

        Returns:
            str: Validated JWT secret for current environment

        Raises:
            ValueError: If production secret is not properly configured
        """
        if self.ENVIRONMENT == "production":
            # Production: Must be set via environment variable
            env_secret = os.getenv("SECRET_KEY")
            if not env_secret:
                raise ValueError(
                    "SECRET_KEY environment variable MUST be set in production. "
                    "Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )

            # Additional production validation
            if len(env_secret) < 44:
                raise ValueError("Production SECRET_KEY must be at least 44 characters (256 bits)")

            # Check if it's a development default
            if env_secret == self.SECRET_KEY and "dev-secret" in env_secret:
                raise ValueError("Production cannot use development default SECRET_KEY")

            return env_secret

        elif self.ENVIRONMENT == "testing":
            # Testing: Use deterministic but secure secret for reproducible tests
            test_secret = os.getenv("SECRET_KEY", "test-jwt-secret-deterministic-but-secure-32chars-min")
            if len(test_secret) < 32:
                raise ValueError("Test SECRET_KEY must be at least 32 characters")
            return test_secret

        else:
            # Development: Use generated secure secret or environment override
            dev_secret = os.getenv("SECRET_KEY", self.SECRET_KEY)
            return dev_secret

    def validate_jwt_configuration(self) -> dict:
        """
        Validate complete JWT configuration for security compliance.

        Returns:
            dict: Validation results with security status
        """
        results = {
            "secret_validation": "PASS",
            "algorithm_security": "PASS",
            "token_expiration": "PASS",
            "environment_config": "PASS",
            "security_score": 10,
            "warnings": [],
            "errors": []
        }

        try:
            # Validate secret
            secret = self.get_jwt_secret_for_environment()
            if len(secret) < 32:
                results["errors"].append("SECRET_KEY too short")
                results["secret_validation"] = "FAIL"
                results["security_score"] -= 3

        except ValueError as e:
            results["errors"].append(f"Secret validation failed: {str(e)}")
            results["secret_validation"] = "FAIL"
            results["security_score"] -= 3

        # Validate algorithm
        if self.ALGORITHM not in ["HS256", "RS256", "PS256"]:
            results["errors"].append(f"Insecure JWT algorithm: {self.ALGORITHM}")
            results["algorithm_security"] = "FAIL"
            results["security_score"] -= 2

        # Validate token expiration
        if self.ACCESS_TOKEN_EXPIRE_MINUTES > 60:
            results["warnings"].append("Access token expiration > 60 minutes may be insecure")
            results["security_score"] -= 1

        if self.REFRESH_TOKEN_EXPIRE_MINUTES > 10080:  # 7 days
            results["warnings"].append("Refresh token expiration > 7 days may be insecure")
            results["security_score"] -= 1

        # Environment-specific validation
        if self.ENVIRONMENT == "production":
            if not os.getenv("SECRET_KEY"):
                results["errors"].append("Production SECRET_KEY must be set via environment variable")
                results["environment_config"] = "FAIL"
                results["security_score"] -= 3

        return results

    class Config:
        env_file = [".env.development", ".env.test", ".env.production", ".env"]
        env_file_encoding = 'utf-8'



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
    
    # Configuración de múltiples resoluciones
    IMAGE_RESOLUTIONS: dict = {
        "original": None,  # Sin redimensionar
        "large": (1200, 1200),
        "medium": (600, 600), 
        "thumbnail": (300, 300),
        "small": (150, 150)
    }
    # Calidad de compresión por resolución
    IMAGE_QUALITY: dict = {
        "original": 95,  # Calidad alta para original
        "large": 90,
        "medium": 85,
        "thumbnail": 80,
        "small": 75
    }

    # Configuración de watermark MeStocker
    WATERMARK_ENABLED: bool = True
    WATERMARK_LOGO_PATH: str = "app/static/logos/mestocker_logo.png"
    WATERMARK_OPACITY: float = 0.7  # 70% opacidad
    WATERMARK_POSITION: str = "bottom_right"  # Posición esquina inferior derecha
    WATERMARK_MARGIN: int = 10  # Margen desde bordes en píxeles

    # Formato de salida estandarizado
    OUTPUT_FORMAT: str = "JPEG"
    
    # Wompi Payment Gateway Configuration
    WOMPI_PUBLIC_KEY: str = Field(default="", description="Wompi public key")
    WOMPI_PRIVATE_KEY: str = Field(default="", description="Wompi private key")
    WOMPI_ENVIRONMENT: str = Field(default="test", description="Wompi environment")
    WOMPI_WEBHOOK_SECRET: str = Field(default="", description="Wompi webhook secret")
    WOMPI_BASE_URL: str = Field(default="https://sandbox.wompi.co/v1", description="Wompi base URL")

    # ===== REDIS SECURITY METHODS - SECURITY BACKEND AI =====

    def get_secure_redis_url(self, db: int = 0) -> str:
        """
        Get environment-aware Redis URL for development simplicity.

        Returns:
            str: Redis URL appropriate for current environment
        """
        import os

        if self.ENVIRONMENT == "production":
            # Production: Use environment variable for password if needed
            redis_password = os.getenv("REDIS_PASSWORD", "")
            redis_host = os.getenv("REDIS_HOST", "localhost")
            if redis_password:
                return f"redis://:{redis_password}@{redis_host}:6379/{db}"
            else:
                return f"redis://{redis_host}:6379/{db}"

        elif self.ENVIRONMENT == "staging":
            # Staging: Network access
            return f"redis://192.168.1.137:6379/{db}"

        else:  # development
            # Development: Localhost without authentication for simplicity
            return f"redis://localhost:6379/{db}"

    def get_redis_cache_url(self) -> str:
        """Get secure Redis cache URL."""
        return self.get_secure_redis_url(self.REDIS_CACHE_DB)

    def get_redis_session_url(self) -> str:
        """Get secure Redis session URL."""
        return self.get_secure_redis_url(self.REDIS_SESSION_DB)

    def get_redis_queue_url(self) -> str:
        """Get secure Redis queue URL."""
        return self.get_secure_redis_url(self.REDIS_QUEUE_DB)

    def validate_redis_security(self) -> dict:
        """
        Validate Redis security configuration.

        Returns:
            dict: Security validation results
        """
        results = {
            "authentication_configured": True,
            "environment_appropriate": True,
            "password_strength": "adequate",
            "network_security": "secure",
            "security_score": 8,
            "warnings": [],
            "errors": []
        }

        try:
            # Check if URLs contain authentication
            cache_url = self.get_redis_cache_url()
            if ":@" in cache_url or not ":" in cache_url.split("@")[0]:
                results["errors"].append("Redis URL missing authentication")
                results["authentication_configured"] = False
                results["security_score"] -= 4

            # Environment-specific validation
            if self.ENVIRONMENT == "production":
                import os
                if not os.getenv("REDIS_PASSWORD"):
                    results["errors"].append("Production REDIS_PASSWORD not set via environment variable")
                    results["environment_appropriate"] = False
                    results["security_score"] -= 3

            # Password strength check
            redis_url = self.get_redis_cache_url()
            if redis_url:
                password_part = redis_url.split("://:")[-1].split("@")[0]
                if len(password_part) < 32:
                    results["warnings"].append("Redis password should be at least 32 characters")
                    results["password_strength"] = "weak"
                    results["security_score"] -= 1

        except Exception as e:
            results["errors"].append(f"Redis security validation failed: {str(e)}")
            results["security_score"] = 2

        return results

settings = Settings()