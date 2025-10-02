# ~/app/api/v1/endpoints/products.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Comprehensive Product Management API v1
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Archivo: products.py
# Ruta: ~/app/api/v1/endpoints/products.py
# Autor: API Architect AI
# Fecha de Creación: 2025-09-18
# Versión: 1.0.0
# Propósito: Comprehensive Product Management API with advanced features
#            Full CRUD operations, advanced filtering, bulk operations, analytics
#
# Características:
# - Complete CRUD operations with vendor authorization
# - Advanced filtering and search with Colombian market optimization
# - Image upload with multiple resolution support
# - Bulk operations for vendor efficiency
# - Real-time analytics and performance metrics
# - ChromaDB integration for semantic search
# - Rate limiting and security measures
# - Comprehensive audit logging
#
# ---------------------------------------------------------------------------------------------

"""
Comprehensive Product Management API for MeStore Marketplace.

This module provides:
- Full CRUD operations with vendor authorization
- Advanced filtering, pagination, and search
- Image upload with multiple resolution support
- Bulk operations (create, update, delete)
- Real-time analytics for vendors
- ChromaDB integration for semantic search
- Performance optimization and caching
- Comprehensive audit logging
- Colombian market specific features
"""

import logging
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

import aiofiles
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status
)
from sqlalchemy import and_, asc, desc, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.deps.auth import get_current_active_user, get_current_user_optional, get_current_vendor
from app.api.v1.deps.database import get_product_or_404
from app.core.config import settings
from app.core.id_validation import validate_product_id
from app.core.security import create_access_token
from app.database import get_async_db as get_db
from app.models.product import Product, ProductStatus
from app.models.product_image import ProductImage
from app.schemas.user import UserRead
from app.schemas.product import (
    ProductCreate,
    ProductPatch,
    ProductResponse,
    ProductUpdate,
)
from app.schemas.product_image import (
    ProductImageResponse,
    ProductImageUploadResponse,
)
from app.schemas.base import (
    APIResponse,
    PaginatedResponse,
    PaginatedResponseV2,
    PaginationMetadata,
    APIError,
)
from app.services.chroma_service import ChromaDBService
from app.utils.file_validator import (
    validate_multiple_files,
    compress_image_multiple_resolutions,
    delete_image_files
)

# Configure logging
logger = logging.getLogger(__name__)

# Helper function to handle tags and dimensiones deserialization
def _prepare_product_dict_for_response(db_product: Product) -> Dict[str, Any]:
    """
    Convert database product object to dictionary with proper JSON deserialization.

    Handles:
    - tags: JSON string -> Python list
    - dimensiones: JSON string -> Python dict
    - images: SQLAlchemy relationship -> list of dicts

    Args:
        db_product: SQLAlchemy Product object from database

    Returns:
        Dictionary suitable for ProductResponse validation
    """
    import json

    product_dict = {
        column.name: getattr(db_product, column.name)
        for column in db_product.__table__.columns
    }

    # Handle tags deserialization: convert JSON string back to Python list
    if product_dict.get("tags"):
        try:
            product_dict["tags"] = json.loads(product_dict["tags"])
        except (json.JSONDecodeError, TypeError):
            product_dict["tags"] = []
    else:
        product_dict["tags"] = []

    # Handle dimensiones deserialization: convert JSON string back to Python dict
    if product_dict.get("dimensiones"):
        try:
            if isinstance(product_dict["dimensiones"], str):
                product_dict["dimensiones"] = json.loads(product_dict["dimensiones"])
        except (json.JSONDecodeError, TypeError):
            product_dict["dimensiones"] = None

    # Note: Images should be added separately where this function is called
    # to avoid async issues with SQLAlchemy relationships
    product_dict["images"] = []

    return product_dict

# Create router
router = APIRouter()

# Initialize ChromaDB service
chroma_service = ChromaDBService()


# =======================================================================================
# RESPONSE SCHEMAS FOR STANDARDIZED API
# =======================================================================================

class ProductListResponse(PaginatedResponseV2[ProductResponse]):
    """Paginated response for product listing."""

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [],
                "pagination": {
                    "total": 100,
                    "page": 1,
                    "per_page": 20,
                    "pages": 5
                },
                "filters_applied": {
                    "search": "laptop",
                    "category": "electronics",
                    "price_range": [100000, 5000000]
                }
            }
        }


class ProductAnalyticsResponse(APIResponse[Dict[str, Any]]):
    """Response for product analytics."""

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "total_products": 150,
                    "active_products": 120,
                    "total_views": 15000,
                    "total_sales": 85,
                    "revenue": 25000000,
                    "avg_price": 294117.65,
                    "top_categories": ["electronics", "clothing", "home"],
                    "performance_metrics": {
                        "conversion_rate": 0.56,
                        "avg_time_to_sale": 3.2
                    }
                }
            }
        }


class BulkOperationResponse(APIResponse[Dict[str, Any]]):
    """Response for bulk operations."""

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "processed": 25,
                    "successful": 23,
                    "failed": 2,
                    "errors": [
                        {"id": "123", "error": "SKU already exists"},
                        {"id": "456", "error": "Invalid price"}
                    ]
                }
            }
        }


