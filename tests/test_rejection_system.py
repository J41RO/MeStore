import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.services.notification_service import NotificationService, NotificationType, NotificationChannel
from app.services.product_verification_workflow import ProductVerificationWorkflow, ProductRejection, RejectionReason
from app.models.incoming_product_queue import IncomingProductQueue
from app.models.user import User
from app.api.v1.endpoints.admin import router


class TestNotificationService:
    """Tests para el servicio de notificaciones"""
    
    def setup_method(self):
        self.notification_service = NotificationService()
    
    def test_notification_service_initialization(self):
        """Test que el servicio se inicializa correctamente"""
        assert self.notification_service is not None
        assert len(self.notification_service.templates) > 0
        assert NotificationType.PRODUCT_REJECTED in self.notification_service.templates
    
    def test_template_structure(self):
        """Test que los templates tienen la estructura correcta"""
        template = self.notification_service.templates[NotificationType.PRODUCT_REJECTED]
        
        assert template.type == NotificationType.PRODUCT_REJECTED
        assert "tracking_number" in template.subject_template
        assert "vendor_name" in template.body_template
        assert template.sms_template is not None
    
    @pytest.mark.asyncio
    async def test_send_notification_email_only(self):
        """Test envío de notificación solo por email"""
        template_data = {
            "vendor_name": "Test Vendor",
            "tracking_number": "TRK001",
            "rejection_reasons": "Calidad insuficiente",
            "quality_score": 3,
            "rejection_summary": "Quality Issues",
            "inspector_notes": "Test notes",
            "appeal_deadline": "2024-01-01 12:00",
            "can_appeal": "Sí"
        }
        
        with patch.object(self.notification_service, '_send_email', return_value=True) as mock_email:
            result = await self.notification_service.send_notification(
                NotificationType.PRODUCT_REJECTED,
                "test@example.com",
                None,
                template_data,
                [NotificationChannel.EMAIL]
            )
            
            assert result is True
            mock_email.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_notification_email_and_sms(self):
        """Test envío de notificación por email y SMS"""
        template_data = {
            "vendor_name": "Test Vendor",
            "tracking_number": "TRK001",
            "rejection_reasons": "Calidad insuficiente",
            "quality_score": 3,
            "rejection_summary": "Quality Issues"
        }
        
        with patch.object(self.notification_service, '_send_email', return_value=True) as mock_email, \
             patch.object(self.notification_service, '_send_sms', return_value=True) as mock_sms:
            
            result = await self.notification_service.send_notification(
                NotificationType.PRODUCT_REJECTED,
                "test@example.com",
                "+1234567890",
                template_data,
                [NotificationChannel.EMAIL, NotificationChannel.SMS]
            )
            
            assert result is True
            mock_email.assert_called_once()
            mock_sms.assert_called_once()
    
    def test_create_appeal_deadline(self):
        """Test creación de deadline de apelación"""
        deadline = self.notification_service.create_appeal_deadline(24)
        
        assert deadline > datetime.now()
        assert deadline <= datetime.now() + timedelta(hours=25)


