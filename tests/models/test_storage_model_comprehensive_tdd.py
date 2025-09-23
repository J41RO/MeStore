# ~/tests/models/test_storage_model_comprehensive_tdd.py
# ---------------------------------------------------------------------------------------------
# MeStore - Comprehensive TDD Tests for Storage Model
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# TDD SPECIALIST COMPREHENSIVE COVERAGE MISSION
# Model: app/models/storage.py
# Target Coverage: 85%+
# Methodology: RED-GREEN-REFACTOR
#
# COVERAGE ANALYSIS:
# - Basic CRUD operations and validation
# - Storage type enum validation
# - Capacity and occupancy management
# - Pricing calculation methods
# - Contract management (dates, renewal)
# - Tracking and optimization methods
# - Business logic for space management
# - Edge cases and error handling
# ---------------------------------------------------------------------------------------------

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.storage import Storage, StorageType
from app.models.base import BaseModel


class TestStorageModelBasics:
    """TDD: Test basic Storage model functionality and validation"""

    @pytest.mark.tdd
    def test_storage_creation_minimal_fields(self, db_session):
        """Test creating storage with minimal required fields"""
        storage = Storage(
            tipo=StorageType.PEQUENO,
            capacidad_max=100
        )
        db_session.add(storage)
        db_session.commit()

        assert storage.id is not None
        assert storage.tipo == StorageType.PEQUENO
        assert storage.capacidad_max == 100
        assert storage.productos_actuales == 0
        assert storage.ocupacion_actual == Decimal('0.00')

    @pytest.mark.tdd
    def test_storage_creation_all_fields(self, db_session):
        """Test creating storage with all fields"""
        storage = Storage(
            tipo=StorageType.GRANDE,
            capacidad_max=500,
            vendedor_id="vendor-123",
            productos_actuales=100,
            ocupacion_actual=Decimal('20.00'),
            tarifa_mensual=Decimal('500000.00'),
            tarifa_por_producto=Decimal('1500.00'),
            fecha_inicio=datetime(2025, 1, 1),
            fecha_fin=datetime(2025, 12, 31),
            renovacion_automatica=True
        )
        db_session.add(storage)
        db_session.commit()

        assert storage.tipo == StorageType.GRANDE
        assert storage.capacidad_max == 500
        assert storage.vendedor_id == "vendor-123"
        assert storage.productos_actuales == 100
        assert storage.ocupacion_actual == Decimal('20.00')
        assert storage.tarifa_mensual == Decimal('500000.00')
        assert storage.renovacion_automatica is True

    @pytest.mark.tdd
    def test_storage_init_sets_defaults(self, db_session):
        """Test Storage __init__ sets proper defaults"""
        storage = Storage(tipo=StorageType.MEDIANO, capacidad_max=250)

        assert storage.productos_actuales == 0
        assert storage.ocupacion_actual == Decimal('0.00')

    @pytest.mark.tdd
    def test_storage_init_custom_defaults(self, db_session):
        """Test Storage __init__ with custom defaults"""
        storage = Storage(
            tipo=StorageType.MEDIANO,
            capacidad_max=250,
            productos_actuales=50,
            ocupacion_actual=Decimal('20.00')
        )

        assert storage.productos_actuales == 50
        assert storage.ocupacion_actual == Decimal('20.00')