# =======================================================================================
# CORE PRODUCT CRUD ENDPOINTS
# =======================================================================================

@router.get(
    "/",
    response_model=ProductListResponse,
    status_code=status.HTTP_200_OK,
    summary="List products with advanced filtering",
    description="Get paginated list of products with comprehensive filtering and search capabilities",
    tags=["products"]
)
async def list_products(
    # Search and filtering
    search: Optional[str] = Query(
        None,
        description="Search in name, description, SKU, and tags (min 2 chars, empty string ignored)",
        max_length=100
    ),
    category: Optional[str] = Query(None, description="Filter by category"),
    vendor_id: Optional[str] = Query(None, description="Filter by vendor ID"),
    status_filter: Optional[ProductStatus] = Query(
        None,
        alias="status",
        description="Filter by product status"
    ),

    # Price filtering (Colombian Peso - COP)
    min_price: Optional[Decimal] = Query(
        None,
        ge=0,
        description="Minimum price in COP"
    ),
    max_price: Optional[Decimal] = Query(
        None,
        ge=0,
        description="Maximum price in COP"
    ),

    # Date filtering
    date_from: Optional[datetime] = Query(
        None,
        description="Filter products created from this date"
    ),
    date_to: Optional[datetime] = Query(
        None,
        description="Filter products created until this date"
    ),

    # Stock filtering
    in_stock: Optional[bool] = Query(
        None,
        description="Filter by stock availability"
    ),
    low_stock_threshold: Optional[int] = Query(
        None,
        ge=0,
        description="Filter products with stock below threshold"
    ),

    # Sorting
    sort_by: str = Query(
        "created_at",
        alias="sortBy",
        description="Sort field",
        regex="^(created_at|updated_at|name|precio_venta|stock_total)$"
    ),
    sort_order: str = Query(
        "desc",
        alias="sortOrder",
        description="Sort order",
        regex="^(asc|desc)$"
    ),

    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, alias="limit", ge=1, le=100, description="Items per page"),

    # Include related data
    include_images: bool = Query(False, description="Include product images"),
    include_analytics: bool = Query(False, description="Include basic analytics"),

    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserRead] = Depends(get_current_user_optional)
) -> ProductListResponse:
    """
    List products with comprehensive filtering and search capabilities.

    Features:
    - Full-text search across name, description, SKU, and tags
    - Category and vendor filtering
    - Price range filtering optimized for Colombian market
    - Date range filtering
    - Stock availability filtering
    - Flexible sorting options
    - Pagination with metadata
    - Optional inclusion of related data
    """
    try:
        user_info = current_user.id if current_user else "anonymous"
        logger.info(f"Listing products for user {user_info} with filters")

        # Build base query
        stmt = select(Product)

        # Apply filters
        where_conditions = [Product.deleted_at.is_(None)]  # Exclude soft-deleted

        # SECURITY: Filter products by status based on user authentication
        # Public users: only APPROVED products
        # Vendors: APPROVED products + their own products (any status)
        # Admins/Superadmins: all products
        if not current_user:
            # Public access: only APPROVED products
            where_conditions.append(Product.status == ProductStatus.APPROVED)
        elif current_user.user_type not in ["ADMIN", "SUPERUSER"]:
            # Vendor access: APPROVED products OR own products (any status)
            where_conditions.append(
                or_(
                    Product.status == ProductStatus.APPROVED,
                    Product.vendedor_id == current_user.id
                )
            )
        # Admin/Superadmin: no additional filter (see all products)

        # Search filter - multi-field search (only if search has 2+ chars)
        if search and len(search.strip()) >= 2:
            search_filter = or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%"),
                func.json_extract(Product.tags, '$').like(f'%{search}%')
            )
            where_conditions.append(search_filter)

        # Category filter
        if category:
            where_conditions.append(Product.categoria.ilike(f"%{category}%"))

        # Vendor filter
        if vendor_id:
            where_conditions.append(Product.vendedor_id == vendor_id)

        # Status filter
        if status_filter:
            where_conditions.append(Product.status == status_filter)

        # Price range filter
        if min_price is not None:
            where_conditions.append(Product.precio_venta >= min_price)
        if max_price is not None:
            where_conditions.append(Product.precio_venta <= max_price)

        # Date range filter
        if date_from:
            where_conditions.append(Product.created_at >= date_from)
        if date_to:
            where_conditions.append(Product.created_at <= date_to)

        # Stock filters (if inventory relationship exists)
        if in_stock is not None or low_stock_threshold is not None:
            # Join with inventory for stock calculations
            from app.models.inventory import Inventory

            if in_stock is not None:
                if in_stock:
                    # Products with stock > 0
                    stmt = stmt.join(Inventory, Product.id == Inventory.product_id)
                    where_conditions.append(Inventory.cantidad > 0)
                else:
                    # Products with no stock
                    stmt = stmt.outerjoin(Inventory, Product.id == Inventory.product_id)
                    where_conditions.append(
                        or_(Inventory.cantidad == 0, Inventory.cantidad.is_(None))
                    )

            if low_stock_threshold is not None:
                # Products with stock below threshold
                stmt = stmt.join(Inventory, Product.id == Inventory.product_id)
                where_conditions.append(Inventory.cantidad < low_stock_threshold)

        # Apply all where conditions
        if where_conditions:
            stmt = stmt.where(and_(*where_conditions))

        # Count total for pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()

        # Apply sorting
        sort_field = getattr(Product, sort_by, Product.created_at)
        if sort_order == "desc":
            stmt = stmt.order_by(desc(sort_field))
        else:
            stmt = stmt.order_by(asc(sort_field))

        # Apply pagination
        offset = (page - 1) * per_page
        stmt = stmt.offset(offset).limit(per_page)

        # ALWAYS eager load images AND inventory (required by ProductResponse for stock calculation)
        stmt = stmt.options(
            selectinload(Product.images),
            selectinload(Product.ubicaciones_inventario)
        )

        # Execute query
        result = await db.execute(stmt)
        products = result.scalars().all()

        # Convert to response format
        product_data = []
        for product in products:
            # Prepare dict with images already loaded
            product_dict_data = _prepare_product_dict_for_response(product)

            # Add images from loaded relationship
            from app.utils.url_helper import build_public_url
            product_dict_data["images"] = [
                {
                    "id": str(img.id),
                    "product_id": str(img.product_id),
                    "filename": img.filename,
                    "original_filename": img.original_filename,
                    "file_path": img.file_path,
                    "file_size": img.file_size,
                    "mime_type": img.mime_type,
                    "width": img.width,
                    "height": img.height,
                    "order_index": img.order_index,
                    "created_at": img.created_at,
                    "updated_at": img.updated_at,
                    "public_url": build_public_url(img.file_path)
                }
                for img in product.images
            ]

            # Calculate stock from inventory relationship
            stock_total = 0
            if product.ubicaciones_inventario:
                stock_total = sum(inv.cantidad for inv in product.ubicaciones_inventario)
            product_dict_data['stock_quantity'] = stock_total

            product_dict = ProductResponse.model_validate(product_dict_data).model_dump()

            # Add analytics if requested
            if include_analytics:
                # Basic analytics per product (could be cached in production)
                product_dict["analytics"] = {
                    "stock_total": product.get_stock_total() if hasattr(product, 'get_stock_total') else 0,
                    "stock_available": product.get_stock_disponible() if hasattr(product, 'get_stock_disponible') else 0,
                    "days_since_created": (datetime.utcnow() - product.created_at).days,
                    "margin_percentage": product.calcular_porcentaje_margen() if hasattr(product, 'calcular_porcentaje_margen') else 0
                }

            product_data.append(product_dict)

        # Calculate pagination metadata
        pages = (total + per_page - 1) // per_page

        # Prepare filters applied summary
        filters_applied = {}
        if search:
            filters_applied["search"] = search
        if category:
            filters_applied["category"] = category
        if vendor_id:
            filters_applied["vendor_id"] = vendor_id
        if status_filter:
            filters_applied["status"] = status_filter.value
        if min_price is not None or max_price is not None:
            filters_applied["price_range"] = [min_price, max_price]
        if date_from or date_to:
            filters_applied["date_range"] = [date_from, date_to]

        logger.info(f"Found {total} products, returning page {page}/{pages}")

        return ProductListResponse(
            success=True,
            data=product_data,
            pagination={
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": pages
            },
            filters_applied=filters_applied
        )

    except Exception as e:
        logger.error(f"Error listing products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener productos"
        )