class TestProductRejection:
    """Tests para la funcionalidad de rechazo de productos"""
    
    def setup_method(self):
        # Mock database session
        self.mock_db = Mock(spec=Session)
        
        # Mock vendor
        self.mock_vendor = Mock()
        self.mock_vendor.email = "vendor@example.com"
        self.mock_vendor.telefono = "+1234567890"
        self.mock_vendor.nombre = "Test Vendor"
        
        # Mock queue item
        self.mock_queue_item = Mock()
        self.mock_queue_item.id = 1
        self.mock_queue_item.tracking_number = "TRK001"
        self.mock_queue_item.vendor = self.mock_vendor
        self.mock_queue_item.verification_status = "IN_PROGRESS"
        self.mock_queue_item.verification_attempts = 0
        
        # Mock workflow
        self.workflow = ProductVerificationWorkflow(self.mock_db, self.mock_queue_item)
    
    def test_rejection_reason_enum(self):
        """Test que los enum de razones de rechazo están definidos"""
        assert RejectionReason.QUALITY_ISSUES == "quality_issues"
        assert RejectionReason.MISSING_DOCUMENTATION == "missing_documentation"
        assert RejectionReason.DAMAGED_PRODUCT == "damaged_product"
        assert RejectionReason.INCORRECT_DIMENSIONS == "incorrect_dimensions"
        assert RejectionReason.COUNTERFEIT_SUSPECTED == "counterfeit_suspected"
        assert RejectionReason.SAFETY_CONCERNS == "safety_concerns"
        assert RejectionReason.OTHER == "other"
    
    def test_product_rejection_model(self):
        """Test que el modelo ProductRejection funciona correctamente"""
        rejection = ProductRejection(
            reason=RejectionReason.QUALITY_ISSUES,
            description="Test rejection",
            quality_score=3,
            inspector_notes="Inspector notes",
            can_appeal=True
        )
        
        assert rejection.reason == RejectionReason.QUALITY_ISSUES
        assert rejection.description == "Test rejection"
        assert rejection.quality_score == 3
        assert rejection.can_appeal is True
    
    @pytest.mark.asyncio
    async def test_reject_product_success(self):
        """Test rechazo exitoso de producto"""
        rejection = ProductRejection(
            reason=RejectionReason.QUALITY_ISSUES,
            description="Producto con defectos",
            quality_score=3,
            inspector_notes="Múltiples defectos encontrados",
            can_appeal=True
        )
        
        with patch.object(self.workflow.notification_service, 'send_notification', return_value=True) as mock_notify:
            result = await self.workflow.reject_product(rejection, "inspector_123")
            
            assert result is True
            assert self.mock_queue_item.verification_status == "REJECTED"
            assert self.mock_queue_item.quality_issues == "quality_issues"
            assert self.mock_queue_item.verification_notes == "Producto con defectos"
            assert self.mock_queue_item.quality_score == 3
            
            mock_notify.assert_called_once()
            self.mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_reject_product_notification_failure(self):
        """Test rechazo con fallo en notificación"""
        rejection = ProductRejection(
            reason=RejectionReason.QUALITY_ISSUES,
            description="Test rejection",
            quality_score=3,
            inspector_notes="Test notes",
            can_appeal=True
        )
        
        with patch.object(self.workflow.notification_service, 'send_notification', return_value=False):
            result = await self.workflow.reject_product(rejection, "inspector_123")
            
            assert result is False
            self.mock_db.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_reject_product_no_vendor(self):
        """Test rechazo sin vendedor asociado"""
        self.mock_queue_item.vendor = None
        
        rejection = ProductRejection(
            reason=RejectionReason.QUALITY_ISSUES,
            description="Test rejection",
            quality_score=3,
            inspector_notes="Test notes",
            can_appeal=True
        )
        
        result = await self.workflow.reject_product(rejection, "inspector_123")
        
        assert result is False
        self.mock_db.rollback.assert_called_once()
    
    def test_format_rejection_reasons(self):
        """Test formateo de razones de rechazo"""
        rejection = ProductRejection(
            reason=RejectionReason.QUALITY_ISSUES,
            description="Producto con defectos múltiples",
            quality_score=3,
            inspector_notes="Test notes",
            can_appeal=True
        )
        
        formatted = self.workflow._format_rejection_reasons(rejection)
        
        assert "Problemas de calidad detectados" in formatted
        assert "Producto con defectos múltiples" in formatted
    
    @pytest.mark.asyncio
    async def test_approve_product_success(self):
        """Test aprobación exitosa de producto"""
        with patch.object(self.workflow.notification_service, 'send_notification', return_value=True):
            result = await self.workflow.approve_product("inspector_123", quality_score=8)
            
            assert result is True
            assert self.mock_queue_item.verification_status == "APPROVED"
            assert self.mock_queue_item.quality_score == 8
            self.mock_db.commit.assert_called_once()


