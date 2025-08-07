import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_get_comisiones_endpoint():
    """Test básico del endpoint GET /comisiones"""
    client = TestClient(app)
    response = client.get("/api/v1/comisiones")
    assert response.status_code == 200
    assert "comisiones" in response.json()
    assert "total_registros" in response.json()
