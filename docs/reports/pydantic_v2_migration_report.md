
# Pydantic V2 Compatibility Analysis Report
# MeStore Backend Schema Migration Requirements

## 🚨 CRITICAL FINDINGS


### 1. DEPRECATED `class Config` PATTERN (48 occurrences)

**Issue**: Using Pydantic V1 `class Config` instead of V2 `model_config = ConfigDict()`

**Files affected**:

**app/schemas/leads.py**:
  - Line 35: class Config:
  - Line 58: class Config:

**app/schemas/payout_history.py**:
  - Line 25: class Config:
  - Line 35: class Config:

**app/schemas/payout_request.py**:
  - Line 20: class Config:
  - Line 28: class Config:

**app/schemas/alerts.py**:
  - Line 27: class Config:
  - Line 42: class Config:
  - Line 56: class Config:
  - Line 71: class Config:
  - Line 87: class Config:

**app/schemas/common.py**:
  - Line 108: class Config:
  - Line 133: class Config:
  - Line 159: class Config:
  - Line 196: class Config:
  - Line 211: class Config:

**app/schemas/category.py**:
  - Line 155: class Config:
  - Line 173: class Config:
  - Line 276: class Config:

**app/schemas/admin.py**:
  - Line 16: class Config:
  - Line 38: class Config:

**app/schemas/product_verification.py**:
  - Line 64: class Config:
  - Line 103: class Config:
  - Line 128: class Config:
  - Line 156: class Config:
  - Line 193: class Config:
  - Line 215: class Config:
  - Line 271: class Config:
  - Line 321: class Config:
  - Line 341: class Config:

**app/schemas/vendor_document.py**:
  - Line 54: class Config:
  - Line 68: class Config:
  - Line 79: class Config:

**app/schemas/system_config.py**:
  - Line 67: class Config:
  - Line 92: class Config:
  - Line 107: class Config:

**app/schemas/product.py**:
  - Line 111: class Config(ProductConfig):
  - Line 291: class Config(ProductConfig):
  - Line 349: class Config(ProductConfig):
  - Line 530: class Config(ProductConfig):
  - Line 589: class Config(ProductConfig):

**app/schemas/inventory_audit.py**:
  - Line 60: class Config:
  - Line 75: class Config:
  - Line 138: class Config:
  - Line 182: class Config:

**app/schemas/vendor_profile.py**:
  - Line 130: class Config:
  - Line 225: class Config:

**app/schemas/transaction.py**:
  - Line 175: class Config:

### 2. DEPRECATED `@validator` DECORATOR (18 occurrences)

**Issue**: Using Pydantic V1 `@validator` instead of V2 `@field_validator`

**Files affected**:

**app/schemas/leads.py**:
  - Line 13: @validator('telefono')
  - Line 23: @validator('nombre')
  - Line 29: @validator('empresa')

**app/schemas/payout_request.py**:
  - Line 31: @validator('numero_cuenta')
  - Line 38: @validator('banco')
  - Line 45: @validator('monto_solicitado')

**app/schemas/category.py**:
  - Line 236: @validator('categories')
  - Line 259: @validator('primary_category_id')

**app/schemas/vendor_document.py**:
  - Line 19: @validator('file_size')
  - Line 26: @validator('mime_type')
  - Line 87: @validator('status')
  - Line 93: @validator('verification_notes')

**app/schemas/system_config.py**:
  - Line 36: @validator('value')
  - Line 76: @validator('settings')

**app/schemas/vendor_profile.py**:
  - Line 82: @validator('business_hours')
  - Line 99: @validator('social_media_links')
  - Line 159: @validator('account_number')
  - Line 174: @validator('tipo_cuenta')

### 3. MISSING ConfigDict IMPORTS (13 files)

**Issue**: Files using `class Config` but missing `ConfigDict` import

**Files affected**:

**app/schemas/leads.py**:
  Current imports: ['from pydantic import BaseModel, EmailStr, Field, validator']
  Required: Add `ConfigDict` to pydantic imports

**app/schemas/payout_history.py**:
  Current imports: ['from pydantic import BaseModel, Field']
  Required: Add `ConfigDict` to pydantic imports

**app/schemas/payout_request.py**:
  Current imports: ['from pydantic import BaseModel, Field', 'from pydantic import validator']
  Required: Add `ConfigDict` to pydantic imports

