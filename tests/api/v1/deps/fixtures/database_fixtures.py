"""
Database Testing Fixtures for TDD

Comprehensive fixtures for database dependency testing following TDD patterns.
These fixtures support RED-GREEN-REFACTOR methodology with proper isolation.

Author: TDD Specialist AI
Date: 2025-09-21
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import AsyncGenerator, Dict, Any, Optional

from app.models.user import User, UserType
from app.models.product import Product
from app.models.order import Order


@pytest.fixture
async def mock_async_session() -> AsyncMock:
    """
    Mock AsyncSession for database dependency testing.

    Returns:
        AsyncMock: Configured mock session with standard methods
    """
    session = AsyncMock(spec=AsyncSession)

    # Configure standard session methods
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.begin = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.get = AsyncMock()

    # Configure context manager behavior
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)

    return session


@pytest.fixture
def mock_user_entity() -> User:
    """
    Mock User entity for get_user_or_404 testing.

    Returns:
        User: Mock user with realistic data
    """
    user_id = uuid.uuid4()
    return User(
        id=user_id,
        email="test@example.com",
        nombre="Test",
        apellido="User",
        user_type=UserType.BUYER,
        is_active=True,
        is_verified=False,
        documento_identidad="12345678",
        telefono="123456789"
    )


@pytest.fixture
def mock_product_entity() -> Product:
    """
    Mock Product entity with soft-delete support.

    Returns:
        Product: Mock product with realistic data
    """
    product_id = uuid.uuid4()
    vendor_id = uuid.uuid4()

    return Product(
        id=product_id,
        nombre="Test Product",
        descripcion="Test product description",
        precio=99.99,
        categoria="electronics",
        vendor_id=vendor_id,
        stock=10,
        deleted_at=None  # Not soft-deleted
    )


@pytest.fixture
def mock_soft_deleted_product() -> Product:
    """
    Mock soft-deleted Product entity.

    Returns:
        Product: Mock product that is soft-deleted
    """
    from datetime import datetime

    product_id = uuid.uuid4()
    vendor_id = uuid.uuid4()

    return Product(
        id=product_id,
        nombre="Deleted Product",
        descripcion="This product was deleted",
        precio=99.99,
        categoria="electronics",
        vendor_id=vendor_id,
        stock=0,
        deleted_at=datetime.now()  # Soft-deleted
    )


@pytest.fixture
def mock_order_entity() -> Order:
    """
    Mock Order entity for get_order_or_404 testing.

    Returns:
        Order: Mock order with realistic data
    """
    order_id = uuid.uuid4()
    buyer_id = uuid.uuid4()

    return Order(
        id=order_id,
        buyer_id=buyer_id,
        total=199.98,
        status="pending",
        items=[]
    )


@pytest.fixture
def mock_commission_entity() -> Dict[str, Any]:
    """
    Mock Commission entity for get_commission_or_404 testing.

    Returns:
        Dict: Mock commission data
    """
    commission_id = uuid.uuid4()
    vendor_id = uuid.uuid4()
    order_id = uuid.uuid4()

    return {
        "id": commission_id,
        "vendor_id": vendor_id,
        "order_id": order_id,
        "amount": 19.99,
        "rate": 0.10,
        "status": "pending"
    }


@pytest.fixture
async def mock_session_with_rollback() -> AsyncMock:
    """
    Mock session that simulates rollback on exception.

    Returns:
        AsyncMock: Session configured to test rollback behavior
    """
    session = await mock_async_session()

    # Configure rollback to be called on exception
    session.execute.side_effect = SQLAlchemyError("Test database error")

    return session


@pytest.fixture
def mock_session_factory() -> callable:
    """
    Factory for creating mock sessions with different configurations.

    Returns:
        callable: Factory function for creating configured sessions
    """
    async def create_session(
        has_data: bool = True,
        raises_exception: bool = False,
        exception_type: type = SQLAlchemyError,
        return_value: Any = None
    ) -> AsyncMock:
        """
        Create configured mock session.

        Args:
            has_data: Whether session should return data
            raises_exception: Whether session should raise exception
            exception_type: Type of exception to raise
            return_value: Value to return from queries

        Returns:
            AsyncMock: Configured session
        """
        session = AsyncMock(spec=AsyncSession)

        if raises_exception:
            session.execute.side_effect = exception_type("Test error")
        elif has_data:
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = return_value
            session.execute.return_value = mock_result
        else:
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            session.execute.return_value = mock_result

        # Configure standard methods
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.close = AsyncMock()

        return session

    return create_session


@pytest.fixture
def entity_test_data() -> Dict[str, Dict[str, Any]]:
    """
    Test data for all entity types.

    Returns:
        Dict: Complete test data for all entities
    """
    return {
        "user": {
            "valid_id": str(uuid.uuid4()),
            "invalid_ids": [
                "invalid-uuid",
                "12345",
                "",
                None,
                "not-a-uuid",
                "123e4567-e89b-12d3-a456-42661417400"  # Missing character
            ],
            "malicious_ids": [
                "'; DROP TABLE users; --",
                "1' OR '1'='1",
                "../../../etc/passwd",
                "<script>alert('xss')</script>",
                "../../admin/users"
            ]
        },
        "product": {
            "valid_id": str(uuid.uuid4()),
            "soft_deleted_filter_required": True,
            "invalid_ids": [
                "invalid-product-uuid",
                "0",
                "null",
                "undefined"
            ]
        },
        "order": {
            "valid_id": str(uuid.uuid4()),
            "invalid_ids": [
                "invalid-order-uuid",
                "fake-order-id"
            ]
        },
        "commission": {
            "valid_id": str(uuid.uuid4()),
            "invalid_ids": [
                "invalid-commission-uuid",
                "fake-commission-id"
            ]
        }
    }


@pytest.fixture
def database_error_scenarios() -> list:
    """
    Database error scenarios for testing error handling.

    Returns:
        list: Error scenarios with expected behavior
    """
    return [
        {
            "error": SQLAlchemyError("Connection timeout"),
            "expected_status": 500,
            "should_rollback": True
        },
        {
            "error": ValueError("Invalid UUID format"),
            "expected_status": 400,
            "should_rollback": False
        },
        {
            "error": Exception("Unexpected database error"),
            "expected_status": 500,
            "should_rollback": True
        }
    ]


@pytest.fixture
async def isolated_test_session() -> AsyncGenerator[AsyncMock, None]:
    """
    Isolated test session with proper cleanup.

    Yields:
        AsyncMock: Isolated session for testing
    """
    session = await mock_async_session()

    try:
        yield session
    finally:
        # Ensure proper cleanup
        await session.rollback()
        await session.close()


@pytest.fixture
def performance_test_config() -> Dict[str, Any]:
    """
    Configuration for performance testing.

    Returns:
        Dict: Performance test configuration
    """
    return {
        "max_response_time": 0.01,  # 10ms
        "concurrent_requests": 100,
        "timeout_threshold": 0.1,   # 100ms
        "memory_limit_mb": 50
    }


@pytest.fixture
def tdd_test_markers() -> Dict[str, str]:
    """
    TDD test phase markers for organizing tests.

    Returns:
        Dict: Mapping of TDD phases to pytest markers
    """
    return {
        "red": "red_test",
        "green": "green_test",
        "refactor": "refactor_test",
        "security": "security",
        "performance": "performance",
        "integration": "integration"
    }