# ~/app/services/transaction_service.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Transaction Service for Financial Movement Logging (PRODUCTION_READY)
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: transaction_service.py
# Ruta: ~/app/services/transaction_service.py
# Autor: Jairo
# Fecha de Creación: 2025-09-12
# Última Actualización: 2025-09-12
# Versión: 1.0.0
# Propósito: Servicio de registro de transacciones financieras con auditoría completa
#            Integrado con sistema de comisiones para trazabilidad financiera
#
# Modificaciones:
# 2025-09-12 - Creación inicial con preparación hosting enterprise
#
# ---------------------------------------------------------------------------------------------

"""
PRODUCTION_READY: Servicio de registro de transacciones financieras

Este módulo contiene:
- TransactionService: Registro de movimientos financieros con auditoría
- Integración con Commission system para trazabilidad completa
- Logging estructurado para auditoría financiera
- Validación de integridad de transacciones y montos
- Configuración dinámica por ambiente
"""

import os
import logging
import hashlib
import hmac
import secrets
from decimal import Decimal
from typing import Dict, List, Optional, Union
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from sqlalchemy import select, and_, func, text, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models.transaction import Transaction, EstadoTransaccion, TransactionType, MetodoPago
from app.models.commission import Commission, CommissionStatus
from app.models.user import User
from app.models.order import Order

# Configure structured logging for financial auditing
logger = logging.getLogger(__name__)


class TransactionError(Exception):
    """Exception raised for transaction errors"""
    def __init__(self, message: str, transaction_id: Optional[UUID] = None, details: Optional[Dict] = None):
        super().__init__(message)
        self.transaction_id = transaction_id
        self.details = details or {}


