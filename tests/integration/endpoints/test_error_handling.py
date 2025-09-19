"""
Error Handling Validation Tests.
Comprehensive testing of error responses, status codes, and error message consistency.

File: tests/integration/endpoints/test_error_handling.py
Author: Integration Testing AI
Date: 2025-09-17
Purpose: Validate standardized error handling across all API endpoints
"""

import pytest
import json
from typing import Dict, List, Any, Optional
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserType
from app.core.security import create_access_token

# Test markers
pytestmark = [
    pytest.mark.integration,
    pytest.mark.api,
    pytest.mark.error_handling,
    pytest.mark.critical
]


class ErrorHandlingValidator:
    """
    Comprehensive error handling validation framework.
    Tests error response consistency, status codes, and message standardization.
    """

    def __init__(self, client: AsyncClient, session: AsyncSession):
        self.client = client
        self.session = session
        self.validation_results = {
            "status_code_consistency": {},
            "error_message_format": {},
            "authentication_errors": {},
            "authorization_errors": {},
            "validation_errors": {},
            "not_found_errors": {},
            "server_errors": {},
            "rate_limiting_errors": {}
        }

    async def validate_all_error_handling(self) -> Dict[str, Any]:
        """Run all error handling validation tests."""

        # 1. Test HTTP status code consistency
        await self._test_status_code_consistency()

        # 2. Test error message format standardization
        await self._test_error_message_format()

        # 3. Test authentication errors (401)
        await self._test_authentication_errors()

        # 4. Test authorization errors (403)
        await self._test_authorization_errors()

        # 5. Test validation errors (422)
        await self._test_validation_errors()

        # 6. Test not found errors (404)
        await self._test_not_found_errors()

        # 7. Test server errors (500)
        await self._test_server_errors()

        # 8. Test rate limiting errors (429)
        await self._test_rate_limiting_errors()

        return self._generate_error_handling_report()

    async def _test_status_code_consistency(self):
        """Test HTTP status code consistency across endpoints."""

        consistency_results = {}

        # Test endpoints that should return 200
        success_endpoints = [
            {"path": "/api/v1/health", "method": "GET", "expected": 200},
        ]

        # Test endpoints that should return 401 without auth
        auth_required_endpoints = [
            {"path": "/api/v1/auth/me", "method": "GET", "expected": 401},
            {"path": "/api/v1/products", "method": "GET", "expected": 401},
            {"path": "/api/v1/orders", "method": "GET", "expected": 401},
        ]

        # Test endpoints that should return 404
        not_found_endpoints = [
            {"path": "/api/v1/nonexistent", "method": "GET", "expected": 404},
            {"path": "/api/v1/invalid/endpoint", "method": "GET", "expected": 404},
        ]

        # Test success endpoints
        for endpoint in success_endpoints:
            result = await self._test_endpoint_status(endpoint)
            consistency_results[f"success_{endpoint['path']}"] = result

        # Test auth required endpoints
        for endpoint in auth_required_endpoints:
            result = await self._test_endpoint_status(endpoint)
            consistency_results[f"auth_required_{endpoint['path']}"] = result

        # Test not found endpoints
        for endpoint in not_found_endpoints:
            result = await self._test_endpoint_status(endpoint)
            consistency_results[f"not_found_{endpoint['path']}"] = result

        self.validation_results["status_code_consistency"] = consistency_results

    async def _test_error_message_format(self):
        """Test error message format standardization."""

        format_results = {}

        # Test 401 error format
        format_401 = await self._test_401_error_format()
        format_results["error_401_format"] = format_401

        # Test 422 validation error format
        format_422 = await self._test_422_error_format()
        format_results["error_422_format"] = format_422

        # Test 404 error format
        format_404 = await self._test_404_error_format()
        format_results["error_404_format"] = format_404

        # Test error response structure consistency
        structure_test = await self._test_error_structure_consistency()
        format_results["structure_consistency"] = structure_test

        self.validation_results["error_message_format"] = format_results

    async def _test_authentication_errors(self):
        """Test authentication error scenarios (401)."""

        auth_error_results = {}

        # Test no token provided
        no_token_result = await self._test_no_token_error()
        auth_error_results["no_token"] = no_token_result

        # Test invalid token
        invalid_token_result = await self._test_invalid_token_error()
        auth_error_results["invalid_token"] = invalid_token_result

        # Test expired token
        expired_token_result = await self._test_expired_token_error()
        auth_error_results["expired_token"] = expired_token_result

        # Test malformed token
        malformed_token_result = await self._test_malformed_token_error()
        auth_error_results["malformed_token"] = malformed_token_result

        self.validation_results["authentication_errors"] = auth_error_results

    async def _test_authorization_errors(self):
        """Test authorization error scenarios (403)."""

        auth_error_results = {}

        # Test insufficient permissions
        insufficient_perms = await self._test_insufficient_permissions()
        auth_error_results["insufficient_permissions"] = insufficient_perms

        # Test role-based access violations
        role_violations = await self._test_role_based_violations()
        auth_error_results["role_violations"] = role_violations

        # Test resource ownership violations
        ownership_violations = await self._test_ownership_violations()
        auth_error_results["ownership_violations"] = ownership_violations

        self.validation_results["authorization_errors"] = auth_error_results

    async def _test_validation_errors(self):
        """Test validation error scenarios (422)."""

        validation_results = {}

        # Test missing required fields
        missing_fields = await self._test_missing_required_fields()
        validation_results["missing_fields"] = missing_fields

        # Test invalid data types
        invalid_types = await self._test_invalid_data_types()
        validation_results["invalid_types"] = invalid_types

        # Test invalid field values
        invalid_values = await self._test_invalid_field_values()
        validation_results["invalid_values"] = invalid_values

        # Test constraint violations
        constraints = await self._test_constraint_violations()
        validation_results["constraints"] = constraints

        self.validation_results["validation_errors"] = validation_results

    async def _test_not_found_errors(self):
        """Test not found error scenarios (404)."""

        not_found_results = {}

        # Test non-existent endpoints
        nonexistent_endpoints = await self._test_nonexistent_endpoints()
        not_found_results["nonexistent_endpoints"] = nonexistent_endpoints

        # Test non-existent resources
        nonexistent_resources = await self._test_nonexistent_resources()
        not_found_results["nonexistent_resources"] = nonexistent_resources

        self.validation_results["not_found_errors"] = not_found_results

    async def _test_server_errors(self):
        """Test server error handling (500)."""

        server_error_results = {}

        # Test that normal operations don't cause server errors
        normal_operations = await self._test_normal_operations_no_500()
        server_error_results["normal_operations"] = normal_operations

        # Test graceful degradation
        graceful_degradation = await self._test_graceful_degradation()
        server_error_results["graceful_degradation"] = graceful_degradation

        self.validation_results["server_errors"] = server_error_results

    async def _test_rate_limiting_errors(self):
        """Test rate limiting error scenarios (429)."""

        rate_limit_results = {}

        # Test rate limiting behavior
        rate_limiting = await self._test_rate_limiting_behavior()
        rate_limit_results["rate_limiting"] = rate_limiting

        self.validation_results["rate_limiting_errors"] = rate_limit_results

    # Specific test implementations

    async def _test_endpoint_status(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Test specific endpoint status code."""
        try:
            if endpoint["method"] == "GET":
                response = await self.client.get(endpoint["path"])
            elif endpoint["method"] == "POST":
                response = await self.client.post(endpoint["path"], json={})
            else:
                return {"error": f"Unsupported method: {endpoint['method']}"}

            return {
                "success": response.status_code == endpoint["expected"],
                "actual_status": response.status_code,
                "expected_status": endpoint["expected"],
                "status_correct": response.status_code == endpoint["expected"]
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_401_error_format(self) -> Dict[str, Any]:
        """Test 401 error message format."""
        try:
            response = await self.client.get("/api/v1/auth/me")

            if response.status_code == 401:
                error_data = response.json()

                # Check standard error format
                has_detail = "detail" in error_data
                detail_is_string = isinstance(error_data.get("detail"), str) if has_detail else False

                return {
                    "success": True,
                    "status_code": response.status_code,
                    "has_detail": has_detail,
                    "detail_is_string": detail_is_string,
                    "format_valid": has_detail and detail_is_string,
                    "error_data": error_data
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": "Expected 401 status code"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_422_error_format(self) -> Dict[str, Any]:
        """Test 422 validation error format."""
        try:
            # Send invalid data to trigger validation error
            invalid_data = {"email": "not-an-email", "password": ""}
            response = await self.client.post("/api/v1/auth/login", json=invalid_data)

            if response.status_code == 422:
                error_data = response.json()

                # Check validation error format
                has_detail = "detail" in error_data
                detail_structure_valid = False

                if has_detail:
                    detail = error_data["detail"]
                    if isinstance(detail, list):
                        # Pydantic validation error format
                        detail_structure_valid = all(
                            isinstance(item, dict) and "loc" in item and "msg" in item and "type" in item
                            for item in detail
                        )
                    elif isinstance(detail, str):
                        # Simple string error
                        detail_structure_valid = True

                return {
                    "success": True,
                    "status_code": response.status_code,
                    "has_detail": has_detail,
                    "detail_structure_valid": detail_structure_valid,
                    "format_valid": has_detail and detail_structure_valid,
                    "error_data": error_data
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": "Expected 422 status code"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_404_error_format(self) -> Dict[str, Any]:
        """Test 404 error message format."""
        try:
            response = await self.client.get("/api/v1/nonexistent")

            if response.status_code == 404:
                error_data = response.json()

                # Check 404 error format
                has_detail = "detail" in error_data

                return {
                    "success": True,
                    "status_code": response.status_code,
                    "has_detail": has_detail,
                    "format_valid": has_detail,
                    "error_data": error_data
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": "Expected 404 status code"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_error_structure_consistency(self) -> Dict[str, Any]:
        """Test error response structure consistency."""
        try:
            # Test multiple error scenarios for structure consistency
            error_responses = []

            # 401 error
            response_401 = await self.client.get("/api/v1/auth/me")
            if response_401.status_code == 401:
                error_responses.append(("401", response_401.json()))

            # 404 error
            response_404 = await self.client.get("/api/v1/nonexistent")
            if response_404.status_code == 404:
                error_responses.append(("404", response_404.json()))

            # 422 error
            response_422 = await self.client.post("/api/v1/auth/login", json={"email": "invalid"})
            if response_422.status_code == 422:
                error_responses.append(("422", response_422.json()))

            # Check consistency
            all_have_detail = all("detail" in error_data for _, error_data in error_responses)

            return {
                "success": True,
                "error_count": len(error_responses),
                "all_have_detail": all_have_detail,
                "structure_consistent": all_have_detail,
                "error_responses": error_responses
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_no_token_error(self) -> Dict[str, Any]:
        """Test error when no authentication token is provided."""
        try:
            response = await self.client.get("/api/v1/auth/me")

            return {
                "success": response.status_code == 401,
                "status_code": response.status_code,
                "correct_error": response.status_code == 401,
                "error_message": response.json().get("detail") if response.status_code == 401 else None
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_invalid_token_error(self) -> Dict[str, Any]:
        """Test error when invalid token is provided."""
        try:
            headers = {"Authorization": "Bearer invalid_token_123"}
            response = await self.client.get("/api/v1/auth/me", headers=headers)

            return {
                "success": response.status_code == 401,
                "status_code": response.status_code,
                "correct_error": response.status_code == 401,
                "error_message": response.json().get("detail") if response.status_code == 401 else None
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_expired_token_error(self) -> Dict[str, Any]:
        """Test error when expired token is provided."""
        try:
            # Use a clearly expired token
            expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxfQ.invalid"
            headers = {"Authorization": f"Bearer {expired_token}"}
            response = await self.client.get("/api/v1/auth/me", headers=headers)

            return {
                "success": response.status_code == 401,
                "status_code": response.status_code,
                "correct_error": response.status_code == 401,
                "error_message": response.json().get("detail") if response.status_code == 401 else None
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_malformed_token_error(self) -> Dict[str, Any]:
        """Test error when malformed token is provided."""
        try:
            headers = {"Authorization": "Bearer malformed.token.here"}
            response = await self.client.get("/api/v1/auth/me", headers=headers)

            return {
                "success": response.status_code == 401,
                "status_code": response.status_code,
                "correct_error": response.status_code == 401,
                "error_message": response.json().get("detail") if response.status_code == 401 else None
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_insufficient_permissions(self) -> Dict[str, Any]:
        """Test error when user has insufficient permissions."""
        try:
            # Create vendor user and try to access admin endpoint
            vendor_user = await self._create_test_user(user_type=UserType.VENDEDOR)
            vendor_token = create_access_token(data={"sub": str(vendor_user.id)})
            headers = {"Authorization": f"Bearer {vendor_token}"}

            response = await self.client.get("/api/v1/admin/users", headers=headers)

            return {
                "success": response.status_code == 403,
                "status_code": response.status_code,
                "correct_error": response.status_code == 403,
                "error_message": response.json().get("detail") if response.status_code == 403 else None
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_role_based_violations(self) -> Dict[str, Any]:
        """Test role-based access violations."""
        try:
            # Create buyer user and try to create products (vendor operation)
            buyer_user = await self._create_test_user(user_type=UserType.COMPRADOR)
            buyer_token = create_access_token(data={"sub": str(buyer_user.id)})
            headers = {"Authorization": f"Bearer {buyer_token}"}

            product_data = {
                "sku": "BUYER-VIOLATION-TEST",
                "name": "Buyer Violation Test Product",
                "precio_venta": 100000.0
            }

            response = await self.client.post("/api/v1/products", json=product_data, headers=headers)

            return {
                "success": response.status_code in [403, 401],
                "status_code": response.status_code,
                "correct_error": response.status_code in [403, 401],
                "error_message": response.json().get("detail") if response.status_code in [403, 401] else None
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_ownership_violations(self) -> Dict[str, Any]:
        """Test resource ownership violations."""
        try:
            # This would test accessing resources owned by other users
            # For now, we'll test basic access control
            vendor_user = await self._create_test_user(user_type=UserType.VENDEDOR)
            vendor_token = create_access_token(data={"sub": str(vendor_user.id)})
            headers = {"Authorization": f"Bearer {vendor_token}"}

            # Try to access admin endpoint
            response = await self.client.get("/api/v1/admin/users", headers=headers)

            return {
                "success": response.status_code == 403,
                "status_code": response.status_code,
                "correct_error": response.status_code == 403,
                "note": "Full ownership violation testing requires resource-specific endpoints"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_missing_required_fields(self) -> Dict[str, Any]:
        """Test validation errors for missing required fields."""
        try:
            # Test login with missing fields
            response = await self.client.post("/api/v1/auth/login", json={})

            return {
                "success": response.status_code == 422,
                "status_code": response.status_code,
                "correct_error": response.status_code == 422,
                "error_details": response.json() if response.status_code == 422 else None
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_invalid_data_types(self) -> Dict[str, Any]:
        """Test validation errors for invalid data types."""
        try:
            # Test with invalid data types
            invalid_data = {
                "email": 123,  # Should be string
                "password": True  # Should be string
            }

            response = await self.client.post("/api/v1/auth/login", json=invalid_data)

            return {
                "success": response.status_code == 422,
                "status_code": response.status_code,
                "correct_error": response.status_code == 422,
                "error_details": response.json() if response.status_code == 422 else None
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_invalid_field_values(self) -> Dict[str, Any]:
        """Test validation errors for invalid field values."""
        try:
            # Test with invalid email format
            invalid_data = {
                "email": "not-an-email",
                "password": "validpassword"
            }

            response = await self.client.post("/api/v1/auth/login", json=invalid_data)

            return {
                "success": response.status_code in [422, 401],  # Could be validation or auth error
                "status_code": response.status_code,
                "correct_error": response.status_code in [422, 401],
                "error_details": response.json() if response.status_code in [422, 401] else None
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_constraint_violations(self) -> Dict[str, Any]:
        """Test constraint violation errors."""
        try:
            # Test creating product with negative price (business constraint)
            vendor_user = await self._create_test_user(user_type=UserType.VENDEDOR)
            vendor_token = create_access_token(data={"sub": str(vendor_user.id)})
            headers = {"Authorization": f"Bearer {vendor_token}"}

            invalid_product = {
                "sku": "CONSTRAINT-TEST",
                "name": "Constraint Test Product",
                "precio_venta": -100.0  # Negative price should violate constraints
            }

            response = await self.client.post("/api/v1/products", json=invalid_product, headers=headers)

            return {
                "success": response.status_code in [400, 422],
                "status_code": response.status_code,
                "correct_error": response.status_code in [400, 422],
                "constraint_enforced": response.status_code in [400, 422]
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_nonexistent_endpoints(self) -> Dict[str, Any]:
        """Test accessing non-existent endpoints."""
        try:
            nonexistent_endpoints = [
                "/api/v1/nonexistent",
                "/api/v1/invalid/endpoint",
                "/api/v2/products"  # Different version
            ]

            results = {}
            for endpoint in nonexistent_endpoints:
                response = await self.client.get(endpoint)
                results[endpoint] = {
                    "status_code": response.status_code,
                    "correct_404": response.status_code == 404
                }

            all_404 = all(result["correct_404"] for result in results.values())

            return {
                "success": all_404,
                "all_return_404": all_404,
                "endpoint_results": results
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_nonexistent_resources(self) -> Dict[str, Any]:
        """Test accessing non-existent resources."""
        try:
            # Test accessing non-existent resource by ID
            vendor_user = await self._create_test_user(user_type=UserType.VENDEDOR)
            vendor_token = create_access_token(data={"sub": str(vendor_user.id)})
            headers = {"Authorization": f"Bearer {vendor_token}"}

            # Try to access non-existent product
            response = await self.client.get("/api/v1/products/nonexistent-id", headers=headers)

            return {
                "success": response.status_code == 404,
                "status_code": response.status_code,
                "correct_404": response.status_code == 404,
                "resource_not_found_handled": response.status_code == 404
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_normal_operations_no_500(self) -> Dict[str, Any]:
        """Test that normal operations don't cause 500 errors."""
        try:
            # Test various normal operations
            operations = []

            # Health check
            health_response = await self.client.get("/api/v1/health")
            operations.append(("health", health_response.status_code))

            # Login attempt (may fail but shouldn't be 500)
            login_response = await self.client.post("/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "testpass"
            })
            operations.append(("login", login_response.status_code))

            # Check for any 500 errors
            has_500_errors = any(status_code == 500 for _, status_code in operations)

            return {
                "success": not has_500_errors,
                "no_500_errors": not has_500_errors,
                "operations": operations,
                "stability_good": not has_500_errors
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_graceful_degradation(self) -> Dict[str, Any]:
        """Test graceful degradation under error conditions."""
        try:
            # Test that the API remains responsive under various error conditions
            error_conditions = []

            # Invalid JSON
            try:
                response = await self.client.post(
                    "/api/v1/auth/login",
                    content="invalid json content",
                    headers={"Content-Type": "application/json"}
                )
                error_conditions.append(("invalid_json", response.status_code, response.status_code != 500))
            except Exception:
                error_conditions.append(("invalid_json", 500, False))

            # Large payload (within reason)
            large_data = {"data": "x" * 10000}  # 10KB of data
            response = await self.client.post("/api/v1/auth/login", json=large_data)
            error_conditions.append(("large_payload", response.status_code, response.status_code != 500))

            graceful_degradation = all(graceful for _, _, graceful in error_conditions)

            return {
                "success": graceful_degradation,
                "graceful_degradation": graceful_degradation,
                "error_conditions": error_conditions,
                "resilience_good": graceful_degradation
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_rate_limiting_behavior(self) -> Dict[str, Any]:
        """Test rate limiting behavior."""
        try:
            # Test multiple rapid requests
            import asyncio

            # Make multiple concurrent requests
            tasks = []
            for _ in range(10):
                tasks.append(self.client.get("/api/v1/health"))

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            # Check for rate limiting responses
            status_codes = [
                r.status_code for r in responses
                if hasattr(r, 'status_code')
            ]

            has_rate_limiting = any(code == 429 for code in status_codes)
            all_successful = all(code in [200, 429] for code in status_codes)

            return {
                "success": all_successful,
                "rate_limiting_detected": has_rate_limiting,
                "all_responses_valid": all_successful,
                "status_codes": status_codes,
                "total_requests": len(tasks)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _create_test_user(self, user_type: UserType = UserType.VENDEDOR) -> User:
        """Create a test user for error testing."""
        from app.core.security import get_password_hash
        import uuid
        import time

        user = User(
            id=uuid.uuid4(),
            email=f"error_test_{int(time.time())}_{uuid.uuid4().hex[:8]}@example.com",
            password_hash=await get_password_hash("testpass123"),
            nombre="Error Test User",
            apellido="Test",
            user_type=user_type,
            is_active=True
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    def _generate_error_handling_report(self) -> Dict[str, Any]:
        """Generate error handling validation report."""

        total_validations = 0
        passed_validations = 0

        # Count all validation results
        for category, tests in self.validation_results.items():
            for test_name, result in tests.items():
                if isinstance(result, dict) and "success" in result:
                    total_validations += 1
                    if result.get("success"):
                        passed_validations += 1

        # Calculate compliance
        compliance_percentage = (passed_validations / total_validations * 100) if total_validations > 0 else 0

        return {
            "error_handling_compliance": {
                "total_validations": total_validations,
                "passed_validations": passed_validations,
                "compliance_percentage": round(compliance_percentage, 2),
                "status": "ROBUST" if compliance_percentage >= 90 else "NEEDS_IMPROVEMENT"
            },
            "detailed_results": self.validation_results,
            "recommendations": self._generate_error_handling_recommendations()
        }

    def _generate_error_handling_recommendations(self) -> List[str]:
        """Generate recommendations for error handling improvements."""
        recommendations = []

        # Check status code consistency
        status_consistency = self.validation_results.get("status_code_consistency", {})
        for test_name, result in status_consistency.items():
            if isinstance(result, dict) and not result.get("status_correct"):
                recommendations.append(f"Status code inconsistency in {test_name}")

        # Check error message format
        error_format = self.validation_results.get("error_message_format", {})
        structure_test = error_format.get("structure_consistency", {})
        if not structure_test.get("structure_consistent"):
            recommendations.append("Error message structure needs standardization")

        # Check authentication errors
        auth_errors = self.validation_results.get("authentication_errors", {})
        for error_type, result in auth_errors.items():
            if isinstance(result, dict) and not result.get("correct_error"):
                recommendations.append(f"Authentication error handling needs improvement for {error_type}")

        # Check authorization errors
        authz_errors = self.validation_results.get("authorization_errors", {})
        for error_type, result in authz_errors.items():
            if isinstance(result, dict) and not result.get("correct_error"):
                recommendations.append(f"Authorization error handling needs improvement for {error_type}")

        # Check server errors
        server_errors = self.validation_results.get("server_errors", {})
        normal_ops = server_errors.get("normal_operations", {})
        if not normal_ops.get("no_500_errors"):
            recommendations.append("Server error handling needs improvement - 500 errors in normal operations")

        if not recommendations:
            recommendations.append("All error handling is properly implemented and consistent!")

        return recommendations


# Test classes using the error handling validator
@pytest.mark.asyncio
@pytest.mark.integration
class TestErrorHandling:
    """
    Test comprehensive error handling validation.
    """

    async def test_comprehensive_error_handling(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession
    ):
        """
        Comprehensive test of error handling across all scenarios.
        """

        validator = ErrorHandlingValidator(async_client, async_session)
        error_report = await validator.validate_all_error_handling()

        # Assert error handling standards
        assert error_report["error_handling_compliance"]["compliance_percentage"] >= 85, \
            f"Error handling compliance below threshold: {error_report['error_handling_compliance']['compliance_percentage']}%"

        # Log results
        print("\n=== ERROR HANDLING VALIDATION REPORT ===")
        print(f"Total Validations: {error_report['error_handling_compliance']['total_validations']}")
        print(f"Passed Validations: {error_report['error_handling_compliance']['passed_validations']}")
        print(f"Compliance: {error_report['error_handling_compliance']['compliance_percentage']}%")
        print(f"Status: {error_report['error_handling_compliance']['status']}")

        print("\n=== ERROR HANDLING RECOMMENDATIONS ===")
        for rec in error_report["recommendations"]:
            print(f"- {rec}")

        return error_report

    async def test_authentication_error_consistency(self, async_client: AsyncClient, async_session: AsyncSession):
        """Test authentication error consistency."""

        validator = ErrorHandlingValidator(async_client, async_session)
        await validator._test_authentication_errors()

        auth_results = validator.validation_results["authentication_errors"]

        # Verify authentication errors
        no_token = auth_results.get("no_token", {})
        assert no_token.get("success"), "No token error must return 401"

        invalid_token = auth_results.get("invalid_token", {})
        assert invalid_token.get("success"), "Invalid token error must return 401"

    async def test_authorization_error_consistency(self, async_client: AsyncClient, async_session: AsyncSession):
        """Test authorization error consistency."""

        validator = ErrorHandlingValidator(async_client, async_session)
        await validator._test_authorization_errors()

        authz_results = validator.validation_results["authorization_errors"]

        # Verify authorization errors
        insufficient_perms = authz_results.get("insufficient_permissions", {})
        assert insufficient_perms.get("success"), "Insufficient permissions must return 403"

    async def test_validation_error_consistency(self, async_client: AsyncClient, async_session: AsyncSession):
        """Test validation error consistency."""

        validator = ErrorHandlingValidator(async_client, async_session)
        await validator._test_validation_errors()

        validation_results = validator.validation_results["validation_errors"]

        # Verify validation errors
        missing_fields = validation_results.get("missing_fields", {})
        assert missing_fields.get("success"), "Missing required fields must return 422"

    async def test_server_error_handling(self, async_client: AsyncClient, async_session: AsyncSession):
        """Test server error handling."""

        validator = ErrorHandlingValidator(async_client, async_session)
        await validator._test_server_errors()

        server_results = validator.validation_results["server_errors"]

        # Verify server error handling
        normal_ops = server_results.get("normal_operations", {})
        assert normal_ops.get("success"), "Normal operations must not cause 500 errors"

        graceful_degradation = server_results.get("graceful_degradation", {})
        assert graceful_degradation.get("success"), "API must handle error conditions gracefully"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])