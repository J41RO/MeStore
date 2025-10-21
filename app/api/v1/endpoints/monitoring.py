"""
Monitoring Endpoints - System Statistics and Health Monitoring

This module provides comprehensive monitoring endpoints for tracking:
- User statistics (total users, vendors, buyers, admins, active users)
- Authentication statistics (login attempts, tokens, OAuth callbacks)
- API statistics (request counts, error rates, response times)
- Redis statistics (keys, memory usage, blacklist entries)

Created by: backend-framework-ai
Date: 2025-10-13
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User, UserType
from app.schemas.response_base import StandardResponse
from app.utils.response_utils import ResponseUtils

router = APIRouter(tags=["monitoring"])


def _extract_response_data(response: Any) -> Dict[str, Any]:
    """
    Safely extract the data payload from a JSONResponse produced by ResponseUtils.
    Falls back to an empty dict if the structure is unexpected.
    """
    if response is None:
        return {}

    body = getattr(response, "body", None)
    if body is None:
        return {}

    try:
        if isinstance(body, bytes):
            payload = json.loads(body.decode("utf-8"))
        elif isinstance(body, str):
            payload = json.loads(body)
        elif isinstance(body, dict):
            payload = body
        else:
            return {}

        if isinstance(payload, dict):
            return payload.get("data", {})
    except Exception:
        return {}

    return {}


@router.get("/users/stats", response_model=StandardResponse)
async def get_user_statistics(
    db: AsyncSession = Depends(get_db)
) -> StandardResponse:
    """
    Get comprehensive user statistics.

    Returns:
        - total_users: Total number of users in the system
        - total_vendors: Number of vendor users
        - total_buyers: Number of buyer/customer users
        - total_admins: Number of admin users (all types)
        - active_today: Users who logged in within last 24 hours
        - recent_users: Users created in the last 7 days
        - verified_users: Users with verified email
        - unverified_users: Users without verified email
    """
    try:
        # Calculate date thresholds
        today = datetime.utcnow()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)

        # Total users count
        total_result = await db.execute(
            select(func.count(User.id))
        )
        total_users = total_result.scalar() or 0

        # Count by user type
        vendors_result = await db.execute(
            select(func.count(User.id)).where(User.user_type == UserType.VENDOR)
        )
        total_vendors = vendors_result.scalar() or 0

        buyers_result = await db.execute(
            select(func.count(User.id)).where(
                or_(User.user_type == UserType.BUYER, User.user_type == UserType.CUSTOMER)
            )
        )
        total_buyers = buyers_result.scalar() or 0

        # Admin users (all admin types)
        admins_result = await db.execute(
            select(func.count(User.id)).where(
                or_(
                    User.user_type == UserType.ADMIN,
                    User.user_type == UserType.ADMIN_MARKETING,
                    User.user_type == UserType.ADMIN_LOGISTICS,
                    User.user_type == UserType.ADMIN_SUPPORT,
                    User.user_type == UserType.ADMIN_SALES,
                    User.user_type == UserType.SUPERUSER,
                    User.user_type == UserType.OWNER
                )
            )
        )
        total_admins = admins_result.scalar() or 0

        # Active users today (logged in within last 24 hours)
        active_today_result = await db.execute(
            select(func.count(User.id)).where(
                and_(
                    User.last_login.isnot(None),
                    User.last_login >= yesterday
                )
            )
        )
        active_today = active_today_result.scalar() or 0

        # Recent users (created in last 7 days)
        recent_users_result = await db.execute(
            select(func.count(User.id)).where(
                and_(
                    User.created_at.isnot(None),
                    User.created_at >= week_ago
                )
            )
        )
        recent_users = recent_users_result.scalar() or 0

        # Verified users
        verified_result = await db.execute(
            select(func.count(User.id)).where(User.email_verified == True)
        )
        verified_users = verified_result.scalar() or 0

        # Unverified users
        unverified_users = total_users - verified_users

        # Active users percentage
        active_percentage = (active_today / total_users * 100) if total_users > 0 else 0

        stats = {
            "total_users": total_users,
            "total_vendors": total_vendors,
            "total_buyers": total_buyers,
            "total_admins": total_admins,
            "active_today": active_today,
            "active_percentage": round(active_percentage, 2),
            "recent_users": recent_users,
            "verified_users": verified_users,
            "unverified_users": unverified_users,
            "verification_rate": round((verified_users / total_users * 100) if total_users > 0 else 0, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

        return ResponseUtils.success(
            data=stats,
            message="User statistics retrieved successfully"
        )

    except Exception as e:
        # Handle errors gracefully - return zeros if database unavailable
        return ResponseUtils.success(
            data={
                "total_users": 0,
                "total_vendors": 0,
                "total_buyers": 0,
                "total_admins": 0,
                "active_today": 0,
                "active_percentage": 0.0,
                "recent_users": 0,
                "verified_users": 0,
                "unverified_users": 0,
                "verification_rate": 0.0,
                "timestamp": datetime.utcnow().isoformat(),
                "error": f"Data unavailable: {str(e)}"
            },
            message="User statistics retrieved with partial data"
        )


@router.get("/auth/stats", response_model=StandardResponse)
async def get_auth_statistics(
    db: AsyncSession = Depends(get_db)
) -> StandardResponse:
    """
    Get authentication statistics.

    Note: This endpoint returns mock values with TODO comments as the authentication
    logging tables don't exist yet. Future implementation will track:
    - Login attempts (successful/failed)
    - Active JWT tokens
    - OAuth callbacks
    - Password reset requests

    Returns mock data until logging tables are implemented.
    """
    try:
        # TODO: Implement when auth logging tables are created
        # For now, return mock data with clear indication

        stats = {
            "login_attempts_24h": 0,  # TODO: Implement with auth_logs table
            "successful_logins_24h": 0,  # TODO: Implement with auth_logs table
            "failed_logins_24h": 0,  # TODO: Implement with auth_logs table
            "active_tokens": 0,  # TODO: Implement with token tracking
            "oauth_callbacks_24h": 0,  # TODO: Implement with oauth_logs table
            "password_resets_24h": 0,  # TODO: Implement with password_reset_logs table
            "locked_accounts": 0,  # Can be calculated from User model
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Auth statistics require logging tables - returning mock data"
        }

        # Calculate locked accounts from User model
        locked_result = await db.execute(
            select(func.count(User.id)).where(
                and_(
                    User.account_locked_until.isnot(None),
                    User.account_locked_until > datetime.utcnow()
                )
            )
        )
        stats["locked_accounts"] = locked_result.scalar() or 0

        return ResponseUtils.success(
            data=stats,
            message="Auth statistics retrieved (mock data - logging tables not implemented)"
        )

    except Exception as e:
        return ResponseUtils.success(
            data={
                "login_attempts_24h": 0,
                "successful_logins_24h": 0,
                "failed_logins_24h": 0,
                "active_tokens": 0,
                "oauth_callbacks_24h": 0,
                "password_resets_24h": 0,
                "locked_accounts": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "error": f"Data unavailable: {str(e)}"
            },
            message="Auth statistics retrieved with errors"
        )


@router.get("/api/stats", response_model=StandardResponse)
async def get_api_statistics() -> StandardResponse:
    """
    Get API request statistics.

    Note: This endpoint returns mock values with TODO comments as the API request
    logging infrastructure doesn't exist yet. Future implementation will track:
    - Total requests per endpoint
    - Error rates by status code
    - Average response times
    - Rate limit violations

    Returns mock data until request logging is implemented.
    """
    try:
        # TODO: Implement when request logging middleware is created
        # For now, return mock data with clear indication

        stats = {
            "total_requests_24h": 0,  # TODO: Implement with request logging middleware
            "successful_requests_24h": 0,  # TODO: Implement with request logging
            "error_requests_24h": 0,  # TODO: Implement with request logging
            "average_response_time_ms": 0.0,  # TODO: Implement with performance tracking
            "rate_limit_violations_24h": 0,  # TODO: Implement with rate limit logging
            "slowest_endpoint": None,  # TODO: Implement with performance tracking
            "most_used_endpoint": None,  # TODO: Implement with request logging
            "error_rate_percentage": 0.0,  # TODO: Calculate from logs
            "timestamp": datetime.utcnow().isoformat(),
            "note": "API statistics require logging infrastructure - returning mock data"
        }

        return ResponseUtils.success(
            data=stats,
            message="API statistics retrieved (mock data - logging infrastructure not implemented)"
        )

    except Exception as e:
        return ResponseUtils.success(
            data={
                "total_requests_24h": 0,
                "successful_requests_24h": 0,
                "error_requests_24h": 0,
                "average_response_time_ms": 0.0,
                "rate_limit_violations_24h": 0,
                "slowest_endpoint": None,
                "most_used_endpoint": None,
                "error_rate_percentage": 0.0,
                "timestamp": datetime.utcnow().isoformat(),
                "error": f"Data unavailable: {str(e)}"
            },
            message="API statistics retrieved with errors"
        )


@router.get("/redis/stats", response_model=StandardResponse)
async def get_redis_statistics() -> StandardResponse:
    """
    Get Redis cache statistics.

    Attempts to connect to Redis and retrieve:
    - Total keys count
    - Memory usage
    - Blacklist entries
    - Cache hit rate (if available)

    Returns zeros if Redis is unavailable (graceful degradation).
    """
    try:
        # Try to import Redis - optional dependency
        try:
            from app.core.redis import get_redis
            import redis.asyncio as aioredis
        except ImportError:
            return ResponseUtils.success(
                data={
                    "redis_available": False,
                    "total_keys": 0,
                    "memory_used_mb": 0.0,
                    "blacklist_entries": 0,
                    "cache_hit_rate": 0.0,
                    "timestamp": datetime.utcnow().isoformat(),
                    "note": "Redis client not available - install redis package"
                },
                message="Redis statistics unavailable (client not installed)"
            )

        # Try to connect to Redis
        try:
            redis_client = await get_redis()

            # Get Redis info
            info = await redis_client.info()

            # Count total keys across all databases
            total_keys = 0
            for db_num in range(16):  # Redis has 16 databases by default
                try:
                    await redis_client.select(db_num)
                    db_size = await redis_client.dbsize()
                    total_keys += db_size
                except Exception:
                    pass  # Skip if database doesn't exist

            # Reset to default database
            await redis_client.select(0)

            # Get memory usage (convert bytes to MB)
            memory_used_bytes = info.get('used_memory', 0)
            memory_used_mb = memory_used_bytes / (1024 * 1024)

            # Count blacklist entries (if pattern exists)
            blacklist_keys = await redis_client.keys("blacklist:*")
            blacklist_entries = len(blacklist_keys)

            # Calculate cache hit rate if stats are available
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total_requests = hits + misses
            cache_hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0.0

            stats = {
                "redis_available": True,
                "total_keys": total_keys,
                "memory_used_mb": round(memory_used_mb, 2),
                "blacklist_entries": blacklist_entries,
                "cache_hit_rate": round(cache_hit_rate, 2),
                "connected_clients": info.get('connected_clients', 0),
                "uptime_seconds": info.get('uptime_in_seconds', 0),
                "timestamp": datetime.utcnow().isoformat()
            }

            return ResponseUtils.success(
                data=stats,
                message="Redis statistics retrieved successfully"
            )

        except Exception as redis_error:
            # Redis connection failed - return zeros gracefully
            return ResponseUtils.success(
                data={
                    "redis_available": False,
                    "total_keys": 0,
                    "memory_used_mb": 0.0,
                    "blacklist_entries": 0,
                    "cache_hit_rate": 0.0,
                    "connected_clients": 0,
                    "uptime_seconds": 0,
                    "timestamp": datetime.utcnow().isoformat(),
                    "note": f"Redis connection failed: {str(redis_error)}"
                },
                message="Redis statistics unavailable (connection failed)"
            )

    except Exception as e:
        return ResponseUtils.success(
            data={
                "redis_available": False,
                "total_keys": 0,
                "memory_used_mb": 0.0,
                "blacklist_entries": 0,
                "cache_hit_rate": 0.0,
                "timestamp": datetime.utcnow().isoformat(),
                "error": f"Unexpected error: {str(e)}"
            },
            message="Redis statistics retrieved with errors"
        )


@router.get("/system/stats", response_model=StandardResponse)
async def get_system_statistics(
    db: AsyncSession = Depends(get_db)
) -> StandardResponse:
    """
    Get combined system statistics from all monitoring endpoints.

    This is a convenience endpoint that aggregates data from:
    - User statistics
    - Auth statistics
    - API statistics
    - Redis statistics

    Returns a comprehensive system health overview.
    """
    try:
        # Call individual stat endpoints to aggregate data
        user_stats_response = await get_user_statistics(db=db)
        auth_stats_response = await get_auth_statistics(db=db)
        api_stats_response = await get_api_statistics()
        redis_stats_response = await get_redis_statistics()

        # Aggregate all statistics using safe extraction helpers
        system_stats = {
            "users": _extract_response_data(user_stats_response),
            "auth": _extract_response_data(auth_stats_response),
            "api": _extract_response_data(api_stats_response),
            "redis": _extract_response_data(redis_stats_response),
            "timestamp": datetime.utcnow().isoformat()
        }

        return ResponseUtils.success(
            data=system_stats,
            message="System statistics retrieved successfully"
        )

    except Exception as e:
        return ResponseUtils.error(
            error_code="SYSTEM_STATS_ERROR",
            message=f"Error retrieving system statistics: {str(e)}",
            status_code=500
        )
