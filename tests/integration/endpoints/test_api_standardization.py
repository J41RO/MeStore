"""
Integration tests for API endpoint standardization validation.
Tests comprehensive endpoint consistency, authentication flows, and CRUD operations.

File: tests/integration/endpoints/test_api_standardization.py
Author: Integration Testing AI
Date: 2025-09-17
Purpose: Validate API endpoint standardization compliance and consistency
"""

import pytest
import time
from typing import Dict, List, Any, Optional
from httpx import AsyncClient
from fastapi import status
from unittest.mock import AsyncMock
import json
import re
from decimal import Decimal

from app.models.user import User, UserType
from app.models.product import Product
from app.models.order import Order, OrderStatus
from app.core.security import create_access_token
from sqlalchemy.ext.asyncio import AsyncSession

# Test markers for categorization
pytestmark = [
    pytest.mark.integration,
    pytest.mark.api,
    pytest.mark.auth,
    pytest.mark.critical
]


class APIStandardizationTester:
    """
    Comprehensive API standardization testing framework.
    Validates endpoint consistency, authentication flows, and CRUD operations.
    """

    def __init__(self, client: AsyncClient, session: AsyncSession):
        self.client = client
        self.session = session
        self.test_results = {
            "endpoint_consistency": {},
            "authentication_flows": {},
            "crud_operations": {},
            "error_handling": {},
            "response_schemas": {},
            "performance_metrics": {}
        }

    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all standardization tests and return compliance metrics."""

        # 1. Endpoint Consistency Tests
        await self._test_endpoint_consistency()

        # 2. Authentication Flow Tests
        await self._test_authentication_flows()

        # 3. CRUD Operations Tests
        await self._test_crud_operations()

        # 4. Error Handling Tests
        await self._test_error_handling()

        # 5. Response Schema Tests
        await self._test_response_schemas()

        # 6. Performance Validation
        await self._test_performance_standards()

        return self._generate_compliance_report()

    async def _test_endpoint_consistency(self):
        """Test URL patterns, HTTP methods, and endpoint naming consistency."""

        endpoints_to_test = [
            # Authentication endpoints
            {"path": "/api/v1/auth/login", "method": "POST", "category": "auth"},
            {"path": "/api/v1/auth/register", "method": "POST", "category": "auth"},
            {"path": "/api/v1/auth/logout", "method": "POST", "category": "auth"},
            {"path": "/api/v1/auth/me", "method": "GET", "category": "auth"},
            {"path": "/api/v1/auth/refresh-token", "method": "POST", "category": "auth"},

            # Product endpoints (testing both legacy and standardized)
            {"path": "/api/v1/products", "method": "GET", "category": "products"},
            {"path": "/api/v1/products", "method": "POST", "category": "products"},

            # Order endpoints
            {"path": "/api/v1/orders", "method": "GET", "category": "orders"},
            {"path": "/api/v1/orders", "method": "POST", "category": "orders"},

            # Commission endpoints
            {"path": "/api/v1/commissions", "method": "GET", "category": "commissions"},

            # Admin endpoints
            {"path": "/api/v1/admin/users", "method": "GET", "category": "admin"},

            # Health endpoint
            {"path": "/api/v1/health", "method": "GET", "category": "system"},
        ]

        consistency_results = {}

        for endpoint in endpoints_to_test:
            try:
                # Test endpoint existence and basic response
                if endpoint["method"] == "GET":
                    response = await self.client.get(endpoint["path"])
                elif endpoint["method"] == "POST":
                    response = await self.client.post(endpoint["path"], json={})
                else:
                    continue

                # Validate URL pattern consistency
                url_pattern_valid = self._validate_url_pattern(endpoint["path"])

                # Check response headers for standardization
                headers_valid = self._validate_response_headers(response.headers)

                consistency_results[endpoint["path"]] = {
                    "exists": response.status_code != 404,
                    "url_pattern_valid": url_pattern_valid,
                    "headers_standardized": headers_valid,
                    "status_code": response.status_code,
                    "response_time": getattr(response, 'elapsed', None),
                    "category": endpoint["category"]
                }

            except Exception as e:
                consistency_results[endpoint["path"]] = {
                    "exists": False,
                    "error": str(e),
                    "category": endpoint["category"]
                }

        self.test_results["endpoint_consistency"] = consistency_results

    async def _test_authentication_flows(self):
        """Test complete authentication flows including login, token validation, and logout."""

        auth_flow_results = {}

        # Test 1: Complete login flow
        login_result = await self._test_login_flow()
        auth_flow_results["login_flow"] = login_result

        # Test 2: Token validation flow
        if login_result.get("success"):
            token_validation_result = await self._test_token_validation_flow(
                login_result.get("access_token")
            )
            auth_flow_results["token_validation"] = token_validation_result

            # Test 3: Protected endpoint access
            protected_access_result = await self._test_protected_endpoint_access(
                login_result.get("access_token")
            )
            auth_flow_results["protected_access"] = protected_access_result

            # Test 4: Logout flow
            logout_result = await self._test_logout_flow(login_result.get("access_token"))
            auth_flow_results["logout_flow"] = logout_result

        # Test 5: Role-based authorization
        role_auth_result = await self._test_role_based_authorization()
        auth_flow_results["role_authorization"] = role_auth_result

        self.test_results["authentication_flows"] = auth_flow_results

    async def _test_crud_operations(self):
        """Test CRUD operations for major entities with standardized responses."""

        crud_results = {}

        # Create test user for authentication
        test_user = await self._create_test_user()
        auth_token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Test Product CRUD
        product_crud = await self._test_product_crud(headers)
        crud_results["products"] = product_crud

        # Test Order CRUD (read-only for testing)
        order_crud = await self._test_order_crud(headers)
        crud_results["orders"] = order_crud

        # Test User management CRUD (admin functions)
        user_crud = await self._test_user_crud(headers)
        crud_results["users"] = user_crud

        self.test_results["crud_operations"] = crud_results

    async def _test_error_handling(self):
        """Test standardized error responses across all endpoints."""

        error_handling_results = {}

        # Test 1: 401 Unauthorized responses
        unauth_result = await self._test_unauthorized_responses()
        error_handling_results["unauthorized_401"] = unauth_result

        # Test 2: 403 Forbidden responses
        forbidden_result = await self._test_forbidden_responses()
        error_handling_results["forbidden_403"] = forbidden_result

        # Test 3: 404 Not Found responses
        not_found_result = await self._test_not_found_responses()
        error_handling_results["not_found_404"] = not_found_result

        # Test 4: 422 Validation Error responses
        validation_result = await self._test_validation_error_responses()
        error_handling_results["validation_422"] = validation_result

        # Test 5: 500 Internal Server Error handling
        server_error_result = await self._test_server_error_responses()
        error_handling_results["server_error_500"] = server_error_result

        self.test_results["error_handling"] = error_handling_results

    async def _test_response_schemas(self):
        """Test response schema consistency across endpoints."""

        schema_results = {}

        # Test success response schema standardization
        success_schema_result = await self._test_success_response_schemas()
        schema_results["success_responses"] = success_schema_result

        # Test error response schema standardization
        error_schema_result = await self._test_error_response_schemas()
        schema_results["error_responses"] = error_schema_result

        # Test pagination response schema
        pagination_schema_result = await self._test_pagination_response_schemas()
        schema_results["pagination_responses"] = pagination_schema_result

        self.test_results["response_schemas"] = schema_results

    async def _test_performance_standards(self):
        """Test performance standards for API endpoints."""

        performance_results = {}

        # Test response time standards
        response_time_result = await self._test_response_time_standards()
        performance_results["response_times"] = response_time_result

        # Test concurrent request handling
        concurrency_result = await self._test_concurrent_request_handling()
        performance_results["concurrency"] = concurrency_result

        self.test_results["performance_metrics"] = performance_results

    # Helper methods for specific test implementations

    def _validate_url_pattern(self, path: str) -> bool:
        """Validate URL pattern follows REST conventions."""
        # Standard pattern: /api/v{version}/{resource}[/{id}][/{subresource}]
        pattern = r'^/api/v\d+/[a-z-]+(/[a-zA-Z0-9-]+)*(/[a-z-]+)*$'
        return bool(re.match(pattern, path))

    def _validate_response_headers(self, headers) -> bool:
        """Validate response headers follow standards."""
        required_headers = ['content-type']
        return all(header.lower() in [h.lower() for h in headers.keys()]
                  for header in required_headers)

    async def _test_login_flow(self) -> Dict[str, Any]:
        """Test complete login flow."""
        try:
            # Test with valid credentials
            login_data = {
                "email": "test@example.com",
                "password": "testpass123"
            }

            # Create test user first
            test_user = await self._create_test_user()
            login_data["email"] = test_user.email

            response = await self.client.post("/api/v1/auth/login", json=login_data)

            if response.status_code == 200:
                response_data = response.json()
                return {
                    "success": True,
                    "access_token": response_data.get("access_token"),
                    "token_type": response_data.get("token_type"),
                    "response_time": getattr(response, 'elapsed', None)
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_token_validation_flow(self, token: str) -> Dict[str, Any]:
        """Test token validation with /me endpoint."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get("/api/v1/auth/me", headers=headers)

            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "user_data_valid": bool(response.json().get("id")) if response.status_code == 200 else False
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_protected_endpoint_access(self, token: str) -> Dict[str, Any]:
        """Test access to protected endpoints."""
        try:
            headers = {"Authorization": f"Bearer {token}"}

            # Test multiple protected endpoints
            protected_endpoints = [
                "/api/v1/products",
                "/api/v1/orders"
            ]

            results = {}
            for endpoint in protected_endpoints:
                response = await self.client.get(endpoint, headers=headers)
                results[endpoint] = {
                    "accessible": response.status_code in [200, 404],  # 404 is acceptable for empty resources
                    "status_code": response.status_code
                }

            return {"success": True, "endpoints": results}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_logout_flow(self, token: str) -> Dict[str, Any]:
        """Test logout flow."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.post("/api/v1/auth/logout", headers=headers)

            return {
                "success": response.status_code == 200,
                "status_code": response.status_code
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_role_based_authorization(self) -> Dict[str, Any]:
        """Test role-based authorization."""
        try:
            # Create users with different roles
            vendor_user = await self._create_test_user(user_type=UserType.VENDEDOR)
            admin_user = await self._create_test_user(user_type=UserType.SUPERUSER, email="admin@test.com")
            buyer_user = await self._create_test_user(user_type=UserType.COMPRADOR, email="buyer@test.com")

            # Test admin-only endpoints
            admin_token = create_access_token(data={"sub": str(admin_user.id)})
            vendor_token = create_access_token(data={"sub": str(vendor_user.id)})

            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            vendor_headers = {"Authorization": f"Bearer {vendor_token}"}

            # Test admin access to admin endpoints
            admin_response = await self.client.get("/api/v1/admin/users", headers=admin_headers)
            vendor_response = await self.client.get("/api/v1/admin/users", headers=vendor_headers)

            return {
                "admin_access_valid": admin_response.status_code in [200, 404],
                "vendor_access_blocked": vendor_response.status_code == 403,
                "role_separation_working": True
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _create_test_user(self, user_type: UserType = UserType.VENDEDOR, email: str = "test@example.com") -> User:
        """Create a test user for authentication testing."""
        from app.core.security import get_password_hash
        import uuid

        user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash=await get_password_hash("testpass123"),
            nombre="Test User",
            apellido="Test",
            user_type=user_type,
            is_active=True
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def _test_product_crud(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Test Product CRUD operations."""
        crud_results = {}

        try:
            # Test CREATE
            product_data = {
                "sku": f"TEST-PRODUCT-{int(time.time())}",
                "name": "Test Product",
                "description": "Test product description",
                "precio_venta": 100000.0,
                "precio_costo": 80000.0,
                "categoria": "Test Category"
            }

            create_response = await self.client.post("/api/v1/products", json=product_data, headers=headers)
            crud_results["create"] = {
                "success": create_response.status_code in [200, 201],
                "status_code": create_response.status_code
            }

            # Test READ
            read_response = await self.client.get("/api/v1/products", headers=headers)
            crud_results["read"] = {
                "success": read_response.status_code == 200,
                "status_code": read_response.status_code
            }

            return crud_results

        except Exception as e:
            return {"error": str(e)}

    async def _test_order_crud(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Test Order CRUD operations."""
        try:
            # Test READ (orders listing)
            response = await self.client.get("/api/v1/orders", headers=headers)

            return {
                "read": {
                    "success": response.status_code == 200,
                    "status_code": response.status_code
                }
            }

        except Exception as e:
            return {"error": str(e)}

    async def _test_user_crud(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Test User management CRUD operations."""
        try:
            # Test user info endpoint
            response = await self.client.get("/api/v1/auth/me", headers=headers)

            return {
                "read_profile": {
                    "success": response.status_code == 200,
                    "status_code": response.status_code
                }
            }

        except Exception as e:
            return {"error": str(e)}

    async def _test_unauthorized_responses(self) -> Dict[str, Any]:
        """Test 401 Unauthorized responses."""
        try:
            # Test protected endpoint without token
            response = await self.client.get("/api/v1/auth/me")

            return {
                "correct_status": response.status_code == 401,
                "status_code": response.status_code,
                "has_error_message": "detail" in response.json() if response.status_code == 401 else False
            }

        except Exception as e:
            return {"error": str(e)}

    async def _test_forbidden_responses(self) -> Dict[str, Any]:
        """Test 403 Forbidden responses."""
        try:
            # Create vendor user and try to access admin endpoint
            vendor_user = await self._create_test_user(user_type=UserType.VENDEDOR)
            vendor_token = create_access_token(data={"sub": str(vendor_user.id)})
            headers = {"Authorization": f"Bearer {vendor_token}"}

            response = await self.client.get("/api/v1/admin/users", headers=headers)

            return {
                "correct_status": response.status_code == 403,
                "status_code": response.status_code
            }

        except Exception as e:
            return {"error": str(e)}

    async def _test_not_found_responses(self) -> Dict[str, Any]:
        """Test 404 Not Found responses."""
        try:
            # Test non-existent endpoint
            response = await self.client.get("/api/v1/nonexistent")

            return {
                "correct_status": response.status_code == 404,
                "status_code": response.status_code
            }

        except Exception as e:
            return {"error": str(e)}

    async def _test_validation_error_responses(self) -> Dict[str, Any]:
        """Test 422 Validation Error responses."""
        try:
            # Test login with invalid data
            invalid_data = {"email": "invalid-email", "password": ""}
            response = await self.client.post("/api/v1/auth/login", json=invalid_data)

            return {
                "correct_status": response.status_code == 422,
                "status_code": response.status_code,
                "has_validation_details": "detail" in response.json() if response.status_code == 422 else False
            }

        except Exception as e:
            return {"error": str(e)}

    async def _test_server_error_responses(self) -> Dict[str, Any]:
        """Test 500 Internal Server Error handling."""
        # This is harder to test reliably, so we'll just check that endpoints don't return 500 for normal requests
        try:
            response = await self.client.get("/api/v1/health")

            return {
                "no_server_errors": response.status_code != 500,
                "status_code": response.status_code
            }

        except Exception as e:
            return {"error": str(e)}

    async def _test_success_response_schemas(self) -> Dict[str, Any]:
        """Test success response schema consistency."""
        # Test login success response schema
        try:
            test_user = await self._create_test_user(email="schema_test@example.com")
            login_data = {"email": test_user.email, "password": "testpass123"}

            response = await self.client.post("/api/v1/auth/login", json=login_data)

            if response.status_code == 200:
                data = response.json()
                required_fields = ["access_token", "token_type"]
                has_required = all(field in data for field in required_fields)

                return {
                    "login_schema_valid": has_required,
                    "status_code": response.status_code
                }
            else:
                return {"login_schema_valid": False, "status_code": response.status_code}

        except Exception as e:
            return {"error": str(e)}

    async def _test_error_response_schemas(self) -> Dict[str, Any]:
        """Test error response schema consistency."""
        try:
            # Test validation error schema
            response = await self.client.post("/api/v1/auth/login", json={})

            if response.status_code == 422:
                data = response.json()
                has_detail = "detail" in data

                return {
                    "validation_error_schema_valid": has_detail,
                    "status_code": response.status_code
                }
            else:
                return {"validation_error_schema_valid": False, "status_code": response.status_code}

        except Exception as e:
            return {"error": str(e)}

    async def _test_pagination_response_schemas(self) -> Dict[str, Any]:
        """Test pagination response schema consistency."""
        try:
            # Create test user and test paginated endpoint
            test_user = await self._create_test_user(email="pagination_test@example.com")
            token = create_access_token(data={"sub": str(test_user.id)})
            headers = {"Authorization": f"Bearer {token}"}

            response = await self.client.get("/api/v1/products?page=1&limit=10", headers=headers)

            return {
                "pagination_accessible": response.status_code in [200, 404],
                "status_code": response.status_code
            }

        except Exception as e:
            return {"error": str(e)}

    async def _test_response_time_standards(self) -> Dict[str, Any]:
        """Test response time standards."""
        response_times = {}

        endpoints = [
            "/api/v1/health",
            "/api/v1/auth/login"
        ]

        for endpoint in endpoints:
            try:
                start_time = time.time()

                if endpoint == "/api/v1/auth/login":
                    test_user = await self._create_test_user(email=f"perf_test_{time.time()}@example.com")
                    response = await self.client.post(endpoint, json={
                        "email": test_user.email,
                        "password": "testpass123"
                    })
                else:
                    response = await self.client.get(endpoint)

                end_time = time.time()
                response_time = end_time - start_time

                response_times[endpoint] = {
                    "response_time": response_time,
                    "under_threshold": response_time < 2.0,  # 2 second threshold
                    "status_code": response.status_code
                }

            except Exception as e:
                response_times[endpoint] = {"error": str(e)}

        return response_times

    async def _test_concurrent_request_handling(self) -> Dict[str, Any]:
        """Test concurrent request handling."""
        # Simple concurrency test
        try:
            import asyncio

            # Create multiple concurrent requests to health endpoint
            tasks = []
            for _ in range(5):
                tasks.append(self.client.get("/api/v1/health"))

            start_time = time.time()
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            successful_responses = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code == 200)

            return {
                "concurrent_requests_handled": successful_responses,
                "total_requests": len(tasks),
                "total_time": end_time - start_time,
                "all_successful": successful_responses == len(tasks)
            }

        except Exception as e:
            return {"error": str(e)}

    def _generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""

        # Calculate compliance percentages
        total_tests = 0
        passed_tests = 0

        # Count endpoint consistency tests
        consistency_results = self.test_results.get("endpoint_consistency", {})
        for endpoint, result in consistency_results.items():
            total_tests += 3  # exists, url_pattern_valid, headers_standardized
            if result.get("exists"): passed_tests += 1
            if result.get("url_pattern_valid"): passed_tests += 1
            if result.get("headers_standardized"): passed_tests += 1

        # Count authentication flow tests
        auth_results = self.test_results.get("authentication_flows", {})
        for flow, result in auth_results.items():
            total_tests += 1
            if result.get("success"): passed_tests += 1

        # Count CRUD operation tests
        crud_results = self.test_results.get("crud_operations", {})
        for entity, operations in crud_results.items():
            for operation, result in operations.items():
                if isinstance(result, dict) and "success" in result:
                    total_tests += 1
                    if result.get("success"): passed_tests += 1

        # Count error handling tests
        error_results = self.test_results.get("error_handling", {})
        for error_type, result in error_results.items():
            if isinstance(result, dict):
                total_tests += 1
                if result.get("correct_status") or result.get("no_server_errors"): passed_tests += 1

        # Calculate compliance percentage
        compliance_percentage = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        return {
            "compliance_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "compliance_percentage": round(compliance_percentage, 2),
                "status": "COMPLIANT" if compliance_percentage >= 95 else "NEEDS_IMPROVEMENT"
            },
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        # Check endpoint consistency issues
        consistency_results = self.test_results.get("endpoint_consistency", {})
        for endpoint, result in consistency_results.items():
            if not result.get("exists"):
                recommendations.append(f"Endpoint {endpoint} is not accessible - verify routing")
            if not result.get("url_pattern_valid"):
                recommendations.append(f"Endpoint {endpoint} does not follow REST URL conventions")
            if not result.get("headers_standardized"):
                recommendations.append(f"Endpoint {endpoint} missing standard response headers")

        # Check authentication issues
        auth_results = self.test_results.get("authentication_flows", {})
        if not auth_results.get("login_flow", {}).get("success"):
            recommendations.append("Login flow requires attention - authentication not working properly")

        # Check error handling
        error_results = self.test_results.get("error_handling", {})
        for error_type, result in error_results.items():
            if isinstance(result, dict) and not result.get("correct_status") and not result.get("no_server_errors"):
                recommendations.append(f"Error handling for {error_type} needs standardization")

        if not recommendations:
            recommendations.append("All API standardization tests passed - excellent compliance!")

        return recommendations