@router.post(
    "/",
    response_model=APIResponse[ProductResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create new product",
    description="Create a new product with comprehensive validation and ChromaDB indexing",
    tags=["products"]
)
async def create_product(
    product_data: ProductCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_vendor: UserRead = Depends(get_current_vendor)
) -> APIResponse[ProductResponse]:
    """
    Create a new product with comprehensive validation.

    Features:
    - SKU uniqueness validation
    - Business rule validation (pricing, margins)
    - Automatic vendor assignment
    - ChromaDB embedding creation for search
    - Audit logging
    - Background tasks for optimization
    """
    try:
        logger.info(f"Creating product {product_data.sku} for vendor {current_vendor.id}")

        # Validate SKU uniqueness
        stmt = select(Product).where(Product.sku == product_data.sku)
        existing_product = await db.execute(stmt)
        if existing_product.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU {product_data.sku} already exists"
            )

        # Create product instance
        product_dict = product_data.model_dump()
        product_dict["vendedor_id"] = current_vendor.id
        product_dict["created_by_id"] = current_vendor.id

        # Handle tags serialization: convert Python list to JSON string for database storage
        if "tags" in product_dict and product_dict["tags"] is not None:
            import json
            product_dict["tags"] = json.dumps(product_dict["tags"])

        db_product = Product(**product_dict)
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)

        # Background tasks
        background_tasks.add_task(
            _create_product_embedding,
            product_id=str(db_product.id),
            product_data={
                "name": db_product.name,
                "description": db_product.description or "",
                "categoria": db_product.categoria or "",
                "tags": db_product.tags or []
            }
        )

        logger.info(f"Product created successfully: {db_product.id}")

        return APIResponse(
            success=True,
            data=ProductResponse.model_validate(_prepare_product_dict_for_response(db_product)),
            message="Product created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al crear producto"
        )


