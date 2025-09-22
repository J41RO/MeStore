"""
Comprehensive Test Fixtures for TDD
==================================

This module provides comprehensive test fixtures for the MeStore project
following TDD methodology with complete business scenario coverage.

Author: TDD Specialist AI
Date: 2025-09-17
Purpose: Provide reusable test fixtures for all business domains
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User, UserType
from app.models.product import Product
from app.models.order import Order, OrderStatus
from tests.database_fixtures import test_data_factory


class BusinessScenarioFixtures:
    """
    Comprehensive business scenario fixtures for TDD testing.

    Provides pre-configured business scenarios that represent
    real-world usage patterns in the MeStore platform.
    """

    @pytest.fixture(scope="function")
    def complete_vendor_scenario(self, test_data_factory):
        """
        Complete vendor business scenario.

        Creates a vendor with products, orders, and transactions
        representing a typical vendor lifecycle.
        """
        # Create vendor user
        vendor = test_data_factory.create_test_user(
            user_type="VENDOR",
            email="vendor@testscenario.com",
            nombre="Juan Carlos",
            apellido="Vendedor"
        )

        # Create product catalog for vendor
        products = []
        for i in range(3):
            product = test_data_factory.create_test_product(
                vendor_id=vendor.id,
                name=f"Producto {i+1}",
                precio_venta=50000.0 + (i * 10000),
                stock=20 - (i * 5)
            )
            products.append(product)

        # Create buyers and orders
        buyers = []
        orders = []
        for i in range(2):
            buyer = test_data_factory.create_test_user(
                user_type="BUYER",
                email=f"buyer{i+1}@testscenario.com"
            )
            buyers.append(buyer)

            # Create order for this buyer
            order = test_data_factory.create_test_order(
                buyer_id=buyer.id,
                total_amount=75000.0 + (i * 25000),
                status=OrderStatus.CONFIRMED if i == 0 else OrderStatus.PENDING
            )
            orders.append(order)

        return {
            "vendor": vendor,
            "products": products,
            "buyers": buyers,
            "orders": orders,
            "scenario_type": "complete_vendor_operation"
        }

    @pytest.fixture(scope="function")
    def multi_vendor_marketplace_scenario(self, test_data_factory):
        """
        Multi-vendor marketplace scenario.

        Creates multiple vendors with competing products
        to test marketplace dynamics.
        """
        # Create multiple vendors
        vendors = []
        for i in range(3):
            vendor = test_data_factory.create_test_user(
                user_type="VENDOR",
                email=f"vendor{i+1}@marketplace.com",
                nombre=f"Vendor {i+1}",
                apellido="Business"
            )
            vendors.append(vendor)

        # Create competing products
        product_categories = ["Electronics", "Clothing", "Home"]
        all_products = []

        for vendor in vendors:
            vendor_products = []
            for j, category in enumerate(product_categories):
                product = test_data_factory.create_test_product(
                    vendor_id=vendor.id,
                    name=f"{category} Product by {vendor.nombre}",
                    precio_venta=100000.0 + (j * 20000),
                    categoria=category,
                    stock=15
                )
                vendor_products.append(product)
            all_products.append(vendor_products)

        # Create buyers with varied purchasing patterns
        buyers = []
        orders = []
        for i in range(5):
            buyer = test_data_factory.create_test_user(
                user_type="BUYER",
                email=f"buyer{i+1}@marketplace.com"
            )
            buyers.append(buyer)

            # Create orders from different vendors
            order = test_data_factory.create_test_order(
                buyer_id=buyer.id,
                total_amount=150000.0 + (i * 10000),
                status=OrderStatus.CONFIRMED
            )
            orders.append(order)

        return {
            "vendors": vendors,
            "products": all_products,
            "buyers": buyers,
            "orders": orders,
            "scenario_type": "multi_vendor_marketplace"
        }

    @pytest.fixture(scope="function")
    def high_volume_scenario(self, test_data_factory):
        """
        High volume business scenario for performance testing.

        Creates a large number of entities to test system
        performance under load.
        """
        # Create admin user
        admin = test_data_factory.create_test_user(
            user_type="SUPERUSER",
            email="admin@highvolume.com"
        )

        # Create multiple vendors
        vendors = []
        for i in range(10):
            vendor = test_data_factory.create_test_user(
                user_type="VENDOR",
                email=f"vendor{i+1}@highvolume.com"
            )
            vendors.append(vendor)

        # Create large product catalog
        products = []
        for vendor in vendors:
            for j in range(5):  # 5 products per vendor = 50 total
                product = test_data_factory.create_test_product(
                    vendor_id=vendor.id,
                    name=f"Product {j+1} by Vendor {vendor.email}",
                    precio_venta=25000.0 + (j * 5000),
                    stock=100
                )
                products.append(product)

        # Create many buyers
        buyers = []
        for i in range(25):
            buyer = test_data_factory.create_test_user(
                user_type="BUYER",
                email=f"buyer{i+1}@highvolume.com"
            )
            buyers.append(buyer)

        return {
            "admin": admin,
            "vendors": vendors,
            "products": products,
            "buyers": buyers,
            "scenario_type": "high_volume_performance"
        }


class AuthenticationFixtures:
    """Authentication and authorization test fixtures."""

    @pytest.fixture(scope="function")
    async def authenticated_users(self, isolated_async_session: AsyncSession):
        """Create authenticated users for all roles."""
        from app.core.security import get_password_hash

        users = {}
        user_types = ["SUPERUSER", "VENDOR", "BUYER"]

        for user_type in user_types:
            user = User(
                id=uuid.uuid4(),
                email=f"auth_{user_type.lower()}@test.com",
                password_hash=await get_password_hash("testpass123"),
                nombre=f"Auth {user_type}",
                apellido="User",
                user_type=UserType[user_type],
                is_active=True
            )

            isolated_async_session.add(user)
            users[user_type.lower()] = user

        await isolated_async_session.commit()
        for user in users.values():
            await isolated_async_session.refresh(user)

        return users

    @pytest.fixture(scope="function")
    def auth_tokens(self, authenticated_users):
        """Generate JWT tokens for authenticated users."""
        from app.core.security import create_access_token

        tokens = {}
        for role, user in authenticated_users.items():
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "user_type": user.user_type.value,
                "nombre": user.nombre,
                "apellido": user.apellido
            }
            tokens[role] = create_access_token(data=token_data)

        return tokens

    @pytest.fixture(scope="function")
    def auth_headers(self, auth_tokens):
        """Generate authorization headers for API testing."""
        headers = {}
        for role, token in auth_tokens.items():
            headers[role] = {"Authorization": f"Bearer {token}"}

        return headers


class ProductInventoryFixtures:
    """Product and inventory management test fixtures."""

    @pytest.fixture(scope="function")
    def product_catalog_scenario(self, test_data_factory):
        """Complete product catalog with various scenarios."""
        vendor = test_data_factory.create_test_user("VENDOR")

        # Create products with different conditions
        products = {
            "active_product": test_data_factory.create_test_product(
                vendor_id=vendor.id,
                name="Active Product",
                stock=50,
                is_active=True
            ),
            "low_stock_product": test_data_factory.create_test_product(
                vendor_id=vendor.id,
                name="Low Stock Product",
                stock=2,
                is_active=True
            ),
            "out_of_stock_product": test_data_factory.create_test_product(
                vendor_id=vendor.id,
                name="Out of Stock Product",
                stock=0,
                is_active=True
            ),
            "inactive_product": test_data_factory.create_test_product(
                vendor_id=vendor.id,
                name="Inactive Product",
                stock=10,
                is_active=False
            ),
            "premium_product": test_data_factory.create_test_product(
                vendor_id=vendor.id,
                name="Premium Product",
                precio_venta=500000.0,
                stock=5,
                is_active=True
            )
        }

        return {
            "vendor": vendor,
            "products": products,
            "scenario_type": "product_catalog"
        }

    @pytest.fixture(scope="function")
    def inventory_update_scenario(self, test_data_factory):
        """Scenario for testing inventory updates and constraints."""
        vendor = test_data_factory.create_test_user("VENDOR")

        # Create products that will be updated
        products = []
        for i in range(5):
            product = test_data_factory.create_test_product(
                vendor_id=vendor.id,
                name=f"Inventory Product {i+1}",
                stock=10 + i,
                precio_venta=25000.0 + (i * 5000)
            )
            products.append(product)

        # Prepare update scenarios
        update_scenarios = [
            {"product_index": 0, "new_stock": 15, "expected_result": "success"},
            {"product_index": 1, "new_stock": 0, "expected_result": "success"},
            {"product_index": 2, "new_stock": -5, "expected_result": "error"},
            {"product_index": 3, "new_stock": 1000, "expected_result": "success"},
            {"product_index": 4, "new_stock": 1, "expected_result": "success"}
        ]

        return {
            "vendor": vendor,
            "products": products,
            "update_scenarios": update_scenarios,
            "scenario_type": "inventory_update"
        }


class OrderProcessingFixtures:
    """Order processing and workflow test fixtures."""

    @pytest.fixture(scope="function")
    def order_lifecycle_scenario(self, test_data_factory):
        """Complete order lifecycle from creation to completion."""
        # Create participants
        vendor = test_data_factory.create_test_user("VENDOR")
        buyer = test_data_factory.create_test_user("BUYER")
        admin = test_data_factory.create_test_user("SUPERUSER")

        # Create products for the order
        products = []
        for i in range(3):
            product = test_data_factory.create_test_product(
                vendor_id=vendor.id,
                name=f"Order Product {i+1}",
                precio_venta=50000.0 + (i * 10000),
                stock=20
            )
            products.append(product)

        # Create orders in different stages
        orders = {
            "pending_order": test_data_factory.create_test_order(
                buyer_id=buyer.id,
                total_amount=150000.0,
                status=OrderStatus.PENDING
            ),
            "confirmed_order": test_data_factory.create_test_order(
                buyer_id=buyer.id,
                total_amount=200000.0,
                status=OrderStatus.CONFIRMED
            ),
            "shipped_order": test_data_factory.create_test_order(
                buyer_id=buyer.id,
                total_amount=100000.0,
                status=OrderStatus.SHIPPED
            )
        }

        # Define status transitions to test
        status_transitions = [
            {"from": OrderStatus.PENDING, "to": OrderStatus.CONFIRMED, "valid": True},
            {"from": OrderStatus.CONFIRMED, "to": OrderStatus.PROCESSING, "valid": True},
            {"from": OrderStatus.PROCESSING, "to": OrderStatus.SHIPPED, "valid": True},
            {"from": OrderStatus.SHIPPED, "to": OrderStatus.DELIVERED, "valid": True},
            {"from": OrderStatus.DELIVERED, "to": OrderStatus.PENDING, "valid": False},
            {"from": OrderStatus.CANCELLED, "to": OrderStatus.CONFIRMED, "valid": False}
        ]

        return {
            "vendor": vendor,
            "buyer": buyer,
            "admin": admin,
            "products": products,
            "orders": orders,
            "status_transitions": status_transitions,
            "scenario_type": "order_lifecycle"
        }

    @pytest.fixture(scope="function")
    def order_validation_scenario(self, test_data_factory):
        """Scenario for testing order validation and edge cases."""
        vendor = test_data_factory.create_test_user("VENDOR")
        buyer = test_data_factory.create_test_user("BUYER")

        # Create products with different constraints
        in_stock_product = test_data_factory.create_test_product(
            vendor_id=vendor.id,
            name="In Stock Product",
            stock=10,
            precio_venta=50000.0
        )

        out_of_stock_product = test_data_factory.create_test_product(
            vendor_id=vendor.id,
            name="Out of Stock Product",
            stock=0,
            precio_venta=75000.0
        )

        # Define order validation scenarios
        validation_scenarios = [
            {
                "name": "valid_order",
                "buyer_id": buyer.id,
                "total_amount": 50000.0,
                "expected_result": "success"
            },
            {
                "name": "invalid_amount",
                "buyer_id": buyer.id,
                "total_amount": -1000.0,
                "expected_result": "error"
            },
            {
                "name": "missing_buyer",
                "buyer_id": None,
                "total_amount": 50000.0,
                "expected_result": "error"
            },
            {
                "name": "zero_amount",
                "buyer_id": buyer.id,
                "total_amount": 0.0,
                "expected_result": "error"
            }
        ]

        return {
            "vendor": vendor,
            "buyer": buyer,
            "in_stock_product": in_stock_product,
            "out_of_stock_product": out_of_stock_product,
            "validation_scenarios": validation_scenarios,
            "scenario_type": "order_validation"
        }


class FinancialTestFixtures:
    """Financial operations test fixtures including commissions."""

    @pytest.fixture(scope="function")
    def commission_calculation_scenario(self, test_data_factory):
        """Scenario for testing commission calculations."""
        vendors = []
        orders = []

        # Create vendors with different commission rates
        commission_rates = [0.05, 0.08, 0.10, 0.12]  # 5%, 8%, 10%, 12%

        for i, rate in enumerate(commission_rates):
            vendor = test_data_factory.create_test_user(
                user_type="VENDOR",
                email=f"vendor{i+1}@commission.com"
            )
            vendors.append(vendor)

            # Create buyer for this vendor's order
            buyer = test_data_factory.create_test_user(
                user_type="BUYER",
                email=f"buyer{i+1}@commission.com"
            )

            # Create order for commission calculation
            order = test_data_factory.create_test_order(
                buyer_id=buyer.id,
                total_amount=100000.0 * (i + 1),  # Different amounts
                status=OrderStatus.CONFIRMED
            )
            orders.append(order)

        # Define commission test scenarios
        commission_scenarios = [
            {
                "order_amount": 100000.0,
                "commission_rate": 0.05,
                "expected_commission": 5000.0,
                "test_type": "standard_commission"
            },
            {
                "order_amount": 250000.0,
                "commission_rate": 0.08,
                "expected_commission": 20000.0,
                "test_type": "medium_order_commission"
            },
            {
                "order_amount": 500000.0,
                "commission_rate": 0.10,
                "expected_commission": 50000.0,
                "test_type": "large_order_commission"
            },
            {
                "order_amount": 1000000.0,
                "commission_rate": 0.12,
                "expected_commission": 120000.0,
                "test_type": "premium_order_commission"
            }
        ]

        return {
            "vendors": vendors,
            "orders": orders,
            "commission_scenarios": commission_scenarios,
            "scenario_type": "commission_calculation"
        }

    @pytest.fixture(scope="function")
    def payment_processing_scenario(self, test_data_factory):
        """Scenario for testing payment processing workflows."""
        buyer = test_data_factory.create_test_user("BUYER")
        vendor = test_data_factory.create_test_user("VENDOR")

        # Create orders for different payment scenarios
        payment_orders = {
            "successful_payment": test_data_factory.create_test_order(
                buyer_id=buyer.id,
                total_amount=150000.0,
                status=OrderStatus.PENDING
            ),
            "failed_payment": test_data_factory.create_test_order(
                buyer_id=buyer.id,
                total_amount=200000.0,
                status=OrderStatus.PENDING
            ),
            "partial_payment": test_data_factory.create_test_order(
                buyer_id=buyer.id,
                total_amount=300000.0,
                status=OrderStatus.PENDING
            )
        }

        # Define payment scenarios
        payment_scenarios = [
            {
                "payment_method": "credit_card",
                "amount": 150000.0,
                "expected_result": "success",
                "expected_status": OrderStatus.CONFIRMED
            },
            {
                "payment_method": "credit_card",
                "amount": 200000.0,
                "expected_result": "failure",
                "expected_status": OrderStatus.CANCELLED
            },
            {
                "payment_method": "bank_transfer",
                "amount": 300000.0,
                "expected_result": "pending",
                "expected_status": OrderStatus.PENDING
            }
        ]

        return {
            "buyer": buyer,
            "vendor": vendor,
            "orders": payment_orders,
            "payment_scenarios": payment_scenarios,
            "scenario_type": "payment_processing"
        }


# Performance Testing Fixtures

@pytest.fixture(scope="function")
def performance_baseline_data(test_data_factory):
    """Create baseline data for performance testing."""
    # Create consistent test data for performance benchmarking
    vendors = []
    products = []
    buyers = []
    orders = []

    # Create 5 vendors
    for i in range(5):
        vendor = test_data_factory.create_test_user(
            user_type="VENDOR",
            email=f"perf_vendor{i}@test.com"
        )
        vendors.append(vendor)

        # Create 10 products per vendor
        for j in range(10):
            product = test_data_factory.create_test_product(
                vendor_id=vendor.id,
                name=f"Performance Product {i}-{j}",
                precio_venta=50000.0 + (j * 1000),
                stock=20
            )
            products.append(product)

    # Create 20 buyers
    for i in range(20):
        buyer = test_data_factory.create_test_user(
            user_type="BUYER",
            email=f"perf_buyer{i}@test.com"
        )
        buyers.append(buyer)

        # Create 2 orders per buyer
        for j in range(2):
            order = test_data_factory.create_test_order(
                buyer_id=buyer.id,
                total_amount=100000.0 + (j * 25000),
                status=OrderStatus.CONFIRMED
            )
            orders.append(order)

    return {
        "vendors": vendors,
        "products": products,
        "buyers": buyers,
        "orders": orders,
        "scenario_type": "performance_baseline"
    }


# Error Handling Fixtures

@pytest.fixture(scope="function")
def error_scenario_data():
    """Data for testing error handling scenarios."""
    return {
        "invalid_emails": [
            "invalid-email",
            "test@",
            "@domain.com",
            "",
            None
        ],
        "invalid_amounts": [
            -1000.0,
            0.0,
            float('inf'),
            float('nan'),
            "not_a_number"
        ],
        "invalid_user_types": [
            "INVALID_TYPE",
            "",
            None,
            123,
            []
        ],
        "boundary_values": {
            "max_order_amount": 10000000.0,
            "min_order_amount": 1.0,
            "max_stock": 999999,
            "min_stock": 0
        }
    }


if __name__ == "__main__":
    print("Comprehensive Test Fixtures for TDD")
    print("==================================")
    print("Available fixture categories:")
    print("- BusinessScenarioFixtures: Complete business workflows")
    print("- AuthenticationFixtures: Auth and authorization scenarios")
    print("- ProductInventoryFixtures: Product and inventory management")
    print("- OrderProcessingFixtures: Order lifecycle and validation")
    print("- FinancialTestFixtures: Commission and payment processing")
    print("- Performance and error handling fixtures")