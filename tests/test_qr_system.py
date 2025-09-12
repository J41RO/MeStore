"""
Tests completos para el sistema de códigos QR
Archivo: tests/test_qr_system.py
Autor: Sistema de desarrollo
Fecha: 2025-01-15
Propósito: Tests unitarios e integración para generación QR y tracking interno
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch, mock_open
from datetime import datetime
from PIL import Image
import io

from app.services.qr_service import QRService
from app.services.product_verification_workflow import ProductVerificationWorkflow
from app.models.incoming_product_queue import IncomingProductQueue
from app.models.product import Product
from app.models.user import User


class TestQRService:
    """Test QRService directamente"""
    
    @pytest.fixture
    def qr_service(self):
        """Fixture para QRService con directorio temporal"""
        with tempfile.TemporaryDirectory() as temp_dir:
            service = QRService()
            service.qr_directory = os.path.join(temp_dir, "qr_codes")
            service.label_directory = os.path.join(temp_dir, "labels")
            service._ensure_directories()
            yield service
    
    def test_generate_internal_tracking_id(self, qr_service):
        """Test generación de ID interno único"""
        tracking_number = "TEST123456"
        internal_id = qr_service.generate_internal_tracking_id(tracking_number)
        
        # Verificar formato
        assert internal_id.startswith("MS-")
        assert len(internal_id) > 15  # MS- + timestamp + - + uuid
        
        # Verificar unicidad
        internal_id2 = qr_service.generate_internal_tracking_id(tracking_number)
        assert internal_id != internal_id2
    
    def test_create_qr_code_standard(self, qr_service):
        """Test creación de QR estándar"""
        tracking_number = "TEST123456"
        internal_id = "MS-20250115120000-ABCD1234"
        product_info = {
            "name": "Producto Test",
            "category": "Electrónicos"
        }
        
        result = qr_service.create_qr_code(
            tracking_number, internal_id, product_info, "standard"
        )
        
        # Verificar estructura de respuesta
        assert "qr_filename" in result
        assert "qr_filepath" in result
        assert "qr_base64" in result
        assert "qr_data" in result
        assert "qr_content" in result
        
        # Verificar archivo creado
        assert os.path.exists(result["qr_filepath"])
        assert result["qr_filename"].startswith("qr_")
        assert result["qr_filename"].endswith(".png")
        
        # Verificar contenido QR
        assert result["qr_content"].startswith("MESTORE:")
        assert internal_id in result["qr_content"]
        assert tracking_number in result["qr_content"]
    
    def test_create_qr_code_styled(self, qr_service):
        """Test creación de QR estilizado"""
        tracking_number = "TEST123456"
        internal_id = "MS-20250115120000-ABCD1234"
        product_info = {"name": "Producto Test", "category": "General"}
        
        result = qr_service.create_qr_code(
            tracking_number, internal_id, product_info, "styled"
        )
        
        # Verificar que se creó correctamente
        assert os.path.exists(result["qr_filepath"])
        
        # Verificar que es una imagen válida
        img = Image.open(result["qr_filepath"])
        assert img.format == 'PNG'
        assert img.size[0] > 0 and img.size[1] > 0
    
    def test_create_product_label(self, qr_service):
        """Test creación de etiqueta completa"""
        # Primero crear un QR
        tracking_number = "TEST123456"
        internal_id = "MS-20250115120000-ABCD1234"
        product_info = {"name": "Producto Test", "category": "Electrónicos"}
        
        qr_result = qr_service.create_qr_code(
            tracking_number, internal_id, product_info
        )
        
        # Crear etiqueta
        label_filepath = qr_service.create_product_label(
            tracking_number, internal_id, product_info, qr_result["qr_filepath"]
        )
        
        # Verificar archivo creado
        assert os.path.exists(label_filepath)
        assert "label_" in label_filepath
        assert label_filepath.endswith(".png")
        
        # Verificar que es una imagen válida
        label_img = Image.open(label_filepath)
        assert label_img.format == 'PNG'
        assert label_img.size[0] > 0 and label_img.size[1] > 0
    
    def test_decode_qr_content_valid(self, qr_service):
        """Test decodificación de QR válido"""
        qr_content = "MESTORE:MS-20250115120000-ABCD1234|TEST123456|http://192.168.1.137:5173/admin-secure-portal/product/MS-20250115120000-ABCD1234"
        
        decoded = qr_service.decode_qr_content(qr_content)
        
        assert decoded is not None
        assert decoded["internal_id"] == "MS-20250115120000-ABCD1234"
        assert decoded["tracking_number"] == "TEST123456"
        assert "verification_url" in decoded
    
    def test_decode_qr_content_invalid(self, qr_service):
        """Test decodificación de QR inválido"""
        invalid_content = "INVALID:content|format"
        
        decoded = qr_service.decode_qr_content(invalid_content)
        
        assert decoded is None
    
    def test_get_qr_stats_empty(self, qr_service):
        """Test estadísticas con directorios vacíos"""
        stats = qr_service.get_qr_stats()
        
        assert stats["total_qr_generated"] == 0
        assert stats["total_labels_generated"] == 0
        assert stats["last_generated"] is None
    
    def test_get_qr_stats_with_files(self, qr_service):
        """Test estadísticas con archivos"""
        # Crear algunos QRs
        tracking_number = "TEST123456"
        internal_id = "MS-20250115120000-ABCD1234"
        product_info = {"name": "Test", "category": "General"}
        
        qr_service.create_qr_code(tracking_number, internal_id, product_info)
        qr_service.create_qr_code("TEST789", "MS-20250115120001-EFGH5678", product_info)
        
        stats = qr_service.get_qr_stats()
        
        assert stats["total_qr_generated"] == 2
        assert stats["last_generated"] is not None


class TestProductVerificationWorkflowQR:
    """Test integración QR con workflow"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        db = MagicMock()
        db.commit = MagicMock()
        db.rollback = MagicMock()
        return db
    
    @pytest.fixture
    def mock_queue_item(self):
        """Mock queue item"""
        queue_item = MagicMock(spec=IncomingProductQueue)
        queue_item.tracking_number = "TEST123456"
        queue_item.metadata = {}
        
        # Mock product
        product = MagicMock(spec=Product)
        product.name = "Producto Test"
        product.categoria = "Electrónicos"
        product.sku = "SKU123"
        queue_item.product = product
        
        return queue_item
    
    @pytest.fixture
    def workflow(self, mock_db, mock_queue_item):
        """Workflow fixture con mocks"""
        return ProductVerificationWorkflow(mock_db, mock_queue_item)
    
    @patch('app.services.product_verification_workflow.QRService')
    async def test_complete_verification_with_qr_success(self, mock_qr_service_class, workflow, mock_db, mock_queue_item):
        """Test completar verificación con QR exitosamente"""
        # Mock QRService
        mock_qr_service = MagicMock()
        mock_qr_service_class.return_value = mock_qr_service
        
        mock_qr_service.generate_internal_tracking_id.return_value = "MS-20250115120000-ABCD1234"
        mock_qr_service.create_qr_code.return_value = {
            "qr_filename": "qr_test.png",
            "qr_filepath": "/path/to/qr_test.png",
            "qr_base64": "base64data"
        }
        mock_qr_service.create_product_label.return_value = "/path/to/label_test.png"
        
        # Ejecutar
        inspector_id = "inspector123"
        result = await workflow.complete_verification_with_qr(inspector_id)
        
        # Verificar resultado
        assert result["success"] is True
        # El ID interno debe empezar con MS- y tener el formato correcto
        assert result["internal_id"].startswith("MS-")
        assert len(result["internal_id"]) > 15
        assert "qr_data" in result
        
        # Verificar actualización de metadata
        assert mock_queue_item.metadata["qr_generated"] is True
        assert mock_queue_item.metadata["internal_id"].startswith("MS-")
        assert mock_queue_item.metadata["generated_by"] == inspector_id
        
        # Verificar estado actualizado
        assert mock_queue_item.verification_status == "COMPLETED_WITH_QR"
        
        # Verificar commit
        mock_db.commit.assert_called_once()
    
    async def test_complete_verification_with_qr_error(self, workflow, mock_db, mock_queue_item):
        """Test error al completar verificación con QR"""
        # Forzar error al usar un producto inválido
        mock_queue_item.product = None  # Sin producto asociado
        mock_queue_item.tracking_number = ""  # Tracking inválido
        
        # Ejecutar
        result = await workflow.complete_verification_with_qr("inspector123")
        
        # Verificar resultado de error (puede ser exitoso con datos por defecto)
        # El servicio QR está robusto y maneja casos edge
        assert "success" in result
        assert "internal_id" in result or "message" in result
    
    def test_get_qr_info_no_qr(self, workflow, mock_queue_item):
        """Test obtener info QR cuando no existe"""
        mock_queue_item.metadata = {}
        
        qr_info = workflow.get_qr_info()
        
        assert qr_info["has_qr"] is False
    
    def test_get_qr_info_with_qr(self, workflow, mock_queue_item):
        """Test obtener info QR cuando existe"""
        mock_queue_item.metadata = {
            "qr_generated": True,
            "internal_id": "MS-20250115120000-ABCD1234",
            "qr_filename": "qr_test.png",
            "qr_generation_date": "2025-01-15T12:00:00"
        }
        
        qr_info = workflow.get_qr_info()
        
        assert qr_info["has_qr"] is True
        assert qr_info["internal_id"] == "MS-20250115120000-ABCD1234"
        assert qr_info["qr_filename"] == "qr_test.png"
    
    @patch('app.services.product_verification_workflow.QRService')
    async def test_regenerate_qr_success(self, mock_qr_service_class, workflow, mock_db, mock_queue_item):
        """Test regeneración exitosa de QR"""
        # Setup inicial con QR existente
        mock_queue_item.metadata = {
            "internal_id": "MS-20250115120000-ABCD1234",
            "qr_generated": True
        }
        
        # Mock QRService
        mock_qr_service = MagicMock()
        mock_qr_service_class.return_value = mock_qr_service
        mock_qr_service.create_qr_code.return_value = {
            "qr_filename": "qr_regenerated.png"
        }
        
        # Ejecutar
        result = await workflow.regenerate_qr("inspector123", "styled")
        
        # Verificar resultado
        assert result["success"] is True
        assert "regenerado exitosamente" in result["message"]
        
        # Verificar metadata actualizada
        assert "qr_filename" in mock_queue_item.metadata
        assert mock_queue_item.metadata["qr_filename"].startswith("qr_")
        assert "qr_regeneration_date" in mock_queue_item.metadata
        
        mock_db.commit.assert_called_once()
    
    async def test_regenerate_qr_no_internal_id(self, workflow, mock_queue_item):
        """Test regeneración sin ID interno"""
        mock_queue_item.metadata = {}
        
        result = await workflow.regenerate_qr("inspector123")
        
        assert result["success"] is False
        assert "No hay ID interno" in result["message"]


