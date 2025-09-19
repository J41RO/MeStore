# ~/app/models/vendor_audit.py
# ---------------------------------------------------------------------------------------------
# MeStore - Modelo SQLAlchemy VendorAuditLog
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: vendor_audit.py
# Ruta: ~/app/models/vendor_audit.py
# Autor: Jairo
# Fecha de Creación: 2025-09-09
# Última Actualización: 2025-09-09
# Versión: 1.0.0
# Propósito: Modelo SQLAlchemy para auditoría de cambios en vendedores
#            Permite tracking automático de todas las acciones administrativas
#
# Modificaciones:
# 2025-09-09 - Creación inicial del modelo VendorAuditLog
#
# ---------------------------------------------------------------------------------------------
"""
Modelo SQLAlchemy VendorAuditLog para MeStore.
Este módulo contiene el modelo para auditoría de cambios:
- Campos básicos: id, vendor_id, admin_id, action_type, old_values, new_values
- Timestamps automáticos: created_at
- Enum ActionType: APPROVED, REJECTED, SUSPENDED, ACTIVATED, PROFILE_UPDATED
- Sistema de tracking automático de cambios
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, ForeignKey, JSON
from sqlalchemy import Index
# UUID import removed for SQLite compatibility
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING
from enum import Enum as PyEnum
from sqlalchemy import Enum

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


class ActionType(PyEnum):
    """Tipos de acciones que se pueden auditar"""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"
    ACTIVATED = "ACTIVATED"
    PROFILE_UPDATED = "PROFILE_UPDATED"
    NOTE_ADDED = "NOTE_ADDED"
    STATUS_CHANGED = "STATUS_CHANGED"
    BULK_ACTION = "BULK_ACTION"


class VendorAuditLog(BaseModel):
    """
    Modelo para auditoría de cambios en vendedores.
    
    Attributes:
        id: str único del registro (heredado de BaseModel)
        vendor_id: ID del vendedor afectado
        admin_id: ID del administrador que realizó la acción
        action_type: Tipo de acción realizada (enum ActionType)
        old_values: Valores anteriores en formato JSON
        new_values: Valores nuevos en formato JSON
        description: Descripción adicional de la acción
        created_at: Timestamp de creación (heredado de BaseModel)
        
    Relationships:
        vendor: Relación con el usuario vendedor
        admin: Relación con el usuario administrador
        
    Constraints:
        - vendor_id y admin_id son campos obligatorios
        - action_type es obligatorio
        - Índices optimizados para consultas temporales
    """
    
    __tablename__ = 'vendor_audit_logs'
    
    # === CAMPOS PRINCIPALES ===
    vendor_id = Column(
        String(36),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID del vendedor afectado"
    )
    
    admin_id = Column(
        String(36),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID del administrador que realizó la acción"
    )
    
    action_type = Column(
        Enum(ActionType),
        nullable=False,
        index=True,
        comment="Tipo de acción realizada"
    )
    
    old_values = Column(
        JSON,
        nullable=True,
        comment="Valores anteriores en formato JSON"
    )
    
    new_values = Column(
        JSON,
        nullable=True,
        comment="Valores nuevos en formato JSON"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Descripción adicional de la acción"
    )
    
    # === RELATIONSHIPS ===
    vendor = relationship(
        "User",
        foreign_keys=[vendor_id],
        back_populates="audit_logs_received",
        lazy="select"
    )
    
    admin = relationship(
        "User",
        foreign_keys=[admin_id],
        back_populates="audit_logs_created",
        lazy="select"
    )
    
    # === ÍNDICES OPTIMIZADOS ===
    __table_args__ = (
        Index('ix_vendor_audit_vendor_created', 'vendor_id', 'created_at'),
        Index('ix_vendor_audit_admin_created', 'admin_id', 'created_at'),
        Index('ix_vendor_audit_action_created', 'action_type', 'created_at'),
    )
    
    def to_dict(self) -> dict:
        """Convierte el modelo a diccionario para serialización"""
        return {
            'id': str(self.id),
            'vendor_id': str(self.vendor_id),
            'admin_id': str(self.admin_id),
            'action_type': self.action_type.value if self.action_type else None,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'vendor_name': f"{self.vendor.nombre} {self.vendor.apellido}" if self.vendor else None,
            'admin_name': f"{self.admin.nombre} {self.admin.apellido}" if self.admin else None,
        }
    
    @classmethod
    def log_vendor_action(cls, vendor_id: str, admin_id: str, action_type: ActionType, 
                         old_values: dict = None, new_values: dict = None, 
                         description: str = None):
        """
        Método utilitario para crear registros de auditoría.
        
        Args:
            vendor_id: ID del vendedor afectado
            admin_id: ID del administrador que realiza la acción
            action_type: Tipo de acción (enum ActionType)
            old_values: Valores anteriores (opcional)
            new_values: Valores nuevos (opcional)
            description: Descripción adicional (opcional)
            
        Returns:
            VendorAuditLog: Instancia del registro de auditoría creado
        """
        return cls(
            vendor_id=vendor_id,
            admin_id=admin_id,
            action_type=action_type,
            old_values=old_values,
            new_values=new_values,
            description=description
        )