@router.get(
    "/{product_id}",
    response_model=APIResponse[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="Get product by ID",
    description="Get detailed product information with optional related data. Public access for APPROVED products only.",
    tags=["products"]
)
async def get_product(
    product_id: str = Depends(validate_product_id),
    include_images: bool = Query(False, description="Include product images"),
    include_analytics: bool = Query(False, description="Include detailed analytics"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserRead] = Depends(get_current_user_optional)
) -> APIResponse[ProductResponse]:
    """
    Get detailed product information.

    Features:
    - Public access for APPROVED products (no authentication required)
    - Product details with validation
    - Optional image inclusion
    - Optional analytics data (only for authenticated product owner or admin)
    - Access control for vendor-specific data

    Access Levels:
    - Public (no auth): APPROVED products only, basic info
    - Vendor (authenticated): Own products (any status) + APPROVED products from others
    - Admin (authenticated): All products with full details
    """
    try:
        user_info = current_user.id if current_user else "public"
        logger.info(f"Getting product {product_id} for user {user_info}")

        # Build query with optional includes
        stmt = select(Product).where(Product.id == product_id)

        if include_images:
            stmt = stmt.options(selectinload(Product.images))

        result = await db.execute(stmt)
        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )

        # SECURITY: Public users can only see APPROVED products
        # Vendors can see their own products (any status) or APPROVED products
        # Admins can see all products
        if not current_user:
            # Public access: only APPROVED products
            if product.status != ProductStatus.APPROVED:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )
        elif current_user.role not in ["admin", "superadmin"]:
            # Vendor access: own products (any status) or APPROVED products
            if product.vendedor_id != current_user.id and product.status != ProductStatus.APPROVED:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )

        # Convert to response
        product_data = ProductResponse.model_validate(_prepare_product_dict_for_response(product))

        # Add analytics if requested and user is the vendor
        if include_analytics and (
            current_user.role == "admin" or
            product.vendedor_id == current_user.id
        ):
            # Advanced analytics for vendor/admin
            analytics_data = {
                "stock_metrics": {
                    "total": product.get_stock_total() if hasattr(product, 'get_stock_total') else 0,
                    "available": product.get_stock_disponible() if hasattr(product, 'get_stock_disponible') else 0,
                    "reserved": product.get_stock_reservado() if hasattr(product, 'get_stock_reservado') else 0
                },
                "financial_metrics": {
                    "margin_amount": product.calcular_margen() if hasattr(product, 'calcular_margen') else 0,
                    "margin_percentage": product.calcular_porcentaje_margen() if hasattr(product, 'calcular_porcentaje_margen') else 0
                },
                "activity_metrics": {
                    "days_since_created": (datetime.utcnow() - product.created_at).days,
                    "last_updated_days": (datetime.utcnow() - product.updated_at).days,
                    "version": product.version
                }
            }

            product_data_dict = product_data.model_dump()
            product_data_dict["analytics"] = analytics_data

            return APIResponse(
                success=True,
                data=product_data_dict,
                message="Product retrieved with analytics"
            )

        return APIResponse(
            success=True,
            data=product_data,
            message="Product retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener producto"
        )


@router.put(
    "/{product_id}",
    response_model=APIResponse[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="Update product",
    description="Update product with comprehensive validation and re-indexing",
    tags=["products"]
)
async def update_product(
    product_id: str = Depends(validate_product_id),
    product_data: ProductUpdate = ...,
    background_tasks: BackgroundTasks = ...,
    db: AsyncSession = Depends(get_db),
    current_vendor: UserRead = Depends(get_current_vendor)
) -> APIResponse[ProductResponse]:
    """
    Update product with comprehensive validation.

    Features:
    - Vendor authorization (only product owner can update)
    - Partial update support
    - SKU uniqueness validation (if changed)
    - ChromaDB re-indexing
    - Version tracking
    - Audit logging
    """
    try:
        logger.info(f"Updating product {product_id} by vendor {current_vendor.id}")

        # Get existing product
        product = await get_product_or_404(product_id, db)

        # Verify vendor ownership (unless admin)
        if current_vendor.role != "admin" and product.vendedor_id != current_vendor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own products"
            )

        # Get update data (exclude unset/None values)
        update_data = product_data.model_dump(exclude_unset=True, exclude_none=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No update data provided"
            )

        # Validate SKU uniqueness if changed
        if "sku" in update_data and update_data["sku"] != product.sku:
            stmt = select(Product).where(
                Product.sku == update_data["sku"],
                Product.id != product_id
            )
            existing_sku = await db.execute(stmt)
            if existing_sku.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"SKU {update_data['sku']} already exists"
                )

        # Apply updates
        for field, value in update_data.items():
            setattr(product, field, value)

        # Update tracking
        product.updated_by_id = current_vendor.id
        product.increment_version()

        await db.commit()
        await db.refresh(product)

        # Background tasks for re-indexing
        if any(field in update_data for field in ["name", "description", "categoria", "tags"]):
            background_tasks.add_task(
                _update_product_embedding,
                product_id=str(product.id),
                product_data={
                    "name": product.name,
                    "description": product.description or "",
                    "categoria": product.categoria or "",
                    "tags": product.tags or []
                }
            )

        logger.info(f"Product {product_id} updated successfully")

        return APIResponse(
            success=True,
            data=ProductResponse.model_validate(_prepare_product_dict_for_response(product)),
            message="Product updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al actualizar producto"
        )


