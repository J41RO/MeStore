# ~/app/services/queue_notification_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Sistema de Notificaciones para Cola de Productos Entrantes
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: queue_notification_service.py
# Ruta: ~/app/services/queue_notification_service.py
# Autor: Jairo
# Fecha de Creación: 2025-09-10
# Última Actualización: 2025-09-10
# Versión: 1.0.0
# Propósito: Servicio de notificaciones automáticas para cola de productos entrantes
#            Gestiona alertas por llegadas tardías, productos vencidos, y asignaciones
#
# ---------------------------------------------------------------------------------------------

"""
Sistema de Notificaciones para Cola de Productos Entrantes.

Este módulo contiene:
- QueueNotificationService: Servicio principal para notificaciones automáticas
- NotificationTypes: Tipos de notificaciones soportadas
- EmailTemplates: Templates para notificaciones por email
- NotificationScheduler: Programador de notificaciones automáticas
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from dataclasses import dataclass

from app.models.incoming_product_queue import IncomingProductQueue, VerificationStatus, QueuePriority, DelayReason
from app.models.user import User, UserType
from app.models.product import Product
from app.database import get_db

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Tipos de notificaciones automáticas"""
    ARRIVAL_OVERDUE = "ARRIVAL_OVERDUE"           # Llegada tardía
    DEADLINE_APPROACHING = "DEADLINE_APPROACHING"  # Deadline próximo
    DEADLINE_OVERDUE = "DEADLINE_OVERDUE"         # Deadline vencido
    QUEUE_ASSIGNMENT = "QUEUE_ASSIGNMENT"         # Nueva asignación
    QUALITY_ISSUE = "QUALITY_ISSUE"               # Problema de calidad
    PROCESSING_DELAYED = "PROCESSING_DELAYED"     # Procesamiento retrasado
    HIGH_PRIORITY_ALERT = "HIGH_PRIORITY_ALERT"   # Alerta alta prioridad
    DAILY_SUMMARY = "DAILY_SUMMARY"               # Resumen diario
    WEEKLY_REPORT = "WEEKLY_REPORT"               # Reporte semanal


@dataclass
class NotificationData:
    """Datos para una notificación"""
    type: NotificationType
    recipient_id: str
    recipient_email: str
    recipient_name: str
    title: str
    message: str
    data: Dict[str, Any]
    priority: str = "NORMAL"
    scheduled_for: Optional[datetime] = None


