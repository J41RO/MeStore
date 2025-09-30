# ~/app/models/user.py
# ---------------------------------------------------------------------------------------------
# MeStore - Modelo SQLAlchemy User
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: user.py
# Ruta: ~/app/models/user.py
# Autor: Jairo
# Fecha de Creación: 2025-07-25
# Última Actualización: 2025-08-09
# Versión: 1.3.0
# Propósito: Modelo SQLAlchemy para gestión de usuarios del sistema con OTP
#            Incluye campos básicos, OTP verification, constraints de seguridad
#
# Modificaciones:
# 2025-07-25 - Creación inicial del modelo User básico
# 2025-07-25 - Agregados campos nombre y apellido
# 2025-08-01 - Agregados campos OTP para verificación email/SMS
# 2025-08-09 - Agregado relationship con ComissionDispute
#
# ---------------------------------------------------------------------------------------------

"""
Modelo SQLAlchemy User para MeStore.

Este módulo contiene el modelo principal para gestión de usuarios:
- Campos básicos: id, email, password_hash, nombre, apellido
- Campos OTP: email_verified, phone_verified, otp_secret, etc.
- Constraints de seguridad: email único, campos obligatorios
- Timestamps automáticos: created_at, updated_at
- Optimizaciones: índices apropiados para consultas frecuentes
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, JSON
from sqlalchemy import Index
from app.core.types import UUID, generate_uuid
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from sqlalchemy import Enum
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.payout_request import PayoutRequest

from app.models.base import BaseModel


class UserType(PyEnum):
    """
    Enumeración para tipos de usuario en el sistema.

    Jerarquía de permisos (menor a mayor):
        BUYER: Usuario básico que puede realizar compras
        VENDOR: Usuario que puede vender productos
        ADMIN: Administrador con permisos de gestión
        SUPERUSER: Super administrador con todos los permisos
        SYSTEM: Usuario sistema para operaciones internas

    IMPORTANT: Values match database enum (uppercase)
    """
    BUYER = "BUYER"
    VENDOR = "VENDOR"
    ADMIN = "ADMIN"
    SUPERUSER = "SUPERUSER"
    SYSTEM = "SYSTEM"

class VendorStatus(str, PyEnum):
    """
    Estados granulares para el proceso de onboarding de vendors.
    
    Flujo de estados:
        DRAFT: Registro iniciado, documentos pendientes
        PENDING_DOCUMENTS: Documentos subidos, pendientes de verificación  
        PENDING_APPROVAL: Documentos verificados, pendiente aprobación admin
        APPROVED: Vendor aprobado y activo
        REJECTED: Vendor rechazado con motivo
    """
    DRAFT = "draft"
    PENDING_DOCUMENTS = "pending_documents"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(BaseModel):
    """
    Modelo SQLAlchemy para usuarios del sistema.

    Campos:
        id: Clave primaria UUID autoincremental
        email: Email único del usuario (índice para búsquedas)
        password_hash: Hash bcrypt de la contraseña
        nombre: Nombre del usuario
        apellido: Apellido del usuario
        user_type: Tipo de usuario (comprador/vendedor/admin/superuser)
        is_active: Estado activo del usuario
        is_verified: Usuario ha verificado su email
        
        # Campos colombianos específicos
        cedula: Cédula de ciudadanía colombiana
        telefono: Número de teléfono
        ciudad: Ciudad de residencia
        empresa: Empresa donde trabaja
        direccion: Dirección completa
        
        # Campos OTP para verificación
        email_verified: Email verificado con OTP
        phone_verified: Teléfono verificado con OTP
        otp_secret: Código OTP temporal (6 dígitos)
        otp_expires_at: Expiración del código OTP
        otp_attempts: Intentos fallidos de OTP
        otp_type: Tipo de OTP (EMAIL o SMS)
        last_otp_sent: Último envío de OTP
        
        # Timestamps automáticos
        last_login: Último login del usuario
        created_at: Timestamp de creación automático
        updated_at: Timestamp de última actualización automático

    Constraints:
        - Email debe ser único en toda la tabla
        - Email y password_hash son campos obligatorios
        - Índices optimizados para consultas frecuentes
    """

    __tablename__ = "users"

    # === CLAVE PRIMARIA ===
    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid,
        index=True,
        comment="Identificador único UUID del usuario"
    )

    # === CAMPOS BANCARIOS PARA PERFIL ===
    banco = Column(
        String(100),
        nullable=True,
        comment="Nombre del banco para transferencias (opcional)"
    )

    tipo_cuenta = Column(
        String(20),
        nullable=True,
        comment="Tipo de cuenta: AHORROS o CORRIENTE (opcional)"
    )

    numero_cuenta = Column(
        String(50),
        nullable=True,
        comment="Número de cuenta bancaria (opcional)"
    )

    # === CAMPOS DE RESET DE CONTRASEÑA ===
    reset_token = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Token temporal para reset de contraseña"
    )

    reset_token_expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Fecha y hora de expiración del token de reset"
    )

    reset_attempts = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Número de intentos de reset de contraseña"
    )

    last_reset_request = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha y hora del último request de reset"
    )

    # === CAMPOS GOOGLE OAUTH ===
    google_id = Column(
        String(100),
        nullable=True,
        unique=True,
        index=True,
        comment="ID único de Google para OAuth"
    )

    google_email = Column(
        String(255),
        nullable=True,
        comment="Email desde Google OAuth (puede diferir del email principal)"
    )

    google_name = Column(
        String(200),
        nullable=True,
        comment="Nombre completo desde Google OAuth"
    )

    google_picture = Column(
        String(500),
        nullable=True,
        comment="URL de foto de perfil desde Google"
    )

    google_verified_email = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Si el email está verificado en Google"
    )

    oauth_provider = Column(
        String(50),
        nullable=True,
        comment="Proveedor OAuth usado (google, facebook, etc.)"
    )

    oauth_linked_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha cuando se vinculó la cuenta OAuth"
    )

    # === CAMPOS DE AUTENTICACIÓN ===
    email = Column(
        String(255), 
        unique=True, 
        nullable=False, 
        index=True,
        comment="Email único del usuario, usado para login"
    )

    password_hash = Column(
        String(255),
        nullable=False,
        comment="Hash bcrypt de la contraseña del usuario"
    )

    # === CAMPOS DE INFORMACIÓN PERSONAL ===
    nombre = Column(
        String(100),
        nullable=True,
        comment="Nombre del usuario"
    )

    apellido = Column(
        String(100),
        nullable=True,
        comment="Apellido del usuario"
    )

    # === TIPO Y ESTADO DE USUARIO ===
    user_type = Column(
        Enum(UserType),
        nullable=False,
        default=UserType.BUYER,
        comment="Tipo de usuario: buyer, vendor, admin o superuser"
    )

    vendor_status = Column(
        Enum(VendorStatus),
        nullable=True,
        default=VendorStatus.DRAFT,
        comment="Estado específico del proceso de onboarding de vendor"
    )

    is_active = Column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="Indica si el usuario está activo en el sistema"
    )

    is_verified = Column(
        Boolean,
        default=False,
        server_default='false',
        nullable=False,
        comment="Indica si el usuario ha verificado su email"
    )

    # === CAMPOS ESPECÍFICOS COLOMBIANOS ===
    cedula = Column(
        String(20),
        nullable=True,
        unique=True,
        index=True,
        comment="Cédula de ciudadanía colombiana (opcional, única)"
    )

    telefono = Column(
        String(20),
        nullable=True,
        comment="Número de teléfono colombiano (opcional)"
    )

    ciudad = Column(
        String(100),
        nullable=True,
        comment="Ciudad de residencia en Colombia (opcional)"
    )

    empresa = Column(
        String(200),
        nullable=True,
        comment="Empresa donde trabaja el usuario (opcional)"
    )

    direccion = Column(
        String(300),
        nullable=True,
        comment="Dirección de residencia completa (opcional)"
    )

    # === CAMPOS OTP PARA VERIFICACIÓN EMAIL/SMS ===
    email_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment='Email verificado con código OTP'
    )

    phone_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment='Teléfono verificado con código OTP'
    )

    otp_secret = Column(
        String(6),
        nullable=True,
        comment='Código OTP temporal (6 dígitos)'
    )

    otp_expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment='Fecha y hora de expiración del código OTP'
    )

    otp_attempts = Column(
        Integer,
        default=0,
        nullable=False,
        comment='Número de intentos fallidos de verificación OTP'
    )

    otp_type = Column(
        String(10),
        nullable=True,
        comment='Tipo de OTP enviado: EMAIL o SMS'
    )

    last_otp_sent = Column(
        DateTime(timezone=True),
        nullable=True,
        comment='Fecha y hora del último envío de OTP'
    )

    # === CAMPOS ADMINISTRATIVOS ===
    security_clearance_level = Column(
        Integer,
        nullable=False,
        default=3,
        comment='Nivel de autorización de seguridad (1-5) para usuarios admin'
    )

    department_id = Column(
        String(100),
        nullable=True,
        comment='ID del departamento al que pertenece el usuario admin'
    )

    employee_id = Column(
        String(50),
        nullable=True,
        comment='ID de empleado para usuarios administrativos'
    )

    performance_score = Column(
        Integer,
        nullable=False,
        default=100,
        comment='Puntuación de desempeño del usuario admin (0-100)'
    )

    failed_login_attempts = Column(
        Integer,
        nullable=False,
        default=0,
        comment='Número de intentos fallidos de login'
    )

    account_locked_until = Column(
        DateTime(timezone=True),
        nullable=True,
        comment='Fecha hasta la cual la cuenta está bloqueada'
    )

    force_password_change = Column(
        Boolean,
        default=False,
        nullable=False,
        comment='Indica si el usuario debe cambiar su contraseña en el próximo login'
    )

    # === TIMESTAMPS ===
    last_login = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp del último login del usuario"
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp de última actualización del registro"
    )

    # === CAMPOS DE PERFIL DE VENDOR ===
    # Avatar/Logo del vendor
    avatar_url = Column(
        String(500), 
        nullable=True, 
        comment="URL del avatar/logo del vendor"
    )
    
    # Información del negocio
    business_name = Column(
        String(200), 
        nullable=True, 
        comment="Nombre comercial del negocio"
    )
    
    business_description = Column(
        Text, 
        nullable=True, 
        comment="Descripción del negocio"
    )
    
    website_url = Column(
        String(500), 
        nullable=True, 
        comment="Sitio web del vendor"
    )
    
    social_media_links = Column(
        JSON, 
        nullable=True, 
        comment="Enlaces de redes sociales"
    )
    
    business_hours = Column(
        JSON, 
        nullable=True, 
        comment="Horarios de atención"
    )
    
    shipping_policy = Column(
        Text, 
        nullable=True, 
        comment="Política de envíos"
    )
    
    return_policy = Column(
        Text, 
        nullable=True, 
        comment="Política de devoluciones"
    )
    
    # === CONFIGURACIONES DE NOTIFICACIONES VENDOR ===
    notification_preferences = Column(
        JSON, 
        nullable=True,
        default={
            "email_new_orders": True,
            "email_low_stock": True,
            "sms_urgent_orders": False,
            "push_daily_summary": True
        },
        comment="Preferencias de notificaciones del vendor"
    )
    
    # === INFORMACIÓN BANCARIA EXPANDIDA ===
    bank_name = Column(
        String(100), 
        nullable=True, 
        comment="Nombre del banco"
    )
    
    account_holder_name = Column(
        String(200), 
        nullable=True, 
        comment="Titular de la cuenta"
    )
    
    account_number = Column(
        String(50), 
        nullable=True, 
        comment="Número de cuenta"
    )

    # === RELATIONSHIPS ===
    # Relationship con PayoutRequest
    payout_requests = relationship('PayoutRequest', back_populates='vendedor')

    # Relationship con Storage
    espacios_storage = relationship(
        "Storage",
        foreign_keys="Storage.vendedor_id",
        back_populates="vendedor"
    )

    # Relationship con Product
    productos_vendidos = relationship(
        "Product",
        foreign_keys="Product.vendedor_id",
        back_populates="vendedor"
    )

    # Relationships con Transaction
    transacciones_comprador = relationship(
        "Transaction",
        foreign_keys="Transaction.comprador_id",
        back_populates="comprador"
    )

    transacciones_vendedor = relationship(
        "Transaction",
        foreign_keys="Transaction.vendedor_id",
        back_populates="vendedor"
    )

    # Relationships con Order system
    orders = relationship("Order", back_populates="buyer")
    payment_methods = relationship("PaymentMethod", back_populates="buyer")

    # Relationship con Inventory
    ubicaciones_inventario = relationship(
        "Inventory",
        back_populates="user",
        overlaps="inventarios_actualizados,updated_by"
    )

    # Relationship con commission disputes
    commission_disputes = relationship(
        "ComissionDispute",
        foreign_keys="ComissionDispute.usuario_id",
        back_populates="usuario"
    )

    # Commission relationships
    vendor_commissions = relationship(
        "Commission",
        foreign_keys="Commission.vendor_id",
        back_populates="vendor"
    )
    approved_commissions = relationship(
        "Commission",
        foreign_keys="Commission.approved_by_id",
        back_populates="approver"
    )

    # Admin Activity Log relationship
    admin_activity_logs = relationship(
        "AdminActivityLog",
        foreign_keys="AdminActivityLog.admin_user_id",
        back_populates="admin_user"
    )
    # Relationship con InventoryAudit
    auditorias_realizadas = relationship(
        "InventoryAudit",
        foreign_keys="InventoryAudit.auditor_id",
        back_populates="auditor"
    )

    # Relationships con VendorAuditLog
    audit_logs_received = relationship(
        "VendorAuditLog",
        foreign_keys="VendorAuditLog.vendor_id",
        back_populates="vendor"
    )

    audit_logs_created = relationship(
        "VendorAuditLog",
        foreign_keys="VendorAuditLog.admin_id",
        back_populates="admin"
    )

    # Relationships con VendorNote
    vendor_notes_received = relationship(
        "VendorNote",
        foreign_keys="VendorNote.vendor_id",
        back_populates="vendor"
    )

    vendor_notes_created = relationship(
        "VendorNote",
        foreign_keys="VendorNote.admin_id",
        back_populates="admin"
    )

    # Relación con documentos de vendor
    vendor_documents = relationship(
        "VendorDocument",
        foreign_keys="VendorDocument.vendor_id",
        back_populates="vendor"
    )

    # === ÍNDICES OPTIMIZADOS ===
    __table_args__ = (
        Index('ix_user_type_active', 'user_type', 'is_active'),  # Vendedores activos
        Index('ix_user_email_active', 'email', 'is_active'),     # Autenticación optimizada
        Index('ix_user_created_type', 'created_at', 'user_type'), # Reportes temporales
        Index('ix_user_active_created', 'is_active', 'created_at'), # Usuarios recientes activos
        Index('ix_user_otp_expires', 'otp_expires_at'),          # OTP expiración
        Index('ix_user_email_verified', 'email_verified'),       # Usuarios verificados
        Index('ix_user_google_id', 'google_id'),                 # Google OAuth lookup
        Index('ix_user_oauth_provider', 'oauth_provider'),       # OAuth provider search
    )

    def __init__(self, **kwargs):
        """Constructor personalizado para aplicar defaults correctamente."""
        # Aplicar defaults explícitos para campos de estado
        if 'is_verified' not in kwargs:
            kwargs['is_verified'] = False
        if 'is_active' not in kwargs:
            kwargs['is_active'] = True
        if 'email_verified' not in kwargs:
            kwargs['email_verified'] = False
        if 'phone_verified' not in kwargs:
            kwargs['phone_verified'] = False
        if 'otp_attempts' not in kwargs:
            kwargs['otp_attempts'] = 0
            
        # Llamar al constructor padre
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """Representación string del objeto User para debugging."""
        return f"<User(id={self.id}, email='{self.email}', active={self.is_active})>"

    def __str__(self) -> str:
        """Representación string amigable del User."""
        status = "activo" if self.is_active else "inactivo"
        return f"Usuario {self.email} ({status})"

    @property
    def full_name(self) -> str:
        """Retorna el nombre completo del usuario."""
        if self.nombre and self.apellido:
            return f"{self.nombre} {self.apellido}"
        elif self.nombre:
            return self.nombre
        elif self.apellido:
            return self.apellido
        else:
            return "Usuario sin nombre"

    def to_dict(self) -> dict:
        """Convierte el objeto User a diccionario para serialización."""
        return {
            'id': str(self.id) if self.id else None,
            'email': self.email,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'user_type': self.user_type.value if self.user_type else None,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'email_verified': self.email_verified,
            'phone_verified': self.phone_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'cedula': self.cedula,
            'telefono': self.telefono,
            'ciudad': self.ciudad,
            'empresa': self.empresa,
            'direccion': self.direccion,
            'full_name': self.full_name
        }

    def to_enterprise_dict(self) -> dict:
        """Convierte el objeto User a diccionario con campos enterprise para admin management."""
        return {
            'id': str(self.id) if self.id else None,
            'email': self.email,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'full_name': self.full_name,
            'user_type': self.user_type.value if self.user_type else None,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'security_clearance_level': self.security_clearance_level,
            'department_id': self.department_id,
            'employee_id': self.employee_id,
            'performance_score': self.performance_score,
            'failed_login_attempts': self.failed_login_attempts,
            'account_locked': self.account_locked_until is not None,
            'requires_password_change': self.force_password_change,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'telefono': self.telefono,
            'ciudad': self.ciudad,
            'departamento': getattr(self, 'departamento', None)
        }

    # === MÉTODOS OTP ===
    def is_otp_valid(self) -> bool:
        """Verifica si el OTP actual no ha expirado."""
        if not self.otp_expires_at:
            return False
        return datetime.utcnow() < self.otp_expires_at.replace(tzinfo=None)

    def can_request_otp(self) -> bool:
        """Verifica si puede solicitar un nuevo OTP (cooldown de 1 minuto)."""
        if not self.last_otp_sent:
            return True
        cooldown_seconds = 60  # 1 minuto
        time_since_last = datetime.utcnow() - self.last_otp_sent.replace(tzinfo=None)
        return time_since_last.total_seconds() >= cooldown_seconds

    def reset_otp_attempts(self):
        """Reinicia el contador de intentos fallidos de OTP."""
        self.otp_attempts = 0

    def increment_otp_attempts(self):
        """Incrementa el contador de intentos fallidos de OTP."""
        self.otp_attempts += 1

    def is_otp_blocked(self) -> bool:
        """Verifica si está bloqueado por demasiados intentos fallidos."""
        return self.otp_attempts >= 5  # Máximo 5 intentos

    # === MÉTODOS PASSWORD RESET ===
    def can_request_password_reset(self) -> bool:
        """Verifica si puede solicitar reset de contraseña (cooldown 5 minutos)."""
        if not self.last_reset_request:
            return True
        cooldown_seconds = 300  # 5 minutos
        time_since_last = datetime.utcnow() - self.last_reset_request.replace(tzinfo=None)
        return time_since_last.total_seconds() >= cooldown_seconds

    def is_reset_token_valid(self) -> bool:
        """Verifica si el token de reset es válido y no ha expirado."""
        if not self.reset_token or not self.reset_token_expires_at:
            return False
        return datetime.utcnow() < self.reset_token_expires_at.replace(tzinfo=None)

    def is_reset_blocked(self) -> bool:
        """Verifica si está bloqueado por demasiados intentos de reset."""
        return (self.reset_attempts or 0) >= 3  # Máximo 3 intentos por día

    def increment_reset_attempts(self):
        """Incrementa el contador de intentos fallidos de reset."""
        self.reset_attempts += 1

    def clear_reset_data(self):
        """Limpia todos los datos de reset de contraseña."""
        self.reset_token = None
        self.reset_token_expires_at = None
        self.reset_attempts = 0

    # === MÉTODOS DE AUTORIZACIÓN ===
    def is_superuser(self) -> bool:
        """Verifica si el usuario es SUPERUSER."""
        return self.user_type == UserType.SUPERUSER

    def is_admin(self) -> bool:
        """Verifica si el usuario es ADMIN."""
        return self.user_type == UserType.ADMIN

    def is_admin_or_higher(self) -> bool:
        """Verifica si el usuario es ADMIN, SUPERUSER o SYSTEM."""
        return self.user_type in [UserType.ADMIN, UserType.SUPERUSER, UserType.SYSTEM]

    def is_vendor(self) -> bool:
        """Verifica si el usuario es VENDOR."""
        return self.user_type == UserType.VENDOR

    def is_buyer(self) -> bool:
        """Verifica si el usuario es BUYER."""
        return self.user_type == UserType.BUYER

    def is_account_locked(self) -> bool:
        """Verifica si la cuenta está bloqueada."""
        if not self.account_locked_until:
            return False
        return datetime.utcnow() < self.account_locked_until.replace(tzinfo=None)

    def is_superuser(self) -> bool:
        """Verifica si el usuario es un superusuario."""
        return self.user_type == UserType.SUPERUSER

    def has_required_colombian_consents(self) -> bool:
        """Verifica si el usuario ha aceptado los consentimientos requeridos en Colombia."""
        # Verificar habeas data y tratamiento de datos según ley colombiana
        habeas_data = getattr(self, 'habeas_data_accepted', False)
        data_processing = getattr(self, 'data_processing_consent', False)
        return habeas_data and data_processing

# Alias para Buyer - usar User con user_type='buyer'
# Se define aquí para referencia en los modelos de orden
from sqlalchemy import text

def get_buyers():
    """Helper function to get buyers"""
    from sqlalchemy.orm import Session
    return Session.query(User).filter(User.user_type == 'BUYER')