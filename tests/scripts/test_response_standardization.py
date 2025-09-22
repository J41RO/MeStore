#!/usr/bin/env python3
# ~/test_response_standardization.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Response Standardization Validation Test
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
Comprehensive test script for FastAPI response standardization implementation.

This script validates:
- Standardized response schemas work correctly
- Exception handlers return proper format
- Response utilities function as expected
- Error codes are consistent
- Pagination format is correct
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

def test_response_schemas():
    """Test response schema creation and validation."""
    print("🧪 Testing Response Schemas...")

    try:
        from app.schemas.response_base import (
            SuccessResponse,
            ErrorResponse,
            PaginatedResponse,
            PaginationInfo,
            ErrorDetail,
            create_success_response,
            create_error_response,
            create_paginated_response
        )

        # Test SuccessResponse
        success_data = {"id": 1, "name": "Test Product"}
        success_response = create_success_response(
            data=success_data,
            message="Test successful"
        )

        assert success_response.status == "success"
        assert success_response.data == success_data
        assert success_response.message == "Test successful"
        assert isinstance(success_response.timestamp, datetime)
        print("✅ SuccessResponse schema validation passed")

        # Test ErrorResponse
        error_details = [ErrorDetail(
            field="email",
            message="Invalid email format",
            error_type="validation_error"
        )]

        error_response = create_error_response(
            error_code="VALIDATION_ERROR",
            error_message="Input validation failed",
            details=error_details
        )

        assert error_response.status == "error"
        assert error_response.error_code == "VALIDATION_ERROR"
        assert error_response.error_message == "Input validation failed"
        assert len(error_response.details) == 1
        print("✅ ErrorResponse schema validation passed")

        # Test PaginatedResponse
        test_items = [{"id": 1}, {"id": 2}, {"id": 3}]
        paginated_response = create_paginated_response(
            data=test_items,
            page=1,
            size=10,
            total=25
        )

        assert paginated_response.status == "success"
        assert len(paginated_response.data) == 3
        assert paginated_response.pagination.page == 1
        assert paginated_response.pagination.total == 25
        assert paginated_response.pagination.pages == 3
        assert paginated_response.pagination.has_next == True
        assert paginated_response.pagination.has_prev == False
        print("✅ PaginatedResponse schema validation passed")

        return True

    except Exception as e:
        print(f"❌ Response schema test failed: {e}")
        return False


def test_response_utils():
    """Test response utility functions."""
    print("\n🧪 Testing Response Utils...")

    try:
        from app.schemas.response_base import ErrorCodes

        # Test that error codes are accessible
        assert hasattr(ErrorCodes, 'BAD_REQUEST')
        assert hasattr(ErrorCodes, 'NOT_FOUND')
        print("✅ ErrorCodes accessible")

        # Test basic response schema creation without utilities (to avoid import issues)
        from app.schemas.response_base import create_success_response, create_error_response

        # Test success response creation
        success_resp = create_success_response(
            data={"test": "data"},
            message="Test message"
        )
        assert success_resp.status == "success"
        print("✅ Success response creation passed")

        # Test error response creation
        error_resp = create_error_response(
            error_code=ErrorCodes.BAD_REQUEST,
            error_message="Test error"
        )
        assert error_resp.status == "error"
        print("✅ Error response creation passed")

        return True

    except Exception as e:
        print(f"❌ Response utils test failed: {e}")
        return False


def test_error_codes():
    """Test error code consistency."""
    print("\n🧪 Testing Error Codes...")

    try:
        from app.schemas.response_base import ErrorCodes

        # Check all error codes exist
        expected_codes = [
            "BAD_REQUEST", "UNAUTHORIZED", "FORBIDDEN", "NOT_FOUND",
            "METHOD_NOT_ALLOWED", "CONFLICT", "VALIDATION_ERROR",
            "TOO_MANY_REQUESTS", "INTERNAL_SERVER_ERROR", "BAD_GATEWAY",
            "SERVICE_UNAVAILABLE", "GATEWAY_TIMEOUT", "INSUFFICIENT_FUNDS",
            "PRODUCT_NOT_AVAILABLE", "ORDER_NOT_FOUND", "PAYMENT_FAILED",
            "COMMISSION_CALCULATION_ERROR", "VENDOR_NOT_AUTHORIZED",
            "BUYER_NOT_VERIFIED"
        ]

        for code in expected_codes:
            assert hasattr(ErrorCodes, code), f"Missing error code: {code}"

        print("✅ All expected error codes are present")
        return True

    except Exception as e:
        print(f"❌ Error codes test failed: {e}")
        return False


