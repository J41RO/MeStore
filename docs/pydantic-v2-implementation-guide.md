# Pydantic V2 Implementation Guide for MeStore

## Quick Start

### 1. Run the Migration Script

```bash
# Dry run to see what will change
python scripts/migrate_pydantic_v2.py --dry-run

# Run migration on specific file
python scripts/migrate_pydantic_v2.py --file leads.py

# Run full migration
python scripts/migrate_pydantic_v2.py
```

### 2. Validate the Migration

```bash
# Run migration tests
python -m pytest tests/migration/test_pydantic_v2_compatibility.py -v

# Run full test suite
python -m pytest tests/ -v

# Check API documentation
uvicorn app.main:app --reload
# Visit http://localhost:8000/docs
```

## Example Migrations

### Config Class Migration

#### Before (V1):
```python
class LeadCreateSchema(BaseModel):
    email: EmailStr = Field(..., description="Email corporativo del lead")
    nombre: str = Field(..., min_length=2, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "juan.perez@miempresa.com",
                "nombre": "Juan Pérez"
            }
        }
```

#### After (V2):
```python
from pydantic import ConfigDict

class LeadCreateSchema(BaseModel):
    email: EmailStr = Field(..., description="Email corporativo del lead")
    nombre: str = Field(..., min_length=2, max_length=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "juan.perez@miempresa.com",
                "nombre": "Juan Pérez"
            }
        }
    )
```

### Validator Migration

#### Before (V1):
```python
from pydantic import validator

class LeadCreateSchema(BaseModel):
    telefono: Optional[str] = Field(None, max_length=20)

    @validator('telefono')
    def validate_telefono(cls, v):
        if v and v.strip():
            import re
            if not re.match(r'^[+]?[0-9\s\-()]{7,15}$', v.strip()):
                raise ValueError('Formato de teléfono inválido')
            return v.strip()
        return None
```

#### After (V2):
```python
from pydantic import field_validator

class LeadCreateSchema(BaseModel):
    telefono: Optional[str] = Field(None, max_length=20)

    @field_validator('telefono')
    @classmethod
    def validate_telefono(cls, v):
        if v and v.strip():
            import re
            if not re.match(r'^[+]?[0-9\s\-()]{7,15}$', v.strip()):
                raise ValueError('Formato de teléfono inválido')
            return v.strip()
        return None
```

### Complex Validator with Values Parameter

#### Before (V1):
```python
@validator('primary_category_id')
def validate_primary_category(cls, v, values):
    if v is not None and 'category_ids' in values:
        if v not in values['category_ids']:
            raise ValueError("La categoría principal debe estar en la lista")
    return v
```

#### After (V2):
```python
from pydantic import model_validator

@model_validator(mode='after')
def validate_primary_category(self):
    if self.primary_category_id is not None:
        if self.primary_category_id not in self.category_ids:
            raise ValueError("La categoría principal debe estar en la lista")
    return self
```

## Common Migration Patterns

### 1. Standard Config Migration

```python
# V1 → V2 Config patterns
{
    # Basic config
    "class Config:\n    from_attributes = True":
    "model_config = ConfigDict(from_attributes=True)",

    # With JSON encoders
    "class Config:\n    from_attributes = True\n    json_encoders = {...}":
    "model_config = ConfigDict(from_attributes=True, json_encoders={...})",

    # With schema extra
    "class Config:\n    json_schema_extra = {...}":
    "model_config = ConfigDict(json_schema_extra={...})"
}
```

### 2. Import Updates

```python
# Add these imports when needed
from pydantic import ConfigDict, field_validator, model_validator

# Keep existing imports
from pydantic import BaseModel, Field, EmailStr
```

### 3. Validator Method Signatures

```python
# V1 signatures
@validator('field')
def validate_field(cls, v): ...

@validator('field')
def validate_field(cls, v, values): ...

# V2 signatures
@field_validator('field')
@classmethod
def validate_field(cls, v): ...

@model_validator(mode='after')
def validate_model(self): ...
```

## File-by-File Migration Checklist

