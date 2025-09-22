"""
Database dependency injection for FastAPI endpoints.

This module provides standardized database session dependencies
for all API endpoints, consolidating session management in a single location.
"""

from typing import AsyncGenerator, Optional, Type, TypeVar, Union
from uuid import UUID
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.core.database import AsyncSessionLocal
from app.core.id_validation import IDValidator, IDValidationError
# Import models at module level for better performance
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.commission import Commission

# Type variable for generic entity validation
T = TypeVar('T')

# Configure logger for database operations
logger = logging.getLogger(__name__)


async def _create_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Internal session factory for database dependencies.

    This is the core session management logic that all public
    database dependencies should use to ensure consistency.

    Yields:
        AsyncSession: Database session with transaction management

    Note:
        This is an internal function. Use get_db() for public API.
    """
    async with AsyncSessionLocal() as session:
        try:
            logger.debug("Database session created")
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()
            logger.debug("Database session closed")


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
    async for session in _create_database_session():
        yield session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Alias for get_db() for backwards compatibility.

    Note: Prefer using get_db() directly for new code.
    This function delegates to the standard session factory.
    """
    async for session in _create_database_session():
        yield session


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Alias for get_db() for async session dependency.

    This is an alternative name for get_db() that makes it clear
    we're working with async sessions. Delegates to standard factory.
    """
    async for session in _create_database_session():
        yield session


# Generic entity validation factory
async def _validate_entity_by_id(
    entity_id: str,
    entity_model: Type[T],
    entity_name: str,
    db: AsyncSession,
    additional_filters: Optional[list] = None
) -> T:
    """
    Generic entity validation function that follows DRY principle.

    Args:
        entity_id: UUID string of the entity
        entity_model: SQLAlchemy model class
        entity_name: Human-readable entity name for error messages
        db: Database session
        additional_filters: Additional WHERE clauses (e.g., soft-delete filters)

    Returns:
        T: Entity object if found

    Raises:
        HTTPException: 400 for validation errors, 404 if entity not found
    """
    # Validate ID format - convert IDValidationError to HTTPException
    try:
        validated_id = IDValidator.validate_uuid_string(entity_id, f"{entity_name.lower()}_id")
        logger.debug(f"Validated {entity_name} ID: {validated_id}")
    except IDValidationError as e:
        logger.warning(f"Invalid {entity_name} ID format: {entity_id}")
        # Ensure validation errors return 400, not 500
        status_code = 400 if e.status_code == 500 else e.status_code
        raise HTTPException(
            status_code=status_code,
            detail=e.message
        )

    try:
        # Build query with optional additional filters
        stmt = select(entity_model).where(entity_model.id == validated_id)
        if additional_filters:
            for filter_condition in additional_filters:
                stmt = stmt.where(filter_condition)

        result = await db.execute(stmt)
        entity = result.scalar_one_or_none()
        logger.debug(f"Database query executed for {entity_name}: {entity is not None}")
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching {entity_name} {entity_id}: {str(e)}")
        # Handle database errors with proper classification
        if "connection" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"Unexpected error when fetching {entity_name} {entity_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

    if not entity:
        logger.info(f"{entity_name} not found: {entity_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_name} with ID {entity_id} not found"
        )

    logger.debug(f"Successfully retrieved {entity_name}: {entity_id}")
    return entity


# Database entity validation dependencies
async def get_user_or_404(user_id: str, db: AsyncSession) -> User:
    """
    Get user by ID or raise 404 if not found.

    Args:
        user_id: UUID string of the user
        db: Database session

    Returns:
        User: User object if found

    Raises:
        HTTPException: 400 for validation errors, 404 if user not found
    """
    return await _validate_entity_by_id(
        entity_id=user_id,
        entity_model=User,
        entity_name="User",
        db=db
    )


async def get_product_or_404(product_id: str, db: AsyncSession) -> Product:
    """
    Get product by ID or raise 404 if not found.

    Args:
        product_id: UUID string of the product
        db: Database session

    Returns:
        Product: Product object if found

    Raises:
        HTTPException: 400 for validation errors, 404 if product not found
    """
    return await _validate_entity_by_id(
        entity_id=product_id,
        entity_model=Product,
        entity_name="Product",
        db=db,
        additional_filters=[Product.deleted_at.is_(None)]  # Exclude soft-deleted products
    )


async def get_order_or_404(order_id: str, db: AsyncSession) -> Order:
    """
    Get order by ID or raise 404 if not found.

    Args:
        order_id: UUID string of the order
        db: Database session

    Returns:
        Order: Order object if found

    Raises:
        HTTPException: 400 for validation errors, 404 if order not found
    """
    return await _validate_entity_by_id(
        entity_id=order_id,
        entity_model=Order,
        entity_name="Order",
        db=db
    )


async def get_commission_or_404(commission_id: str, db: AsyncSession) -> Commission:
    """
    Get commission by ID or raise 404 if not found.

    Args:
        commission_id: UUID string of the commission
        db: Database session

    Returns:
        Commission: Commission object if found

    Raises:
        HTTPException: 400 for validation errors, 404 if commission not found
    """
    return await _validate_entity_by_id(
        entity_id=commission_id,
        entity_model=Commission,
        entity_name="Commission",
        db=db
    )


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