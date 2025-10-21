# 🔧 Backend Implementation Guide

This guide shows how to implement the required monitoring endpoints in your FastAPI backend.

## 📋 Required Endpoints

The monitoring dashboard expects these endpoints to be available:

1. `/health` - Health check
2. `/api/v1/monitoring/users/stats` - User statistics
3. `/api/v1/monitoring/auth/stats` - Authentication statistics
4. `/api/v1/monitoring/api/stats` - API statistics
5. `/api/v1/monitoring/redis/stats` - Redis statistics

## 🚀 Implementation

### Step 1: Create Monitoring Module

Create a new file: `app/api/v1/endpoints/monitoring.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.api.v1.deps.auth import get_db
from app.models.user import User
from datetime import datetime, timedelta
import redis.asyncio as redis
import os

router = APIRouter()

# ==================== USER STATS ====================

@router.get("/users/stats")
async def get_user_stats(db: AsyncSession = Depends(get_db)):
    """Get user statistics including total users, breakdown by type, and recent users."""

    try:
        # Total users count
        total_result = await db.execute(select(func.count(User.id)))
        total_users = total_result.scalar() or 0

        # Count by user type
        vendor_result = await db.execute(
            select(func.count(User.id)).where(User.user_type == 'VENDOR')
        )
        vendors = vendor_result.scalar() or 0

        buyer_result = await db.execute(
            select(func.count(User.id)).where(User.user_type == 'BUYER')
        )
        buyers = buyer_result.scalar() or 0

        admin_result = await db.execute(
            select(func.count(User.id)).where(
                User.user_type.in_(['ADMIN', 'SUPERUSER', 'OWNER'])
            )
        )
        admins = admin_result.scalar() or 0

        # Active users today (created or logged in today)
        today = datetime.utcnow().date()
        active_today_result = await db.execute(
            select(func.count(User.id)).where(
                func.date(User.created_at) == today
            )
        )
        active_today = active_today_result.scalar() or 0

        # Recent users (last 10)
        recent_users_result = await db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .limit(10)
        )
        recent_users_orm = recent_users_result.scalars().all()

        recent_users = [
            {
                "id": user.id,
                "email": user.email,
                "user_type": user.user_type,
                "created_at": user.created_at.isoformat()
            }
            for user in recent_users_orm
        ]

        return {
            "total": total_users,
            "vendors": vendors,
            "buyers": buyers,
            "admins": admins,
            "active_today": active_today,
            "recent_users": recent_users
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user stats: {str(e)}")


# ==================== AUTH STATS ====================

@router.get("/auth/stats")
async def get_auth_stats(db: AsyncSession = Depends(get_db)):
    """Get authentication statistics including login attempts and token counts."""

    try:
        # NOTE: These require logging/tracking tables that may not exist yet
        # For now, returning placeholder values
        # You should implement proper tracking in your auth endpoints

        # Example: Count active sessions from a hypothetical sessions table
        # active_tokens_result = await db.execute(
        #     select(func.count(Session.id)).where(Session.is_active == True)
        # )
        # active_tokens = active_tokens_result.scalar() or 0

        return {
            "login_attempts_success": 0,  # TODO: Implement login tracking
            "login_attempts_failed": 0,    # TODO: Implement login tracking
            "oauth_google_callbacks": 0,   # TODO: Implement OAuth tracking
            "active_tokens": 0,             # TODO: Count active JWT tokens
            "blacklisted_tokens": 0,        # TODO: Count blacklisted tokens from Redis
            "registration_step_1": 0,       # TODO: Count users in step 1
            "registration_step_2": 0,       # TODO: Count users in step 2
            "registration_step_3": 0,       # TODO: Count users in step 3
            "registration_step_4": 0        # TODO: Count completed registrations
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching auth stats: {str(e)}")


# ==================== API STATS ====================

@router.get("/api/stats")
async def get_api_stats():
    """Get API statistics including request counts and response times."""

    try:
        # NOTE: This requires request logging middleware
        # For now, returning placeholder values

        # TODO: Implement middleware to track:
        # - Total requests
        # - Success/failure counts
        # - Response times
        # - Top endpoints

        return {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_4xx": 0,
            "failed_5xx": 0,
            "avg_response_time": 0,
            "top_endpoints": []
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching API stats: {str(e)}")


# ==================== REDIS STATS ====================

@router.get("/redis/stats")
async def get_redis_stats():
    """Get Redis statistics including keys, memory usage, and blacklisted tokens."""

    try:
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            return {
                "total_keys": 0,
                "memory_used": "0 MB",
                "blacklisted_tokens": 0,
                "rate_limit_violations": 0
            }

        # Connect to Redis
        redis_client = redis.from_url(redis_url, decode_responses=True)

        # Get database size
        total_keys = await redis_client.dbsize()

        # Get memory info
        memory_info = await redis_client.info("memory")
        memory_used_bytes = memory_info.get("used_memory", 0)
        memory_used_mb = round(memory_used_bytes / (1024 * 1024), 2)

        # Count blacklisted tokens (assuming they're stored with a prefix)
        blacklisted_pattern = "blacklist:*"
        blacklisted_keys = await redis_client.keys(blacklisted_pattern)
        blacklisted_count = len(blacklisted_keys)

        # Count rate limit violations (if tracked)
        rate_limit_pattern = "rate_limit_violation:*"
        rate_limit_keys = await redis_client.keys(rate_limit_pattern)
        rate_limit_violations = len(rate_limit_keys)

        await redis_client.close()

        return {
            "total_keys": total_keys,
            "memory_used": f"{memory_used_mb} MB",
            "blacklisted_tokens": blacklisted_count,
            "rate_limit_violations": rate_limit_violations
        }

    except Exception as e:
        # Return zeros if Redis is not available
        return {
            "total_keys": 0,
            "memory_used": "0 MB",
            "blacklisted_tokens": 0,
            "rate_limit_violations": 0
        }
```

