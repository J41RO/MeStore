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

    # Get CORS origins from configuration - use direct CORS_ORIGINS for reliability
    # This ensures all configured origins (including Vercel) are always included
    try:
        # First, get base origins from CORS_ORIGINS setting
        base_origins = [
            origin.strip()
            for origin in settings.CORS_ORIGINS.split(",")
            if origin.strip() and not origin.strip().startswith("https://*")
        ]

        # Add production frontend origins (CRITICAL FIX: www.mestocker.com)
        production_origins = [
            "https://www.mestocker.com",           # Primary production frontend
            "https://me-store-alpha.vercel.app",   # Vercel deployment
            "https://me-store-4rch67v8-jairos-projects-6e49f915.vercel.app",
        ]

        # Add localhost variations for development convenience
        if settings.ENVIRONMENT == "development":
            localhost_origins = [
                "http://localhost:5173",
                "http://localhost:3000",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:3000",
            ]
            # Combine all origins and remove duplicates
            allowed_origins = list(set(base_origins + localhost_origins + production_origins))
        else:
            # Production: combine base_origins with production origins
            allowed_origins = list(set(base_origins + production_origins))

        logger.info(f"✅ Loaded {len(allowed_origins)} CORS origins from config")
    except Exception as e:
        logger.error(f"❌ Failed to parse CORS origins: {e}")
        # Emergency fallback with production origins
        allowed_origins = [
            "https://www.mestocker.com",          # Production frontend (CRITICAL)
            "https://me-store-alpha.vercel.app",  # Vercel deployment
            "http://localhost:5173",               # Development fallback
            "http://localhost:3000",               # Development fallback
        ]

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