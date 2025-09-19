# Pydantic V2 Migration Examples for MeStore

## Real File Examples

This document shows actual before/after examples for key MeStore schema files.

## Example 1: leads.py Migration

### Before (V1 Syntax)

```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Literal
from datetime import datetime

class LeadCreateSchema(BaseModel):
    email: EmailStr = Field(..., description="Email corporativo del lead")
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre completo del contacto")
    tipo_negocio: Literal['vendedor', 'comprador', 'ambos'] = Field(..., description="Tipo de negocio del lead")
    telefono: Optional[str] = Field(None, max_length=20, description="Número de teléfono WhatsApp")
    empresa: Optional[str] = Field(None, max_length=200, description="Nombre de la empresa")
    source: Optional[str] = Field("landing", max_length=50, description="Fuente de captación del lead")

    @validator('telefono')
    def validate_telefono(cls, v):
        if v and v.strip():
            import re
            if not re.match(r'^[+]?[0-9\s\-()]{7,15}$', v.strip()):
                raise ValueError('Formato de teléfono inválido')
            return v.strip()
        return None

    @validator('nombre')
    def validate_nombre(cls, v):
        if not v or not v.strip():
            raise ValueError('Nombre es requerido')
        return v.strip().title()

    @validator('empresa')
    def validate_empresa(cls, v):
        if v and v.strip():
            return v.strip()
        return None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "juan.perez@miempresa.com",
                "nombre": "Juan Pérez",
                "tipo_negocio": "vendedor",
                "telefono": "+57 300 123 4567",
                "empresa": "Mi Empresa S.A.S",
                "source": "landing"
            }
        }

class LeadResponseSchema(BaseModel):
    id: int
    email: str
    nombre: str
    tipo_negocio: str
    telefono: Optional[str]
    empresa: Optional[str]
    source: str
    created_at: datetime
    status: str

    class Config:
        from_attributes = True
```

### After (V2 Syntax)

```python
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, Literal
from datetime import datetime

class LeadCreateSchema(BaseModel):
    email: EmailStr = Field(..., description="Email corporativo del lead")
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre completo del contacto")
    tipo_negocio: Literal['vendedor', 'comprador', 'ambos'] = Field(..., description="Tipo de negocio del lead")
    telefono: Optional[str] = Field(None, max_length=20, description="Número de teléfono WhatsApp")
    empresa: Optional[str] = Field(None, max_length=200, description="Nombre de la empresa")
    source: Optional[str] = Field("landing", max_length=50, description="Fuente de captación del lead")

    @field_validator('telefono')
    @classmethod
    def validate_telefono(cls, v):
        if v and v.strip():
            import re
            if not re.match(r'^[+]?[0-9\s\-()]{7,15}$', v.strip()):
                raise ValueError('Formato de teléfono inválido')
            return v.strip()
        return None

    @field_validator('nombre')
    @classmethod
    def validate_nombre(cls, v):
        if not v or not v.strip():
            raise ValueError('Nombre es requerido')
        return v.strip().title()

    @field_validator('empresa')
    @classmethod
    def validate_empresa(cls, v):
        if v and v.strip():
            return v.strip()
        return None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "juan.perez@miempresa.com",
                "nombre": "Juan Pérez",
                "tipo_negocio": "vendedor",
                "telefono": "+57 300 123 4567",
                "empresa": "Mi Empresa S.A.S",
                "source": "landing"
            }
        }
    )

class LeadResponseSchema(BaseModel):
    id: int
    email: str
    nombre: str
    tipo_negocio: str
    telefono: Optional[str]
    empresa: Optional[str]
    source: str
    created_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)
```

## Example 2: category.py Complex Validator Migration

### Before (V1 Syntax)

```python
from pydantic import BaseModel, Field, validator

class CategoryBulkCreate(BaseModel):
    categories: List[CategoryCreate] = Field(
        ...,
        min_items=1,
        max_items=100,
        description="Lista de categorías a crear (máximo 100)"
    )

    @validator('categories')
    def validate_categories(cls, v):
        """Validar que no hay slugs duplicados en el lote."""
        slugs = [cat.slug for cat in v if cat.slug]
        if len(slugs) != len(set(slugs)):
            raise ValueError("No se permiten slugs duplicados en el lote")
        return v

class ProductCategoryAssignment(BaseModel):
    category_ids: List[UUID] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="Lista de IDs de categorías a asignar (máximo 10)"
    )
    primary_category_id: Optional[UUID] = Field(
        None,
        description="ID de la categoría principal (debe estar en category_ids)"
    )

    @validator('primary_category_id')
    def validate_primary_category(cls, v, values):
        """Validar que la categoría principal esté en la lista de categorías."""
        if v is not None and 'category_ids' in values:
            if v not in values['category_ids']:
                raise ValueError("La categoría principal debe estar en la lista de categorías")
        return v
```

