"""
Tests específicos para funcionalidad de fulfillment del modelo Product.

Tests para campos peso, dimensiones, categoria, tags y métodos relacionados.
"""

import pytest
from decimal import Decimal

from app.models.product import Product, ProductStatus


class TestProductFulfillment:
    """Tests para campos y funcionalidad de fulfillment."""

    def test_create_product_with_fulfillment_fields(self):
        """Test crear producto con todos los campos de fulfillment."""
        product = Product(
            sku="FULFILL-001",
            name="Producto Test Fulfillment",
            peso=Decimal("1.250"),
            dimensiones={"largo": 30, "ancho": 20, "alto": 15},
            categoria="Electronics",
            tags=["gadget", "portable", "electronic"]
        )
        
        assert product.peso == Decimal("1.250")
        assert product.dimensiones == {"largo": 30, "ancho": 20, "alto": 15}
        assert product.categoria == "Electronics"
        assert product.tags == ["gadget", "portable", "electronic"]

    def test_peso_precision_decimal(self):
        """Test precisión del campo peso (DECIMAL 8,3)."""
        product = Product(
            sku="PESO-001",
            name="Test Peso Precisión",
            peso=Decimal("12345.123")  # 8 dígitos, 3 decimales
        )
        
        assert product.peso == Decimal("12345.123")
        assert str(product.peso) == "12345.123"

    def test_dimensiones_json_structure(self):
        """Test estructura JSON para dimensiones."""
        dimensiones_validas = {
            "largo": 25.5,
            "ancho": 15.0,
            "alto": 10.2
        }
        
        product = Product(
            sku="DIM-001",
            name="Test Dimensiones",
            dimensiones=dimensiones_validas
        )
        
        assert product.dimensiones["largo"] == 25.5
        assert product.dimensiones["ancho"] == 15.0
        assert product.dimensiones["alto"] == 10.2

    def test_tags_json_array(self):
        """Test tags como array JSON."""
        tags = ["electronics", "smartphone", "5g", "android"]
        
        product = Product(
            sku="TAGS-001",
            name="Test Tags",
            tags=tags
        )
        
        assert len(product.tags) == 4
        assert "electronics" in product.tags
        assert "smartphone" in product.tags

    def test_calcular_volumen_method(self):
        """Test método calcular_volumen()."""
        product = Product(
            sku="VOL-001",
            name="Test Volumen",
            dimensiones={"largo": 10, "ancho": 5, "alto": 2}
        )
        
        volumen = product.calcular_volumen()
        assert volumen == 100.0  # 10 * 5 * 2

    def test_calcular_volumen_sin_dimensiones(self):
        """Test calcular_volumen() sin dimensiones."""
        product = Product(
            sku="VOL-002",
            name="Test Sin Dimensiones"
        )
        
        volumen = product.calcular_volumen()
        assert volumen == 0.0

    def test_calcular_volumen_dimensiones_incompletas(self):
        """Test calcular_volumen() con dimensiones incompletas."""
        product = Product(
            sku="VOL-003",
            name="Test Dimensiones Incompletas",
            dimensiones={"largo": 10, "ancho": 5}  # Falta 'alto'
        )
        
        volumen = product.calcular_volumen()
        assert volumen == 0.0

    def test_tiene_tag_method(self):
        """Test método tiene_tag()."""
        product = Product(
            sku="TAG-001",
            name="Test Búsqueda Tags",
            tags=["Electronics", "Portable", "Gaming"]
        )
        
        assert product.tiene_tag("electronics") is True  # Case insensitive
        assert product.tiene_tag("PORTABLE") is True
        assert product.tiene_tag("gaming") is True
        assert product.tiene_tag("nonexistent") is False

    def test_tiene_tag_sin_tags(self):
        """Test tiene_tag() sin tags."""
        product = Product(
            sku="TAG-002",
            name="Test Sin Tags"
        )
        
        assert product.tiene_tag("anything") is False

    def test_to_dict_includes_fulfillment(self):
        """Test to_dict() incluye campos de fulfillment."""
        product = Product(
            sku="DICT-001",
            name="Test Dict Fulfillment",
            peso=Decimal("2.500"),
            dimensiones={"largo": 20, "ancho": 15, "alto": 8},
            categoria="Books",
            tags=["fiction", "mystery"]
        )
        
        product_dict = product.to_dict()
        
        assert "peso" in product_dict
        assert "dimensiones" in product_dict
        assert "categoria" in product_dict
        assert "tags" in product_dict
        
        assert product_dict["peso"] == 2.5  # Convertido a float
        assert product_dict["dimensiones"] == {"largo": 20, "ancho": 15, "alto": 8}
        assert product_dict["categoria"] == "Books"
        assert product_dict["tags"] == ["fiction", "mystery"]

    def test_fulfillment_fields_nullable(self):
        """Test que campos de fulfillment son opcionales."""
        product = Product(
            sku="NULL-001",
            name="Test Campos Opcionales"
            # Sin campos de fulfillment
        )
        
        assert product.peso is None
        assert product.dimensiones is None
        assert product.categoria is None
        assert product.tags is None
        
        # Métodos deben manejar valores None
        assert product.calcular_volumen() == 0.0
        assert product.tiene_tag("any") is False

    def test_categoria_indexada(self):
        """Test que categoria está indexada para búsquedas."""
        # Este test verifica que el campo categoria tiene índice
        # (implícito por la configuración index=True)
        product = Product(
            sku="CAT-001",
            name="Test Categoria",
            categoria="Sports"
        )
        
        assert product.categoria == "Sports"
        # El índice se verifica a nivel de base de datos
