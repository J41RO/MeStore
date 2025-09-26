"""
Admin User Management Endpoints
Funcionalidades para que los admins gestionen usuarios del sistema
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.api.v1.deps.auth import get_current_user
from app.database import get_async_db as get_db
from app.models.user import User, UserType
from app.schemas.user import UserRead
from app.schemas.admin_users import (
    AdminUserListResponse,
    AdminUserDetail,
    AdminUserUpdate,
    AdminUserStats,
    UserResetRequest
)
from app.services.admin_permission_service import admin_permission_service, PermissionDeniedError
from app.core.logging import audit_logger

router = APIRouter()

@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_type: Optional[UserType] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None
):
    """
    Lista todos los usuarios con filtros y paginación
    Requiere permisos de admin
    """
    # Verificar permisos de admin
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden acceder a la gestión de usuarios"
        )

    try:
        # Construir query base (simplified - no complex joins)
        query = select(User)

        # Aplicar filtros
        filters = []

        if user_type:
            filters.append(User.user_type == user_type)

        if is_active is not None:
            filters.append(User.is_active == is_active)

        if is_verified is not None:
            filters.append(User.is_verified == is_verified)

        if search:
            search_filter = or_(
                User.email.ilike(f"%{search}%"),
                User.nombre.ilike(f"%{search}%"),
                User.telefono.ilike(f"%{search}%"),
                User.empresa.ilike(f"%{search}%")
            )
            filters.append(search_filter)

        # Aplicar filtros al query
        if filters:
            query = query.where(*filters)

        # Contar total
        count_query = select(func.count(User.id))
        if filters:
            count_query = count_query.where(*filters)

        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Aplicar paginación y ordenamiento
        query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        users = result.scalars().all()

        # Obtener estadísticas simples
        buyer_count = vendor_count = admin_count = 0
        for user in users:
            if user.user_type == UserType.BUYER:
                buyer_count += 1
            elif user.user_type == UserType.VENDOR:
                vendor_count += 1
            elif user.user_type == UserType.ADMIN:
                admin_count += 1

        stats = AdminUserStats(
            buyer=buyer_count,
            vendor=vendor_count,
            admin=admin_count
        )

        # Convert users to AdminUserDetail manually to avoid from_orm issues
        admin_users = []
        for user in users:
            admin_user = AdminUserDetail(
                id=user.id,
                email=user.email,
                nombre=user.nombre,
                apellido=user.apellido,
                user_type=user.user_type,
                cedula=user.cedula,
                telefono=user.telefono,
                ciudad=user.ciudad,
                empresa=user.empresa,
                direccion=user.direccion,
                is_verified=user.is_verified,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=getattr(user, 'last_login', None),
                total_orders=0,  # We'll calculate this later
                total_spent=0.0,  # We'll calculate this later
            )
            admin_users.append(admin_user)

        return AdminUserListResponse(
            users=admin_users,
            total=total,
            skip=skip,
            limit=limit,
            stats=stats
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users: {str(e)}"
        )

@router.get("/users/{user_id}", response_model=AdminUserDetail)
async def get_user_detail(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
    user_id: UUID
):
    """
    Obtiene detalles completos de un usuario específico
    """
    # Verificar permisos de admin
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden acceder a los detalles de usuario"
        )

    query = select(User).options(
        selectinload(User.transactions)
    ).where(User.id == user_id)

    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    # Log de auditoría
    await audit_logger.log_admin_action(
        user_id=str(current_user.id),
        action="view_user_detail",
        resource_type="user",
        resource_id=str(user_id),
        details={"viewed_user_email": user.email}
    )

    return AdminUserDetail.from_orm(user)

@router.put("/users/{user_id}", response_model=AdminUserDetail)
async def update_user(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
    user_id: UUID,
    user_update: AdminUserUpdate
):
    """
    Actualiza un usuario (solo admins)
    """
    # Verificar permisos de admin
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden modificar usuarios"
        )

    # Buscar usuario
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    # Guardar valores originales para audit log
    original_values = {
        "email": user.email,
        "nombre": user.nombre,
        "user_type": user.user_type.value,
        "is_active": user.is_active,
        "is_verified": user.is_verified
    }

    # Aplicar cambios
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    try:
        await db.commit()
        await db.refresh(user)

        # Log de auditoría
        await audit_logger.log_admin_action(
            user_id=str(current_user.id),
            action="update_user",
            resource_type="user",
            resource_id=str(user_id),
            details={
                "original_values": original_values,
                "updated_values": update_data,
                "target_user_email": user.email
            }
        )

        return AdminUserDetail.from_orm(user)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando usuario: {str(e)}"
        )

@router.delete("/users/{user_id}")
async def delete_user(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
    user_id: UUID,
    permanent: bool = Query(False, description="Si true, elimina permanentemente. Si false, solo desactiva")
):
    """
    Elimina o desactiva un usuario
    """
    # Verificar permisos de admin
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden eliminar usuarios"
        )

    # No permitir auto-eliminación
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminarte a ti mismo"
        )

    # Buscar usuario
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    try:
        if permanent:
            # Eliminación permanente (cuidado con las FK constraints)
            await db.delete(user)
            action = "delete_user_permanent"
            message = f"Usuario {user.email} eliminado permanentemente"
        else:
            # Solo desactivar
            user.is_active = False
            action = "deactivate_user"
            message = f"Usuario {user.email} desactivado"

        await db.commit()

        # Log de auditoría
        await audit_logger.log_admin_action(
            user_id=str(current_user.id),
            action=action,
            resource_type="user",
            resource_id=str(user_id),
            details={
                "target_user_email": user.email,
                "permanent": permanent
            }
        )

        return {"message": message}

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando usuario: {str(e)}"
        )

@router.post("/users/{user_id}/reset")
async def reset_user(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
    user_id: UUID,
    reset_request: UserResetRequest
):
    """
    Resetea un usuario para permitir re-registro con el mismo email
    PERFECTA para tu caso de uso de testing
    """
    # Verificar permisos de admin
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden resetear usuarios"
        )

    # Buscar usuario
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    original_email = user.email

    try:
        # Opción 1: Eliminar completamente (permite re-registro)
        if reset_request.delete_completely:
            await db.delete(user)
            await db.commit()

            message = f"Usuario {original_email} eliminado completamente. Puede registrarse nuevamente."
            action = "reset_user_complete_deletion"

        # Opción 2: Reset parcial (mantener histórico pero liberar email)
        else:
            # Cambiar email para liberar el original
            import time
            user.email = f"{user.email}.deleted.{int(time.time())}"
            user.is_active = False
            user.is_verified = False
            user.deleted_at = func.now()

            await db.commit()

            message = f"Usuario reseteado. Email {original_email} liberado para nuevo registro."
            action = "reset_user_partial"

        # Log de auditoría
        await audit_logger.log_admin_action(
            user_id=str(current_user.id),
            action=action,
            resource_type="user",
            resource_id=str(user_id),
            details={
                "original_email": original_email,
                "reset_type": "complete" if reset_request.delete_completely else "partial",
                "reason": reset_request.reason
            }
        )

        return {
            "message": message,
            "original_email": original_email,
            "can_reregister": True
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reseteando usuario: {str(e)}"
        )

@router.get("/users/stats/summary", response_model=AdminUserStats)
async def get_user_stats(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_user)
):
    """
    Estadísticas rápidas de usuarios
    """
    # Verificar permisos de admin
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden ver estadísticas"
        )

    # Obtener estadísticas
    stats_query = select(
        User.user_type,
        func.count().label('count')
    ).group_by(User.user_type)

    result = await db.execute(stats_query)
    user_stats = {row.user_type.value: row.count for row in result.all()}

    return AdminUserStats(**user_stats)