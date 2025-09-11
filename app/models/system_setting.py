from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import Any, Dict, Optional
import json
from datetime import datetime

from app.database import Base

class SystemSetting(Base):
    """
    Model for storing system-wide configuration settings with categorization and validation.
    """
    __tablename__ = "system_settings"

    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)  # Store as JSON string for flexibility
    
    # Configuration metadata
    category = Column(String(50), nullable=False, index=True)  # general, email, security, business
    data_type = Column(String(20), nullable=False)  # string, integer, boolean, json, float
    description = Column(Text, nullable=False)
    default_value = Column(Text, nullable=True)
    
    # Access control
    is_public = Column(Boolean, default=False)  # Visible to non-admin users
    is_editable = Column(Boolean, default=True)  # Can be modified through UI
    
    # Audit fields
    last_modified_by = Column(Integer, nullable=True)  # FK to users
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Performance indexes
    __table_args__ = (
        Index('idx_system_settings_category', 'category'),
        Index('idx_system_settings_public', 'is_public'),
        Index('idx_system_settings_editable', 'is_editable'),
    )
    
    def get_typed_value(self) -> Any:
        """
        Convert stored string value to appropriate Python type based on data_type.
        """
        if not self.value:
            return self.get_default_typed_value()
            
        try:
            if self.data_type == 'boolean':
                return self.value.lower() in ('true', '1', 'yes', 'on')
            elif self.data_type == 'integer':
                return int(self.value)
            elif self.data_type == 'float':
                return float(self.value)
            elif self.data_type == 'json':
                return json.loads(self.value)
            else:  # string
                return self.value
        except (ValueError, json.JSONDecodeError):
            # Return default value if conversion fails
            return self.get_default_typed_value()
    
    def get_default_typed_value(self) -> Any:
        """
        Get the default value with proper type conversion.
        """
        if not self.default_value:
            return self._get_type_default()
            
        try:
            if self.data_type == 'boolean':
                return self.default_value.lower() in ('true', '1', 'yes', 'on')
            elif self.data_type == 'integer':
                return int(self.default_value)
            elif self.data_type == 'float':
                return float(self.default_value)
            elif self.data_type == 'json':
                return json.loads(self.default_value)
            else:  # string
                return self.default_value
        except (ValueError, json.JSONDecodeError):
            return self._get_type_default()
    
    def _get_type_default(self) -> Any:
        """
        Get system default for data type.
        """
        defaults = {
            'string': '',
            'integer': 0,
            'float': 0.0,
            'boolean': False,
            'json': {}
        }
        return defaults.get(self.data_type, '')
    
    def set_typed_value(self, value: Any) -> None:
        """
        Set value with proper type validation and conversion.
        """
        if self.data_type == 'boolean':
            if isinstance(value, bool):
                self.value = str(value).lower()
            else:
                # Convert string-like values
                self.value = str(bool(str(value).lower() in ('true', '1', 'yes', 'on'))).lower()
        elif self.data_type == 'integer':
            self.value = str(int(value))
        elif self.data_type == 'float':
            self.value = str(float(value))
        elif self.data_type == 'json':
            if isinstance(value, (dict, list)):
                self.value = json.dumps(value)
            else:
                self.value = str(value)
        else:  # string
            self.value = str(value)
    
    @classmethod
    def get_default_settings(cls) -> list[dict]:
        """
        Get list of default system settings to be created on first setup.
        """
        return [
            # GENERAL CATEGORY
            {
                'key': 'site_name',
                'value': 'MeStocker',
                'category': 'general',
                'data_type': 'string',
                'description': 'Nombre del sitio web',
                'default_value': 'MeStocker',
                'is_public': True,
                'is_editable': True
            },
            {
                'key': 'site_description', 
                'value': 'Tu almacén virtual en Bucaramanga',
                'category': 'general',
                'data_type': 'string',
                'description': 'Descripción del sitio web',
                'default_value': 'Tu almacén virtual en Bucaramanga',
                'is_public': True,
                'is_editable': True
            },
            {
                'key': 'maintenance_mode',
                'value': 'false',
                'category': 'general',
                'data_type': 'boolean',
                'description': 'Activar modo de mantenimiento',
                'default_value': 'false',
                'is_public': False,
                'is_editable': True
            },
            {
                'key': 'max_upload_size',
                'value': '10485760',
                'category': 'general',
                'data_type': 'integer',
                'description': 'Tamaño máximo de archivo en bytes (10MB)',
                'default_value': '10485760',
                'is_public': False,
                'is_editable': True
            },
            
            # EMAIL CATEGORY
            {
                'key': 'smtp_host',
                'value': 'localhost',
                'category': 'email',
                'data_type': 'string',
                'description': 'Servidor SMTP para envío de emails',
                'default_value': 'localhost',
                'is_public': False,
                'is_editable': True
            },
            {
                'key': 'smtp_port',
                'value': '587',
                'category': 'email',
                'data_type': 'integer',
                'description': 'Puerto del servidor SMTP',
                'default_value': '587',
                'is_public': False,
                'is_editable': True
            },
            {
                'key': 'smtp_user',
                'value': '',
                'category': 'email',
                'data_type': 'string',
                'description': 'Usuario para autenticación SMTP',
                'default_value': '',
                'is_public': False,
                'is_editable': True
            },
            {
                'key': 'email_from_name',
                'value': 'MeStocker',
                'category': 'email',
                'data_type': 'string',
                'description': 'Nombre del remitente en emails',
                'default_value': 'MeStocker',
                'is_public': False,
                'is_editable': True
            },
            {
                'key': 'email_from_address',
                'value': 'noreply@mestocker.com',
                'category': 'email',
                'data_type': 'string',
                'description': 'Dirección del remitente en emails',
                'default_value': 'noreply@mestocker.com',
                'is_public': False,
                'is_editable': True
            },
            {
                'key': 'email_notifications_enabled',
                'value': 'true',
                'category': 'email',
                'data_type': 'boolean',
                'description': 'Habilitar notificaciones por email',
                'default_value': 'true',
                'is_public': False,
                'is_editable': True
            },
            
            # BUSINESS CATEGORY
            {
                'key': 'default_commission_rate',
                'value': '0.15',
                'category': 'business',
                'data_type': 'float',
                'description': 'Tasa de comisión por defecto (15%)',
                'default_value': '0.15',
                'is_public': False,
                'is_editable': True
            },
            {
                'key': 'min_commission_rate',
                'value': '0.05',
                'category': 'business',
                'data_type': 'float',
                'description': 'Tasa mínima de comisión (5%)',
                'default_value': '0.05',
                'is_public': False,
                'is_editable': True
            },
            {
                'key': 'max_commission_rate',
                'value': '0.30',
                'category': 'business',
                'data_type': 'float',
                'description': 'Tasa máxima de comisión (30%)',
                'default_value': '0.30',
                'is_public': False,
                'is_editable': True
            },
            {
                'key': 'auto_approve_vendors',
                'value': 'false',
                'category': 'business',
                'data_type': 'boolean',
                'description': 'Aprobar vendedores automáticamente',
                'default_value': 'false',
                'is_public': False,
                'is_editable': True
            },
            {
                'key': 'require_vendor_verification',
                'value': 'true',
                'category': 'business',
                'data_type': 'boolean',
                'description': 'Requerir verificación de vendedores',
                'default_value': 'true',
                'is_public': False,
                'is_editable': True
            },
            
            # SECURITY CATEGORY
            {
                'key': 'session_timeout_minutes',
                'value': '120',
                'category': 'security',
                'data_type': 'integer',
                'description': 'Tiempo de expiración de sesión en minutos',
                'default_value': '120',
                'is_public': False,
                'is_editable': True
            },
            {
                'key': 'max_login_attempts',
                'value': '5',
                'category': 'security',
                'data_type': 'integer',
                'description': 'Máximo número de intentos de login',
                'default_value': '5',
                'is_public': False,
                'is_editable': True
            },
            {
                'key': 'password_min_length',
                'value': '8',
                'category': 'security',
                'data_type': 'integer',
                'description': 'Longitud mínima de contraseña',
                'default_value': '8',
                'is_public': False,
                'is_editable': True
            },
            {
                'key': 'require_2fa_admin',
                'value': 'false',
                'category': 'security',
                'data_type': 'boolean',
                'description': 'Requerir 2FA para administradores',
                'default_value': 'false',
                'is_public': False,
                'is_editable': True
            }
        ]
    
    def __repr__(self):
        return f"<SystemSetting(key='{self.key}', category='{self.category}', value='{self.value[:50]}...')>"