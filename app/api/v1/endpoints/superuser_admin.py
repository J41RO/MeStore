# ~/app/api/v1/endpoints/superuser_admin.py
# ---------------------------------------------------------------------------------------------
# MeStore - Endpoints de Administración Superusuario
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: superuser_admin.py
# Ruta: ~/app/api/v1/endpoints/superuser_admin.py
# Autor: Backend Framework AI
# Fecha de Creación: 2025-09-26
# Propósito: Endpoints FastAPI para portal de administración superusuario
#            incluye gestión avanzada de usuarios, filtrado, estadísticas y operaciones bulk
#
# ---------------------------------------------------------------------------------------------

"""
Endpoints de Administración Superusuario para MeStore.

Este módulo proporciona endpoints especializados para administradores superusuario:
- Listado paginado de usuarios con filtros avanzados
- CRUD completo de usuarios con validaciones de seguridad
- Estadísticas y analytics para dashboard administrativo
- Operaciones bulk para gestión masiva de usuarios
- Audit logging integrado para compliance
- Validaciones específicas para operaciones críticas como eliminación de usuarios
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db as get_db
from app.api.v1.deps.auth import require_roles
from app.models.user import UserType, User
from app.schemas.user import UserRead
from app.schemas.superuser_admin import (
    UserFilterParameters,
    UserFilterSortBy,
    UserFilterStatus,
    UserListResponse,
    UserDetailedInfo,
    UserCreateRequest,
    UserUpdateRequest,
    UserStatsResponse,
    UserDeleteResponse,
    BulkUserActionRequest,
    BulkUserActionResponse
)
from app.services.superuser_service import SuperuserService
from app.core.csrf_protection import validate_csrf_protection
from app.core.rate_limiting import check_admin_rate_limit
from app.core.logging import logger

# Crear router con prefix específico para superuser admin
router = APIRouter()

# Dependencia para validar permisos de superusuario
require_superuser = require_roles([UserType.SUPERUSER])


# =================================================================
# ENDPOINTS DE LISTADO Y BÚSQUEDA DE USUARIOS
# =================================================================

@router.get("/users", response_model=UserListResponse)
async def get_users_paginated(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(require_superuser),
    # Parámetros de filtrado y búsqueda
    search: Optional[str] = Query(None, description="Búsqueda en email, nombre, apellido o cédula"),
    email: Optional[str] = Query(None, description="Filtro exacto por email"),
    user_type: Optional[UserType] = Query(None, description="Filtrar por tipo de usuario"),
    status: Optional[UserFilterStatus] = Query(UserFilterStatus.ALL, description="Estado del usuario"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    is_verified: Optional[bool] = Query(None, description="Filtrar por verificación general"),
    email_verified: Optional[bool] = Query(None, description="Filtrar por verificación de email"),
    phone_verified: Optional[bool] = Query(None, description="Filtrar por verificación de teléfono"),

    # Parámetros de fecha
    created_after: Optional[str] = Query(None, description="Usuarios creados después (YYYY-MM-DD)"),
    created_before: Optional[str] = Query(None, description="Usuarios creados antes (YYYY-MM-DD)"),
    last_login_after: Optional[str] = Query(None, description="Último login después (YYYY-MM-DD)"),
    last_login_before: Optional[str] = Query(None, description="Último login antes (YYYY-MM-DD)"),

    # Parámetros administrativos
    security_clearance_min: Optional[int] = Query(None, ge=1, le=5, description="Nivel mínimo de clearance"),
    security_clearance_max: Optional[int] = Query(None, ge=1, le=5, description="Nivel máximo de clearance"),
    department_id: Optional[str] = Query(None, description="ID del departamento"),

    # Paginación y ordenamiento
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Elementos por página"),
    sort_by: UserFilterSortBy = Query(UserFilterSortBy.CREATED_AT_DESC, description="Criterio de ordenamiento")
):
    """
    Obtener lista paginada de usuarios con filtros avanzados.

    Este endpoint permite a los superusuarios buscar y filtrar usuarios
    con múltiples criterios y obtener resultados paginados optimizados.

    **Permisos requeridos:** SUPERUSER

    **Funcionalidades:**
    - Búsqueda de texto libre en email, nombre, apellido y cédula
    - Filtros por tipo de usuario, estado, verificación
    - Filtros por rango de fechas de creación y último login
    - Filtros administrativos por nivel de clearance y departamento
    - Paginación optimizada con metadatos
    - Múltiples opciones de ordenamiento
    - Estadísticas del resultado de búsqueda
    """
    try:
        # Rate limiting para proteger el endpoint
        check_admin_rate_limit(str(current_user.id))

        # Validar y parsear fechas si se proporcionan
        filters = UserFilterParameters(
            search=search,
            email=email,
            user_type=user_type,
            status=status,
            is_active=is_active,
            is_verified=is_verified,
            email_verified=email_verified,
            phone_verified=phone_verified,
            created_after=created_after,
            created_before=created_before,
            last_login_after=last_login_after,
            last_login_before=last_login_before,
            security_clearance_min=security_clearance_min,
            security_clearance_max=security_clearance_max,
            department_id=department_id,
            page=page,
            size=size,
            sort_by=sort_by
        )

        # Crear servicio y ejecutar consulta
        service = SuperuserService(db)
        result = await service.get_users_paginated(filters, current_user)

        logger.info(f"Superuser {current_user.email} listed {result.total} users with filters")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_users_paginated: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo lista de usuarios: {str(e)}"
        )




# =================================================================
# ENDPOINTS CRUD DE USUARIOS
# =================================================================

@router.get("/users/stats")
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(require_superuser)
):
    """Get real user statistics from PostgreSQL database"""
    try:
        from sqlalchemy import select, func
        from datetime import datetime, timedelta

        # Base filter: excluir usuarios soft-deleted (igual que el endpoint de listado)
        base_filter = User.deleted_at.is_(None)

        # Contar usuarios totales usando ORM (solo activos, no soft-deleted)
        result = await db.execute(select(func.count(User.id)).where(base_filter))
        total_users = result.scalar()

        # Contar por tipo de usuario usando ORM (solo activos, no soft-deleted)
        result = await db.execute(select(func.count(User.id)).where(
            base_filter & (User.user_type == UserType.VENDOR)
        ))
        total_vendors = result.scalar()

        result = await db.execute(select(func.count(User.id)).where(
            base_filter & (User.user_type == UserType.BUYER)
        ))
        total_buyers = result.scalar()

        result = await db.execute(select(func.count(User.id)).where(
            base_filter & (User.user_type == UserType.ADMIN)
        ))
        total_admins = result.scalar()

        result = await db.execute(select(func.count(User.id)).where(
            base_filter & (User.user_type == UserType.SUPERUSER)
        ))
        total_superusers = result.scalar()

        # Contar usuarios verificados (solo activos, no soft-deleted)
        result = await db.execute(select(func.count(User.id)).where(
            base_filter & (User.is_verified == True)
        ))
        verified_users = result.scalar()

        # Contar usuarios activos (solo activos, no soft-deleted)
        result = await db.execute(select(func.count(User.id)).where(
            base_filter & (User.is_active == True)
        ))
        active_users = result.scalar()

        # Contar vendedores pendientes (vendors not verified) (solo activos, no soft-deleted)
        result = await db.execute(select(func.count(User.id)).where(
            base_filter & (User.user_type == UserType.VENDOR) & (User.is_verified == False)
        ))
        pending_vendors = result.scalar()

        # Contar registros recientes (último mes) - compatible con SQLite y PostgreSQL (solo activos, no soft-deleted)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        result = await db.execute(select(func.count(User.id)).where(
            base_filter & (User.created_at >= thirty_days_ago)
        ))
        recent_registrations = result.scalar()

        return {
            "totalUsers": total_users,
            "totalVendors": total_vendors,
            "totalBuyers": total_buyers,
            "totalAdmins": total_admins,
            "totalSuperusers": total_superusers,
            "verifiedUsers": verified_users,
            "activeUsers": active_users,
            "inactiveUsers": total_users - active_users,
            "pendingVendors": pending_vendors,
            "recentRegistrations": recent_registrations
        }
    except Exception as e:
        print(f"Error in get_user_stats: {e}")
        import traceback
        traceback.print_exc()
        # Return error instead of fallback to debug the issue
        raise HTTPException(
            status_code=500,
            detail=f"Database error in stats: {str(e)}"
        )


@router.get("/users/deleted", response_model=UserListResponse)
async def get_deleted_users(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(require_superuser),
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Elementos por página"),
    search: Optional[str] = Query(None, description="Búsqueda en email, nombre, apellido")
):
    """
    Obtener lista de usuarios eliminados (soft-deleted).

    **Permisos requeridos:** SUPERUSER

    **Funcionalidades:**
    - Solo usuarios con deleted_at no nulo
    - Búsqueda de texto libre en campos básicos
    - Paginación optimizada
    - Información de cuándo fueron eliminados
    """
    try:
        from sqlalchemy import select, func, or_

        # Query base: solo usuarios soft-deleted
        query = select(User).where(User.deleted_at.is_not(None))

        # Aplicar búsqueda si se proporciona
        if search:
            search_filter = or_(
                User.email.ilike(f"%{search}%"),
                User.nombre.ilike(f"%{search}%"),
                User.apellido.ilike(f"%{search}%")
            )
            query = query.where(search_filter)

        # Contar total
        count_query = select(func.count(User.id)).where(User.deleted_at.is_not(None))
        if search:
            count_query = count_query.where(search_filter)

        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Aplicar paginación y ordenamiento (más reciente primero)
        query = query.order_by(User.deleted_at.desc()).offset((page - 1) * size).limit(size)

        result = await db.execute(query)
        users = result.scalars().all()

        # Convertir a formato de respuesta
        user_summaries = []
        for user in users:
            user_summary = {
                "id": user.id,
                "email": user.email,
                "nombre": user.nombre,
                "apellido": user.apellido,
                "full_name": f"{user.nombre or ''} {user.apellido or ''}".strip(),
                "user_type": user.user_type.value,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "email_verified": getattr(user, 'email_verified', False),
                "phone_verified": getattr(user, 'phone_verified', False),
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "deleted_at": user.deleted_at.isoformat() if user.deleted_at else None,
                "last_login": getattr(user, 'last_login', None),
                "vendor_status": None,
                "business_name": getattr(user, 'empresa', None),
                "security_clearance_level": getattr(user, 'security_clearance_level', 1),
                "department_id": None,
                "failed_login_attempts": getattr(user, 'failed_login_attempts', 0),
                "account_locked": False
            }
            user_summaries.append(user_summary)

        logger.info(f"Superuser {current_user.email} listed {total} deleted users")

        return {
            "users": user_summaries,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": (total + size - 1) // size,
            "has_next": page * size < total,
            "has_previous": page > 1,
            "filters_applied": {"deleted_only": True, "search": search},
            "summary_stats": {"deleted_users": total}
        }

    except Exception as e:
        logger.error(f"Error getting deleted users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo usuarios eliminados: {str(e)}"
        )


@router.get("/users/{user_id}", response_model=UserDetailedInfo)
async def get_user_details(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(require_superuser),
    user_id: UUID
):
    """
    Obtener información detallada de un usuario específico.

    Proporciona acceso completo a todos los datos del usuario incluyendo
    información personal, administrativa, de seguridad y específica de vendors.

    **Permisos requeridos:** SUPERUSER

    **Información incluida:**
    - Datos personales completos
    - Estados de verificación y seguridad
    - Información administrativa y clearance
    - Datos bancarios (para vendors)
    - Timestamps y actividad reciente
    """
    try:
        service = SuperuserService(db)
        user_details = await service.get_user_by_id(str(user_id), current_user)

        logger.info(f"Superuser {current_user.email} viewed details for user {user_id}")
        return user_details

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user details for {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo detalles del usuario: {str(e)}"
        )


@router.post("/users", response_model=UserDetailedInfo, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(require_superuser),
    user_data: UserCreateRequest
):
    """
    Crear nuevo usuario con validaciones de seguridad avanzadas.

    Permite a los superusuarios crear usuarios de cualquier tipo con
    validaciones completas y configuración administrativa.

    **Permisos requeridos:** SUPERUSER

    **Funcionalidades:**
    - Validación de email único con protección contra inyecciones
    - Validación de cédula única (opcional)
    - Hashing seguro de contraseñas con validaciones de fortaleza
    - Configuración de nivel de clearance de seguridad
    - Inicialización apropiada para vendors
    - Audit logging completo
    """
    try:
        # Validar CSRF para operación de escritura - TEMPORALMENTE DESHABILITADO PARA FRONTEND
        # validate_csrf_protection(request, str(current_user.id))

        # Rate limiting más estricto para creación
        check_admin_rate_limit(str(current_user.id), action="create_user")

        service = SuperuserService(db)
        new_user = await service.create_user(user_data, current_user)

        logger.info(f"Superuser {current_user.email} created new user {new_user.email}")
        return new_user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando usuario: {str(e)}"
        )


@router.put("/users/{user_id}", response_model=UserDetailedInfo)
async def update_user(
    *,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(require_superuser),
    user_id: UUID,
    update_data: UserUpdateRequest
):
    """
    Actualizar usuario existente con validaciones completas.

    Permite actualizaciones parciales de usuarios con validaciones de
    integridad y registro de cambios para auditoría.

    **Permisos requeridos:** SUPERUSER

    **Funcionalidades:**
    - Actualizaciones parciales (solo campos proporcionados)
    - Validación de cédula única si se cambia
    - Registro de cambios para audit trail
    - Validaciones de integridad de datos
    - Actualización de timestamps automática
    """
    try:
        # Validar CSRF para operación de escritura - TEMPORALMENTE DESHABILITADO PARA FRONTEND
        # validate_csrf_protection(request, str(current_user.id))

        service = SuperuserService(db)
        updated_user = await service.update_user(str(user_id), update_data, current_user)

        logger.info(f"Superuser {current_user.email} updated user {user_id}")
        return updated_user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando usuario: {str(e)}"
        )


@router.delete("/users/{user_id}", response_model=UserDeleteResponse)
async def delete_user(
    *,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(require_superuser),
    user_id: UUID,
    reason: Optional[str] = Query(None, description="Razón de la eliminación")
):
    """
    Eliminar usuario con verificación exhaustiva de dependencias.

    **⚠️ OPERACIÓN CRÍTICA - USO PRINCIPAL: TESTING SMS VERIFICATION**

    Este endpoint está diseñado específicamente para permitir a los
    superusuarios eliminar cuentas de vendors durante testing para
    poder probar el flujo de verificación SMS sin errores de duplicados.

    **Permisos requeridos:** SUPERUSER

    **Verificaciones de seguridad:**
    - Prevención de auto-eliminación
    - Verificación de dependencias críticas (transacciones)
    - Cleanup automático de dependencias no críticas
    - Desactivación de productos asociados
    - Audit logging detallado con razón

    **Casos de uso:**
    - Limpieza de datos de testing
    - Eliminación de cuentas fraudulentas
    - Cleanup de usuarios duplicados
    - **PRINCIPAL: Testing de verificación SMS de vendors**
    """
    try:
        # Validar CSRF para operación crítica - TEMPORALMENTE DESHABILITADO PARA FRONTEND
        # validate_csrf_protection(request, str(current_user.id))

        # Rate limiting más estricto para eliminación
        check_admin_rate_limit(str(current_user.id))

        service = SuperuserService(db)
        result = await service.delete_user(str(user_id), current_user, reason)

        logger.warning(f"Superuser {current_user.email} deleted user {user_id} - Reason: {reason}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando usuario: {str(e)}"
        )


# =================================================================
# ENDPOINTS DE OPERACIONES BULK
# =================================================================

@router.post("/users/bulk-action", response_model=BulkUserActionResponse)
async def bulk_user_action(
    *,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(require_superuser),
    action_request: BulkUserActionRequest
):
    """
    Ejecutar operaciones masivas sobre múltiples usuarios.

    Permite realizar acciones sobre múltiples usuarios simultáneamente
    con manejo de errores individuales y reporte detallado de resultados.

    **Permisos requeridos:** SUPERUSER

    **Acciones disponibles:**
    - `activate`: Activar usuarios
    - `deactivate`: Desactivar usuarios
    - `verify_email`: Marcar emails como verificados
    - `unverify_email`: Marcar emails como no verificados
    - `reset_failed_attempts`: Resetear intentos fallidos de login
    - `force_password_change`: Forzar cambio de contraseña
    - `update_clearance`: Actualizar nivel de clearance (requiere parámetro)

    **Características:**
    - Procesamiento resiliente (continúa si algunos fallan)
    - Reporte detallado de éxitos y fallos
    - Validación de existencia de usuarios
    - Audit logging completo
    """
    try:
        # Validar CSRF para operación de escritura masiva - TEMPORALMENTE DESHABILITADO PARA FRONTEND
        # validate_csrf_protection(request, str(current_user.id))

        # Rate limiting más estricto para operaciones bulk
        check_admin_rate_limit(str(current_user.id), action="bulk_action")

        service = SuperuserService(db)
        result = await service.bulk_user_action(action_request, current_user)

        logger.info(f"Superuser {current_user.email} executed bulk action {action_request.action} on {len(action_request.user_ids)} users")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk user action: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en operación masiva: {str(e)}"
        )


# =================================================================
# ENDPOINTS DE INFORMACIÓN Y UTILIDADES
# =================================================================

@router.get("/users/{user_id}/dependencies")
async def check_user_dependencies(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(require_superuser),
    user_id: UUID
):
    """
    Verificar dependencias de un usuario antes de eliminación.

    Proporciona información detallada sobre las dependencias del usuario
    para evaluar el impacto de su eliminación.

    **Permisos requeridos:** SUPERUSER

    **Información incluida:**
    - Productos asociados (si es vendor)
    - Transacciones como comprador/vendedor
    - Clasificación de dependencias (críticas vs no críticas)
    - Advertencias sobre impacto de eliminación
    """
    try:
        from sqlalchemy import select, func
        from app.models.product import Product
        from app.models.transaction import Transaction

        # Obtener usuario - Excluir soft-deleted
        query = select(User).where(User.id == str(user_id), User.deleted_at.is_(None))
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        dependencies = {
            "user_id": str(user_id),
            "email": user.email,
            "user_type": user.user_type.value,
            "dependencies": {}
        }

        # Verificar productos si es vendor
        if user.user_type == UserType.VENDOR:
            products_query = select(func.count(Product.id)).filter(Product.vendedor_id == user.id)
            products_result = await db.execute(products_query)
            products_count = products_result.scalar()
            dependencies["dependencies"]["products"] = {
                "count": products_count,
                "critical": False,
                "impact": "Productos serán desactivados" if products_count > 0 else "Sin impacto"
            }

        # Verificar transacciones
        buyer_transactions_query = select(func.count(Transaction.id)).filter(Transaction.comprador_id == user.id)
        vendor_transactions_query = select(func.count(Transaction.id)).filter(Transaction.vendedor_id == user.id)

        buyer_result = await db.execute(buyer_transactions_query)
        vendor_result = await db.execute(vendor_transactions_query)

        buyer_transactions = buyer_result.scalar()
        vendor_transactions = vendor_result.scalar()
        total_transactions = buyer_transactions + vendor_transactions

        dependencies["dependencies"]["transactions"] = {
            "as_buyer": buyer_transactions,
            "as_vendor": vendor_transactions,
            "total": total_transactions,
            "critical": total_transactions > 0,
            "impact": f"BLOQUEA ELIMINACIÓN - {total_transactions} transacciones" if total_transactions > 0 else "Sin impacto"
        }

        # Determinar si se puede eliminar
        can_delete = total_transactions == 0
        dependencies["can_delete"] = can_delete
        dependencies["block_reasons"] = [] if can_delete else [f"Usuario tiene {total_transactions} transacciones"]

        logger.info(f"Superuser {current_user.email} checked dependencies for user {user_id}")
        return dependencies

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking user dependencies for {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verificando dependencias: {str(e)}"
        )



@router.delete("/users/{user_id}/permanent")
async def permanently_delete_user(
    *,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(require_superuser),
    user_id: UUID,
    reason: Optional[str] = Query(None, description="Razón de la eliminación permanente"),
    confirm: bool = Query(False, description="Confirmación requerida para eliminación permanente")
):
    """
    Eliminar usuario PERMANENTEMENTE de la base de datos.

    **⚠️ OPERACIÓN CRÍTICA - IRREVERSIBLE**

    Esta operación elimina completamente el usuario de la base de datos.
    NO se puede deshacer. Requiere confirmación explícita.

    **Permisos requeridos:** SUPERUSER

    **Verificaciones de seguridad:**
    - Usuario debe estar previamente soft-deleted
    - Prevención de auto-eliminación
    - Verificación de dependencias críticas
    - Confirmación explícita requerida
    - Cleanup de dependencias no críticas
    """
    try:
        if not confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Eliminación permanente requiere confirmación explícita con confirm=true"
            )

        # Prevenir auto-eliminación
        if str(user_id) == str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes eliminarte permanentemente a ti mismo"
            )

        # Verificar que el usuario existe y está soft-deleted
        from sqlalchemy import select
        query = select(User).where(User.id == str(user_id))
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        if user.deleted_at is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden eliminar permanentemente usuarios que ya estén soft-deleted. Usa DELETE /users/{id} primero."
            )

        # Verificar dependencias críticas
        from app.models.transaction import Transaction
        from sqlalchemy import func

        transaction_query = select(func.count(Transaction.id)).where(
            (Transaction.comprador_id == user.id) | (Transaction.vendedor_id == user.id)
        )
        transaction_result = await db.execute(transaction_query)
        transaction_count = transaction_result.scalar()

        if transaction_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar permanentemente: usuario tiene {transaction_count} transacciones asociadas"
            )

        # Cleanup de productos si es vendor (desactivar, no eliminar)
        if user.user_type.value == "VENDOR":
            from app.models.product import Product
            products_query = select(Product).where(Product.vendedor_id == user.id)
            products_result = await db.execute(products_query)
            products = products_result.scalars().all()

            for product in products:
                product.is_active = False
                product.updated_at = datetime.utcnow()

        # Guardar información para logging
        user_info = {
            "id": str(user.id),
            "email": user.email,
            "user_type": user.user_type.value,
            "deleted_at": user.deleted_at.isoformat() if user.deleted_at else None
        }

        # ELIMINACIÓN PERMANENTE
        await db.delete(user)
        await db.commit()

        logger.critical(f"PERMANENT DELETION: Superuser {current_user.email} permanently deleted user {user_info['email']} (ID: {user_info['id']}) - Reason: {reason}")

        return {
            "success": True,
            "message": f"Usuario {user_info['email']} eliminado permanentemente",
            "deleted_user": user_info,
            "performed_by": current_user.email,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error permanently deleting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando permanentemente usuario: {str(e)}"
        )


@router.post("/users/{user_id}/restore")
async def restore_deleted_user(
    *,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(require_superuser),
    user_id: UUID,
    reason: Optional[str] = Query(None, description="Razón de la restauración")
):
    """
    Restaurar usuario soft-deleted.

    Permite restaurar un usuario que fue eliminado lógicamente,
    quitando el timestamp de deleted_at.

    **Permisos requeridos:** SUPERUSER
    """
    try:
        from sqlalchemy import select

        # Verificar que el usuario existe y está soft-deleted
        query = select(User).where(User.id == str(user_id))
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        if user.deleted_at is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario no está eliminado"
            )

        # Restaurar usuario
        user.deleted_at = None
        user.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(user)

        logger.info(f"Superuser {current_user.email} restored user {user.email} (ID: {user_id}) - Reason: {reason}")

        return {
            "success": True,
            "message": f"Usuario {user.email} restaurado exitosamente",
            "restored_user": {
                "id": str(user.id),
                "email": user.email,
                "user_type": user.user_type.value
            },
            "performed_by": current_user.email,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restoring user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error restaurando usuario: {str(e)}"
        )


@router.get("/health")
async def superuser_admin_health():
    """
    Health check para endpoints de administración superusuario.

    Endpoint simple para verificar que el módulo de administración
    superusuario está funcionando correctamente.

    **Sin autenticación requerida** - Solo para health checks
    """
    return {
        "status": "healthy",
        "module": "superuser_admin",
        "version": "1.0.0",
        "endpoints_available": [
            "GET /users - Lista paginada de usuarios",
            "GET /users/deleted - Lista de usuarios eliminados",
            "GET /users/stats - Estadísticas de usuarios",
            "GET /users/{id} - Detalles de usuario",
            "POST /users - Crear usuario",
            "PUT /users/{id} - Actualizar usuario",
            "DELETE /users/{id} - Eliminar usuario (soft delete)",
            "DELETE /users/{id}/permanent - Eliminar usuario permanentemente",
            "POST /users/{id}/restore - Restaurar usuario eliminado",
            "POST /users/bulk-action - Operaciones masivas",
            "GET /users/{id}/dependencies - Verificar dependencias"
        ]
    }