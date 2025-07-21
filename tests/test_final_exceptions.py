"""
Tests completos para exception handlers personalizados.
Basado en investigación real del sistema - casos que funcionan 100%.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestExceptionHandlers:
    """Suite completa de tests para exception handlers con casos reales."""

    def test_validation_error_real_endpoint(self):
        """Test RequestValidationError: Endpoint /logs/logs con campos requeridos faltantes."""
        # Enviar JSON inválido a endpoint real que requiere campos específicos
        response = client.post(
            "/api/v1/logs/logs",
            json={
                "invalid_field": "data"  # Faltan campos: level, message, timestamp, url, userAgent
            }
        )
        
        # Verificar status code de validación
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        
        # Verificar estructura JSON estandarizada
        json_data = response.json()
        assert "error" in json_data, f"Missing 'error' field in: {json_data}"
        assert "detail" in json_data, f"Missing 'detail' field in: {json_data}"
        assert "status_code" in json_data, f"Missing 'status_code' field in: {json_data}"
        assert "path" in json_data, f"Missing 'path' field in: {json_data}"
        
        # Verificar contenido específico
        assert json_data["error"] == "ValidationError", f"Expected 'ValidationError', got {json_data['error']}"
        assert json_data["status_code"] == 422
        assert json_data["path"] == "/api/v1/logs/logs"
        assert "Field required" in json_data["detail"]
        
        print(f"✅ ValidationError handler working: {json_data['error']}")

    def test_http_exception_404(self):
        """Test HTTPException: Endpoint no existente devuelve 404 estandarizado."""
        response = client.get("/api/v1/nonexistent_endpoint_testing_12345")
        
        # Verificar status code
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        
        # Verificar estructura JSON estandarizada
        json_data = response.json()
        assert "error" in json_data, f"Missing 'error' field in: {json_data}"
        assert "detail" in json_data, f"Missing 'detail' field in: {json_data}"
        assert "status_code" in json_data, f"Missing 'status_code' field in: {json_data}"
        assert "path" in json_data, f"Missing 'path' field in: {json_data}"
        
        # Verificar contenido específico
        assert json_data["error"] == "HTTP404", f"Expected 'HTTP404', got {json_data['error']}"
        assert json_data["status_code"] == 404
        assert json_data["path"] == "/api/v1/nonexistent_endpoint_testing_12345"
        assert json_data["detail"] == "Not Found"
        
        print(f"✅ HTTP Exception handler working: {json_data['error']}")

    def test_http_exception_403(self):
        """Test HTTPException: Endpoint protegido devuelve 403 estandarizado."""
        response = client.get("/api/v1/marketplace/protected")
        
        # Verificar status code
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        
        # Verificar estructura JSON estandarizada
        json_data = response.json()
        assert "error" in json_data, f"Missing 'error' field in: {json_data}"
        assert "detail" in json_data, f"Missing 'detail' field in: {json_data}"
        assert "status_code" in json_data, f"Missing 'status_code' field in: {json_data}"
        assert "path" in json_data, f"Missing 'path' field in: {json_data}"
        
        # Verificar contenido específico
        assert json_data["error"] == "HTTP403", f"Expected 'HTTP403', got {json_data['error']}"
        assert json_data["status_code"] == 403
        assert json_data["path"] == "/api/v1/marketplace/protected"
        
        print(f"✅ HTTP 403 Exception handler working: {json_data['error']}")

    def test_successful_endpoint_no_error(self):
        """Test endpoint exitoso para contrastar con errores."""
        response = client.get("/api/v1/health/health")
        
        # Verificar status code exitoso
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verificar estructura de respuesta exitosa
        json_data = response.json()
        assert "status" in json_data, f"Missing 'status' field in success response: {json_data}"
        assert json_data["status"] == "healthy"
        
        print(f"✅ Successful endpoint working: {response.status_code}")

    def test_exception_handlers_registration(self):
        """Test que verifica que todos los handlers están registrados."""
        # Verificar que tenemos al menos 4 handlers registrados
        handlers_count = len(app.exception_handlers)
        assert handlers_count >= 4, f"Expected at least 4 handlers, got {handlers_count}"
        
        # Verificar handlers específicos
        from app.api.v1.handlers.exceptions import AppException
        from fastapi import HTTPException
        from fastapi.exceptions import RequestValidationError
        
        assert AppException in app.exception_handlers, "AppException handler not registered"
        assert HTTPException in app.exception_handlers, "HTTPException handler not registered" 
        assert RequestValidationError in app.exception_handlers, "RequestValidationError handler not registered"
        assert Exception in app.exception_handlers, "Global Exception handler not registered"
        
        print(f"✅ {handlers_count} exception handlers registrados correctamente")

    def test_custom_exceptions_available(self):
        """Test que verifica que las excepciones personalizadas están disponibles."""
        # Verificar que las excepciones personalizadas se pueden importar
        from app.api.v1.handlers.exceptions import (
            AppException,
            EmbeddingNotFoundException,
            InvalidEmbeddingPayloadException,
            EmbeddingProcessingException,
            register_exception_handlers,
        )
        
        # Verificar que son clases válidas
        assert issubclass(EmbeddingNotFoundException, AppException)
        assert issubclass(InvalidEmbeddingPayloadException, AppException)
        assert issubclass(EmbeddingProcessingException, AppException)
        assert callable(register_exception_handlers)
        
        print("✅ All custom exceptions imported and verified")

    def test_embeddings_exception_usage_in_code(self):
        """Test que verifica que excepciones personalizadas están usadas en código real."""
        # Verificar que las excepciones están siendo importadas y usadas
        import os
        embeddings_file = "app/api/v1/endpoints/embeddings.py"
        assert os.path.exists(embeddings_file), "Embeddings file should exist"
        
        with open(embeddings_file, 'r') as f:
            content = f.read()
        
        # Verificar que están importadas
        assert "InvalidEmbeddingPayloadException" in content, "InvalidEmbeddingPayloadException not imported"
        assert "EmbeddingNotFoundException" in content, "EmbeddingNotFoundException not imported"
        
        # Verificar que están siendo usadas (raise statements)
        assert "raise InvalidEmbeddingPayloadException" in content, "InvalidEmbeddingPayloadException not used"
        assert "raise EmbeddingNotFoundException" in content, "EmbeddingNotFoundException not used"
        
        print("✅ Custom exceptions are used in real endpoint code")


if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])
