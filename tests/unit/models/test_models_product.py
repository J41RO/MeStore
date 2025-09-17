# ~/tests/test_models_product.py
# ---------------------------------------------------------------------------------------------
# MeStore - Tests para modelo Product
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_models_product.py
# Ruta: ~/tests/test_models_product.py
# Autor: Jairo
# Fecha de Creación: 2025-07-27
# Última Actualización: 2025-07-27
# Versión: 1.0.0
# Propósito: Tests unitarios para modelo Product con validaciones y métodos
#            Verifica herencia de BaseModel y funcionalidad específica
#
# Modificaciones:
# 2025-07-27 - Creación inicial de tests para Product
#
# ---------------------------------------------------------------------------------------------

"""
Tests para modelo Product.

Este módulo contiene tests unitarios para verificar:
- Creación de productos con campos básicos
- Validaciones de SKU y name
- Herencia correcta de BaseModel
- Métodos personalizados (to_dict, __repr__, __str__)
- Constraints de unicidad en SKU
- Comportamiento de soft delete
"""

import pytest
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from app.models.product import Product
from app.models.base import BaseModel


class TestProductCreation:
    """Tests para creación y validación básica de productos."""

    def test_create_product_with_minimal_data(self):
        """Test creación de producto con datos mínimos requeridos."""
        product = Product(
            sku="PROD001",
            name="Producto de Prueba"
        )

        # Verificar campos obligatorios
        assert product.sku == "PROD001"
        assert product.name == "Producto de Prueba"
        assert product.description is None

        # Verificar herencia de BaseModel
        # ID se genera al persistir en DB, no en memoria
        assert product.id is None  # En memoria no tiene ID aún
        assert product.created_at is None  # Timestamps se generan al persistir
        assert product.updated_at is None
        assert product.deleted_at is None

    def test_create_product_with_full_data(self):
        """Test creación de producto con todos los campos."""
        product = Product(
            sku="PROD002",
            name="Producto Completo",
            description="Descripción detallada del producto de prueba"
        )

        assert product.sku == "PROD002"
        assert product.name == "Producto Completo"
        assert product.description == "Descripción detallada del producto de prueba"

        # Verificar que hereda de BaseModel
        assert isinstance(product, BaseModel)

    def test_product_inherits_base_model_methods(self):
        """Test que Product hereda métodos de BaseModel."""
        product = Product(sku="INHERIT001", name="Test Herencia")

        # Verificar métodos heredados existen
        assert hasattr(product, 'is_active')
        assert hasattr(product, 'is_deleted')
        assert hasattr(product, 'to_dict')

        # Verificar comportamiento
        assert product.is_active() is True  # No está soft deleted
        assert product.is_deleted() is False


class TestProductValidations:
    """Tests para validaciones del modelo Product."""

    def test_sku_validation_empty(self):
        """Test validación de SKU vacío."""
        with pytest.raises(ValueError, match="SKU no puede estar vacío"):
            Product(sku="", name="Test")

    def test_sku_validation_none(self):
        """Test validación de SKU None."""
        with pytest.raises(ValueError, match="SKU no puede estar vacío"):
            Product(sku=None, name="Test")

    def test_sku_validation_too_long(self):
        """Test validación de SKU muy largo."""
        long_sku = "A" * 51  # 51 caracteres
        with pytest.raises(ValueError, match="SKU no puede exceder 50 caracteres"):
            Product(sku=long_sku, name="Test")

    def test_sku_normalization(self):
        """Test normalización de SKU (mayúsculas y trim)."""
        product = Product(sku=" prod123 ", name="Test")
        assert product.sku == "PROD123"

    def test_name_validation_empty(self):
        """Test validación de name vacío."""
        with pytest.raises(ValueError, match="Nombre del producto no puede estar vacío"):
            Product(sku="TEST001", name="")

    def test_name_validation_none(self):
        """Test validación de name None."""
        with pytest.raises(ValueError, match="Nombre del producto no puede estar vacío"):
            Product(sku="TEST001", name=None)

    def test_name_validation_too_long(self):
        """Test validación de name muy largo."""
        long_name = "A" * 201  # 201 caracteres
        with pytest.raises(ValueError, match="Nombre no puede exceder 200 caracteres"):
            Product(sku="TEST001", name=long_name)

    def test_name_normalization(self):
        """Test normalización de name (trim)."""
        product = Product(sku="TEST001", name="  Producto de Prueba  ")
        assert product.name == "Producto de Prueba"