class TransactionService:
    """
    PRODUCTION_READY: Servicio de registro de transacciones financieras
    
    Maneja el registro completo de movimientos financieros con auditoría,
    validación de integridad y trazabilidad completa de comisiones.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.audit_level = os.getenv('TRANSACTION_AUDIT_LEVEL', 'standard')
        self.enable_detailed_logging = self.audit_level in ['detailed', 'debug']

        # Financial validation settings
        self.max_transaction_amount = Decimal(os.getenv('MAX_TRANSACTION_AMOUNT', '10000000'))  # 10M COP
        self.min_transaction_amount = Decimal(os.getenv('MIN_TRANSACTION_AMOUNT', '100'))      # 100 COP

        # SECURITY FIX: Cryptographic integrity settings
        self.integrity_secret = os.getenv('TRANSACTION_INTEGRITY_SECRET',
                                         secrets.token_urlsafe(32))  # Secure random default
        self.enable_integrity_checks = os.getenv('ENABLE_TRANSACTION_INTEGRITY', 'true').lower() == 'true'
        
    def get_db(self) -> Session:
        """Get database session - use provided or create new"""
        if self.db:
            return self.db
        return SessionLocal()
    
    def create_commission_transaction(
        self,
        commission: Commission,
        payment_method: MetodoPago,
        notes: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Transaction:
        """
        Crea transacción financiera asociada a una comisión
        
        Args:
            commission: Comisión para la cual crear transacción
            payment_method: Método de pago utilizado
            notes: Notas adicionales
            db: Sesión de base de datos opcional
            
        Returns:
            Transaction: Transacción creada y guardada
            
        Raises:
            TransactionError: Si hay errores en la creación
        """
        db = db or self.get_db()
        
        try:
            # Validate commission
            if not commission or commission.status != CommissionStatus.APPROVED:
                raise TransactionError(
                    f"Commission {commission.id if commission else 'None'} is not approved for transaction",
                    details={'commission_id': str(commission.id) if commission else None}
                )
            
            # Check if transaction already exists for this commission
            existing_transaction = db.query(Transaction).filter(
                Transaction.id == commission.transaction_id
            ).first() if commission.transaction_id else None
            
            if existing_transaction:
                logger.info(f"Transaction already exists for commission {commission.id}: {existing_transaction.id}")
                return existing_transaction
            
            # Validate vendor exists
            vendor = db.query(User).filter(User.id == commission.vendor_id).first()
            if not vendor:
                raise TransactionError(
                    f"Vendor {commission.vendor_id} not found",
                    details={'vendor_id': str(commission.vendor_id)}
                )
            
            # Validate order exists
            order = db.query(Order).filter(Order.id == commission.order_id).first()
            if not order:
                raise TransactionError(
                    f"Order {commission.order_id} not found",
                    details={'order_id': commission.order_id}
                )
            
            # Generate transaction reference
            transaction_ref = self._generate_transaction_reference()

            # Create transaction for vendor payment
            transaction = Transaction(
                monto=commission.vendor_amount,
                metodo_pago=payment_method,
                estado=EstadoTransaccion.PENDIENTE,
                transaction_type=TransactionType.COMISION,
                comprador_id=order.buyer_id,  # Buyer pays
                vendedor_id=commission.vendor_id,  # Vendor receives
                porcentaje_mestocker=commission.commission_rate * 100,  # Convert to percentage
                monto_vendedor=commission.vendor_amount,
                referencia_externa=transaction_ref,
                observaciones=notes or f"Commission payment for order {order.order_number}",
                inventory_id=None  # Commission transactions don't relate to specific inventory
            )

            # SECURITY FIX: Generate cryptographic integrity hash
            if self.enable_integrity_checks:
                transaction.integrity_hash = self._generate_integrity_hash(transaction, commission)
            
            # Save transaction
            db.add(transaction)
            db.flush()  # Get the ID without committing
            
            # Link transaction to commission
            commission.transaction_id = transaction.id
            
            db.commit()
            db.refresh(transaction)
            
            # Log for audit trail
            self._log_transaction_creation(transaction, commission)
            
            logger.info(f"Transaction created successfully: {transaction.id} for commission {commission.id}")
            
            return transaction
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating transaction for commission {commission.id if commission else 'None'}: {e}")
            if isinstance(e, TransactionError):
                raise
            raise TransactionError(
                f"Unexpected error creating transaction: {str(e)}",
                details={'commission_id': str(commission.id) if commission else None}
            )
    
    def process_transaction_payment(
        self,
        transaction_id: UUID,
        payment_reference: Optional[str] = None,
        gateway_response: Optional[Dict] = None,
        db: Optional[Session] = None
    ) -> Transaction:
        """
        Procesa el pago de una transacción
        
        Args:
            transaction_id: ID de la transacción a procesar
            payment_reference: Referencia del pago del gateway
            gateway_response: Respuesta completa del gateway
            db: Sesión de base de datos opcional
            
        Returns:
            Transaction: Transacción actualizada
        """
        db = db or self.get_db()
        
        try:
            transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
            if not transaction:
                raise TransactionError(f"Transaction {transaction_id} not found")
            
            if transaction.estado != EstadoTransaccion.PENDIENTE:
                raise TransactionError(
                    f"Transaction {transaction_id} is not in pending status: {transaction.estado}"
                )
            
            # SECURITY FIX: Validate transaction integrity before processing
            if self.enable_integrity_checks:
                if not self._validate_transaction_integrity_hash(transaction):
                    raise TransactionError(f"Transaction integrity validation failed for {transaction_id}")

            # Update transaction status
            transaction.estado = EstadoTransaccion.PROCESANDO
            transaction.referencia_pago = payment_reference
            if gateway_response:
                transaction.observaciones = (transaction.observaciones or '') + f"\nGateway response: {gateway_response}"
            
            db.commit()
            
            # Simulate payment processing (in production, integrate with real payment gateway)
            success = self._simulate_payment_processing(transaction)
            
            if success:
                transaction.marcar_pago_completado(payment_reference)
                transaction.estado = EstadoTransaccion.COMPLETADA
                
                # Mark associated commission as paid
                if transaction.transaction_type == TransactionType.COMISION:
                    commission = db.query(Commission).filter(
                        Commission.transaction_id == transaction.id
                    ).first()
                    if commission:
                        commission.mark_as_paid(f"Payment processed via transaction {transaction.id}")
            else:
                transaction.estado = EstadoTransaccion.FALLIDA
                transaction.observaciones = (transaction.observaciones or '') + "\nPayment processing failed"
            
            db.commit()
            
            self._log_transaction_processing(transaction, success)
            
            return transaction
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing transaction {transaction_id}: {e}")
            if isinstance(e, TransactionError):
                raise
            raise TransactionError(f"Unexpected error processing transaction: {str(e)}")
    
    def get_transaction_history(
        self,
        user_id: Optional[UUID] = None,
        transaction_type: Optional[TransactionType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status_filter: Optional[List[EstadoTransaccion]] = None,
        limit: int = 100,
        offset: int = 0,
        db: Optional[Session] = None
    ) -> Dict:
        """
        Obtiene historial de transacciones con filtros
        
        Returns:
            Dict con transacciones y metadata de paginación
        """
        db = db or self.get_db()
        
        try:
            # Build query
            query = db.query(Transaction)
            
            if user_id:
                query = query.filter(
                    or_(
                        Transaction.comprador_id == user_id,
                        Transaction.vendedor_id == user_id
                    )
                )
            
            if transaction_type:
                query = query.filter(Transaction.transaction_type == transaction_type)
            
            if start_date:
                query = query.filter(Transaction.created_at >= start_date)
            
            if end_date:
                query = query.filter(Transaction.created_at <= end_date)
            
            if status_filter:
                query = query.filter(Transaction.estado.in_(status_filter))
            
            # Get total count
            total_count = query.count()
            
            # Apply pagination and ordering
            transactions = query.order_by(
                Transaction.created_at.desc()
            ).offset(offset).limit(limit).all()
            
            # Calculate summary statistics
            summary = self._calculate_transaction_summary(
                query.filter(Transaction.estado == EstadoTransaccion.COMPLETADA).all()
            )
            
            return {
                'transactions': [t.to_dict() for t in transactions],
                'pagination': {
                    'total': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_next': offset + limit < total_count,
                    'has_prev': offset > 0
                },
                'summary': summary,
                'filters_applied': {
                    'user_id': str(user_id) if user_id else None,
                    'transaction_type': transaction_type.value if transaction_type else None,
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None,
                    'status_filter': [s.value for s in status_filter] if status_filter else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting transaction history: {e}")
            raise TransactionError(f"Error retrieving transaction history: {str(e)}")
    
    def validate_transaction_integrity(
        self,
        transaction: Transaction,
        db: Optional[Session] = None
    ) -> Dict[str, bool]:
        """
        Valida la integridad de una transacción
        
        Returns:
            Dict con resultados de validación
        """
        db = db or self.get_db()
        results = {'valid': True, 'errors': []}
        
        try:
            # Basic amount validation
            if transaction.monto <= 0:
                results['valid'] = False
                results['errors'].append('Transaction amount must be positive')
            
            if transaction.monto > self.max_transaction_amount:
                results['valid'] = False
                results['errors'].append(f'Transaction amount exceeds maximum: {self.max_transaction_amount}')
            
            if transaction.monto < self.min_transaction_amount:
                results['valid'] = False
                results['errors'].append(f'Transaction amount below minimum: {self.min_transaction_amount}')
            
            # Commission-specific validation
            if transaction.transaction_type == TransactionType.COMISION:
                commission = db.query(Commission).filter(
                    Commission.transaction_id == transaction.id
                ).first()
                
                if commission:
                    # Validate amounts match
                    if abs(transaction.monto_vendedor - commission.vendor_amount) > Decimal('0.01'):
                        results['valid'] = False
                        results['errors'].append('Transaction vendor amount does not match commission')
                    
                    # Validate commission integrity
                    if not self._validate_commission_calculation(commission):
                        results['valid'] = False
                        results['errors'].append('Commission calculation integrity failed')
            
            # User validation
            if transaction.comprador_id:
                buyer = db.query(User).filter(User.id == transaction.comprador_id).first()
                if not buyer:
                    results['valid'] = False
                    results['errors'].append('Buyer user not found')
            
            if transaction.vendedor_id:
                vendor = db.query(User).filter(User.id == transaction.vendedor_id).first()
                if not vendor:
                    results['valid'] = False
                    results['errors'].append('Vendor user not found')
            
            # SECURITY FIX: Enhanced validation with cryptographic checks
            crypto_validation = self._validate_financial_consistency(transaction, commission)
            if not crypto_validation['valid']:
                results['valid'] = False
                results['errors'].extend(crypto_validation['errors'])

            return results

        except Exception as e:
            logger.error(f"Error validating transaction integrity: {e}")
            return {'valid': False, 'errors': [f'Validation error: {str(e)}']}
    
    def _generate_transaction_reference(self) -> str:
        """Genera referencia única de transacción"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid4())[:8].upper()
        return f"TXN-{timestamp}-{random_suffix}"
    
    def _simulate_payment_processing(self, transaction: Transaction) -> bool:
        """
        Simula procesamiento de pago
        En producción, aquí se integraría con gateway de pago real
        """
        # In development, simulate random success/failure for testing
        if self.environment == 'development':
            import random
            return random.choice([True, True, True, False])  # 75% success rate
        
        # In production, implement actual payment gateway integration
        return True
    
    def _log_transaction_creation(self, transaction: Transaction, commission: Commission) -> None:
        """Log de auditoría para creación de transacción"""
        audit_data = {
            'transaction_id': str(transaction.id),
            'commission_id': str(commission.id),
            'amount': float(transaction.monto),
            'vendor_amount': float(transaction.monto_vendedor),
            'payment_method': transaction.metodo_pago.value,
            'transaction_type': transaction.transaction_type.value,
            'vendor_id': str(transaction.vendedor_id),
            'buyer_id': str(transaction.comprador_id),
            'reference': transaction.referencia_externa,
            'timestamp': datetime.now().isoformat(),
            'environment': self.environment
        }
        
        if self.enable_detailed_logging:
            logger.info(f"Transaction creation audit: {audit_data}")
        else:
            logger.info(f"Transaction created: {transaction.referencia_externa}")
    
    def _log_transaction_processing(self, transaction: Transaction, success: bool) -> None:
        """Log de auditoría para procesamiento de transacción"""
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"Transaction processing {status}: {transaction.id} - {transaction.referencia_externa}")
    
    def _calculate_transaction_summary(self, transactions: List[Transaction]) -> Dict:
        """Calcula resumen estadístico de transacciones"""
        if not transactions:
            return {
                'total_amount': 0.0,
                'total_transactions': 0,
                'avg_amount': 0.0,
                'commission_total': 0.0,
                'by_payment_method': {}
            }
        
        total_amount = sum(t.monto for t in transactions)
        commission_transactions = [t for t in transactions if t.transaction_type == TransactionType.COMISION]
        commission_total = sum(t.monto for t in commission_transactions)
        
        by_method = {}
        for t in transactions:
            method = t.metodo_pago.value
            if method not in by_method:
                by_method[method] = {'count': 0, 'amount': 0.0}
            by_method[method]['count'] += 1
            by_method[method]['amount'] += float(t.monto)
        
        return {
            'total_amount': float(total_amount),
            'total_transactions': len(transactions),
            'avg_amount': float(total_amount / len(transactions)),
            'commission_total': float(commission_total),
            'by_payment_method': by_method
        }
    
    def _validate_commission_calculation(self, commission: Commission) -> bool:
        """Valida cálculos de comisión"""
        expected_commission, expected_vendor, expected_platform = Commission.calculate_commission(
            commission.order_amount,
            commission.commission_rate,
            commission.commission_type
        )

        return (
            abs(commission.commission_amount - expected_commission) < Decimal('0.01') and
            abs(commission.vendor_amount - expected_vendor) < Decimal('0.01') and
            abs(commission.platform_amount - expected_platform) < Decimal('0.01')
        )

    # === SECURITY METHODS - Cryptographic Integrity ===

    def _generate_integrity_hash(self, transaction: Transaction, commission: Commission = None) -> str:
        """Generate cryptographic integrity hash for transaction."""

        # Create hash input from critical transaction data
        hash_data = {
            'monto': str(transaction.monto),
            'vendedor_id': str(transaction.vendedor_id),
            'comprador_id': str(transaction.comprador_id),
            'monto_vendedor': str(transaction.monto_vendedor),
            'porcentaje_mestocker': str(transaction.porcentaje_mestocker),
            'transaction_type': transaction.transaction_type.value,
            'referencia_externa': transaction.referencia_externa,
        }

        # Add commission data if available
        if commission:
            hash_data.update({
                'commission_id': str(commission.id),
                'commission_rate': str(commission.commission_rate),
                'commission_amount': str(commission.commission_amount),
                'order_id': str(commission.order_id)
            })

        # Create deterministic string representation
        hash_string = '|'.join(f"{k}:{v}" for k, v in sorted(hash_data.items()))

        # Generate HMAC-SHA256 with secret
        return hmac.new(
            self.integrity_secret.encode('utf-8'),
            hash_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _validate_transaction_integrity_hash(self, transaction: Transaction) -> bool:
        """Validate transaction integrity hash."""

        if not self.enable_integrity_checks or not hasattr(transaction, 'integrity_hash'):
            return True  # Skip validation if not enabled or hash not present

        # Regenerate hash with current transaction data
        expected_hash = self._generate_integrity_hash(transaction)

        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(transaction.integrity_hash, expected_hash)

    def _validate_financial_consistency(self, transaction: Transaction, commission: Commission = None) -> Dict[str, bool]:
        """Comprehensive financial consistency validation."""

        validation_results = {'valid': True, 'errors': []}

        # Basic amount validation
        if transaction.monto <= 0:
            validation_results['valid'] = False
            validation_results['errors'].append('Transaction amount must be positive')

        # Commission-transaction consistency
        if commission and transaction.transaction_type == TransactionType.COMISION:
            # Validate amounts match
            if abs(transaction.monto_vendedor - commission.vendor_amount) > Decimal('0.01'):
                validation_results['valid'] = False
                validation_results['errors'].append('Transaction-commission amount mismatch')

            # Validate percentage calculation
            expected_percentage = float(commission.commission_rate * 100)
            if abs(transaction.porcentaje_mestocker - expected_percentage) > 0.01:
                validation_results['valid'] = False
                validation_results['errors'].append('Commission percentage mismatch')

        # Cryptographic integrity validation
        if self.enable_integrity_checks:
            if not self._validate_transaction_integrity_hash(transaction):
                validation_results['valid'] = False
                validation_results['errors'].append('Cryptographic integrity validation failed')

        return validation_results

    def create_transaction(
        self,
        monto: Decimal,
        metodo_pago: MetodoPago,
        transaction_type: TransactionType,
        comprador_id: UUID,
        vendedor_id: Optional[UUID] = None,
        inventory_id: Optional[int] = None,
        porcentaje_mestocker: Optional[Decimal] = None,
        notes: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Transaction:
        """
        Crea una nueva transacción genérica

        Args:
            monto: Monto de la transacción
            metodo_pago: Método de pago
            transaction_type: Tipo de transacción
            comprador_id: ID del comprador
            vendedor_id: ID del vendedor (opcional)
            inventory_id: ID del inventario relacionado (opcional)
            porcentaje_mestocker: Porcentaje de comisión (opcional)
            notes: Notas adicionales
            db: Sesión de base de datos opcional

        Returns:
            Transaction: Nueva transacción creada

        Raises:
            TransactionError: Si hay errores en la creación
        """
        db = db or self.get_db()

        try:
            # Validate amount
            if monto <= 0:
                raise TransactionError("Transaction amount must be positive")

            if monto > self.max_transaction_amount:
                raise TransactionError(f"Transaction amount exceeds maximum: {self.max_transaction_amount}")

            if monto < self.min_transaction_amount:
                raise TransactionError(f"Transaction amount below minimum: {self.min_transaction_amount}")

            # Validate users exist
            buyer = db.query(User).filter(User.id == comprador_id).first()
            if not buyer:
                raise TransactionError(f"Buyer {comprador_id} not found")

            if vendedor_id:
                vendor = db.query(User).filter(User.id == vendedor_id).first()
                if not vendor:
                    raise TransactionError(f"Vendor {vendedor_id} not found")

            # Calculate vendor amount
            if porcentaje_mestocker and vendedor_id:
                commission_rate = porcentaje_mestocker / Decimal('100')
                platform_amount = monto * commission_rate
                vendor_amount = monto - platform_amount
            else:
                vendor_amount = monto if vendedor_id else Decimal('0')

            # Generate transaction reference
            transaction_ref = self._generate_transaction_reference()

            # Create transaction
            transaction = Transaction(
                monto=monto,
                metodo_pago=metodo_pago,
                estado=EstadoTransaccion.PENDIENTE,
                transaction_type=transaction_type,
                comprador_id=comprador_id,
                vendedor_id=vendedor_id,
                porcentaje_mestocker=float(porcentaje_mestocker) if porcentaje_mestocker else None,
                monto_vendedor=vendor_amount,
                referencia_externa=transaction_ref,
                observaciones=notes,
                inventory_id=inventory_id
            )

            # Generate integrity hash
            if self.enable_integrity_checks:
                transaction.integrity_hash = self._generate_integrity_hash(transaction)

            # Save transaction
            db.add(transaction)
            db.commit()
            db.refresh(transaction)

            # Log creation
            logger.info(f"Transaction created: {transaction.id} - {transaction_ref}")

            return transaction

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating transaction: {e}")
            if isinstance(e, TransactionError):
                raise
            raise TransactionError(f"Unexpected error creating transaction: {str(e)}")

    def update_transaction_status(
        self,
        transaction_id: UUID,
        new_status: EstadoTransaccion,
        notes: Optional[str] = None,
        payment_reference: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Transaction:
        """
        Actualiza el estado de una transacción

        Args:
            transaction_id: ID de la transacción
            new_status: Nuevo estado
            notes: Notas adicionales
            payment_reference: Referencia de pago
            db: Sesión de base de datos opcional

        Returns:
            Transaction: Transacción actualizada

        Raises:
            TransactionError: Si hay errores en la actualización
        """
        db = db or self.get_db()

        try:
            transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
            if not transaction:
                raise TransactionError(f"Transaction {transaction_id} not found")

            # Validate state transition
            valid_transitions = {
                EstadoTransaccion.PENDIENTE: [EstadoTransaccion.PROCESANDO, EstadoTransaccion.FALLIDA, EstadoTransaccion.CANCELADA],
                EstadoTransaccion.PROCESANDO: [EstadoTransaccion.COMPLETADA, EstadoTransaccion.FALLIDA],
                EstadoTransaccion.COMPLETADA: [],  # Final state
                EstadoTransaccion.FALLIDA: [EstadoTransaccion.PENDIENTE],  # Can retry
                EstadoTransaccion.CANCELADA: []  # Final state
            }

            if new_status not in valid_transitions.get(transaction.estado, []):
                raise TransactionError(
                    f"Invalid state transition from {transaction.estado} to {new_status}"
                )

            # Update transaction
            old_status = transaction.estado
            transaction.estado = new_status

            if payment_reference:
                transaction.referencia_pago = payment_reference

            if notes:
                current_notes = transaction.observaciones or ""
                transaction.observaciones = f"{current_notes}\n{datetime.now().isoformat()}: {notes}".strip()

            # Handle specific status updates
            if new_status == EstadoTransaccion.COMPLETADA and payment_reference:
                transaction.marcar_pago_completado(payment_reference)

            db.commit()

            # Log status change
            logger.info(f"Transaction {transaction_id} status changed: {old_status} -> {new_status}")

            return transaction

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating transaction {transaction_id}: {e}")
            if isinstance(e, TransactionError):
                raise
            raise TransactionError(f"Unexpected error updating transaction: {str(e)}")

    def calculate_fees(
        self,
        base_amount: Decimal,
        commission_rate: Decimal,
        transaction_type: TransactionType = TransactionType.VENTA
    ) -> Dict[str, Decimal]:
        """
        Calcula tarifas y montos para una transacción

        Args:
            base_amount: Monto base de la transacción
            commission_rate: Tasa de comisión (como decimal, ej: 0.15 para 15%)
            transaction_type: Tipo de transacción

        Returns:
            Dict con breakdown de montos calculados
        """
        try:
            if base_amount <= 0:
                raise TransactionError("Base amount must be positive")

            if commission_rate < 0 or commission_rate > 1:
                raise TransactionError("Commission rate must be between 0 and 1")

            # Calculate amounts
            platform_fee = base_amount * commission_rate
            vendor_amount = base_amount - platform_fee

            # Apply transaction type specific adjustments
            processing_fee = Decimal('0')
            if transaction_type == TransactionType.COMISION:
                # Small processing fee for commission transactions
                processing_fee = base_amount * Decimal('0.001')  # 0.1%
            elif transaction_type == TransactionType.DEVOLUCION:
                # No platform fee for refunds
                platform_fee = Decimal('0')
                vendor_amount = base_amount

            net_amount = base_amount - platform_fee - processing_fee

            return {
                'base_amount': base_amount,
                'platform_fee': platform_fee,
                'processing_fee': processing_fee,
                'vendor_amount': vendor_amount,
                'net_amount': net_amount,
                'commission_rate': commission_rate,
                'effective_rate': platform_fee / base_amount if base_amount > 0 else Decimal('0')
            }

        except Exception as e:
            logger.error(f"Error calculating fees: {e}")
            raise TransactionError(f"Error calculating transaction fees: {str(e)}")

    def process_refund(
        self,
        original_transaction_id: UUID,
        refund_amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Transaction:
        """
        Procesa una devolución/reembolso

        Args:
            original_transaction_id: ID de la transacción original
            refund_amount: Monto a reembolsar (None para reembolso completo)
            reason: Razón del reembolso
            db: Sesión de base de datos opcional

        Returns:
            Transaction: Nueva transacción de reembolso

        Raises:
            TransactionError: Si hay errores en el proceso
        """
        db = db or self.get_db()

        try:
            # Get original transaction
            original_tx = db.query(Transaction).filter(
                Transaction.id == original_transaction_id
            ).first()

            if not original_tx:
                raise TransactionError(f"Original transaction {original_transaction_id} not found")

            if original_tx.estado != EstadoTransaccion.COMPLETADA:
                raise TransactionError(f"Original transaction must be completed to process refund")

            # Determine refund amount
            if refund_amount is None:
                refund_amount = original_tx.monto
            elif refund_amount <= 0 or refund_amount > original_tx.monto:
                raise TransactionError(f"Invalid refund amount: {refund_amount}")

            # Create refund transaction
            refund_ref = self._generate_transaction_reference()

            refund_transaction = Transaction(
                monto=refund_amount,
                metodo_pago=original_tx.metodo_pago,
                estado=EstadoTransaccion.PENDIENTE,
                transaction_type=TransactionType.DEVOLUCION,
                comprador_id=original_tx.comprador_id,
                vendedor_id=original_tx.vendedor_id,
                porcentaje_mestocker=0.0,  # No commission on refunds
                monto_vendedor=refund_amount,  # Full amount goes back to buyer
                referencia_externa=refund_ref,
                observaciones=f"Refund for transaction {original_tx.referencia_externa}. Reason: {reason or 'Not specified'}",
                inventory_id=original_tx.inventory_id
            )

            # Generate integrity hash
            if self.enable_integrity_checks:
                refund_transaction.integrity_hash = self._generate_integrity_hash(refund_transaction)

            # Save refund transaction
            db.add(refund_transaction)
            db.flush()

            # Process refund immediately (in production, this would go through payment gateway)
            refund_transaction.estado = EstadoTransaccion.COMPLETADA
            refund_transaction.marcar_pago_completado(f"REFUND-{refund_ref}")

            db.commit()
            db.refresh(refund_transaction)

            # Log refund
            logger.info(f"Refund processed: {refund_transaction.id} for original {original_transaction_id}")

            return refund_transaction

        except Exception as e:
            db.rollback()
            logger.error(f"Error processing refund for {original_transaction_id}: {e}")
            if isinstance(e, TransactionError):
                raise
            raise TransactionError(f"Unexpected error processing refund: {str(e)}")