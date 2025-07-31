# ~/tests/models/test_transaction_commission.py
# ---------------------------------------------------------------------------------------------
# MeStore - Tests para campos de comisiones en Transaction
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_transaction_commission.py
# Ruta: ~/tests/models/test_transaction_commission.py
# Autor: Jairo
# Fecha de Creación: 2025-07-29
# Última Actualización: 2025-07-29
# Versión: 1.0.0
# Propósito: Tests unitarios para campos de comisiones (porcentaje_mestocker, monto_vendedor)
#            y métodos de cálculo de comisiones en modelo Transaction
#
# Modificaciones:
# 2025-07-29 - Creación inicial con tests de campos y métodos de comisión
#
# ---------------------------------------------------------------------------------------------

"""
Tests unitarios para campos de comisiones en modelo Transaction.

Cubre:
- Campos porcentaje_mestocker y monto_vendedor
- Validaciones de constraints (0-100% para porcentaje, >= 0 para monto)
- Métodos calcular_monto_vendedor() y aplicar_comision_automatica()
- Serialización en to_dict() con nuevos campos
"""

import pytest
from decimal import Decimal
from app.models.transaction import Transaction, TransactionType, MetodoPago, EstadoTransaccion
from app.models.user import User
from app.models.product import Product


class TestTransactionCommissionFields:
    """Tests para campos de comisiones en Transaction."""

    def test_campos_comision_existen(self):
        """Verificar que los campos de comisión existen en el modelo."""
        transaction = Transaction()

        # Verificar que los campos existen
        assert hasattr(transaction, 'porcentaje_mestocker')
        assert hasattr(transaction, 'monto_vendedor')

        # Verificar que son None por defecto (nullable=True)
        assert transaction.porcentaje_mestocker is None
        assert transaction.monto_vendedor is None

    def test_campos_comision_tipos_correctos(self):
        """Verificar tipos de datos de los campos de comisión."""
        transaction = Transaction()

        # Asignar valores y verificar tipos
        transaction.porcentaje_mestocker = Decimal('5.50')
        transaction.monto_vendedor = Decimal('950.00')

        assert isinstance(transaction.porcentaje_mestocker, Decimal)
        assert isinstance(transaction.monto_vendedor, Decimal)

    def test_porcentaje_mestocker_rangos_validos(self):
        """Verificar que porcentaje_mestocker acepta rangos válidos."""
        transaction = Transaction()

        # Rangos válidos
        transaction.porcentaje_mestocker = Decimal('0.00')    # Mínimo
        assert transaction.porcentaje_mestocker == Decimal('0.00')

        transaction.porcentaje_mestocker = Decimal('5.50')    # Típico
        assert transaction.porcentaje_mestocker == Decimal('5.50')

        transaction.porcentaje_mestocker = Decimal('100.00')  # Máximo
        assert transaction.porcentaje_mestocker == Decimal('100.00')

    def test_monto_vendedor_valores_validos(self):
        """Verificar que monto_vendedor acepta valores válidos."""
        transaction = Transaction()

        # Valores válidos
        transaction.monto_vendedor = Decimal('0.00')         # Mínimo
        assert transaction.monto_vendedor == Decimal('0.00')

        transaction.monto_vendedor = Decimal('1500.75')      # Típico
        assert transaction.monto_vendedor == Decimal('1500.75')

        transaction.monto_vendedor = Decimal('999999999.99') # Máximo
        assert transaction.monto_vendedor == Decimal('999999999.99')


class TestTransactionCommissionMethods:
    """Tests para métodos de cálculo de comisiones."""

    def test_calcular_monto_vendedor_basico(self):
        """Test básico de cálculo de monto vendedor."""
        transaction = Transaction()
        transaction.monto = Decimal('1000.00')
        transaction.porcentaje_mestocker = Decimal('5.00')

        resultado = transaction.calcular_monto_vendedor()

        # 1000 - (1000 * 5 / 100) = 1000 - 50 = 950
        assert resultado == Decimal('950.00')

    def test_calcular_monto_vendedor_sin_monto(self):
        """Test cuando no hay monto definido."""
        transaction = Transaction()
        transaction.porcentaje_mestocker = Decimal('5.00')
        # transaction.monto es None

        resultado = transaction.calcular_monto_vendedor()
        assert resultado is None

    def test_calcular_monto_vendedor_sin_porcentaje(self):
        """Test cuando no hay porcentaje definido."""
        transaction = Transaction()
        transaction.monto = Decimal('1000.00')
        # transaction.porcentaje_mestocker es None

        resultado = transaction.calcular_monto_vendedor()
        assert resultado is None

    def test_calcular_monto_vendedor_precision(self):
        """Test de precisión en cálculos con decimales."""
        transaction = Transaction()
        transaction.monto = Decimal('1234.56')
        transaction.porcentaje_mestocker = Decimal('7.25')

        resultado = transaction.calcular_monto_vendedor()

        # 1234.56 - (1234.56 * 7.25 / 100) = 1234.56 - 89.5056 = 1145.0544
        expected = Decimal('1145.0544')
        assert resultado == expected

    def test_aplicar_comision_automatica(self):
        """Test de aplicación automática de comisión."""
        transaction = Transaction()
        transaction.monto = Decimal('2000.00')

        transaction.aplicar_comision_automatica(Decimal('10.00'))

        # Verificar que se asignó el porcentaje
        assert transaction.porcentaje_mestocker == Decimal('10.00')

        # Verificar que se calculó el monto vendedor
        # 2000 - (2000 * 10 / 100) = 2000 - 200 = 1800
        assert transaction.monto_vendedor == Decimal('1800.00')

    def test_aplicar_comision_automatica_sin_monto(self):
        """Test aplicación automática sin monto."""
        transaction = Transaction()
        # transaction.monto es None

        transaction.aplicar_comision_automatica(Decimal('5.00'))

        # Se asigna el porcentaje pero monto_vendedor es None
        assert transaction.porcentaje_mestocker == Decimal('5.00')
        assert transaction.monto_vendedor is None


