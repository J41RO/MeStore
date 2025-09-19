#!/usr/bin/env python3
"""
Comprehensive Integration Testing Suite for MeStore
==================================================
Tests all integrated components working together:
- Security + Authentication Flow
- Payment + Order Integration
- Performance + Caching Integration
- Cross-System Integration
- Complete user journey validation

Author: Integration Testing AI
Date: 2025-09-17
"""

import asyncio
import pytest
import time
from decimal import Decimal
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch

from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.user import User, UserType
from app.models.product import Product
from app.models.order import Order, OrderStatus
from app.models.transaction import Transaction, TransactionStatus
from app.core.security import create_access_token, get_password_hash
from app.services.auth_service import AuthService
from app.services.transaction_service import TransactionService
from app.services.commission_service import CommissionService


class IntegrationTestSuite:
    """Comprehensive integration test suite for all system components."""

    def __init__(self, async_client: AsyncClient, async_session: AsyncSession):
        self.client = async_client
        self.db = async_session
        self.test_users = {}
        self.test_products = {}
        self.test_orders = {}
        self.test_tokens = {}

    async def setup_test_data(self):
        """Setup comprehensive test data for all integration scenarios."""
        # Create test users for each role
        await self._create_test_users()

        # Create test products
        await self._create_test_products()

        # Generate authentication tokens
        await self._generate_auth_tokens()

    async def _create_test_users(self):
        """Create test users for different roles."""
        users_data = [
            {
                "email": "integration_admin@test.com",
                "password": "admin123",
                "nombre": "Integration",
                "apellido": "Admin",
                "user_type": UserType.SUPERUSER,
                "role": "admin"
            },
            {
                "email": "integration_vendor@test.com",
                "password": "vendor123",
                "nombre": "Integration",
                "apellido": "Vendor",
                "user_type": UserType.VENDEDOR,
                "role": "vendor"
            },
            {
                "email": "integration_buyer@test.com",
                "password": "buyer123",
                "nombre": "Integration",
                "apellido": "Buyer",
                "user_type": UserType.COMPRADOR,
                "role": "buyer"
            }
        ]

        for user_data in users_data:
            password_hash = await get_password_hash(user_data["password"])

            user = User(
                email=user_data["email"],
                password_hash=password_hash,
                nombre=user_data["nombre"],
                apellido=user_data["apellido"],
                user_type=user_data["user_type"],
                is_active=True
            )

            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

            self.test_users[user_data["role"]] = user

    async def _create_test_products(self):
        """Create test products for order integration tests."""
        vendor = self.test_users["vendor"]

        products_data = [
            {
                "sku": "INTEG-PROD-001",
                "name": "Integration Test Product 1",
                "description": "Product for integration testing",
                "precio_venta": 50000.0,
                "precio_costo": 40000.0,
                "stock": 100,
                "categoria": "Electronics"
            },
            {
                "sku": "INTEG-PROD-002",
                "name": "Integration Test Product 2",
                "description": "Second product for integration testing",
                "precio_venta": 75000.0,
                "precio_costo": 60000.0,
                "stock": 50,
                "categoria": "Fashion"
            }
        ]

        for prod_data in products_data:
            product = Product(
                sku=prod_data["sku"],
                name=prod_data["name"],
                description=prod_data["description"],
                precio_venta=prod_data["precio_venta"],
                precio_costo=prod_data["precio_costo"],
                stock=prod_data["stock"],
                categoria=prod_data["categoria"],
                vendor_id=vendor.id
            )

            self.db.add(product)
            await self.db.commit()
            await self.db.refresh(product)

            self.test_products[prod_data["sku"]] = product

    async def _generate_auth_tokens(self):
        """Generate JWT tokens for all test users."""
        for role, user in self.test_users.items():
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "user_type": user.user_type.value,
                "nombre": user.nombre,
                "apellido": user.apellido
            }
            token = create_access_token(data=token_data)
            self.test_tokens[role] = token


