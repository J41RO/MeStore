"""
Tests for API ID consistency validation across all endpoints.

This test suite ensures that all API endpoints consistently handle UUID-based IDs
with proper validation, error handling, and response formatting.
"""

import pytest
import uuid
from uuid import UUID
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.core.id_validation import (
    IDValidator,
    IDValidationError,
    FastIDValidator,
    normalize_uuid_string,
    convert_to_uuid_object
)


class TestIDValidationUtilities:
    """Test ID validation utility functions."""

    def test_is_valid_uuid_string(self):
        """Test UUID string validation."""
        # Valid UUIDs
        valid_uuid = str(uuid.uuid4())
        assert IDValidator.is_valid_uuid_string(valid_uuid) is True

        # Invalid UUIDs
        assert IDValidator.is_valid_uuid_string("invalid") is False
        assert IDValidator.is_valid_uuid_string("") is False
        assert IDValidator.is_valid_uuid_string(None) is False
        assert IDValidator.is_valid_uuid_string("123") is False
        assert IDValidator.is_valid_uuid_string("550e8400-e29b-41d4-a716-44665544000") is False  # Wrong length

    def test_validate_uuid_string(self):
        """Test UUID string validation with normalization."""
        valid_uuid = str(uuid.uuid4())

        # Valid UUID should return normalized string
        result = IDValidator.validate_uuid_string(valid_uuid)
        assert result == valid_uuid.lower()

        # Uppercase UUID should be normalized to lowercase
        uppercase_uuid = valid_uuid.upper()
        result = IDValidator.validate_uuid_string(uppercase_uuid)
        assert result == valid_uuid.lower()

        # Invalid UUID should raise exception
        with pytest.raises(IDValidationError) as exc_info:
            IDValidator.validate_uuid_string("invalid")
        assert "Invalid id format" in str(exc_info.value)

    def test_validate_optional_uuid_string(self):
        """Test optional UUID validation."""
        valid_uuid = str(uuid.uuid4())

        # Valid UUID
        result = IDValidator.validate_optional_uuid_string(valid_uuid)
        assert result == valid_uuid.lower()

        # None should return None
        result = IDValidator.validate_optional_uuid_string(None)
        assert result is None

        # Empty string should return None
        result = IDValidator.validate_optional_uuid_string("")
        assert result is None

    def test_fast_id_validator(self):
        """Test performance-optimized ID validator."""
        valid_uuid = str(uuid.uuid4())

        # Valid UUID
        assert FastIDValidator.is_valid_uuid_fast(valid_uuid) is True
        assert FastIDValidator.validate_uuid_fast(valid_uuid) == valid_uuid.lower()

        # Invalid UUID
        assert FastIDValidator.is_valid_uuid_fast("invalid") is False

        with pytest.raises(HTTPException):
            FastIDValidator.validate_uuid_fast("invalid")

    def test_normalize_uuid_string(self):
        """Test UUID normalization function."""
        valid_uuid = str(uuid.uuid4())
        uuid_obj = uuid.UUID(valid_uuid)

        # String input
        result = normalize_uuid_string(valid_uuid)
        assert result == valid_uuid.lower()

        # UUID object input
        result = normalize_uuid_string(uuid_obj)
        assert result == str(uuid_obj).lower()

        # None input
        result = normalize_uuid_string(None)
        assert result is None

        # Invalid input
        result = normalize_uuid_string("invalid")
        assert result is None

    def test_convert_to_uuid_object(self):
        """Test UUID object conversion."""
        valid_uuid = str(uuid.uuid4())
        uuid_obj = uuid.UUID(valid_uuid)

        # String input
        result = convert_to_uuid_object(valid_uuid)
        assert isinstance(result, UUID)
        assert str(result) == valid_uuid

        # UUID object input
        result = convert_to_uuid_object(uuid_obj)
        assert result == uuid_obj

        # None input
        result = convert_to_uuid_object(None)
        assert result is None

        # Invalid input
        result = convert_to_uuid_object("invalid")
        assert result is None


