# ~/tests/api/test_productos.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Tests para endpoints de productos
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_productos.py
# Ruta: ~/tests/api/test_productos.py
# Autor: Jairo
# Fecha de Creación: 2025-01-14
# Última Actualización: 2025-01-14
# Versión: 1.0.0
# Propósito: Tests para endpoints de productos de la API v1
#            Validar funcionalidad del endpoint POST /productos
#
# Modificaciones:
# 2025-01-14 - Implementación inicial de tests básicos
#
# ---------------------------------------------------------------------------------------------

"""
Tests para endpoints de productos.

Este módulo contiene:
- Tests para endpoint POST /productos
- Validación de creación exitosa
- Validación de errores (SKU duplicado)
- Tests de validación de datos
"""

import time

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.product import Product


class TestCreateProducto:
    """Test suite para endpoint POST /productos"""

    def test_create_producto_success(self, client_with_test_db: TestClient):
        """Test creación exitosa de producto."""
        # SKU único para evitar duplicados
        timestamp = int(time.time() * 1000)  # timestamp en milisegundos
        product_data = {
            "sku": f"TEST-{timestamp}",  # SKU único basado en timestamp
            "name": "Producto Test",
            "description": "Descripción del producto test",
            "precio_venta": 150.0,
            "categoria": "Electrónicos",
        }

        response = client_with_test_db.post("/api/v1/productos/", json=product_data)

        assert response.status_code == 201
        data = response.json()
        assert data["sku"] == f"TEST-{timestamp}"
        assert data["name"] == "Producto Test"
        assert data["precio_venta"] == 150.0
        assert "id" in data
        assert data["categoria"] == "Electrónicos"

    def test_create_producto_duplicate_sku(self, client_with_test_db: TestClient):
        """Test error por SKU duplicado."""
        # Usar timestamp único también aquí
        timestamp = int(time.time() * 1000)
        product_data = {
            "sku": f"DUP-{timestamp}",
            "name": "Producto Duplicado",
            "description": "Test duplicado",
            "precio_venta": 150.0,
            "categoria": "Test",
        }

        # Crear primer producto
        response1 = client_with_test_db.post("/api/v1/productos/", json=product_data)
        assert response1.status_code == 201

        # Intentar crear duplicado (mismo SKU)
        response2 = client_with_test_db.post("/api/v1/productos/", json=product_data)
        assert response2.status_code == 400
        assert "ya existe" in response2.json()["detail"]

    def test_create_producto_invalid_data(self, client_with_test_db: TestClient):
        """Test validación de datos inválidos."""
        # Test sin SKU requerido
        invalid_data = {
            "name": "Producto Sin SKU",
            "description": "Test sin SKU",
            "precio_venta": 150.0,
            "categoria": "Test",
        }

        response = client_with_test_db.post("/api/v1/productos/", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_create_producto_minimal_data(self, client_with_test_db: TestClient):
        """Test creación con datos mínimos requeridos."""
        # SKU único para este test también
        timestamp = int(time.time() * 1000)
        minimal_data = {
            "sku": f"MIN-{timestamp}",
            "name": "Producto Mínimo",
            "description": "Test mínimo",
            "precio_venta": 100.0,  # Precio mínimo válido
            "categoria": "Test",
        }

        response = client_with_test_db.post("/api/v1/productos/", json=minimal_data)

        assert response.status_code == 201
        data = response.json()
        assert data["sku"] == f"MIN-{timestamp}"
        assert data["name"] == "Producto Mínimo"