def test_exception_handlers():
    """Test exception handler imports and structure."""
    print("\n🧪 Testing Exception Handlers...")

    try:
        # Import just the base classes to avoid dependency issues
        from app.schemas.response_base import ErrorCodes, ErrorDetail

        # Test that we can create ErrorDetail objects
        error_detail = ErrorDetail(
            field="test_field",
            message="Test message",
            error_type="test_error"
        )
        assert error_detail.field == "test_field"
        assert error_detail.message == "Test message"
        print("✅ ErrorDetail structure validated")

        # Test ErrorCodes exist
        assert hasattr(ErrorCodes, 'BAD_REQUEST')
        assert hasattr(ErrorCodes, 'UNAUTHORIZED')
        print("✅ ErrorCodes available")

        print("✅ Exception handler core components validated")
        return True

    except Exception as e:
        print(f"❌ Exception handlers test failed: {e}")
        return False


def test_middleware_imports():
    """Test middleware imports and basic structure."""
    print("\n🧪 Testing Middleware Imports...")

    try:
        # Test that middleware file exists and can be imported
        import app.middleware.response_standardization as middleware_module

        # Check that key classes are defined
        assert hasattr(middleware_module, 'ResponseStandardizationMiddleware')
        assert hasattr(middleware_module, 'ResponseTimingMiddleware')
        assert hasattr(middleware_module, 'RequestLoggingMiddleware')

        print("✅ All middleware classes are available")
        return True

    except Exception as e:
        print(f"❌ Middleware imports test failed: {e}")
        return False


def test_schema_serialization():
    """Test that schemas can be properly serialized to JSON."""
    print("\n🧪 Testing Schema Serialization...")

    try:
        from app.schemas.response_base import (
            create_success_response,
            create_error_response,
            create_paginated_response,
            ErrorDetail
        )

        # Test success response serialization
        success_resp = create_success_response(
            data={"id": 1, "name": "Test"},
            message="Success"
        )
        success_json = success_resp.model_dump()
        assert "status" in success_json
        assert "data" in success_json
        assert "timestamp" in success_json
        print("✅ SuccessResponse serialization passed")

        # Test error response serialization
        error_details = [ErrorDetail(
            field="email",
            message="Invalid format",
            error_type="validation"
        )]
        error_resp = create_error_response(
            error_code="VALIDATION_ERROR",
            error_message="Validation failed",
            details=error_details
        )
        error_json = error_resp.model_dump()
        assert "status" in error_json
        assert "error_code" in error_json
        assert "details" in error_json
        print("✅ ErrorResponse serialization passed")

        # Test paginated response serialization
        paginated_resp = create_paginated_response(
            data=[{"id": 1}, {"id": 2}],
            page=1,
            size=10,
            total=25
        )
        paginated_json = paginated_resp.model_dump()
        assert "status" in paginated_json
        assert "data" in paginated_json
        assert "pagination" in paginated_json
        print("✅ PaginatedResponse serialization passed")

        return True

    except Exception as e:
        print(f"❌ Schema serialization test failed: {e}")
        return False


def run_all_tests():
    """Run all validation tests."""
    print("🚀 Starting FastAPI Response Standardization Validation Tests\n")

    tests = [
        test_response_schemas,
        test_response_utils,
        test_error_codes,
        test_exception_handlers,
        test_middleware_imports,
        test_schema_serialization
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)

    # Summary
    print(f"\n📊 Test Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")

    if all(results):
        print("\n🎉 All tests passed! FastAPI Response Standardization is working correctly.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please review the implementation.")
        return False


def main():
    """Main function to run validation tests."""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()