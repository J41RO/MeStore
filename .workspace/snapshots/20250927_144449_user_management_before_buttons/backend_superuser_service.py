# ~/app/services/superuser_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Servicio de Administración Superusuario
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: superuser_service.py
# Ruta: ~/app/services/superuser_service.py
# Autor: Backend Framework AI
# Fecha de Creación: 2025-09-26
# Propósito: Servicio de negocio para operaciones avanzadas de administración de usuarios
#            incluye CRUD completo, filtrado avanzado, estadísticas y operaciones bulk
#
# ---------------------------------------------------------------------------------------------

"""
Servicio de Administración Superusuario para MeStore.

Este servicio proporciona operaciones avanzadas de gestión de usuarios:
- CRUD completo de usuarios con validaciones de seguridad
- Filtrado avanzado y paginación optimizada
- Estadísticas y analytics de usuarios
- Operaciones bulk para gestión masiva
- Audit logging para compliance y trazabilidad
- Verificación de dependencias antes de eliminaciones
"""

import uuid
import asyncio
from typing import List, Dict, Optional, Tuple, Any, Union
from datetime import datetime, timedelta, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc, text, delete, update
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.user import User, UserType, VendorStatus
from app.models.product import Product, ProductStatus
from app.models.transaction import Transaction
from app.schemas.superuser_admin import (
    UserFilterParameters,
    UserFilterSortBy,
    UserFilterStatus,
    UserSummary,
    UserDetailedInfo,
    UserListResponse,
    UserCreateRequest,
    UserUpdateRequest,
    UserStatsResponse,
    UserDeleteResponse,
    BulkUserActionRequest,
    BulkUserActionResponse
)
from app.schemas.user import UserRead
from app.services.auth_service import auth_service
from app.core.logging import logger
# from app.core.exceptions import ValidationError, SecurityError
# Using HTTPException instead