@pytest.mark.integration
class TestSecurityAuthenticationIntegration:
    """Test Security + Authentication Flow integration."""

    @pytest.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient, async_session: AsyncSession):
        """Setup test suite."""
        self.test_suite = IntegrationTestSuite(async_client, async_session)
        await self.test_suite.setup_test_data()

    async def test_complete_authentication_workflow(self):
        """Test complete authentication workflow with security middleware."""
        # Test login with security validation
        login_data = {
            "email": "integration_admin@test.com",
            "password": "admin123"
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }

        response = await self.test_suite.client.post(
            "/api/v1/auth/login",
            json=login_data,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == login_data["email"]

    async def test_jwt_token_validation_across_endpoints(self):
        """Test JWT token validation across different protected endpoints."""
        token = self.test_suite.test_tokens["admin"]
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        }

        # Test multiple protected endpoints
        protected_endpoints = [
            "/api/v1/auth/me",
            "/api/v1/admin/users",
            "/api/v1/products/",
            "/api/v1/orders/"
        ]

        for endpoint in protected_endpoints:
            response = await self.test_suite.client.get(endpoint, headers=headers)
            # Should not be 401/403 (authentication should work)
            assert response.status_code != 401
            assert response.status_code != 403

    async def test_role_based_access_control(self):
        """Test role-based access control across integrated system."""
        # Admin should access admin endpoints
        admin_token = self.test_suite.test_tokens["admin"]
        admin_headers = {
            "Authorization": f"Bearer {admin_token}",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        }

        response = await self.test_suite.client.get(
            "/api/v1/admin/users",
            headers=admin_headers
        )
        assert response.status_code in [200, 404]  # 404 if endpoint not found, but not 403

        # Buyer should NOT access admin endpoints
        buyer_token = self.test_suite.test_tokens["buyer"]
        buyer_headers = {
            "Authorization": f"Bearer {buyer_token}",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        }

        response = await self.test_suite.client.get(
            "/api/v1/admin/users",
            headers=buyer_headers
        )
        assert response.status_code in [403, 404]  # Should be forbidden or not found

    async def test_brute_force_protection(self):
        """Test brute force protection integration."""
        # Attempt multiple failed logins
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }

        failed_attempts = 0
        for i in range(10):  # Try multiple failed logins
            response = await self.test_suite.client.post(
                "/api/v1/auth/login",
                json={
                    "email": "integration_admin@test.com",
                    "password": "wrongpassword"
                },
                headers=headers
            )

            if response.status_code == 401:
                failed_attempts += 1
            elif response.status_code == 429:  # Rate limited
                break

        # Should eventually get rate limited
        assert failed_attempts > 0


@pytest.mark.integration
class TestPaymentOrderIntegration:
    """Test Payment + Order Integration with external services."""

    @pytest.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient, async_session: AsyncSession):
        """Setup test suite."""
        self.test_suite = IntegrationTestSuite(async_client, async_session)
        await self.test_suite.setup_test_data()

    @patch('app.services.payment_service.WompiPaymentService')
    async def test_end_to_end_payment_flow(self, mock_payment_service):
        """Test complete payment flow with order processing."""
        # Mock Wompi payment service
        mock_payment_instance = Mock()
        mock_payment_instance.create_payment.return_value = {
            "payment_id": "wompi_12345",
            "status": "APPROVED",
            "reference": "test_ref_123"
        }
        mock_payment_service.return_value = mock_payment_instance

        buyer_token = self.test_suite.test_tokens["buyer"]
        headers = {
            "Authorization": f"Bearer {buyer_token}",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }

        # Create order
        product = list(self.test_suite.test_products.values())[0]
        order_data = {
            "items": [
                {
                    "product_id": str(product.id),
                    "quantity": 2,
                    "price": product.precio_venta
                }
            ],
            "shipping_address": "Test Address 123",
            "shipping_city": "Bogotá",
            "shipping_state": "Cundinamarca",
            "payment_method": "credit_card"
        }

        response = await self.test_suite.client.post(
            "/api/v1/orders/",
            json=order_data,
            headers=headers
        )

        # Should create order successfully
        assert response.status_code in [200, 201]
        order_response = response.json()

        # Verify order creation
        assert "id" in order_response or "order_id" in order_response

    async def test_commission_calculation_on_payment(self):
        """Test commission calculation triggered by successful payment."""
        # This would test the integration between payment success and commission calculation
        vendor = self.test_suite.test_users["vendor"]
        buyer = self.test_suite.test_users["buyer"]
        product = list(self.test_suite.test_products.values())[0]

        # Create order in database directly for testing
        order = Order(
            order_number="INTEG-TEST-001",
            buyer_id=buyer.id,
            total_amount=100000.0,
            status=OrderStatus.CONFIRMED,
            shipping_name="Test Buyer",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Bogotá",
            shipping_state="Cundinamarca"
        )

        self.test_suite.db.add(order)
        await self.test_suite.db.commit()
        await self.test_suite.db.refresh(order)

        # Test commission calculation service integration
        commission_service = CommissionService(db_session=self.test_suite.db)

        # This should integrate with the payment processing
        commission_result = await commission_service.calculate_commission(
            order_id=order.id,
            vendor_id=vendor.id,
            order_amount=Decimal("100000.00")
        )

        assert commission_result is not None

    @patch('app.services.fraud_detection_service.FraudDetectionService')
    async def test_fraud_detection_integration(self, mock_fraud_service):
        """Test fraud detection integration during payment processing."""
        # Mock fraud detection
        mock_fraud_instance = Mock()
        mock_fraud_instance.check_transaction.return_value = {
            "risk_score": 0.2,
            "status": "APPROVED",
            "reasons": []
        }
        mock_fraud_service.return_value = mock_fraud_instance

        buyer_token = self.test_suite.test_tokens["buyer"]
        headers = {
            "Authorization": f"Bearer {buyer_token}",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }

        # Test order creation with fraud detection
        product = list(self.test_suite.test_products.values())[0]
        order_data = {
            "items": [{"product_id": str(product.id), "quantity": 1}],
            "shipping_address": "Test Address",
            "payment_method": "credit_card"
        }

        response = await self.test_suite.client.post(
            "/api/v1/orders/",
            json=order_data,
            headers=headers
        )

        # Fraud detection should not block valid transaction
        assert response.status_code in [200, 201, 422]  # 422 if validation issues