class TestStorageValidation:
    """TDD: Test storage validation methods"""

    @pytest.mark.tdd
    def test_validate_capacidad_max_positive(self, db_session):
        """Test capacidad_max validation with positive value"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        # Should not raise exception
        validated = storage.validate_capacidad_max("capacidad_max", 100)
        assert validated == 100

    @pytest.mark.tdd
    def test_validate_capacidad_max_zero(self, db_session):
        """Test capacidad_max validation with zero value"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=1)

        with pytest.raises(ValueError, match="La capacidad máxima debe ser mayor a 0"):
            storage.validate_capacidad_max("capacidad_max", 0)

    @pytest.mark.tdd
    def test_validate_capacidad_max_negative(self, db_session):
        """Test capacidad_max validation with negative value"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=1)

        with pytest.raises(ValueError, match="La capacidad máxima debe ser mayor a 0"):
            storage.validate_capacidad_max("capacidad_max", -10)

    @pytest.mark.tdd
    def test_validate_tipo_enum_value(self, db_session):
        """Test tipo validation with StorageType enum"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        validated = storage.validate_tipo("tipo", StorageType.MEDIANO)
        assert validated == StorageType.MEDIANO

    @pytest.mark.tdd
    def test_validate_tipo_string_value(self, db_session):
        """Test tipo validation with string value"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        validated = storage.validate_tipo("tipo", "GRANDE")
        assert validated == StorageType.GRANDE

    @pytest.mark.tdd
    def test_validate_tipo_invalid_string(self, db_session):
        """Test tipo validation with invalid string"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        with pytest.raises(ValueError, match="Tipo de almacenamiento inválido"):
            storage.validate_tipo("tipo", "INVALID_TYPE")

    @pytest.mark.tdd
    def test_validate_fecha_fin_valid(self, db_session):
        """Test fecha_fin validation with valid date"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.fecha_inicio = datetime(2025, 1, 1)

        validated = storage.validate_fecha_fin("fecha_fin", datetime(2025, 12, 31))
        assert validated == datetime(2025, 12, 31)

    @pytest.mark.tdd
    def test_validate_fecha_fin_invalid(self, db_session):
        """Test fecha_fin validation with invalid date"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.fecha_inicio = datetime(2025, 6, 1)

        with pytest.raises(ValueError, match="La fecha de fin debe ser posterior"):
            storage.validate_fecha_fin("fecha_fin", datetime(2025, 3, 1))

    @pytest.mark.tdd
    def test_validate_tarifa_mensual_positive(self, db_session):
        """Test tarifa_mensual validation with positive value"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        validated = storage.validate_tarifa_mensual("tarifa_mensual", Decimal('100000.00'))
        assert validated == Decimal('100000.00')

    @pytest.mark.tdd
    def test_validate_tarifa_mensual_zero(self, db_session):
        """Test tarifa_mensual validation with zero value"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        validated = storage.validate_tarifa_mensual("tarifa_mensual", Decimal('0.00'))
        assert validated == Decimal('0.00')

    @pytest.mark.tdd
    def test_validate_tarifa_mensual_negative(self, db_session):
        """Test tarifa_mensual validation with negative value"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        with pytest.raises(ValueError, match="La tarifa mensual debe ser mayor o igual a 0"):
            storage.validate_tarifa_mensual("tarifa_mensual", Decimal('-100.00'))


class TestStorageOccupancyTracking:
    """TDD: Test storage occupancy tracking functionality"""

    @pytest.mark.tdd
    def test_actualizar_ocupacion(self, db_session):
        """Test actualizar_ocupacion calculation"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.productos_actuales = 25

        with patch('app.models.storage.datetime') as mock_datetime:
            mock_now = datetime(2025, 1, 15, 12, 0, 0)
            mock_datetime.utcnow.return_value = mock_now

            storage.actualizar_ocupacion()

            assert storage.ocupacion_actual == Decimal('25.00')
            assert storage.ultima_actualizacion == mock_now

    @pytest.mark.tdd
    def test_actualizar_ocupacion_over_capacity(self, db_session):
        """Test actualizar_ocupacion with over capacity"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.productos_actuales = 120  # Over capacity

        storage.actualizar_ocupacion()

        assert storage.ocupacion_actual == Decimal('100.00')  # Capped at 100%

    @pytest.mark.tdd
    def test_agregar_productos_success(self, db_session):
        """Test agregar_productos successful addition"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.productos_actuales = 50

        with patch.object(storage, 'actualizar_ocupacion') as mock_update:
            result = storage.agregar_productos(20)

            assert result is True
            assert storage.productos_actuales == 70
            mock_update.assert_called_once()

    @pytest.mark.tdd
    def test_agregar_productos_exceeds_capacity(self, db_session):
        """Test agregar_productos when exceeding capacity"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.productos_actuales = 90

        result = storage.agregar_productos(20)  # Would exceed capacity

        assert result is False
        assert storage.productos_actuales == 90  # Unchanged

    @pytest.mark.tdd
    def test_agregar_productos_zero_or_negative(self, db_session):
        """Test agregar_productos with zero or negative quantity"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        assert storage.agregar_productos(0) is False
        assert storage.agregar_productos(-5) is False

    @pytest.mark.tdd
    def test_remover_productos_success(self, db_session):
        """Test remover_productos successful removal"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.productos_actuales = 50

        with patch.object(storage, 'actualizar_ocupacion') as mock_update:
            result = storage.remover_productos(20)

            assert result is True
            assert storage.productos_actuales == 30
            mock_update.assert_called_once()

    @pytest.mark.tdd
    def test_remover_productos_insufficient_stock(self, db_session):
        """Test remover_productos with insufficient stock"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.productos_actuales = 10

        result = storage.remover_productos(20)  # More than available

        assert result is False
        assert storage.productos_actuales == 10  # Unchanged

    @pytest.mark.tdd
    def test_get_espacio_disponible(self, db_session):
        """Test get_espacio_disponible calculation"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.productos_actuales = 75

        espacio = storage.get_espacio_disponible()
        assert espacio == 25

    @pytest.mark.tdd
    def test_get_espacio_disponible_full(self, db_session):
        """Test get_espacio_disponible when full"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.productos_actuales = 100

        espacio = storage.get_espacio_disponible()
        assert espacio == 0

    @pytest.mark.tdd
    def test_get_espacio_disponible_over_capacity(self, db_session):
        """Test get_espacio_disponible when over capacity"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.productos_actuales = 120

        espacio = storage.get_espacio_disponible()
        assert espacio == 0  # max(0, negative) = 0


class TestStorageBusinessLogic:
    """TDD: Test storage business logic methods"""

    @pytest.mark.tdd
    def test_calcular_ocupacion_porcentaje_normal(self, db_session):
        """Test calcular_ocupacion_porcentaje with normal values"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        porcentaje = storage.calcular_ocupacion_porcentaje(25)
        assert porcentaje == 25.0

    @pytest.mark.tdd
    def test_calcular_ocupacion_porcentaje_over_capacity(self, db_session):
        """Test calcular_ocupacion_porcentaje over capacity"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        porcentaje = storage.calcular_ocupacion_porcentaje(120)
        assert porcentaje == 100.0  # Capped at 100%

    @pytest.mark.tdd
    def test_calcular_ocupacion_porcentaje_negative_productos(self, db_session):
        """Test calcular_ocupacion_porcentaje with negative productos_actuales"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        porcentaje = storage.calcular_ocupacion_porcentaje(-10)
        assert porcentaje == 0.0

    @pytest.mark.tdd
    def test_productos_disponibles(self, db_session):
        """Test productos_disponibles calculation"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        disponibles = storage.productos_disponibles(30)
        assert disponibles == 70

    @pytest.mark.tdd
    def test_esta_lleno_true(self, db_session):
        """Test esta_lleno returns True when at capacity"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        assert storage.esta_lleno(100) is True
        assert storage.esta_lleno(110) is True  # Over capacity

    @pytest.mark.tdd
    def test_esta_lleno_false(self, db_session):
        """Test esta_lleno returns False when below capacity"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        assert storage.esta_lleno(50) is False
        assert storage.esta_lleno(99) is False

    @pytest.mark.tdd
    def test_puede_almacenar_true(self, db_session):
        """Test puede_almacenar returns True when space available"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        assert storage.puede_almacenar(70, 20) is True
        assert storage.puede_almacenar(50, 50) is True  # Exactly at capacity

    @pytest.mark.tdd
    def test_puede_almacenar_false(self, db_session):
        """Test puede_almacenar returns False when exceeding capacity"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        assert storage.puede_almacenar(80, 30) is False
        assert storage.puede_almacenar(100, 1) is False


class TestStoragePricing:
    """TDD: Test storage pricing functionality"""

    @pytest.mark.tdd
    def test_calcular_costo_mensual_tarifa_base_only(self, db_session):
        """Test calcular_costo_mensual with only base monthly fee"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.tarifa_mensual = Decimal('50000.00')
        storage.tarifa_por_producto = None

        costo = storage.calcular_costo_mensual(20)
        assert costo == Decimal('50000.00')

    @pytest.mark.tdd
    def test_calcular_costo_mensual_tarifa_producto_only(self, db_session):
        """Test calcular_costo_mensual with only per-product fee"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.tarifa_mensual = None
        storage.tarifa_por_producto = Decimal('1000.00')

        costo = storage.calcular_costo_mensual(25)
        assert costo == Decimal('25000.00')

    @pytest.mark.tdd
    def test_calcular_costo_mensual_both_tarifas(self, db_session):
        """Test calcular_costo_mensual with both fees"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.tarifa_mensual = Decimal('30000.00')
        storage.tarifa_por_producto = Decimal('500.00')

        costo = storage.calcular_costo_mensual(40)
        assert costo == Decimal('50000.00')  # 30000 + (500 * 40)

    @pytest.mark.tdd
    def test_calcular_costo_mensual_no_tarifas(self, db_session):
        """Test calcular_costo_mensual with no fees"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.tarifa_mensual = None
        storage.tarifa_por_producto = None

        costo = storage.calcular_costo_mensual(20)
        assert costo == Decimal('0.00')

    @pytest.mark.tdd
    def test_es_gratis_true(self, db_session):
        """Test es_gratis returns True when no fees"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.tarifa_mensual = None
        storage.tarifa_por_producto = None

        assert storage.es_gratis() is True

    @pytest.mark.tdd
    def test_es_gratis_true_zero_fees(self, db_session):
        """Test es_gratis returns True with zero fees"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.tarifa_mensual = Decimal('0.00')
        storage.tarifa_por_producto = Decimal('0.00')

        assert storage.es_gratis() is True

    @pytest.mark.tdd
    def test_es_gratis_false(self, db_session):
        """Test es_gratis returns False when fees exist"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.tarifa_mensual = Decimal('10000.00')

        assert storage.es_gratis() is False

    @pytest.mark.tdd
    def test_get_tarifa_mensual_formateada_with_value(self, db_session):
        """Test get_tarifa_mensual_formateada with fee"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.tarifa_mensual = Decimal('150000.50')

        formatted = storage.get_tarifa_mensual_formateada()
        assert formatted == "$150,000.50 COP"

    @pytest.mark.tdd
    def test_get_tarifa_mensual_formateada_none(self, db_session):
        """Test get_tarifa_mensual_formateada with None"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.tarifa_mensual = None

        formatted = storage.get_tarifa_mensual_formateada()
        assert formatted == "Gratis"

    @pytest.mark.tdd
    def test_get_tarifa_producto_formateada_with_value(self, db_session):
        """Test get_tarifa_producto_formateada with fee"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.tarifa_por_producto = Decimal('2500.00')

        formatted = storage.get_tarifa_producto_formateada()
        assert formatted == "$2,500.00 COP por producto"

    @pytest.mark.tdd
    def test_get_tarifa_producto_formateada_none(self, db_session):
        """Test get_tarifa_producto_formateada with None"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.tarifa_por_producto = None

        formatted = storage.get_tarifa_producto_formateada()
        assert formatted == "Gratis"