### After (V2 Syntax)

```python
from pydantic import BaseModel, Field, field_validator, model_validator

class CategoryBulkCreate(BaseModel):
    categories: List[CategoryCreate] = Field(
        ...,
        min_items=1,
        max_items=100,
        description="Lista de categorías a crear (máximo 100)"
    )

    @field_validator('categories')
    @classmethod
    def validate_categories(cls, v):
        """Validar que no hay slugs duplicados en el lote."""
        slugs = [cat.slug for cat in v if cat.slug]
        if len(slugs) != len(set(slugs)):
            raise ValueError("No se permiten slugs duplicados en el lote")
        return v

class ProductCategoryAssignment(BaseModel):
    category_ids: List[UUID] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="Lista de IDs de categorías a asignar (máximo 10)"
    )
    primary_category_id: Optional[UUID] = Field(
        None,
        description="ID de la categoría principal (debe estar en category_ids)"
    )

    @model_validator(mode='after')
    def validate_primary_category(self):
        """Validar que la categoría principal esté en la lista de categorías."""
        if self.primary_category_id is not None:
            if self.primary_category_id not in self.category_ids:
                raise ValueError("La categoría principal debe estar en la lista de categorías")
        return self
```

## Example 3: payout_request.py Financial Validation

### Before (V1 Syntax)

```python
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from datetime import datetime
from typing import Optional

class PayoutRequestCreate(BaseModel):
    monto_solicitado: Decimal = Field(..., gt=0, description="Monto a solicitar")
    tipo_cuenta: str = Field(..., pattern="^(AHORROS|CORRIENTE)$")
    numero_cuenta: str = Field(..., min_length=8, max_length=50)
    banco: str = Field(..., min_length=3, max_length=100)
    observaciones: Optional[str] = Field(None, max_length=500)

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v)
        }

    @validator('numero_cuenta')
    def validar_numero_cuenta(cls, v):
        """Validar que el número de cuenta sea numérico."""
        if not v.isdigit():
            raise ValueError('El número de cuenta debe contener solo dígitos')
        return v

    @validator('banco')
    def validar_banco(cls, v):
        """Validar nombre del banco."""
        if not v.strip():
            raise ValueError('El nombre del banco es obligatorio')
        return v.strip().title()

    @validator('monto_solicitado')
    def validar_monto_colombia(cls, v):
        """Validar límites de monto para Colombia."""
        if v > 50000000:  # 50 millones COP
            raise ValueError('El monto máximo es 50,000,000 COP')
        if v < 10000:  # Mínimo 10 mil COP
            raise ValueError('El monto mínimo es 10,000 COP')
        return v
```

### After (V2 Syntax)

```python
from pydantic import BaseModel, Field, field_validator, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional

class PayoutRequestCreate(BaseModel):
    monto_solicitado: Decimal = Field(..., gt=0, description="Monto a solicitar")
    tipo_cuenta: str = Field(..., pattern="^(AHORROS|CORRIENTE)$")
    numero_cuenta: str = Field(..., min_length=8, max_length=50)
    banco: str = Field(..., min_length=3, max_length=100)
    observaciones: Optional[str] = Field(None, max_length=500)

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v)
        }
    )

    @field_validator('numero_cuenta')
    @classmethod
    def validar_numero_cuenta(cls, v):
        """Validar que el número de cuenta sea numérico."""
        if not v.isdigit():
            raise ValueError('El número de cuenta debe contener solo dígitos')
        return v

    @field_validator('banco')
    @classmethod
    def validar_banco(cls, v):
        """Validar nombre del banco."""
        if not v.strip():
            raise ValueError('El nombre del banco es obligatorio')
        return v.strip().title()

    @field_validator('monto_solicitado')
    @classmethod
    def validar_monto_colombia(cls, v):
        """Validar límites de monto para Colombia."""
        if v > 50000000:  # 50 millones COP
            raise ValueError('El monto máximo es 50,000,000 COP')
        if v < 10000:  # Mínimo 10 mil COP
            raise ValueError('El monto mínimo es 10,000 COP')
        return v
```