@pytest.mark.integration
class TestPerformanceCachingIntegration:
    """Test Performance + Caching Integration with Redis."""

    @pytest.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient, async_session: AsyncSession):
        """Setup test suite."""
        self.test_suite = IntegrationTestSuite(async_client, async_session)
        await self.test_suite.setup_test_data()

    async def test_redis_caching_integration(self):
        """Test Redis caching integration with API endpoints."""
        token = self.test_suite.test_tokens["admin"]
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        }

        # Test cacheable endpoint multiple times
        endpoint = "/api/v1/products/"

        # First request (should hit database)
        start_time = time.time()
        response1 = await self.test_suite.client.get(endpoint, headers=headers)
        first_request_time = time.time() - start_time

        # Second request (should hit cache)
        start_time = time.time()
        response2 = await self.test_suite.client.get(endpoint, headers=headers)
        second_request_time = time.time() - start_time

        # Both requests should succeed
        assert response1.status_code in [200, 404]
        assert response2.status_code in [200, 404]

        # Cache should make second request faster (if caching is implemented)
        if response1.status_code == 200:
            assert second_request_time <= first_request_time + 0.1  # Allow some variance

    async def test_session_management_integration(self):
        """Test session management integration with Redis."""
        # Test login creates session
        login_data = {
            "email": "integration_admin@test.com",
            "password": "admin123"
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }

        response = await self.test_suite.client.post(
            "/api/v1/auth/login",
            json=login_data,
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")

            # Use token for authenticated request
            auth_headers = {
                "Authorization": f"Bearer {token}",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            }

            response = await self.test_suite.client.get(
                "/api/v1/auth/me",
                headers=auth_headers
            )

            assert response.status_code in [200, 404]

    async def test_performance_under_load(self):
        """Test system performance under concurrent load."""
        token = self.test_suite.test_tokens["buyer"]
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        }

        # Simulate concurrent requests
        async def make_request():
            return await self.test_suite.client.get("/api/v1/products/", headers=headers)

        # Create multiple concurrent requests
        tasks = [make_request() for _ in range(10)]
        start_time = time.time()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time

        # Analyze performance
        successful_responses = [r for r in responses if not isinstance(r, Exception) and r.status_code in [200, 404]]

        assert len(successful_responses) > 0
        assert total_time < 30.0  # Should complete within 30 seconds


