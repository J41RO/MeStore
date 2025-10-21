# ~/tests/test_schemas_product.py
# ---------------------------------------------------------------------------------------------
# MeStore - Tests para Product Pydantic Schemas
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""
Tests para schemas Product con validaciones de negocio.

Prueba todas las validaciones business implementadas:
- SKU format empresarial
- Pricing coherence  
- Fulfillment rules
- Status transitions
- Serialización con tipos complejos
"""

import pytest
from decimal import Decimal
from datetime import datetime
from uuid import uuid4
from pydantic import ValidationError

from app.schemas.product import (
    ProductBase,
    ProductCreate,
    ProductUpdate,
    ProductRead,
    ProductResponse
)
from app.models.product import ProductStatus


class TestProductBase:
    """Tests para ProductBase schema."""

    def test_product_base_valid(self):
        """Test creación válida de ProductBase."""
        data = {
            "sku": "ELEC-LAPTOP-001",
            "name": "Laptop Gaming",
            "status": ProductStatus.DISPONIBLE,
            "precio_venta": Decimal("2500000"),
            "precio_costo": Decimal("2000000"),
            "peso": Decimal("2.5")
        }

        product = ProductBase(**data)
        assert product.sku == "ELEC-LAPTOP-001"
        assert product.name == "Laptop Gaming"
        assert product.precio_venta == Decimal("2500000")

    def test_sku_validation_success(self):
        """Test validación SKU exitosa."""
        valid_skus = [
            "ELEC-LAPTOP-001",
            "CLOTH-SHIRT-ABC",
            "HOME-KITCHEN-123"
        ]

        for sku in valid_skus:
            product = ProductBase(sku=sku, name="Test Product")
            assert product.sku == sku.upper()

    def test_sku_validation_failure(self):
        """Test validación SKU falla con formatos inválidos."""
        invalid_skus = [
            "A",  # Muy corto
            "INVALID@SKU",  # Caracteres especiales
            "NOGUIONES",  # Sin guiones
            "a" * 51  # Muy largo
        ]

        for sku in invalid_skus:
            with pytest.raises(ValidationError):
                ProductBase(sku=sku, name="Test Product")

    def test_precio_validation(self):
        """Test validación precios."""
        # Precio muy bajo
        with pytest.raises(ValidationError):
            ProductBase(
                sku="TEST-001", 
                name="Test", 
                precio_venta=Decimal("50")
            )

        # Precio muy alto
        with pytest.raises(ValidationError):
            ProductBase(
                sku="TEST-001", 
                name="Test", 
                precio_venta=Decimal("200000000")
            )

        # Precio válido
        product = ProductBase(
            sku="TEST-001", 
            name="Test", 
            precio_venta=Decimal("100000")
        )
        assert product.precio_venta == Decimal("100000")

    def test_peso_validation(self):
        """Test validación peso."""
        # Peso muy bajo
        with pytest.raises(ValidationError):
            ProductBase(
                sku="TEST-001", 
                name="Test", 
                peso=Decimal("0.0001")
            )

        # Peso muy alto
        with pytest.raises(ValidationError):
            ProductBase(
                sku="TEST-001", 
                name="Test", 
                peso=Decimal("2000")
            )

        # Peso válido
        product = ProductBase(
            sku="TEST-001", 
            name="Test", 
            peso=Decimal("1.5")
        )
        assert product.peso == Decimal("1.5")

    def test_dimensiones_validation_success(self):
        """Test validación dimensiones exitosa."""
        valid_dimensiones = {
            "largo": 30.0,
            "ancho": 20.0,
            "alto": 5.0
        }

        product = ProductBase(
            sku="TEST-001",
            name="Test",
            dimensiones=valid_dimensiones
        )
        assert product.dimensiones == valid_dimensiones

    def test_dimensiones_validation_failure(self):
        """Test validación dimensiones falla."""
        # Dimensiones faltantes
        with pytest.raises(ValidationError):
            ProductBase(
                sku="TEST-001",
                name="Test",
                dimensiones={"largo": 30.0}  # Faltan ancho y alto
            )

        # Dimensión muy grande
        with pytest.raises(ValidationError):
            ProductBase(
                sku="TEST-001",
                name="Test",
                dimensiones={
                    "largo": 600.0,  # Muy grande
                    "ancho": 20.0,
                    "alto": 5.0
                }
            )

        # Dimensión negativa
        with pytest.raises(ValidationError):
            ProductBase(
                sku="TEST-001",
                name="Test",
                dimensiones={
                    "largo": -10.0,  # Negativa
                    "ancho": 20.0,
                    "alto": 5.0
                }
            )

    def test_tags_validation_success(self):
        """Test validación tags exitosa."""
        valid_tags = ["laptop", "gaming", "rgb"]

        product = ProductBase(
            sku="TEST-001",
            name="Test",
            tags=valid_tags
        )
        assert product.tags == valid_tags

    def test_tags_validation_failure(self):
        """Test validación tags falla."""
        # Demasiados tags
        with pytest.raises(ValidationError):
            ProductBase(
                sku="TEST-001",
                name="Test",
                tags=[f"tag{i}" for i in range(15)]  # Más de 10
            )

        # Tag muy corto
        with pytest.raises(ValidationError):
            ProductBase(
                sku="TEST-001",
                name="Test",
                tags=["a"]  # Muy corto
            )

        # Tag con caracteres inválidos
        with pytest.raises(ValidationError):
            ProductBase(
                sku="TEST-001",
                name="Test",
                tags=["tag@invalid"]  # Carácter especial
            )

    def test_tags_normalization(self):
        """Test normalización de tags (lowercase, sin duplicados)."""
        input_tags = ["LAPTOP", "Gaming", "RGB", "laptop"]  # Duplicado y mayúsculas

        product = ProductBase(
            sku="TEST-001",
            name="Test",
            tags=input_tags
        )

        # Debe normalizar a lowercase y remover duplicados
        expected_tags = ["laptop", "gaming", "rgb"]
        assert product.tags == expected_tags

    def test_pricing_coherence_validation(self):
        """Test validación coherencia entre precios."""
        # Precio venta < precio costo (inválido)
        with pytest.raises(ValidationError):
            ProductBase(
                sku="TEST-001",
                name="Test",
                precio_venta=Decimal("1000"),
                precio_costo=Decimal("2000")
            )

        # Comisión > 30% precio venta (inválido)
        with pytest.raises(ValidationError):
            ProductBase(
                sku="TEST-001",
                name="Test",
                precio_venta=Decimal("1000"),
                comision_mestocker=Decimal("400")  # 40%
            )

        # Coherencia válida
        product = ProductBase(
            sku="TEST-001",
            name="Test",
            precio_venta=Decimal("1000"),
            precio_costo=Decimal("800"),
            comision_mestocker=Decimal("300")  # 30%
        )
        assert product.precio_venta == Decimal("1000")


class TestProductCreate:
    """Tests para ProductCreate schema."""

    def test_product_create_required_fields(self):
        """Test campos obligatorios en ProductCreate."""
        # SKU y name son obligatorios
        with pytest.raises(ValidationError):
            ProductCreate()  # Sin campos obligatorios

        # Solo name (falta SKU)
        with pytest.raises(ValidationError):
            ProductCreate(name="Test Product")

        # Solo SKU (falta name)
        with pytest.raises(ValidationError):
            ProductCreate(sku="TEST-001")

        # Ambos campos obligatorios
        product = ProductCreate(sku="TEST-001", name="Test Product")
        assert product.sku == "TEST-001"
        assert product.name == "Test Product"

    def test_product_create_with_all_fields(self):
        """Test ProductCreate con todos los campos."""
        data = {
            "sku": "ELEC-LAPTOP-002",
            "name": "Laptop Gaming Pro",
            "description": "Laptop gaming profesional",
            "status": ProductStatus.DISPONIBLE,
            "precio_venta": Decimal("3500000"),
            "precio_costo": Decimal("2800000"),
            "comision_mestocker": Decimal("350000"),
            "peso": Decimal("2.8"),
            "dimensiones": {"largo": 38.0, "ancho": 26.0, "alto": 3.5},
            "categoria": "Electronics",
            "tags": ["laptop", "gaming", "professional"]
        }

        product = ProductCreate(**data)
        assert product.sku == "ELEC-LAPTOP-002"
        assert product.precio_venta == Decimal("3500000")
        assert len(product.tags) == 3


class TestProductUpdate:
    """Tests para ProductUpdate schema."""

    def test_product_update_all_optional(self):
        """Test que todos los campos son opcionales en ProductUpdate."""
        # Puede crear ProductUpdate vacío
        update = ProductUpdate()
        assert update.sku is None
        assert update.name is None

        # Puede actualizar solo algunos campos
        update = ProductUpdate(name="Updated Name", precio_venta=Decimal("2000000"))
        assert update.name == "Updated Name"
        assert update.precio_venta == Decimal("2000000")
        assert update.sku is None  # Otros campos siguen None

    def test_product_update_validations(self):
        """Test que las validaciones funcionan en updates."""
        # SKU inválido
        with pytest.raises(ValidationError):
            ProductUpdate(sku="INVALID@SKU")

        # Precio inválido
        with pytest.raises(ValidationError):
            ProductUpdate(precio_venta=Decimal("50"))

        # Update válido
        update = ProductUpdate(
            sku="UPDATED-001",
            precio_venta=Decimal("150000")
        )
        assert update.sku == "UPDATED-001"


class TestProductRead:
    """Tests para ProductRead schema."""

    def test_product_read_complete(self):
        """Test ProductRead con todos los campos."""
        data = {
            # Campos de ProductBase
            "sku": "ELEC-LAPTOP-001",
            "name": "Laptop Gaming",
            "status": ProductStatus.DISPONIBLE,
            "precio_venta": Decimal("2500000"),

            # Campos adicionales de ProductRead
            "id": uuid4(),
            "vendedor_id": uuid4(),
            "version": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        product = ProductRead(**data)
        assert product.sku == "ELEC-LAPTOP-001"
        assert product.id is not None
        assert product.version == 1

    def test_product_read_json_serialization(self):
        """Test serialización JSON de ProductRead."""
        data = {
            "sku": "TEST-001",
            "name": "Test Product",
            "status": ProductStatus.DISPONIBLE,
            "precio_venta": Decimal("100000"),
            "id": uuid4(),
            "version": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        product = ProductRead(**data)

        # Debe poder serializar a JSON
        json_data = product.model_dump_json()
        assert isinstance(json_data, str)

        # Debe poder convertir a dict
        dict_data = product.model_dump()
        assert isinstance(dict_data, dict)
        assert "sku" in dict_data


class TestProductResponse:
    """Tests para ProductResponse schema."""

    def test_product_response_alias(self):
        """Test que ProductResponse es alias de ProductRead."""
        data = {
            "sku": "TEST-001",
            "name": "Test Product",
            "status": ProductStatus.DISPONIBLE,
            "id": uuid4(),
            "version": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        # Ambos deben comportarse igual
        product_read = ProductRead(**data)
        product_response = ProductResponse(**data)

        assert product_read.sku == product_response.sku
        assert product_read.id == product_response.id


class TestComplexValidations:
    """Tests para validaciones complejas y casos edge."""

    def test_decimal_precision(self):
        """Test manejo preciso de Decimal para precios."""
        product = ProductBase(
            sku="TEST-001",
            name="Test",
            precio_venta=Decimal("2500000.99"),
            precio_costo=Decimal("2000000.50")
        )

        assert product.precio_venta == Decimal("2500000.99")
        assert product.precio_costo == Decimal("2000000.50")

    def test_status_enum_validation(self):
        """Test validación del enum ProductStatus."""
        valid_statuses = [
            ProductStatus.TRANSITO,
            ProductStatus.VERIFICADO,
            ProductStatus.DISPONIBLE,
            ProductStatus.VENDIDO
        ]

        for status in valid_statuses:
            product = ProductBase(
                sku="TEST-001",
                name="Test",
                status=status
            )
            assert product.status == status

    def test_edge_cases_pricing(self):
        """Test casos edge para pricing."""
        # Precio exactamente en el límite mínimo
        product = ProductBase(
            sku="TEST-001",
            name="Test",
            precio_venta=Decimal("100")
        )
        assert product.precio_venta == Decimal("100")

        # Comisión exactamente 30%
        product = ProductBase(
            sku="TEST-001",
            name="Test",
            precio_venta=Decimal("1000"),
            comision_mestocker=Decimal("300")
        )
        assert product.comision_mestocker == Decimal("300")
