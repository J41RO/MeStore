from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)

class NotificationType(str, Enum):
    PRODUCT_REJECTED = "product_rejected"
    PRODUCT_APPROVED = "product_approved"
    QUALITY_ISSUES = "quality_issues"
    APPEAL_REQUEST = "appeal_request"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"

class NotificationTemplate(BaseModel):
    type: NotificationType
    subject_template: str
    body_template: str
    sms_template: Optional[str] = None

class NotificationService:
    def __init__(self):
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[NotificationType, NotificationTemplate]:
        return {
            NotificationType.PRODUCT_REJECTED: NotificationTemplate(
                type=NotificationType.PRODUCT_REJECTED,
                subject_template="Producto Rechazado - Tracking: {{ tracking_number }}",
                body_template="""
Estimado(a) {{ vendor_name }},

Lamentamos informarle que su producto con tracking {{ tracking_number }} ha sido rechazado durante el proceso de verificación.

Razones del rechazo:
{{ rejection_reasons }}

Calificación de calidad: {{ quality_score }}/10

Próximos pasos:
1. Puede solicitar una apelación dentro de 48 horas
2. Puede enviar un producto de reemplazo
3. Contactar soporte para más información

Para apelar esta decisión, responda a este email con evidencia adicional.

Saludos cordiales,
Equipo MeStocker
                """,
                sms_template="MeStocker: Producto {{ tracking_number }} rechazado. Razón: {{ rejection_summary }}. Puede apelar en 48h."
            ),
            NotificationType.PRODUCT_APPROVED: NotificationTemplate(
                type=NotificationType.PRODUCT_APPROVED,
                subject_template="Producto Aprobado - Tracking: {{ tracking_number }}",
                body_template="""
Estimado(a) {{ vendor_name }},

¡Excelentes noticias! Su producto con tracking {{ tracking_number }} ha sido aprobado y está listo para su procesamiento.

Calificación de calidad: {{ quality_score }}/10

Su producto será procesado y estará disponible para la venta en las próximas 24-48 horas.

Saludos cordiales,
Equipo MeStocker
                """,
                sms_template="MeStocker: Producto {{ tracking_number }} APROBADO. Calificación: {{ quality_score }}/10."
            ),
            NotificationType.QUALITY_ISSUES: NotificationTemplate(
                type=NotificationType.QUALITY_ISSUES,
                subject_template="Problemas de Calidad Detectados - Tracking: {{ tracking_number }}",
                body_template="""
Estimado(a) {{ vendor_name }},

Hemos detectado algunos problemas de calidad con su producto tracking {{ tracking_number }}.

Problemas detectados:
{{ quality_issues }}

Calificación de calidad: {{ quality_score }}/10

Acción requerida:
{{ required_action }}

Saludos cordiales,
Equipo MeStocker
                """,
                sms_template="MeStocker: Problemas de calidad en {{ tracking_number }}. Revisión requerida."
            )
        }
    
    async def send_notification(
        self,
        notification_type: NotificationType,
        recipient_email: str,
        recipient_phone: Optional[str],
        template_data: Dict[str, Any],
        channels: List[NotificationChannel] = [NotificationChannel.EMAIL]
    ) -> bool:
        """Enviar notificación a través de múltiples canales"""
        template = self.templates.get(notification_type)
        if not template:
            raise ValueError(f"Template no encontrado para {notification_type}")
        
        success = True
        
        try:
            if NotificationChannel.EMAIL in channels:
                success &= await self._send_email(template, recipient_email, template_data)
                
            if NotificationChannel.SMS in channels and recipient_phone:
                success &= await self._send_sms(template, recipient_phone, template_data)
                
            # Log de notificación enviada
            logger.info(f"Notification sent - Type: {notification_type}, Email: {recipient_email}, Success: {success}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    async def _send_email(self, template: NotificationTemplate, email: str, data: Dict[str, Any]) -> bool:
        """Enviar notificación por email"""
        try:
            subject = Template(template.subject_template).render(**data)
            body = Template(template.body_template).render(**data)
            
            # Configurar mensaje
            msg = MIMEMultipart()
            msg['From'] = "notifications@mestocker.com"
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Por ahora, solo log (en producción conectar SMTP real)
            logger.info(f"EMAIL SENT to {email}: {subject}")
            print(f"📧 EMAIL SENT to {email}")
            print(f"📧 Subject: {subject}")
            print(f"📧 Body: {body}")
            print("=" * 50)
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False
    
    async def _send_sms(self, template: NotificationTemplate, phone: str, data: Dict[str, Any]) -> bool:
        """Enviar notificación por SMS"""
        try:
            if template.sms_template:
                message = Template(template.sms_template).render(**data)
                
                # Por ahora, solo log (en producción conectar SMS provider)
                logger.info(f"SMS SENT to {phone}: {message}")
                print(f"📱 SMS SENT to {phone}")
                print(f"📱 Message: {message}")
                print("=" * 50)
                
            return True
            
        except Exception as e:
            logger.error(f"Error enviando SMS: {e}")
            return False
    
    def create_appeal_deadline(self, hours: int = 48) -> datetime:
        """Crear deadline para apelación"""
        return datetime.now() + timedelta(hours=hours)
    
    async def send_bulk_notifications(
        self,
        notification_type: NotificationType,
        recipients: List[Dict[str, Any]],
        base_template_data: Dict[str, Any],
        channels: List[NotificationChannel] = [NotificationChannel.EMAIL]
    ) -> Dict[str, int]:
        """Enviar notificaciones en lote"""
        results = {"success": 0, "failed": 0}
        
        for recipient in recipients:
            template_data = {**base_template_data, **recipient.get("template_data", {})}
            
            success = await self.send_notification(
                notification_type,
                recipient["email"],
                recipient.get("phone"),
                template_data,
                channels
            )
            
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
                
        return results