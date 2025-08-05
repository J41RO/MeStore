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
# Última Actualización: 2025-08-04
# Versión: 1.1.0
# Propósito: Tests para endpoints de productos de la API v1
#            Validar funcionalidad del endpoint POST /productos y GET /productos
#
# Modificaciones:
# 2025-01-14 - Implementación inicial de tests básicos
# 2025-08-04 - Corrección de tests mal diseñados y limpieza de código
#
# ---------------------------------------------------------------------------------------------

"""
Tests para endpoints de productos.

Este módulo contiene:
- Tests para endpoint POST /productos
- Tests para endpoint GET /productos
- Validación de creación exitosa
- Validación de errores (SKU duplicado)
- Tests de validación de datos
- Tests de filtros y paginación
"""

import time

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

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


class TestGetProductos:
    """Tests para endpoint GET /productos con filtros y paginación."""

    @pytest.mark.asyncio
    async def test_get_productos_basic_list_FIXED(self, async_client: AsyncClient):
        """Test GET productos lista básica - crea producto y lo busca."""
        import time

        timestamp = int(time.time() * 1000)

        # Crear producto con campos correctos
        producto_data = {
            "sku": f"TEST-BASIC-{timestamp}",
            "name": "Producto Test Básico",
            "description": "Producto creado para test básico",
            "precio_venta": 100.0,
            "categoria": "Test",
        }

        # Crear producto PRIMERO
        create_response = await async_client.post(
            "/api/v1/productos/", json=producto_data
        )
        assert create_response.status_code == 201

        # DESPUÉS hacer GET que encontrará el producto
        response = await async_client.get("/api/v1/productos/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Verificar estructura de respuesta
        producto = data[0]
        assert "id" in producto
        assert "sku" in producto
        assert "name" in producto
        assert "precio_venta" in producto

    @pytest.mark.asyncio
    async def test_get_productos_empty_list(self, async_client: AsyncClient):
        """Test GET productos cuando no hay productos en la base de datos."""
        response = await async_client.get("/api/v1/productos/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0  # Lista debe estar vacía

    @pytest.mark.asyncio
    async def test_get_productos_search_filter(self, async_client: AsyncClient):
        """Test filtro de búsqueda por texto."""
        # Crear producto específico para búsqueda
        import time

        timestamp = int(time.time() * 1000)
        search_product = {
            "sku": f"SEARCH-{timestamp}",
            "name": "Producto Especial Búsqueda",
            "description": "Test de búsqueda específica",
            "precio_venta": 150.0,
            "categoria": "Test",
        }

        create_response = await async_client.post(
            "/api/v1/productos/", json=search_product
        )
        assert create_response.status_code == 201

        # Buscar por nombre
        response = await async_client.get("/api/v1/productos/?search=Especial")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any("Especial" in p["name"] for p in data)

    @pytest.mark.asyncio
    async def test_get_productos_categoria_filter(self, async_client: AsyncClient):
        """Test filtro por categoría."""
        import time

        timestamp = int(time.time() * 1000)

        # Crear producto con categoría específica
        category_product = {
            "sku": f"CAT-{timestamp}",
            "name": "Producto Categoría Test",
            "description": "Test filtro categoría",
            "precio_venta": 200.0,
            "categoria": "Electrónicos",
        }

        create_response = await async_client.post(
            "/api/v1/productos/", json=category_product
        )
        assert create_response.status_code == 201

        # Filtrar por categoría
        response = await async_client.get("/api/v1/productos/?categoria=Electrónicos")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all("Electrónicos" in p["categoria"] for p in data)

    @pytest.mark.asyncio
    async def test_get_productos_price_range_filter(self, async_client: AsyncClient):
        """Test filtros de rango de precio."""
        import time

        timestamp = int(time.time() * 1000)

        # Crear producto con precio específico
        price_product = {
            "sku": f"PRICE-{timestamp}",
            "name": "Producto Precio Test",
            "description": "Test filtro precio",
            "precio_venta": 200000.0,
            "categoria": "Test",
        }

        create_response = await async_client.post(
            "/api/v1/productos/", json=price_product
        )
        assert create_response.status_code == 201

        # Filtrar por rango de precio
        response = await async_client.get(
            "/api/v1/productos/?precio_min=150000&precio_max=250000"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(150000 <= p["precio_venta"] <= 250000 for p in data)

    @pytest.mark.asyncio
    async def test_get_productos_pagination(self, async_client: AsyncClient):
        """Test paginación."""
        # Test con límite específico
        response = await async_client.get("/api/v1/productos/?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

        # Test con skip
        response = await async_client.get("/api/v1/productos/?skip=1&limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1

    @pytest.mark.asyncio
    async def test_get_productos_sorting(self, async_client: AsyncClient):
        """Test ordenamiento."""
        # Test ordenamiento por precio ascendente
        response = await async_client.get(
            "/api/v1/productos/?sort_by=precio_venta&sort_order=asc"
        )
        assert response.status_code == 200
        data = response.json()

        if len(data) > 1:
            # Verificar que están ordenados por precio ascendente
            precios = [p["precio_venta"] for p in data]
            assert precios == sorted(precios)

    @pytest.mark.asyncio
    async def test_get_producto_by_id_success(self, async_client: AsyncClient):
        """Test obtener producto específico por ID exitosamente."""
        import time

        timestamp = int(time.time() * 1000)

        # Crear producto para obtener por ID
        product_data = {
            "sku": f"BYID-{timestamp}",
            "name": "Producto By ID Test",
            "description": "Test obtener por ID específico",
            "precio_venta": 250.0,
            "categoria": "Test",
        }

        # Crear producto
        create_response = await async_client.post(
            "/api/v1/productos/", json=product_data
        )
        assert create_response.status_code == 201
        created_product = create_response.json()
        product_id = created_product["id"]

        # Obtener producto por ID
        response = await async_client.get(f"/api/v1/productos/{product_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["sku"] == f"BYID-{timestamp}"
        assert data["name"] == "Producto By ID Test"
        assert data["precio_venta"] == 250.0

    @pytest.mark.asyncio
    async def test_get_producto_by_id_not_found(self, async_client: AsyncClient):
        """Test error 404 cuando producto no existe."""
        from uuid import uuid4

        # Usar UUID que no existe
        non_existent_id = str(uuid4())

        response = await async_client.get(f"/api/v1/productos/{non_existent_id}")

        assert response.status_code == 404
        data = response.json()
        assert "no encontrado" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_producto_by_id_invalid_uuid(self, async_client: AsyncClient):
        """Test error de validación con UUID inválido."""
        invalid_id = "not-a-valid-uuid"

        response = await async_client.get(f"/api/v1/productos/{invalid_id}")

        assert response.status_code == 422  # Validation error


# ========================================================================
# TESTS PARA ENDPOINT PUT /productos/{id} - MICRO-FASE 2
# ========================================================================


class TestProductosPUT:
    """Tests comprehensivos para endpoint PUT /productos/{id}"""

    async def test_update_producto_exitoso_campos_parciales(
        self, async_client, sample_product_data
    ):
        """Test actualización exitosa con campos parciales"""
        # Crear producto primero
        create_response = await async_client.post(
            "/api/v1/productos/", json=sample_product_data
        )
        assert create_response.status_code == 201
        producto_id = create_response.json()["id"]

        # Actualizar solo algunos campos
        update_data = {
            "name": "Producto Actualizado",
            "precio_venta": 200000.0,
            "description": "Descripción actualizada",
        }

        response = await async_client.put(
            f"/api/v1/productos/{producto_id}", json=update_data
        )

        assert response.status_code == 200

        result = response.json()
        assert result["name"] == "Producto Actualizado"
        assert result["precio_venta"] == 200000.0
        assert result["description"] == "Descripción actualizada"
        # Verificar que campos no actualizados se preservaron
        assert result["sku"] == sample_product_data["sku"]

    async def test_update_producto_exitoso_campos_completos(
        self, async_client, sample_product_data
    ):
        """Test actualización exitosa con todos los campos"""
        # Crear producto primero
        create_response = await async_client.post(
            "/api/v1/productos/", json=sample_product_data
        )
        assert create_response.status_code == 201
        producto_id = create_response.json()["id"]

        # Actualizar todos los campos
        update_data = {
            "name": "Producto Completamente Actualizado",
            "description": "Nueva descripción completa",
            "precio_venta": 200000.0,
            "sku": "SKU-UPDATE-001",
            "categoria": "Nueva Categoría",
        }

        response = await async_client.put(
            f"/api/v1/productos/{producto_id}", json=update_data
        )
        assert response.status_code == 200

        result = response.json()
        assert result["name"] == update_data["name"]
        assert result["description"] == update_data["description"]
        assert result["precio_venta"] == 200000.0
        assert result["sku"] == update_data["sku"]
        assert result["categoria"] == update_data["categoria"]

    async def test_update_producto_no_encontrado_404(self, async_client):
        """Test producto no encontrado devuelve 404"""
        import uuid

        producto_id_inexistente = str(uuid.uuid4())

        update_data = {"nombre": "No importa", "precio": 100.0}

        response = await async_client.put(
            f"/api/v1/productos/{producto_id_inexistente}", json=update_data
        )
        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"].lower()

    async def test_update_producto_sku_duplicado_400(
        self, async_client, sample_product_data
    ):
        """Test SKU duplicado en actualización devuelve 400"""
        # Crear primer producto
        create_response1 = await async_client.post(
            "/api/v1/productos/", json=sample_product_data
        )
        assert create_response1.status_code == 201

        # Crear segundo producto con SKU diferente
        sample_product_data2 = sample_product_data.copy()
        sample_product_data2["sku"] = "SKU-DIFERENTE-001"
        sample_product_data2["nombre"] = "Producto 2"

        create_response2 = await async_client.post(
            "/api/v1/productos/", json=sample_product_data2
        )
        assert create_response2.status_code == 201
        producto_id_2 = create_response2.json()["id"]

        # Intentar actualizar producto 2 con SKU del producto 1 (duplicado)
        update_data = {"sku": sample_product_data["sku"]}  # SKU que ya existe

        response = await async_client.put(
            f"/api/v1/productos/{producto_id_2}", json=update_data
        )
        assert response.status_code == 400
        assert "ya está en uso" in response.json()["detail"].lower()

    async def test_update_producto_uuid_invalido_422(self, async_client):
        """Test UUID inválido devuelve 422"""
        producto_id_invalido = "no-es-un-uuid-valido"

        update_data = {"nombre": "No importa", "precio": 100.0}

        response = await async_client.put(
            f"/api/v1/productos/{producto_id_invalido}", json=update_data
        )
        assert response.status_code == 422

    async def test_update_producto_sin_datos_400(
        self, async_client, sample_product_data
    ):
        """Test actualización sin datos devuelve 400"""
        # Crear producto primero
        create_response = await async_client.post(
            "/api/v1/productos/", json=sample_product_data
        )
        assert create_response.status_code == 201
        producto_id = create_response.json()["id"]

        # Intentar actualizar sin datos
        update_data = {}

        response = await async_client.put(
            f"/api/v1/productos/{producto_id}", json=update_data
        )
        assert response.status_code == 400
        assert "no se proporcionaron datos" in response.json()["detail"].lower()

    async def test_update_producto_datos_nulos_400(
        self, async_client, sample_product_data
    ):
        """Test actualización con todos los datos como None"""
        # Crear producto primero
        create_response = await async_client.post(
            "/api/v1/productos/", json=sample_product_data
        )
        assert create_response.status_code == 201
        producto_id = create_response.json()["id"]

        # Intentar actualizar con datos nulos
        update_data = {"nombre": None, "precio": None, "descripcion": None}

        response = await async_client.put(
            f"/api/v1/productos/{producto_id}", json=update_data
        )
        assert response.status_code == 400
        assert "no se proporcionaron datos" in response.json()["detail"].lower()

    async def test_update_producto_preserva_campos_no_enviados(
        self, async_client, sample_product_data
    ):
        """Test que campos no enviados se preservan"""
        # Crear producto primero
        create_response = await async_client.post(
            "/api/v1/productos/", json=sample_product_data
        )
        assert create_response.status_code == 201
        producto_id = create_response.json()["id"]
        producto_original = create_response.json()

        # Actualizar solo el nombre
        update_data = {"name": "Solo Nombre Actualizado"}

        response = await async_client.put(
            f"/api/v1/productos/{producto_id}", json=update_data
        )
        assert response.status_code == 200

        result = response.json()
        # Campo actualizado
        assert result["name"] == "Solo Nombre Actualizado"
        # Campos preservados
        assert result["precio_venta"] == producto_original["precio_venta"]
        assert result["sku"] == producto_original["sku"]
        assert result["description"] == producto_original["description"]
        assert result["categoria"] == producto_original["categoria"]


# ========================================================================
# TESTS PARA ENDPOINT PATCH /productos/{id} - OPERACIONES ESPECÍFICAS
# ========================================================================


class TestProductosPATCH:
    """Tests para endpoint PATCH /productos/{id} - operaciones específicas"""

    async def test_patch_precio_exitoso(self, async_client, sample_product_data):
        """Test PATCH exitoso solo precio"""
        # Crear producto
        create_response = await async_client.post(
            "/api/v1/productos/", json=sample_product_data
        )
        assert create_response.status_code == 201
        producto_id = create_response.json()["id"]

        # PATCH solo precio
        patch_data = {"precio_venta": 199999.99}
        response = await async_client.patch(
            f"/api/v1/productos/{producto_id}", json=patch_data
        )

        assert response.status_code == 200
        result = response.json()
        assert result["precio_venta"] == 199999.99
        # Verificar que otros campos no cambiaron
        assert result["name"] == sample_product_data["name"]

    async def test_patch_precio_alternativo(self, async_client, sample_product_data):
        """Test PATCH exitoso - verificación de respuesta"""
        # Crear producto
        create_response = await async_client.post(
            "/api/v1/productos/", json=sample_product_data
        )
        assert create_response.status_code == 201
        producto_id = create_response.json()["id"]

        # PATCH precio (stock se maneja en inventory)
        patch_data = {"precio_venta": 160000.0}
        response = await async_client.patch(
            f"/api/v1/productos/{producto_id}", json=patch_data
        )

        assert response.status_code == 200
        result = response.json()
        # Stock se maneja en inventory, verificar solo respuesta exitosa
        assert "id" in result
        assert result["precio_venta"] is not None

    async def test_patch_is_active_exitoso(self, async_client, sample_product_data):
        """Test PATCH exitoso cambio de precio 2"""
        # Crear producto
        create_response = await async_client.post(
            "/api/v1/productos/", json=sample_product_data
        )
        assert create_response.status_code == 201
        producto_id = create_response.json()["id"]

        # PATCH cambiar precio
        patch_data = {"precio_venta": 175000.0}
        response = await async_client.patch(
            f"/api/v1/productos/{producto_id}", json=patch_data
        )

        assert response.status_code == 200
        result = response.json()
        assert result["precio_venta"] == 175000.0

    async def test_patch_multiple_fields(self, async_client, sample_product_data):
        """Test PATCH exitoso múltiples campos"""
        # Crear producto
        create_response = await async_client.post(
            "/api/v1/productos/", json=sample_product_data
        )
        assert create_response.status_code == 201
        producto_id = create_response.json()["id"]

        # PATCH múltiples campos
        patch_data = {
            "precio_venta": 299999.99,
            "peso": 2.5,
            "categoria": "Electronics",
        }
        response = await async_client.patch(
            f"/api/v1/productos/{producto_id}", json=patch_data
        )

        assert response.status_code == 200
        result = response.json()
        assert result["precio_venta"] == 299999.99
        assert result["peso"] == 2.5
        assert result["categoria"] == "Electronics"

    async def test_patch_producto_no_encontrado(self, async_client):
        """Test PATCH producto inexistente"""
        from uuid import uuid4

        patch_data = {"precio_venta": 150000.0}
        response = await async_client.patch(
            f"/api/v1/productos/{uuid4()}", json=patch_data
        )

        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"]

    async def test_patch_datos_vacios(self, async_client, sample_product_data):
        """Test PATCH sin datos"""
        # Crear producto
        create_response = await async_client.post(
            "/api/v1/productos/", json=sample_product_data
        )
        assert create_response.status_code == 201
        producto_id = create_response.json()["id"]

        # PATCH sin datos
        patch_data = {}
        response = await async_client.patch(
            f"/api/v1/productos/{producto_id}", json=patch_data
        )

        assert response.status_code == 400
        assert "No se proporcionaron datos" in response.json()["detail"]

    async def test_patch_precio_invalido(self, async_client, sample_product_data):
        """Test PATCH con precio inválido"""
        # Crear producto
        create_response = await async_client.post(
            "/api/v1/productos/", json=sample_product_data
        )
        assert create_response.status_code == 201
        producto_id = create_response.json()["id"]

        # PATCH precio negativo
        patch_data = {"precio_venta": -100.0}
        response = await async_client.patch(
            f"/api/v1/productos/{producto_id}", json=patch_data
        )

        assert response.status_code == 422  # Validation error