class TestRejectionEndpoints:
    """Tests para los endpoints de rechazo"""
    
    @pytest.fixture
    def client(self):
        from app.main import app
        return TestClient(app)
    
    def test_rejection_endpoint_structure(self):
        """Test que los endpoints de rechazo están definidos"""
        # Verificar que las rutas están registradas
        routes = [route.path for route in router.routes]
        
        expected_routes = [
            "/incoming-products/{queue_id}/verification/reject",
            "/incoming-products/{queue_id}/rejection-history",
            "/rejections/summary",
            "/incoming-products/{queue_id}/verification/approve"
        ]
        
        for expected_route in expected_routes:
            assert any(expected_route in route for route in routes), f"Route {expected_route} not found"


class TestIntegrationRejectionSystem:
    """Tests de integración del sistema completo de rechazo"""
    
    @pytest.mark.asyncio
    async def test_complete_rejection_workflow(self):
        """Test del flujo completo de rechazo"""
        # Mock de todas las dependencias
        mock_db = Mock(spec=Session)
        mock_vendor = Mock()
        mock_vendor.email = "vendor@test.com"
        mock_vendor.telefono = "+1234567890"
        mock_vendor.nombre = "Test Vendor"
        
        mock_queue_item = Mock()
        mock_queue_item.id = 1
        mock_queue_item.tracking_number = "TRK001"
        mock_queue_item.vendor = mock_vendor
        mock_queue_item.verification_status = "IN_PROGRESS"
        mock_queue_item.verification_attempts = 0
        
        # Crear workflow
        workflow = ProductVerificationWorkflow(mock_db, mock_queue_item)
        
        # Crear rechazo
        rejection = ProductRejection(
            reason=RejectionReason.QUALITY_ISSUES,
            description="Producto no cumple estándares de calidad",
            quality_score=2,
            inspector_notes="Defectos múltiples encontrados durante inspección",
            can_appeal=True
        )
        
        # Simular rechazo exitoso
        with patch.object(workflow.notification_service, 'send_notification', return_value=True):
            result = await workflow.reject_product(rejection, "inspector_123")
            
            # Verificaciones
            assert result is True
            assert mock_queue_item.verification_status == "REJECTED"
            assert mock_queue_item.quality_issues == "quality_issues"
            assert mock_queue_item.verification_notes == "Producto no cumple estándares de calidad"
            assert mock_queue_item.quality_score == 2
            
            # Verificar que se incrementaron los intentos
            assert mock_queue_item.verification_attempts == 1
            
            # Verificar que se hizo commit
            mock_db.commit.assert_called_once()
    
    def test_rejection_reasons_coverage(self):
        """Test que todas las razones de rechazo están cubiertas"""
        workflow = ProductVerificationWorkflow(Mock(), Mock())
        
        # Test que todas las razones tienen mapeo
        for reason in RejectionReason:
            test_rejection = ProductRejection(
                reason=reason,
                description="Test description",
                quality_score=5,
                inspector_notes="Test notes",
                can_appeal=True
            )
            
            formatted = workflow._format_rejection_reasons(test_rejection)
            assert formatted is not None
            assert len(formatted) > 0
            assert "Test description" in formatted


class TestRejectionSystemSecurity:
    """Tests de seguridad del sistema de rechazo"""
    
    def test_admin_permission_required(self):
        """Test que se requieren permisos de admin"""
        from app.api.v1.endpoints.admin import get_current_admin_user
        from fastapi import HTTPException
        
        # Usuario sin permisos
        mock_user = Mock()
        mock_user.is_superuser = False
        mock_user.user_type = "VENDOR"
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_admin_user(mock_user)
        
        assert exc_info.value.status_code == 403
    
    def test_admin_permission_allowed(self):
        """Test que usuarios admin pueden acceder"""
        from app.api.v1.endpoints.admin import get_current_admin_user
        
        # Usuario con permisos
        mock_user = Mock()
        mock_user.is_superuser = True
        
        result = get_current_admin_user(mock_user)
        assert result == mock_user


# Configuración de pytest
@pytest.fixture(scope="session")
def event_loop():
    """Crear event loop para tests async"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v", "--tb=short"])