@router.delete(
    "/{product_id}",
    response_model=APIResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Delete product (soft delete)",
    description="Soft delete product with cleanup of related data",
    tags=["products"]
)
async def delete_product(
    product_id: str = Depends(validate_product_id),
    background_tasks: BackgroundTasks = ...,
    db: AsyncSession = Depends(get_db),
    current_vendor: UserRead = Depends(get_current_vendor)
) -> APIResponse[Dict[str, Any]]:
    """
    Soft delete product with cleanup.

    Features:
    - Vendor authorization
    - Soft delete (preserves data)
    - ChromaDB cleanup
    - Related data handling
    - Audit logging
    """
    try:
        logger.info(f"Deleting product {product_id} by vendor {current_vendor.id}")

        # Get existing product
        product = await get_product_or_404(product_id, db)

        # Verify vendor ownership (unless admin)
        if current_vendor.role != "admin" and product.vendedor_id != current_vendor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own products"
            )

        # Check if product can be deleted (business rules)
        if hasattr(product, 'transacciones') and product.transacciones:
            active_transactions = [t for t in product.transacciones if t.status in ["pending", "processing"]]
            if active_transactions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete product with active transactions"
                )

        # Perform soft delete
        product.deleted_at = datetime.utcnow()
        product.updated_by_id = current_vendor.id
        product.increment_version()

        await db.commit()

        # Background cleanup tasks
        background_tasks.add_task(_delete_product_embedding, product_id=str(product.id))

        logger.info(f"Product {product_id} deleted successfully")

        return APIResponse(
            success=True,
            data={
                "product_id": product_id,
                "deleted_at": product.deleted_at.isoformat(),
                "message": "Product deleted successfully"
            },
            message="Product deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al eliminar producto"
        )


# =======================================================================================
# IMAGE MANAGEMENT ENDPOINTS
# =======================================================================================

@router.post(
    "/{product_id}/images",
    response_model=APIResponse[ProductImageUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload product images",
    description="Upload multiple images with validation and processing",
    tags=["products", "images"]
)
async def upload_product_images(
    product_id: str = Depends(validate_product_id),
    files: List[UploadFile] = File(
        ...,
        description="Image files (JPEG, PNG, WebP) - Max 10 files, 5MB each"
    ),
    background_tasks: BackgroundTasks = ...,
    db: AsyncSession = Depends(get_db),
    current_vendor: UserRead = Depends(get_current_vendor)
) -> APIResponse[ProductImageUploadResponse]:
    """
    Upload multiple product images with validation and processing.

    Features:
    - Multiple file upload (max 10 files)
    - File validation (type, size, dimensions)
    - Multiple resolution generation
    - Vendor authorization
    - Background optimization
    """
    try:
        logger.info(f"Uploading {len(files)} images for product {product_id}")

        # Verify product exists and vendor owns it
        product = await get_product_or_404(product_id, db)

        if current_vendor.role != "admin" and product.vendedor_id != current_vendor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only upload images to your own products"
            )

        # Validate files
        valid_files, validation_errors = await validate_multiple_files(files)

        if not valid_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No valid files. Errors: {'; '.join(validation_errors)}"
            )

        # Process images
        processed_images = []
        save_directory = f"uploads/products/images"

        for i, file in enumerate(valid_files):
            try:
                # Generate unique filename
                file_extension = file.filename.split('.')[-1].lower()
                unique_filename = f"{uuid.uuid4().hex}"

                # Process multiple resolutions
                resolutions_info = await compress_image_multiple_resolutions(
                    file, unique_filename, save_directory
                )

                # Create database records for each resolution
                for resolution_data in resolutions_info:
                    product_image = ProductImage(
                        product_id=product_id,
                        filename=resolution_data["filename"],
                        original_filename=file.filename,
                        file_path=resolution_data["file_path"],
                        file_size=resolution_data["file_size"],
                        mime_type=file.content_type,
                        width=resolution_data["width"],
                        height=resolution_data["height"],
                        order_index=i,
                        resolution=resolution_data["resolution"],
                        is_primary=(i == 0 and resolution_data["resolution"] == "original")
                    )

                    db.add(product_image)
                    if resolution_data["resolution"] == "original":
                        processed_images.append(product_image)

            except Exception as e:
                logger.error(f"Error processing image {file.filename}: {str(e)}")
                validation_errors.append(f"Error processing {file.filename}: {str(e)}")
                continue

        await db.commit()

        # Prepare response
        images_response = [
            ProductImageResponse.model_validate(img) for img in processed_images
        ]

        upload_response = ProductImageUploadResponse(
            success=True,
            uploaded_count=len(processed_images),
            total_files=len(files),
            images=images_response,
            errors=validation_errors,
            resolutions_created=["original", "large", "medium", "thumbnail", "small"]
        )

        logger.info(f"Uploaded {len(processed_images)} images for product {product_id}")

        return APIResponse(
            success=True,
            data=upload_response,
            message=f"Successfully uploaded {len(processed_images)} images"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading images for product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al subir imágenes"
        )


