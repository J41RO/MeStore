# tests/api/test_pagos_historial.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_historial_pagos_basic():
    """Test básico del endpoint de historial de pagos."""
    response = client.get("/api/v1/pagos/historial")
    assert response.status_code == 200
    assert "transacciones" in response.json()
    assert "total" in response.json()
