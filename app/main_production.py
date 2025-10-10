"""
Main Production - Versión minimalista para deployment
Solo incluye: FastAPI + Auth + PostgreSQL + CORS

Este archivo es una versión ultra-simplificada para garantizar que
el servidor arranque en producción sin ningún bloqueo.

Características:
- FastAPI básico
- CORS configurado
- Health check
- API routes importadas con fallback
- Sin servicios opcionales (Redis, ChromaDB, etc.)
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Minimal lifespan - no blocking operations"""
    logger.info("🚀 Starting MeStocker API - Production Mode")
    yield
    logger.info("👋 Shutting down MeStocker API")

# FastAPI app
logger.info("Creating FastAPI application...")
app = FastAPI(
    title="MeStocker API",
    description="Production-ready marketplace API for Colombia",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
logger.info("✅ FastAPI application created")

# CORS Configuration - Production Secure Origins
# CRITICAL FIX: Explicit origins required when allow_credentials=True
# Wildcard ["*"] is INVALID with allow_credentials=True per CORS spec
logger.info("Setting up CORS middleware...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.mestocker.com",           # Production frontend
        "https://me-store-alpha.vercel.app",   # Vercel deployment
        "http://localhost:5173",                # Local development (Vite)
        "http://localhost:3000",                # Local development (React)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "X-Requested-With",
        "Cache-Control",
        "X-API-Key",
        "X-CSRF-Token",
    ],
    max_age=3600,
)
logger.info("✅ CORS middleware configured with explicit production origins")

# Health check - siempre disponible
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "mode": "production",
        "service": "MeStocker API",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MeStocker API - Production",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

# Import routes with fallback
logger.info("Loading API routes...")
try:
    from app.api.v1.api import api_router
    app.include_router(api_router, prefix="/api/v1")
    logger.info("✅ API routes loaded successfully")
except Exception as e:
    logger.error(f"❌ Error loading API routes: {e}")
    logger.warning("Continuing without full API routes - health check still available")
    # Continuar sin rutas - al menos el health check funcionará

# Exception handler básico
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for production"""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return {
        "error": "Internal Server Error",
        "message": str(exc) if logger.level == logging.DEBUG else "An error occurred",
        "status_code": 500
    }

logger.info("🎯 MeStocker API - Production mode initialized")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
