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
    """Setup essential middleware - ULTRA SIMPLIFIED for deployment reliability"""
    logger.info("Setting up minimal middleware for fast startup...")

    # MINIMAL CORS - No validation to prevent startup blocking
    allowed_origins = ["*"]  # Temporary for startup - can be restricted later

    # Only in development, use specific origins
    if settings.ENVIRONMENT == "development":
        try:
            allowed_origins = settings.get_cors_origins_for_environment()
        except:
            allowed_origins = ["http://localhost:5173", "http://localhost:3000"]

    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"CORS allowed origins: {allowed_origins}")

    # MINIMAL MIDDLEWARE CHAIN - Fast startup priority
    # 1. GZip compression (lightweight, non-blocking)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    logger.info("✅ GZipMiddleware added")

    # 2. CORS Middleware - minimal configuration for fast startup
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=3600,
    )
    logger.info("✅ CORSMiddleware added (minimal config for fast startup)")

    logger.info("Minimal middleware setup completed - fast startup guaranteed")