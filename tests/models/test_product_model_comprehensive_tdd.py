# ~/tests/models/test_product_model_comprehensive_tdd.py
# ---------------------------------------------------------------------------------------------
# MeStore - Comprehensive TDD Tests for Product Model
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# TDD SPECIALIST COMPREHENSIVE COVERAGE MISSION
# Model: app/models/product.py
# Target Coverage: 85%+
# Methodology: RED-GREEN-REFACTOR
#
# COVERAGE ANALYSIS:
# - Basic CRUD operations and validation
# - Stock management methods
# - Category management (primary/secondary)
# - Business logic (pricing, margins, volume)
# - Vendor management and relationships
# - Status transitions and workflow
# - Search and tagging functionality
# - Migration utilities
# - Edge cases and error handling
# ---------------------------------------------------------------------------------------------

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.product import Product, ProductStatus
from app.models.inventory import Inventory, InventoryStatus
from app.models.base import BaseModel


class TestProductModelBasics:
    """TDD: Test basic Product model functionality and validation"""

    @pytest.mark.tdd
    def test_product_creation_minimal_fields(self, db_session):
        """Test creating product with minimal required fields"""
        product = Product(
            sku="PROD-001",
            name="Smartphone Samsung"
        )
        db_session.add(product)
        db_session.commit()

        assert product.id is not None
        assert product.sku == "PROD-001"
        assert product.name == "Smartphone Samsung"
        assert product.status == ProductStatus.TRANSITO
        assert product.version == 1

    @pytest.mark.tdd
    def test_product_creation_all_fields(self, db_session):
        """Test creating product with all fields"""
        product = Product(
            sku="PROD-002",
            name="iPhone 15 Pro",
            description="Latest iPhone with advanced features",
            status=ProductStatus.DISPONIBLE,
            precio_venta=Decimal("3500000.00"),
            precio_costo=Decimal("2800000.00"),
            comision_mestocker=Decimal("525000.00"),
            peso=Decimal("0.187"),
            dimensiones='{"largo": 15.9, "ancho": 7.68, "alto": 0.83}',
            categoria="Smartphones",
            tags='["premium", "apple", "5g", "pro"]'
        )
        db_session.add(product)
        db_session.commit()

        assert product.name == "iPhone 15 Pro"
        assert product.description == "Latest iPhone with advanced features"
        assert product.status == ProductStatus.DISPONIBLE
        assert product.precio_venta == Decimal("3500000.00")
        assert product.peso == Decimal("0.187")
        assert '"premium"' in product.tags

    @pytest.mark.tdd
    def test_sku_validation_empty(self, db_session):
        """Test SKU validation with empty value"""
        with pytest.raises(ValueError, match="SKU no puede estar vacío"):
            Product(sku="", name="Test Product")

    @pytest.mark.tdd
    def test_sku_validation_too_long(self, db_session):
        """Test SKU validation with too long value"""
        long_sku = "A" * 51  # Exceeds 50 char limit
        with pytest.raises(ValueError, match="SKU no puede exceder 50 caracteres"):
            Product(sku=long_sku, name="Test Product")

    @pytest.mark.tdd
    def test_sku_normalization(self, db_session):
        """Test SKU normalization to uppercase"""
        product = Product(sku="prod-001", name="Test Product")
        assert product.sku == "PROD-001"

    @pytest.mark.tdd
    def test_name_validation_empty(self, db_session):
        """Test name validation with empty value"""
        with pytest.raises(ValueError, match="Nombre del producto no puede estar vacío"):
            Product(sku="PROD-001", name="")

    @pytest.mark.tdd
    def test_name_validation_too_long(self, db_session):
        """Test name validation with too long value"""
        long_name = "A" * 201  # Exceeds 200 char limit
        with pytest.raises(ValueError, match="Nombre no puede exceder 200 caracteres"):
            Product(sku="PROD-001", name=long_name)

    @pytest.mark.tdd
    def test_name_validation_whitespace(self, db_session):
        """Test name validation strips whitespace"""
        product = Product(sku="PROD-001", name="  Test Product  ")
        assert product.name == "Test Product"