## Example 4: common.py Generic Response Schemas

### Before (V1 Syntax)

```python
from typing import TypeVar, Generic, Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    status: APIStatus = APIStatus.SUCCESS
    data: T = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Human-readable message")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional response metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PaginatedResponse(BaseModel, Generic[T]):
    status: APIStatus = APIStatus.SUCCESS
    data: List[T] = Field(..., description="List of items")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")
    message: Optional[str] = Field(None, description="Human-readable message")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional response metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### After (V2 Syntax)

```python
from typing import TypeVar, Generic, Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    status: APIStatus = APIStatus.SUCCESS
    data: T = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Human-readable message")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional response metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

class PaginatedResponse(BaseModel, Generic[T]):
    status: APIStatus = APIStatus.SUCCESS
    data: List[T] = Field(..., description="List of items")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")
    message: Optional[str] = Field(None, description="Human-readable message")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional response metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
```

## Example 5: Advanced V2 Features Usage

### Using field_serializer for Custom Output

```python
from pydantic import BaseModel, Field, field_serializer
from decimal import Decimal
from datetime import datetime

class ProductPrice(BaseModel):
    price: Decimal = Field(..., description="Product price in COP")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_serializer('price')
    def serialize_price(self, price: Decimal) -> str:
        """Serialize price as formatted Colombian peso string"""
        return f"${price:,.0f} COP"

    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime) -> str:
        """Serialize datetime in Colombian timezone"""
        # Convert to Colombian time (UTC-5)
        return dt.isoformat()
```

### Using computed_field for Derived Values

```python
from pydantic import BaseModel, computed_field
from typing import Optional

class UserProfile(BaseModel):
    nombre: str
    apellido: str
    cedula: Optional[str] = None

    @computed_field
    @property
    def full_name(self) -> str:
        """Computed full name from nombre and apellido"""
        return f"{self.nombre} {self.apellido}"

    @computed_field
    @property
    def has_identification(self) -> bool:
        """Check if user has identification document"""
        return self.cedula is not None and len(self.cedula) > 0

    @computed_field
    @property
    def profile_completeness(self) -> float:
        """Calculate profile completeness percentage"""
        fields = [self.nombre, self.apellido, self.cedula]
        filled = sum(1 for field in fields if field)
        return (filled / len(fields)) * 100
```

### Using model_validator for Complex Business Rules

```python
from pydantic import BaseModel, model_validator, Field
from datetime import datetime, date
from typing import Optional

class VendorSubscription(BaseModel):
    vendor_id: str
    plan_type: str = Field(..., pattern="^(basic|premium|enterprise)$")
    start_date: date
    end_date: Optional[date] = None
    is_active: bool = True
    monthly_fee: Decimal

    @model_validator(mode='after')
    def validate_subscription_rules(self):
        """Validate complex business rules for vendor subscriptions"""

        # Rule 1: End date must be after start date
        if self.end_date and self.end_date <= self.start_date:
            raise ValueError('End date must be after start date')

        # Rule 2: Premium plans require specific fee structure
        if self.plan_type == 'premium' and self.monthly_fee < 50000:
            raise ValueError('Premium plans require minimum fee of 50,000 COP')

        # Rule 3: Enterprise plans must have end date
        if self.plan_type == 'enterprise' and not self.end_date:
            raise ValueError('Enterprise plans must have defined end date')

        # Rule 4: Active subscriptions must not be expired
        if self.is_active and self.end_date and self.end_date < date.today():
            raise ValueError('Active subscriptions cannot have past end dates')

        return self
