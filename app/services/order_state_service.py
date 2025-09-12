# ~/app/services/order_state_service.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Enterprise Order State Service
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
Enterprise Order State Management Service

Sistema avanzado de gestión de estados de órdenes con:
- Transiciones automáticas según business rules
- Validaciones de seguridad por usuario
- Logging estructurado para auditoría
- Timestamps automáticos para cada transición
- Configuración dinámica para hosting
"""

import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from dataclasses import dataclass

from app.models.order import Order, OrderStatus
from app.models.user import User
from app.core.logger import get_logger
from app.services.notification_service import NotificationService

logger = get_logger(__name__)


class StateTransitionError(Exception):
    """Error personalizado para transiciones de estado inválidas"""
    pass


@dataclass
class OrdersConfig:
    """PRODUCTION_READY: Configuración dinámica Orders"""
    
    def __init__(self):
        self.ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
        self.EMAIL_BASE_URL = self._get_email_base_url()
        self.NOTIFICATION_WEBHOOK_URL = os.getenv('NOTIFICATION_WEBHOOK_URL')
        self.ORDER_TRACKING_BASE_URL = self._get_tracking_base_url()
        
    def _get_email_base_url(self) -> str:
        if self.ENVIRONMENT == 'production':
            # TODO_HOSTING: Configurar dominio real
            return os.getenv('FRONTEND_URL', 'https://tudominio.com')
        return os.getenv('DEV_FRONTEND_URL', 'http://192.168.1.137:5173')
    
    def _get_tracking_base_url(self) -> str:
        if self.ENVIRONMENT == 'production':
            return os.getenv('TRACKING_API_URL', 'https://api.tudominio.com')
        return os.getenv('DEV_API_URL', 'http://192.168.1.137:8000')


class OrderStateService:
    """
    Servicio Enterprise para gestión avanzada de estados de órdenes.
    
    Características:
    - Business rules automáticas
    - Validaciones de seguridad
    - Logging estructurado
    - Notificaciones automáticas
    - Configuración dinámica
    """
    
    def __init__(self):
        self.config = OrdersConfig()
        self.notification_service = NotificationService()
        self._setup_business_rules()
        
    def _setup_business_rules(self):
        """Define las reglas de negocio para transiciones válidas"""
        self.VALID_TRANSITIONS = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
            OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
            OrderStatus.DELIVERED: [OrderStatus.REFUNDED],  # Solo refund después de entrega
            OrderStatus.CANCELLED: [],  # Estado final
            OrderStatus.REFUNDED: []    # Estado final
        }
        
        # Estados que requieren permisos especiales
        self.ADMIN_ONLY_TRANSITIONS = {
            OrderStatus.REFUNDED,
            OrderStatus.CANCELLED  # Solo admin puede cancelar órdenes confirmadas
        }
        
    async def transition_order_state(
        self, 
        db: AsyncSession,
        order_id: int,
        new_state: OrderStatus,
        user: User,
        reason: Optional[str] = None
    ) -> Order:
        """
        Transiciona una orden a un nuevo estado con validaciones completas.
        
        Args:
            db: Sesión de base de datos
            order_id: ID de la orden
            new_state: Nuevo estado deseado
            user: Usuario que ejecuta la transición
            reason: Razón opcional para la transición
            
        Returns:
            Order: Orden actualizada
            
        Raises:
            StateTransitionError: Si la transición no es válida
            PermissionError: Si el usuario no tiene permisos
        """
        # Obtener orden actual
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalars().first()
        
        if not order:
            raise StateTransitionError(f"Orden {order_id} no encontrada")
        
        # Validar transición
        await self._validate_transition(order, new_state, user)
        
        # Ejecutar transición
        old_state = order.status
        await self._execute_transition(db, order, new_state, user, reason)
        
        # Logging estructurado
        await self._log_transition(order, old_state, new_state, user, reason)
        
        # Notificación automática
        await self._notify_transition(order, old_state, new_state, user)
        
        logger.info(
            f"Order state transition completed",
            extra={
                "order_id": order_id,
                "old_state": old_state.value,
                "new_state": new_state.value,
                "user_id": user.id,
                "user_type": user.user_type
            }
        )
        
        return order
        
    async def _validate_transition(
        self, 
        order: Order, 
        new_state: OrderStatus, 
        user: User
    ):
        """Valida que la transición sea válida según business rules"""
        
        # Verificar transición permitida
        valid_transitions = self.VALID_TRANSITIONS.get(order.status, [])
        if new_state not in valid_transitions:
            raise StateTransitionError(
                f"Transición inválida: {order.status.value} -> {new_state.value}. "
                f"Transiciones válidas: {[t.value for t in valid_transitions]}"
            )
        
        # Verificar permisos de usuario
        if new_state in self.ADMIN_ONLY_TRANSITIONS:
            if user.user_type not in ['ADMIN', 'SUPERUSER']:
                raise PermissionError(
                    f"Solo administradores pueden transicionar a estado {new_state.value}"
                )
        
        # Validaciones específicas por estado
        await self._validate_specific_state(order, new_state, user)
        
    async def _validate_specific_state(
        self, 
        order: Order, 
        new_state: OrderStatus, 
        user: User
    ):
        """Validaciones específicas para cada estado"""
        
        if new_state == OrderStatus.SHIPPED:
            # Verificar que tenga información de envío
            if not order.tracking_number:
                raise StateTransitionError(
                    "No se puede marcar como enviado sin número de tracking"
                )
                
        elif new_state == OrderStatus.DELIVERED:
            # Verificar que esté en estado SHIPPED
            if order.status != OrderStatus.SHIPPED:
                raise StateTransitionError(
                    "Solo se puede entregar una orden que esté en estado SHIPPED"
                )
                
        elif new_state == OrderStatus.REFUNDED:
            # Verificar que esté entregada
            if order.status != OrderStatus.DELIVERED:
                raise StateTransitionError(
                    "Solo se puede reembolsar una orden que esté entregada"
                )
    
    async def _execute_transition(
        self,
        db: AsyncSession,
        order: Order,
        new_state: OrderStatus,
        user: User,
        reason: Optional[str]
    ):
        """Ejecuta la transición actualizando timestamps automáticamente"""
        
        # Actualizar estado
        order.status = new_state
        order.updated_at = datetime.utcnow()
        
        # Actualizar timestamps específicos según estado
        timestamp_updates = {
            OrderStatus.CONFIRMED: {"confirmed_at": datetime.utcnow()},
            OrderStatus.SHIPPED: {"shipped_at": datetime.utcnow()},
            OrderStatus.DELIVERED: {"delivered_at": datetime.utcnow()}
        }
        
        if new_state in timestamp_updates:
            for field, value in timestamp_updates[new_state].items():
                setattr(order, field, value)
        
        # Guardar cambios
        await db.commit()
        await db.refresh(order)
        
    async def _log_transition(
        self,
        order: Order,
        old_state: OrderStatus,
        new_state: OrderStatus,
        user: User,
        reason: Optional[str]
    ):
        """Logging estructurado para auditoría enterprise"""
        
        log_data = {
            "action": "order_state_transition",
            "order_id": order.id,
            "order_number": order.order_number,
            "old_state": old_state.value,
            "new_state": new_state.value,
            "user_id": user.id,
            "user_type": user.user_type,
            "user_email": getattr(user, 'email', 'unknown'),
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "tracking_url": f"{self.config.ORDER_TRACKING_BASE_URL}/api/v1/orders/track/{order.order_number}"
        }
        
        logger.info(
            f"Order {order.order_number} transitioned from {old_state.value} to {new_state.value}",
            extra=log_data
        )
        
    async def _notify_transition(
        self,
        order: Order,
        old_state: OrderStatus,
        new_state: OrderStatus,
        user: User
    ):
        """Envía notificaciones automáticas para la transición"""
        
        # Estados que requieren notificación al cliente
        notify_states = {
            OrderStatus.CONFIRMED,
            OrderStatus.SHIPPED,
            OrderStatus.DELIVERED,
            OrderStatus.CANCELLED,
            OrderStatus.REFUNDED
        }
        
        if new_state in notify_states:
            try:
                await self.notification_service.send_order_status_notification(
                    order=order,
                    old_status=old_state,
                    new_status=new_state
                )
                logger.info(f"Notification sent for order {order.order_number} -> {new_state.value}")
                
            except Exception as e:
                logger.error(
                    f"Failed to send notification for order {order.order_number}",
                    extra={"error": str(e), "order_id": order.id}
                )
    
    def get_valid_transitions(self, current_state: OrderStatus) -> List[OrderStatus]:
        """Retorna las transiciones válidas para un estado actual"""
        return self.VALID_TRANSITIONS.get(current_state, [])
    
    def can_user_transition_to(
        self, 
        user: User, 
        target_state: OrderStatus
    ) -> bool:
        """Verifica si un usuario puede transicionar a un estado específico"""
        
        if target_state in self.ADMIN_ONLY_TRANSITIONS:
            return user.user_type in ['ADMIN', 'SUPERUSER']
        return True
    
    async def get_order_timeline(
        self, 
        db: AsyncSession, 
        order_id: int
    ) -> List[Dict]:
        """
        Retorna la línea de tiempo completa de una orden para tracking.
        
        Returns:
            Lista de eventos con timestamps para tracking público
        """
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalars().first()
        
        if not order:
            return []
        
        timeline = []
        
        # Evento creación
        timeline.append({
            "status": "created",
            "timestamp": order.created_at,
            "description": "Orden creada",
            "is_current": order.status == OrderStatus.PENDING
        })
        
        # Eventos con timestamps
        timeline_events = [
            ("confirmed", order.confirmed_at, "Orden confirmada", OrderStatus.CONFIRMED),
            ("processing", None, "Procesando orden", OrderStatus.PROCESSING),  # No timestamp específico
            ("shipped", order.shipped_at, "Orden enviada", OrderStatus.SHIPPED),
            ("delivered", order.delivered_at, "Orden entregada", OrderStatus.DELIVERED)
        ]
        
        for event_name, timestamp, description, status in timeline_events:
            if timestamp or order.status == status:
                timeline.append({
                    "status": event_name,
                    "timestamp": timestamp,
                    "description": description,
                    "is_current": order.status == status
                })
        
        # Evento cancelación si aplica
        if order.status == OrderStatus.CANCELLED:
            timeline.append({
                "status": "cancelled",
                "timestamp": order.updated_at,
                "description": "Orden cancelada",
                "is_current": True
            })
            
        return timeline


# Instancia global del servicio
order_state_service = OrderStateService()