**app/schemas/alerts.py**:
  Current imports: ['from pydantic import BaseModel, Field']
  Required: Add `ConfigDict` to pydantic imports

**app/schemas/common.py**:
  Current imports: ['from pydantic import BaseModel, Field']
  Required: Add `ConfigDict` to pydantic imports

**app/schemas/category.py**:
  Current imports: ['from pydantic import BaseModel, Field, validator']
  Required: Add `ConfigDict` to pydantic imports

**app/schemas/admin.py**:
  Current imports: ['from pydantic import BaseModel, Field']
  Required: Add `ConfigDict` to pydantic imports

**app/schemas/vendor_document.py**:
  Current imports: ['from pydantic import BaseModel, validator']
  Required: Add `ConfigDict` to pydantic imports

**app/schemas/system_config.py**:
  Current imports: ['from pydantic import BaseModel, Field, validator']
  Required: Add `ConfigDict` to pydantic imports

**app/schemas/product.py**:
  Current imports: ['from pydantic import UUID4, BaseModel, Field, field_validator, model_validator']
  Required: Add `ConfigDict` to pydantic imports

**app/schemas/inventory_audit.py**:
  Current imports: ['from pydantic import BaseModel, Field, validator']
  Required: Add `ConfigDict` to pydantic imports

**app/schemas/vendor_profile.py**:
  Current imports: ['from pydantic import BaseModel, Field, HttpUrl, validator']
  Required: Add `ConfigDict` to pydantic imports

**app/schemas/transaction.py**:
  Current imports: ['from pydantic import BaseModel, Field, field_validator']
  Required: Add `ConfigDict` to pydantic imports


## 📊 MIGRATION IMPACT ASSESSMENT

**Total files requiring migration**: 14
**Critical patterns found**: 89

### High Priority Files (Most Critical):
- **app/schemas/common.py** (11 issues)
- **app/schemas/product_verification.py** (9 issues)
- **app/schemas/vendor_document.py** (8 issues)
- **app/schemas/system_config.py** (8 issues)
- **app/schemas/payout_request.py** (7 issues)
- **app/schemas/vendor_profile.py** (7 issues)
- **app/schemas/leads.py** (6 issues)
- **app/schemas/alerts.py** (6 issues)
- **app/schemas/category.py** (6 issues)
- **app/schemas/product.py** (6 issues)


## 🔧 MIGRATION REQUIREMENTS

### For `class Config` → `model_config = ConfigDict()`:

**Before (Pydantic V1)**:
```python
class MySchema(BaseModel):
    field: str

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

**After (Pydantic V2)**:
```python
from pydantic import BaseModel, ConfigDict

class MySchema(BaseModel):
    field: str

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
```

### For `@validator` → `@field_validator`:

**Before (Pydantic V1)**:
```python
from pydantic import validator

@validator('field_name')
def validate_field(cls, v):
    return v
```

**After (Pydantic V2)**:
```python
from pydantic import field_validator

@field_validator('field_name')
@classmethod
def validate_field(cls, v):
    return v
```

## ⚠️ COMPATIBILITY NOTES

1. **Breaking Changes**: These patterns WILL cause runtime errors in Pydantic V2
2. **Import Changes**: Need to update imports to include `ConfigDict` and replace `validator` with `field_validator`
3. **Decorator Changes**: All `@validator` decorators need `@classmethod` decorator added
4. **Testing Impact**: All schemas with these patterns need comprehensive testing after migration

## 🎯 RECOMMENDED MIGRATION ORDER

1. **First**: Fix import statements (add ConfigDict, replace validator with field_validator)
2. **Second**: Convert all `class Config` to `model_config = ConfigDict()`
3. **Third**: Update all `@validator` to `@field_validator` with `@classmethod`
4. **Fourth**: Run comprehensive tests to ensure functionality
5. **Fifth**: Update any custom validation logic that might be affected

## ✅ FILES ALREADY COMPLIANT

These files are already using Pydantic V2 syntax correctly:
- app/schemas/base.py ✅
- app/schemas/user.py ✅ (partially - uses model_config but has some class methods that need @classmethod)
- app/schemas/auth.py ✅
- app/schemas/inventory.py ✅
- app/schemas/order.py ✅
- app/schemas/commission.py ✅
- app/schemas/storage.py ✅
- app/schemas/search.py ✅

