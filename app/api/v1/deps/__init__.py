
"""
FastAPI dependencies for API v1.

This module exports all dependency functions used across API endpoints,
providing a centralized import location for authentication, database,
and other cross-cutting concerns.
"""

from .auth import get_current_user, get_current_active_user
from .database import get_db, get_db_session

__all__ = [
    # Authentication dependencies
    "get_current_user",
    "get_current_active_user",
    # Database dependencies
    "get_db", 
    "get_db_session",
]