class TestProductStockManagement:
    """TDD: Test product stock tracking functionality"""

    @pytest.mark.tdd
    def test_get_stock_total_no_inventory(self, db_session):
        """Test get_stock_total with no inventory locations"""
        product = Product(sku="PROD-001", name="Test Product")
        product.ubicaciones_inventario = []

        assert product.get_stock_total() == 0

    @pytest.mark.tdd
    def test_get_stock_total_with_inventory(self, db_session):
        """Test get_stock_total with inventory locations"""
        product = Product(sku="PROD-001", name="Test Product")
        db_session.add(product)
        db_session.flush()  # Get product ID

        # Create real inventory locations
        inv1 = Inventory(
            product_id=product.id,
            zona="A",
            estante="01",
            posicion="001",
            cantidad=10,
            cantidad_reservada=0
        )
        inv2 = Inventory(
            product_id=product.id,
            zona="A",
            estante="01",
            posicion="002",
            cantidad=15,
            cantidad_reservada=0
        )

        db_session.add_all([inv1, inv2])
        db_session.flush()

        # Refresh product to load relationship
        db_session.refresh(product)

        assert product.get_stock_total() == 25

    @pytest.mark.tdd
    def test_get_stock_disponible(self, db_session):
        """Test get_stock_disponible calculation"""
        product = Product(sku="PROD-002", name="Test Product")
        db_session.add(product)
        db_session.flush()

        # Create real inventory locations with reserved stock
        inv1 = Inventory(
            product_id=product.id,
            zona="A",
            estante="01",
            posicion="001",
            cantidad=10,
            cantidad_reservada=2
        )
        inv2 = Inventory(
            product_id=product.id,
            zona="A",
            estante="01",
            posicion="002",
            cantidad=15,
            cantidad_reservada=3
        )

        db_session.add_all([inv1, inv2])
        db_session.flush()

        # Refresh product to load relationship
        db_session.refresh(product)

        assert product.get_stock_disponible() == 20  # (10-2) + (15-3) = 8 + 12 = 20

    @pytest.mark.tdd
    def test_get_stock_reservado(self, db_session):
        """Test get_stock_reservado calculation"""
        product = Product(sku="PROD-003", name="Test Product")
        db_session.add(product)
        db_session.flush()

        # Create real inventory locations with reserved stock
        inv1 = Inventory(
            product_id=product.id,
            zona="A",
            estante="01",
            posicion="001",
            cantidad=10,
            cantidad_reservada=2
        )
        inv2 = Inventory(
            product_id=product.id,
            zona="A",
            estante="01",
            posicion="002",
            cantidad=15,
            cantidad_reservada=3
        )

        db_session.add_all([inv1, inv2])
        db_session.flush()

        # Refresh product to load relationship
        db_session.refresh(product)

        assert product.get_stock_reservado() == 5

    @pytest.mark.tdd
    def test_tiene_stock_disponible_true(self, db_session):
        """Test tiene_stock_disponible returns True when stock available"""
        product = Product(sku="PROD-001", name="Test Product")

        with patch.object(product, 'get_stock_disponible', return_value=10):
            assert product.tiene_stock_disponible() is True

    @pytest.mark.tdd
    def test_tiene_stock_disponible_false(self, db_session):
        """Test tiene_stock_disponible returns False when no stock"""
        product = Product(sku="PROD-001", name="Test Product")

        with patch.object(product, 'get_stock_disponible', return_value=0):
            assert product.tiene_stock_disponible() is False

    @pytest.mark.tdd
    def test_is_low_stock_true(self, db_session):
        """Test is_low_stock returns True when below threshold"""
        product = Product(sku="PROD-001", name="Test Product")

        with patch.object(product, 'get_stock_total', return_value=5):
            assert product.is_low_stock(10) is True

    @pytest.mark.tdd
    def test_is_low_stock_false(self, db_session):
        """Test is_low_stock returns False when above threshold"""
        product = Product(sku="PROD-001", name="Test Product")

        with patch.object(product, 'get_stock_total', return_value=15):
            assert product.is_low_stock(10) is False


