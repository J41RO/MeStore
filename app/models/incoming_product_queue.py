# ~/app/models/incoming_product_queue.py
# ---------------------------------------------------------------------------------------------
# MeStore - Modelo de Cola de Productos Entrantes
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: incoming_product_queue.py
# Ruta: ~/app/models/incoming_product_queue.py
# Autor: Jairo
# Fecha de Creación: 2025-09-10
# Última Actualización: 2025-09-10
# Versión: 1.0.0
# Propósito: Modelo IncomingProductQueue para gestión de productos entrantes en tránsito
#            Se integra con el sistema Product existente para flujo TRANSITO → VERIFICADO
#
# ---------------------------------------------------------------------------------------------

"""
Modelo IncomingProductQueue para gestión de productos entrantes.

Este módulo contiene:
- Clase IncomingProductQueue: Modelo principal para cola de productos entrantes
- Enum QueuePriority: Prioridades de verificación
- Enum VerificationStatus: Estados de verificación en la cola
- Relaciones con Product y User existentes
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Enum as SQLEnum, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from enum import Enum
from typing import Optional, Dict, Any
import uuid
from datetime import datetime, timedelta

from .base import BaseModel


class QueuePriority(str, Enum):
    """
    Enumeración para prioridades en la cola de productos entrantes.
    
    Prioridades de verificación:
        LOW: Prioridad baja - productos sin urgencia
        NORMAL: Prioridad normal - flujo estándar
        HIGH: Prioridad alta - productos urgentes
        CRITICAL: Prioridad crítica - productos con fecha límite inmediata
        EXPEDITED: Prioridad expedita - productos de clientes premium
    """
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    EXPEDITED = "EXPEDITED"


class VerificationStatus(str, Enum):
    """
    Enumeración para estados de verificación en la cola.
    
    Estados del proceso de verificación:
        PENDING: Pendiente de asignación
        ASSIGNED: Asignado a verificador
        IN_PROGRESS: En proceso de verificación
        QUALITY_CHECK: En verificación de calidad
        APPROVED: Aprobado, listo para VERIFICADO
        REJECTED: Rechazado, requiere acción
        ON_HOLD: En espera por documentación/información
        COMPLETED: Completado, producto movido a VERIFICADO
    """
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    QUALITY_CHECK = "QUALITY_CHECK"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"


class DelayReason(str, Enum):
    """
    Razones comunes de retraso en la cola.
    
    Razones de retraso:
        TRANSPORT: Retraso en transporte
        CUSTOMS: Retraso en aduanas
        DOCUMENTATION: Documentación faltante o incorrecta
        VENDOR_DELAY: Retraso del vendor
        QUALITY_ISSUES: Problemas de calidad
        CAPACITY: Falta de capacidad de verificación
        OTHER: Otras razones
    """
    TRANSPORT = "TRANSPORT"
    CUSTOMS = "CUSTOMS"
    DOCUMENTATION = "DOCUMENTATION"
    VENDOR_DELAY = "VENDOR_DELAY"
    QUALITY_ISSUES = "QUALITY_ISSUES"
    CAPACITY = "CAPACITY"
    OTHER = "OTHER"


class IncomingProductQueue(BaseModel):
    """
    Modelo IncomingProductQueue para gestión de productos entrantes en tránsito.
    
    Este modelo gestiona la cola de productos que están en estado TRANSITO
    y necesitan ser verificados antes de pasar a estado VERIFICADO.
    
    Campos principales:
    - product_id: Referencia al producto en tránsito
    - vendor_id: Vendor que envía el producto
    - expected_arrival: Fecha esperada de llegada
    - actual_arrival: Fecha real de llegada
    - verification_status: Estado del proceso de verificación
    - priority: Prioridad en la cola
    - assigned_to: Usuario asignado para verificación
    """
    
    __tablename__ = "incoming_product_queue"
    
    # Relación con Product existente
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey('products.id'),
        nullable=False,
        index=True,
        comment="ID del producto en tránsito"
    )
    
    # Vendor que envía el producto
    vendor_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=False,
        index=True,
        comment="Vendor responsable del envío"
    )
    
    # Gestión de fechas de llegada
    expected_arrival = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Fecha esperada de llegada"
    )
    
    actual_arrival = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Fecha real de llegada"
    )
    
    # Estado y prioridad en la cola
    verification_status = Column(
        SQLEnum(VerificationStatus),
        default=VerificationStatus.PENDING,
        nullable=False,
        index=True,
        comment="Estado actual en el proceso de verificación"
    )
    
    priority = Column(
        SQLEnum(QueuePriority),
        default=QueuePriority.NORMAL,
        nullable=False,
        index=True,
        comment="Prioridad en la cola de verificación"
    )
    
    # Asignación de tarea
    assigned_to = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=True,
        index=True,
        comment="Usuario asignado para verificación"
    )
    
    assigned_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de asignación"
    )
    
    # Tiempo límite para completar verificación
    deadline = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha límite para completar verificación"
    )
    
    # Información de seguimiento
    tracking_number = Column(
        String(100),
        nullable=True,
        comment="Número de tracking del envío"
    )
    
    carrier = Column(
        String(50),
        nullable=True,
        comment="Empresa transportadora"
    )
    
    # Gestión de retrasos
    is_delayed = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica si el producto está retrasado"
    )
    
    delay_reason = Column(
        SQLEnum(DelayReason),
        nullable=True,
        comment="Razón del retraso si aplica"
    )
    
    # Notas y observaciones
    notes = Column(
        Text,
        nullable=True,
        comment="Notas generales sobre el producto"
    )
    
    verification_notes = Column(
        Text,
        nullable=True,
        comment="Notas específicas del proceso de verificación"
    )
    
    # Información de calidad
    quality_score = Column(
        Integer,
        nullable=True,
        comment="Puntuación de calidad (1-10)"
    )
    
    quality_issues = Column(
        Text,
        nullable=True,
        comment="Problemas de calidad identificados"
    )
    
    # Metadata de procesamiento
    processing_started_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Inicio del procesamiento de verificación"
    )
    
    processing_completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Finalización del procesamiento"
    )
    
    # Contadores de intentos
    verification_attempts = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Número de intentos de verificación"
    )
    
    # Relationships
    product = relationship("Product", back_populates="queue_entries")
    vendor = relationship("User", foreign_keys=[vendor_id], backref="sent_products")
    assigned_user = relationship("User", foreign_keys=[assigned_to], backref="assigned_verifications")
    
    def __init__(self, **kwargs):
        """Inicializar entrada de cola con defaults automáticos"""
        # Auto-calcular deadline si no se proporciona
        if 'deadline' not in kwargs and 'expected_arrival' in kwargs and kwargs['expected_arrival']:
            # Deadline por defecto: 3 días después de la llegada esperada
            kwargs['deadline'] = kwargs['expected_arrival'] + timedelta(days=3)
        
        super().__init__(**kwargs)
    
    @property
    def is_overdue(self) -> bool:
        """Verificar si está vencido"""
        if not self.deadline:
            return False
        return datetime.utcnow() > self.deadline
    
    @property
    def days_in_queue(self) -> int:
        """Calcular días en la cola"""
        if not self.created_at:
            return 0
        delta = datetime.utcnow() - self.created_at
        return delta.days
    
    @property
    def processing_time_hours(self) -> Optional[float]:
        """Calcular tiempo de procesamiento en horas"""
        if not self.processing_started_at:
            return None
        
        end_time = self.processing_completed_at or datetime.utcnow()
        delta = end_time - self.processing_started_at
        return delta.total_seconds() / 3600
    
    @property
    def is_high_priority(self) -> bool:
        """Verificar si es alta prioridad"""
        return self.priority in [QueuePriority.HIGH, QueuePriority.CRITICAL, QueuePriority.EXPEDITED]
    
    @property
    def status_display(self) -> str:
        """Texto legible del estado"""
        status_map = {
            VerificationStatus.PENDING: "Pendiente",
            VerificationStatus.ASSIGNED: "Asignado",
            VerificationStatus.IN_PROGRESS: "En Proceso",
            VerificationStatus.QUALITY_CHECK: "Control Calidad",
            VerificationStatus.APPROVED: "Aprobado",
            VerificationStatus.REJECTED: "Rechazado",
            VerificationStatus.ON_HOLD: "En Espera",
            VerificationStatus.COMPLETED: "Completado"
        }
        return status_map.get(self.verification_status, str(self.verification_status))
    
    @property
    def priority_display(self) -> str:
        """Texto legible de la prioridad"""
        priority_map = {
            QueuePriority.LOW: "Baja",
            QueuePriority.NORMAL: "Normal",
            QueuePriority.HIGH: "Alta",
            QueuePriority.CRITICAL: "Crítica",
            QueuePriority.EXPEDITED: "Expedita"
        }
        return priority_map.get(self.priority, str(self.priority))
    
    def assign_to_user(self, user_id: UUID, notes: Optional[str] = None):
        """Asignar producto a un verificador"""
        self.assigned_to = user_id
        self.assigned_at = datetime.utcnow()
        self.verification_status = VerificationStatus.ASSIGNED
        
        if notes:
            self.verification_notes = (self.verification_notes or "") + f"\n[{datetime.utcnow()}] Asignado: {notes}"
    
    def start_processing(self, notes: Optional[str] = None):
        """Iniciar proceso de verificación"""
        self.processing_started_at = datetime.utcnow()
        self.verification_status = VerificationStatus.IN_PROGRESS
        self.verification_attempts += 1
        
        if notes:
            self.verification_notes = (self.verification_notes or "") + f"\n[{datetime.utcnow()}] Iniciado: {notes}"
    
    def complete_verification(self, approved: bool, quality_score: Optional[int] = None, notes: Optional[str] = None):
        """Completar proceso de verificación"""
        self.processing_completed_at = datetime.utcnow()
        
        if approved:
            self.verification_status = VerificationStatus.APPROVED
            if quality_score:
                self.quality_score = quality_score
        else:
            self.verification_status = VerificationStatus.REJECTED
        
        if notes:
            action = "Aprobado" if approved else "Rechazado"
            self.verification_notes = (self.verification_notes or "") + f"\n[{datetime.utcnow()}] {action}: {notes}"
    
    def mark_as_delayed(self, reason: DelayReason, notes: Optional[str] = None):
        """Marcar producto como retrasado"""
        self.is_delayed = True
        self.delay_reason = reason
        
        if notes:
            self.notes = (self.notes or "") + f"\n[{datetime.utcnow()}] Retraso ({reason.value}): {notes}"
    
    def update_arrival(self, actual_arrival: datetime):
        """Actualizar fecha de llegada real"""
        self.actual_arrival = actual_arrival
        
        # Verificar si llegó tarde
        if self.expected_arrival and actual_arrival > self.expected_arrival:
            delay_days = (actual_arrival - self.expected_arrival).days
            if delay_days > 0:
                self.mark_as_delayed(
                    DelayReason.TRANSPORT, 
                    f"Llegada tardía por {delay_days} día(s)"
                )
    
    @validates('quality_score')
    def validate_quality_score(self, key, quality_score):
        """Validar puntuación de calidad"""
        if quality_score is not None:
            if not 1 <= quality_score <= 10:
                raise ValueError("Quality score debe estar entre 1 y 10")
        return quality_score
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del producto en cola"""
        return {
            "days_in_queue": self.days_in_queue,
            "processing_time_hours": self.processing_time_hours,
            "is_overdue": self.is_overdue,
            "is_delayed": self.is_delayed,
            "verification_attempts": self.verification_attempts,
            "quality_score": self.quality_score,
            "priority_level": self.priority.value,
            "current_status": self.verification_status.value
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializar entrada de cola a diccionario."""
        base_dict = super().to_dict()
        queue_dict = {
            "product_id": str(self.product_id) if self.product_id else None,
            "vendor_id": str(self.vendor_id) if self.vendor_id else None,
            "expected_arrival": self.expected_arrival.isoformat() if self.expected_arrival else None,
            "actual_arrival": self.actual_arrival.isoformat() if self.actual_arrival else None,
            "verification_status": self.verification_status.value if self.verification_status else None,
            "priority": self.priority.value if self.priority else None,
            "assigned_to": str(self.assigned_to) if self.assigned_to else None,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "tracking_number": self.tracking_number,
            "carrier": self.carrier,
            "is_delayed": self.is_delayed,
            "delay_reason": self.delay_reason.value if self.delay_reason else None,
            "notes": self.notes,
            "verification_notes": self.verification_notes,
            "quality_score": self.quality_score,
            "quality_issues": self.quality_issues,
            "processing_started_at": self.processing_started_at.isoformat() if self.processing_started_at else None,
            "processing_completed_at": self.processing_completed_at.isoformat() if self.processing_completed_at else None,
            "verification_attempts": self.verification_attempts,
            "is_overdue": self.is_overdue,
            "days_in_queue": self.days_in_queue,
            "processing_time_hours": self.processing_time_hours,
            "is_high_priority": self.is_high_priority,
            "status_display": self.status_display,
            "priority_display": self.priority_display,
            "metrics": self.get_metrics()
        }
        return {**base_dict, **queue_dict}
    
    def __repr__(self) -> str:
        """Representación string del objeto IncomingProductQueue."""
        return f"<IncomingProductQueue {self.verification_status.value} - Priority: {self.priority.value}>"