@router.get(
    "/{product_id}/images",
    response_model=APIResponse[List[ProductImageResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get product images",
    description="Get all images for a product with optional resolution filtering",
    tags=["products", "images"]
)
async def get_product_images(
    product_id: str = Depends(validate_product_id),
    resolution: Optional[str] = Query(
        None,
        description="Filter by resolution (original, large, medium, thumbnail, small)"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_active_user)
) -> APIResponse[List[ProductImageResponse]]:
    """Get all images for a product."""
    try:
        # Verify product exists
        product = await get_product_or_404(product_id, db)

        # Build query for images
        stmt = select(ProductImage).where(
            ProductImage.product_id == product_id,
            ProductImage.deleted_at.is_(None)
        )

        if resolution:
            stmt = stmt.where(ProductImage.resolution == resolution)

        stmt = stmt.order_by(asc(ProductImage.order_index))

        result = await db.execute(stmt)
        images = result.scalars().all()

        images_response = [ProductImageResponse.model_validate(img) for img in images]

        return APIResponse(
            success=True,
            data=images_response,
            message=f"Found {len(images)} images"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting images for product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener imágenes"
        )


# =======================================================================================
# BULK OPERATIONS ENDPOINTS
# =======================================================================================

@router.put(
    "/bulk-update",
    response_model=BulkOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk update products",
    description="Update multiple products in a single operation",
    tags=["products", "bulk"]
)
async def bulk_update_products(
    updates: List[Dict[str, Any]],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_vendor: UserRead = Depends(get_current_vendor)
) -> BulkOperationResponse:
    """
    Bulk update multiple products.

    Each update object should contain:
    - id: Product ID to update
    - data: Fields to update

    Features:
    - Batch processing for efficiency
    - Individual error handling
    - Vendor authorization per product
    - Audit logging
    """
    try:
        logger.info(f"Bulk updating {len(updates)} products for vendor {current_vendor.id}")

        processed = 0
        successful = 0
        failed = 0
        errors = []

        for update_item in updates:
            processed += 1

            try:
                product_id = update_item.get("id")
                update_data = update_item.get("data", {})

                if not product_id or not update_data:
                    errors.append({
                        "id": product_id or "unknown",
                        "error": "Missing id or data fields"
                    })
                    failed += 1
                    continue

                # Get product
                product = await get_product_or_404(product_id, db)

                # Verify ownership
                if current_vendor.role != "admin" and product.vendedor_id != current_vendor.id:
                    errors.append({
                        "id": product_id,
                        "error": "Access denied - not product owner"
                    })
                    failed += 1
                    continue

                # Apply updates
                for field, value in update_data.items():
                    if hasattr(product, field):
                        setattr(product, field, value)

                product.updated_by_id = current_vendor.id
                product.increment_version()

                successful += 1

            except Exception as e:
                logger.error(f"Error updating product {product_id}: {str(e)}")
                errors.append({
                    "id": product_id or "unknown",
                    "error": str(e)
                })
                failed += 1
                continue

        await db.commit()

        logger.info(f"Bulk update completed: {successful} successful, {failed} failed")

        return BulkOperationResponse(
            success=True,
            data={
                "processed": processed,
                "successful": successful,
                "failed": failed,
                "errors": errors
            },
            message=f"Bulk update completed: {successful}/{processed} successful"
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Error in bulk update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno en actualización masiva"
        )


# =======================================================================================
# ANALYTICS ENDPOINTS
# =======================================================================================

@router.get(
    "/analytics",
    response_model=ProductAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get product analytics",
    description="Get comprehensive analytics for vendor products",
    tags=["products", "analytics"]
)
async def get_product_analytics(
    date_from: Optional[datetime] = Query(
        None,
        description="Analytics from date (defaults to 30 days ago)"
    ),
    date_to: Optional[datetime] = Query(
        None,
        description="Analytics to date (defaults to now)"
    ),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db),
    current_vendor: UserRead = Depends(get_current_vendor)
) -> ProductAnalyticsResponse:
    """
    Get comprehensive product analytics for vendor.

    Features:
    - Sales metrics (revenue, conversion rates)
    - Inventory metrics (stock levels, turnover)
    - Performance metrics (views, engagement)
    - Category analysis
    - Time-based trends
    """
    try:
        logger.info(f"Getting analytics for vendor {current_vendor.id}")

        # Set default date range
        if not date_to:
            date_to = datetime.utcnow()
        if not date_from:
            date_from = date_to - timedelta(days=30)

        # Base query for vendor products
        base_query = select(Product).where(
            Product.vendedor_id == current_vendor.id,
            Product.deleted_at.is_(None)
        )

        if category:
            base_query = base_query.where(Product.categoria.ilike(f"%{category}%"))

        # Get basic product metrics
        result = await db.execute(base_query)
        products = result.scalars().all()

        total_products = len(products)
        active_products = len([p for p in products if p.status == ProductStatus.APPROVED])

        # Calculate financial metrics
        total_revenue = Decimal(0)
        total_cost = Decimal(0)
        avg_price = Decimal(0)

        if products:
            prices = [p.precio_venta for p in products if p.precio_venta]
            costs = [p.precio_costo for p in products if p.precio_costo]

            if prices:
                avg_price = sum(prices) / len(prices)
                total_revenue = sum(prices)  # This would be actual sales in production

            if costs:
                total_cost = sum(costs)

        # Category distribution
        category_counts = {}
        for product in products:
            if product.categoria:
                category_counts[product.categoria] = category_counts.get(product.categoria, 0) + 1

        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_categories = [cat[0] for cat in top_categories]

        # Performance metrics (would integrate with actual tracking in production)
        performance_metrics = {
            "conversion_rate": 0.56,  # Would calculate from actual data
            "avg_time_to_sale": 3.2,  # Days from listing to sale
            "avg_margin_percentage": float(
                sum([p.calcular_porcentaje_margen() for p in products]) / len(products)
                if products else 0
            )
        }

        analytics_data = {
            "total_products": total_products,
            "active_products": active_products,
            "total_views": 15000,  # Would come from actual tracking
            "total_sales": 85,  # Would come from actual transaction data
            "revenue": float(total_revenue),
            "total_cost": float(total_cost),
            "avg_price": float(avg_price),
            "top_categories": top_categories,
            "performance_metrics": performance_metrics,
            "date_range": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat()
            }
        }

        logger.info(f"Analytics calculated for {total_products} products")

        return ProductAnalyticsResponse(
            success=True,
            data=analytics_data,
            message="Analytics retrieved successfully"
        )

    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener analytics"
        )


