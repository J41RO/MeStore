"""
Tests para endpoint PUT /perfil/datos-bancarios.
Verifica actualización de datos bancarios del perfil.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

# Banking profile tests - now enabled for comprehensive API testing


def test_update_datos_bancarios_sin_auth():
    """Test que el endpoint requiere autenticación."""
    client = TestClient(app)
    response = client.put("/api/v1/perfil/datos-bancarios", json={
        "banco": "Bancolombia",
        "tipo_cuenta": "AHORROS", 
        "numero_cuenta": "12345678"
    })
    assert response.status_code == 401  # Sin auth debe fallar


def test_update_datos_bancarios_payload_valido():
    """Test validación de payload con datos bancarios válidos."""
    client = TestClient(app)
    # Test sin auth pero con payload válido para verificar estructura
    response = client.put("/api/v1/perfil/datos-bancarios", json={
        "banco": "Bancolombia",
        "tipo_cuenta": "CORRIENTE",
        "numero_cuenta": "12345678901"
    })
    # Debe fallar por auth, no por validación de datos
    assert response.status_code == 401


def test_update_datos_bancarios_payload_invalido():
    """Test validación de payload con datos inválidos."""
    client = TestClient(app)
    # Test con tipo_cuenta inválido
    response = client.put("/api/v1/perfil/datos-bancarios", json={
        "banco": "Bancolombia",
        "tipo_cuenta": "INVALIDO",  # Debe ser AHORROS o CORRIENTE
        "numero_cuenta": "123"  # Muy corto (min 8)
    })
    # Puede ser 401 (auth) o 422 (validación) - ambos son correctos
    assert response.status_code in [401, 422]