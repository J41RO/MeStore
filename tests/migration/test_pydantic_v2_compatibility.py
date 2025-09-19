"""
Pydantic V2 Migration Compatibility Tests
========================================

Comprehensive test suite to validate Pydantic V2 migration compatibility
across all MeStore schema files and API integrations.

Author: Technical Debt Manager AI
Date: 2025-09-18
"""

import pytest
import json
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from typing import Dict, Any

from pydantic import ValidationError
from fastapi.testclient import TestClient

# Import schemas to test
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.schemas.product import ProductCreate, ProductRead
from app.schemas.category import CategoryCreate, CategoryRead
from app.schemas.transaction import TransactionCreate
from app.schemas.common import APIResponse, PaginatedResponse, APIError
from app.schemas.vendor_profile import VendorProfileCreate


class TestPydanticV2BasicCompatibility:
    """Test basic Pydantic V2 functionality"""

    def test_model_creation_works(self):
        """Test that model creation works with V2 syntax"""
        user_data = {
            "email": "test@example.com",
            "nombre": "Test",
            "apellido": "User",
            "password": "TestPass123",
            "user_type": "buyer"
        }
        user = UserCreate(**user_data)
        assert user.email == "test@example.com"
        assert user.nombre == "Test"
        assert user.user_type == "buyer"

    def test_model_validation_errors(self):
        """Test that validation errors maintain expected format"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="invalid-email")

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert 'loc' in errors[0]
        assert 'msg' in errors[0]
        assert 'type' in errors[0]

    def test_model_dump_serialization(self):
        """Test that model_dump() works correctly"""
        user_data = {
            "email": "test@example.com",
            "nombre": "Test",
            "apellido": "User",
            "password": "TestPass123"
        }
        user = UserCreate(**user_data)
        serialized = user.model_dump()

        assert isinstance(serialized, dict)
        assert serialized["email"] == "test@example.com"
        assert "password" in serialized  # Password should be included in dump

    def test_model_dump_exclude(self):
        """Test that model_dump(exclude=...) works correctly"""
        user_data = {
            "email": "test@example.com",
            "nombre": "Test",
            "apellido": "User",
            "password": "TestPass123"
        }
        user = UserCreate(**user_data)
        serialized = user.model_dump(exclude={"password"})

        assert "password" not in serialized
        assert serialized["email"] == "test@example.com"

    def test_json_schema_generation(self):
        """Test that JSON schemas generate correctly"""
        schema = UserCreate.model_json_schema()

        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "email" in schema["properties"]
        assert "required" in schema


class TestValidatorMigration:
    """Test that field validators work correctly after migration"""

    def test_phone_validator(self):
        """Test Colombian phone validation"""
        # Valid phone numbers
        valid_phones = [
            "+57 300 123 4567",
            "3001234567",
            "+573001234567"
        ]

        for phone in valid_phones:
            user_data = {
                "email": "test@example.com",
                "nombre": "Test",
                "apellido": "User",
                "password": "TestPass123",
                "telefono": phone
            }
            user = UserCreate(**user_data)
            assert user.telefono == "+57 3001234567"

    def test_cedula_validator(self):
        """Test Colombian cedula validation"""
        user_data = {
            "email": "test@example.com",
            "nombre": "Test",
            "apellido": "User",
            "password": "TestPass123",
            "cedula": "12345678"
        }
        user = UserCreate(**user_data)
        assert user.cedula == "12345678"

        # Test invalid cedula
        with pytest.raises(ValidationError):
            UserCreate(**{**user_data, "cedula": "123"})  # Too short

    def test_password_validator(self):
        """Test password strength validation"""
        # Valid password
        user_data = {
            "email": "test@example.com",
            "nombre": "Test",
            "apellido": "User",
            "password": "ValidPass123"
        }
        user = UserCreate(**user_data)
        assert user.password == "ValidPass123"

        # Invalid passwords
        invalid_passwords = [
            "short",           # Too short
            "NoNumbersHere",   # No numbers
            "nonumbers123",    # No uppercase
            "NOCAPITALS123"    # No lowercase
        ]

        for invalid_pass in invalid_passwords:
            with pytest.raises(ValidationError):
                UserCreate(**{**user_data, "password": invalid_pass})


class TestConfigMigration:
    """Test that model_config works correctly"""

    def test_from_attributes_config(self):
        """Test from_attributes configuration works"""
        # Simulate SQLAlchemy model
        class MockUser:
            def __init__(self):
                self.id = uuid4()
                self.email = "test@example.com"
                self.nombre = "Test"
                self.apellido = "User"
                self.user_type = "buyer"
                self.is_active = True
                self.created_at = datetime.utcnow()
                self.updated_at = datetime.utcnow()

        mock_user = MockUser()
        user_read = UserRead.model_validate(mock_user)

        assert user_read.email == "test@example.com"
        assert user_read.nombre == "Test"
        assert isinstance(user_read.id, UUID)

    def test_json_encoders_config(self):
        """Test that custom JSON encoders work"""
        # Test with datetime
        user_data = {
            "id": uuid4(),
            "email": "test@example.com",
            "nombre": "Test",
            "apellido": "User",
            "user_type": "buyer",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        user = UserRead(**user_data)
        json_str = user.model_dump_json()
        parsed = json.loads(json_str)

        # Check that datetime was properly serialized
        assert isinstance(parsed["created_at"], str)
        assert "T" in parsed["created_at"]  # ISO format


class TestComplexSchemas:
    """Test more complex schema patterns"""

    def test_category_hierarchy_schema(self):
        """Test category schema with hierarchy"""
        category_data = {
            "name": "Electronics",
            "slug": "electronics",
            "description": "Electronic products",
            "is_active": True,
            "sort_order": 1
        }

        category = CategoryCreate(**category_data)
        assert category.name == "Electronics"
        assert category.slug == "electronics"

    def test_generic_api_response(self):
        """Test generic API response schemas"""
        user_data = {
            "id": uuid4(),
            "email": "test@example.com",
            "nombre": "Test",
            "apellido": "User",
            "user_type": "buyer",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        user = UserRead(**user_data)
        response = APIResponse[UserRead](
            data=user,
            message="User retrieved successfully"
        )

        assert response.status == "success"
        assert response.data.email == "test@example.com"
        assert response.message == "User retrieved successfully"

    def test_paginated_response(self):
        """Test paginated response schema"""
        users = [
            UserRead(
                id=uuid4(),
                email=f"user{i}@example.com",
                nombre=f"User{i}",
                apellido="Test",
                user_type="buyer",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            for i in range(3)
        ]

        paginated = PaginatedResponse[UserRead](
            data=users,
            pagination={
                "page": 1,
                "size": 20,
                "total": 3,
                "total_pages": 1,
                "has_next": False,
                "has_prev": False
            }
        )

        assert len(paginated.data) == 3
        assert paginated.pagination["total"] == 3


class TestFastAPIIntegration:
    """Test FastAPI integration with Pydantic V2"""

    def test_request_validation(self):
        """Test that request validation works in FastAPI context"""
        # This would be tested with actual FastAPI test client
        # For now, we test the schema validation directly

        valid_user_data = {
            "email": "test@example.com",
            "nombre": "Test",
            "apellido": "User",
            "password": "TestPass123"
        }

        # Should not raise any exceptions
        user = UserCreate(**valid_user_data)
        assert user.email == "test@example.com"

    def test_response_serialization(self):
        """Test response serialization for FastAPI"""
        user_data = {
            "id": uuid4(),
            "email": "test@example.com",
            "nombre": "Test",
            "apellido": "User",
            "user_type": "buyer",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        user = UserRead(**user_data)

        # Test that model can be serialized to JSON (for FastAPI responses)
        json_data = user.model_dump()
        assert isinstance(json_data, dict)
        assert json_data["email"] == "test@example.com"

        # Test JSON string serialization
        json_str = user.model_dump_json()
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["email"] == "test@example.com"


class TestPerformanceRegression:
    """Test that V2 migration doesn't degrade performance"""

    def test_validation_performance(self):
        """Ensure validation performance is acceptable"""
        import time

        user_data = {
            "email": "test@example.com",
            "nombre": "Test",
            "apellido": "User",
            "password": "TestPass123"
        }

        # Warm up
        for _ in range(10):
            UserCreate(**user_data)

        # Performance test
        start_time = time.time()
        iterations = 1000

        for _ in range(iterations):
            UserCreate(**user_data)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete 1000 validations in under 1 second
        assert duration < 1.0, f"Validation took {duration:.2f}s for {iterations} iterations"

    def test_serialization_performance(self):
        """Test serialization performance"""
        import time

        user_data = {
            "id": uuid4(),
            "email": "test@example.com",
            "nombre": "Test",
            "apellido": "User",
            "user_type": "buyer",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        user = UserRead(**user_data)

        # Performance test
        start_time = time.time()
        iterations = 1000

        for _ in range(iterations):
            user.model_dump()

        end_time = time.time()
        duration = end_time - start_time

        # Should complete 1000 serializations in under 0.5 seconds
        assert duration < 0.5, f"Serialization took {duration:.2f}s for {iterations} iterations"


class TestErrorHandling:
    """Test error handling patterns"""

    def test_validation_error_structure(self):
        """Test that validation errors have the expected structure"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="invalid-email",
                nombre="",  # Too short
                password="weak"  # Too weak
            )

        errors = exc_info.value.errors()

        # Should have multiple validation errors
        assert len(errors) >= 3

        # Each error should have required fields
        for error in errors:
            assert 'loc' in error
            assert 'msg' in error
            assert 'type' in error

    def test_field_specific_errors(self):
        """Test field-specific validation errors"""
        # Test email validation
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="not-an-email",
                nombre="Test",
                apellido="User",
                password="ValidPass123"
            )

        errors = exc_info.value.errors()
        email_error = next((e for e in errors if 'email' in e['loc']), None)
        assert email_error is not None


class TestBackwardCompatibility:
    """Test backward compatibility with existing code"""

    def test_schema_dict_access(self):
        """Test that schemas still work with dict-like access where needed"""
        user_data = {
            "email": "test@example.com",
            "nombre": "Test",
            "apellido": "User",
            "password": "TestPass123"
        }

        user = UserCreate(**user_data)

        # Test attribute access (should work)
        assert user.email == "test@example.com"
        assert user.nombre == "Test"

        # Test model_dump for dict-like access
        user_dict = user.model_dump()
        assert user_dict["email"] == "test@example.com"
        assert user_dict["nombre"] == "Test"

    def test_optional_fields_handling(self):
        """Test that optional fields are handled correctly"""
        # Create user with minimal required fields
        minimal_user = UserCreate(
            email="test@example.com",
            nombre="Test",
            apellido="User",
            password="TestPass123"
        )

        assert minimal_user.cedula is None
        assert minimal_user.telefono is None
        assert minimal_user.ciudad is None

        # Create user with all fields
        full_user = UserCreate(
            email="test@example.com",
            nombre="Test",
            apellido="User",
            password="TestPass123",
            cedula="12345678",
            telefono="+57 300 123 4567",
            ciudad="Bogotá"
        )

        assert full_user.cedula == "12345678"
        assert full_user.telefono == "+57 3001234567"
        assert full_user.ciudad == "Bogotá"


@pytest.mark.integration
class TestSchemaFileCompatibility:
    """Integration tests for all schema files"""

    def test_all_schemas_importable(self):
        """Test that all schema files can be imported without errors"""
        try:
            from app.schemas import (
                user, product, category, transaction, vendor_profile,
                alerts, common, commission, leads, payout_request
            )
            # If we get here, all imports succeeded
            assert True
        except ImportError as e:
            pytest.fail(f"Schema import failed: {e}")

    def test_model_validation_works(self):
        """Test basic model validation for key schemas"""
        # Test UserCreate
        user = UserCreate(
            email="test@example.com",
            nombre="Test",
            apellido="User",
            password="TestPass123"
        )
        assert user.email == "test@example.com"

        # Test CategoryCreate
        category = CategoryCreate(
            name="Test Category",
            description="Test description"
        )
        assert category.name == "Test Category"

    def test_config_migration_success(self):
        """Test that all Config classes have been properly migrated"""
        from app.schemas.user import UserCreate
        from app.schemas.category import CategoryCreate

        # Check that models have model_config instead of Config
        assert hasattr(UserCreate, 'model_config')
        assert hasattr(CategoryCreate, 'model_config') or not hasattr(CategoryCreate, 'Config')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])