class TestProductCategoryManagement:
    """TDD: Test product category management functionality"""

    @pytest.mark.tdd
    def test_get_primary_category_exists(self, db_session):
        """Test get_primary_category when primary category exists"""
        product = Product(sku="PROD-001", name="Test Product")

        # Mock category associations
        mock_assoc1 = Mock()
        mock_assoc1.is_primary = False
        mock_assoc1.category = Mock()
        mock_assoc1.category.name = "Secondary"

        mock_assoc2 = Mock()
        mock_assoc2.is_primary = True
        mock_assoc2.category = Mock()
        mock_assoc2.category.name = "Primary"

        product.category_associations = [mock_assoc1, mock_assoc2]

        primary = product.get_primary_category()
        assert primary.name == "Primary"

    @pytest.mark.tdd
    def test_get_primary_category_none(self, db_session):
        """Test get_primary_category when no primary category exists"""
        product = Product(sku="PROD-001", name="Test Product")

        # Mock category associations with no primary
        mock_assoc = Mock()
        mock_assoc.is_primary = False
        product.category_associations = [mock_assoc]

        assert product.get_primary_category() is None

    @pytest.mark.tdd
    def test_get_secondary_categories(self, db_session):
        """Test get_secondary_categories returns non-primary categories"""
        product = Product(sku="PROD-001", name="Test Product")

        # Mock category associations
        mock_assoc1 = Mock()
        mock_assoc1.is_primary = True
        mock_assoc1.category = Mock()
        mock_assoc1.category.name = "Primary"

        mock_assoc2 = Mock()
        mock_assoc2.is_primary = False
        mock_assoc2.category = Mock()
        mock_assoc2.category.name = "Secondary1"

        mock_assoc3 = Mock()
        mock_assoc3.is_primary = False
        mock_assoc3.category = Mock()
        mock_assoc3.category.name = "Secondary2"

        product.category_associations = [mock_assoc1, mock_assoc2, mock_assoc3]

        secondary = product.get_secondary_categories()
        assert len(secondary) == 2
        assert secondary[0].name == "Secondary1"
        assert secondary[1].name == "Secondary2"

    @pytest.mark.tdd
    def test_add_category(self, db_session):
        """Test add_category functionality"""
        product = Product(sku="PROD-001", name="Test Product")
        product.id = "test-product-id"
        product.category_associations = []

        # Mock category
        mock_category = Mock()
        mock_category.id = "test-category-id"

        with patch('app.models.category.ProductCategory') as MockProductCategory:
            mock_association = Mock()
            MockProductCategory.return_value = mock_association

            product.add_category(mock_category, is_primary=True, sort_order=1)

            MockProductCategory.assert_called_once_with(
                product_id="test-product-id",
                category_id="test-category-id",
                is_primary=True,
                sort_order=1,
                assigned_by_id=None
            )
            assert mock_association in product.category_associations

    @pytest.mark.tdd
    def test_has_category_true(self, db_session):
        """Test has_category returns True when category exists"""
        product = Product(sku="PROD-001", name="Test Product")

        mock_category = Mock()
        mock_category.id = "test-category-id"

        mock_assoc = Mock()
        mock_assoc.category_id = "test-category-id"
        product.category_associations = [mock_assoc]

        assert product.has_category(mock_category) is True

    @pytest.mark.tdd
    def test_has_category_false(self, db_session):
        """Test has_category returns False when category doesn't exist"""
        product = Product(sku="PROD-001", name="Test Product")

        mock_category = Mock()
        mock_category.id = "different-category-id"

        mock_assoc = Mock()
        mock_assoc.category_id = "test-category-id"
        product.category_associations = [mock_assoc]

        assert product.has_category(mock_category) is False


