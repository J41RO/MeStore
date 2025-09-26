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
import os
from app.services.smtp_email_service import SMTPEmailService as EmailService

logger = logging.getLogger(__name__)

class NotificationType(str, Enum):
    PRODUCT_REJECTED = "product_rejected"
    PRODUCT_APPROVED = "product_approved"
    QUALITY_ISSUES = "quality_issues"
    APPEAL_REQUEST = "appeal_request"
    # Nuevos tipos para órdenes
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_SHIPPED = "order_shipped"
    ORDER_DELIVERED = "order_delivered"
    ORDER_CANCELLED = "order_cancelled"
    ORDER_REFUNDED = "order_refunded"

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
        self.email_service = EmailService()
        self.retry_attempts = 3
        self.retry_delay = 5  # seconds
        
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
            ),
            
            # TEMPLATES PARA ÓRDENES ENTERPRISE
            NotificationType.ORDER_CONFIRMED: NotificationTemplate(
                type=NotificationType.ORDER_CONFIRMED,
                subject_template="✅ Orden Confirmada #{{ order_number }} - MeStore",
                body_template="""
¡Hola {{ customer_name }}!

✅ Hemos confirmado tu orden con éxito.

📋 DETALLES DE TU ORDEN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Número de Orden: #{{ order_number }}
Estado: {{ order_status }}
Fecha de Confirmación: {{ confirmed_at }}
Total: ${{ total_amount | number_format }} COP

📦 PRÓXIMOS PASOS:
• Procesaremos tu orden en las próximas 24 horas
• Te notificaremos cuando sea enviada
• Tiempo estimado de entrega: {{ estimated_delivery_days }} días hábiles

🔍 SEGUIMIENTO:
Puedes rastrear tu orden en cualquier momento:
{{ tracking_url }}

💬 ¿PREGUNTAS?
Contáctanos: soporte@mestore.com
WhatsApp: +57 (300) 123-4567

¡Gracias por confiar en MeStore!

Equipo MeStore 🛍️
                """,
                sms_template="MeStore: Orden #{{ order_number }} confirmada! Total: ${{ total_amount }}. Seguimiento: {{ tracking_url }}"
            ),
            
            NotificationType.ORDER_SHIPPED: NotificationTemplate(
                type=NotificationType.ORDER_SHIPPED,
                subject_template="🚚 Tu orden #{{ order_number }} está en camino - MeStore",
                body_template="""
¡Hola {{ customer_name }}!

🚚 ¡Tu orden ya está en camino!

📦 INFORMACIÓN DE ENVÍO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Número de Orden: #{{ order_number }}
Número de Seguimiento: {{ tracking_number }}
Transportadora: {{ carrier }}
Fecha de Envío: {{ shipped_at }}
Entrega Estimada: {{ estimated_delivery_date }}

📍 DIRECCIÓN DE ENTREGA:
{{ shipping_address }}

🔍 SEGUIMIENTO EN TIEMPO REAL:
{{ tracking_url }}
{{ carrier_tracking_url }}

📋 RESUMEN DEL PEDIDO:
Total: ${{ total_amount | number_format }} COP
Método de Pago: {{ payment_method }}

💡 CONSEJOS DE ENTREGA:
• Mantén tu celular disponible para coordinación
• Alguien debe estar presente para recibir el paquete
• Ten tu documento de identidad listo

¿Necesitas cambiar la dirección o fecha de entrega?
Contacta inmediatamente: soporte@mestore.com

¡Gracias por elegir MeStore!

Equipo MeStore 🛍️
                """,
                sms_template="MeStore: Orden #{{ order_number }} enviada! Tracking: {{ tracking_number }}. Llegará el {{ estimated_delivery_date }}."
            ),
            
            NotificationType.ORDER_DELIVERED: NotificationTemplate(
                type=NotificationType.ORDER_DELIVERED,
                subject_template="📦 ¡Tu orden #{{ order_number }} fue entregada! - MeStore",
                body_template="""
¡Hola {{ customer_name }}!

📦 ¡Tu orden ha sido entregada exitosamente!

✅ CONFIRMACIÓN DE ENTREGA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Número de Orden: #{{ order_number }}
Fecha de Entrega: {{ delivered_at }}
Recibido por: {{ received_by | default("Cliente") }}
Dirección: {{ delivery_address }}

🌟 ¿CÓMO FUE TU EXPERIENCIA?
Nos encantaría conocer tu opinión. Califica tu experiencia:
{{ review_url }}

💰 PROGRAMA DE REFERIDOS:
¡Comparte MeStore y gana descuentos!
{{ referral_link }}

🛍️ ¿BUSCAS MÁS PRODUCTOS?
Descubre nuestras ofertas especiales:
{{ marketplace_url }}

📞 SOPORTE POST-VENTA:
Si tienes algún problema con tu pedido:
• Email: soporte@mestore.com  
• WhatsApp: +57 (300) 123-4567
• Garantía de 30 días en todos nuestros productos

¡Gracias por confiar en MeStore!
Esperamos verte pronto de nuevo 😊

Equipo MeStore 🛍️
                """,
                sms_template="MeStore: ¡Orden #{{ order_number }} entregada! Califica tu experiencia: {{ review_url }}"
            ),
            
            NotificationType.ORDER_CANCELLED: NotificationTemplate(
                type=NotificationType.ORDER_CANCELLED,
                subject_template="❌ Orden #{{ order_number }} cancelada - MeStore",
                body_template="""
Hola {{ customer_name }},

❌ Tu orden ha sido cancelada.

📋 INFORMACIÓN DE CANCELACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Número de Orden: #{{ order_number }}
Fecha de Cancelación: {{ cancelled_at }}
Motivo: {{ cancellation_reason }}
Estado del Reembolso: {{ refund_status }}

💰 REEMBOLSO:
{% if refund_status == "processed" %}
✅ Tu reembolso ha sido procesado exitosamente.
Método de devolución: {{ refund_method }}
Monto: ${{ refund_amount | number_format }} COP
Tiempo estimado de acreditación: {{ refund_time_estimate }}
{% else %}
⏳ Tu reembolso será procesado en 3-5 días hábiles.
Te notificaremos por email cuando esté listo.
{% endif %}

🔄 ¿QUIERES HACER OTRO PEDIDO?
Explora nuestros productos disponibles:
{{ marketplace_url }}

💬 ¿NECESITAS AYUDA?
Contáctanos: soporte@mestore.com
WhatsApp: +57 (300) 123-4567

Lamentamos cualquier inconveniente.

Equipo MeStore 🛍️
                """,
                sms_template="MeStore: Orden #{{ order_number }} cancelada. Reembolso procesándose. Info: {{ support_url }}"
            ),
            
            NotificationType.ORDER_REFUNDED: NotificationTemplate(
                type=NotificationType.ORDER_REFUNDED,
                subject_template="💰 Reembolso procesado - Orden #{{ order_number }} - MeStore",
                body_template="""
Hola {{ customer_name }},

💰 Tu reembolso ha sido procesado exitosamente.

💸 DETALLES DEL REEMBOLSO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Número de Orden: #{{ order_number }}
Monto Reembolsado: ${{ refund_amount | number_format }} COP
Fecha de Procesamiento: {{ processed_at }}
Método de Devolución: {{ refund_method }}
ID de Referencia: {{ refund_reference }}

⏰ TIEMPOS DE ACREDITACIÓN:
{% if refund_method == "credit_card" %}
• Tarjeta de Crédito/Débito: 3-7 días hábiles
{% elif refund_method == "pse" %}
• PSE: 1-3 días hábiles
{% elif refund_method == "nequi" %}
• Nequi: Inmediato a 24 horas
{% else %}
• Método seleccionado: 3-7 días hábiles
{% endif %}

📧 COMPROBANTE:
Este email sirve como comprobante oficial de tu reembolso.
Guárdalo para tu referencia.

🔄 ¿CAMBIO DE OPINIÓN?
Si quieres hacer un nuevo pedido:
{{ marketplace_url }}

💬 SOPORTE:
Si no ves el reembolso después del tiempo estimado:
• Email: soporte@mestore.com
• WhatsApp: +57 (300) 123-4567
• Horario: Lun-Sáb 8AM-8PM

Gracias por tu comprensión.

Equipo MeStore 🛍️
                """,
                sms_template="MeStore: Reembolso ${{ refund_amount }} procesado para orden #{{ order_number }}. Acreditación en 3-7 días."
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
    
    # ===== MÉTODOS ESPECÍFICOS PARA ÓRDENES ENTERPRISE =====
    
    async def send_order_status_notification(
        self,
        order: Any,  # Order model instance
        old_status: Any,  # OrderStatus enum
        new_status: Any   # OrderStatus enum
    ) -> bool:
        """
        Envía notificación específica para cambio de estado de orden.
        
        Método optimizado con retry automático y configuración dinámica.
        """
        try:
            # Mapear estados a tipos de notificación
            status_to_notification = {
                "confirmed": NotificationType.ORDER_CONFIRMED,
                "shipped": NotificationType.ORDER_SHIPPED, 
                "delivered": NotificationType.ORDER_DELIVERED,
                "cancelled": NotificationType.ORDER_CANCELLED,
                "refunded": NotificationType.ORDER_REFUNDED
            }
            
            notification_type = status_to_notification.get(new_status.value)
            if not notification_type:
                logger.info(f"No notification template for status: {new_status.value}")
                return True  # No error, just no notification needed
            
            # Preparar datos del template con URLs dinámicas
            template_data = await self._prepare_order_template_data(order, old_status, new_status)
            
            # Obtener información del buyer
            buyer_email = getattr(order.buyer, 'email', None) if hasattr(order, 'buyer') else None
            buyer_phone = getattr(order.buyer, 'telefono', None) if hasattr(order, 'buyer') else None
            
            if not buyer_email:
                logger.warning(f"No email found for order {order.order_number}")
                return False
            
            # Enviar con retry automático
            return await self._send_with_retry(
                notification_type,
                buyer_email,
                buyer_phone,
                template_data
            )
            
        except Exception as e:
            logger.error(
                f"Error sending order notification: {e}",
                extra={
                    "order_id": getattr(order, 'id', None),
                    "order_number": getattr(order, 'order_number', None),
                    "old_status": old_status.value if old_status else None,
                    "new_status": new_status.value if new_status else None
                }
            )
            return False
    
    async def _prepare_order_template_data(
        self, 
        order: Any,
        old_status: Any,
        new_status: Any
    ) -> Dict[str, Any]:
        """Prepara datos del template con configuración dinámica"""
        
        # URLs dinámicas según entorno
        base_url = os.getenv('DEV_FRONTEND_URL', 'http://192.168.1.137:5173')
        if os.getenv('ENVIRONMENT') == 'production':
            base_url = os.getenv('FRONTEND_URL', 'https://tudominio.com')
        
        tracking_url = f"{base_url}/orders/track/{order.order_number}"
        marketplace_url = f"{base_url}/marketplace"
        review_url = f"{base_url}/orders/{order.id}/review"
        referral_link = f"{base_url}/referral/{getattr(order.buyer, 'id', 'user')}"
        support_url = f"{base_url}/support"
        
        # Datos base del template
        template_data = {
            "order_number": order.order_number,
            "order_status": new_status.value.replace('_', ' ').title(),
            "customer_name": getattr(order.buyer, 'nombre', 'Cliente') if hasattr(order, 'buyer') else "Cliente",
            "total_amount": f"{float(order.total_amount):,.0f}",
            "tracking_url": tracking_url,
            "marketplace_url": marketplace_url,
            "review_url": review_url,
            "referral_link": referral_link,
            "support_url": support_url,
            
            # Timestamps formateados
            "confirmed_at": order.confirmed_at.strftime("%d/%m/%Y %H:%M") if order.confirmed_at else None,
            "shipped_at": order.shipped_at.strftime("%d/%m/%Y %H:%M") if order.shipped_at else None,
            "delivered_at": order.delivered_at.strftime("%d/%m/%Y %H:%M") if order.delivered_at else None,
            "cancelled_at": order.updated_at.strftime("%d/%m/%Y %H:%M") if new_status.value == "cancelled" else None,
            "processed_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
        
        # Datos específicos por estado
        if new_status.value == "shipped":
            template_data.update({
                "tracking_number": getattr(order, 'tracking_number', 'En proceso'),
                "carrier": getattr(order, 'carrier', 'Transportadora nacional'),
                "shipping_address": getattr(order, 'shipping_address', 'Dirección registrada'),
                "estimated_delivery_date": self._calculate_delivery_date(),
                "carrier_tracking_url": f"https://tracking.carrier.com/{getattr(order, 'tracking_number', '')}",
                "payment_method": getattr(order, 'payment_method', 'Método registrado')
            })
        
        elif new_status.value == "delivered":
            template_data.update({
                "delivery_address": getattr(order, 'shipping_address', 'Dirección registrada'),
                "received_by": getattr(order, 'received_by', 'Cliente')
            })
        
        elif new_status.value in ["cancelled", "refunded"]:
            template_data.update({
                "cancellation_reason": getattr(order, 'cancellation_reason', 'Cancelación solicitada'),
                "refund_status": "processed" if new_status.value == "refunded" else "processing",
                "refund_method": getattr(order, 'refund_method', 'Método original'),
                "refund_amount": f"{float(getattr(order, 'refund_amount', order.total_amount)):,.0f}",
                "refund_reference": getattr(order, 'refund_reference', f"REF-{order.order_number}"),
                "refund_time_estimate": "3-7 días hábiles"
            })
        
        # Datos generales adicionales
        template_data.update({
            "estimated_delivery_days": self._get_estimated_delivery_days(),
        })
        
        return template_data
    
    async def _send_with_retry(
        self,
        notification_type: NotificationType,
        email: str,
        phone: Optional[str],
        template_data: Dict[str, Any],
        channels: List[NotificationChannel] = [NotificationChannel.EMAIL]
    ) -> bool:
        """Envía notificación con sistema de retry automático"""
        
        for attempt in range(self.retry_attempts):
            try:
                success = await self.send_notification(
                    notification_type,
                    email,
                    phone,
                    template_data,
                    channels
                )
                
                if success:
                    if attempt > 0:
                        logger.info(f"Notification sent successfully on attempt {attempt + 1}")
                    return True
                    
            except Exception as e:
                logger.warning(f"Notification attempt {attempt + 1} failed: {e}")
                
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))  # Backoff exponencial
                else:
                    logger.error(f"All {self.retry_attempts} notification attempts failed")
        
        return False
    
    def _calculate_delivery_date(self) -> str:
        """Calcula fecha estimada de entrega"""
        estimated_date = datetime.now() + timedelta(days=3)  # 3 días por defecto
        return estimated_date.strftime("%d/%m/%Y")
    
    def _get_estimated_delivery_days(self) -> int:
        """Obtiene días estimados de entrega"""
        return 3  # Por defecto 3 días hábiles
    
    # ===== CONFIGURACIÓN DINÁMICA ENTERPRISE =====
    
    def get_notification_config(self) -> Dict[str, str]:
        """
        Retorna configuración dinámica para notificaciones.
        
        TODO_HOSTING: Configurar variables de entorno en producción
        """
        return {
            "environment": os.getenv('ENVIRONMENT', 'development'),
            "frontend_url": os.getenv('DEV_FRONTEND_URL', 'http://192.168.1.137:5173'),
            "api_url": os.getenv('DEV_API_URL', 'http://192.168.1.137:8000'),
            "notification_webhook_url": os.getenv('NOTIFICATION_WEBHOOK_URL', ''),
            "email_provider": os.getenv('EMAIL_PROVIDER', 'sendgrid'),
            "sms_provider": os.getenv('SMS_PROVIDER', 'twilio')
        }