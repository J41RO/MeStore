# Ruta: MeStore/app/api/v1/endpoints/auth.py
"""
MINIMAL AUTH STUB FOR DIAGNOSTIC PURPOSES
This file replaces the full auth endpoint to diagnose Render timeout issues.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/test")
async def auth_test():
    """Minimal test endpoint - no dependencies, no services"""
    return {
        "status": "ok",
        "message": "Auth endpoint is responsive",
        "service": "MeStore API - Diagnostic Mode"
    }


@router.get("/ping")
async def auth_ping():
    """Ultra-minimal ping endpoint"""
    return {"pong": True}
