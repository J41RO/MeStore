# ~/app/tasks/queue_scheduler.py
# ---------------------------------------------------------------------------------------------
# MeStore - Programador de Tareas para Cola de Productos Entrantes
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: queue_scheduler.py
# Ruta: ~/app/tasks/queue_scheduler.py
# Autor: Jairo
# Fecha de Creación: 2025-09-10
# Última Actualización: 2025-09-10
# Versión: 1.0.0
# Propósito: Tareas programadas para verificación automática de notificaciones
#            y mantenimiento de la cola de productos entrantes
#
# ---------------------------------------------------------------------------------------------

"""
Programador de Tareas para Cola de Productos Entrantes.

Este módulo contiene:
- QueueScheduler: Programador principal de tareas automáticas
- BackgroundTasks: Tareas que se ejecutan en segundo plano
- CronJobs: Configuración de tareas programadas
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.services.queue_notification_service import queue_notification_service

logger = logging.getLogger(__name__)


class QueueScheduler:
    """Programador de tareas para cola de productos entrantes"""
    
    def __init__(self):
        self.running = False
        self.tasks: Dict[str, asyncio.Task] = {}
    
    async def start(self):
        """Iniciar el programador de tareas"""
        if self.running:
            logger.warning("El programador ya está ejecutándose")
            return
        
        self.running = True
        logger.info("🚀 Iniciando programador de tareas para cola de productos")
        
        # Iniciar tareas programadas
        self.tasks['notification_checker'] = asyncio.create_task(
            self._notification_checker_task()
        )
        
        self.tasks['daily_summary'] = asyncio.create_task(
            self._daily_summary_task()
        )
        
        self.tasks['queue_maintenance'] = asyncio.create_task(
            self._queue_maintenance_task()
        )
        
        logger.info("✅ Todas las tareas programadas iniciadas correctamente")
    
    async def stop(self):
        """Detener el programador de tareas"""
        if not self.running:
            return
        
        logger.info("🛑 Deteniendo programador de tareas...")
        self.running = False
        
        # Cancelar todas las tareas
        for task_name, task in self.tasks.items():
            logger.info(f"Cancelando tarea: {task_name}")
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.info(f"Tarea {task_name} cancelada correctamente")
        
        self.tasks.clear()
        logger.info("✅ Programador de tareas detenido")
    
    async def _notification_checker_task(self):
        """Tarea para verificar y enviar notificaciones cada 15 minutos"""
        while self.running:
            try:
                logger.debug("🔔 Ejecutando verificación de notificaciones...")
                
                async with AsyncSessionLocal() as db:
                    notifications_sent = await queue_notification_service.check_and_send_notifications(db)
                    
                    if any(notifications_sent.values()):
                        logger.info(f"Notificaciones enviadas: {notifications_sent}")
                    else:
                        logger.debug("No hay notificaciones que enviar")
                
                # Esperar 15 minutos antes de la siguiente verificación
                await asyncio.sleep(900)  # 15 minutos = 900 segundos
                
            except asyncio.CancelledError:
                logger.info("Tarea de notificaciones cancelada")
                break
            except Exception as e:
                logger.error(f"Error en verificación de notificaciones: {str(e)}")
                # Esperar 5 minutos antes de reintentar en caso de error
                await asyncio.sleep(300)
    
    async def _daily_summary_task(self):
        """Tarea para generar resumen diario a las 23:00"""
        while self.running:
            try:
                now = datetime.now()
                
                # Calcular próximas 23:00 horas
                next_summary = now.replace(hour=23, minute=0, second=0, microsecond=0)
                if now.hour >= 23:
                    next_summary += timedelta(days=1)
                
                # Calcular tiempo de espera
                wait_seconds = (next_summary - now).total_seconds()
                logger.debug(f"📊 Próximo resumen diario en {wait_seconds/3600:.2f} horas")
                
                await asyncio.sleep(wait_seconds)
                
                if not self.running:
                    break
                
                # Generar resumen diario
                logger.info("📊 Generando resumen diario de cola...")
                
                async with AsyncSessionLocal() as db:
                    summary = await queue_notification_service.generate_daily_summary(db)
                    
                    # Aquí se podría enviar el resumen por email a administradores
                    logger.info(f"Resumen diario generado: {summary}")
                
            except asyncio.CancelledError:
                logger.info("Tarea de resumen diario cancelada")
                break
            except Exception as e:
                logger.error(f"Error en resumen diario: {str(e)}")
                await asyncio.sleep(3600)  # Esperar 1 hora antes de reintentar
    
    async def _queue_maintenance_task(self):
        """Tarea de mantenimiento de cola cada 6 horas"""
        while self.running:
            try:
                logger.debug("🔧 Ejecutando mantenimiento de cola...")
                
                async with AsyncSessionLocal() as db:
                    maintenance_results = await self._perform_queue_maintenance(db)
                    
                    if maintenance_results:
                        logger.info(f"Mantenimiento completado: {maintenance_results}")
                
                # Esperar 6 horas antes del próximo mantenimiento
                await asyncio.sleep(21600)  # 6 horas = 21600 segundos
                
            except asyncio.CancelledError:
                logger.info("Tarea de mantenimiento cancelada")
                break
            except Exception as e:
                logger.error(f"Error en mantenimiento de cola: {str(e)}")
                await asyncio.sleep(1800)  # Esperar 30 minutos antes de reintentar
    
    async def _perform_queue_maintenance(self, db: AsyncSession) -> Dict[str, Any]:
        """Realizar tareas de mantenimiento de la cola"""
        try:
            from sqlalchemy import select, update, and_, func
            from app.models.incoming_product_queue import IncomingProductQueue, VerificationStatus
            
            maintenance_results = {
                "cleaned_completed": 0,
                "updated_priorities": 0,
                "archived_old": 0
            }
            
            # 1. Limpiar entradas completadas muy antiguas (>30 días)
            old_completed_date = datetime.utcnow() - timedelta(days=30)
            
            cleanup_query = select(func.count(IncomingProductQueue.id)).filter(
                and_(
                    IncomingProductQueue.verification_status == VerificationStatus.COMPLETED,
                    IncomingProductQueue.processing_completed_at < old_completed_date
                )
            )
            
            old_count_result = await db.execute(cleanup_query)
            old_completed_count = old_count_result.scalar()
            
            if old_completed_count > 0:
                # En un entorno real, aquí se archivarían en lugar de eliminar
                logger.info(f"Encontradas {old_completed_count} entradas completadas antigas para archivar")
                maintenance_results["archived_old"] = old_completed_count
            
            # 2. Auto-incrementar prioridad de elementos muy antiguos sin asignar
            old_pending_date = datetime.utcnow() - timedelta(days=7)
            
            priority_update = update(IncomingProductQueue).where(
                and_(
                    IncomingProductQueue.verification_status == VerificationStatus.PENDING,
                    IncomingProductQueue.created_at < old_pending_date,
                    IncomingProductQueue.priority == 'NORMAL'
                )
            ).values(
                priority='HIGH',
                updated_at=func.now()
            )
            
            priority_result = await db.execute(priority_update)
            maintenance_results["updated_priorities"] = priority_result.rowcount
            
            # 3. Marcar automáticamente como retrasados productos sin llegada después de deadline
            from app.models.incoming_product_queue import DelayReason
            
            auto_delay_query = select(IncomingProductQueue).filter(
                and_(
                    IncomingProductQueue.expected_arrival < datetime.utcnow(),
                    IncomingProductQueue.actual_arrival.is_(None),
                    IncomingProductQueue.is_delayed == False,
                    IncomingProductQueue.verification_status.in_([
                        VerificationStatus.PENDING,
                        VerificationStatus.ASSIGNED
                    ])
                )
            )
            
            auto_delay_result = await db.execute(auto_delay_query)
            auto_delay_items = auto_delay_result.scalars().all()
            
            for item in auto_delay_items:
                item.mark_as_delayed(
                    DelayReason.TRANSPORT,
                    "Automático: Marcado como retrasado por mantenimiento de cola"
                )
            
            if auto_delay_items:
                maintenance_results["auto_delayed"] = len(auto_delay_items)
            
            # Guardar cambios
            await db.commit()
            
            return maintenance_results
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error en mantenimiento de cola: {str(e)}")
            return {}
    
    async def force_notification_check(self):
        """Forzar verificación inmediata de notificaciones"""
        try:
            logger.info("🔔 Forzando verificación de notificaciones...")
            
            async with AsyncSessionLocal() as db:
                notifications_sent = await queue_notification_service.check_and_send_notifications(db)
                logger.info(f"Verificación forzada completada: {notifications_sent}")
                return notifications_sent
                
        except Exception as e:
            logger.error(f"Error en verificación forzada: {str(e)}")
            return {}
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del programador"""
        return {
            "running": self.running,
            "active_tasks": list(self.tasks.keys()),
            "task_status": {
                name: "running" if not task.done() else "completed"
                for name, task in self.tasks.items()
            }
        }


# Instancia global del programador
queue_scheduler = QueueScheduler()


@asynccontextmanager
async def lifespan_queue_scheduler():
    """Context manager para iniciar/detener el programador con la aplicación"""
    await queue_scheduler.start()
    try:
        yield
    finally:
        await queue_scheduler.stop()


# Función de utilidad para integrar con FastAPI
async def startup_queue_scheduler():
    """Iniciar el programador al arrancar la aplicación"""
    await queue_scheduler.start()


async def shutdown_queue_scheduler():
    """Detener el programador al cerrar la aplicación"""
    await queue_scheduler.stop()