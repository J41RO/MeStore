# MeStore Pydantic V2 Migration Strategy

## Executive Summary

This document provides a comprehensive migration strategy for upgrading MeStore's Pydantic schemas from V1 to V2 syntax. The migration addresses breaking changes in Pydantic V2 while maintaining backward compatibility and following MeStore's coding standards.

## Current State Analysis

### Pydantic Usage Assessment
- **Total Schema Files**: 20+ files in `/app/schemas/`
- **Config Classes Found**: 14 files with V1 `Config` classes
- **Validator Decorators**: 18 instances of `@validator` decorator
- **Current Version**: Pydantic 2.11.7 (already V2, but using V1 syntax)
- **Mixed Patterns**: Some files already use V2 syntax (e.g., `user.py`), others use V1

### Key Migration Areas
1. **Config Class → model_config**: 14 files need migration
2. **@validator → @field_validator**: 6 files with 18 validator instances
3. **JSON Schema Generation**: Schema examples need updates
4. **FastAPI Integration**: Ensure compatibility with FastAPI dependencies

## 1. Step-by-Step Migration Plan

### Phase 1: Preparation (1-2 hours)
1. **Create Migration Branch**
   ```bash
   git checkout -b feature/pydantic-v2-migration
   ```

2. **Backup Current State**
   ```bash
   cp -r app/schemas app/schemas.backup
   ```

3. **Create Migration Test Suite**
   ```bash
   mkdir tests/migration
   touch tests/migration/test_pydantic_v2_compatibility.py
   ```

### Phase 2: Config Class Migration (2-3 hours)

#### Files Requiring Config → model_config Migration:
- `leads.py`
- `payout_history.py`
- `payout_request.py`
- `alerts.py`
- `common.py`
- `category.py`
- `admin.py`
- `product_verification.py`
- `vendor_document.py`
- `system_config.py`
- `product.py`
- `inventory_audit.py`
- `vendor_profile.py`
- `transaction.py`

#### Migration Pattern:
```python
# BEFORE (V1 Syntax)
class MyModel(BaseModel):
    field: str

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}
        use_enum_values = True
        json_schema_extra = {"example": {...}}

# AFTER (V2 Syntax)
from pydantic import ConfigDict

class MyModel(BaseModel):
    field: str

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat()},
        use_enum_values=True,
        json_schema_extra={"example": {...}}
    )
```

### Phase 3: Validator Migration (2-3 hours)

#### Files Requiring @validator → @field_validator Migration:
- `leads.py` (4 validators)
- `payout_request.py` (4 validators)
- `category.py` (2 validators)
- `vendor_document.py` (3 validators)
- `system_config.py` (2 validators)
- `vendor_profile.py` (3 validators)

#### Migration Pattern:
```python
# BEFORE (V1 Syntax)
from pydantic import validator

class MyModel(BaseModel):
    phone: str

    @validator('phone')
    def validate_phone(cls, v):
        if not v.isdigit():
            raise ValueError('Phone must be numeric')
        return v

# AFTER (V2 Syntax)
from pydantic import field_validator

class MyModel(BaseModel):
    phone: str

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not v.isdigit():
            raise ValueError('Phone must be numeric')
        return v
```

### Phase 4: Import Updates (30 minutes)
Update imports across all schema files:
```python
# Add V2 imports
from pydantic import ConfigDict, field_validator
# Remove V1 imports if no longer needed
# from pydantic import validator (remove if fully migrated)
```

## 2. Code Refactoring Strategy

### A. Minimize Breaking Changes

#### Backward Compatibility Approach:
- Migrate files incrementally
- Test each file after migration
- Use feature flags for critical paths
- Maintain API contract compatibility

#### Critical Files Priority:
1. **High Priority**: `user.py`, `product.py`, `transaction.py` (core business models)
2. **Medium Priority**: `category.py`, `vendor_profile.py`, `alerts.py`
3. **Low Priority**: `system_config.py`, `admin.py`, `storage.py`

### B. FastAPI Integration Compatibility

#### Ensure Compatibility With:
```python
# FastAPI dependency injection
from fastapi import Depends
from app.schemas.user import UserCreate, UserRead

@app.post("/users/", response_model=UserRead)
async def create_user(user: UserCreate):
    # Should work without changes
    pass
```