### High Priority Files (Core Business Logic)

#### ✅ user.py
- **Status**: Already migrated to V2
- **Uses**: `field_validator`, `ConfigDict`
- **Action**: ✅ No changes needed

#### 🔄 product.py
- **Current**: V1 Config classes
- **Required**: Migrate Config → model_config
- **Complexity**: Medium (multiple schemas)

#### 🔄 transaction.py
- **Current**: V1 Config classes
- **Required**: Migrate Config → model_config
- **Complexity**: Low

### Medium Priority Files

#### 🔄 category.py
- **Current**: V1 Config classes + 2 validators
- **Required**: Migrate Config + validators
- **Complexity**: Medium

#### 🔄 vendor_profile.py
- **Current**: V1 Config classes + 3 validators
- **Required**: Migrate Config + validators
- **Complexity**: High (complex validation logic)

#### 🔄 alerts.py
- **Current**: V1 Config classes
- **Required**: Migrate Config → model_config
- **Complexity**: Low

### Low Priority Files

#### 🔄 leads.py
- **Current**: V1 Config classes + 4 validators
- **Required**: Migrate Config + validators
- **Complexity**: Medium

#### 🔄 payout_request.py
- **Current**: V1 Config classes + 4 validators
- **Required**: Migrate Config + validators
- **Complexity**: Medium

#### 🔄 common.py
- **Current**: V1 Config classes
- **Required**: Migrate Config → model_config
- **Complexity**: Low

## Manual Review Required

### Files with Complex Validators

1. **vendor_profile.py**
   - Complex business logic validation
   - Multi-field dependencies
   - May need model_validator

2. **category.py**
   - Hierarchy validation
   - Cross-field dependencies

3. **payout_request.py**
   - Financial validation rules
   - Colombian banking specifics

### Validation Patterns Requiring model_validator

```python
# When validation depends on multiple fields
@model_validator(mode='after')
def validate_dates(self):
    if self.end_date and self.start_date:
        if self.end_date <= self.start_date:
            raise ValueError('End date must be after start date')
    return self

# When validation needs access to all field values
@model_validator(mode='after')
def validate_business_rules(self):
    if self.type == 'premium' and not self.subscription_id:
        raise ValueError('Premium accounts require subscription')
    return self
```

## Testing Strategy

### 1. Unit Tests

```bash
# Test specific schema
python -m pytest tests/migration/test_pydantic_v2_compatibility.py::TestValidatorMigration::test_phone_validator -v

# Test all schemas
python -m pytest tests/migration/ -v
```

### 2. Integration Tests

```bash
# Test API endpoints
python -m pytest tests/api/ -v

# Test database integration
python -m pytest tests/integration/ -v
```

### 3. Performance Tests

```bash
# Run performance benchmarks
python -m pytest tests/migration/test_pydantic_v2_compatibility.py::TestPerformanceRegression -v
```

## Rollback Procedures

### Quick Rollback

```bash
# Restore from backup
rm -rf app/schemas
cp -r app/schemas.backup app/schemas
git add app/schemas/
git commit -m "rollback: revert pydantic v2 migration"
```

### Selective Rollback

```bash
# Rollback specific file
git checkout HEAD~1 -- app/schemas/problematic_file.py
git add app/schemas/problematic_file.py
git commit -m "rollback: revert migration for problematic_file.py"
```

### Verify Rollback

```bash
# Ensure system works after rollback
python -m pytest tests/ -x
uvicorn app.main:app --reload &
curl http://localhost:8000/health
```

## Performance Optimization

### Enable V2 Performance Features

```python
model_config = ConfigDict(
    # Performance optimizations
    str_strip_whitespace=True,     # Auto-strip strings
    validate_assignment=True,       # Validate on assignment
    use_enum_values=True,          # Use enum values directly
    frozen=True,                   # Immutable models (for read-only)

    # Validation modes
    validate_default=True,         # Validate default values
    arbitrary_types_allowed=False, # Strict type checking

    # Serialization
    ser_json_bytes=False,         # JSON serialization format
    hide_input_in_errors=True,    # Security: hide sensitive input
)
```

