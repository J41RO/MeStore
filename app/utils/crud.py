# ~/app/utils/crud.py
# ---------------------------------------------------------------------------------------------
# MeStore - CRUD Operations Genéricas Reutilizables
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: crud.py
# Ruta: ~/app/utils/crud.py
# Autor: Jairo
# Fecha de Creación: 2025-07-23
# Última Actualización: 2025-07-23
# Versión: 1.0.0
# Propósito: Operaciones CRUD genéricas con paginación, filtrado y soft delete support
#
# ---------------------------------------------------------------------------------------------

"""
CRUD Operations - Operaciones Create, Read, Update, Delete genéricas

Proporciona:
- create_record(): Crear nuevo registro con validación
- update_record(): Actualizar registro existente
- list_records(): Listar con paginación y filtros
- get_record(): Obtener registro por ID con opciones
- delete_record(): Soft delete por defecto
- CRUDBase: Clase base para CRUD específicos de modelo
"""

import uuid
from datetime import datetime
from typing import Optional, Type, TypeVar, List, Dict, Any, Union

from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.models.base import BaseModel
from app.utils.database import DatabaseUtils

# Type variables para typing genérico
ModelType = TypeVar('ModelType', bound=BaseModel)
CreateSchemaType = TypeVar('CreateSchemaType')
UpdateSchemaType = TypeVar('UpdateSchemaType')


class CRUDOperations:
    """Operaciones CRUD genéricas para cualquier modelo"""

    @staticmethod
    async def create_record(
        session: AsyncSession,
        model: Type[ModelType],
        data: Dict[str, Any]
    ) -> ModelType:
        """
        Crear nuevo registro.

        Args:
            session: Sesión async de SQLAlchemy
            model: Clase del modelo
            data: Diccionario con datos para crear

        Returns:
            Instancia del modelo creado
        """
        # Filtrar datos válidos para el modelo
        valid_fields = {
            key: value for key, value in data.items()
            if hasattr(model, key) and key not in ['id', 'created_at', 'updated_at']
        }

        # Crear instancia
        instance = model(**valid_fields)

        # Guardar en DB
        session.add(instance)
        await session.commit()
        await session.refresh(instance)

        return instance

    @staticmethod
    async def update_record(
        session: AsyncSession,
        model: Type[ModelType],
        record_id: uuid.UUID,
        data: Dict[str, Any],
        exclude_deleted: bool = True
    ) -> Optional[ModelType]:
        """
        Actualizar registro existente.

        Args:
            session: Sesión async de SQLAlchemy
            model: Clase del modelo
            record_id: UUID del registro a actualizar
            data: Diccionario con datos a actualizar
            exclude_deleted: Excluir registros soft deleted

        Returns:
            Instancia actualizada o None si no existe
        """
        # Obtener registro actual
        instance = await DatabaseUtils.get_by_id(
            session, model, record_id, include_deleted=not exclude_deleted
        )

        if not instance:
            return None

        # Filtrar datos válidos para actualización
        valid_fields = {
            key: value for key, value in data.items()
            if hasattr(model, key) and 
            key not in ['id', 'created_at', 'deleted_at'] and
            value is not None
        }

        # Aplicar cambios
        for field, value in valid_fields.items():
            setattr(instance, field, value)

        # Actualizar timestamp
        instance.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(instance)

        return instance

    @staticmethod
    async def list_records(
        session: AsyncSession,
        model: Type[ModelType],
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        search_fields: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        include_deleted: bool = False
    ) -> Dict[str, Any]:
        """
        Listar registros con paginación y filtros.

        Args:
            session: Sesión async de SQLAlchemy
            model: Clase del modelo
            skip: Offset para paginación
            limit: Límite de registros
            filters: Filtros exactos por campo
            search: Término de búsqueda
            search_fields: Campos donde buscar (por defecto ['name', 'email'])
            order_by: Campo para ordenar
            include_deleted: Incluir registros soft deleted

        Returns:
            Dict con items, total, skip, limit
        """
        # Query base
        query = select(model)

        # Filtro de soft delete
        if not include_deleted:
            query = query.where(model.deleted_at.is_(None))

        # Aplicar filtros exactos
        if filters:
            for field, value in filters.items():
                if hasattr(model, field) and value is not None:
                    field_attr = getattr(model, field)
                    query = query.where(field_attr == value)

        # Aplicar búsqueda de texto
        if search and search_fields:
            search_conditions = []
            search_term = f"%{search}%"

            for field_name in search_fields:
                if hasattr(model, field_name):
                    field_attr = getattr(model, field_name)
                    # Solo aplicar ILIKE a campos String
                    if hasattr(field_attr.type, 'length'):  # Es un String field
                        search_conditions.append(field_attr.ilike(search_term))

            if search_conditions:
                query = query.where(or_(*search_conditions))

        # Contar total antes de paginación
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar()

        # Aplicar ordenamiento
        if order_by and hasattr(model, order_by):
            order_field = getattr(model, order_by)
            query = query.order_by(order_field.desc())
        else:
            query = query.order_by(model.created_at.desc())

        # Aplicar paginación
        query = query.offset(skip).limit(limit)

        # Ejecutar query
        result = await session.execute(query)
        items = result.scalars().all()

        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_next": skip + limit < total,
            "has_prev": skip > 0
        }

    @staticmethod
    async def get_record(
        session: AsyncSession,
        model: Type[ModelType],
        record_id: uuid.UUID,
        include_deleted: bool = False
    ) -> Optional[ModelType]:
        """
        Obtener registro por ID (wrapper de DatabaseUtils.get_by_id).

        Args:
            session: Sesión async de SQLAlchemy
            model: Clase del modelo
            record_id: UUID del registro
            include_deleted: Incluir registros soft deleted

        Returns:
            Instancia del modelo o None
        """
        return await DatabaseUtils.get_by_id(
            session, model, record_id, include_deleted
        )

    @staticmethod
    async def delete_record(
        session: AsyncSession,
        model: Type[ModelType],
        record_id: uuid.UUID,
        hard_delete: bool = False
    ) -> bool:
        """
        Eliminar registro (soft delete por defecto).

        Args:
            session: Sesión async de SQLAlchemy
            model: Clase del modelo
            record_id: UUID del registro
            hard_delete: True para eliminación física

        Returns:
            True si se eliminó, False si no existía
        """
        if hard_delete:
            return await DatabaseUtils.hard_delete(session, model, record_id)
        else:
            return await DatabaseUtils.soft_delete(session, model, record_id)


