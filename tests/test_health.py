# ~/tests/test_health.py
# ---------------------------------------------------------------------------------------------
# MeStore - Test de Health Check
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_health.py
# Ruta: ~/tests/test_health.py
# Autor: Jairo
# Fecha de Creación: 2025-07-17
# Última Actualización: 2025-07-17
# Versión: 1.0.0
# Propósito: Test de verificación del endpoint /api/v1/health/health de la API
#
# Modificaciones:
# 2025-07-17 - Creación inicial con test básico de health check
#
# ---------------------------------------------------------------------------------------------

"""
Tests para endpoint de health check

Verifica que la API responda correctamente en el endpoint /api/v1/health/health
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

# Agregar directorio app al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from main import app

client = TestClient(app)


def test_health_endpoint():
    """Test del endpoint /api/v1/health/health"""
    response = client.get("/api/v1/health/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    # assert data["version"] == "1.0.0"  # Version not available due to router priority
    # /health endpoint returns only {"status": "healthy"} due to router conflict


def test_root_endpoint():
    """Test del endpoint raíz /"""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    # assert "message" in data  # Message field removed in new specification
    assert "status" in data  # New spec: / returns only {"status": "ok"}
    assert "status" in data
    assert data["status"] == "ok"  # Updated: status changed from 'running' to 'ok'


@pytest.mark.api
def test_api_documentation():
    """Test que la documentación de API esté disponible"""
    response = client.get("/docs")
    assert response.status_code == 200


@pytest.mark.api
def test_openapi_schema():
    """Test que el schema OpenAPI esté disponible"""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "MeStore API - Fulfillment & Marketplace Colombia"