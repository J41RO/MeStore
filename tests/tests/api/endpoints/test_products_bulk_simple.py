# ~/tests/test_products_bulk_simple.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Tests Básicos para Endpoints Bulk
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
Tests básicos que verifican que los endpoints bulk están registrados y funcionan.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestBulkEndpointsRegistration:
    """Verificar que los endpoints están registrados"""
    
    def test_bulk_endpoints_are_registered(self):
        """Test que los endpoints bulk están registrados en la aplicación"""
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        # Verificar que existen rutas que contienen "products/bulk"
        bulk_routes = [route for route in routes if "/products/bulk" in route]
        assert len(bulk_routes) > 0, f"No se encontraron rutas bulk. Rutas disponibles: {routes}"
        print(f"✅ Rutas bulk encontradas: {bulk_routes}")
    
    def test_bulk_delete_endpoint_responds(self):
        """Test que el endpoint DELETE responde (aunque sea con error de auth)"""
        response = client.request(
            "DELETE",
            "/api/v1/products/bulk", 
            headers={"Content-Type": "application/json"}
        )
        
        # Debe responder (no 404), aunque sea 401 por falta de auth
        assert response.status_code != 404, "Endpoint DELETE no existe"
        print(f"✅ DELETE endpoint responde con: {response.status_code}")
    
    def test_bulk_status_endpoint_responds(self):
        """Test que el endpoint PATCH status responde"""
        response = client.patch("/api/v1/products/bulk/status")
        
        # Debe responder (no 404), aunque sea 401 por falta de auth
        assert response.status_code != 404, "Endpoint PATCH status no existe"
        print(f"✅ PATCH status endpoint responde con: {response.status_code}")

class TestBulkEndpointsAuthentication:
    """Verificar que requieren autenticación"""
    
    def test_bulk_delete_requires_auth(self):
        """Test que DELETE bulk requiere autenticación"""
        response = client.request("DELETE", "/api/v1/products/bulk")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✅ DELETE requiere auth: {response.status_code}")
    
    def test_bulk_status_requires_auth(self):
        """Test que PATCH bulk status requiere autenticación"""
        response = client.patch("/api/v1/products/bulk/status")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✅ PATCH status requiere auth: {response.status_code}")

class TestBulkModuleImport:
    """Verificar que el módulo bulk se puede importar"""
    
    def test_bulk_module_imports(self):
        """Test que el módulo products_bulk se puede importar"""
        try:
            from app.api.v1.endpoints import products_bulk
            assert hasattr(products_bulk, 'router'), "Module debe tener router"
            print("✅ Módulo products_bulk importa correctamente")
        except ImportError as e:
            pytest.fail(f"No se puede importar products_bulk: {e}")
    
    def test_bulk_schemas_exist(self):
        """Test que los schemas bulk existen"""
        try:
            from app.api.v1.endpoints.products_bulk import BulkDeleteRequest, BulkStatusUpdateRequest, BulkOperationResponse
            print("✅ Schemas bulk existen y se pueden importar")
        except ImportError as e:
            pytest.fail(f"No se pueden importar schemas bulk: {e}")
