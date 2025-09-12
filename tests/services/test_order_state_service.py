# ~/tests/services/test_order_state_service.py
# Tests para Order State Service Enterprise

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from app.services.order_state_service import (
    OrderStateService, 
    StateTransitionError,
    OrdersConfig
)
from app.models.order import Order, OrderStatus
from app.models.user import User


class TestOrderStateService:
    """Tests para OrderStateService enterprise"""

    @pytest.fixture
    def service(self):
        """Fixture del servicio de estados"""
        return OrderStateService()

    @pytest.fixture
    def mock_order(self):
        """Mock order para testing"""
        order = Mock(spec=Order)
        order.id = 123
        order.order_number = "ORD-2025-001"
        order.status = OrderStatus.PENDING
        order.tracking_number = "TRK123456"
        return order

    @pytest.fixture
    def mock_admin_user(self):
        """Mock admin user para testing"""
        user = Mock(spec=User)
        user.id = "admin-uuid"
        user.user_type = "ADMIN"
        user.email = "admin@mestore.com"
        return user

    @pytest.fixture
    def mock_regular_user(self):
        """Mock regular user para testing"""
        user = Mock(spec=User)
        user.id = "user-uuid"
        user.user_type = "BUYER"
        user.email = "buyer@mestore.com"
        return user

    def test_valid_transitions_setup(self, service):
        """Test que las transiciones válidas estén configuradas correctamente"""
        # Verificar estados iniciales
        assert OrderStatus.CONFIRMED in service.VALID_TRANSITIONS[OrderStatus.PENDING]
        assert OrderStatus.CANCELLED in service.VALID_TRANSITIONS[OrderStatus.PENDING]
        
        # Verificar estados finales
        assert service.VALID_TRANSITIONS[OrderStatus.CANCELLED] == []
        assert service.VALID_TRANSITIONS[OrderStatus.REFUNDED] == []

    def test_get_valid_transitions(self, service):
        """Test obtener transiciones válidas para un estado"""
        transitions = service.get_valid_transitions(OrderStatus.PENDING)
        assert OrderStatus.CONFIRMED in transitions
        assert OrderStatus.CANCELLED in transitions
        assert len(transitions) == 2

    def test_can_user_transition_to_admin_only(self, service, mock_admin_user, mock_regular_user):
        """Test permisos de usuario para transiciones admin-only"""
        # Admin puede hacer refunds
        assert service.can_user_transition_to(mock_admin_user, OrderStatus.REFUNDED)
        
        # Usuario regular no puede hacer refunds
        assert not service.can_user_transition_to(mock_regular_user, OrderStatus.REFUNDED)

    def test_can_user_transition_to_regular_states(self, service, mock_regular_user):
        """Test que usuarios regulares pueden hacer transiciones normales"""
        assert service.can_user_transition_to(mock_regular_user, OrderStatus.CONFIRMED)
        assert service.can_user_transition_to(mock_regular_user, OrderStatus.SHIPPED)

    @pytest.mark.asyncio
    async def test_validate_transition_success(self, service, mock_order, mock_admin_user):
        """Test validación exitosa de transición"""
        # No debe lanzar excepción para transición válida
        await service._validate_transition(mock_order, OrderStatus.CONFIRMED, mock_admin_user)

    @pytest.mark.asyncio 
    async def test_validate_transition_invalid_state(self, service, mock_order, mock_admin_user):
        """Test validación falla para estado inválido"""
        # Intentar pasar de PENDING directamente a DELIVERED (inválido)
        with pytest.raises(StateTransitionError) as exc_info:
            await service._validate_transition(mock_order, OrderStatus.DELIVERED, mock_admin_user)
        
        assert "Transición inválida" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_transition_permission_denied(self, service, mock_order, mock_regular_user):
        """Test validación falla por permisos insuficientes"""
        # Cambiar el estado de la orden para que REFUNDED sea una transición válida
        mock_order.status = OrderStatus.DELIVERED
        
        with pytest.raises(PermissionError) as exc_info:
            await service._validate_transition(mock_order, OrderStatus.REFUNDED, mock_regular_user)
        
        assert "Solo administradores" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_specific_state_shipped_without_tracking(self, service, mock_order, mock_admin_user):
        """Test validación específica para SHIPPED sin tracking"""
        mock_order.tracking_number = None
        mock_order.status = OrderStatus.CONFIRMED
        
        with pytest.raises(StateTransitionError) as exc_info:
            await service._validate_specific_state(mock_order, OrderStatus.SHIPPED, mock_admin_user)
        
        assert "sin número de tracking" in str(exc_info.value)

    def test_orders_config_development(self):
        """Test configuración en ambiente development"""
        import os
        os.environ['ENVIRONMENT'] = 'development'
        os.environ['DEV_FRONTEND_URL'] = 'http://localhost:3000'
        
        config = OrdersConfig()
        assert config.ENVIRONMENT == 'development'
        assert 'localhost' in config.EMAIL_BASE_URL

    def test_orders_config_production(self):
        """Test configuración en ambiente production"""
        import os
        os.environ['ENVIRONMENT'] = 'production'
        os.environ['FRONTEND_URL'] = 'https://myapp.com'
        
        config = OrdersConfig()
        assert config.ENVIRONMENT == 'production'
        assert config.EMAIL_BASE_URL == 'https://myapp.com'