#### Test OpenAPI Schema Generation:
```python
# Verify OpenAPI docs still generate correctly
@app.get("/docs")  # Should work post-migration
```

### C. Error Handling Migration

#### V1 to V2 Error Pattern:
```python
# V2 validation errors have different structure
try:
    user = UserCreate(**data)
except ValidationError as e:
    # e.errors() format may differ slightly
    errors = [{"field": err["loc"][-1], "message": err["msg"]} for err in e.errors()]
```

## 3. Testing Approach

### A. Migration Test Suite

Create comprehensive test file:
```python
# tests/migration/test_pydantic_v2_compatibility.py
import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreate, UserRead
from app.schemas.product import ProductCreate
from app.schemas.category import CategoryCreate

class TestPydanticV2Migration:
    def test_model_creation_works(self):
        """Test that model creation works with V2 syntax"""
        user_data = {
            "email": "test@example.com",
            "nombre": "Test",
            "apellido": "User",
            "password": "TestPass123"
        }
        user = UserCreate(**user_data)
        assert user.email == "test@example.com"

    def test_validation_errors_format(self):
        """Test that validation errors maintain expected format"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="invalid-email")

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert 'loc' in errors[0]
        assert 'msg' in errors[0]

    def test_fastapi_response_model_compatibility(self):
        """Test FastAPI response model serialization"""
        # Mock database user object
        user_dict = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "test@example.com",
            "nombre": "Test",
            "apellido": "User",
            "user_type": "buyer",
            "is_active": True,
            "created_at": "2025-01-15T10:30:00Z"
        }

        user_response = UserRead(**user_dict)
        json_data = user_response.model_dump()
        assert json_data["email"] == "test@example.com"

    def test_json_schema_generation(self):
        """Test that JSON schemas generate correctly"""
        schema = UserCreate.model_json_schema()
        assert "properties" in schema
        assert "email" in schema["properties"]
```

### B. Integration Tests

#### Database Model Compatibility:
```python
def test_sqlalchemy_integration():
    """Test that Pydantic models work with SQLAlchemy"""
    # Test from_attributes=True functionality
    user_orm = User(email="test@example.com", nombre="Test")
    user_schema = UserRead.model_validate(user_orm)
    assert user_schema.email == "test@example.com"
```

#### API Endpoint Tests:
```python
def test_api_endpoints_work():
    """Test that API endpoints work post-migration"""
    response = client.post("/api/v1/users/", json={
        "email": "test@example.com",
        "nombre": "Test",
        "apellido": "User",
        "password": "TestPass123"
    })
    assert response.status_code == 201
```

### C. Performance Tests

#### Schema Validation Performance:
```python
import time
import pytest

def test_validation_performance():
    """Ensure V2 migration doesn't degrade performance"""
    data = {
        "email": "test@example.com",
        "nombre": "Test",
        "apellido": "User",
        "password": "TestPass123"
    }

    start_time = time.time()
    for _ in range(1000):
        UserCreate(**data)
    end_time = time.time()

    # Should complete 1000 validations in under 1 second
    assert (end_time - start_time) < 1.0
```

## 4. Risk Assessment & Rollback Procedures

### A. Risk Matrix

| Risk Category | Probability | Impact | Mitigation |
|---------------|-------------|--------|------------|
| Breaking API Responses | Low | High | Comprehensive testing, staged rollout |
| Validation Behavior Changes | Medium | Medium | Validator compatibility tests |
| Performance Degradation | Low | Medium | Performance benchmarks |
| FastAPI Integration Issues | Low | High | Integration test suite |
| Database ORM Compatibility | Low | High | SQLAlchemy integration tests |

### B. Rollback Strategy

#### Immediate Rollback (< 5 minutes):
```bash
# If critical issues are discovered
git checkout main
git cherry-pick <critical-fix-commit>
# Deploy immediately
```

#### Partial Rollback (Schema-specific):
```bash
# Rollback specific schema file
git checkout main -- app/schemas/problematic_file.py
git commit -m "hotfix: rollback problematic schema migration"
```

#### Full Migration Rollback:
```bash
# Restore entire schemas directory
rm -rf app/schemas
cp -r app/schemas.backup app/schemas
git add app/schemas/
git commit -m "rollback: revert pydantic v2 migration"
```

### C. Monitoring & Validation

