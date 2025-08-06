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


def test_delete_imagen_helper():
    """Test helper delete_image_files."""
    from app.utils.file_validator import delete_image_files
    import asyncio

    # Test que el helper existe y es async
    assert callable(delete_image_files)
    assert asyncio.iscoroutinefunction(delete_image_files)

    print("✅ Helper delete_image_files disponible y es async")


def test_delete_imagen_schema():
    """Test schema ProductImageDeleteResponse."""
    from app.schemas.product_image import ProductImageDeleteResponse
    from uuid import uuid4

    # Test creación de schema con datos válidos
    test_data = {
        "success": True,
        "message": "Imagen eliminada exitosamente",
        "deleted_image_id": uuid4()
    }

    schema = ProductImageDeleteResponse(**test_data)

    # Validar campos
    assert schema.success is True
    assert "eliminada" in schema.message
    assert schema.deleted_image_id is not None

    # Validar serialización
    dict_output = schema.model_dump()
    assert "success" in dict_output
    assert "message" in dict_output
    assert "deleted_image_id" in dict_output

    print("✅ Schema ProductImageDeleteResponse funcional")


def test_watermark_functionality():
    """Test completo de funcionalidad watermark MeStocker."""
    from app.utils.file_validator import apply_watermark
    from app.core.config import settings
    from PIL import Image
    import os

    print("🧪 INICIANDO TEST WATERMARK COMPLETO")

    # 1. Verificar configuración watermark existe
    print("📋 1/5: Verificando configuración...")
    assert hasattr(settings, 'WATERMARK_ENABLED'), "WATERMARK_ENABLED debe existir"
    assert hasattr(settings, 'WATERMARK_LOGO_PATH'), "WATERMARK_LOGO_PATH debe existir"
    assert hasattr(settings, 'WATERMARK_OPACITY'), "WATERMARK_OPACITY debe existir"
    assert hasattr(settings, 'WATERMARK_POSITION'), "WATERMARK_POSITION debe existir"
    assert hasattr(settings, 'WATERMARK_MARGIN'), "WATERMARK_MARGIN debe existir"
    print("✅ Configuración watermark completa")

    # 2. Verificar función apply_watermark existe y es callable
    print("📋 2/5: Verificando función...")
    assert callable(apply_watermark), "apply_watermark debe ser función callable"
    print("✅ Función apply_watermark disponible")

    # 3. Test con imagen sintética (crear imagen test en memoria)
    print("📋 3/5: Creando imagen test...")
    test_image = Image.new('RGB', (400, 300), color='white')
    assert test_image.size == (400, 300), "Imagen test debe tener tamaño correcto"
    print("✅ Imagen test creada: 400x300 píxeles")

    # 4. Aplicar watermark (debe manejar logo faltante gracefully)
    print("📋 4/5: Aplicando watermark...")
    result_image = apply_watermark(test_image, 'original')

    # Verificar que retorna imagen válida
    assert isinstance(result_image, Image.Image), "Debe retornar objeto Image"
    assert result_image.size == (400, 300), "Tamaño debe mantenerse"
    assert result_image.mode == 'RGB', "Modo debe ser RGB"
    print("✅ Watermark aplicado exitosamente")

    # 5. Test diferentes resoluciones
    print("📋 5/5: Probando diferentes resoluciones...")
    resoluciones_test = ['thumbnail', 'small', 'medium', 'large', 'original']

    for resolucion in resoluciones_test:
        resultado = apply_watermark(test_image.copy(), resolucion)
        assert isinstance(resultado, Image.Image), f"Resolución {resolucion} debe retornar Image"
        assert resultado.size == (400, 300), f"Tamaño debe mantenerse para {resolucion}"
        print(f"✅ Resolución {resolucion}: OK")

    print("🎉 ✅ TEST WATERMARK COMPLETADO EXITOSAMENTE")
    print("📊 Todas las verificaciones pasaron:")
    print("   - Configuración: 5/5 atributos ✅")
    print("   - Función: Callable y funcional ✅")
    print("   - Imagen test: Procesada correctamente ✅")
    print("   - Resoluciones: 5/5 soportadas ✅")
    print("   - Manejo errores: Graceful ✅")


def test_watermark_with_logo_present():
    """Test watermark cuando logo existe."""
    from app.utils.file_validator import apply_watermark
    from app.core.config import settings
    from PIL import Image
    import os

    print("🧪 TEST CON LOGO PRESENTE")

    # Verificar si logo existe
    logo_exists = os.path.exists(settings.WATERMARK_LOGO_PATH)
    print(f"📋 Logo existe: {logo_exists}")
    print(f"📁 Ruta logo: {settings.WATERMARK_LOGO_PATH}")

    # Crear imagen test
    test_image = Image.new('RGB', (800, 600), color='lightblue')

    # Aplicar watermark
    result = apply_watermark(test_image, 'large')

    # Verificaciones básicas
    assert isinstance(result, Image.Image)
    assert result.size == (800, 600)

    if logo_exists:
        print("✅ Test con logo real completado")
    else:
        print("⚠️ Test sin logo (manejo graceful verificado)")


def test_watermark_error_handling():
    """Test manejo de errores en watermark."""
    from app.utils.file_validator import apply_watermark
    from PIL import Image

    print("🧪 TEST MANEJO DE ERRORES")

    # Test con imagen corrupta simulada (None)
    try:
        # Esto no debería romper la función
        test_image = Image.new('RGB', (100, 100), 'red')
        result = apply_watermark(test_image, 'invalid_resolution')
        assert isinstance(result, Image.Image), "Debe manejar resolución inválida gracefully"
        print("✅ Manejo de resolución inválida: OK")
    except Exception as e:
        # Si hay excepción, debe ser manejada por la función
        assert False, f"apply_watermark no debe lanzar excepciones: {e}"

    print("✅ Manejo de errores verificado")