class TestProductBusinessLogic:
    """TDD: Test product business logic methods"""

    @pytest.mark.tdd
    def test_calcular_margen_with_prices(self, db_session):
        """Test calcular_margen with valid prices"""
        product = Product(
            sku="PROD-001",
            name="Test Product",
            precio_venta=Decimal("100.00"),
            precio_costo=Decimal("70.00")
        )

        margen = product.calcular_margen()
        assert margen == 30.0

    @pytest.mark.tdd
    def test_calcular_margen_no_prices(self, db_session):
        """Test calcular_margen with no prices"""
        product = Product(sku="PROD-001", name="Test Product")

        margen = product.calcular_margen()
        assert margen == 0.0

    @pytest.mark.tdd
    def test_calcular_porcentaje_margen(self, db_session):
        """Test calcular_porcentaje_margen calculation"""
        product = Product(
            sku="PROD-001",
            name="Test Product",
            precio_venta=Decimal("100.00"),
            precio_costo=Decimal("80.00")
        )

        porcentaje = product.calcular_porcentaje_margen()
        assert porcentaje == 25.0

    @pytest.mark.tdd
    def test_calcular_porcentaje_margen_zero_cost(self, db_session):
        """Test calcular_porcentaje_margen with zero cost"""
        product = Product(
            sku="PROD-001",
            name="Test Product",
            precio_venta=Decimal("100.00"),
            precio_costo=Decimal("0.00")
        )

        porcentaje = product.calcular_porcentaje_margen()
        assert porcentaje == 0.0

    @pytest.mark.tdd
    def test_calcular_volumen_valid_dimensions(self, db_session):
        """Test calcular_volumen with valid dimensions"""
        product = Product(sku="PROD-001", name="Test Product")
        product.dimensiones = {"largo": 10, "ancho": 5, "alto": 2}

        volumen = product.calcular_volumen()
        assert volumen == 100.0

    @pytest.mark.tdd
    def test_calcular_volumen_invalid_dimensions(self, db_session):
        """Test calcular_volumen with invalid dimensions"""
        product = Product(sku="PROD-001", name="Test Product")
        product.dimensiones = {"largo": 10, "ancho": 5}  # Missing 'alto'

        volumen = product.calcular_volumen()
        assert volumen == 0.0

    @pytest.mark.tdd
    def test_tiene_tag_true(self, db_session):
        """Test tiene_tag returns True when tag exists"""
        product = Product(sku="PROD-001", name="Test Product")
        product.tags = ["premium", "featured", "sale"]

        assert product.tiene_tag("Premium") is True  # Case insensitive

    @pytest.mark.tdd
    def test_tiene_tag_false(self, db_session):
        """Test tiene_tag returns False when tag doesn't exist"""
        product = Product(sku="PROD-001", name="Test Product")
        product.tags = ["premium", "featured"]

        assert product.tiene_tag("sale") is False

    @pytest.mark.tdd
    def test_has_description_true(self, db_session):
        """Test has_description returns True with valid description"""
        product = Product(
            sku="PROD-001",
            name="Test Product",
            description="This is a detailed description"
        )

        assert product.has_description() is True

    @pytest.mark.tdd
    def test_has_description_false(self, db_session):
        """Test has_description returns False with empty description"""
        product = Product(sku="PROD-001", name="Test Product")

        assert product.has_description() is False

    @pytest.mark.tdd
    def test_get_display_name(self, db_session):
        """Test get_display_name format"""
        product = Product(sku="PROD-001", name="Test Product")

        display_name = product.get_display_name()
        assert display_name == "PROD-001 - Test Product"


