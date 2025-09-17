# ~/app/models/commission.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Commission Model for Financial Operations (PRODUCTION_READY)
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: commission.py
# Ruta: ~/app/models/commission.py
# Autor: Jairo
# Fecha de Creación: 2025-09-12
# Última Actualización: 2025-09-12
# Versión: 1.0.0
# Propósito: Sistema de comisiones con configuración dinámica para hosting
#            Incluye cálculo automático, separación vendor/platform, auditoría
#
# Modificaciones:
# 2025-09-12 - Creación inicial con preparación hosting enterprise
#
# ---------------------------------------------------------------------------------------------

"""
PRODUCTION_READY: Sistema de comisiones con configuración dinámica

Este módulo contiene:
- Commission: Modelo principal para comisiones calculadas por orden
- CommissionSettings: Configuración dinámica por ambiente  
- CommissionStatus: Estados de comisiones para auditoria
- Relationships optimizadas con User, Order, Transaction
- Índices para performance en queries frecuentes
- Configuración dinámica para hosting (no URLs hardcodeadas)
"""

import os
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum as PyEnum
from typing import Dict, Optional
from datetime import datetime
from uuid import uuid4
import uuid

from sqlalchemy import (
    DECIMAL,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel


class CommissionStatus(PyEnum):
    """Estados de una comisión para auditoría financiera"""
    PENDING = "PENDING"           # Calculada pero no procesada
    APPROVED = "APPROVED"         # Aprobada para pago
    PAID = "PAID"                # Pagada al vendedor
    DISPUTED = "DISPUTED"         # En disputa
    REFUNDED = "REFUNDED"         # Reembolsada
    CANCELLED = "CANCELLED"       # Cancelada


class CommissionType(PyEnum):
    """Tipos de comisión según el producto/categoría"""
    STANDARD = "STANDARD"         # Comisión estándar
    PREMIUM = "PREMIUM"           # Comisión reducida para vendors premium
    PROMOTIONAL = "PROMOTIONAL"   # Comisión promocional temporal
    CATEGORY_BASED = "CATEGORY_BASED"  # Basada en categoría del producto


class Commission(BaseModel):
    """
    PRODUCTION_READY: Modelo Commission para cálculos financieros enterprise
    
    Registra comisiones calculadas automáticamente por cada orden,
    con separación precisa de montos vendor/platform y auditoría completa.
    """
    __tablename__ = "commissions"

    # Primary identification
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    commission_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Foreign keys - optimized with indexes
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    vendor_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Financial amounts - using DECIMAL for precision
    order_amount = Column(DECIMAL(precision=10, scale=2), nullable=False)
    commission_rate = Column(DECIMAL(precision=5, scale=4), nullable=False)  # e.g., 0.0500 = 5%
    commission_amount = Column(DECIMAL(precision=10, scale=2), nullable=False)
    vendor_amount = Column(DECIMAL(precision=10, scale=2), nullable=False)  # order_amount - commission_amount
    platform_amount = Column(DECIMAL(precision=10, scale=2), nullable=False)  # commission_amount
    
    # Commission metadata
    commission_type = Column(Enum(CommissionType), nullable=False, default=CommissionType.STANDARD)
    status = Column(Enum(CommissionStatus), nullable=False, default=CommissionStatus.PENDING, index=True)
    currency = Column(String(3), nullable=False, default="COP")
    
    # Audit and tracking fields
    calculation_method = Column(String(100), nullable=False, default="automatic")
    notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)  # For internal admin use
    
    # Status tracking timestamps - critical for financial auditing
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    disputed_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Approval tracking
    approved_by_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships - optimized loading
    order = relationship("Order", back_populates="commissions", lazy="select")
    vendor = relationship("User", foreign_keys=[vendor_id], back_populates="vendor_commissions", lazy="select")
    approver = relationship("User", foreign_keys=[approved_by_id], back_populates="approved_commissions", lazy="select")
    transaction = relationship("Transaction", back_populates="commission", lazy="select")
    # TODO: Add disputes relationship when ComissionDispute model is updated to include commission_id
    # disputes = relationship("ComissionDispute", back_populates="commission", cascade="all, delete-orphan")
    
    # Database constraints for financial integrity
    __table_args__ = (
        # Ensure positive amounts
        CheckConstraint('order_amount > 0', name='check_order_amount_positive'),
        CheckConstraint('commission_amount >= 0', name='check_commission_amount_non_negative'),
        CheckConstraint('vendor_amount >= 0', name='check_vendor_amount_non_negative'),
        CheckConstraint('platform_amount >= 0', name='check_platform_amount_non_negative'),
        CheckConstraint('commission_rate >= 0 AND commission_rate <= 1', name='check_commission_rate_valid'),
        
        # Ensure math integrity: vendor_amount + platform_amount = order_amount
        CheckConstraint('vendor_amount + platform_amount = order_amount', name='check_amounts_balance'),
        
        # Performance indexes for common queries
        Index('idx_commission_vendor_status', vendor_id, status),
        Index('idx_commission_calculation_date', calculated_at),
        Index('idx_commission_order_vendor', order_id, vendor_id),
    )
    
    def __repr__(self) -> str:
        return f"<Commission {self.commission_number}: ${self.commission_amount} for vendor {self.vendor_id}>"
    
    def to_dict(self) -> Dict:
        """Serialización segura para APIs con formateo de montos"""
        return {
            'id': str(self.id),
            'commission_number': self.commission_number,
            'order_id': self.order_id,
            'vendor_id': self.vendor_id,
            'order_amount': float(self.order_amount),
            'commission_rate': float(self.commission_rate),
            'commission_amount': float(self.commission_amount),
            'vendor_amount': float(self.vendor_amount),
            'platform_amount': float(self.platform_amount),
            'commission_type': self.commission_type.value,
            'status': self.status.value,
            'currency': self.currency,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def calculate_commission(
        cls, 
        order_amount: Decimal, 
        commission_rate: Decimal,
        commission_type: CommissionType = CommissionType.STANDARD
    ) -> tuple[Decimal, Decimal, Decimal]:
        """
        Calcula montos de comisión con precisión financiera
        
        Returns:
            tuple: (commission_amount, vendor_amount, platform_amount)
        """
        # Ensure we're working with Decimal for financial precision
        order_amount = Decimal(str(order_amount))
        commission_rate = Decimal(str(commission_rate))
        
        # Calculate commission with proper rounding
        commission_amount = (order_amount * commission_rate).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        # Calculate vendor amount (what vendor receives)
        vendor_amount = (order_amount - commission_amount).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        # Platform amount is the commission
        platform_amount = commission_amount
        
        return commission_amount, vendor_amount, platform_amount
    
    def approve(self, approver_user_id: uuid.UUID, notes: Optional[str] = None) -> None:
        """Aprueba la comisión para pago"""
        self.status = CommissionStatus.APPROVED
        self.approved_at = func.now()
        self.approved_by_id = approver_user_id
        if notes:
            self.admin_notes = notes
    
    def mark_as_paid(self, notes: Optional[str] = None) -> None:
        """Marca la comisión como pagada"""
        self.status = CommissionStatus.PAID
        self.paid_at = func.now()
        if notes:
            self.admin_notes = (self.admin_notes or '') + f"\nPaid: {notes}"
    
    def dispute(self, notes: Optional[str] = None) -> None:
        """Marca la comisión como disputada"""
        self.status = CommissionStatus.DISPUTED
        self.disputed_at = func.now()
        if notes:
            self.notes = notes
    
    def resolve_dispute(self, resolution_notes: str, approver_user_id: uuid.UUID) -> None:
        """Resuelve la disputa de comisión"""
        self.status = CommissionStatus.APPROVED
        self.resolved_at = func.now()
        self.approved_by_id = approver_user_id
        self.admin_notes = (self.admin_notes or '') + f"\nDispute resolved: {resolution_notes}"


class CommissionSettings:
    """
    PRODUCTION_READY: Sistema de configuración dinámica para comisiones
    
    Maneja tasas de comisión y configuración por ambiente sin URLs hardcodeadas
    """
    
    def __init__(self):
        self.ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
        self.COMMISSION_RATES = self._get_commission_rates()
        self.PAYMENT_GATEWAY_CONFIG = self._get_payment_config()
        self.WEBHOOK_URLS = self._get_webhook_urls()
        self.AUDIT_LEVEL = os.getenv('COMMISSION_AUDIT_LEVEL', 'standard')
    
    def _get_commission_rates(self) -> Dict[str, float]:
        """Obtiene tasas de comisión por ambiente"""
        if self.ENVIRONMENT == 'production':
            # TODO_HOSTING: Configurar rates reales de producción
            return {
                'default_rate': float(os.getenv('DEFAULT_COMMISSION_RATE', '0.05')),  # 5%
                'premium_rate': float(os.getenv('PREMIUM_COMMISSION_RATE', '0.03')),  # 3% for premium vendors
                'promotional_rate': float(os.getenv('PROMOTIONAL_COMMISSION_RATE', '0.02')),  # 2% promotional
                'high_volume_rate': float(os.getenv('HIGH_VOLUME_COMMISSION_RATE', '0.04')),  # 4% for high volume
            }
        
        # Development/staging rates
        return {
            'default_rate': 0.05,      # 5%
            'premium_rate': 0.03,      # 3%
            'promotional_rate': 0.02,  # 2%
            'high_volume_rate': 0.04,  # 4%
        }
    
    def _get_payment_config(self) -> Dict[str, str]:
        """Configuración de gateway de pagos por ambiente"""
        # Dynamic URL configuration for hosting
        if self.ENVIRONMENT == 'production':
            base_url = os.getenv('BASE_URL', 'https://api.tudominio.com')
        else:
            base_url = os.getenv('BASE_URL', f"http://{os.getenv('HOST', 'localhost')}:{os.getenv('PORT', '8000')}")
        
        if self.ENVIRONMENT == 'production':
            # TODO_HOSTING: Configurar gateway real de producción
            return {
                'gateway_url': os.getenv('PAYMENT_GATEWAY_URL', f"{base_url}/api/v1/payments"),
                'webhook_secret': os.getenv('PAYMENT_WEBHOOK_SECRET', 'dev-secret'),
                'api_key': os.getenv('PAYMENT_API_KEY', 'dev-key'),
            }
        
        return {
            'gateway_url': f"{base_url}/api/v1/payments",
            'webhook_secret': 'dev-webhook-secret',
            'api_key': 'dev-api-key',
        }
    
    def _get_webhook_urls(self) -> Dict[str, str]:
        """URLs de webhooks dinámicas por ambiente"""
        # Dynamic URL configuration for hosting
        if self.ENVIRONMENT == 'production':
            base_url = os.getenv('BASE_URL', 'https://api.tudominio.com')
        else:
            base_url = os.getenv('BASE_URL', f"http://{os.getenv('HOST', 'localhost')}:{os.getenv('PORT', '8000')}")
        
        return {
            'commission_calculated': f"{base_url}/api/v1/webhooks/commission/calculated",
            'commission_approved': f"{base_url}/api/v1/webhooks/commission/approved",
            'commission_paid': f"{base_url}/api/v1/webhooks/commission/paid",
            'commission_disputed': f"{base_url}/api/v1/webhooks/commission/disputed",
        }
    
    def get_commission_rate(self, commission_type: CommissionType = CommissionType.STANDARD) -> float:
        """Obtiene la tasa de comisión según el tipo"""
        rate_map = {
            CommissionType.STANDARD: self.COMMISSION_RATES['default_rate'],
            CommissionType.PREMIUM: self.COMMISSION_RATES['premium_rate'],
            CommissionType.PROMOTIONAL: self.COMMISSION_RATES['promotional_rate'],
            CommissionType.CATEGORY_BASED: self.COMMISSION_RATES['high_volume_rate'],
        }
        
        return rate_map.get(commission_type, self.COMMISSION_RATES['default_rate'])
    
    def validate_commission_calculation(self, commission: 'Commission') -> bool:
        """Valida que el cálculo de comisión sea correcto"""
        expected_commission, expected_vendor, expected_platform = Commission.calculate_commission(
            commission.order_amount,
            commission.commission_rate,
            commission.commission_type
        )
        
        return (
            commission.commission_amount == expected_commission and
            commission.vendor_amount == expected_vendor and
            commission.platform_amount == expected_platform
        )


# Global settings instance - initialized once per application
commission_settings = CommissionSettings()