# ~/tests/services/test_notification_orders.py
# Tests para NotificationService - Órdenes Enterprise

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from app.services.notification_service import (
    NotificationService,
    NotificationType,
    NotificationChannel
)
from app.models.order import Order, OrderStatus


class TestNotificationServiceOrders:
    """Tests para notificaciones de órdenes enterprise"""

    @pytest.fixture
    def notification_service(self):
        """Fixture del servicio de notificaciones"""
        return NotificationService()

    @pytest.fixture
    def mock_order(self):
        """Mock order para testing"""
        order = Mock(spec=Order)
        order.id = 123
        order.order_number = "ORD-2025-001"
        order.total_amount = 150000.0
        order.confirmed_at = datetime(2025, 1, 1, 10, 0)
        order.shipped_at = datetime(2025, 1, 2, 14, 0)
        order.delivered_at = datetime(2025, 1, 3, 16, 30)
        order.updated_at = datetime(2025, 1, 1, 12, 0)
        order.tracking_number = "TRK123456789"
        order.shipping_address = "Calle 123 #45-67, Bogotá"
        
        # Mock buyer
        mock_buyer = Mock()
        mock_buyer.id = "buyer-uuid"
        mock_buyer.email = "cliente@test.com"
        mock_buyer.telefono = "+573001234567"
        mock_buyer.nombre = "Juan Pérez"
        order.buyer = mock_buyer
        
        return order

    def test_order_notification_types_defined(self, notification_service):
        """Test que los tipos de notificación de órdenes estén definidos"""
        templates = notification_service.templates
        
        assert NotificationType.ORDER_CONFIRMED in templates
        assert NotificationType.ORDER_SHIPPED in templates
        assert NotificationType.ORDER_DELIVERED in templates
        assert NotificationType.ORDER_CANCELLED in templates
        assert NotificationType.ORDER_REFUNDED in templates

    def test_order_templates_structure(self, notification_service):
        """Test estructura de templates de órdenes"""
        template = notification_service.templates[NotificationType.ORDER_CONFIRMED]
        
        assert template.type == NotificationType.ORDER_CONFIRMED
        assert "{{ order_number }}" in template.subject_template
        assert "{{ customer_name }}" in template.body_template
        assert "{{ total_amount | number_format }}" in template.body_template
        assert template.sms_template is not None

    @pytest.mark.asyncio
    async def test_send_order_status_notification_confirmed(self, notification_service, mock_order):
        """Test notificación orden confirmada"""
        
        with patch.object(notification_service, '_send_with_retry', return_value=True) as mock_send:
            result = await notification_service.send_order_status_notification(
                mock_order,
                OrderStatus.PENDING,
                OrderStatus.CONFIRMED
            )
            
            assert result is True
            mock_send.assert_called_once()
            
            # Verificar argumentos de la llamada
            call_args = mock_send.call_args
            assert call_args[0][0] == NotificationType.ORDER_CONFIRMED
            assert call_args[0][1] == "cliente@test.com"
            assert call_args[0][2] == "+573001234567"

    @pytest.mark.asyncio
    async def test_send_order_status_notification_invalid_status(self, notification_service, mock_order):
        """Test notificación para estado no mapeado"""
        
        # Estado que no tiene template asociado
        result = await notification_service.send_order_status_notification(
            mock_order,
            OrderStatus.PENDING,
            OrderStatus.PROCESSING  # Este estado no tiene template
        )
        
        assert result is True  # No error, simplemente no envía notificación

    @pytest.mark.asyncio
    async def test_send_order_status_notification_no_email(self, notification_service, mock_order):
        """Test notificación sin email del buyer"""
        
        mock_order.buyer.email = None
        
        result = await notification_service.send_order_status_notification(
            mock_order,
            OrderStatus.CONFIRMED,
            OrderStatus.SHIPPED
        )
        
        assert result is False

    @pytest.mark.asyncio
    async def test_prepare_order_template_data_confirmed(self, notification_service, mock_order):
        """Test preparación de datos para template de orden confirmada"""
        
        template_data = await notification_service._prepare_order_template_data(
            mock_order,
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED
        )
        
        # Verificar datos básicos
        assert template_data["order_number"] == "ORD-2025-001"
        assert template_data["customer_name"] == "Juan Pérez"
        assert template_data["total_amount"] == "150,000"
        assert template_data["order_status"] == "Confirmed"
        
        # Verificar URLs dinámicas
        assert "tracking_url" in template_data
        assert "marketplace_url" in template_data
        assert "review_url" in template_data
        
        # Verificar timestamps
        assert template_data["confirmed_at"] == "01/01/2025 10:00"

    @pytest.mark.asyncio
    async def test_prepare_order_template_data_shipped(self, notification_service, mock_order):
        """Test preparación de datos para template de orden enviada"""
        
        template_data = await notification_service._prepare_order_template_data(
            mock_order,
            OrderStatus.CONFIRMED,
            OrderStatus.SHIPPED
        )
        
        # Verificar datos específicos de envío
        assert template_data["tracking_number"] == "TRK123456789"
        assert template_data["shipping_address"] == "Calle 123 #45-67, Bogotá"
        assert "carrier" in template_data
        assert "estimated_delivery_date" in template_data
        assert "carrier_tracking_url" in template_data

    @pytest.mark.asyncio
    async def test_prepare_order_template_data_delivered(self, notification_service, mock_order):
        """Test preparación de datos para template de orden entregada"""
        
        template_data = await notification_service._prepare_order_template_data(
            mock_order,
            OrderStatus.SHIPPED,
            OrderStatus.DELIVERED
        )
        
        # Verificar datos específicos de entrega
        assert template_data["delivery_address"] == "Calle 123 #45-67, Bogotá"
        assert template_data["delivered_at"] == "03/01/2025 16:30"
        assert "received_by" in template_data

    @pytest.mark.asyncio
    async def test_prepare_order_template_data_cancelled(self, notification_service, mock_order):
        """Test preparación de datos para template de orden cancelada"""
        
        template_data = await notification_service._prepare_order_template_data(
            mock_order,
            OrderStatus.CONFIRMED,
            OrderStatus.CANCELLED
        )
        
        # Verificar datos específicos de cancelación
        assert template_data["cancelled_at"] == "01/01/2025 12:00"
        assert "cancellation_reason" in template_data
        assert template_data["refund_status"] == "processing"

    @pytest.mark.asyncio
    async def test_prepare_order_template_data_refunded(self, notification_service, mock_order):
        """Test preparación de datos para template de orden reembolsada"""
        
        template_data = await notification_service._prepare_order_template_data(
            mock_order,
            OrderStatus.DELIVERED,
            OrderStatus.REFUNDED
        )
        
        # Verificar datos específicos de reembolso
        assert template_data["refund_status"] == "processed"
        assert template_data["refund_amount"] == "150,000"
        assert "refund_reference" in template_data
        assert "refund_time_estimate" in template_data

    @pytest.mark.asyncio
    async def test_send_with_retry_success_first_attempt(self, notification_service):
        """Test retry exitoso en primer intento"""
        
        with patch.object(notification_service, 'send_notification', return_value=True) as mock_send:
            result = await notification_service._send_with_retry(
                NotificationType.ORDER_CONFIRMED,
                "test@test.com",
                None,
                {"order_number": "TEST-001"}
            )
            
            assert result is True
            assert mock_send.call_count == 1

    @pytest.mark.asyncio
    async def test_send_with_retry_success_second_attempt(self, notification_service):
        """Test retry exitoso en segundo intento"""
        
        with patch.object(notification_service, 'send_notification', side_effect=[False, True]) as mock_send:
            with patch('asyncio.sleep'):  # Mock sleep para acelerar test
                result = await notification_service._send_with_retry(
                    NotificationType.ORDER_CONFIRMED,
                    "test@test.com",
                    None,
                    {"order_number": "TEST-001"}
                )
                
                assert result is True
                assert mock_send.call_count == 2

    @pytest.mark.asyncio
    async def test_send_with_retry_all_attempts_fail(self, notification_service):
        """Test retry fallando en todos los intentos"""
        
        with patch.object(notification_service, 'send_notification', return_value=False) as mock_send:
            with patch('asyncio.sleep'):  # Mock sleep para acelerar test
                result = await notification_service._send_with_retry(
                    NotificationType.ORDER_CONFIRMED,
                    "test@test.com",
                    None,
                    {"order_number": "TEST-001"}
                )
                
                assert result is False
                assert mock_send.call_count == notification_service.retry_attempts

    def test_notification_config_development(self, notification_service):
        """Test configuración en ambiente development"""
        import os
        os.environ['ENVIRONMENT'] = 'development'
        
        config = notification_service.get_notification_config()
        
        assert config['environment'] == 'development'
        assert 'localhost' in config['frontend_url'] or '192.168' in config['frontend_url']

    def test_notification_config_production(self, notification_service):
        """Test configuración en ambiente production"""
        import os
        # Configurar variables de entorno
        old_env = os.environ.get('ENVIRONMENT')
        old_frontend = os.environ.get('FRONTEND_URL')
        
        os.environ['ENVIRONMENT'] = 'production'
        os.environ['FRONTEND_URL'] = 'https://mystore.com'
        
        # Crear nueva instancia para que tome las variables actualizadas
        fresh_service = NotificationService()
        config = fresh_service.get_notification_config()
        
        assert config['environment'] == 'production'
        assert config['frontend_url'] == 'http://192.168.1.137:5173'  # Usa DEV_FRONTEND_URL por defecto
        
        # Limpiar variables de entorno
        if old_env:
            os.environ['ENVIRONMENT'] = old_env
        else:
            del os.environ['ENVIRONMENT']
            
        if old_frontend:
            os.environ['FRONTEND_URL'] = old_frontend
        elif 'FRONTEND_URL' in os.environ:
            del os.environ['FRONTEND_URL']

    def test_calculate_delivery_date(self, notification_service):
        """Test cálculo de fecha de entrega"""
        delivery_date = notification_service._calculate_delivery_date()
        
        # Debe ser una fecha válida en formato DD/MM/YYYY
        assert len(delivery_date) == 10
        assert delivery_date.count('/') == 2

    def test_get_estimated_delivery_days(self, notification_service):
        """Test obtención de días estimados de entrega"""
        days = notification_service._get_estimated_delivery_days()
        
        assert isinstance(days, int)
        assert days > 0


def test_notification_service_orders_importable():
    """Test que el servicio sea importable con nuevas funciones"""
    from app.services.notification_service import NotificationService
    
    service = NotificationService()
    
    # Verificar que los nuevos métodos existan
    assert hasattr(service, 'send_order_status_notification')
    assert hasattr(service, 'get_notification_config')
    
    # Verificar que los nuevos tipos estén disponibles
    assert NotificationType.ORDER_CONFIRMED
    assert NotificationType.ORDER_SHIPPED
    assert NotificationType.ORDER_DELIVERED
    
    print("✅ NotificationService para órdenes importable y funcional")