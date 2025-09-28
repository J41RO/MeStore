"""
Endpoint compatible con frontend existente
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User, UserType
from app.api.v1.deps.auth import require_admin

router = APIRouter()

@router.get("/users/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(require_admin)
) -> Dict[str, Any]:
    """Estadísticas para el dashboard - Compatible con frontend"""
    
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    total_users = len(users)
    total_vendors = len([u for u in users if u.user_type == UserType.VENDOR])
    verified_users = len([u for u in users if u.is_verified])
    
    # Registros últimos 7 días
    week_ago = datetime.now() - timedelta(days=7)
    recent_registrations = len([u for u in users if u.created_at and u.created_at >= week_ago])
    
    return {
        "totalUsers": total_users,
        "totalVendors": total_vendors,
        "totalAdmins": total_users - total_vendors,
        "verifiedUsers": verified_users,
        "pendingVendors": total_vendors - verified_users,
        "recentRegistrations": recent_registrations,
        "activeUsers": len([u for u in users if u.is_active]),
        "inactiveUsers": len([u for u in users if not u.is_active])
    }

@router.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """Lista de usuarios para el frontend"""
    
    result = await db.execute(
        select(User)
        .offset(skip)
        .limit(limit)
        .order_by(User.created_at.desc())
    )
    users = result.scalars().all()
    
    return {
        "users": [
            {
                "id": str(user.id),
                "email": user.email,
                "nombre": user.nombre or "",
                "apellido": user.apellido or "",
                "user_type": user.user_type.value,
                "vendor_status": user.vendor_status,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
            for user in users
        ],
        "total": len(users),
        "skip": skip,
        "limit": limit
    }