class TestTransactionCommissionSerialization:
    """Tests para serialización de campos de comisión."""

    def test_to_dict_incluye_campos_comision(self):
        """Verificar que to_dict() incluye campos de comisión."""
        transaction = Transaction()
        transaction.monto = Decimal('1000.00')
        transaction.porcentaje_mestocker = Decimal('5.00')
        transaction.monto_vendedor = Decimal('950.00')

        result_dict = transaction.to_dict()

        # Verificar que los campos están presentes
        assert 'porcentaje_mestocker' in result_dict
        assert 'monto_vendedor' in result_dict

        # Verificar valores (convertidos a float para JSON)
        assert result_dict['porcentaje_mestocker'] == 5.0
        assert result_dict['monto_vendedor'] == 950.0

    def test_to_dict_campos_comision_none(self):
        """Verificar serialización cuando campos de comisión son None."""
        transaction = Transaction()
        transaction.monto = Decimal('1000.00')
        # porcentaje_mestocker y monto_vendedor son None

        result_dict = transaction.to_dict()

        # Verificar que están presentes pero con valor None
        assert result_dict['porcentaje_mestocker'] is None
        assert result_dict['monto_vendedor'] is None

    def test_to_dict_get_monto_formateado_funciona(self):
        """Verificar que get_monto_formateado() funciona en to_dict()."""
        transaction = Transaction()
        transaction.monto = Decimal('1500.75')

        result_dict = transaction.to_dict()

        # No debería haber TypeError
        assert 'monto_formateado' in result_dict
        assert result_dict['monto_formateado'] == '$1,500.75 COP'


class TestTransactionCommissionIntegration:
    """Tests de integración para funcionalidad completa de comisiones."""

    def test_flujo_completo_comision(self):
        """Test del flujo completo de manejo de comisiones."""
        # Crear transacción
        transaction = Transaction()
        transaction.monto = Decimal('2500.00')
        transaction.metodo_pago = MetodoPago.TARJETA_CREDITO
        transaction.estado = EstadoTransaccion.PENDIENTE
        transaction.transaction_type = TransactionType.VENTA

        # Aplicar comisión automáticamente
        transaction.aplicar_comision_automatica(Decimal('8.50'))

        # Verificar cálculos
        assert transaction.porcentaje_mestocker == Decimal('8.50')
        # 2500 - (2500 * 8.5 / 100) = 2500 - 212.5 = 2287.5
        assert transaction.monto_vendedor == Decimal('2287.50')

        # Verificar serialización
        data = transaction.to_dict()
        assert data['monto'] == 2500.0
        assert data['porcentaje_mestocker'] == 8.5
        assert data['monto_vendedor'] == 2287.5
        assert data['monto_formateado'] == '$2,500.00 COP'

    def test_recalculo_monto_vendedor(self):
        """Test de recálculo cuando cambia el porcentaje."""
        transaction = Transaction()
        transaction.monto = Decimal('1000.00')

        # Primera comisión
        transaction.aplicar_comision_automatica(Decimal('5.00'))
        assert transaction.monto_vendedor == Decimal('950.00')

        # Cambiar comisión y recalcular
        transaction.aplicar_comision_automatica(Decimal('10.00'))
        assert transaction.porcentaje_mestocker == Decimal('10.00')
        assert transaction.monto_vendedor == Decimal('900.00')


# Tests adicionales que podrían necesitarse
class TestTransactionCommissionEdgeCases:
    """Tests para casos límite y edge cases."""

    def test_comision_cero_porcentaje(self):
        """Test con comisión de 0%."""
        transaction = Transaction()
        transaction.monto = Decimal('1000.00')
        transaction.aplicar_comision_automatica(Decimal('0.00'))

        assert transaction.porcentaje_mestocker == Decimal('0.00')
        assert transaction.monto_vendedor == Decimal('1000.00')  # Sin comisión

    def test_comision_maxima_porcentaje(self):
        """Test con comisión máxima de 100%."""
        transaction = Transaction()
        transaction.monto = Decimal('1000.00')
        transaction.aplicar_comision_automatica(Decimal('100.00'))

        assert transaction.porcentaje_mestocker == Decimal('100.00')
        assert transaction.monto_vendedor == Decimal('0.00')  # Todo va a comisión