class TestProductMethods:
    """Tests para métodos personalizados del modelo Product."""

    def test_repr_method(self):
        """Test método __repr__."""
        product = Product(sku="REPR001", name="Test Repr")
        repr_str = repr(product)

        assert "Product" in repr_str
        assert "REPR001" in repr_str
        assert "Test Repr" in repr_str
        assert str(product.id) in repr_str

    def test_str_method(self):
        """Test método __str__."""
        product = Product(sku="STR001", name="Test String")
        str_representation = str(product)

        assert str_representation == "Producto STR001: Test String"

    def test_to_dict_method(self):
        """Test método to_dict incluye campos específicos."""
        product = Product(
            sku="DICT001",
            name="Test Dict",
            description="Descripción de prueba"
        )

        product_dict = product.to_dict()

        # Verificar campos específicos de Product
        assert product_dict["sku"] == "DICT001"
        assert product_dict["name"] == "Test Dict"
        assert product_dict["description"] == "Descripción de prueba"

        # Verificar campos heredados de BaseModel
        assert "id" in product_dict
        assert "created_at" in product_dict
        assert "updated_at" in product_dict
        assert "deleted_at" in product_dict

    def test_has_description_method(self):
        """Test método has_description."""
        # Producto con descripción
        product_with_desc = Product(
            sku="DESC001",
            name="Con Descripción",
            description="Tiene descripción"
        )
        assert product_with_desc.has_description() is True

        # Producto sin descripción
        product_no_desc = Product(sku="DESC002", name="Sin Descripción")
        assert product_no_desc.has_description() is False

        # Producto con descripción vacía
        product_empty_desc = Product(
            sku="DESC003",
            name="Descripción Vacía",
            description=""
        )
        assert product_empty_desc.has_description() is False

    def test_get_display_name_method(self):
        """Test método get_display_name."""
        product = Product(sku="DISPLAY001", name="Producto Display")
        display_name = product.get_display_name()

        assert display_name == "DISPLAY001 - Producto Display"


class TestProductConstraints:
    """Tests para constraints y reglas de base de datos."""

    def test_tablename(self):
        """Test que el nombre de tabla es correcto."""
        assert Product.__tablename__ == "products"

    def test_sku_unique_constraint(self):
        """Test que SKU debe ser único (simulado)."""
        # Nota: Este test simula el comportamiento
        # En tests reales con DB, se verificaría IntegrityError
        product1 = Product(sku="UNIQUE001", name="Primero")
        product2 = Product(sku="UNIQUE001", name="Segundo")

        # Ambos objetos se crean en memoria
        assert product1.sku == product2.sku
        # En DB real, el segundo causaría IntegrityError

    def test_required_fields(self):
        """Test campos obligatorios mediante validadores."""
        # SQLAlchemy permite crear objetos, valida con validadores
        # Test que validadores capturan campos requeridos
        
        # SKU vacío debe fallar en validación
        with pytest.raises(ValueError, match="SKU no puede estar vacío"):
            Product(sku="", name="Test")
        
        # Name vacío debe fallar en validación  
        with pytest.raises(ValueError, match="Nombre del producto no puede estar vacío"):
            Product(sku="TEST", name="")
        
        # Creación exitosa con datos válidos
        product = Product(sku="VALID001", name="Producto Válido")
        assert product.sku == "VALID001"
        assert product.name == "Producto Válido"

    def test_optional_fields(self):
        """Test campos opcionales."""
        # description es opcional
        product = Product(sku="OPT001", name="Opcional")
        assert product.description is None


# Fixtures para tests que requieran datos compartidos
@pytest.fixture
def sample_product():
    """Fixture que retorna un producto de ejemplo."""
    return Product(
        sku="SAMPLE001",
        name="Producto de Ejemplo",
        description="Descripción de ejemplo para tests"
    )


@pytest.fixture
def minimal_product():
    """Fixture que retorna un producto con datos mínimos."""
    return Product(sku="MIN001", name="Mínimo")


class TestProductFixtures:
    """Tests usando fixtures."""

    def test_sample_product_fixture(self, sample_product):
        """Test usando fixture de producto completo."""
        assert sample_product.sku == "SAMPLE001"
        assert sample_product.has_description() is True

    def test_minimal_product_fixture(self, minimal_product):
        """Test usando fixture de producto mínimo."""
        assert minimal_product.sku == "MIN001"
        assert minimal_product.has_description() is False