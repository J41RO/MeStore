# ~/app/utils/database.py
# ---------------------------------------------------------------------------------------------
# MeStore - Database Utilities para queries comunes
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: database.py
# Ruta: ~/app/utils/database.py
# Autor: Jairo
# Fecha de Creación: 2025-07-23
# Última Actualización: 2025-07-23
# Versión: 1.0.0
# Propósito: Utilities genéricas para operaciones CRUD comunes con soporte AsyncSession
#            Incluye get_by_id, soft_delete, hard_delete y operaciones con filtros
#
# ---------------------------------------------------------------------------------------------

"""
Database Utilities - Operaciones CRUD genéricas reutilizables

Proporciona:
- get_by_id(): Obtener registro por UUID con soporte async
- soft_delete(): Marcar registro como eliminado (deleted_at)
- hard_delete(): Eliminación física del registro
- get_active(): Filtrar solo registros no eliminados
- exists(): Verificar existencia de registro
- count_active(): Contar registros activos
"""

import uuid
from datetime import datetime
from typing import Optional, Type, TypeVar, List, Dict, Any

from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.models.base import BaseModel

# Type variable para generic typing
ModelType = TypeVar('ModelType', bound=BaseModel)


class DatabaseUtils:
    """Utilities genéricas para operaciones de base de datos"""

    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        model: Type[ModelType],
        record_id: uuid.UUID,
        include_deleted: bool = False
    ) -> Optional[ModelType]:
        """
        Obtener registro por ID con soporte para soft delete.

        Args:
            session: Sesión async de SQLAlchemy
            model: Clase del modelo a consultar
            record_id: UUID del registro a buscar
            include_deleted: Si incluir registros soft deleted

        Returns:
            Instancia del modelo o None si no existe
        """
        query = select(model).where(model.id == record_id)

        if not include_deleted:
            query = query.where(model.deleted_at.is_(None))

        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def soft_delete(
        session: AsyncSession,
        model: Type[ModelType],
        record_id: uuid.UUID
    ) -> bool:
        """
        Realizar soft delete de un registro.

        Args:
            session: Sesión async de SQLAlchemy
            model: Clase del modelo
            record_id: UUID del registro a eliminar

        Returns:
            True si se eliminó, False si no existía
        """
        query = (
            update(model)
            .where(and_(
                model.id == record_id,
                model.deleted_at.is_(None)
            ))
            .values(
                deleted_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )

        result = await session.execute(query)
        await session.commit()

        return result.rowcount > 0

    @staticmethod
    async def hard_delete(
        session: AsyncSession,
        model: Type[ModelType],
        record_id: uuid.UUID
    ) -> bool:
        """
        Realizar eliminación física de un registro.

        Args:
            session: Sesión async de SQLAlchemy
            model: Clase del modelo
            record_id: UUID del registro a eliminar

        Returns:
            True si se eliminó, False si no existía
        """
        query = delete(model).where(model.id == record_id)

        result = await session.execute(query)
        await session.commit()

        return result.rowcount > 0

    @staticmethod
    async def get_active(
        session: AsyncSession,
        model: Type[ModelType],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Obtener registros activos (no soft deleted).

        Args:
            session: Sesión async de SQLAlchemy
            model: Clase del modelo
            limit: Límite de registros
            offset: Offset para paginación
            order_by: Campo para ordenar (por defecto created_at desc)

        Returns:
            Lista de registros activos
        """
        query = select(model).where(model.deleted_at.is_(None))

        # Ordenar
        if order_by:
            if hasattr(model, order_by):
                order_field = getattr(model, order_by)
                query = query.order_by(order_field.desc())
        else:
            query = query.order_by(model.created_at.desc())

        # Paginación
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def exists(
        session: AsyncSession,
        model: Type[ModelType],
        record_id: uuid.UUID,
        include_deleted: bool = False
    ) -> bool:
        """
        Verificar si existe un registro por ID.

        Args:
            session: Sesión async de SQLAlchemy
            model: Clase del modelo
            record_id: UUID del registro
            include_deleted: Si incluir registros soft deleted

        Returns:
            True si existe, False si no
        """
        query = select(func.count(model.id)).where(model.id == record_id)

        if not include_deleted:
            query = query.where(model.deleted_at.is_(None))

        result = await session.execute(query)
        count = result.scalar()

        return count > 0

    @staticmethod
    async def count_active(
        session: AsyncSession,
        model: Type[ModelType]
    ) -> int:
        """
        Contar registros activos de un modelo.

        Args:
            session: Sesión async de SQLAlchemy
            model: Clase del modelo

        Returns:
            Número de registros activos
        """
        query = select(func.count(model.id)).where(model.deleted_at.is_(None))

        result = await session.execute(query)
        return result.scalar()

    @staticmethod
    async def restore_soft_deleted(
        session: AsyncSession,
        model: Type[ModelType],
        record_id: uuid.UUID
    ) -> bool:
        """
        Restaurar un registro soft deleted.

        Args:
            session: Sesión async de SQLAlchemy
            model: Clase del modelo
            record_id: UUID del registro a restaurar

        Returns:
            True si se restauró, False si no existía o no estaba eliminado
        """
        query = (
            update(model)
            .where(and_(
                model.id == record_id,
                model.deleted_at.is_not(None)
            ))
            .values(
                deleted_at=None,
                updated_at=datetime.utcnow()
            )
        )

        result = await session.execute(query)
        await session.commit()

        return result.rowcount > 0