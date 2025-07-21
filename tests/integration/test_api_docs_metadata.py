"""
Test de integración para verificar metadata de API y documentación.

Este test verifica que la configuración de metadata FastAPI funcione correctamente
y que los endpoints de documentación estén disponibles.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAPIDocsMetadata:
    """Test suite para metadata y documentación de API."""

    def test_openapi_json_endpoint_available(self):
        """Verificar que /openapi.json devuelve código 200."""
        response = client.get("/openapi.json")
        assert response.status_code == 200, f"OpenAPI endpoint failed with status {response.status_code}"

        # Verificar que la respuesta es JSON válido
        openapi_data = response.json()
        assert isinstance(openapi_data, dict), "OpenAPI response should be a JSON object"

    def test_openapi_schema_contains_metadata(self):
        """Confirmar presencia de title, version, tags en el esquema OpenAPI."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        openapi_data = response.json()

        # Verificar información básica de la API
        assert "info" in openapi_data, "OpenAPI schema should contain info section"
        info = openapi_data["info"]

        # Verificar title específico
        expected_title = "MeStore API - Fulfillment & Marketplace Colombia"
        actual_title = info.get("title")
        assert info["title"] == expected_title, f"Expected title: {expected_title}, got: {actual_title}"

        # Verificar version
        actual_version = info.get("version")
        assert info["version"] == "1.0.0", f"Expected version 1.0.0, got: {actual_version}"

        # Verificar description
        base_desc = "API pública de MeStore para gestión de productos, IA, salud del sistema y agentes autónomos."
        description = info["description"]
        assert base_desc in description, f"Base description not found in: {description[:100]}..."

        # Verificar que contiene información de entornos
        assert "🏗️ ENTORNOS CONFIGURADOS:" in description, "Description should contain environment info"
        assert "192.168.1.137:8000" in description, "Description should contain backend URL"
        assert "192.168.1.137:5173" in description, "Description should contain frontend URL"

        # Verificar que existen tags
        assert "tags" in openapi_data, "OpenAPI schema should contain tags section"
        tags = openapi_data["tags"]

        # Verificar tags específicos definidos en metadata
        expected_tags = ["health", "embeddings", "logs", "marketplace", "agents"]
        actual_tag_names = [tag["name"] for tag in tags]

        for expected_tag in expected_tags:
            assert expected_tag in actual_tag_names, f"Tag {expected_tag} not found in OpenAPI tags"

        # Verificar que cada tag tiene descripción
        for tag in tags:
            tag_name = tag["name"]
            assert "description" in tag, f"Tag {tag_name} should have description"
            assert len(tag["description"]) > 0, f"Tag {tag_name} description should not be empty"

    def test_docs_and_redoc_endpoints_available(self):
        """Verificar que /docs y /redoc estén disponibles."""
        # Test Swagger UI endpoint
        docs_response = client.get("/docs")
        assert docs_response.status_code == 200, f"Swagger docs endpoint failed with status {docs_response.status_code}"

        # Verificar que contiene contenido HTML
        docs_content = docs_response.text
        assert "swagger" in docs_content.lower() or "openapi" in docs_content.lower(), "Docs endpoint should contain Swagger/OpenAPI content"

        # Test ReDoc endpoint
        redoc_response = client.get("/redoc")
        assert redoc_response.status_code == 200, f"ReDoc endpoint failed with status {redoc_response.status_code}"

        # Verificar que contiene contenido HTML de ReDoc
        redoc_content = redoc_response.text
        assert "redoc" in redoc_content.lower(), "ReDoc endpoint should contain ReDoc content"

        # Verificar que ambos endpoints referencian el schema OpenAPI
        assert "/openapi.json" in docs_content, "Docs should reference OpenAPI schema"
        assert "/openapi.json" in redoc_content, "ReDoc should reference OpenAPI schema"


if __name__ == "__main__":
    # Ejecutar tests si se llama directamente
    pytest.main([__file__, "-v"])