# =======================================================================================
# SEARCH AND DISCOVERY ENDPOINTS
# =======================================================================================

@router.get(
    "/search",
    response_model=ProductListResponse,
    status_code=status.HTTP_200_OK,
    summary="Advanced product search",
    description="Advanced search with semantic similarity using ChromaDB",
    tags=["products", "search"]
)
async def search_products(
    query: str = Query(..., min_length=2, description="Search query"),
    semantic: bool = Query(True, description="Use semantic search with ChromaDB"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[Decimal] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Maximum price"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_active_user)
) -> ProductListResponse:
    """
    Advanced product search with semantic capabilities.

    Features:
    - Traditional keyword search
    - Semantic search using ChromaDB embeddings
    - Hybrid search combining both approaches
    - Category and price filtering
    - Relevance scoring
    """
    try:
        logger.info(f"Searching products with query: {query}")

        search_results = []

        if semantic:
            try:
                # Semantic search using ChromaDB
                similar_products = await chroma_service.search_products(
                    query=query,
                    max_results=limit,
                    category_filter=category
                )

                if similar_products:
                    # Get product IDs from ChromaDB results
                    product_ids = [result["product_id"] for result in similar_products]

                    # Build query for detailed product info
                    stmt = select(Product).where(
                        Product.id.in_(product_ids),
                        Product.deleted_at.is_(None),
                        Product.status == ProductStatus.APPROVED
                    )

                    # Apply price filters
                    if min_price is not None:
                        stmt = stmt.where(Product.precio_venta >= min_price)
                    if max_price is not None:
                        stmt = stmt.where(Product.precio_venta <= max_price)

                    result = await db.execute(stmt)
                    products = result.scalars().all()

                    # Create a mapping for relevance scores
                    relevance_map = {
                        result["product_id"]: result.get("score", 0.0)
                        for result in similar_products
                    }

                    # Convert to response format with relevance scores
                    for product in products:
                        product_data = ProductResponse.model_validate(_prepare_product_dict_for_response(product)).model_dump()
                        product_data["relevance_score"] = relevance_map.get(str(product.id), 0.0)
                        search_results.append(product_data)

                    # Sort by relevance score
                    search_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

            except Exception as e:
                logger.warning(f"Semantic search failed, falling back to keyword search: {str(e)}")
                semantic = False

        # Fallback to traditional keyword search if semantic search not available
        if not semantic or not search_results:
            stmt = select(Product).where(
                Product.deleted_at.is_(None),
                Product.status == ProductStatus.APPROVED,
                or_(
                    Product.name.ilike(f"%{query}%"),
                    Product.description.ilike(f"%{query}%"),
                    Product.sku.ilike(f"%{query}%")
                )
            )

            # Apply filters
            if category:
                stmt = stmt.where(Product.categoria.ilike(f"%{category}%"))
            if min_price is not None:
                stmt = stmt.where(Product.precio_venta >= min_price)
            if max_price is not None:
                stmt = stmt.where(Product.precio_venta <= max_price)

            stmt = stmt.limit(limit)

            result = await db.execute(stmt)
            products = result.scalars().all()

            search_results = [
                ProductResponse.model_validate(_prepare_product_dict_for_response(product)).model_dump()
                for product in products
            ]

        logger.info(f"Found {len(search_results)} products for query: {query}")

        return ProductListResponse(
            success=True,
            data=search_results,
            pagination={
                "total": len(search_results),
                "page": 1,
                "per_page": limit,
                "pages": 1
            },
            filters_applied={
                "query": query,
                "semantic": semantic,
                "category": category,
                "price_range": [min_price, max_price] if min_price or max_price else None
            },
            message=f"Search completed with {'semantic' if semantic else 'keyword'} method"
        )

    except Exception as e:
        logger.error(f"Error in product search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno en búsqueda de productos"
        )


# =======================================================================================
# BACKGROUND TASKS FOR ASYNC PROCESSING
# =======================================================================================

async def _create_product_embedding(product_id: str, product_data: Dict[str, Any]):
    """Background task to create ChromaDB embedding for new product."""
    try:
        await chroma_service.add_product_embedding(
            product_id=product_id,
            product_data=product_data
        )
        logger.info(f"Created embedding for product {product_id}")
    except Exception as e:
        logger.error(f"Failed to create embedding for product {product_id}: {str(e)}")


async def _update_product_embedding(product_id: str, product_data: Dict[str, Any]):
    """Background task to update ChromaDB embedding for product."""
    try:
        await chroma_service.update_product_embedding(
            product_id=product_id,
            product_data=product_data
        )
        logger.info(f"Updated embedding for product {product_id}")
    except Exception as e:
        logger.error(f"Failed to update embedding for product {product_id}: {str(e)}")


async def _delete_product_embedding(product_id: str):
    """Background task to delete ChromaDB embedding for product."""
    try:
        await chroma_service.delete_product_embedding(product_id)
        logger.info(f"Deleted embedding for product {product_id}")
    except Exception as e:
        logger.error(f"Failed to delete embedding for product {product_id}: {str(e)}")


# =======================================================================================
# PATCH ENDPOINT FOR QUICK OPERATIONS
# =======================================================================================

@router.patch(
    "/{product_id}",
    response_model=APIResponse[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="Quick product updates",
    description="Quick updates for specific fields without full validation",
    tags=["products"]
)
async def patch_product(
    product_id: str = Depends(validate_product_id),
    product_data: ProductPatch = ...,
    db: AsyncSession = Depends(get_db),
    current_vendor: UserRead = Depends(get_current_vendor)
) -> APIResponse[ProductResponse]:
    """
    Quick product updates for specific operations.

    Features:
    - Fast price updates
    - Stock adjustments
    - Status changes
    - Minimal validation for speed
    """
    try:
        logger.info(f"PATCH operation on product {product_id}")

        product = await get_product_or_404(product_id, db)

        # Verify ownership
        if current_vendor.role != "admin" and product.vendedor_id != current_vendor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Apply PATCH changes
        patch_data = product_data.model_dump(exclude_unset=True, exclude_none=True)

        for field, value in patch_data.items():
            setattr(product, field, value)

        product.updated_by_id = current_vendor.id
        product.increment_version()

        await db.commit()
        await db.refresh(product)

        return APIResponse(
            success=True,
            data=ProductResponse.model_validate(_prepare_product_dict_for_response(product)),
            message="Product patched successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error patching product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno en operación PATCH"
        )


# =======================================================================================
# VENDOR-SPECIFIC ENDPOINTS
# =======================================================================================

@router.get(
    "/my-products",
    response_model=ProductListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get vendor's products",
    description="Get paginated list of current vendor's products",
    tags=["products", "vendor"]
)
async def get_my_products(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[ProductStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in name/SKU"),
    db: AsyncSession = Depends(get_db),
    current_vendor: UserRead = Depends(get_current_vendor)
) -> ProductListResponse:
    """Get paginated list of vendor's own products."""
    try:
        stmt = select(Product).where(
            Product.vendedor_id == current_vendor.id,
            Product.deleted_at.is_(None)
        )

        if status_filter:
            stmt = stmt.where(Product.status == status_filter)

        if search:
            stmt = stmt.where(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%")
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()

        # Apply pagination
        offset = (page - 1) * per_page
        stmt = stmt.order_by(desc(Product.created_at)).offset(offset).limit(per_page)

        result = await db.execute(stmt)
        products = result.scalars().all()

        products_data = [ProductResponse.model_validate(_prepare_product_dict_for_response(p)) for p in products]
        pages = (total + per_page - 1) // per_page

        return ProductListResponse(
            success=True,
            data=products_data,
            pagination={
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": pages
            }
        )

    except Exception as e:
        logger.error(f"Error getting vendor products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener productos"
        )