```

## Example 6: Migrating Complex Inheritance Patterns

### Before (V1 Syntax)

```python
class BaseProduct(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal

    class Config:
        from_attributes = True

class DigitalProduct(BaseProduct):
    download_url: str
    file_size: int

    @validator('file_size')
    def validate_file_size(cls, v):
        if v > 1000000000:  # 1GB limit
            raise ValueError('File size cannot exceed 1GB')
        return v

    class Config(BaseProduct.Config):
        json_schema_extra = {
            "example": {
                "name": "Software License",
                "price": 99.99,
                "download_url": "https://...",
                "file_size": 50000000
            }
        }
```

### After (V2 Syntax)

```python
from pydantic import ConfigDict, field_validator

class BaseProduct(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal

    model_config = ConfigDict(from_attributes=True)

class DigitalProduct(BaseProduct):
    download_url: str
    file_size: int

    @field_validator('file_size')
    @classmethod
    def validate_file_size(cls, v):
        if v > 1000000000:  # 1GB limit
            raise ValueError('File size cannot exceed 1GB')
        return v

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Software License",
                "price": 99.99,
                "download_url": "https://...",
                "file_size": 50000000
            }
        }
    )
```

## Testing Your Migrations

### Unit Test Example

```python
import pytest
from pydantic import ValidationError

def test_lead_create_validation():
    """Test that LeadCreateSchema validation works after migration"""

    # Valid data
    valid_data = {
        "email": "test@example.com",
        "nombre": "Juan Pérez",
        "tipo_negocio": "vendedor",
        "telefono": "+57 300 123 4567"
    }

    lead = LeadCreateSchema(**valid_data)
    assert lead.email == "test@example.com"
    assert lead.nombre == "Juan Pérez"
    assert lead.telefono == "+57 300 123 4567"

    # Invalid data
    with pytest.raises(ValidationError) as exc_info:
        LeadCreateSchema(
            email="invalid-email",
            nombre="",
            tipo_negocio="invalid_type"
        )

    errors = exc_info.value.errors()
    error_fields = [err['loc'][-1] for err in errors]
    assert 'email' in error_fields
    assert 'nombre' in error_fields
    assert 'tipo_negocio' in error_fields

def test_model_serialization():
    """Test that models serialize correctly after migration"""

    lead_data = {
        "email": "test@example.com",
        "nombre": "Juan Pérez",
        "tipo_negocio": "vendedor"
    }

    lead = LeadCreateSchema(**lead_data)

    # Test model_dump
    serialized = lead.model_dump()
    assert isinstance(serialized, dict)
    assert serialized["email"] == "test@example.com"

    # Test JSON serialization
    json_str = lead.model_dump_json()
    assert isinstance(json_str, str)
    assert "test@example.com" in json_str
```

### API Integration Test

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_endpoint_after_migration():
    """Test that API endpoints work after Pydantic V2 migration"""

    # Test POST with valid data
    response = client.post("/api/v1/leads/", json={
        "email": "test@example.com",
        "nombre": "Juan Pérez",
        "tipo_negocio": "vendedor",
        "telefono": "+57 300 123 4567"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"

    # Test validation errors
    response = client.post("/api/v1/leads/", json={
        "email": "invalid-email",
        "nombre": ""
    })

    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data
```

## Common Migration Patterns Summary

| V1 Pattern | V2 Pattern | Notes |
|------------|------------|-------|
| `class Config:` | `model_config = ConfigDict(...)` | Main configuration migration |
| `@validator('field')` | `@field_validator('field') @classmethod` | Single field validation |
| `@validator('field') with values` | `@model_validator(mode='after')` | Multi-field validation |
| `schema_extra` | `json_schema_extra` | Schema examples |
| `allow_population_by_field_name` | `populate_by_name` | Field population |
| `json_encoders` | `json_encoders` (same) | Custom JSON encoding |

## File-by-File Migration Status

| File | Status | Priority | Complexity | Notes |
|------|--------|----------|------------|-------|
| user.py | ✅ Done | High | Low | Already V2 |
| leads.py | 🔄 Pending | Medium | Medium | 4 validators |
| category.py | 🔄 Pending | Medium | Medium | Complex validation |
| payout_request.py | 🔄 Pending | High | Medium | Financial validation |
| common.py | 🔄 Pending | Low | Low | Generic schemas |
| product.py | 🔄 Pending | High | High | Core business logic |
| vendor_profile.py | 🔄 Pending | Medium | High | Complex validators |
| transaction.py | 🔄 Pending | High | Medium | Financial data |

This comprehensive example set provides real migration patterns for all the major schema files in MeStore, making it easy to understand and apply the V2 migration across the entire codebase.