class TestProductVersioning:
    """TDD: Test product versioning and tracking"""

    @pytest.mark.tdd
    def test_increment_version_initial(self, db_session):
        """Test increment_version from initial state"""
        product = Product(sku="PROD-001", name="Test Product")
        product.version = None

        product.increment_version()
        assert product.version == 1

    @pytest.mark.tdd
    def test_increment_version_existing(self, db_session):
        """Test increment_version with existing version"""
        product = Product(sku="PROD-001", name="Test Product")
        product.version = 5

        product.increment_version()
        assert product.version == 6

    @pytest.mark.tdd
    def test_update_tracking(self, db_session):
        """Test update_tracking sets updated_by_id and increments version"""
        product = Product(sku="PROD-001", name="Test Product")
        product.version = 1

        product.update_tracking("user-123")

        assert product.updated_by_id == "user-123"
        assert product.version == 2

    @pytest.mark.tdd
    def test_set_vendedor(self, db_session):
        """Test set_vendedor functionality"""
        product = Product(sku="PROD-001", name="Test Product")
        product.version = 1

        product.set_vendedor("vendor-123")

        assert product.vendedor_id == "vendor-123"
        assert product.version == 2

    @pytest.mark.tdd
    def test_is_vendido_por_true(self, db_session):
        """Test is_vendido_por returns True for correct vendor"""
        product = Product(sku="PROD-001", name="Test Product")
        product.vendedor_id = "vendor-123"

        assert product.is_vendido_por("vendor-123") is True

    @pytest.mark.tdd
    def test_is_vendido_por_false(self, db_session):
        """Test is_vendido_por returns False for different vendor"""
        product = Product(sku="PROD-001", name="Test Product")
        product.vendedor_id = "vendor-123"

        assert product.is_vendido_por("vendor-456") is False


class TestProductSerialization:
    """TDD: Test product serialization methods"""

    @pytest.mark.tdd
    def test_to_dict_basic(self, db_session):
        """Test to_dict with basic product data"""
        product = Product(
            sku="PROD-001",
            name="Test Product",
            description="Test description",
            status=ProductStatus.DISPONIBLE,
            precio_venta=Decimal("100.00"),
            version=1
        )

        # Mock required methods
        product.get_stock_total = Mock(return_value=10)
        product.get_stock_disponible = Mock(return_value=8)
        product.get_stock_reservado = Mock(return_value=2)
        product.tiene_stock_disponible = Mock(return_value=True)
        product.get_primary_category = Mock(return_value=None)
        product.get_secondary_categories = Mock(return_value=[])
        product.ubicaciones_inventario = []
        product.category_associations = []

        result = product.to_dict()

        assert result["sku"] == "PROD-001"
        assert result["name"] == "Test Product"
        assert result["description"] == "Test description"
        assert result["status"] == "DISPONIBLE"
        assert result["precio_venta"] == 100.00
        assert result["version"] == 1
        assert result["stock_total"] == 10
        assert result["stock_disponible"] == 8
        assert result["tiene_stock"] is True

    @pytest.mark.tdd
    def test_repr_method(self, db_session):
        """Test __repr__ method"""
        product = Product(sku="PROD-001", name="Test Product")
        product.id = "test-uuid"

        repr_str = repr(product)

        assert "Product" in repr_str
        assert "test-uuid" in repr_str
        assert "PROD-001" in repr_str
        assert "Test Product" in repr_str

    @pytest.mark.tdd
    def test_str_method(self, db_session):
        """Test __str__ method"""
        product = Product(sku="PROD-001", name="Test Product")

        str_repr = str(product)

        assert str_repr == "Producto PROD-001: Test Product"


class TestProductClassMethods:
    """TDD: Test product class methods"""

    @pytest.mark.tdd
    def test_get_low_stock_products(self, db_session):
        """Test get_low_stock_products class method"""
        with patch('app.models.inventory.Inventory') as MockInventory:
            mock_session = Mock()

            # Mock the complex query chain
            mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = []

            result = Product.get_low_stock_products(mock_session, 10)

            assert isinstance(result, list)
            mock_session.query.assert_called()

    @pytest.mark.tdd
    def test_get_inactive_products(self, db_session):
        """Test get_inactive_products class method"""
        with patch('app.models.inventory.Inventory') as MockInventory:
            mock_session = Mock()

            # Mock the complex query chains
            mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = []
            mock_session.query.return_value.outerjoin.return_value.filter.return_value.all.return_value = []

            result = Product.get_inactive_products(mock_session, 30)

            assert isinstance(result, list)


