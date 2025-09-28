"""
Enterprise User Management System
Gestión completa de usuarios con datos reales
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.user import User, UserType
from app.api.v1.deps.auth import require_admin
from app.schemas.user import UserResponse
from pydantic import BaseModel

router = APIRouter()

class UserManagementStats(BaseModel):
    total_users: int
    total_vendors: int
    total_admins: int
    verified_users: int
    pending_vendors: int
    recent_registrations: int

class UserActionRequest(BaseModel):
    action: str  # "activate", "suspend", "verify", "delete"
    reason: Optional[str] = None

@router.get("/stats", response_model=UserManagementStats)
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(require_admin)
):
    """Estadísticas completas de usuarios del sistema"""
    
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    total_users = len(users)
    total_vendors = len([u for u in users if u.user_type == UserType.VENDOR])
    total_admins = len([u for u in users if u.user_type in [UserType.ADMIN, UserType.SUPERUSER]])
    verified_users = len([u for u in users if u.is_verified])
    pending_vendors = len([u for u in users if u.vendor_status == "DRAFT"])
    
    # Registros últimos 7 días
    from datetime import datetime, timedelta
    week_ago = datetime.now() - timedelta(days=7)
    recent_registrations = len([u for u in users if u.created_at and u.created_at >= week_ago])
    
    return UserManagementStats(
        total_users=total_users,
        total_vendors=total_vendors,
        total_admins=total_admins,
        verified_users=verified_users,
        pending_vendors=pending_vendors,
        recent_registrations=recent_registrations
    )

@router.get("/users")
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(require_admin)
):
    """Lista completa de usuarios con filtros avanzados"""
    
    query = select(User)
    
    # Filtros
    if user_type:
        query = query.where(User.user_type == user_type)
    
    if status == "verified":
        query = query.where(User.is_verified == True)
    elif status == "unverified":
        query = query.where(User.is_verified == False)
    elif status == "active":
        query = query.where(User.is_active == True)
    elif status == "inactive":
        query = query.where(User.is_active == False)
    
    if search:
        query = query.where(
            (User.email.ilike(f"%{search}%")) |
            (User.nombre.ilike(f"%{search}%")) |
            (User.apellido.ilike(f"%{search}%"))
        )
    
    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    # Return simplified user data to avoid schema issues
    user_list = []
    for user in users:
        user_data = {
            "id": str(user.id),
            "email": user.email,
            "nombre": getattr(user, 'nombre', 'Usuario'),
            "apellido": getattr(user, 'apellido', 'Usuario'),
            "user_type": user.user_type.value if user.user_type else "BUYER",
            "vendor_status": getattr(user, 'vendor_status', 'DRAFT'),
            "is_active": getattr(user, 'is_active', True),
            "is_verified": getattr(user, 'is_verified', False),
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "is_superuser": user.user_type.value == "SUPERUSER" if user.user_type else False
        }
        user_list.append(user_data)
    return user_list

@router.put("/users/{user_id}/action")
async def user_action(
    user_id: str,
    action_request: UserActionRequest,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(require_admin)
):
    """Acciones de gestión de usuarios: activar, suspender, verificar, eliminar"""
    
    # Buscar usuario
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # 🛡️ PROTECCIÓN CRÍTICA SUPERUSER - NO MODIFICAR SIN AUTORIZACIÓN EXPRESA
    # Esta protección garantiza que admin@mestocker.com siempre tenga acceso
    # CUALQUIER MODIFICACIÓN DEBE SER APROBADA POR EL USUARIO PRINCIPAL
    if user.user_type == UserType.SUPERUSER and action_request.action == "delete":
        raise HTTPException(status_code=403, detail="No se puede eliminar un SUPERUSER")

    # Protección adicional para suspender SUPERUSER
    if user.user_type == UserType.SUPERUSER and action_request.action == "suspend":
        raise HTTPException(status_code=403, detail="No se puede suspender un SUPERUSER")
    
    # Ejecutar acción
    if action_request.action == "activate":
        user.is_active = True
        user.is_verified = True
        message = f"Usuario {user.email} activado"
    
    elif action_request.action == "suspend":
        user.is_active = False
        message = f"Usuario {user.email} suspendido"
    
    elif action_request.action == "verify":
        user.is_verified = True
        if user.vendor_status == "DRAFT":
            user.vendor_status = "ACTIVE"
        message = f"Usuario {user.email} verificado"
    
    elif action_request.action == "delete":
        # Since deleted_at field doesn't exist, we'll just deactivate the user
        user.is_active = False
        user.is_verified = False
        message = f"Usuario {user.email} desactivado (eliminación lógica)"
    
    else:
        raise HTTPException(status_code=400, detail="Acción no válida")
    
    user.updated_at = datetime.now()
    await db.commit()
    
    return {"message": message, "action": action_request.action, "user_id": user_id}