class TestStorageContractManagement:
    """TDD: Test storage contract management functionality"""

    @pytest.mark.tdd
    def test_esta_vigente_true(self, db_session):
        """Test esta_vigente returns True for active contract"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.fecha_inicio = datetime.now() - timedelta(days=30)
        storage.fecha_fin = datetime.now() + timedelta(days=30)

        assert storage.esta_vigente() is True

    @pytest.mark.tdd
    def test_esta_vigente_false_no_start(self, db_session):
        """Test esta_vigente returns False with no start date"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.fecha_inicio = None

        assert storage.esta_vigente() is False

    @pytest.mark.tdd
    def test_esta_vigente_false_expired(self, db_session):
        """Test esta_vigente returns False for expired contract"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.fecha_inicio = datetime.now() - timedelta(days=60)
        storage.fecha_fin = datetime.now() - timedelta(days=10)

        assert storage.esta_vigente() is False

    @pytest.mark.tdd
    def test_esta_vigente_false_future_start(self, db_session):
        """Test esta_vigente returns False for future start date"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.fecha_inicio = datetime.now() + timedelta(days=10)
        storage.fecha_fin = datetime.now() + timedelta(days=60)

        assert storage.esta_vigente() is False

    @pytest.mark.tdd
    def test_dias_restantes_with_end_date(self, db_session):
        """Test dias_restantes calculation"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.fecha_inicio = datetime.now() - timedelta(days=10)
        storage.fecha_fin = datetime.now() + timedelta(days=20)

        days = storage.dias_restantes()
        assert days is not None
        assert 19 <= days <= 21  # Allow for some variance

    @pytest.mark.tdd
    def test_dias_restantes_no_end_date(self, db_session):
        """Test dias_restantes with no end date"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.fecha_inicio = datetime.now() - timedelta(days=10)
        storage.fecha_fin = None

        days = storage.dias_restantes()
        assert days is None

    @pytest.mark.tdd
    def test_requiere_renovacion_true(self, db_session):
        """Test requiere_renovacion returns True when renewal needed"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.fecha_inicio = datetime.now() - timedelta(days=300)
        storage.fecha_fin = datetime.now() + timedelta(days=20)  # Within 30 days
        storage.renovacion_automatica = False

        with patch.object(storage, 'esta_vigente', return_value=True):
            assert storage.requiere_renovacion(30) is True

    @pytest.mark.tdd
    def test_requiere_renovacion_false_auto_renewal(self, db_session):
        """Test requiere_renovacion returns False with auto renewal"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.renovacion_automatica = True

        with patch.object(storage, 'esta_vigente', return_value=True):
            assert storage.requiere_renovacion() is False

    @pytest.mark.tdd
    def test_renovar_contrato(self, db_session):
        """Test renovar_contrato extends end date"""
        original_end = datetime(2025, 12, 31)
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.fecha_fin = original_end

        with patch('dateutil.relativedelta.relativedelta') as mock_relativedelta, \
             patch('app.models.storage.datetime') as mock_datetime:

            mock_new_end = datetime(2026, 12, 31)
            mock_relativedelta.return_value = timedelta(days=365)
            mock_datetime.utcnow.return_value = datetime(2025, 6, 15)

            # Mock the addition operation
            storage.fecha_fin = mock_new_end
            storage.renovar_contrato(12)

            assert storage.ultima_actualizacion == datetime(2025, 6, 15)