class TestProductEdgeCases:
    """TDD: Test edge cases and error conditions"""

    @pytest.mark.tdd
    def test_product_with_none_values(self, db_session):
        """Test product creation with None values where allowed"""
        product = Product(
            sku="PROD-001",
            name="Test Product",
            description=None,
            precio_venta=None,
            precio_costo=None,
            peso=None,
            dimensiones=None,
            categoria=None,
            tags=None
        )

        db_session.add(product)
        db_session.commit()

        assert product.description is None
        assert product.precio_venta is None
        assert product.peso is None

    @pytest.mark.tdd
    def test_product_duplicate_sku_constraint(self, db_session):
        """Test unique constraint on SKU"""
        product1 = Product(sku="PROD-001", name="Product 1")
        product2 = Product(sku="PROD-001", name="Product 2")  # Same SKU

        db_session.add(product1)
        db_session.commit()

        db_session.add(product2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    @pytest.mark.tdd
    def test_product_status_enum_validation(self, db_session):
        """Test ProductStatus enum validation"""
        # Valid statuses
        product = Product(sku="PROD-001", name="Test Product")

        product.status = ProductStatus.TRANSITO
        assert product.status == ProductStatus.TRANSITO

        product.status = ProductStatus.VERIFICADO
        assert product.status == ProductStatus.VERIFICADO

        product.status = ProductStatus.DISPONIBLE
        assert product.status == ProductStatus.DISPONIBLE

        product.status = ProductStatus.VENDIDO
        assert product.status == ProductStatus.VENDIDO

    @pytest.mark.tdd
    def test_product_init_default_status(self, db_session):
        """Test Product __init__ sets default status"""
        product = Product(sku="PROD-001", name="Test Product")

        assert product.status == ProductStatus.TRANSITO

    @pytest.mark.tdd
    def test_product_init_custom_status(self, db_session):
        """Test Product __init__ with custom status"""
        product = Product(
            sku="PROD-001",
            name="Test Product",
            status=ProductStatus.DISPONIBLE
        )

        assert product.status == ProductStatus.DISPONIBLE

    @pytest.mark.tdd
    def test_days_since_last_movement_no_session(self, db_session):
        """Test days_since_last_movement without attached session"""
        product = Product(sku="PROD-001", name="Test Product")
        product.created_at = datetime.now() - timedelta(days=5)

        days = product.days_since_last_movement()

        # Should return days since creation when no inventory data
        assert days >= 4  # Allow for some variance

    @pytest.mark.tdd
    def test_buscar_ubicacion_disponible_found(self, db_session):
        """Test buscar_ubicacion_disponible finds suitable location"""
        product = Product(sku="PROD-004", name="Test Product")
        db_session.add(product)
        db_session.flush()

        # Create real inventory locations
        inv1 = Inventory(
            product_id=product.id,
            zona="A",
            estante="01",
            posicion="001",
            cantidad=10,
            cantidad_reservada=5  # 5 available - not enough
        )
        inv2 = Inventory(
            product_id=product.id,
            zona="A",
            estante="01",
            posicion="002",
            cantidad=20,
            cantidad_reservada=5  # 15 available - enough
        )

        db_session.add_all([inv1, inv2])
        db_session.flush()

        # Refresh product to load relationship
        db_session.refresh(product)

        ubicacion = product.buscar_ubicacion_disponible(10)

        assert ubicacion == inv2

    @pytest.mark.tdd
    def test_buscar_ubicacion_disponible_not_found(self, db_session):
        """Test buscar_ubicacion_disponible when no suitable location"""
        product = Product(sku="PROD-005", name="Test Product")
        db_session.add(product)
        db_session.flush()

        # Create real inventory location with insufficient stock
        inv = Inventory(
            product_id=product.id,
            zona="A",
            estante="01",
            posicion="001",
            cantidad=8,
            cantidad_reservada=3  # 5 available - not enough for 10
        )

        db_session.add(inv)
        db_session.flush()

        # Refresh product to load relationship
        db_session.refresh(product)

        ubicacion = product.buscar_ubicacion_disponible(10)

        assert ubicacion is None