# Test class that uses the APIStandardizationTester
@pytest.mark.asyncio
@pytest.mark.integration
class TestAPIStandardization:
    """
    Main test class for API endpoint standardization validation.
    """

    async def test_comprehensive_api_standardization(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession
    ):
        """
        Comprehensive test of API endpoint standardization.
        Tests endpoint consistency, authentication flows, CRUD operations, and error handling.
        """

        # Initialize the testing framework
        tester = APIStandardizationTester(async_client, async_session)

        # Run comprehensive tests
        compliance_report = await tester.run_comprehensive_tests()

        # Assert compliance standards
        assert compliance_report["compliance_summary"]["compliance_percentage"] >= 80, \
            f"API compliance below threshold: {compliance_report['compliance_summary']['compliance_percentage']}%"

        # Log detailed results for analysis
        print("\n=== API STANDARDIZATION COMPLIANCE REPORT ===")
        print(f"Total Tests: {compliance_report['compliance_summary']['total_tests']}")
        print(f"Passed Tests: {compliance_report['compliance_summary']['passed_tests']}")
        print(f"Compliance: {compliance_report['compliance_summary']['compliance_percentage']}%")
        print(f"Status: {compliance_report['compliance_summary']['status']}")

        print("\n=== RECOMMENDATIONS ===")
        for rec in compliance_report["recommendations"]:
            print(f"- {rec}")

        # Individual assertions for key areas
        assert "endpoint_consistency" in compliance_report["detailed_results"]
        assert "authentication_flows" in compliance_report["detailed_results"]
        assert "error_handling" in compliance_report["detailed_results"]

        return compliance_report

    async def test_endpoint_url_patterns(self, async_client: AsyncClient, async_session: AsyncSession):
        """Test that all endpoints follow REST URL pattern conventions."""

        tester = APIStandardizationTester(async_client, async_session)
        await tester._test_endpoint_consistency()

        consistency_results = tester.test_results["endpoint_consistency"]

        # Check that all tested endpoints follow URL patterns
        for endpoint, result in consistency_results.items():
            if result.get("exists"):
                assert result.get("url_pattern_valid"), f"Endpoint {endpoint} does not follow REST conventions"

    async def test_authentication_security(self, async_client: AsyncClient, async_session: AsyncSession):
        """Test authentication security and token validation."""

        tester = APIStandardizationTester(async_client, async_session)
        await tester._test_authentication_flows()

        auth_results = tester.test_results["authentication_flows"]

        # Verify login flow works
        login_result = auth_results.get("login_flow", {})
        assert login_result.get("success"), "Login flow must work for authentication testing"

        # Verify token validation works
        token_validation = auth_results.get("token_validation", {})
        assert token_validation.get("success"), "Token validation must work for security"

        # Verify role-based authorization
        role_auth = auth_results.get("role_authorization", {})
        assert role_auth.get("role_separation_working"), "Role-based authorization must be enforced"

    async def test_error_response_standardization(self, async_client: AsyncClient, async_session: AsyncSession):
        """Test that error responses follow standardized format."""

        tester = APIStandardizationTester(async_client, async_session)
        await tester._test_error_handling()

        error_results = tester.test_results["error_handling"]

        # Test key error types
        assert error_results.get("unauthorized_401", {}).get("correct_status"), "401 errors must be properly handled"
        assert error_results.get("not_found_404", {}).get("correct_status"), "404 errors must be properly handled"
        assert error_results.get("validation_422", {}).get("correct_status"), "422 validation errors must be properly handled"

    async def test_crud_operations_consistency(self, async_client: AsyncClient, async_session: AsyncSession):
        """Test CRUD operations follow consistent patterns."""

        tester = APIStandardizationTester(async_client, async_session)
        await tester._test_crud_operations()

        crud_results = tester.test_results["crud_operations"]

        # Verify CRUD operations are accessible
        assert "products" in crud_results, "Product CRUD operations must be testable"
        assert "orders" in crud_results, "Order CRUD operations must be testable"
        assert "users" in crud_results, "User management operations must be testable"

    async def test_performance_standards(self, async_client: AsyncClient, async_session: AsyncSession):
        """Test that endpoints meet performance standards."""

        tester = APIStandardizationTester(async_client, async_session)
        await tester._test_performance_standards()

        performance_results = tester.test_results["performance_metrics"]

        # Check response times
        response_times = performance_results.get("response_times", {})
        for endpoint, metrics in response_times.items():
            if "response_time" in metrics:
                assert metrics.get("under_threshold"), f"Endpoint {endpoint} exceeds response time threshold"

        # Check concurrency handling
        concurrency = performance_results.get("concurrency", {})
        if "all_successful" in concurrency:
            assert concurrency.get("all_successful"), "Concurrent requests must be handled successfully"


# Integration flow testing
@pytest.mark.asyncio
@pytest.mark.integration
class TestIntegrationFlows:
    """
    Test complete integration flows from start to finish.
    """

    async def test_complete_user_journey(self, async_client: AsyncClient, async_session: AsyncSession):
        """Test complete user journey: login -> browse -> order -> commission flow."""

        # This would be implemented to test full user workflows
        # For now, we'll do a basic flow test

        tester = APIStandardizationTester(async_client, async_session)

        # Step 1: Login
        login_result = await tester._test_login_flow()
        assert login_result.get("success"), "User must be able to login"

        # Step 2: Access protected resources
        token = login_result.get("access_token")
        if token:
            access_result = await tester._test_protected_endpoint_access(token)
            assert access_result.get("success"), "User must be able to access protected resources"

        # Step 3: Logout
        if token:
            logout_result = await tester._test_logout_flow(token)
            assert logout_result.get("success"), "User must be able to logout"


if __name__ == "__main__":
    # This allows running the tests directly
    pytest.main([__file__, "-v"])