# ~/tests/services/test_order_tracking_service.py
# Tests para OrderTrackingService Enterprise

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta

from app.services.order_tracking_service import (
    OrderTrackingService,
    TrackingEventType,
    TrackingEvent,
    TrackingConfig
)
from app.models.order import Order, OrderStatus


class TestOrderTrackingService:
    """Tests para OrderTrackingService enterprise"""

    @pytest.fixture
    def tracking_service(self):
        """Fixture del servicio de tracking"""
        return OrderTrackingService()

    @pytest.fixture
    def mock_order(self):
        """Mock order para testing"""
        order = Mock(spec=Order)
        order.id = 123
        order.order_number = "ORD-2025-001"
        order.status = OrderStatus.SHIPPED
        order.total_amount = 150000.0
        order.created_at = datetime(2025, 1, 1, 10, 0)
        order.confirmed_at = datetime(2025, 1, 1, 11, 0)
        order.shipped_at = datetime(2025, 1, 2, 14, 0)
        order.delivered_at = None
        order.updated_at = datetime(2025, 1, 2, 14, 30)
        
        # Shipping info
        order.shipping_name = "Juan Pérez"
        order.shipping_address = "Calle 123 #45-67, Bogotá"
        order.tracking_number = "TRK123456789"
        
        # Mock buyer
        mock_buyer = Mock()
        mock_buyer.id = "buyer-uuid"
        mock_buyer.email = "cliente@test.com"
        order.buyer = mock_buyer
        
        # Mock items
        order.items = [Mock(), Mock()]  # 2 items de ejemplo
        
        return order

    def test_tracking_config_initialization(self, tracking_service):
        """Test inicialización de configuración de tracking"""
        config = tracking_service.config
        
        assert isinstance(config, TrackingConfig)
        assert config.ENVIRONMENT in ['development', 'production']
        assert config.TRACKING_PUBLIC_URL is not None

    @pytest.mark.asyncio
    async def test_generate_tracking_events_complete_flow(self, tracking_service, mock_order):
        """Test generación completa de eventos de tracking"""
        
        events = await tracking_service._generate_tracking_events(mock_order)
        
        # Verificar que se generan todos los eventos esperados
        event_types = [event.event_type for event in events]
        
        assert TrackingEventType.ORDER_CREATED in event_types
        assert TrackingEventType.ORDER_CONFIRMED in event_types
        assert TrackingEventType.PROCESSING_STARTED in event_types
        assert TrackingEventType.SHIPPED in event_types
        
        # Verificar orden cronológico
        timestamps = [event.timestamp for event in events]
        assert timestamps == sorted(timestamps)
        
        # Verificar información específica
        created_event = next(e for e in events if e.event_type == TrackingEventType.ORDER_CREATED)
        assert created_event.timestamp == mock_order.created_at
        assert "ORD-2025-001" in created_event.description

    @pytest.mark.asyncio
    async def test_generate_tracking_events_delivered_order(self, tracking_service, mock_order):
        """Test eventos para orden entregada"""
        
        mock_order.status = OrderStatus.DELIVERED
        mock_order.delivered_at = datetime(2025, 1, 3, 16, 30)
        
        events = await tracking_service._generate_tracking_events(mock_order)
        
        # Debe incluir evento de entrega
        delivered_events = [e for e in events if e.event_type == TrackingEventType.DELIVERED]
        assert len(delivered_events) == 1
        
        delivered_event = delivered_events[0]
        assert delivered_event.timestamp == mock_order.delivered_at
        assert "entregado exitosamente" in delivered_event.description

    @pytest.mark.asyncio
    async def test_generate_tracking_events_cancelled_order(self, tracking_service, mock_order):
        """Test eventos para orden cancelada"""
        
        mock_order.status = OrderStatus.CANCELLED
        
        events = await tracking_service._generate_tracking_events(mock_order)
        
        # Debe incluir evento de cancelación
        cancelled_events = [e for e in events if e.event_type == TrackingEventType.CANCELLED]
        assert len(cancelled_events) == 1
        
        cancelled_event = cancelled_events[0]
        assert cancelled_event.timestamp == mock_order.updated_at

    def test_generate_transit_events(self, tracking_service, mock_order):
        """Test generación de eventos de tránsito"""
        
        transit_events = tracking_service._generate_transit_events(mock_order)
        
        assert len(transit_events) >= 1
        
        # Verificar que son eventos estimados
        for event in transit_events:
            assert event.is_estimated is True
        
        # Verificar tipos de eventos
        event_types = [event.event_type for event in transit_events]
        assert TrackingEventType.IN_TRANSIT in event_types

    @pytest.mark.asyncio
    async def test_calculate_delivery_estimate_delivered(self, tracking_service, mock_order):
        """Test estimación para orden ya entregada"""
        
        mock_order.delivered_at = datetime(2025, 1, 3, 16, 30)
        
        estimate = await tracking_service._calculate_delivery_estimate(mock_order)
        
        assert estimate["status"] == "delivered"
        assert "delivered_at" in estimate
        assert estimate["delivery_date"] == "03/01/2025"

    @pytest.mark.asyncio
    async def test_calculate_delivery_estimate_pending(self, tracking_service, mock_order):
        """Test estimación para orden pendiente"""
        
        mock_order.status = OrderStatus.PENDING
        mock_order.delivered_at = None
        
        estimate = await tracking_service._calculate_delivery_estimate(mock_order)
        
        assert estimate["status"] == "estimated"
        assert "estimated_date" in estimate
        assert "estimated_range" in estimate
        assert "confidence" in estimate

    @pytest.mark.asyncio
    async def test_calculate_delivery_estimate_shipped(self, tracking_service, mock_order):
        """Test estimación para orden enviada"""
        
        mock_order.status = OrderStatus.SHIPPED
        mock_order.delivered_at = None
        
        estimate = await tracking_service._calculate_delivery_estimate(mock_order)
        
        assert estimate["status"] == "estimated"
        assert "confidence" in estimate
        # Confianza alta para órdenes ya enviadas
        assert estimate["confidence"] == "high"

    @pytest.mark.asyncio
    async def test_get_carrier_info(self, tracking_service, mock_order):
        """Test información de transportadora"""
        
        carrier_info = await tracking_service._get_carrier_info(mock_order)
        
        assert carrier_info is not None
        assert carrier_info["tracking_number"] == "TRK123456789"
        assert "contact" in carrier_info
        assert "phone" in carrier_info["contact"]

    @pytest.mark.asyncio
    async def test_get_carrier_info_no_tracking(self, tracking_service, mock_order):
        """Test información de transportadora sin tracking number"""
        
        mock_order.tracking_number = None
        
        carrier_info = await tracking_service._get_carrier_info(mock_order)
        
        assert carrier_info is None

    def test_get_current_location(self, tracking_service):
        """Test obtención de ubicación actual"""
        
        events = [
            TrackingEvent(
                event_type=TrackingEventType.ORDER_CREATED,
                timestamp=datetime.now() - timedelta(days=2),
                location="MeStore - Plataforma",
                is_estimated=False
            ),
            TrackingEvent(
                event_type=TrackingEventType.IN_TRANSIT,
                timestamp=datetime.now() - timedelta(hours=6),
                location="Centro de Distribución",
                is_estimated=True
            ),
            TrackingEvent(
                event_type=TrackingEventType.SHIPPED,
                timestamp=datetime.now() - timedelta(days=1),
                location="Centro de Despacho",
                is_estimated=False
            )
        ]
        
        location = tracking_service._get_current_location(events)
        
        # Debe retornar la ubicación del último evento no estimado
        assert location == "Centro de Despacho"

    def test_format_tracking_event(self, tracking_service):
        """Test formateo de evento de tracking"""
        
        event = TrackingEvent(
            event_type=TrackingEventType.SHIPPED,
            timestamp=datetime(2025, 1, 2, 14, 0),
            location="Centro de Despacho",
            description="Paquete enviado",
            is_estimated=False,
            metadata={"tracking_number": "TRK123"}
        )
        
        formatted = tracking_service._format_tracking_event(event)
        
        assert formatted["type"] == "shipped"
        assert formatted["date"] == "02/01/2025"
        assert formatted["time"] == "14:00"
        assert formatted["location"] == "Centro de Despacho"
        assert formatted["is_estimated"] is False
        assert formatted["metadata"]["tracking_number"] == "TRK123"

    def test_generate_public_token(self, tracking_service, mock_order):
        """Test generación de token público"""
        
        token = tracking_service._generate_public_token(mock_order)
        
        assert isinstance(token, str)
        assert len(token) == 12  # MD5 truncado
        
        # El mismo input debe generar el mismo token
        token2 = tracking_service._generate_public_token(mock_order)
        assert token == token2

    def test_validate_public_token(self, tracking_service, mock_order):
        """Test validación de token público"""
        
        valid_token = tracking_service._generate_public_token(mock_order)
        invalid_token = "invalid_token"
        
        assert tracking_service._validate_public_token(mock_order, valid_token) is True
        assert tracking_service._validate_public_token(mock_order, invalid_token) is False

    def test_generate_tracking_id(self, tracking_service, mock_order):
        """Test generación de ID de tracking"""
        
        tracking_id = tracking_service._generate_tracking_id(mock_order)
        
        expected = f"TRK-{mock_order.order_number}-{mock_order.id}"
        assert tracking_id == expected

    def test_get_carrier_tracking_url(self, tracking_service, mock_order):
        """Test URL de tracking de transportadora"""
        
        url = tracking_service._get_carrier_tracking_url(mock_order)
        
        assert url is not None
        assert mock_order.tracking_number in url
        assert "tracking" in url.lower()

    def test_get_carrier_tracking_url_no_tracking(self, tracking_service, mock_order):
        """Test URL de tracking sin número de tracking"""
        
        mock_order.tracking_number = None
        
        url = tracking_service._get_carrier_tracking_url(mock_order)
        
        assert url is None

    @pytest.mark.asyncio
    async def test_get_order_tracking_info(self, tracking_service, mock_order):
        """Test obtención completa de información de tracking"""
        
        # Mock db session
        mock_db = AsyncMock()
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = mock_order
        mock_db.execute.return_value = mock_result
        
        tracking_info = await tracking_service.get_order_tracking_info(mock_db, "ORD-2025-001")
        
        # Verificar estructura completa
        assert tracking_info["order_number"] == "ORD-2025-001"
        assert tracking_info["status"] == OrderStatus.SHIPPED.value
        assert "current_location" in tracking_info
        assert "estimated_delivery" in tracking_info
        assert "tracking_events" in tracking_info
        assert "carrier_info" in tracking_info
        assert "delivery_address" in tracking_info
        assert "order_summary" in tracking_info
        assert "tracking_urls" in tracking_info
        assert "metadata" in tracking_info

    @pytest.mark.asyncio
    async def test_get_order_tracking_info_not_found(self, tracking_service):
        """Test tracking para orden no encontrada"""
        
        mock_db = AsyncMock()
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute.return_value = mock_result
        
        with pytest.raises(ValueError) as exc_info:
            await tracking_service.get_order_tracking_info(mock_db, "NONEXISTENT")
        
        assert "no encontrada" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_public_tracking(self, tracking_service, mock_order):
        """Test tracking público con información filtrada"""
        
        mock_db = AsyncMock()
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = mock_order
        mock_db.execute.return_value = mock_result
        
        # Mock get_order_tracking_info
        with patch.object(tracking_service, 'get_order_tracking_info') as mock_get_info:
            mock_get_info.return_value = {
                "order_number": "ORD-2025-001",
                "status": "shipped",
                "current_location": "En tránsito",
                "estimated_delivery": {"status": "estimated"},
                "tracking_events": [{"type": "shipped", "date": "02/01/2025", "time": "14:00", "location": "Centro de Despacho", "description": "Paquete enviado", "is_estimated": False}],
                "delivery_address": {
                    "name": "Juan Pérez",
                    "address": "Calle secreta 123",
                    "city": "Bogotá",
                    "phone": "1234567890"
                },
                "tracking_urls": {"public_url": "https://track.com/123"},
                "metadata": {"last_sync": "2025-01-02T10:00:00"}
            }
            
            public_info = await tracking_service.get_public_tracking(mock_db, "ORD-2025-001")
            
            # Verificar que información sensible esté filtrada
            assert public_info["order_number"] == "ORD-2025-001"
            assert "delivery_address" in public_info
            assert public_info["delivery_address"]["city"] == "Bogotá"
            
            # Información sensible debe estar oculta
            assert "address" not in public_info["delivery_address"]
            assert "phone" not in public_info["delivery_address"]
            assert "name" not in public_info["delivery_address"]

    def test_get_tracking_config(self, tracking_service):
        """Test configuración de tracking"""
        
        config = tracking_service.get_tracking_config()
        
        assert "environment" in config
        assert "tracking_public_url" in config
        assert "cache_ttl" in config
        
        assert config["environment"] in ["development", "production"]


def test_order_tracking_service_importable():
    """Test que el servicio sea importable correctamente"""
    from app.services.order_tracking_service import order_tracking_service
    
    assert order_tracking_service is not None
    assert hasattr(order_tracking_service, 'get_order_tracking_info')
    assert hasattr(order_tracking_service, 'get_public_tracking')
    assert hasattr(order_tracking_service, 'get_tracking_config')
    
    print("✅ OrderTrackingService importable y funcional")