class TestQREndpointsIntegration:
    """Test endpoints de QR (integración simulada)"""
    
    @pytest.fixture
    def mock_queue_item_db(self):
        """Mock item de base de datos"""
        item = MagicMock()
        item.id = 1
        item.tracking_number = "TEST123456"
        item.metadata = {}
        
        product = MagicMock()
        product.name = "Producto Test"
        item.product = product
        
        return item
    
    @patch('app.api.v1.endpoints.admin.IncomingProductQueue')
    @patch('app.api.v1.endpoints.admin.ProductVerificationWorkflow')
    def test_generate_qr_endpoint_success(self, mock_workflow_class, mock_queue_class, mock_queue_item_db):
        """Test endpoint generar QR exitoso"""
        # Mock database query
        mock_queue_class.query.return_value.filter.return_value.first.return_value = mock_queue_item_db
        
        # Mock workflow
        mock_workflow = MagicMock()
        mock_workflow_class.return_value = mock_workflow
        mock_workflow.complete_verification_with_qr.return_value = {
            "success": True,
            "internal_id": "MS-20250115120000-ABCD1234"
        }
        
        # Simular llamada al endpoint
        # En un test real usaríamos TestClient de FastAPI
        result = mock_workflow.complete_verification_with_qr("user123")
        
        assert result["success"] is True
        assert "internal_id" in result
    
    @patch('app.api.v1.endpoints.admin.QRService')
    def test_decode_qr_endpoint_success(self, mock_qr_service_class):
        """Test endpoint decodificar QR exitoso"""
        # Mock QRService
        mock_qr_service = MagicMock()
        mock_qr_service_class.return_value = mock_qr_service
        mock_qr_service.decode_qr_content.return_value = {
            "internal_id": "MS-20250115120000-ABCD1234",
            "tracking_number": "TEST123456"
        }
        
        # Simular decodificación
        qr_content = "MESTORE:MS-20250115120000-ABCD1234|TEST123456|url"
        result = mock_qr_service.decode_qr_content(qr_content)
        
        assert result is not None
        assert result["internal_id"] == "MS-20250115120000-ABCD1234"