class TestStorageSerialization:
    """TDD: Test storage serialization methods"""

    @pytest.mark.tdd
    def test_to_dict_basic(self, db_session):
        """Test to_dict with basic storage data"""
        storage = Storage(
            tipo=StorageType.MEDIANO,
            capacidad_max=250,
            productos_actuales=50,
            ocupacion_actual=Decimal('20.00'),
            tarifa_mensual=Decimal('100000.00'),
            renovacion_automatica=False
        )

        result = storage.to_dict()

        assert result["tipo"] == "MEDIANO"
        assert result["capacidad_max"] == 250
        assert result["productos_actuales"] == 50
        assert result["ocupacion_actual"] == 20.00
        assert result["tarifa_mensual"] == 100000.00
        assert result["renovacion_automatica"] is False

    @pytest.mark.tdd
    def test_to_dict_with_dates(self, db_session):
        """Test to_dict with date fields"""
        start_date = datetime(2025, 1, 1, 10, 0, 0)
        end_date = datetime(2025, 12, 31, 23, 59, 59)

        storage = Storage(
            tipo=StorageType.GRANDE,
            capacidad_max=500,
            fecha_inicio=start_date,
            fecha_fin=end_date
        )

        result = storage.to_dict()

        assert result["fecha_inicio"] == start_date.isoformat()
        assert result["fecha_fin"] == end_date.isoformat()

    @pytest.mark.tdd
    def test_repr_method(self, db_session):
        """Test __repr__ method"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)
        storage.id = "test-uuid"

        repr_str = repr(storage)

        assert "Storage" in repr_str
        assert "test-uuid" in repr_str
        assert "PEQUENO" in repr_str
        assert "100" in repr_str

    @pytest.mark.tdd
    def test_str_method(self, db_session):
        """Test __str__ method"""
        storage = Storage(tipo=StorageType.GRANDE, capacidad_max=1000)

        str_repr = str(storage)

        assert str_repr == "Storage GRANDE (Capacidad: 1000 productos)"


class TestStorageEdgeCases:
    """TDD: Test edge cases and error conditions"""

    @pytest.mark.tdd
    def test_storage_with_none_values(self, db_session):
        """Test storage creation with None values where allowed"""
        storage = Storage(
            tipo=StorageType.PEQUENO,
            capacidad_max=100,
            vendedor_id=None,
            tarifa_mensual=None,
            tarifa_por_producto=None,
            fecha_inicio=None,
            fecha_fin=None
        )

        db_session.add(storage)
        db_session.commit()

        assert storage.vendedor_id is None
        assert storage.tarifa_mensual is None
        assert storage.fecha_inicio is None

    @pytest.mark.tdd
    def test_storage_constraints_capacidad_positive(self, db_session):
        """Test database constraint for positive capacity"""
        # This would be tested at database level, but we can test validation
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        # Test the validation method directly
        with pytest.raises(ValueError):
            storage.validate_capacidad_max("capacidad_max", 0)

    @pytest.mark.tdd
    def test_storage_enum_values(self, db_session):
        """Test all StorageType enum values"""
        assert StorageType.PEQUENO.value == "PEQUENO"
        assert StorageType.MEDIANO.value == "MEDIANO"
        assert StorageType.GRANDE.value == "GRANDE"
        assert StorageType.ESPECIAL.value == "ESPECIAL"

    @pytest.mark.tdd
    def test_storage_tipo_validation_whitespace(self, db_session):
        """Test tipo validation with whitespace"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        validated = storage.validate_tipo("tipo", "  MEDIANO  ")
        assert validated == StorageType.MEDIANO

    @pytest.mark.tdd
    def test_storage_tipo_validation_lowercase(self, db_session):
        """Test tipo validation with lowercase"""
        storage = Storage(tipo=StorageType.PEQUENO, capacidad_max=100)

        validated = storage.validate_tipo("tipo", "grande")
        assert validated == StorageType.GRANDE