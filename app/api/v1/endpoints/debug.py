"""
Debug Endpoints (Development Only)
===================================

Temporary debugging endpoints for development and testing.
These endpoints should be disabled or protected in production.

Author: Claude Code
Date: 2025-10-07
"""

from typing import Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/tables", response_model=Dict[str, Any])
async def list_database_tables(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    List all tables in the database.

    **Development/Debug endpoint only.**

    Returns:
        - total: Total number of tables
        - tables: List of table names
        - details: Column count for each table
    """

    # Security check - only allow in development
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debug endpoints are disabled in production"
        )

    try:
        # Get sync connection for inspection
        # We need to use the sync engine for inspect()
        from sqlalchemy import create_engine

        # Convert async URL to sync
        sync_url = str(settings.DATABASE_URL)
        if "asyncpg" in sync_url:
            sync_url = sync_url.replace("+asyncpg", "")
        if "aiosqlite" in sync_url:
            sync_url = sync_url.replace("+aiosqlite", "")

        # Create temporary sync engine for inspection
        sync_engine = create_engine(sync_url, echo=False)
        inspector = inspect(sync_engine)

        # Get all table names
        table_names = inspector.get_table_names()

        # Get details for each table
        table_details = {}
        for table_name in table_names:
            columns = inspector.get_columns(table_name)
            table_details[table_name] = {
                "column_count": len(columns),
                "columns": [col["name"] for col in columns]
            }

        # Cleanup
        sync_engine.dispose()

        return {
            "total": len(table_names),
            "tables": sorted(table_names),
            "details": table_details,
            "environment": settings.ENVIRONMENT,
            "database_type": "postgresql" if "postgresql" in sync_url else "sqlite"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing tables: {str(e)}"
        )


@router.get("/health", response_model=Dict[str, str])
async def debug_health_check() -> Dict[str, str]:
    """
    Simple health check endpoint for debugging.

    Returns basic system information.
    """
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "database_url_configured": "yes" if settings.DATABASE_URL else "no",
        "app_name": settings.PROJECT_NAME
    }
