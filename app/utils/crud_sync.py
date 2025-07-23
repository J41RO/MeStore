"""
CRUD Operations Sync - Versiones síncronas para testing
Wrapper de CRUDOperations para Session síncronas
"""

import uuid
from datetime import datetime
from typing import Optional, Type, TypeVar, List, Dict, Any

from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.orm import Session

from app.models.base import BaseModel

ModelType = TypeVar('ModelType', bound=BaseModel)

class CRUDOperationsSync:
    """Operaciones CRUD síncronas para testing"""
    
    @staticmethod
    def create_record(
        session: Session,
        model: Type[ModelType],
        data: Dict[str, Any]
    ) -> ModelType:
        """Crear nuevo registro - versión sync"""
        valid_fields = {
            key: value for key, value in data.items()
            if hasattr(model, key) and key not in ['id', 'created_at', 'updated_at']
        }
        
        instance = model(**valid_fields)
        session.add(instance)
        session.commit()
        session.refresh(instance)
        
        return instance
    
    @staticmethod
    def update_record(
        session: Session,
        model: Type[ModelType],
        record_id: uuid.UUID,
        data: Dict[str, Any],
        exclude_deleted: bool = True
    ) -> Optional[ModelType]:
        """Actualizar registro - versión sync"""
        query = select(model).where(model.id == record_id)
        if exclude_deleted:
            query = query.where(model.deleted_at.is_(None))
        
        result = session.execute(query)
        instance = result.scalar_one_or_none()
        
        if not instance:
            return None
        
        valid_fields = {
            key: value for key, value in data.items()
            if hasattr(model, key) and 
            key not in ['id', 'created_at', 'deleted_at'] and
            value is not None
        }
        
        for field, value in valid_fields.items():
            setattr(instance, field, value)
        
        instance.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(instance)
        
        return instance
    
    @staticmethod
    def get_record(
        session: Session,
        model: Type[ModelType],
        record_id: uuid.UUID,
        include_deleted: bool = False
    ) -> Optional[ModelType]:
        """Obtener registro por ID - versión sync"""
        query = select(model).where(model.id == record_id)
        if not include_deleted:
            query = query.where(model.deleted_at.is_(None))
        
        result = session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    def soft_delete(
        session: Session,
        model: Type[ModelType],
        record_id: uuid.UUID
    ) -> bool:
        """Soft delete - versión sync"""
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
        
        result = session.execute(query)
        session.commit()
        
        return result.rowcount > 0

class CRUDBaseSync:
    """Clase base para CRUD síncronos específicos de modelo"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def create(self, session: Session, data: Dict[str, Any]) -> ModelType:
        return CRUDOperationsSync.create_record(session, self.model, data)
    
    def get(self, session: Session, record_id: uuid.UUID, include_deleted: bool = False) -> Optional[ModelType]:
        return CRUDOperationsSync.get_record(session, self.model, record_id, include_deleted)
    
    def update(self, session: Session, record_id: uuid.UUID, data: Dict[str, Any]) -> Optional[ModelType]:
        return CRUDOperationsSync.update_record(session, self.model, record_id, data)

# Para compatibilidad con tests
CRUDBase = CRUDBaseSync
