"""
Tests para Storage relationships y tracking de ocupación.
"""

import pytest
from uuid import uuid4
from datetime import datetime
from decimal import Decimal

from app.models.storage import Storage, StorageType
from app.models.user import User, UserType


class TestStorageUserRelationships:
    """Tests para relationships bidireccionales Storage ↔ User"""

    def test_create_storage_with_vendedor(self):
        """Test creación de Storage con vendedor_id"""
        vendedor_id = uuid4()
        
        storage = Storage(
            tipo=StorageType.PEQUENO,
            capacidad_max=100,
            vendedor_id=vendedor_id,
            tarifa_mensual=Decimal('50000.00')
        )
        
        assert storage.vendedor_id == vendedor_id
        assert storage.tipo == StorageType.PEQUENO
        assert storage.capacidad_max == 100
        assert storage.productos_actuales == 0  # Default
        assert storage.ocupacion_actual == Decimal('0.00')  # Default

    def test_create_storage_without_vendedor(self):
        """Test creación de Storage sin vendedor (nullable=True)"""
        storage = Storage(
            tipo=StorageType.MEDIANO,
            capacidad_max=500
        )
        
        assert storage.vendedor_id is None
        assert storage.tipo == StorageType.MEDIANO
        assert storage.capacidad_max == 500

    def test_vendedor_relationship_back_populates(self):
        """Test que las relationships usan back_populates correctamente"""
        # Verificar definición en Storage
        storage_rel = Storage.vendedor.property
        assert storage_rel.back_populates == "espacios_storage"
        
        # Verificar definición en User
        user_rel = User.espacios_storage.property
        assert user_rel.back_populates == "vendedor"


class TestStorageTracking:
    """Tests para campos de tracking de ocupación"""

    def test_productos_actuales_default(self):
        """Test que productos_actuales tiene default 0"""
        storage = Storage(
            tipo=StorageType.GRANDE,
            capacidad_max=1000
        )
        
        assert storage.productos_actuales == 0

    def test_ocupacion_actual_default(self):
        """Test que ocupacion_actual tiene default 0.00"""
        storage = Storage(
            tipo=StorageType.ESPECIAL,
            capacidad_max=50
        )
        
        assert storage.ocupacion_actual == Decimal('0.00')

    def test_ultima_actualizacion_nullable(self):
        """Test que ultima_actualizacion puede ser None"""
        storage = Storage(
            tipo=StorageType.PEQUENO,
            capacidad_max=25
        )
        
        assert storage.ultima_actualizacion is None

    def test_actualizar_ocupacion_method(self):
        """Test método actualizar_ocupacion()"""
        storage = Storage(
            tipo=StorageType.MEDIANO,
            capacidad_max=200
        )
        
        # Simular productos actuales
        storage.productos_actuales = 50
        storage.actualizar_ocupacion()
        
        # Verificar cálculo: 50/200 * 100 = 25%
        assert storage.ocupacion_actual == Decimal('25.00')
        assert storage.ultima_actualizacion is not None
        assert isinstance(storage.ultima_actualizacion, datetime)

    def test_agregar_productos_method(self):
        """Test método agregar_productos()"""
        storage = Storage(
            tipo=StorageType.PEQUENO,
            capacidad_max=100
        )
        
        # Agregar productos dentro del límite
        result = storage.agregar_productos(30)
        assert result is True
        assert storage.productos_actuales == 30
        assert storage.ocupacion_actual == Decimal('30.00')
        
        # Intentar agregar más del límite
        result = storage.agregar_productos(80)  # 30 + 80 = 110 > 100
        assert result is False
        assert storage.productos_actuales == 30  # No cambió

    def test_remover_productos_method(self):
        """Test método remover_productos()"""
        storage = Storage(
            tipo=StorageType.GRANDE,
            capacidad_max=500
        )
        
        # Establecer productos iniciales
        storage.productos_actuales = 100
        storage.actualizar_ocupacion()
        
        # Remover productos válidos
        result = storage.remover_productos(25)
        assert result is True
        assert storage.productos_actuales == 75
        assert storage.ocupacion_actual == Decimal('15.00')
        
        # Intentar remover más de los disponibles
        result = storage.remover_productos(100)  # 75 - 100 < 0
        assert result is False
        assert storage.productos_actuales == 75  # No cambió

    def test_get_espacio_disponible_method(self):
        """Test método get_espacio_disponible()"""
        storage = Storage(
            tipo=StorageType.MEDIANO,
            capacidad_max=300
        )
        
        storage.productos_actuales = 120
        disponible = storage.get_espacio_disponible()
        
        assert disponible == 180  # 300 - 120
        
        # Caso límite: storage lleno
        storage.productos_actuales = 300
        disponible = storage.get_espacio_disponible()
        assert disponible == 0