### Step 2: Register Router

In `app/main.py`, add the monitoring router:

```python
from app.api.v1.endpoints import monitoring

# Add to your API router
app.include_router(
    monitoring.router,
    prefix="/api/v1/monitoring",
    tags=["monitoring"]
)
```

### Step 3: Add Middleware for Request Tracking (Optional)

Create `app/middleware/request_tracking.py`:

```python
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta

class RequestTrackingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(lambda: {
            'count': 0,
            'success': 0,
            'failed_4xx': 0,
            'failed_5xx': 0,
            'total_time': 0
        })
        self.start_time = datetime.utcnow()

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        path = request.url.path

        # Update stats
        self.requests[path]['count'] += 1
        self.requests[path]['total_time'] += process_time

        if 200 <= response.status_code < 300:
            self.requests[path]['success'] += 1
        elif 400 <= response.status_code < 500:
            self.requests[path]['failed_4xx'] += 1
        elif 500 <= response.status_code < 600:
            self.requests[path]['failed_5xx'] += 1

        # Add custom header
        response.headers["X-Process-Time"] = str(process_time)

        return response

    def get_stats(self):
        total_requests = sum(stats['count'] for stats in self.requests.values())
        successful = sum(stats['success'] for stats in self.requests.values())
        failed_4xx = sum(stats['failed_4xx'] for stats in self.requests.values())
        failed_5xx = sum(stats['failed_5xx'] for stats in self.requests.values())
        total_time = sum(stats['total_time'] for stats in self.requests.values())

        avg_response_time = (total_time / total_requests * 1000) if total_requests > 0 else 0

        # Top endpoints
        top_endpoints = sorted(
            [
                {
                    'endpoint': path,
                    'count': stats['count'],
                    'avg_time': (stats['total_time'] / stats['count'] * 1000) if stats['count'] > 0 else 0
                }
                for path, stats in self.requests.items()
            ],
            key=lambda x: x['count'],
            reverse=True
        )[:10]

        return {
            'total_requests': total_requests,
            'successful_requests': successful,
            'failed_4xx': failed_4xx,
            'failed_5xx': failed_5xx,
            'avg_response_time': round(avg_response_time, 2),
            'top_endpoints': top_endpoints
        }
```

Add to `app/main.py`:

```python
from app.middleware.request_tracking import RequestTrackingMiddleware

# Global middleware instance
request_tracker = RequestTrackingMiddleware(app)

# Add middleware
app.add_middleware(RequestTrackingMiddleware)

# Update monitoring endpoint
@router.get("/api/stats")
async def get_api_stats():
    return request_tracker.get_stats()
```

### Step 4: Implement Login Tracking (Optional)

In your auth endpoints, track login attempts:

```python
from datetime import datetime
import redis.asyncio as redis

async def track_login_attempt(email: str, success: bool):
    """Track login attempts in Redis."""
    redis_client = redis.from_url(os.getenv("REDIS_URL"))

    # Increment counters
    today = datetime.utcnow().date().isoformat()
    key = f"login_stats:{today}"

    if success:
        await redis_client.hincrby(key, "success", 1)
    else:
        await redis_client.hincrby(key, "failed", 1)

    # Set expiration (30 days)
    await redis_client.expire(key, 30 * 24 * 60 * 60)

    await redis_client.close()

# In your login endpoint
@router.post("/login")
async def login(credentials: LoginSchema, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, credentials.email, credentials.password)

    if user:
        await track_login_attempt(credentials.email, success=True)
        # ... rest of login logic
    else:
        await track_login_attempt(credentials.email, success=False)
        raise HTTPException(status_code=401, detail="Invalid credentials")
```

## 🔒 Security Considerations

### Protect Monitoring Endpoints

Add authentication to monitoring endpoints:

```python
from app.api.v1.deps.auth import get_current_admin_user

@router.get("/users/stats")
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Require admin
):
    # ... implementation
```

### Rate Limiting

Add rate limiting to monitoring endpoints:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/users/stats")
@limiter.limit("10/minute")
async def get_user_stats(request: Request, db: AsyncSession = Depends(get_db)):
    # ... implementation
```

## 🧪 Testing Endpoints

Test your monitoring endpoints:

```bash
# Health check
curl http://localhost:8000/health

# User stats
curl http://localhost:8000/api/v1/monitoring/users/stats

# Auth stats
curl http://localhost:8000/api/v1/monitoring/auth/stats

# API stats
curl http://localhost:8000/api/v1/monitoring/api/stats

# Redis stats
curl http://localhost:8000/api/v1/monitoring/redis/stats
```

## 📊 Example Response

### User Stats
```json
{
  "total": 150,
  "vendors": 60,
  "buyers": 85,
  "admins": 5,
  "active_today": 25,
  "recent_users": [
    {
      "id": "uuid-here",
      "email": "user@example.com",
      "user_type": "VENDOR",
      "created_at": "2024-01-01T12:00:00"
    }
  ]
}
```

## 🚀 Next Steps

1. Implement the basic monitoring endpoints
2. Add request tracking middleware
3. Implement login attempt tracking
4. Add authentication to monitoring endpoints
5. Test all endpoints
6. Deploy and configure dashboard

---

**Need Help?** Check the main README.md for troubleshooting tips.