class CRUDBase:
    """
    Clase base para CRUD específicos de modelo.

    Proporciona operaciones CRUD type-safe para un modelo específico.
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(
        self, 
        session: AsyncSession, 
        data: Dict[str, Any]
    ) -> ModelType:
        """Crear registro del modelo específico"""
        return await CRUDOperations.create_record(session, self.model, data)

    async def get(
        self, 
        session: AsyncSession, 
        record_id: uuid.UUID,
        include_deleted: bool = False
    ) -> Optional[ModelType]:
        """Obtener registro por ID"""
        return await CRUDOperations.get_record(
            session, self.model, record_id, include_deleted
        )

    async def update(
        self, 
        session: AsyncSession, 
        record_id: uuid.UUID, 
        data: Dict[str, Any]
    ) -> Optional[ModelType]:
        """Actualizar registro"""
        return await CRUDOperations.update_record(
            session, self.model, record_id, data
        )

    async def delete(
        self, 
        session: AsyncSession, 
        record_id: uuid.UUID,
        hard_delete: bool = False
    ) -> bool:
        """Eliminar registro"""
        return await CRUDOperations.delete_record(
            session, self.model, record_id, hard_delete
        )

    async def list(
        self, 
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        **kwargs
    ) -> Dict[str, Any]:
        """Listar registros con opciones"""
        return await CRUDOperations.list_records(
            session, self.model, skip=skip, limit=limit, **kwargs
        )