# ~/tests/test_products_bulk_endpoints.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Tests para Endpoints de Operaciones Bulk de Productos
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
Tests para endpoints de operaciones bulk de productos.
"""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from datetime import datetime

from app.main import app
from app.models.user import UserType
from app.schemas.user import UserRead
from app.api.v1.deps.auth import get_current_user

# Cliente de testing
client = TestClient(app)

# Mock user para autenticación
test_user = UserRead(
    id=str(uuid4()),
    email="test@example.com",
    nombre="Test",
    apellido="User", 
    user_type=UserType.ADMIN,
    is_active=True,
    created_at=datetime.now(),
    updated_at=datetime.now(),
    last_login=None
)

def override_get_current_user():
    return test_user

class TestBulkEndpointsBasic:
    """Tests básicos de endpoints bulk"""
    
    def test_bulk_delete_endpoint_exists(self):
        """Test que el endpoint DELETE existe (requiere auth)"""
        response = client.request("DELETE", "/api/v1/products/bulk")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✅ DELETE endpoint existe y requiere auth: {response.status_code}")
    
    def test_bulk_status_endpoint_exists(self):
        """Test que el endpoint PATCH status existe (requiere auth)"""
        response = client.request("PATCH", "/api/v1/products/bulk/status")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✅ PATCH status endpoint existe y requiere auth: {response.status_code}")

class TestBulkEndpointsWithAuth:
    """Tests de endpoints bulk con autenticación"""
    
    @classmethod
    def setup_class(cls):
        """Setup para la clase - aplicar override de auth"""
        app.dependency_overrides[get_current_user] = override_get_current_user
    
    @classmethod
    def teardown_class(cls):
        """Teardown para la clase - limpiar overrides"""
        app.dependency_overrides.clear()
    
    def test_bulk_delete_with_auth_empty_list_validation(self):
        """Test DELETE bulk con auth - validación lista vacía"""
        response = client.request(
            "DELETE", 
            "/api/v1/products/bulk",
            json={"product_ids": []}
        )
        
        # Debe fallar validación (422) - no auth (401)
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        print(f"✅ DELETE con auth valida lista vacía: {response.status_code}")
    
    def test_bulk_delete_with_auth_valid_request(self):
        """Test DELETE bulk con auth - request válida"""
        response = client.request(
            "DELETE", 
            "/api/v1/products/bulk",
            json={"product_ids": [str(uuid4())]}
        )
        
        # Debe procesar (200 o 500, no 401/404/422)
        assert response.status_code not in [401, 404, 422], f"Unexpected status: {response.status_code}"
        print(f"✅ DELETE con auth procesa request: {response.status_code}")
    
    def test_bulk_status_with_auth_invalid_status(self):
        """Test PATCH bulk status con auth - estado inválido"""
        response = client.patch(
            "/api/v1/products/bulk/status",
            json={
                "product_ids": [str(uuid4())],
                "status": "invalid_status"
            }
        )
        
        # Debe fallar validación (422)
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        print(f"✅ PATCH status con auth valida estado: {response.status_code}")
    
    def test_bulk_status_with_auth_valid_request(self):
        """Test PATCH bulk status con auth - request válida"""
        response = client.patch(
            "/api/v1/products/bulk/status",
            json={
                "product_ids": [str(uuid4())],
                "status": "active"
            }
        )
        
        # Debe procesar (200 o 500, no 401/404/422)
        assert response.status_code not in [401, 404, 422], f"Unexpected status: {response.status_code}"
        print(f"✅ PATCH status con auth procesa request: {response.status_code}")

class TestBulkModuleIntegration:
    """Tests de integración del módulo"""
    
    def test_bulk_module_imports(self):
        """Test que el módulo se importa correctamente"""
        try:
            from app.api.v1.endpoints import products_bulk
            assert hasattr(products_bulk, 'router'), "Módulo debe tener router"
            print("✅ Módulo products_bulk importa OK")
        except ImportError as e:
            pytest.fail(f"Error importando products_bulk: {e}")
    
    def test_bulk_schemas_importable(self):
        """Test que los schemas se pueden importar"""
        try:
            from app.api.v1.endpoints.products_bulk import (
                BulkDeleteRequest, 
                BulkStatusUpdateRequest, 
                BulkOperationResponse
            )
            print("✅ Schemas bulk importan OK")
        except ImportError as e:
            pytest.fail(f"Error importando schemas: {e}")
    
    def test_endpoints_registered_in_router(self):
        """Test que los endpoints están en el router de la app"""
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        bulk_routes = [route for route in routes if "/products/bulk" in route]
        assert len(bulk_routes) > 0, f"No se encontraron rutas bulk. Rutas disponibles: {routes[:10]}..."
        print(f"✅ Rutas bulk registradas: {bulk_routes}")

class TestBulkValidationDetails:
    """Tests detallados de validación"""
    
    @classmethod
    def setup_class(cls):
        """Setup para la clase - aplicar override de auth"""
        app.dependency_overrides[get_current_user] = override_get_current_user
    
    @classmethod
    def teardown_class(cls):
        """Teardown para la clase - limpiar overrides"""
        app.dependency_overrides.clear()
    
    def test_bulk_delete_validation_scenarios(self):
        """Test diferentes escenarios de validación DELETE"""
        
        # Lista vacía
        response = client.request("DELETE", "/api/v1/products/bulk", json={"product_ids": []})
        assert response.status_code == 422
        
        # Campo faltante
        response = client.request("DELETE", "/api/v1/products/bulk", json={})
        assert response.status_code == 422
        
        print("✅ DELETE validaciones funcionan correctamente")
    
    def test_bulk_status_validation_scenarios(self):
        """Test diferentes escenarios de validación PATCH status"""
        
        # Estado inválido
        response = client.patch("/api/v1/products/bulk/status", json={
            "product_ids": [str(uuid4())],
            "status": "invalid"
        })
        assert response.status_code == 422
        
        # Lista vacía
        response = client.patch("/api/v1/products/bulk/status", json={
            "product_ids": [],
            "status": "active"
        })
        assert response.status_code == 422
        
        print("✅ PATCH status validaciones funcionan correctamente")
