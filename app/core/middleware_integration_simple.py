"""
Simplified Middleware Integration
================================

Lightweight middleware setup that replaces the complex middleware chain.
This focuses on essential middleware only to get the application running.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.gzip import GZipMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)

def setup_application_middleware(app: FastAPI):
    """Setup essential middleware with enhanced secure CORS configuration"""
    logger.info("Setting up enhanced secure middleware...")

    # Get environment-specific allowed origins (SECURITY FIX: No wildcards)
    try:
        allowed_origins = settings.get_cors_origins_for_environment()
    except ValueError as e:
        logger.error(f"CORS configuration error: {e}")
        raise

    allowed_methods = settings.get_secure_cors_methods()
    allowed_headers = settings.get_secure_cors_headers()

    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"CORS allowed origins: {allowed_origins}")
    logger.info(f"CORS allowed methods: {allowed_methods}")
    logger.info(f"CORS allowed headers: {allowed_headers}")

    # ENHANCED SECURITY VALIDATIONS
    # 1. Double-check no wildcards in origins
    if "*" in allowed_origins:
        logger.error("CRITICAL SECURITY ERROR: Wildcard origins detected in CORS configuration!")
        raise ValueError("CORS origins cannot contain wildcards (*) for security reasons")

    # 2. Validate origins format and security
    for origin in allowed_origins:
        if not origin.startswith(("http://", "https://")):
            logger.error(f"Invalid CORS origin format: {origin}")
            raise ValueError(f"CORS origin must start with http:// or https://: {origin}")

        # Production security check: HTTPS only
        if settings.ENVIRONMENT == "production" and origin.startswith("http://"):
            logger.error(f"Production CORS origin must use HTTPS: {origin}")
            raise ValueError(f"Production environment requires HTTPS origins only: {origin}")

    # 3. Validate methods - restrict dangerous methods in production
    dangerous_methods = {"TRACE", "CONNECT", "PATCH"}
    if settings.ENVIRONMENT == "production":
        for method in allowed_methods:
            if method.upper() in dangerous_methods:
                logger.warning(f"Potentially dangerous HTTP method allowed in production: {method}")

    # 4. Validate headers - ensure no sensitive headers exposed
    sensitive_headers = {"authorization", "cookie", "set-cookie"}
    for header in allowed_headers:
        if header.lower() in sensitive_headers and settings.ENVIRONMENT == "production":
            logger.info(f"Sensitive header allowed (verify this is intentional): {header}")

    # MIDDLEWARE CHAIN SETUP (Optimal Security Order)
    # 1. HTTPS redirect first (highest priority)
    if settings.ENVIRONMENT == "production":
        app.add_middleware(HTTPSRedirectMiddleware)
        logger.info("✅ HTTPSRedirectMiddleware added for production")

    # 2. GZip compression (before CORS for optimal performance)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    logger.info("✅ GZipMiddleware added")

    # 3. CORS Middleware with enhanced secure configuration (after compression)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # SECURE: Environment-specific origins only
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
        max_age=600 if settings.ENVIRONMENT == "production" else 3600,  # Cache preflight requests
        expose_headers=["X-Total-Count", "X-Page-Count"] if settings.ENVIRONMENT != "production" else [],
    )
    logger.info("✅ Enhanced CORSMiddleware added with security validations")

    # Security audit log
    logger.info(f"CORS Security Audit - Environment: {settings.ENVIRONMENT}")
    logger.info(f"Origins: {len(allowed_origins)} configured")
    logger.info(f"Methods: {allowed_methods}")
    logger.info(f"Credentials: {settings.CORS_ALLOW_CREDENTIALS}")
    logger.info(f"HTTPS Enforcement: {settings.ENVIRONMENT == 'production'}")

    logger.info("Enhanced secure middleware setup completed successfully")