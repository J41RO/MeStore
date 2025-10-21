# ~/tests/models/test_transaction.py
# ---------------------------------------------------------------------------------------------
# MeStore - Tests para Transaction Model
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_transaction.py
# Ruta: ~/tests/models/test_transaction.py
# Autor: Jairo
# Fecha de Creación: 2025-01-28
# Última Actualización: 2025-01-28
# Versión: 1.0.0
# Propósito: Tests unitarios completos para el modelo Transaction
#            Valida creación, enums, métodos utilidad y relationships
#
# Modificaciones:
# 2025-01-28 - Implementación inicial de tests Transaction model
#
# ---------------------------------------------------------------------------------------------

"""
Tests unitarios completos para el modelo Transaction.

Cubre:
- Creación de transacciones con diferentes configuraciones
- Validación de enums MetodoPago y EstadoTransaccion
- Tests de métodos de utilidad (estado, formateo, cancelación)
- Serialización y to_dict()
- Validación de constraints básicos
"""

import pytest
import uuid
from decimal import Decimal

from app.models.transaction import Transaction, MetodoPago, EstadoTransaccion


class TestTransactionCreation:
    """Tests para creación básica de Transaction"""

    def test_create_transaction_basic(self):
        """Test creación básica con campos mínimos"""
        transaction = Transaction(
            monto=Decimal('150000.50'),
            metodo_pago=MetodoPago.TARJETA_CREDITO,
            comprador_id=uuid.uuid4()
        )

        assert transaction.monto == Decimal('150000.50')
        assert transaction.metodo_pago == MetodoPago.TARJETA_CREDITO
        assert transaction.comprador_id is not None
        assert isinstance(transaction.comprador_id, uuid.UUID)

    def test_create_transaction_complete(self):
        """Test creación completa con todos los campos"""
        comprador_id = uuid.uuid4()
        vendedor_id = uuid.uuid4()
        product_id = uuid.uuid4()

        transaction = Transaction(
            monto=Decimal('250000.75'),
            metodo_pago=MetodoPago.PSE,
            estado=EstadoTransaccion.PROCESANDO,
            comprador_id=comprador_id,
            vendedor_id=vendedor_id,
            product_id=product_id,
            referencia_externa='PSE-123456789',
            observaciones='Pago procesado vía PSE'
        )

        assert transaction.monto == Decimal('250000.75')
        assert transaction.metodo_pago == MetodoPago.PSE
        assert transaction.estado == EstadoTransaccion.PROCESANDO
        assert transaction.comprador_id == comprador_id
        assert transaction.vendedor_id == vendedor_id
        assert transaction.product_id == product_id
        assert transaction.referencia_externa == 'PSE-123456789'
        assert transaction.observaciones == 'Pago procesado vía PSE'


class TestTransactionEnums:
    """Tests para enums MetodoPago y EstadoTransaccion"""

    def test_metodo_pago_values(self):
        """Test valores disponibles en MetodoPago"""
        expected_values = {
            'EFECTIVO', 'TARJETA_CREDITO', 'TARJETA_DEBITO', 
            'PSE', 'NEQUI', 'DAVIPLATA'
        }
        actual_values = {mp.value for mp in MetodoPago}
        assert actual_values == expected_values

    def test_estado_transaccion_values(self):
        """Test valores disponibles en EstadoTransaccion"""
        expected_values = {
            'PENDIENTE', 'PROCESANDO', 'COMPLETADA', 
            'FALLIDA', 'CANCELADA'
        }
        actual_values = {et.value for et in EstadoTransaccion}
        assert actual_values == expected_values