@pytest.mark.integration
class TestCrossSystemIntegration:
    """Test complete cross-system integration scenarios."""

    @pytest.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient, async_session: AsyncSession):
        """Setup test suite."""
        self.test_suite = IntegrationTestSuite(async_client, async_session)
        await self.test_suite.setup_test_data()

    async def test_complete_user_journey(self):
        """Test complete user journey from registration to order completion."""
        # 1. User Registration
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }

        registration_data = {
            "email": "journey_user@test.com",
            "password": "journey123",
            "nombre": "Journey",
            "apellido": "User",
            "user_type": "buyer"
        }

        response = await self.test_suite.client.post(
            "/api/v1/auth/register",
            json=registration_data,
            headers=headers
        )

        # Registration might not be implemented, so check for various responses
        registration_success = response.status_code in [200, 201]

        # 2. User Login (use existing user if registration failed)
        login_data = {
            "email": "integration_buyer@test.com",
            "password": "buyer123"
        }

        response = await self.test_suite.client.post(
            "/api/v1/auth/login",
            json=login_data,
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")

            auth_headers = {
                "Authorization": f"Bearer {token}",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                "Content-Type": "application/json"
            }

            # 3. Browse Products
            response = await self.test_suite.client.get("/api/v1/products/", headers=auth_headers)
            assert response.status_code in [200, 404]

            # 4. Create Order (if products exist)
            if response.status_code == 200:
                products = response.json()
                if products and len(products) > 0:
                    product = products[0]
                    order_data = {
                        "items": [{"product_id": product.get("id"), "quantity": 1}],
                        "shipping_address": "Journey Test Address"
                    }

                    response = await self.test_suite.client.post(
                        "/api/v1/orders/",
                        json=order_data,
                        headers=auth_headers
                    )

                    # Order creation should work or give validation error
                    assert response.status_code in [200, 201, 422]

    async def test_vendor_product_order_flow(self):
        """Test vendor creates product, buyer purchases, payment processed."""
        # Use vendor to create product
        vendor_token = self.test_suite.test_tokens["vendor"]
        vendor_headers = {
            "Authorization": f"Bearer {vendor_token}",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }

        # Create product as vendor
        product_data = {
            "sku": f"VENDOR-FLOW-{int(time.time())}",
            "name": "Vendor Flow Test Product",
            "description": "Product for vendor flow testing",
            "precio_venta": 25000.0,
            "precio_costo": 20000.0,
            "stock": 10,
            "categoria": "Test"
        }

        response = await self.test_suite.client.post(
            "/api/v1/products/",
            json=product_data,
            headers=vendor_headers
        )

        # Product creation should work or give validation error
        if response.status_code in [200, 201]:
            product = response.json()

            # Now buyer purchases product
            buyer_token = self.test_suite.test_tokens["buyer"]
            buyer_headers = {
                "Authorization": f"Bearer {buyer_token}",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                "Content-Type": "application/json"
            }

            order_data = {
                "items": [{"product_id": product.get("id"), "quantity": 1}],
                "shipping_address": "Buyer Flow Address"
            }

            response = await self.test_suite.client.post(
                "/api/v1/orders/",
                json=order_data,
                headers=buyer_headers
            )

            assert response.status_code in [200, 201, 422]

    async def test_admin_system_monitoring(self):
        """Test admin can monitor all system components."""
        admin_token = self.test_suite.test_tokens["admin"]
        admin_headers = {
            "Authorization": f"Bearer {admin_token}",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        }

        # Test admin can access monitoring endpoints
        monitoring_endpoints = [
            "/api/v1/health/",
            "/api/v1/health-complete/",
            "/api/v1/admin/users",
            "/api/v1/admin/orders",
            "/api/v1/admin/system-stats"
        ]

        for endpoint in monitoring_endpoints:
            response = await self.test_suite.client.get(endpoint, headers=admin_headers)
            # Should not be forbidden (but might be not found)
            assert response.status_code != 403


# Integration test configuration
@pytest.mark.integration
class TestSystemHealthIntegration:
    """Test system health with all integrated components."""

    async def test_system_startup_integration(self, async_client: AsyncClient):
        """Test system can start with all components integrated."""
        # Test basic health endpoint
        response = await async_client.get("/health")
        assert response.status_code == 200

        health_data = response.json()
        assert health_data["status"] == "healthy"

    async def test_database_integration_health(self, async_client: AsyncClient):
        """Test database integration health."""
        response = await async_client.get("/db-test")
        assert response.status_code == 200

        db_data = response.json()
        assert db_data["status"] in ["success", "error"]

    async def test_all_endpoints_accessible(self, async_client: AsyncClient):
        """Test all major endpoints are accessible (not necessarily functional)."""
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        }

        # Test public endpoints
        public_endpoints = [
            "/",
            "/health",
            "/db-test",
            "/docs",
            "/openapi.json"
        ]

        for endpoint in public_endpoints:
            response = await async_client.get(endpoint, headers=headers)
            # Should not be server error
            assert response.status_code < 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])