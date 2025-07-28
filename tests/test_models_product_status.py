# ~/tests/test_models_product_status.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Tests para ProductStatus Enum
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_models_product_status.py
# Ruta: ~/tests/test_models_product_status.py
# Autor: Jairo
# Fecha de Creación: 2025-07-27
# Última Actualización: 2025-07-27
# Versión: 1.0.0
# Propósito: Tests específicos para enum ProductStatus y campo status
#
# Modificaciones:
# 2025-07-27 - Creación inicial con tests básicos de enum
#
# ---------------------------------------------------------------------------------------------

"""
Tests para ProductStatus enum y funcionalidad de campo status.

Tests incluidos:
- Verificación de valores enum
- Default status en creación
- Modificación de status
- Serialización to_dict con status
- Validación de estados válidos
"""

import pytest
from app.models.product import Product, ProductStatus


class TestProductStatus:
    """Tests para enum ProductStatus."""

    def test_product_status_enum_values(self):
        """Verificar que ProductStatus tiene los 4 valores correctos."""
        expected_values = ['TRANSITO', 'VERIFICADO', 'DISPONIBLE', 'VENDIDO']
        actual_values = [status.value for status in ProductStatus]

        assert len(ProductStatus) == 4
        assert all(value in actual_values for value in expected_values)
        assert actual_values == expected_values

    def test_product_status_enum_names(self):
        """Verificar nombres de enum ProductStatus."""
        expected_names = ['TRANSITO', 'VERIFICADO', 'DISPONIBLE', 'VENDIDO']
        actual_names = [status.name for status in ProductStatus]

        assert actual_names == expected_names

    def test_product_status_default_value(self):
        """Verificar que ProductStatus.TRANSITO es el valor por defecto."""
        assert ProductStatus.TRANSITO.value == 'TRANSITO'

        # Verificar que es el primer valor (default implícito)
        statuses = list(ProductStatus)
        assert statuses[0] == ProductStatus.TRANSITO


class TestProductStatusField:
    """Tests para campo status en modelo Product."""

    def test_product_has_status_field(self):
        """Verificar que modelo Product tiene campo status."""
        # Verificar que campo existe en columnas
        columns = [col.name for col in Product.__table__.columns]
        assert 'status' in columns

        # Verificar tipo de columna status
        status_column = None
        for col in Product.__table__.columns:
            if col.name == 'status':
                status_column = col
                break

        assert status_column is not None
        assert not status_column.nullable  # NOT NULL
        assert status_column.default is not None  # Tiene default

    def test_product_creation_with_default_status(self):
        """Verificar que Product se crea con status por defecto."""
        product = Product(
            sku='TEST-STATUS-001',
            name='Test Product',
            description='Test description'
        )

        # En Python object, status puede ser None hasta flush
        # Pero el default está configurado para la base de datos
        status_column = Product.__table__.columns['status']
        default_value = status_column.default.arg
        assert default_value == ProductStatus.TRANSITO

    def test_product_creation_with_specific_status(self):
        """Verificar que Product se puede crear con status específico."""
        product = Product(
            sku='TEST-STATUS-002',
            name='Test Product Available',
            description='Test description',
            status=ProductStatus.DISPONIBLE
        )

        assert product.status == ProductStatus.DISPONIBLE

    def test_product_status_modification(self):
        """Verificar que status de Product se puede modificar."""
        product = Product(
            sku='TEST-STATUS-003',
            name='Test Product',
            description='Test description',
            status=ProductStatus.TRANSITO
        )

        # Modificar status
        product.status = ProductStatus.VERIFICADO
        assert product.status == ProductStatus.VERIFICADO

        # Modificar a otro status
        product.status = ProductStatus.DISPONIBLE
        assert product.status == ProductStatus.DISPONIBLE

        # Modificar a VENDIDO
        product.status = ProductStatus.VENDIDO
        assert product.status == ProductStatus.VENDIDO

    def test_product_to_dict_includes_status(self):
        """Verificar que to_dict() incluye campo status."""
        product = Product(
            sku='TEST-STATUS-004',
            name='Test Product Dict',
            description='Test to_dict with status',
            status=ProductStatus.DISPONIBLE
        )

        product_dict = product.to_dict()

        # Verificar que status está en diccionario
        assert 'status' in product_dict
        assert product_dict['status'] == 'DISPONIBLE'

    def test_product_to_dict_with_none_status(self):
        """Verificar que to_dict() maneja status None correctamente."""
        product = Product(
            sku='TEST-STATUS-005',
            name='Test Product None',
            description='Test to_dict with None status'
        )

        # Status será None hasta flush en base de datos
        product_dict = product.to_dict()

        # Verificar que status está en diccionario
        assert 'status' in product_dict
        # Valor será None hasta que se aplique default en DB
        assert product_dict['status'] == 'TRANSITO'  # __init__ aplica default automáticamente

    def test_product_to_dict_with_manual_none_status(self):
        """Test to_dict method cuando se fuerza status a None manualmente."""
        product = Product(
            sku="TEST-NONE-001",
            name="Test Product None",
            description="Test product for none status"
        )

        # Forzar status a None después de __init__ (caso edge)
        product.status = None

        product_dict = product.to_dict()

        # Verificar estructura básica
        assert 'id' in product_dict
        assert 'sku' in product_dict
        assert 'status' in product_dict

        # En este caso específico, status debería ser None
        assert product_dict["status"] is None  # Forzado a None manualmente

    def test_all_product_status_values_assignable(self):
        """Verificar que todos los valores de ProductStatus son asignables."""
        base_product_data = {
            'sku': 'TEST-STATUS-ALL',
            'name': 'Test All Status',
            'description': 'Test all status values'
        }

        for status in ProductStatus:
            product = Product(**base_product_data, status=status)
            assert product.status == status

            # Verificar serialización
            product_dict = product.to_dict()
            assert product_dict['status'] == status.value