class TestTransactionUtilityMethods:
    """Tests para métodos de utilidad de Transaction"""

    def test_esta_pendiente(self):
        """Test método esta_pendiente()"""
        transaction = Transaction(
            monto=Decimal('100000.00'),
            metodo_pago=MetodoPago.EFECTIVO,
            estado=EstadoTransaccion.PENDIENTE,
            comprador_id=uuid.uuid4()
        )
        assert transaction.esta_pendiente() is True

        transaction.estado = EstadoTransaccion.COMPLETADA
        assert transaction.esta_pendiente() is False

    def test_esta_completada(self):
        """Test método esta_completada()"""
        transaction = Transaction(
            monto=Decimal('100000.00'),
            metodo_pago=MetodoPago.EFECTIVO,
            estado=EstadoTransaccion.COMPLETADA,
            comprador_id=uuid.uuid4()
        )
        assert transaction.esta_completada() is True

        transaction.estado = EstadoTransaccion.PENDIENTE
        assert transaction.esta_completada() is False

    def test_puede_cancelar(self):
        """Test método puede_cancelar()"""
        transaction = Transaction(
            monto=Decimal('100000.00'),
            metodo_pago=MetodoPago.EFECTIVO,
            comprador_id=uuid.uuid4()
        )

        # PENDIENTE puede cancelar
        transaction.estado = EstadoTransaccion.PENDIENTE
        assert transaction.puede_cancelar() is True

        # PROCESANDO puede cancelar
        transaction.estado = EstadoTransaccion.PROCESANDO
        assert transaction.puede_cancelar() is True

        # COMPLETADA no puede cancelar
        transaction.estado = EstadoTransaccion.COMPLETADA
        assert transaction.puede_cancelar() is False

    def test_marcar_como_completada(self):
        """Test método marcar_como_completada()"""
        transaction = Transaction(
            monto=Decimal('100000.00'),
            metodo_pago=MetodoPago.EFECTIVO,
            estado=EstadoTransaccion.PROCESANDO,
            comprador_id=uuid.uuid4()
        )

        # Desde PROCESANDO debe funcionar
        result = transaction.marcar_como_completada()
        assert result is True
        assert transaction.estado == EstadoTransaccion.COMPLETADA

    def test_get_monto_formateado(self):
        """Test método get_monto_formateado()"""
        transaction = Transaction(
            monto=Decimal('1500000.50'),
            metodo_pago=MetodoPago.EFECTIVO,
            comprador_id=uuid.uuid4()
        )

        formatted = transaction.get_monto_formateado()
        assert formatted == '$1,500,000.50 COP'

    def test_es_pago_digital(self):
        """Test método es_pago_digital()"""
        # Métodos digitales
        digital_methods = [
            MetodoPago.TARJETA_CREDITO,
            MetodoPago.TARJETA_DEBITO,
            MetodoPago.PSE,
            MetodoPago.NEQUI,
            MetodoPago.DAVIPLATA
        ]

        for metodo in digital_methods:
            transaction = Transaction(
                monto=Decimal('100000.00'),
                metodo_pago=metodo,
                comprador_id=uuid.uuid4()
            )
            assert transaction.es_pago_digital() is True

        # Método no digital
        transaction = Transaction(
            monto=Decimal('100000.00'),
            metodo_pago=MetodoPago.EFECTIVO,
            comprador_id=uuid.uuid4()
        )
        assert transaction.es_pago_digital() is False


class TestTransactionSerialization:
    """Tests para serialización y to_dict()"""

    def test_to_dict_basic(self):
        """Test serialización básica to_dict()"""
        transaction = Transaction(
            monto=Decimal('250000.75'),
            metodo_pago=MetodoPago.PSE,
            estado=EstadoTransaccion.COMPLETADA,
            comprador_id=uuid.uuid4()
        )

        data = transaction.to_dict()

        # Verificar campos básicos
        assert data['monto'] == 250000.75
        assert data['monto_formateado'] == '$250,000.75 COP'
        assert data['metodo_pago'] == 'PSE'
        assert data['estado'] == 'COMPLETADA'
        assert data['esta_completada'] is True
        assert data['puede_cancelar'] is False
        assert data['es_pago_digital'] is True

        # Verificar que tiene campos esperados
        expected_fields = {
            'monto', 'monto_formateado', 'metodo_pago', 'estado',
            'esta_completada', 'puede_cancelar', 'es_pago_digital'
        }

        for field in expected_fields:
            assert field in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