class TestOrderStateServiceIntegration:
    """Tests de integración para OrderStateService"""

    @pytest.mark.asyncio
    async def test_get_order_timeline_complete(self):
        """Test timeline completa de orden"""
        service = OrderStateService()
        
        # Mock order con timestamps
        mock_order = Mock(spec=Order)
        mock_order.id = 1
        mock_order.status = OrderStatus.DELIVERED
        mock_order.created_at = datetime(2025, 1, 1, 10, 0)
        mock_order.confirmed_at = datetime(2025, 1, 1, 11, 0)
        mock_order.shipped_at = datetime(2025, 1, 2, 9, 0)
        mock_order.delivered_at = datetime(2025, 1, 3, 14, 0)
        
        # Mock db session
        mock_db = AsyncMock()
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = mock_order
        mock_db.execute.return_value = mock_result
        
        timeline = await service.get_order_timeline(mock_db, 1)
        
        # Verificar eventos de timeline (processing no tiene timestamp específico, solo si está en ese estado)
        assert len(timeline) == 4  # created, confirmed, shipped, delivered
        
        # Verificar orden cronológico
        events = [event["status"] for event in timeline]
        expected_events = ["created", "confirmed", "shipped", "delivered"]
        assert events == expected_events
        
        # Verificar timestamps
        assert timeline[0]["timestamp"] == mock_order.created_at
        assert timeline[1]["timestamp"] == mock_order.confirmed_at
        assert timeline[2]["timestamp"] == mock_order.shipped_at
        assert timeline[3]["timestamp"] == mock_order.delivered_at

    @pytest.mark.asyncio
    async def test_get_order_timeline_cancelled(self):
        """Test timeline de orden cancelada"""
        service = OrderStateService()
        
        mock_order = Mock(spec=Order)
        mock_order.id = 1
        mock_order.status = OrderStatus.CANCELLED
        mock_order.created_at = datetime(2025, 1, 1, 10, 0)
        mock_order.confirmed_at = None
        mock_order.shipped_at = None
        mock_order.delivered_at = None
        mock_order.updated_at = datetime(2025, 1, 1, 12, 0)
        
        mock_db = AsyncMock()
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = mock_order
        mock_db.execute.return_value = mock_result
        
        timeline = await service.get_order_timeline(mock_db, 1)
        
        # Debe incluir evento de cancelación
        cancel_events = [e for e in timeline if e["status"] == "cancelled"]
        assert len(cancel_events) == 1
        assert cancel_events[0]["is_current"] is True


def test_order_state_service_importable():
    """Test que el servicio sea importable correctamente"""
    from app.services.order_state_service import order_state_service
    assert order_state_service is not None
    print("✅ OrderStateService importable y funcional")