"""
Database dependency injection for FastAPI endpoints.

This module provides standardized database session dependencies
for all API endpoints, consolidating session management in a single location.
"""

from typing import AsyncGenerator, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.core.database import AsyncSessionLocal
from app.core.id_validation import IDValidator


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Standard database dependency for FastAPI endpoints.

    This is the primary dependency that should be used in all endpoints
    requiring database access. It provides proper session management
    with automatic commit/rollback handling.

    Yields:
        AsyncSession: Database session with transaction management

    Example:
        @router.get("/users/")
        async def get_users(db: AsyncSession = Depends(get_db)):
            # Use db session here
            pass
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Alias for get_db() for backwards compatibility.

    Note: Prefer using get_db() directly for new code.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Alias for get_db() for async session dependency.

    This is an alternative name for get_db() that makes it clear
    we're working with async sessions.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Database entity validation dependencies
async def get_user_or_404(user_id: str, db: AsyncSession):
    """
    Get user by ID or raise 404 if not found.

    Args:
        user_id: UUID string of the user
        db: Database session

    Returns:
        User: User object if found

    Raises:
        HTTPException: 404 if user not found
    """
    from app.models.user import User

    # Validate ID format
    validated_id = IDValidator.validate_uuid_string(user_id, "user_id")

    stmt = select(User).where(User.id == validated_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    return user


async def get_product_or_404(product_id: str, db: AsyncSession):
    """
    Get product by ID or raise 404 if not found.

    Args:
        product_id: UUID string of the product
        db: Database session

    Returns:
        Product: Product object if found

    Raises:
        HTTPException: 404 if product not found
    """
    from app.models.product import Product

    # Validate ID format
    validated_id = IDValidator.validate_uuid_string(product_id, "product_id")

    stmt = select(Product).where(
        Product.id == validated_id,
        Product.deleted_at.is_(None)  # Exclude soft-deleted products
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    return product


async def get_order_or_404(order_id: str, db: AsyncSession):
    """
    Get order by ID or raise 404 if not found.

    Args:
        order_id: UUID string of the order
        db: Database session

    Returns:
        Order: Order object if found

    Raises:
        HTTPException: 404 if order not found
    """
    from app.models.order import Order

    # Validate ID format
    validated_id = IDValidator.validate_uuid_string(order_id, "order_id")

    stmt = select(Order).where(Order.id == validated_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )

    return order


async def get_commission_or_404(commission_id: str, db: AsyncSession):
    """
    Get commission by ID or raise 404 if not found.

    Args:
        commission_id: UUID string of the commission
        db: Database session

    Returns:
        Commission: Commission object if found

    Raises:
        HTTPException: 404 if commission not found
    """
    from app.models.commission import Commission

    # Validate ID format
    validated_id = IDValidator.validate_uuid_string(commission_id, "commission_id")

    stmt = select(Commission).where(Commission.id == validated_id)
    result = await db.execute(stmt)
    commission = result.scalar_one_or_none()

    if not commission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Commission with ID {commission_id} not found"
        )

    return commission


# Export the main dependency for easy import
__all__ = [
    "get_db",
    "get_db_session",
    "get_async_session",
    "get_user_or_404",
    "get_product_or_404",
    "get_order_or_404",
    "get_commission_or_404"
]