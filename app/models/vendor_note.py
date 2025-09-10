# ~/app/models/vendor_note.py
# ---------------------------------------------------------------------------------------------
# MeStore - Modelo SQLAlchemy VendorNote
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: vendor_note.py
# Ruta: ~/app/models/vendor_note.py
# Autor: Jairo
# Fecha de Creación: 2025-09-09
# Última Actualización: 2025-09-09
# Versión: 1.0.0
# Propósito: Modelo SQLAlchemy para notas internas de administradores sobre vendedores
#            Permite tracking de observaciones y comentarios internos
#
# Modificaciones:
# 2025-09-09 - Creación inicial del modelo VendorNote
#
# ---------------------------------------------------------------------------------------------
"""
Modelo SQLAlchemy VendorNote para MeStore.
Este módulo contiene el modelo para notas internas de administradores:
- Campos básicos: id, vendor_id, admin_id, note_text
- Timestamps automáticos: created_at, updated_at
- Relationships: con User (vendor y admin)
- Constraints de seguridad: campos obligatorios
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Text, ForeignKey
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


class VendorNote(BaseModel):
    """
    Modelo para notas internas de administradores sobre vendedores.
    
    Attributes:
        id: UUID único del registro (heredado de BaseModel)
        vendor_id: ID del vendedor sobre el que se hace la nota
        admin_id: ID del administrador que crea la nota
        note_text: Contenido de la nota interna
        created_at: Timestamp de creación (heredado de BaseModel)
        updated_at: Timestamp de última actualización (heredado de BaseModel)
        
    Relationships:
        vendor: Relación con el usuario vendedor
        admin: Relación con el usuario administrador
        
    Constraints:
        - vendor_id y admin_id son campos obligatorios
        - note_text no puede estar vacío
        - Índices optimizados para consultas frecuentes
    """
    
    __tablename__ = 'vendor_notes'
    
    # === CAMPOS PRINCIPALES ===
    vendor_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID del vendedor sobre el que se hace la nota"
    )
    
    admin_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID del administrador que crea la nota"
    )
    
    note_text = Column(
        Text,
        nullable=False,
        comment="Contenido de la nota interna"
    )
    
    # === RELATIONSHIPS ===
    vendor = relationship(
        "User",
        foreign_keys=[vendor_id],
        back_populates="vendor_notes_received",
        lazy="select"
    )
    
    admin = relationship(
        "User",
        foreign_keys=[admin_id],
        back_populates="vendor_notes_created",
        lazy="select"
    )
    
    # === ÍNDICES OPTIMIZADOS ===
    __table_args__ = (
        Index('ix_vendor_notes_vendor_created', 'vendor_id', 'created_at'),
        Index('ix_vendor_notes_admin_created', 'admin_id', 'created_at'),
    )
    
    def to_dict(self) -> dict:
        """Convierte el modelo a diccionario para serialización"""
        return {
            'id': str(self.id),
            'vendor_id': str(self.vendor_id),
            'admin_id': str(self.admin_id),
            'note_text': self.note_text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'vendor_name': f"{self.vendor.nombre} {self.vendor.apellido}" if self.vendor else None,
            'admin_name': f"{self.admin.nombre} {self.admin.apellido}" if self.admin else None,
        }