class TestAPIEndpointIDConsistency:
    """Test ID consistency across API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_product_endpoints_id_validation(self, client):
        """Test product endpoints use consistent ID validation."""
        # Test valid UUID format
        valid_uuid = str(uuid.uuid4())

        # This should return 404 (product not found) not 422 (validation error)
        response = client.get(f"/api/v1/productos/{valid_uuid}")
        assert response.status_code in [404, 401]  # 401 if auth required

        # Test invalid UUID format should return 422 (validation error)
        response = client.get("/api/v1/productos/invalid-uuid")
        assert response.status_code == 422

        # Test malformed UUID should return 422
        response = client.get("/api/v1/productos/123")
        assert response.status_code == 422

    def test_order_endpoints_id_validation(self, client):
        """Test order endpoints use consistent ID validation."""
        # Test valid UUID format
        valid_uuid = str(uuid.uuid4())

        # This should return 404 (order not found) not 422 (validation error)
        response = client.get(f"/api/v1/orders/{valid_uuid}")
        assert response.status_code in [404, 401]  # 401 if auth required

        # Test invalid UUID format should return 422 (validation error)
        response = client.get("/api/v1/orders/invalid-uuid")
        assert response.status_code == 422

    def test_commission_endpoints_id_validation(self, client):
        """Test commission endpoints use consistent ID validation."""
        # Test valid UUID format
        valid_uuid = str(uuid.uuid4())

        # This should return 404 (commission not found) not 422 (validation error)
        response = client.get(f"/api/v1/commissions/{valid_uuid}")
        assert response.status_code in [404, 401]  # 401 if auth required

        # Test invalid UUID format should return 422 (validation error)
        response = client.get("/api/v1/commissions/invalid-uuid")
        assert response.status_code == 422

    def test_user_endpoints_id_validation(self, client):
        """Test user endpoints use consistent ID validation."""
        # Test auth endpoints that should include user ID
        response = client.get("/api/v1/auth/me")
        # Should require authentication, not validation error
        assert response.status_code == 401

    def test_path_parameter_regex_validation(self, client):
        """Test that path parameters correctly validate UUID format."""
        test_cases = [
            # Valid UUID formats
            ("550e8400-e29b-41d4-a716-446655440000", [404, 401]),
            ("AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE", [404, 401]),

            # Invalid UUID formats (should return 422)
            ("invalid", [422]),
            ("123", [422]),
            ("", [404]),  # Empty might be 404 for different route
            ("550e8400-e29b-41d4-a716", [422]),  # Too short
            ("550e8400-e29b-41d4-a716-446655440000x", [422]),  # Too long
            ("550e8400xe29b-41d4-a716-446655440000", [422]),  # Invalid char
        ]

        endpoints = [
            "/api/v1/productos/{}",
            "/api/v1/commissions/{}",
        ]

        for uuid_test, expected_codes in test_cases:
            for endpoint_template in endpoints:
                endpoint = endpoint_template.format(uuid_test)
                response = client.get(endpoint)
                assert response.status_code in expected_codes, \
                    f"Endpoint {endpoint} returned {response.status_code}, expected one of {expected_codes}"


class TestSchemaIDValidation:
    """Test Pydantic schema ID validation."""

    def test_base_id_schema_validation(self):
        """Test base ID schema validation."""
        from app.schemas.base import BaseIDSchema

        valid_uuid = str(uuid.uuid4())

        # Valid UUID should pass
        schema = BaseIDSchema(id=valid_uuid)
        assert schema.id == valid_uuid.lower()

        # Invalid UUID should raise validation error
        with pytest.raises(ValueError):
            BaseIDSchema(id="invalid")

    def test_user_schema_id_validation(self):
        """Test user schema ID validation."""
        from app.schemas.user import UserRead
        from datetime import datetime

        valid_uuid = str(uuid.uuid4())

        # Valid data should pass
        user_data = {
            "id": valid_uuid,
            "email": "test@example.com",
            "nombre": "Test",
            "apellido": "User",
            "user_type": "COMPRADOR",
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        schema = UserRead(**user_data)
        assert schema.id == valid_uuid.lower()

        # Invalid ID should raise validation error
        user_data["id"] = "invalid"
        with pytest.raises(ValueError):
            UserRead(**user_data)

    def test_order_schema_id_validation(self):
        """Test order schema ID validation."""
        from app.schemas.order import OrderResponse
        from datetime import datetime

        valid_order_id = str(uuid.uuid4())
        valid_buyer_id = str(uuid.uuid4())

        order_data = {
            "id": valid_order_id,
            "buyer_id": valid_buyer_id,
            "status": "pending",
            "total_amount": 100.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "items": []
        }

        # Valid IDs should pass
        schema = OrderResponse(**order_data)
        assert schema.id == valid_order_id.lower()
        assert schema.buyer_id == valid_buyer_id.lower()

        # Invalid order ID should raise validation error
        order_data["id"] = "invalid"
        with pytest.raises(ValueError):
            OrderResponse(**order_data)


class TestErrorResponseConsistency:
    """Test consistent error responses for ID validation."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_validation_error_format(self, client):
        """Test that validation errors have consistent format."""
        # Test invalid UUID in path parameter
        response = client.get("/api/v1/productos/invalid-uuid")
        assert response.status_code == 422

        error_data = response.json()
        assert "detail" in error_data

        # Should be a list of validation errors
        if isinstance(error_data["detail"], list):
            for error in error_data["detail"]:
                assert "type" in error
                assert "msg" in error
                assert "loc" in error

    def test_not_found_error_format(self, client):
        """Test that not found errors have consistent format."""
        valid_uuid = str(uuid.uuid4())

        # Test valid UUID format but non-existent entity
        response = client.get(f"/api/v1/productos/{valid_uuid}")

        # Should return 404 (if auth passes) or 401 (if auth required)
        assert response.status_code in [404, 401]

        if response.status_code == 404:
            error_data = response.json()
            assert "detail" in error_data
            assert isinstance(error_data["detail"], str)


class TestPerformanceAndCaching:
    """Test ID validation performance and caching."""

    def test_fast_validator_performance(self):
        """Test that FastIDValidator is actually faster than regular validator."""
        import time

        valid_uuid = str(uuid.uuid4())
        invalid_uuid = "invalid"

        # Test performance of regular validator
        start_time = time.time()
        for _ in range(1000):
            IDValidator.is_valid_uuid_string(valid_uuid)
            IDValidator.is_valid_uuid_string(invalid_uuid)
        regular_time = time.time() - start_time

        # Test performance of fast validator
        start_time = time.time()
        for _ in range(1000):
            FastIDValidator.is_valid_uuid_fast(valid_uuid)
            FastIDValidator.is_valid_uuid_fast(invalid_uuid)
        fast_time = time.time() - start_time

        # Fast validator should be at least 20% faster
        assert fast_time < regular_time * 0.8

    def test_uuid_normalization_consistency(self):
        """Test that UUID normalization is consistent across functions."""
        test_uuid = str(uuid.uuid4())
        uppercase_uuid = test_uuid.upper()
        mixed_case_uuid = test_uuid[0:10].upper() + test_uuid[10:].lower()

        # All normalizations should produce the same result
        result1 = normalize_uuid_string(test_uuid)
        result2 = normalize_uuid_string(uppercase_uuid)
        result3 = normalize_uuid_string(mixed_case_uuid)

        assert result1 == result2 == result3 == test_uuid.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])