# Tests de integración básicos
class TestProductStatusIntegration:
    """Tests de integración para ProductStatus."""

    def test_product_model_column_count(self):
        """Verificar que Product tiene exactamente 11 columnas incluyendo status y pricing."""
        expected_columns = [
            'sku', 'name', 'description', 'status',
            'precio_venta', 'precio_costo', 'comision_mestocker',
            'id', 'created_at', 'updated_at', 'deleted_at'
        ]

        actual_columns = [col.name for col in Product.__table__.columns]

        assert len(actual_columns) == 11
        assert all(col in actual_columns for col in expected_columns)

    def test_pricing_fields_exist(self):
        """Verificar que los campos de pricing existen en el modelo."""
        pricing_fields = ['precio_venta', 'precio_costo', 'comision_mestocker']
        actual_columns = [col.name for col in Product.__table__.columns]

        for field in pricing_fields:
            assert field in actual_columns, f"Campo {field} no encontrado en modelo Product"

    def test_pricing_fields_are_decimal(self):
        """Verificar que los campos de pricing son tipo DECIMAL."""
        from sqlalchemy import DECIMAL

        pricing_fields = ['precio_venta', 'precio_costo', 'comision_mestocker']

        for field_name in pricing_fields:
            column = getattr(Product, field_name)
            assert isinstance(column.type, DECIMAL), f"Campo {field_name} no es tipo DECIMAL"
            assert column.type.precision == 10, f"Campo {field_name} no tiene precisión 10"
            assert column.type.scale == 2, f"Campo {field_name} no tiene escala 2"
            assert column.nullable == True, f"Campo {field_name} debería ser nullable"

    def test_product_status_enum_consistency(self):
        """Verificar consistencia entre enum y valores esperados en proyecto."""
        # Verificar que enum tiene valores esperados para marketplace
        workflow_statuses = {
            ProductStatus.TRANSITO: 'Producto en tránsito hacia almacén',
            ProductStatus.VERIFICADO: 'Producto verificado y en proceso de catalogación',
            ProductStatus.DISPONIBLE: 'Producto disponible para venta',
            ProductStatus.VENDIDO: 'Producto vendido y no disponible'
        }

        # Verificar que todos los estados del workflow están disponibles
        for status, description in workflow_statuses.items():
            assert isinstance(status, ProductStatus)
            assert status.value in ['TRANSITO', 'VERIFICADO', 'DISPONIBLE', 'VENDIDO']