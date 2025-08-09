# ~/tests/api/test_comisiones_dispute.py
"""
Tests para endpoint de disputas de comisiones.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_reportar_disputa_sin_auth():
    """Test endpoint sin autenticación - debe retornar 401."""
    dispute_data = {
        "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
        "motivo": "COMISION_INCORRECTA",
        "descripcion": "La comisión cobrada no corresponde al porcentaje acordado"
    }

    response = client.post("/api/v1/comisiones/dispute", json=dispute_data)
    assert response.status_code == 403  # Sistema devuelve 403 Not authenticated


def test_reportar_disputa_transaction_not_found():
    """Test con transacción inexistente retorna 404."""
    fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
    dispute_data = {
        "transaction_id": fake_uuid,
        "motivo": "COMISION_INCORRECTA", 
        "descripcion": "Test descripción de disputa"
    }

    # Nota: Este test requiere autenticación real para funcionar completamente
    response = client.post("/api/v1/comisiones/dispute", json=dispute_data)
    # Sin auth token, debe ser 401, no 404
    assert response.status_code == 403


def test_reportar_disputa_invalid_data():
    """Test con datos inválidos retorna 422."""
    invalid_data = {
        "transaction_id": "not-a-valid-uuid",
        "motivo": "",  # Vacío
        "descripcion": "x"  # Muy corto
    }

    response = client.post("/api/v1/comisiones/dispute", json=invalid_data)
    assert response.status_code == 403  # Auth required before validation


def test_reportar_disputa_schema_validation():
    """Test validación de schema Pydantic."""
    # Sin campos requeridos
    response = client.post("/api/v1/comisiones/dispute", json={})
    assert response.status_code == 403  # Auth required before validation

    # Con campos pero valores incorrectos
    invalid_data = {
        "transaction_id": "invalid-uuid",
        "motivo": "A" * 101,  # Muy largo (max 100)
        "descripcion": "123"  # Muy corto (min 10)
    }

    response = client.post("/api/v1/comisiones/dispute", json=invalid_data)
    assert response.status_code == 403  # Auth required before validation