class SuperuserService:
    """
    Servicio de administración avanzada de usuarios para superusuarios.

    Proporciona operaciones CRUD completas con validaciones de seguridad,
    filtrado avanzado, estadísticas y audit logging.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # =================================================================
    # OPERACIONES DE LISTADO Y BÚSQUEDA
    # =================================================================

    async def get_users_paginated(
        self,
        filters: UserFilterParameters,
        current_user: UserRead
    ) -> UserListResponse:
        """
        Obtener lista paginada de usuarios con filtros avanzados.

        Args:
            filters: Parámetros de filtrado y paginación
            current_user: Usuario actual (para audit logging)

        Returns:
            UserListResponse: Lista paginada con metadatos

        Raises:
            HTTPException: Si hay errores en los filtros o consulta
        """
        try:
            # Construir query base
            query = select(User)

            # Aplicar filtros de búsqueda
            if filters.search:
                search_term = f"%{filters.search}%"
                search_filter = or_(
                    User.email.ilike(search_term),
                    User.nombre.ilike(search_term),
                    User.apellido.ilike(search_term),
                    User.cedula.ilike(search_term),
                    func.concat(User.nombre, ' ', User.apellido).ilike(search_term)
                )
                query = query.filter(search_filter)

            # Aplicar filtro exacto por email
            if filters.email:
                query = query.filter(User.email == filters.email)

            # Filtros por tipo de usuario
            if filters.user_type:
                query = query.filter(User.user_type == filters.user_type)

            # Filtros por estado
            if filters.status and filters.status != UserFilterStatus.ALL:
                if filters.status == UserFilterStatus.ACTIVE:
                    query = query.filter(User.is_active == True)
                elif filters.status == UserFilterStatus.INACTIVE:
                    query = query.filter(User.is_active == False)
                elif filters.status == UserFilterStatus.VERIFIED:
                    query = query.filter(User.is_verified == True)
                elif filters.status == UserFilterStatus.UNVERIFIED:
                    query = query.filter(User.is_verified == False)
                elif filters.status == UserFilterStatus.EMAIL_VERIFIED:
                    query = query.filter(User.email_verified == True)
                elif filters.status == UserFilterStatus.PHONE_VERIFIED:
                    query = query.filter(User.phone_verified == True)

            # Filtros booleanos explícitos
            if filters.is_active is not None:
                query = query.filter(User.is_active == filters.is_active)
            if filters.is_verified is not None:
                query = query.filter(User.is_verified == filters.is_verified)
            if filters.email_verified is not None:
                query = query.filter(User.email_verified == filters.email_verified)
            if filters.phone_verified is not None:
                query = query.filter(User.phone_verified == filters.phone_verified)

            # Filtros de fecha
            if filters.created_after:
                query = query.filter(User.created_at >= filters.created_after)
            if filters.created_before:
                query = query.filter(User.created_at <= filters.created_before + timedelta(days=1))
            if filters.last_login_after:
                query = query.filter(User.last_login >= filters.last_login_after)
            if filters.last_login_before:
                query = query.filter(User.last_login <= filters.last_login_before + timedelta(days=1))

            # Filtros específicos para vendors
            if filters.vendor_status:
                query = query.filter(User.vendor_status == filters.vendor_status)

            # Filtros administrativos
            if filters.security_clearance_min:
                query = query.filter(User.security_clearance_level >= filters.security_clearance_min)
            if filters.security_clearance_max:
                query = query.filter(User.security_clearance_level <= filters.security_clearance_max)
            if filters.department_id:
                query = query.filter(User.department_id == filters.department_id)

            # Obtener total antes de paginación
            count_query = select(func.count()).select_from(query.subquery())
            total_result = self.db.execute(count_query)
            total = total_result.scalar()

            # Aplicar ordenamiento
            query = self._apply_sorting(query, filters.sort_by)

            # Aplicar paginación
            offset = (filters.page - 1) * filters.size
            query = query.offset(offset).limit(filters.size)

            # Ejecutar query con eager loading para optimizar
            query = query.options(
                selectinload(User.productos_vendidos),
                selectinload(User.transacciones_vendedor)
            )

            result = self.db.execute(query)
            users = result.scalars().all()

            # Convertir a UserSummary con información calculada
            user_summaries = []
            for user in users:
                summary = await self._user_to_summary(user)
                user_summaries.append(summary)

            # Calcular metadatos de paginación
            total_pages = (total + filters.size - 1) // filters.size
            has_next = filters.page < total_pages
            has_previous = filters.page > 1

            # Preparar filtros aplicados para respuesta
            filters_applied = {}
            for field, value in filters.model_dump().items():
                if value is not None and field not in ['page', 'size']:
                    filters_applied[field] = value

            # Calcular estadísticas del resultado
            summary_stats = await self._calculate_result_stats(user_summaries)

            # Log de auditoría
            await self._log_admin_action(
                current_user.id,
                "list_users",
                f"Listed {len(user_summaries)} users with filters: {filters_applied}"
            )

            return UserListResponse(
                users=user_summaries,
                total=total,
                page=filters.page,
                size=filters.size,
                total_pages=total_pages,
                has_next=has_next,
                has_previous=has_previous,
                filters_applied=filters_applied,
                summary_stats=summary_stats
            )

        except Exception as e:
            logger.error(f"Error in get_users_paginated: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error obteniendo lista de usuarios: {str(e)}"
            )

    def _apply_sorting(self, query, sort_by: UserFilterSortBy):
        """Aplicar criterio de ordenamiento a la query."""
        if sort_by == UserFilterSortBy.CREATED_AT_DESC:
            return query.order_by(desc(User.created_at))
        elif sort_by == UserFilterSortBy.CREATED_AT_ASC:
            return query.order_by(asc(User.created_at))
        elif sort_by == UserFilterSortBy.EMAIL_ASC:
            return query.order_by(asc(User.email))
        elif sort_by == UserFilterSortBy.EMAIL_DESC:
            return query.order_by(desc(User.email))
        elif sort_by == UserFilterSortBy.LAST_LOGIN_DESC:
            return query.order_by(desc(User.last_login))
        elif sort_by == UserFilterSortBy.LAST_LOGIN_ASC:
            return query.order_by(asc(User.last_login))
        elif sort_by == UserFilterSortBy.USER_TYPE:
            return query.order_by(asc(User.user_type))
        elif sort_by == UserFilterSortBy.IS_ACTIVE:
            return query.order_by(desc(User.is_active), desc(User.created_at))
        else:
            return query.order_by(desc(User.created_at))

    async def _user_to_summary(self, user: User) -> UserSummary:
        """Convertir User model a UserSummary con datos calculados."""
        return UserSummary(
            id=str(user.id),
            email=user.email,
            nombre=user.nombre,
            apellido=user.apellido,
            full_name=user.full_name,
            user_type=user.user_type,
            is_active=user.is_active,
            is_verified=user.is_verified,
            email_verified=user.email_verified,
            phone_verified=user.phone_verified,
            created_at=user.created_at,
            last_login=user.last_login,
            vendor_status=user.vendor_status if user.user_type == UserType.VENDOR else None,
            business_name=user.business_name if user.user_type == UserType.VENDOR else None,
            security_clearance_level=user.security_clearance_level,
            department_id=user.department_id,
            failed_login_attempts=user.failed_login_attempts,
            account_locked=(user.account_locked_until is not None and
                          user.account_locked_until > datetime.now())
        )

    async def _calculate_result_stats(self, users: List[UserSummary]) -> Dict[str, Union[int, float]]:
        """Calcular estadísticas del resultado de la búsqueda."""
        if not users:
            return {}

        total = len(users)
        active_count = sum(1 for u in users if u.is_active)
        verified_count = sum(1 for u in users if u.is_verified)
        email_verified_count = sum(1 for u in users if u.email_verified)

        # Contar por tipo
        type_counts = {}
        for user_type in UserType:
            type_counts[user_type.value.lower()] = sum(1 for u in users if u.user_type == user_type)

        return {
            "total": total,
            "active_percentage": round((active_count / total) * 100, 2),
            "verified_percentage": round((verified_count / total) * 100, 2),
            "email_verified_percentage": round((email_verified_count / total) * 100, 2),
            **type_counts
        }

    # =================================================================
    # OPERACIONES CRUD DE USUARIOS
    # =================================================================

    async def get_user_by_id(self, user_id: str, current_user: UserRead) -> UserDetailedInfo:
        """
        Obtener información detallada de un usuario específico.

        Args:
            user_id: ID del usuario a obtener
            current_user: Usuario actual (para audit logging)

        Returns:
            UserDetailedInfo: Información completa del usuario

        Raises:
            HTTPException: Si el usuario no existe
        """
        try:
            query = select(User).where(User.id == user_id)
            result = self.db.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )

            # Log de auditoría
            await self._log_admin_action(
                current_user.id,
                "view_user_details",
                f"Viewed details for user {user.email} (ID: {user_id})"
            )

            return UserDetailedInfo(
                id=str(user.id),
                email=user.email,
                nombre=user.nombre,
                apellido=user.apellido,
                full_name=user.full_name,
                user_type=user.user_type,
                is_active=user.is_active,
                is_verified=user.is_verified,
                email_verified=user.email_verified,
                phone_verified=user.phone_verified,
                last_login=user.last_login,
                cedula=user.cedula,
                telefono=user.telefono,
                ciudad=user.ciudad,
                empresa=user.empresa,
                direccion=user.direccion,
                vendor_status=user.vendor_status,
                business_name=user.business_name,
                business_description=user.business_description,
                website_url=user.website_url,
                security_clearance_level=user.security_clearance_level,
                department_id=user.department_id,
                employee_id=user.employee_id,
                performance_score=user.performance_score,
                failed_login_attempts=user.failed_login_attempts,
                account_locked_until=user.account_locked_until,
                force_password_change=user.force_password_change,
                bank_name=user.bank_name,
                account_holder_name=user.account_holder_name,
                account_number=user.account_number,
                created_at=user.created_at,
                updated_at=user.updated_at
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error obteniendo usuario: {str(e)}"
            )

    async def create_user(
        self,
        user_data: UserCreateRequest,
        current_user: UserRead
    ) -> UserDetailedInfo:
        """
        Crear nuevo usuario con validaciones de seguridad.

        Args:
            user_data: Datos del usuario a crear
            current_user: Usuario actual (para audit logging)

        Returns:
            UserDetailedInfo: Usuario creado

        Raises:
            HTTPException: Si hay errores de validación o duplicados
        """
        try:
            # Verificar email único
            existing_user = await self._check_user_exists_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un usuario con este email"
                )

            # Verificar cédula única si se proporciona
            if user_data.cedula:
                existing_cedula = await self._check_user_exists_by_cedula(user_data.cedula)
                if existing_cedula:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Ya existe un usuario con esta cédula"
                    )

            # Generar hash de contraseña
            password_hash = await auth_service.get_password_hash(user_data.password)

            # Crear usuario
            new_user = User(
                id=str(uuid.uuid4()),
                email=user_data.email,
                password_hash=password_hash,
                nombre=user_data.nombre,
                apellido=user_data.apellido,
                user_type=user_data.user_type,
                cedula=user_data.cedula,
                telefono=user_data.telefono,
                ciudad=user_data.ciudad,
                empresa=user_data.empresa,
                direccion=user_data.direccion,
                is_active=user_data.is_active,
                is_verified=user_data.is_verified,
                security_clearance_level=user_data.security_clearance_level,
                created_at=datetime.now()
            )

            # Si es vendor, inicializar status
            if user_data.user_type == UserType.VENDOR:
                new_user.vendor_status = VendorStatus.DRAFT

            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)

            # Log de auditoría
            await self._log_admin_action(
                current_user.id,
                "create_user",
                f"Created user {new_user.email} (ID: {new_user.id}) with type {user_data.user_type.value}",
                {"notes": user_data.notes}
            )

            logger.info(f"User created successfully: {new_user.email} by admin {current_user.email}")

            return await self.get_user_by_id(str(new_user.id), current_user)

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creando usuario: {str(e)}"
            )

    async def update_user(
        self,
        user_id: str,
        update_data: UserUpdateRequest,
        current_user: UserRead
    ) -> UserDetailedInfo:
        """
        Actualizar usuario existente.

        Args:
            user_id: ID del usuario a actualizar
            update_data: Datos de actualización
            current_user: Usuario actual (para audit logging)

        Returns:
            UserDetailedInfo: Usuario actualizado

        Raises:
            HTTPException: Si el usuario no existe o hay errores de validación
        """
        try:
            # Obtener usuario existente
            query = select(User).where(User.id == user_id)
            result = self.db.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )

            # Verificar cédula única si se actualiza
            if update_data.cedula and update_data.cedula != user.cedula:
                existing_cedula = await self._check_user_exists_by_cedula(update_data.cedula)
                if existing_cedula and existing_cedula.id != user.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Ya existe un usuario con esta cédula"
                    )

            # Aplicar actualizaciones
            changes = []
            update_fields = update_data.model_dump(exclude_unset=True)

            for field, value in update_fields.items():
                if field == "admin_notes":
                    continue  # Las notas se manejan en audit log

                old_value = getattr(user, field, None)
                if old_value != value:
                    setattr(user, field, value)
                    changes.append(f"{field}: {old_value} -> {value}")

            user.updated_at = datetime.now()

            await self.db.commit()
            await self.db.refresh(user)

            # Log de auditoría
            await self._log_admin_action(
                current_user.id,
                "update_user",
                f"Updated user {user.email} (ID: {user_id}). Changes: {', '.join(changes)}",
                {"notes": update_data.admin_notes, "changes": changes}
            )

            logger.info(f"User updated successfully: {user.email} by admin {current_user.email}")

            return await self.get_user_by_id(user_id, current_user)

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error actualizando usuario: {str(e)}"
            )

    async def delete_user(
        self,
        user_id: str,
        current_user: UserRead,
        reason: Optional[str] = None
    ) -> UserDeleteResponse:
        """
        Eliminar usuario con verificación de dependencias.

        Args:
            user_id: ID del usuario a eliminar
            current_user: Usuario actual (para audit logging)
            reason: Razón de la eliminación

        Returns:
            UserDeleteResponse: Resultado de la eliminación

        Raises:
            HTTPException: Si hay dependencias o errores
        """
        try:
            # Obtener usuario
            query = select(User).where(User.id == user_id)
            result = self.db.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )

            # Verificar que no se elimine a sí mismo
            if str(user.id) == str(current_user.id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No puedes eliminarte a ti mismo"
                )

            # Verificar dependencias críticas
            dependencies_check = await self._check_user_dependencies(user)

            if dependencies_check["has_critical_dependencies"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No se puede eliminar usuario con dependencias críticas: {', '.join(dependencies_check['critical_reasons'])}"
                )

            # Realizar cleanup de dependencias no críticas
            cleanup_results = await self._cleanup_user_dependencies(user)

            # Eliminar usuario
            await self.db.delete(user)
            await self.db.commit()

            # Log de auditoría
            await self._log_admin_action(
                current_user.id,
                "delete_user",
                f"Deleted user {user.email} (ID: {user_id}). Reason: {reason or 'Not specified'}",
                {
                    "reason": reason,
                    "dependencies_checked": dependencies_check["dependencies_checked"],
                    "cleanup_results": cleanup_results
                }
            )

            logger.warning(f"User deleted: {user.email} by admin {current_user.email}")

            return UserDeleteResponse(
                success=True,
                user_id=user_id,
                email=user.email,
                deleted_at=datetime.now(),
                dependencies_checked=dependencies_check["dependencies_checked"],
                data_cleanup=cleanup_results,
                warnings=dependencies_check.get("warnings", []),
                deleted_by=str(current_user.id),
                reason=reason
            )

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error eliminando usuario: {str(e)}"
            )

    # =================================================================
    # ESTADÍSTICAS Y ANALYTICS
    # =================================================================

    async def get_user_statistics(self, current_user: UserRead) -> UserStatsResponse:
        """
        Obtener estadísticas completas de usuarios para dashboard.

        Args:
            current_user: Usuario actual (para audit logging)

        Returns:
            UserStatsResponse: Estadísticas completas
        """
        try:
            # Consultas base para estadísticas
            total_users_query = select(func.count(User.id))
            active_users_query = select(func.count(User.id)).filter(User.is_active == True)
            verified_users_query = select(func.count(User.id)).filter(User.is_verified == True)

            # Ejecutar consultas básicas en paralelo
            total_result, active_result, verified_result = await asyncio.gather(
                self.db.execute(total_users_query),
                self.db.execute(active_users_query),
                self.db.execute(verified_users_query)
            )

            total_users = total_result.scalar()
            active_users = active_result.scalar()
            verified_users = verified_result.scalar()

            # Estadísticas por tipo de usuario
            type_stats = {}
            for user_type in UserType:
                type_query = select(func.count(User.id)).filter(User.user_type == user_type)
                type_result = self.db.execute(type_query)
                type_stats[user_type.value.lower()] = type_result.scalar()

            # Estadísticas de verificación
            email_verified_query = select(func.count(User.id)).filter(User.email_verified == True)
            phone_verified_query = select(func.count(User.id)).filter(User.phone_verified == True)
            both_verified_query = select(func.count(User.id)).filter(
                and_(User.email_verified == True, User.phone_verified == True)
            )

            email_verified_result, phone_verified_result, both_verified_result = await asyncio.gather(
                self.db.execute(email_verified_query),
                self.db.execute(phone_verified_query),
                self.db.execute(both_verified_query)
            )

            # Estadísticas temporales
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            day_ago = datetime.now() - timedelta(days=1)

            created_today_query = select(func.count(User.id)).filter(
                func.date(User.created_at) == today
            )
            created_week_query = select(func.count(User.id)).filter(
                User.created_at >= week_ago
            )
            created_month_query = select(func.count(User.id)).filter(
                User.created_at >= month_ago
            )
            recent_logins_query = select(func.count(User.id)).filter(
                User.last_login >= day_ago
            )
            locked_accounts_query = select(func.count(User.id)).filter(
                User.account_locked_until > datetime.now()
            )

            # Ejecutar consultas temporales
            temporal_results = await asyncio.gather(
                self.db.execute(created_today_query),
                self.db.execute(created_week_query),
                self.db.execute(created_month_query),
                self.db.execute(recent_logins_query),
                self.db.execute(locked_accounts_query)
            )

            # Estadísticas específicas de vendors
            vendor_stats = await self._get_vendor_statistics()

            # Log de auditoría
            await self._log_admin_action(
                current_user.id,
                "view_user_statistics",
                "Viewed user statistics dashboard"
            )

            return UserStatsResponse(
                total_users=total_users,
                active_users=active_users,
                inactive_users=total_users - active_users,
                verified_users=verified_users,
                buyers=type_stats.get("buyer", 0),
                vendors=type_stats.get("vendor", 0),
                admins=type_stats.get("admin", 0),
                superusers=type_stats.get("superuser", 0),
                email_verified=email_verified_result.scalar(),
                phone_verified=phone_verified_result.scalar(),
                both_verified=both_verified_result.scalar(),
                created_today=temporal_results[0].scalar(),
                created_this_week=temporal_results[1].scalar(),
                created_this_month=temporal_results[2].scalar(),
                recent_logins=temporal_results[3].scalar(),
                locked_accounts=temporal_results[4].scalar(),
                vendor_stats=vendor_stats,
                calculated_at=datetime.now(),
                period="all_time"
            )

        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error obteniendo estadísticas: {str(e)}"
            )

    async def _get_vendor_statistics(self) -> Dict[str, int]:
        """Obtener estadísticas específicas de vendors."""
        vendor_stats = {}

        # Por status de vendor
        for vendor_status in VendorStatus:
            query = select(func.count(User.id)).filter(
                and_(User.user_type == UserType.VENDOR, User.vendor_status == vendor_status)
            )
            result = self.db.execute(query)
            vendor_stats[f"vendor_{vendor_status.value}"] = result.scalar()

        # Vendors con productos
        vendors_with_products_query = select(func.count(func.distinct(Product.vendedor_id))).filter(
            Product.vendedor_id.is_not(None)
        )
        result = self.db.execute(vendors_with_products_query)
        vendor_stats["vendors_with_products"] = result.scalar()

        return vendor_stats

    # =================================================================
    # OPERACIONES BULK
    # =================================================================

    async def bulk_user_action(
        self,
        action_request: BulkUserActionRequest,
        current_user: UserRead
    ) -> BulkUserActionResponse:
        """
        Ejecutar acción bulk sobre múltiples usuarios.

        Args:
            action_request: Parámetros de la acción bulk
            current_user: Usuario actual (para audit logging)

        Returns:
            BulkUserActionResponse: Resultado de la operación
        """
        successful_users = []
        failed_users = []
        warnings = []

        try:
            # Verificar que los usuarios existen
            users_query = select(User).filter(User.id.in_(action_request.user_ids))
            result = self.db.execute(users_query)
            users = result.scalars().all()

            found_ids = {str(user.id) for user in users}
            missing_ids = set(action_request.user_ids) - found_ids

            for missing_id in missing_ids:
                failed_users.append({
                    "user_id": missing_id,
                    "reason": "Usuario no encontrado"
                })

            # Ejecutar acción en usuarios encontrados
            for user in users:
                try:
                    success = await self._execute_bulk_action(user, action_request.action, action_request.parameters)
                    if success:
                        successful_users.append(str(user.id))
                    else:
                        failed_users.append({
                            "user_id": str(user.id),
                            "reason": "La acción no se pudo aplicar a este usuario"
                        })
                except Exception as e:
                    failed_users.append({
                        "user_id": str(user.id),
                        "reason": str(e)
                    })

            # Commit si hay cambios exitosos
            if successful_users:
                await self.db.commit()

            # Log de auditoría
            await self._log_admin_action(
                current_user.id,
                f"bulk_{action_request.action}",
                f"Bulk action {action_request.action} on {len(action_request.user_ids)} users. {len(successful_users)} successful, {len(failed_users)} failed",
                {
                    "reason": action_request.reason,
                    "successful_count": len(successful_users),
                    "failed_count": len(failed_users)
                }
            )

            return BulkUserActionResponse(
                success=len(successful_users) > 0,
                action=action_request.action,
                total_requested=len(action_request.user_ids),
                successful=len(successful_users),
                failed=len(failed_users),
                successful_users=successful_users,
                failed_users=failed_users,
                warnings=warnings,
                processed_at=datetime.now(),
                processed_by=str(current_user.id)
            )

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error in bulk user action: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en operación bulk: {str(e)}"
            )

    async def _execute_bulk_action(self, user: User, action: str, parameters: Dict[str, Any]) -> bool:
        """Ejecutar acción específica en un usuario."""
        if action == "activate":
            user.is_active = True
        elif action == "deactivate":
            user.is_active = False
        elif action == "verify_email":
            user.email_verified = True
        elif action == "unverify_email":
            user.email_verified = False
        elif action == "reset_failed_attempts":
            user.failed_login_attempts = 0
            user.account_locked_until = None
        elif action == "force_password_change":
            user.force_password_change = True
        elif action == "update_clearance":
            new_level = parameters.get("clearance_level")
            if new_level and 1 <= new_level <= 5:
                user.security_clearance_level = new_level
            else:
                return False
        else:
            return False

        user.updated_at = datetime.now()
        return True

    # =================================================================
    # MÉTODOS AUXILIARES
    # =================================================================

    async def _check_user_exists_by_email(self, email: str) -> Optional[User]:
        """Verificar si existe usuario con email específico."""
        query = select(User).where(User.email == email)
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    async def _check_user_exists_by_cedula(self, cedula: str) -> Optional[User]:
        """Verificar si existe usuario con cédula específica."""
        query = select(User).where(User.cedula == cedula)
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    async def _check_user_dependencies(self, user: User) -> Dict[str, Any]:
        """Verificar dependencias del usuario antes de eliminación."""
        dependencies_checked = []
        critical_reasons = []
        warnings = []
        has_critical_dependencies = False

        # Verificar productos como vendor
        if user.user_type == UserType.VENDOR:
            products_query = select(func.count(Product.id)).filter(Product.vendedor_id == user.id)
            products_result = self.db.execute(products_query)
            products_count = products_result.scalar()

            dependencies_checked.append(f"products: {products_count}")
            if products_count > 0:
                warnings.append(f"Usuario tiene {products_count} productos que serán desactivados")

        # Verificar transacciones como comprador/vendedor
        buyer_transactions_query = select(func.count(Transaction.id)).filter(Transaction.comprador_id == user.id)
        vendor_transactions_query = select(func.count(Transaction.id)).filter(Transaction.vendedor_id == user.id)

        buyer_result, vendor_result = await asyncio.gather(
            self.db.execute(buyer_transactions_query),
            self.db.execute(vendor_transactions_query)
        )

        buyer_transactions = buyer_result.scalar()
        vendor_transactions = vendor_result.scalar()

        dependencies_checked.extend([
            f"buyer_transactions: {buyer_transactions}",
            f"vendor_transactions: {vendor_transactions}"
        ])

        # Las transacciones son críticas - no permitir eliminación si existen
        if buyer_transactions > 0 or vendor_transactions > 0:
            has_critical_dependencies = True
            critical_reasons.append(f"tiene {buyer_transactions + vendor_transactions} transacciones")

        return {
            "has_critical_dependencies": has_critical_dependencies,
            "critical_reasons": critical_reasons,
            "warnings": warnings,
            "dependencies_checked": dependencies_checked
        }

    async def _cleanup_user_dependencies(self, user: User) -> Dict[str, int]:
        """Realizar cleanup de dependencias no críticas."""
        cleanup_results = {}

        # Desactivar productos si es vendor
        if user.user_type == UserType.VENDOR:
            products_update = (
                update(Product)
                .where(Product.vendedor_id == user.id)
                .values(status=ProductStatus.INACTIVE, updated_at=datetime.now())
            )
            result = self.db.execute(products_update)
            cleanup_results["products_deactivated"] = result.rowcount

        return cleanup_results

    async def _log_admin_action(
        self,
        admin_id: str,
        action: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log acción administrativa para auditoría."""
        try:
            # En una implementación completa, esto escribiría a una tabla de audit log
            log_data = {
                "admin_id": admin_id,
                "action": action,
                "description": description,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            logger.info(f"Admin action logged: {log_data}")
        except Exception as e:
            logger.error(f"Error logging admin action: {str(e)}")