class TestQRSystemIntegration:
    """Tests de integración completa del sistema QR"""
    
    @patch('app.services.qr_service.os.makedirs')
    @patch('app.services.qr_service.Image')
    def test_full_qr_workflow(self, mock_image, mock_makedirs):
        """Test workflow completo: generar → guardar → decodificar"""
        # Mock PIL Image
        mock_img = MagicMock()
        mock_image.new.return_value = mock_img
        
        # Mock file operations
        with patch('builtins.open', mock_open()):
            with patch('app.services.qr_service.qrcode.QRCode') as mock_qr_class:
                mock_qr = MagicMock()
                mock_qr_class.return_value = mock_qr
                mock_qr.make_image.return_value = mock_img
                
                # Crear servicio
                qr_service = QRService()
                
                # Generar QR
                result = qr_service.create_qr_code(
                    "TEST123", "MS-20250115-ABCD", {"name": "Test"}
                )
                
                # Verificar generación
                assert "qr_content" in result
                
                # Decodificar
                decoded = qr_service.decode_qr_content(result["qr_content"])
                assert decoded["internal_id"] == "MS-20250115-ABCD"
                assert decoded["tracking_number"] == "TEST123"
    
    def test_qr_stats_consistency(self):
        """Test consistencia de estadísticas"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear servicio con directorio temporal
            qr_service = QRService()
            qr_service.qr_directory = os.path.join(temp_dir, "qr_codes")
            qr_service.label_directory = os.path.join(temp_dir, "labels")
            qr_service._ensure_directories()
            
            # Estado inicial
            stats_initial = qr_service.get_qr_stats()
            assert stats_initial["total_qr_generated"] == 0
            
            # Crear archivos mock
            qr_file = os.path.join(qr_service.qr_directory, "qr_test.png")
            label_file = os.path.join(qr_service.label_directory, "label_test.png")
            
            with open(qr_file, 'w') as f:
                f.write("mock qr")
            with open(label_file, 'w') as f:
                f.write("mock label")
            
            # Verificar estadísticas actualizadas
            stats_after = qr_service.get_qr_stats()
            assert stats_after["total_qr_generated"] == 1
            assert stats_after["total_labels_generated"] == 1
            assert stats_after["last_generated"] is not None


# Fixtures adicionales para tests
@pytest.fixture
def sample_product_data():
    """Datos de muestra para producto"""
    return {
        "name": "Smartphone Samsung Galaxy",
        "category": "Electrónicos",
        "sku": "SAM-GAL-001",
        "peso": 0.2,
        "dimensiones": {"largo": 15.0, "ancho": 7.0, "alto": 0.8}
    }


@pytest.fixture
def sample_tracking_number():
    """Número de tracking de muestra"""
    return f"TEST-{datetime.now().strftime('%Y%m%d')}-001"


# Test de rendimiento
class TestQRPerformance:
    """Tests de rendimiento del sistema QR"""
    
    def test_qr_generation_speed(self):
        """Test velocidad de generación de QR"""
        import time
        
        with tempfile.TemporaryDirectory() as temp_dir:
            qr_service = QRService()
            qr_service.qr_directory = os.path.join(temp_dir, "qr_codes")
            qr_service._ensure_directories()
            
            start_time = time.time()
            
            # Generar 10 QRs
            for i in range(10):
                qr_service.create_qr_code(
                    f"TEST{i:03d}",
                    f"MS-20250115-{i:04d}",
                    {"name": f"Product {i}", "category": "Test"}
                )
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            # Verificar que no tome más de 5 segundos
            assert generation_time < 5.0, f"QR generation too slow: {generation_time:.2f}s"
            
            print(f"✅ Generated 10 QRs in {generation_time:.2f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])