### Field-Level Optimizations

```python
# Use computed fields for expensive operations
from pydantic import computed_field

@computed_field
@property
def full_name(self) -> str:
    return f"{self.nombre} {self.apellido}"

# Use field serializers for custom output
from pydantic import field_serializer

@field_serializer('created_at')
def serialize_dt(self, dt: datetime) -> str:
    return dt.isoformat()
```

## Common Issues and Solutions

### Issue 1: Validator Values Parameter

**Problem**: `@validator` using `values` parameter
```python
@validator('field')
def validate_field(cls, v, values):  # ❌ Won't work in V2
```

**Solution**: Use `model_validator`
```python
@model_validator(mode='after')
def validate_field(self):  # ✅ V2 approach
    # Access self.field_name instead of values['field_name']
```

### Issue 2: Config Class Not Migrated

**Problem**: Still using `class Config:`
```python
class Config:  # ❌ V1 syntax
    from_attributes = True
```

**Solution**: Use `model_config`
```python
model_config = ConfigDict(  # ✅ V2 syntax
    from_attributes=True
)
```

### Issue 3: Import Errors

**Problem**: Missing V2 imports
```python
from pydantic import validator  # ❌ V1 import
```

**Solution**: Update imports
```python
from pydantic import field_validator, ConfigDict  # ✅ V2 imports
```

### Issue 4: JSON Schema Generation

**Problem**: Schema examples not showing
```python
class Config:
    schema_extra = {...}  # ❌ Deprecated
```

**Solution**: Use `json_schema_extra`
```python
model_config = ConfigDict(
    json_schema_extra={...}  # ✅ V2 approach
)
```

## Best Practices Going Forward

### 1. Always Use V2 Syntax for New Schemas

```python
from pydantic import BaseModel, ConfigDict, Field, field_validator

class NewSchema(BaseModel):
    field: str = Field(..., description="Description")

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True
    )

    @field_validator('field')
    @classmethod
    def validate_field(cls, v):
        return v.strip()
```

### 2. Use Type Hints Consistently

```python
from typing import Optional, List
from datetime import datetime

class MySchema(BaseModel):
    id: UUID
    name: str
    tags: List[str]
    created_at: datetime
    metadata: Optional[dict] = None
```

### 3. Leverage V2 Features

```python
# Use computed fields
@computed_field
@property
def display_name(self) -> str:
    return f"{self.nombre} {self.apellido}"

# Use field serializers
@field_serializer('price')
def serialize_price(self, value: Decimal) -> float:
    return float(value)

# Use model validators for complex logic
@model_validator(mode='after')
def validate_business_rules(self):
    # Complex validation logic
    return self
```

### 4. Document Complex Validators

```python
@field_validator('telefono')
@classmethod
def validate_telefono(cls, v: Optional[str]) -> Optional[str]:
    """
    Validate Colombian phone number format.

    Accepts:
    - +57 300 123 4567
    - 3001234567
    - +573001234567

    Returns normalized format: +57 3001234567
    """
    if not v:
        return None
    # Validation logic...
```

## Monitoring and Maintenance

### 1. Set Up Monitoring

```python
# Add logging to critical validators
import logging

@field_validator('critical_field')
@classmethod
def validate_critical_field(cls, v):
    try:
        # Validation logic
        return validated_value
    except Exception as e:
        logging.error(f"Validation failed for critical_field: {e}")
        raise
```

### 2. Regular Performance Checks

```bash
# Run performance tests monthly
python -m pytest tests/migration/test_pydantic_v2_compatibility.py::TestPerformanceRegression

# Monitor API response times
# Add to monitoring dashboard
```

### 3. Keep Dependencies Updated

```bash
# Check for Pydantic updates
pip list --outdated | grep pydantic

# Update safely
pip install pydantic>=2.11.7,<3.0.0
```

This implementation guide provides everything needed to successfully migrate MeStore to Pydantic V2 while maintaining system stability and performance.