class QueueNotificationService:
    """Servicio de notificaciones para cola de productos entrantes"""
    
    def __init__(self):
        self.notifications_queue: List[NotificationData] = []
    
    async def check_and_send_notifications(self, db: AsyncSession) -> Dict[str, int]:
        """
        Verificar cola y enviar notificaciones automáticas necesarias.
        
        Returns:
            Dict con conteo de notificaciones enviadas por tipo
        """
        try:
            logger.info("Iniciando verificación de notificaciones automáticas")
            
            notifications_sent = {
                "arrival_overdue": 0,
                "deadline_approaching": 0,
                "deadline_overdue": 0,
                "processing_delayed": 0,
                "high_priority": 0,
                "quality_issues": 0
            }
            
            # Verificar llegadas tardías
            overdue_arrivals = await self._check_overdue_arrivals(db)
            notifications_sent["arrival_overdue"] = len(overdue_arrivals)
            
            # Verificar deadlines próximos (24 horas)
            approaching_deadlines = await self._check_approaching_deadlines(db)
            notifications_sent["deadline_approaching"] = len(approaching_deadlines)
            
            # Verificar deadlines vencidos
            overdue_deadlines = await self._check_overdue_deadlines(db)
            notifications_sent["deadline_overdue"] = len(overdue_deadlines)
            
            # Verificar procesamiento retrasado (más de 48 horas en proceso)
            processing_delayed = await self._check_processing_delayed(db)
            notifications_sent["processing_delayed"] = len(processing_delayed)
            
            # Verificar productos de alta prioridad sin asignar
            high_priority_unassigned = await self._check_high_priority_unassigned(db)
            notifications_sent["high_priority"] = len(high_priority_unassigned)
            
            # Verificar problemas de calidad
            quality_issues = await self._check_quality_issues(db)
            notifications_sent["quality_issues"] = len(quality_issues)
            
            # Enviar todas las notificaciones acumuladas
            await self._send_queued_notifications()
            
            logger.info(f"Notificaciones procesadas: {notifications_sent}")
            return notifications_sent
            
        except Exception as e:
            logger.error(f"Error en verificación de notificaciones: {str(e)}")
            return {}
    
    async def _check_overdue_arrivals(self, db: AsyncSession) -> List[NotificationData]:
        """Verificar productos con llegada tardía"""
        try:
            now = datetime.utcnow()
            
            query = select(IncomingProductQueue, User, Product).select_from(
                IncomingProductQueue.__table__.join(
                    User.__table__, IncomingProductQueue.vendor_id == User.id
                ).join(
                    Product.__table__, IncomingProductQueue.product_id == Product.id
                )
            ).filter(
                and_(
                    IncomingProductQueue.expected_arrival < now,
                    IncomingProductQueue.actual_arrival.is_(None),
                    IncomingProductQueue.verification_status.in_([
                        VerificationStatus.PENDING,
                        VerificationStatus.ASSIGNED
                    ]),
                    IncomingProductQueue.is_delayed == False  # Solo avisar la primera vez
                )
            )
            
            result = await db.execute(query)
            overdue_items = result.all()
            
            notifications = []
            for queue_item, vendor, product in overdue_items:
                # Marcar como retrasado automáticamente
                queue_item.mark_as_delayed(
                    DelayReason.TRANSPORT, 
                    f"Automático: Llegada tardía detectada el {now.strftime('%Y-%m-%d %H:%M')}"
                )
                
                # Crear notificación para vendor
                vendor_notification = NotificationData(
                    type=NotificationType.ARRIVAL_OVERDUE,
                    recipient_id=str(vendor.id),
                    recipient_email=vendor.email,
                    recipient_name=vendor.nombre,
                    title=f"🚨 Producto Retrasado - {product.nombre}",
                    message=f"Su producto '{product.nombre}' tenía llegada esperada el {queue_item.expected_arrival.strftime('%d/%m/%Y')} pero aún no ha arribado. Por favor, actualice el estado del envío.",
                    data={
                        "queue_id": str(queue_item.id),
                        "product_id": str(product.id),
                        "product_name": product.nombre,
                        "expected_arrival": queue_item.expected_arrival.isoformat(),
                        "days_overdue": (now - queue_item.expected_arrival).days,
                        "tracking_number": queue_item.tracking_number,
                        "carrier": queue_item.carrier
                    },
                    priority="HIGH"
                )
                notifications.append(vendor_notification)
                
                # Crear notificación para administradores
                admin_notification = await self._create_admin_notification(
                    NotificationType.ARRIVAL_OVERDUE,
                    f"Producto Retrasado - {product.nombre}",
                    f"El producto '{product.nombre}' del vendor {vendor.nombre} está retrasado {(now - queue_item.expected_arrival).days} días.",
                    {
                        "queue_id": str(queue_item.id),
                        "vendor_name": vendor.nombre,
                        "product_name": product.nombre,
                        "days_overdue": (now - queue_item.expected_arrival).days
                    },
                    db
                )
                if admin_notification:
                    notifications.extend(admin_notification)
            
            # Guardar cambios en BD
            await db.commit()
            
            # Agregar a cola de envío
            self.notifications_queue.extend(notifications)
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error verificando llegadas tardías: {str(e)}")
            return []
    
    async def _check_approaching_deadlines(self, db: AsyncSession) -> List[NotificationData]:
        """Verificar deadlines próximos (24 horas)"""
        try:
            now = datetime.utcnow()
            tomorrow = now + timedelta(hours=24)
            
            query = select(IncomingProductQueue, User, Product).select_from(
                IncomingProductQueue.__table__.join(
                    Product.__table__, IncomingProductQueue.product_id == Product.id
                ).outerjoin(
                    User.__table__, IncomingProductQueue.assigned_to == User.id
                )
            ).filter(
                and_(
                    IncomingProductQueue.deadline.between(now, tomorrow),
                    IncomingProductQueue.verification_status.in_([
                        VerificationStatus.PENDING,
                        VerificationStatus.ASSIGNED,
                        VerificationStatus.IN_PROGRESS
                    ])
                )
            )
            
            result = await db.execute(query)
            approaching_items = result.all()
            
            notifications = []
            for queue_item, assigned_user, product in approaching_items:
                # Notificar al usuario asignado si existe
                if assigned_user:
                    user_notification = NotificationData(
                        type=NotificationType.DEADLINE_APPROACHING,
                        recipient_id=str(assigned_user.id),
                        recipient_email=assigned_user.email,
                        recipient_name=assigned_user.nombre,
                        title=f"⏰ Deadline Próximo - {product.nombre}",
                        message=f"El producto '{product.nombre}' tiene deadline de verificación en las próximas 24 horas ({queue_item.deadline.strftime('%d/%m/%Y %H:%M')}). Favor completar la verificación.",
                        data={
                            "queue_id": str(queue_item.id),
                            "product_id": str(product.id),
                            "product_name": product.nombre,
                            "deadline": queue_item.deadline.isoformat(),
                            "hours_remaining": int((queue_item.deadline - now).total_seconds() / 3600)
                        },
                        priority="HIGH"
                    )
                    notifications.append(user_notification)
                
                # Notificar administradores
                admin_notifications = await self._create_admin_notification(
                    NotificationType.DEADLINE_APPROACHING,
                    f"Deadline Próximo - {product.nombre}",
                    f"El producto '{product.nombre}' tiene deadline en {int((queue_item.deadline - now).total_seconds() / 3600)} horas.",
                    {
                        "queue_id": str(queue_item.id),
                        "product_name": product.nombre,
                        "assigned_to": assigned_user.nombre if assigned_user else "No asignado",
                        "hours_remaining": int((queue_item.deadline - now).total_seconds() / 3600)
                    },
                    db
                )
                if admin_notifications:
                    notifications.extend(admin_notifications)
            
            self.notifications_queue.extend(notifications)
            return notifications
            
        except Exception as e:
            logger.error(f"Error verificando deadlines próximos: {str(e)}")
            return []
    
    async def _check_overdue_deadlines(self, db: AsyncSession) -> List[NotificationData]:
        """Verificar deadlines vencidos"""
        try:
            now = datetime.utcnow()
            
            query = select(IncomingProductQueue, User, Product).select_from(
                IncomingProductQueue.__table__.join(
                    Product.__table__, IncomingProductQueue.product_id == Product.id
                ).outerjoin(
                    User.__table__, IncomingProductQueue.assigned_to == User.id
                )
            ).filter(
                and_(
                    IncomingProductQueue.deadline < now,
                    IncomingProductQueue.verification_status.in_([
                        VerificationStatus.PENDING,
                        VerificationStatus.ASSIGNED,
                        VerificationStatus.IN_PROGRESS,
                        VerificationStatus.QUALITY_CHECK
                    ])
                )
            )
            
            result = await db.execute(query)
            overdue_items = result.all()
            
            notifications = []
            for queue_item, assigned_user, product in overdue_items:
                days_overdue = (now - queue_item.deadline).days
                
                # Notificar al usuario asignado
                if assigned_user:
                    user_notification = NotificationData(
                        type=NotificationType.DEADLINE_OVERDUE,
                        recipient_id=str(assigned_user.id),
                        recipient_email=assigned_user.email,
                        recipient_name=assigned_user.nombre,
                        title=f"🔴 URGENTE: Deadline Vencido - {product.nombre}",
                        message=f"El producto '{product.nombre}' tiene deadline vencido hace {days_overdue} día(s). Requiere atención inmediata.",
                        data={
                            "queue_id": str(queue_item.id),
                            "product_id": str(product.id),
                            "product_name": product.nombre,
                            "deadline": queue_item.deadline.isoformat(),
                            "days_overdue": days_overdue
                        },
                        priority="CRITICAL"
                    )
                    notifications.append(user_notification)
                
                # Notificar administradores
                admin_notifications = await self._create_admin_notification(
                    NotificationType.DEADLINE_OVERDUE,
                    f"🔴 Deadline Vencido - {product.nombre}",
                    f"Producto '{product.nombre}' vencido hace {days_overdue} día(s). Asignado a: {assigned_user.nombre if assigned_user else 'No asignado'}.",
                    {
                        "queue_id": str(queue_item.id),
                        "product_name": product.nombre,
                        "assigned_to": assigned_user.nombre if assigned_user else "No asignado",
                        "days_overdue": days_overdue
                    },
                    db
                )
                if admin_notifications:
                    notifications.extend(admin_notifications)
            
            self.notifications_queue.extend(notifications)
            return notifications
            
        except Exception as e:
            logger.error(f"Error verificando deadlines vencidos: {str(e)}")
            return []
    
    async def _check_processing_delayed(self, db: AsyncSession) -> List[NotificationData]:
        """Verificar productos con procesamiento retrasado (>48h)"""
        try:
            threshold = datetime.utcnow() - timedelta(hours=48)
            
            query = select(IncomingProductQueue, User, Product).select_from(
                IncomingProductQueue.__table__.join(
                    Product.__table__, IncomingProductQueue.product_id == Product.id
                ).outerjoin(
                    User.__table__, IncomingProductQueue.assigned_to == User.id
                )
            ).filter(
                and_(
                    IncomingProductQueue.processing_started_at < threshold,
                    IncomingProductQueue.processing_completed_at.is_(None),
                    IncomingProductQueue.verification_status == VerificationStatus.IN_PROGRESS
                )
            )
            
            result = await db.execute(query)
            delayed_items = result.all()
            
            notifications = []
            for queue_item, assigned_user, product in delayed_items:
                hours_delayed = int((datetime.utcnow() - queue_item.processing_started_at).total_seconds() / 3600)
                
                if assigned_user:
                    user_notification = NotificationData(
                        type=NotificationType.PROCESSING_DELAYED,
                        recipient_id=str(assigned_user.id),
                        recipient_email=assigned_user.email,
                        recipient_name=assigned_user.nombre,
                        title=f"⚠️ Procesamiento Retrasado - {product.nombre}",
                        message=f"El producto '{product.nombre}' lleva {hours_delayed} horas en procesamiento. Favor revisar el estado de verificación.",
                        data={
                            "queue_id": str(queue_item.id),
                            "product_name": product.nombre,
                            "hours_delayed": hours_delayed,
                            "processing_started": queue_item.processing_started_at.isoformat()
                        },
                        priority="HIGH"
                    )
                    notifications.append(user_notification)
            
            self.notifications_queue.extend(notifications)
            return notifications
            
        except Exception as e:
            logger.error(f"Error verificando procesamiento retrasado: {str(e)}")
            return []
    
    async def _check_high_priority_unassigned(self, db: AsyncSession) -> List[NotificationData]:
        """Verificar productos de alta prioridad sin asignar"""
        try:
            query = select(IncomingProductQueue, Product).select_from(
                IncomingProductQueue.__table__.join(
                    Product.__table__, IncomingProductQueue.product_id == Product.id
                )
            ).filter(
                and_(
                    IncomingProductQueue.priority.in_([
                        QueuePriority.HIGH,
                        QueuePriority.CRITICAL,
                        QueuePriority.EXPEDITED
                    ]),
                    IncomingProductQueue.assigned_to.is_(None),
                    IncomingProductQueue.verification_status == VerificationStatus.PENDING,
                    IncomingProductQueue.days_in_queue > 0  # Al menos 1 día sin asignar
                )
            )
            
            result = await db.execute(query)
            unassigned_items = result.all()
            
            notifications = []
            for queue_item, product in unassigned_items:
                # Solo notificar administradores
                admin_notifications = await self._create_admin_notification(
                    NotificationType.HIGH_PRIORITY_ALERT,
                    f"🚨 Alta Prioridad Sin Asignar - {product.nombre}",
                    f"Producto de prioridad {queue_item.priority.value} lleva {queue_item.days_in_queue} día(s) sin asignar.",
                    {
                        "queue_id": str(queue_item.id),
                        "product_name": product.nombre,
                        "priority": queue_item.priority.value,
                        "days_unassigned": queue_item.days_in_queue
                    },
                    db
                )
                if admin_notifications:
                    notifications.extend(admin_notifications)
            
            self.notifications_queue.extend(notifications)
            return notifications
            
        except Exception as e:
            logger.error(f"Error verificando alta prioridad sin asignar: {str(e)}")
            return []
    
    async def _check_quality_issues(self, db: AsyncSession) -> List[NotificationData]:
        """Verificar problemas de calidad reportados"""
        try:
            query = select(IncomingProductQueue, Product, User).select_from(
                IncomingProductQueue.__table__.join(
                    Product.__table__, IncomingProductQueue.product_id == Product.id
                ).join(
                    User.__table__, IncomingProductQueue.vendor_id == User.id
                )
            ).filter(
                and_(
                    IncomingProductQueue.quality_issues.isnot(None),
                    IncomingProductQueue.quality_score < 3,  # Puntuación baja
                    IncomingProductQueue.verification_status.in_([
                        VerificationStatus.QUALITY_CHECK,
                        VerificationStatus.REJECTED
                    ])
                )
            )
            
            result = await db.execute(query)
            quality_items = result.all()
            
            notifications = []
            for queue_item, product, vendor in quality_items:
                # Notificar vendor
                vendor_notification = NotificationData(
                    type=NotificationType.QUALITY_ISSUE,
                    recipient_id=str(vendor.id),
                    recipient_email=vendor.email,
                    recipient_name=vendor.nombre,
                    title=f"❌ Problema de Calidad - {product.nombre}",
                    message=f"Su producto '{product.nombre}' presentó problemas de calidad durante la verificación. Puntuación: {queue_item.quality_score}/10. Detalles: {queue_item.quality_issues}",
                    data={
                        "queue_id": str(queue_item.id),
                        "product_name": product.nombre,
                        "quality_score": queue_item.quality_score,
                        "quality_issues": queue_item.quality_issues
                    },
                    priority="HIGH"
                )
                notifications.append(vendor_notification)
                
                # Notificar administradores
                admin_notifications = await self._create_admin_notification(
                    NotificationType.QUALITY_ISSUE,
                    f"Problema de Calidad - {product.nombre}",
                    f"Producto del vendor {vendor.nombre} con problemas de calidad. Puntuación: {queue_item.quality_score}/10.",
                    {
                        "queue_id": str(queue_item.id),
                        "vendor_name": vendor.nombre,
                        "product_name": product.nombre,
                        "quality_score": queue_item.quality_score
                    },
                    db
                )
                if admin_notifications:
                    notifications.extend(admin_notifications)
            
            self.notifications_queue.extend(notifications)
            return notifications
            
        except Exception as e:
            logger.error(f"Error verificando problemas de calidad: {str(e)}")
            return []
    
    async def _create_admin_notification(
        self, 
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Dict[str, Any],
        db: AsyncSession
    ) -> List[NotificationData]:
        """Crear notificaciones para administradores"""
        try:
            # Obtener todos los administradores
            admin_query = select(User).filter(
                User.user_type == UserType.ADMIN,
                User.is_active == True
            )
            
            result = await db.execute(admin_query)
            admins = result.scalars().all()
            
            notifications = []
            for admin in admins:
                notification = NotificationData(
                    type=notification_type,
                    recipient_id=str(admin.id),
                    recipient_email=admin.email,
                    recipient_name=admin.nombre,
                    title=title,
                    message=message,
                    data=data,
                    priority="HIGH" if notification_type in [
                        NotificationType.DEADLINE_OVERDUE,
                        NotificationType.HIGH_PRIORITY_ALERT
                    ] else "NORMAL"
                )
                notifications.append(notification)
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error creando notificaciones admin: {str(e)}")
            return []
    
    async def _send_queued_notifications(self):
        """Enviar todas las notificaciones en cola"""
        try:
            sent_count = 0
            for notification in self.notifications_queue:
                # Aquí se integraría con el servicio de email/SMS real
                # Por ahora solo loguear
                logger.info(
                    f"📧 Notificación enviada: {notification.type.value} "
                    f"-> {notification.recipient_email} "
                    f"({notification.title})"
                )
                sent_count += 1
            
            # Limpiar cola después de enviar
            self.notifications_queue.clear()
            
            logger.info(f"Total notificaciones enviadas: {sent_count}")
            
        except Exception as e:
            logger.error(f"Error enviando notificaciones: {str(e)}")
    
    async def send_assignment_notification(
        self, 
        queue_item: IncomingProductQueue, 
        assigned_user: User, 
        product: Product,
        notes: Optional[str] = None
    ):
        """Enviar notificación de nueva asignación"""
        try:
            notification = NotificationData(
                type=NotificationType.QUEUE_ASSIGNMENT,
                recipient_id=str(assigned_user.id),
                recipient_email=assigned_user.email,
                recipient_name=assigned_user.nombre,
                title=f"📦 Nueva Asignación - {product.nombre}",
                message=f"Se le ha asignado el producto '{product.nombre}' para verificación. Prioridad: {queue_item.priority_display}. {f'Notas: {notes}' if notes else ''}",
                data={
                    "queue_id": str(queue_item.id),
                    "product_id": str(product.id),
                    "product_name": product.nombre,
                    "priority": queue_item.priority.value,
                    "deadline": queue_item.deadline.isoformat() if queue_item.deadline else None,
                    "notes": notes
                },
                priority="HIGH" if queue_item.is_high_priority else "NORMAL"
            )
            
            self.notifications_queue.append(notification)
            await self._send_queued_notifications()
            
            logger.info(f"Notificación de asignación enviada a {assigned_user.email}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación de asignación: {str(e)}")
    
    async def generate_daily_summary(self, db: AsyncSession) -> Dict[str, Any]:
        """Generar resumen diario de la cola"""
        try:
            today = datetime.utcnow().date()
            
            # Estadísticas del día
            stats_query = select(
                func.count(IncomingProductQueue.id).label('total_items'),
                func.count(
                    func.case((IncomingProductQueue.verification_status == VerificationStatus.COMPLETED, 1))
                ).label('completed_today'),
                func.count(
                    func.case((IncomingProductQueue.verification_status == VerificationStatus.PENDING, 1))
                ).label('pending_items'),
                func.count(
                    func.case((IncomingProductQueue.is_delayed == True, 1))
                ).label('delayed_items'),
                func.count(
                    func.case((IncomingProductQueue.deadline < func.now(), 1))
                ).label('overdue_items')
            ).filter(
                func.date(IncomingProductQueue.created_at) == today
            )
            
            result = await db.execute(stats_query)
            daily_stats = result.first()
            
            summary = {
                "date": today.isoformat(),
                "total_items": daily_stats.total_items or 0,
                "completed_today": daily_stats.completed_today or 0,
                "pending_items": daily_stats.pending_items or 0,
                "delayed_items": daily_stats.delayed_items or 0,
                "overdue_items": daily_stats.overdue_items or 0,
                "completion_rate": (daily_stats.completed_today / daily_stats.total_items * 100) if daily_stats.total_items > 0 else 0
            }
            
            logger.info(f"Resumen diario generado: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generando resumen diario: {str(e)}")
            return {}


# Instancia global del servicio
queue_notification_service = QueueNotificationService()