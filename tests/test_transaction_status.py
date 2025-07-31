"""
Tests específicos para campos de estado de transacciones.
Cubre status, fecha_pago, referencia_pago y métodos asociados.
"""

import pytest
from datetime import datetime
from decimal import Decimal

from app.models.transaction import Transaction, EstadoTransaccion, MetodoPago, TransactionType


class TestTransactionStatusFields:
    """Tests para los nuevos campos de estado"""
    
    def test_status_field_exists(self):
        """Verificar que el campo status existe y es accesible"""
        transaction = Transaction()
        assert hasattr(transaction, 'status')
        assert transaction.status is None  # Nullable por defecto
    
    def test_fecha_pago_field_exists(self):
        """Verificar que el campo fecha_pago existe y es accesible"""
        transaction = Transaction()
        assert hasattr(transaction, 'fecha_pago')
        assert transaction.fecha_pago is None  # Nullable por defecto
    
    def test_referencia_pago_field_exists(self):
        """Verificar que el campo referencia_pago existe y es accesible"""
        transaction = Transaction()
        assert hasattr(transaction, 'referencia_pago')
        assert transaction.referencia_pago is None  # Nullable por defecto
    
    def test_fields_are_nullable(self):
        """Verificar que todos los nuevos campos son nullable"""
        transaction = Transaction(
            monto=Decimal('100.00'),
            metodo_pago=MetodoPago.EFECTIVO,
            estado=EstadoTransaccion.PENDIENTE,
            transaction_type=TransactionType.VENTA,
            porcentaje_mestocker=Decimal('5.00'),
            monto_vendedor=Decimal('95.00')
        )
        
        # Todos los campos nuevos deben poder ser None
        assert transaction.status is None
        assert transaction.fecha_pago is None
        assert transaction.referencia_pago is None


class TestTransactionStatusMethods:
    """Tests para los métodos de utilidad de estado"""
    
    def test_marcar_pago_completado_sin_referencia(self):
        """Test marcar_pago_completado() sin referencia"""
        transaction = Transaction()
        
        # Verificar estado inicial
        assert transaction.status is None
        assert transaction.fecha_pago is None
        assert transaction.referencia_pago is None
        
        # Marcar como completado
        transaction.marcar_pago_completado()
        
        # Verificar cambios
        assert transaction.status == "PAGADO"
        assert transaction.fecha_pago is not None
        assert isinstance(transaction.fecha_pago, datetime)
        assert transaction.referencia_pago is None  # No se proporcionó
    
    def test_marcar_pago_completado_con_referencia(self):
        """Test marcar_pago_completado() con referencia"""
        transaction = Transaction()
        referencia_test = "REF789012345"
        
        # Marcar como completado con referencia
        transaction.marcar_pago_completado(referencia_test)
        
        # Verificar todos los campos
        assert transaction.status == "PAGADO"
        assert transaction.fecha_pago is not None
        assert transaction.referencia_pago == referencia_test
    
    def test_tiene_pago_confirmado_true(self):
        """Test tiene_pago_confirmado() retorna True cuando está confirmado"""
        transaction = Transaction()
        
        # Configurar como pago confirmado
        transaction.status = "PAGADO"
        transaction.fecha_pago = datetime.utcnow()
        
        # Verificar confirmación
        assert transaction.tiene_pago_confirmado() is True
    
    def test_tiene_pago_confirmado_false_sin_status(self):
        """Test tiene_pago_confirmado() retorna False sin status"""
        transaction = Transaction()
        transaction.fecha_pago = datetime.utcnow()
        # status sigue siendo None
        
        assert transaction.tiene_pago_confirmado() is False
    
    def test_tiene_pago_confirmado_false_sin_fecha(self):
        """Test tiene_pago_confirmado() retorna False sin fecha"""
        transaction = Transaction()
        transaction.status = "PAGADO"
        # fecha_pago sigue siendo None
        
        assert transaction.tiene_pago_confirmado() is False


class TestTransactionStatusSerialization:
    """Tests para serialización con nuevos campos"""
    
    def test_to_dict_includes_new_fields(self):
        """Verificar que to_dict() incluye los nuevos campos"""
        transaction = Transaction()
        transaction.status = "PAGADO"
        transaction.fecha_pago = datetime(2025, 7, 29, 12, 0, 0)
        transaction.referencia_pago = "REF555"
        
        dict_data = transaction.to_dict()
        
        # Verificar que los nuevos campos están incluidos
        assert 'status' in dict_data
        assert 'fecha_pago' in dict_data
        assert 'referencia_pago' in dict_data
        
        # Verificar valores
        assert dict_data['status'] == "PAGADO"
        assert dict_data['referencia_pago'] == "REF555"
    
    def test_fecha_pago_iso_format_in_dict(self):
        """Verificar que fecha_pago se serializa en formato ISO"""
        transaction = Transaction()
        test_date = datetime(2025, 7, 29, 15, 30, 45)
        transaction.fecha_pago = test_date
        
        dict_data = transaction.to_dict()
        
        # Verificar formato ISO
        assert dict_data['fecha_pago'] == "2025-07-29T15:30:45"


class TestTransactionStatusIntegrity:
    """Tests de integridad y preservación de funcionalidad"""
    
    def test_campos_originales_preservados(self):
        """Verificar que los campos originales siguen funcionando"""
        transaction = Transaction()
        
        # Verificar que campos originales existen
        assert hasattr(transaction, 'estado')
        assert hasattr(transaction, 'referencia_externa')
        assert hasattr(transaction, 'monto')
        assert hasattr(transaction, 'metodo_pago')
        
        # Verificar que los métodos originales siguen funcionando
        assert hasattr(transaction, 'esta_pendiente')
        assert hasattr(transaction, 'esta_completada')
        assert hasattr(transaction, 'marcar_como_completada')
    
    def test_no_conflicts_between_old_and_new_fields(self):
        """Verificar que no hay conflictos entre campos viejos y nuevos"""
        transaction = Transaction()
        
        # Configurar campos originales
        transaction.estado = EstadoTransaccion.COMPLETADA
        transaction.referencia_externa = "EXT123"
        
        # Configurar campos nuevos
        transaction.status = "PAGADO"
        transaction.referencia_pago = "PAY456"
        
        # Ambos conjuntos deben coexistir sin problemas
        assert transaction.estado == EstadoTransaccion.COMPLETADA
        assert transaction.referencia_externa == "EXT123"
        assert transaction.status == "PAGADO"
        assert transaction.referencia_pago == "PAY456"