class TestStorageConstraints:
    """Tests para constraints de campos de tracking"""

    def test_productos_actuales_constraint(self):
        """Test CheckConstraint productos_actuales >= 0"""
        storage = Storage(
            tipo=StorageType.PEQUENO,
            capacidad_max=50
        )
        
        # Valor válido
        storage.productos_actuales = 0
        assert storage.productos_actuales == 0
        
        storage.productos_actuales = 25
        assert storage.productos_actuales == 25

    def test_ocupacion_actual_constraint_valid_range(self):
        """Test CheckConstraint ocupacion_actual entre 0 y 100"""
        storage = Storage(
            tipo=StorageType.MEDIANO,
            capacidad_max=200
        )
        
        # Valores válidos
        storage.ocupacion_actual = Decimal('0.00')
        assert storage.ocupacion_actual == Decimal('0.00')
        
        storage.ocupacion_actual = Decimal('50.50')
        assert storage.ocupacion_actual == Decimal('50.50')
        
        storage.ocupacion_actual = Decimal('100.00')
        assert storage.ocupacion_actual == Decimal('100.00')


class TestStorageSerialization:
    """Tests para serialización con nuevos campos"""

    def test_to_dict_includes_tracking_fields(self):
        """Test que to_dict() incluye campos de tracking"""
        vendedor_id = uuid4()
        storage = Storage(
            tipo=StorageType.GRANDE,
            capacidad_max=1000,
            vendedor_id=vendedor_id,
            productos_actuales=250,
            ocupacion_actual=Decimal('25.00'),
            tarifa_mensual=Decimal('150000.00')
        )
        
        # Simular última actualización
        storage.ultima_actualizacion = datetime(2025, 7, 29, 12, 0, 0)
        
        result = storage.to_dict()
        
        # Verificar campos nuevos
        assert result['vendedor_id'] == str(vendedor_id)
        assert result['productos_actuales'] == 250
        assert result['ocupacion_actual'] == 25.00
        assert result['ultima_actualizacion'] == '2025-07-29T12:00:00'
        
        # Verificar campos existentes preservados
        assert result['tipo'] == 'GRANDE'
        assert result['capacidad_max'] == 1000
        assert result['tarifa_mensual'] == 150000.00

    def test_to_dict_with_none_values(self):
        """Test serialización con valores None"""
        storage = Storage(
            tipo=StorageType.ESPECIAL,
            capacidad_max=75
        )
        
        result = storage.to_dict()
        
        assert result['vendedor_id'] is None
        assert result['productos_actuales'] == 0  # Default
        assert result['ocupacion_actual'] == 0.00  # Default
        assert result['ultima_actualizacion'] is None
        assert result['tarifa_mensual'] is None
        assert result['tarifa_por_producto'] is None


class TestStorageTrackingIntegration:
    """Tests de integración para tracking automático"""

    def test_full_tracking_workflow(self):
        """Test workflow completo de tracking"""
        storage = Storage(
            tipo=StorageType.MEDIANO,
            capacidad_max=400,
            vendedor_id=uuid4()
        )
        
        # Estado inicial
        assert storage.productos_actuales == 0
        assert storage.ocupacion_actual == Decimal('0.00')
        assert storage.get_espacio_disponible() == 400
        
        # Agregar productos
        storage.agregar_productos(100)
        assert storage.productos_actuales == 100
        assert storage.ocupacion_actual == Decimal('25.00')
        assert storage.get_espacio_disponible() == 300
        assert storage.ultima_actualizacion is not None
        
        # Agregar más productos
        storage.agregar_productos(150)
        assert storage.productos_actuales == 250
        assert storage.ocupacion_actual == Decimal('62.50')
        assert storage.get_espacio_disponible() == 150
        
        # Remover algunos productos
        storage.remover_productos(50)
        assert storage.productos_actuales == 200
        assert storage.ocupacion_actual == Decimal('50.00')
        assert storage.get_espacio_disponible() == 200

    def test_tracking_preserves_pricing(self):
        """Test que tracking no afecta campos de pricing"""
        storage = Storage(
            tipo=StorageType.PEQUENO,
            capacidad_max=100,
            tarifa_mensual=Decimal('75000.00'),
            tarifa_por_producto=Decimal('500.00')
        )
        
        # Verificar pricing inicial
        assert storage.tarifa_mensual == Decimal('75000.00')
        assert storage.tarifa_por_producto == Decimal('500.00')
        
        # Realizar operaciones de tracking
        storage.agregar_productos(25)
        storage.actualizar_ocupacion()
        storage.remover_productos(10)
        
        # Verificar que pricing no cambió
        assert storage.tarifa_mensual == Decimal('75000.00')
        assert storage.tarifa_por_producto == Decimal('500.00')
        
        # Verificar que tracking funcionó
        assert storage.productos_actuales == 15
        assert storage.ocupacion_actual == Decimal('15.00')