#### Post-Migration Monitoring:
- API response time monitoring
- Error rate tracking
- Validation error analysis
- Database query performance

#### Validation Checklist:
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] API documentation generates correctly
- [ ] No performance regression
- [ ] All validator functions work as expected
- [ ] FastAPI response models serialize correctly

## 5. Best Practices for Pydantic V2 Compatibility

### A. Code Organization

#### Schema File Structure:
```python
# Standard V2 schema file structure
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, EmailStr

class MyModel(BaseModel):
    # Fields with proper typing
    id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    created_at: datetime

    # V2 configuration
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        json_schema_extra={"example": {...}}
    )

    # V2 field validators
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip().title()
```

### B. Migration Patterns

#### Complex Validator Migration:
```python
# V1 Multi-field validator
@validator('end_date')
def validate_end_date(cls, v, values):
    if 'start_date' in values and v <= values['start_date']:
        raise ValueError('End date must be after start date')
    return v

# V2 Model validator
from pydantic import model_validator

@model_validator(mode='after')
def validate_dates(self):
    if self.end_date <= self.start_date:
        raise ValueError('End date must be after start date')
    return self
```

#### Custom JSON Encoders:
```python
# V2 approach for custom serialization
from pydantic import field_serializer

class MyModel(BaseModel):
    created_at: datetime

    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()
```

### C. Performance Optimization

#### V2 Performance Features:
```python
model_config = ConfigDict(
    # Enable performance optimizations
    str_strip_whitespace=True,     # Auto-strip strings
    validate_assignment=True,       # Validate on assignment
    use_enum_values=True,          # Use enum values directly
    frozen=True,                   # Immutable models for read-only data
)
```

### D. Error Handling Best Practices

#### Consistent Error Response Format:
```python
from pydantic import ValidationError
from app.schemas.common import APIValidationError, ValidationError as APIValidationErrorItem

def handle_validation_error(exc: ValidationError) -> APIValidationError:
    """Convert Pydantic ValidationError to API format"""
    validation_errors = [
        APIValidationErrorItem(
            field=".".join(str(x) for x in error["loc"]),
            message=error["msg"],
            value=error.get("input"),
            constraint=error.get("type")
        )
        for error in exc.errors()
    ]

    return APIValidationError(
        message="Validation failed",
        validation_errors=validation_errors
    )
```

### E. FastAPI Integration Best Practices

#### Response Model Configuration:
```python
from fastapi import APIRouter
from app.schemas.user import UserRead, UserCreate

router = APIRouter()

@router.post("/users/", response_model=UserRead)
async def create_user(user: UserCreate):
    # V2 models work seamlessly with FastAPI
    return UserRead.model_validate(created_user)
```

#### Dependency Injection:
```python
from fastapi import Depends
from app.schemas.common import PaginationMeta

async def get_pagination(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
) -> PaginationMeta:
    return PaginationMeta(page=page, size=size)
```

## 6. Implementation Timeline

### Week 1: Preparation & High-Priority Files
- Day 1-2: Setup migration environment, create test suite
- Day 3-5: Migrate core schemas (`user.py`, `product.py`, `transaction.py`)

### Week 2: Medium-Priority Files & Testing
- Day 1-3: Migrate remaining schema files
- Day 4-5: Comprehensive testing and integration validation

### Week 3: Deployment & Monitoring
- Day 1-2: Staging environment deployment and testing
- Day 3: Production deployment with monitoring
- Day 4-5: Performance monitoring and optimization

## 7. Success Criteria

### Technical Metrics:
- [ ] 100% test coverage maintained
- [ ] Zero breaking changes to API contracts
- [ ] Performance within 5% of baseline
- [ ] All Pydantic V2 features properly utilized

### Business Metrics:
- [ ] No user-facing disruption
- [ ] API documentation remains accurate
- [ ] Development velocity maintained
- [ ] Code maintainability improved

## Conclusion

This migration strategy provides a systematic approach to upgrading MeStore's Pydantic schemas to V2 while maintaining system stability and performance. The phased approach minimizes risk while ensuring comprehensive coverage of all migration aspects.

The strategy prioritizes backward compatibility and includes robust testing and rollback procedures to ensure a smooth transition. Following this plan will result in a more maintainable, performant, and future-proof codebase aligned with Pydantic V2 best practices.