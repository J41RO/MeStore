# ~/app/models/movement_tracker.py
# ---------------------------------------------------------------------------------------------
# MeStore - Modelo de Movement Tracker
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: movement_tracker.py
# Ruta: ~/app/models/movement_tracker.py
# Autor: Jairo
# Fecha de Creación: 2025-09-10
# Última Actualización: 2025-09-10
# Versión: 1.0.0
# Propósito: Modelo MovementTracker para tracking detallado de movimientos con historial completo
#            Incluye auditoría, trazabilidad y analytics
#
# ---------------------------------------------------------------------------------------------

"""
Modelo MovementTracker para tracking detallado de movimientos.

Este módulo contiene:
- Clase MovementTracker: Modelo principal para auditoría de movimientos
- Enum ActionType: Tipos de acciones trackeable
- Campos JSON: Datos antes/después del cambio
- Metadata: IP, user agent, session para auditoría completa
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, Text, JSON
from enum import Enum as PyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from typing import Optional, Dict, Any
from datetime import datetime

from .base import BaseModel


class ActionType(PyEnum):
    """
    Enumeración para tipos de acciones trackeables.
    
    Tipos de acciones:
        CREATE: Creación de nuevo movimiento
        UPDATE: Actualización de movimiento existente
        CANCEL: Cancelación de movimiento
        APPROVE: Aprobación de movimiento pendiente
        REJECT: Rechazo de movimiento pendiente
        BATCH_CREATE: Creación de movimientos en lote
        BATCH_UPDATE: Actualización de movimientos en lote
        SYSTEM_AUTO: Acción automática del sistema
    """
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    CANCEL = "CANCEL"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    BATCH_CREATE = "BATCH_CREATE"
    BATCH_UPDATE = "BATCH_UPDATE"
    SYSTEM_AUTO = "SYSTEM_AUTO"


class MovementTracker(BaseModel):
    """
    Modelo MovementTracker para auditoría detallada de movimientos.
    
    Registra cada acción realizada sobre movimientos con información
    completa para trazabilidad, auditoría y analytics.
    
    Campos principales:
    - movement_id: Referencia al movimiento original
    - user_id/user_name: Usuario que realizó la acción
    - action_type: Tipo de acción realizada
    - previous_data/new_data: Estados antes/después (JSON)
    - Metadata: IP, user agent, session para auditoría
    """
    
    __tablename__ = "movement_tracker"
    
    # Relación con MovimientoStock
    movement_id = Column(
        UUID(as_uuid=True),
        ForeignKey('movimientos_stock.id'),
        nullable=False,
        index=True,
        comment="ID del movimiento trackeado"
    )
    
    # Usuario que realizó la acción
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=False,
        index=True,
        comment="Usuario que realizó la acción"
    )
    
    user_name = Column(
        String(100),
        nullable=False,
        comment="Nombre del usuario (snapshot)"
    )
    
    # Tipo de acción realizada
    action_type = Column(
        String(20),
        nullable=False,
        index=True,
        comment="Tipo de acción realizada"
    )
    
    # Estados antes y después (JSON)
    previous_data = Column(
        JSON,
        nullable=True,
        comment="Estado anterior del movimiento (JSON)"
    )
    
    new_data = Column(
        JSON,
        nullable=False,
        comment="Nuevo estado del movimiento (JSON)"
    )
    
    # Metadata de auditoría
    ip_address = Column(
        String(45),  # IPv6 compatible
        nullable=True,
        comment="Dirección IP del usuario"
    )
    
    user_agent = Column(
        Text,
        nullable=True,
        comment="User Agent del navegador"
    )
    
    session_id = Column(
        String(100),
        nullable=True,
        index=True,
        comment="ID de sesión del usuario"
    )
    
    # Metadata adicional de ubicación
    location_from = Column(
        JSON,
        nullable=True,
        comment="Ubicación origen (JSON)"
    )
    
    location_to = Column(
        JSON,
        nullable=True,
        comment="Ubicación destino (JSON)"
    )
    
    # Para movimientos en lote
    batch_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID de lote para movimientos agrupados"
    )
    
    # Comentarios adicionales
    notes = Column(
        Text,
        nullable=True,
        comment="Notas adicionales del tracking"
    )
    
    # Timestamp específico de la acción
    action_timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="Timestamp específico de la acción"
    )
    
    # Relationships
    movement = relationship("MovimientoStock", backref="tracking_history")
    user = relationship("User", backref="tracked_actions")
    
    def __init__(self, **kwargs):
        """Inicializar tracker con defaults automáticos"""
        # Asegurar timestamp si no se proporciona
        if 'action_timestamp' not in kwargs:
            kwargs['action_timestamp'] = datetime.utcnow()
        
        # Llamar al constructor padre
        super().__init__(**kwargs)
    
    @property
    def is_create_action(self) -> bool:
        """Verificar si es una acción de creación"""
        return self.action_type in [ActionType.CREATE.value, ActionType.BATCH_CREATE.value]
    
    @property
    def is_update_action(self) -> bool:
        """Verificar si es una acción de actualización"""
        return self.action_type in [ActionType.UPDATE.value, ActionType.BATCH_UPDATE.value]
    
    @property
    def is_system_action(self) -> bool:
        """Verificar si es una acción del sistema"""
        return self.action_type == ActionType.SYSTEM_AUTO.value
    
    @property
    def has_location_change(self) -> bool:
        """Verificar si hubo cambio de ubicación"""
        return self.location_from is not None and self.location_to is not None
    
    def get_changes(self) -> Dict[str, Any]:
        """Obtener diccionario de cambios realizados"""
        if not self.previous_data or not self.new_data:
            return {}
        
        changes = {}
        for key, new_value in self.new_data.items():
            old_value = self.previous_data.get(key)
            if old_value != new_value:
                changes[key] = {
                    'old': old_value,
                    'new': new_value
                }
        
        return changes
    
    def to_dict(self) -> dict:
        """Serializar tracker a diccionario."""
        base_dict = super().to_dict()
        tracker_dict = {
            "movement_id": str(self.movement_id) if self.movement_id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "user_name": self.user_name,
            "action_type": self.action_type,
            "previous_data": self.previous_data,
            "new_data": self.new_data,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "location_from": self.location_from,
            "location_to": self.location_to,
            "batch_id": str(self.batch_id) if self.batch_id else None,
            "notes": self.notes,
            "action_timestamp": self.action_timestamp.isoformat() if self.action_timestamp else None,
            "is_create_action": self.is_create_action,
            "is_update_action": self.is_update_action,
            "is_system_action": self.is_system_action,
            "has_location_change": self.has_location_change,
            "changes": self.get_changes(),
        }
        return {**base_dict, **tracker_dict}
    
    def __repr__(self) -> str:
        """Representación string del objeto MovementTracker."""
        return f"<MovementTracker {self.action_type} by {self.user_name} at {self.action_timestamp}>"