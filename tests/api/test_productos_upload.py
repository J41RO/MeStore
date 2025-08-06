# ~/tests/api/test_productos_upload.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Tests de Validación de Upload de Imágenes
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_productos_upload.py
# Ruta: ~/tests/api/test_productos_upload.py
# Autor: Jairo
# Fecha de Creación: 2025-08-05
# Última Actualización: 2025-08-05
# Versión: 1.0.0
# Propósito: Tests comprehensivos para validación de upload de imágenes
#            Incluye casos válidos, inválidos y límites del sistema
#
# Modificaciones:
# 2025-08-05 - Creación inicial con tests de validación completos
#
# ---------------------------------------------------------------------------------------------

"""
Tests para validaciones de upload de imágenes de productos.

Descripción detallada de qué contiene este módulo:
- TestProductosUploadValidation: Clase principal de tests
- create_test_image: Utilidad para crear imágenes de prueba
- test_upload_formato_jpeg_valido: Test de caso exitoso
- test_upload_formato_no_permitido: Test de caso de error
- test_upload_archivo_muy_grande: Test de límites de tamaño
"""

import pytest
from fastapi.testclient import TestClient
from io import BytesIO
from PIL import Image
import tempfile
import os


class TestProductosUploadValidation:
    """Tests para validaciones de upload de imágenes"""

    def create_test_image(self, format="JPEG", size=(100, 100)):
        """Crear imagen de test en memoria"""
        img = Image.new('RGB', size, color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format=format)
        img_bytes.seek(0)
        return img_bytes

    async def test_upload_formato_jpeg_valido(self, async_client, sample_product_data):
        """Test upload JPEG válido"""
        # Crear producto
        create_response = await async_client.post("/api/v1/productos/", json=sample_product_data)
        assert create_response.status_code == 201
        producto_id = create_response.json()["id"]

        # Crear imagen JPEG test
        img_data = self.create_test_image("JPEG")

        # Upload
        files = [("files", ("test.jpg", img_data, "image/jpeg"))]
        response = await async_client.post(f"/api/v1/productos/{producto_id}/imagenes", files=files)

        assert response.status_code == 201
        result = response.json()
        assert result["success"] is True
        assert result["uploaded_count"] == 1
        assert len(result["errors"]) == 0

    async def test_upload_formato_no_permitido(self, async_client, sample_product_data):
        """Test upload formato no permitido"""
        # Crear producto
        create_response = await async_client.post("/api/v1/productos/", json=sample_product_data)
        producto_id = create_response.json()["id"]

        # Intentar upload archivo de texto
        files = [("files", ("test.txt", BytesIO(b"no es imagen"), "text/plain"))]
        response = await async_client.post(f"/api/v1/productos/{producto_id}/imagenes", files=files)

        assert response.status_code == 400
        assert "no permitida" in response.json()["detail"].lower()

    async def test_upload_archivo_muy_grande(self, async_client, sample_product_data):
        """Test upload archivo que excede límite de tamaño"""
        # Crear producto
        create_response = await async_client.post("/api/v1/productos/", json=sample_product_data)
        producto_id = create_response.json()["id"]

        # Crear imagen grande (6MB simulado)
        large_data = BytesIO(b"x" * (6 * 1024 * 1024))

        # Intentar upload
        files = [("files", ("large.jpg", large_data, "image/jpeg"))]
        response = await async_client.post(f"/api/v1/productos/{producto_id}/imagenes", files=files)

        assert response.status_code == 400
        assert "excede" in response.json()["detail"].lower()


def test_url_helper_functionality():
    """Test funcionalidad del helper de URLs."""
    from app.utils.url_helper import build_public_url

    # Test casos normales
    assert build_public_url("uploads/productos/imagenes/test.jpg") == "/media/productos/imagenes/test.jpg"
    assert build_public_url("productos/imagenes/test.jpg") == "/media/productos/imagenes/test.jpg"

    # Test rutas sin uploads/
    assert build_public_url("test.jpg") == "/media/test.jpg"

    # Verificar formato correcto
    result = build_public_url("uploads/productos/imagenes/abc123.jpg")
    assert result.startswith("/media/")
    assert "uploads/" not in result

    # Test casos edge
    assert build_public_url("") == "/media/"
    assert build_public_url("/") == "/media//"

    print("✅ Todos los tests de url_helper pasaron")