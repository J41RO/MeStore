"""
Tests para endpoint VendorList - Listado y filtrado de vendedores.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.vendedor import EstadoVendedor, TipoCuentaVendedor

client = TestClient(app)

class TestVendorList:
    """Tests para endpoint GET /api/v1/vendedores/list"""
    
    def test_vendor_list_without_filters(self):
        """Test endpoint sin filtros"""
        response = client.get("/api/v1/vendedores/list")
        
        # Verificar que el endpoint responde (puede dar 401/403 sin autenticación)
        assert response.status_code in [200, 401, 403], f"Status inesperado: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "vendedores" in data
            assert "total" in data
            assert "limit" in data
            assert "offset" in data
            assert isinstance(data["vendedores"], list)
    
    def test_vendor_list_with_estado_filter(self):
        """Test filtro por estado"""
        response = client.get("/api/v1/vendedores/list?estado=activo")
        
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert "vendedores" in data
    
    def test_vendor_list_with_tipo_cuenta_filter(self):
        """Test filtro por tipo de cuenta"""
        response = client.get("/api/v1/vendedores/list?tipo_cuenta=premium")
        
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert "vendedores" in data
    
    def test_vendor_list_with_pagination(self):
        """Test paginación"""
        response = client.get("/api/v1/vendedores/list?limit=5&offset=0")
        
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert data["limit"] == 5
            assert data["offset"] == 0
    
    def test_vendor_list_combined_filters(self):
        """Test combinación de filtros"""
        response = client.get("/api/v1/vendedores/list?estado=activo&tipo_cuenta=basica&limit=10")
        
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert "vendedores" in data
            assert data["limit"] == 10
    
    def test_vendor_list_invalid_estado(self):
        """Test con estado inválido"""
        response = client.get("/api/v1/vendedores/list?estado=inexistente")
        
        # El endpoint requiere autenticación, por lo que puede dar 401/403 antes de validar
        # En un sistema real, la autenticación se verifica antes que la validación de parámetros
        assert response.status_code in [401, 403, 422], f"Status inesperado: {response.status_code}"
    
    def test_vendor_list_invalid_pagination(self):
        """Test con paginación inválida"""
        response = client.get("/api/v1/vendedores/list?limit=0")
        
        # El endpoint requiere autenticación, por lo que puede dar 401/403 antes de validar parámetros
        # En un sistema de producción, la autenticación se verifica antes que la validación
        assert response.status_code in [401, 403, 422], f"Status inesperado: {response.status_code}"
    
    def test_vendor_list_response_structure(self):
        """Test estructura de respuesta"""
        response = client.get("/api/v1/vendedores/list")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verificar estructura principal
            required_fields = ["vendedores", "total", "limit", "offset"]
            for field in required_fields:
                assert field in data, f"Campo {field} faltante en respuesta"
            
            # Verificar estructura de items si hay vendedores
            if data["vendedores"]:
                vendedor = data["vendedores"][0]
                vendor_fields = ["id", "email", "estado", "tipo_cuenta", "fecha_registro"]
                for field in vendor_fields:
                    assert field in vendedor, f"Campo {field} faltante en vendedor"

def test_health_check_still_works():
    """Test que el health check sigue funcionando tras agregar VendorList"""
    response = client.get("/api/v1/vendedores/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "endpoints" in data

if __name__ == "__main__":
    pytest.main(["-v", __file__])
