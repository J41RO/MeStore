from pydantic import BaseModel, Field, validator, field_validator
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
import json

class ConfigCategory(str, Enum):
    """Valid configuration categories"""
    GENERAL = "general"
    EMAIL = "email"
    BUSINESS = "business"
    SECURITY = "security"

class ConfigDataType(str, Enum):
    """Valid data types for configuration values"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"

class SystemSettingBase(BaseModel):
    """Base schema for system settings"""
    key: str = Field(..., min_length=1, max_length=255, description="Unique configuration key")
    value: str = Field(..., description="Configuration value as string")
    category: ConfigCategory = Field(..., description="Configuration category")
    data_type: ConfigDataType = Field(..., description="Data type for value validation")
    description: str = Field(..., min_length=1, description="Human-readable description")
    default_value: Optional[str] = Field(None, description="Default value if not set")
    is_public: bool = Field(default=False, description="Visible to non-admin users")
    is_editable: bool = Field(default=True, description="Can be modified through UI")

class SystemSettingCreate(SystemSettingBase):
    """Schema for creating a new system setting"""
    
    @field_validator('value')

    
    @classmethod
    def validate_value_type(cls, v):
        """Validate that value matches the specified data_type"""
        if 'data_type' not in values:
            return v
            
        data_type = values['data_type']
        
        try:
            if data_type == ConfigDataType.BOOLEAN:
                # Accept various boolean representations
                bool_val = str(v).lower() in ('true', '1', 'yes', 'on')
                return str(bool_val).lower()
            elif data_type == ConfigDataType.INTEGER:
                int(v)  # Validate it's a valid integer
                return v
            elif data_type == ConfigDataType.FLOAT:
                float(v)  # Validate it's a valid float
                return v
            elif data_type == ConfigDataType.JSON:
                json.loads(v)  # Validate it's valid JSON
                return v
            # String type always valid
            return v
        except (ValueError, json.JSONDecodeError) as e:
            raise ValueError(f"Value '{v}' is not valid for data type '{data_type}': {str(e)}")

class SystemSettingUpdate(BaseModel):
    """Schema for updating a system setting"""
    value: str = Field(..., description="New configuration value")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SystemSettingBulkUpdate(BaseModel):
    """Schema for bulk updating multiple settings"""
    settings: Dict[str, str] = Field(..., description="Dictionary of key-value pairs to update")
    
    @field_validator('settings')

    
    @classmethod
    def validate_settings_not_empty(cls, v):
        if not v:
            raise ValueError("Settings dictionary cannot be empty")
        if len(v) > 50:  # Reasonable limit for bulk updates
            raise ValueError("Cannot update more than 50 settings at once")
        return v

class SystemSettingResponse(SystemSettingBase):
    """Schema for returning system setting data"""
    id: str
    last_modified_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    typed_value: Any = Field(..., description="Value converted to appropriate Python type")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SystemSettingPublicResponse(BaseModel):
    """Schema for public system settings (non-sensitive)"""
    key: str
    value: str
    category: ConfigCategory
    data_type: ConfigDataType
    description: str
    typed_value: Any
    
    class Config:
        from_attributes = True

class ConfigCategoryInfo(BaseModel):
    """Information about a configuration category"""
    name: str
    display_name: str
    description: str
    setting_count: int

class ConfigCategoriesResponse(BaseModel):
    """Response schema for categories endpoint"""
    categories: List[ConfigCategoryInfo]

class SystemConfigSummary(BaseModel):
    """Summary of system configuration"""
    total_settings: int
    categories: List[ConfigCategoryInfo]
    last_updated: Optional[datetime]
    editable_settings: int
    public_settings: int

class ConfigValidationError(BaseModel):
    """Error details for configuration validation"""
    key: str
    error: str
    current_value: Optional[str]
    expected_type: str

class ConfigValidationResponse(BaseModel):
    """Response for configuration validation"""
    valid: bool
    errors: List[ConfigValidationError]

# Predefined category information
CATEGORY_INFO = {
    ConfigCategory.GENERAL: {
        "display_name": "Configuración General",
        "description": "Configuraciones básicas del sistema como nombre, descripción y límites generales"
    },
    ConfigCategory.EMAIL: {
        "display_name": "Configuración de Email",
        "description": "Configuraciones SMTP y parámetros para el envío de correos electrónicos"
    },
    ConfigCategory.BUSINESS: {
        "display_name": "Configuración de Negocio",
        "description": "Parámetros comerciales como comisiones, aprobaciones automáticas y verificaciones"
    },
    ConfigCategory.SECURITY: {
        "display_name": "Configuración de Seguridad",
        "description": "Parámetros de seguridad, sesiones, autenticación y políticas de contraseñas"
    }
}

def get_category_display_name(category: ConfigCategory) -> str:
    """Get human-readable category name"""
    return CATEGORY_INFO.get(category, {}).get("display_name", category.value.title())

def get_category_description(category: ConfigCategory) -> str:
    """Get category description"""
    return CATEGORY_INFO.get(category, {}).get("description", "")

# Type definitions for better type hints
ConfigValue = Union[str, int, float, bool, Dict, List]
ConfigDict = Dict[str, ConfigValue]