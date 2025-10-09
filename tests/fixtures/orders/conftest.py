"""
Pytest fixtures for order testing - TDD Suite Complete

This module provides comprehensive fixtures for:
- User authentication (customers, vendors, admins)
- Product data with stock
- Order creation payloads
- Database setup and teardown

Created: 2025-10-09
Squad: tdd-specialist + unit-testing-ai + integration-testing
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database import get_db
from app.models.user import User, UserType
from app.models.product import Product
from app.models.inventory import Inventory
from app.core.config import settings


# ============================================================================
# APPLICATION FIXTURE
# ============================================================================

@pytest.fixture(scope="session")
def test_app():
    """FastAPI application instance for testing."""
    return app


@pytest.fixture
def client(test_app):
    """Test client for making HTTP requests."""
    return TestClient(test_app)


# ============================================================================
# USER FIXTURES - AUTHENTICATION
# ============================================================================

@pytest.fixture
def customer_user_data() -> Dict[str, Any]:
    """Customer user data for testing."""
    return {
        "id": str(uuid4()),
        "email": "customer@test.com",
        "nombre": "Test Customer",
        "user_type": UserType.CUSTOMER,
        "is_active": True,
        "is_verified": True
    }


@pytest.fixture
def vendor_user_data() -> Dict[str, Any]:
    """Vendor user data for testing."""
    return {
        "id": str(uuid4()),
        "email": "vendor@test.com",
        "nombre": "Test Vendor",
        "user_type": UserType.VENDOR,
        "is_active": True,
        "is_verified": True
    }


@pytest.fixture
def admin_user_data() -> Dict[str, Any]:
    """Admin user data for testing."""
    return {
        "id": str(uuid4()),
        "email": "admin@test.com",
        "nombre": "Test Admin",
        "user_type": UserType.SUPERUSER,
        "is_active": True,
        "is_verified": True
    }


def create_test_jwt_token(user_data: Dict[str, Any]) -> str:
    """
    Create a test JWT token for authentication.

    Args:
        user_data: User data dictionary

    Returns:
        Encoded JWT token string
    """
    payload = {
        "sub": user_data["id"],
        "email": user_data["email"],
        "nombre": user_data.get("nombre", "Test User"),
        "user_type": user_data["user_type"].value if hasattr(user_data["user_type"], "value") else str(user_data["user_type"]),
        "is_active": user_data.get("is_active", True),
        "is_verified": user_data.get("is_verified", True),
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "jti": str(uuid4()),
        "typ": "access",
        "iss": "mestore-api",
        "aud": "mestore-client"
    }

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token


@pytest.fixture
def customer_token(customer_user_data) -> str:
    """JWT token for customer user."""
    return create_test_jwt_token(customer_user_data)


@pytest.fixture
def vendor_token(vendor_user_data) -> str:
    """JWT token for vendor user."""
    return create_test_jwt_token(vendor_user_data)


@pytest.fixture
def admin_token(admin_user_data) -> str:
    """JWT token for admin user."""
    return create_test_jwt_token(admin_user_data)


@pytest.fixture
def customer_auth_headers(customer_token) -> Dict[str, str]:
    """Authentication headers for customer."""
    return {"Authorization": f"Bearer {customer_token}"}


@pytest.fixture
def vendor_auth_headers(vendor_token) -> Dict[str, str]:
    """Authentication headers for vendor."""
    return {"Authorization": f"Bearer {vendor_token}"}


@pytest.fixture
def admin_auth_headers(admin_token) -> Dict[str, str]:
    """Authentication headers for admin."""
    return {"Authorization": f"Bearer {admin_token}"}


# ============================================================================
# PRODUCT FIXTURES
# ============================================================================

@pytest.fixture
def product_with_stock_data() -> Dict[str, Any]:
    """Product data with available stock."""
    return {
        "id": str(uuid4()),
        "name": "Test Product with Stock",
        "sku": f"TEST-{uuid4().hex[:8].upper()}",
        "precio_venta": Decimal("50000.00"),
        "categoria": "Electronics",
        "subcategoria": "Phones",
        "marca": "TestBrand",
        "descripcion": "Test product description",
        "stock": 100  # Available stock
    }


@pytest.fixture
def product_without_stock_data() -> Dict[str, Any]:
    """Product data with no available stock."""
    return {
        "id": str(uuid4()),
        "name": "Test Product No Stock",
        "sku": f"TEST-{uuid4().hex[:8].upper()}",
        "precio_venta": Decimal("75000.00"),
        "categoria": "Electronics",
        "subcategoria": "Tablets",
        "marca": "TestBrand",
        "descripcion": "Out of stock product",
        "stock": 0  # No stock
    }


@pytest.fixture
def product_without_price_data() -> Dict[str, Any]:
    """Product data without price set."""
    return {
        "id": str(uuid4()),
        "name": "Test Product No Price",
        "sku": f"TEST-{uuid4().hex[:8].upper()}",
        "precio_venta": None,  # No price
        "categoria": "Electronics",
        "subcategoria": "Accessories",
        "marca": "TestBrand",
        "descripcion": "Product without price",
        "stock": 50
    }


# ============================================================================
# ORDER PAYLOAD FIXTURES
# ============================================================================

@pytest.fixture
def valid_order_payload(product_with_stock_data) -> Dict[str, Any]:
    """Valid order creation payload."""
    return {
        "items": [
            {
                "product_id": product_with_stock_data["id"],
                "quantity": 2
            }
        ],
        "shipping_name": "Juan Pérez",
        "shipping_phone": "+57 300 1234567",
        "shipping_email": "juan@example.com",
        "shipping_address": "Calle 123 #45-67, Apto 501",
        "shipping_city": "Bucaramanga",
        "shipping_state": "Santander",
        "shipping_postal_code": "680001",
        "notes": "Entregar en la mañana"
    }


@pytest.fixture
def empty_cart_payload() -> Dict[str, Any]:
    """Order payload with empty cart."""
    return {
        "items": [],  # Empty cart
        "shipping_name": "Test User",
        "shipping_phone": "3001234567",
        "shipping_address": "Test Address",
        "shipping_city": "Bogotá",
        "shipping_state": "Cundinamarca"
    }


@pytest.fixture
def missing_shipping_info_payload(product_with_stock_data) -> Dict[str, Any]:
    """Order payload missing required shipping info."""
    return {
        "items": [
            {"product_id": product_with_stock_data["id"], "quantity": 1}
        ],
        "shipping_name": "Test User"
        # Missing: phone, address, city, state
    }


@pytest.fixture
def insufficient_stock_payload(product_with_stock_data) -> Dict[str, Any]:
    """Order payload requesting more stock than available."""
    return {
        "items": [
            {
                "product_id": product_with_stock_data["id"],
                "quantity": 99999  # Way more than available
            }
        ],
        "shipping_name": "Test User",
        "shipping_phone": "3001234567",
        "shipping_email": "test@test.com",
        "shipping_address": "Test Address 123",
        "shipping_city": "Medellín",
        "shipping_state": "Antioquia"
    }


@pytest.fixture
def invalid_product_id_payload() -> Dict[str, Any]:
    """Order payload with non-existent product."""
    return {
        "items": [
            {
                "product_id": str(uuid4()),  # Random UUID that doesn't exist
                "quantity": 1
            }
        ],
        "shipping_name": "Test User",
        "shipping_phone": "3001234567",
        "shipping_address": "Test Address",
        "shipping_city": "Cali",
        "shipping_state": "Valle del Cauca"
    }


@pytest.fixture
def multiple_items_payload(product_with_stock_data) -> Dict[str, Any]:
    """Order payload with multiple different products."""
    return {
        "items": [
            {"product_id": product_with_stock_data["id"], "quantity": 2},
            {"product_id": str(uuid4()), "quantity": 1},  # Second product
            {"product_id": str(uuid4()), "quantity": 3}   # Third product
        ],
        "shipping_name": "Test User",
        "shipping_phone": "3001234567",
        "shipping_email": "test@test.com",
        "shipping_address": "Carrera 15 #23-45",
        "shipping_city": "Cartagena",
        "shipping_state": "Bolívar",
        "shipping_postal_code": "130001"
    }


# ============================================================================
# CALCULATION FIXTURES
# ============================================================================

@pytest.fixture
def free_shipping_threshold_payload(product_with_stock_data) -> Dict[str, Any]:
    """
    Order payload that should qualify for free shipping.

    Subtotal >= 200,000 COP → Free shipping
    """
    # Need quantity that results in subtotal >= 200,000
    # If product price is 50,000, need at least 4 units
    return {
        "items": [
            {"product_id": product_with_stock_data["id"], "quantity": 5}  # 250,000 COP
        ],
        "shipping_name": "Test User",
        "shipping_phone": "3001234567",
        "shipping_address": "Test Address",
        "shipping_city": "Bogotá",
        "shipping_state": "Cundinamarca"
    }


@pytest.fixture
def standard_shipping_cost_payload(product_with_stock_data) -> Dict[str, Any]:
    """
    Order payload that should have standard shipping cost.

    Subtotal < 200,000 COP → 15,000 COP shipping
    """
    return {
        "items": [
            {"product_id": product_with_stock_data["id"], "quantity": 1}  # 50,000 COP
        ],
        "shipping_name": "Test User",
        "shipping_phone": "3001234567",
        "shipping_address": "Test Address",
        "shipping_city": "Barranquilla",
        "shipping_state": "Atlántico"
    }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

@pytest.fixture
def calculate_expected_total():
    """
    Helper function to calculate expected order total.

    Returns a function that calculates:
    - Subtotal
    - Tax (19% IVA)
    - Shipping (free if >= 200k, else 15k)
    - Total
    """
    def _calculate(subtotal: Decimal) -> Dict[str, Decimal]:
        FREE_SHIPPING_THRESHOLD = Decimal("200000.00")
        STANDARD_SHIPPING = Decimal("15000.00")
        IVA_RATE = Decimal("0.19")

        tax_amount = subtotal * IVA_RATE
        shipping_cost = Decimal("0.00") if subtotal >= FREE_SHIPPING_THRESHOLD else STANDARD_SHIPPING
        total_amount = subtotal + tax_amount + shipping_cost

        return {
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "shipping_cost": shipping_cost,
            "total_amount": total_amount
        }

    return _calculate
