# ~/app/api/v1/endpoints/productos.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Endpoints de Productos API v1
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: productos.py
# Ruta: ~/app/api/v1/endpoints/productos.py
# Autor: Jairo
# Fecha de Creación: 2025-01-14
# Última Actualización: 2025-08-05
# Versión: 1.2.0
# Propósito: Endpoints de gestión de productos para la API v1
#            Implementa CRUD operations con validaciones empresariales
#            Incluye endpoint para upload múltiple de imágenes
#
# Modificaciones:
# 2025-01-14 - Implementación inicial del endpoint POST /productos
# 2025-08-05 - Agregado endpoint PATCH /productos/{id} para actualización parcial
# 2025-08-05 - Agregado endpoint POST /productos/{id}/imagenes para upload de imágenes
#
# ---------------------------------------------------------------------------------------------

"""
Endpoints de gestión de productos para la API v1.

Este módulo contiene:
- POST /productos: Crear nuevos productos con validaciones
- GET /productos: Listar productos con filtros y paginación
- GET /productos/{id}: Obtener producto específico por ID
- PUT /productos/{id}: Actualizar producto completo
- PATCH /productos/{id}: Actualizar producto parcial (operaciones rápidas)
- DELETE /productos/{id}: Eliminar producto (soft delete)
- POST /productos/{id}/imagenes: Upload múltiple de imágenes
- Validaciones empresariales (SKU único, datos requeridos)
- Manejo de errores específicos del dominio
- Logging estructurado para auditoría
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from PIL import Image
from sqlalchemy import and_, asc, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.product import Product
from app.models.product_image import ProductImage
from app.schemas.product import (
    ProductCreate,
    ProductPatch,
    ProductResponse,
    ProductUpdate,
)
from app.schemas.product_image import (
    ProductImageDeleteResponse,
    ProductImageResponse,
    ProductImageUploadResponse,
)
from app.utils.file_validator import validate_multiple_files, get_image_dimensions, compress_image_multiple_resolutions, delete_image_files


# Configurar logging
logger = logging.getLogger(__name__)

# Logger ya configurado arriba - verificando que funciona
# logger = logging.getLogger(__name__)  # Ya existe

# Crear router
router = APIRouter()


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
    description="Crear un nuevo producto con validaciones empresariales",
    tags=["productos"],
)
async def create_producto(
    producto_data: ProductCreate, db: AsyncSession = Depends(get_db)
) -> ProductResponse:
    """
    Crear un nuevo producto en el marketplace.

    Args:
        producto_data: Datos del producto con validaciones
        db: Sesión de base de datos async

    Returns:
        ProductResponse: Producto creado con información completa

    Raises:
        HTTPException 400: Datos inválidos o SKU duplicado
        HTTPException 500: Error interno del servidor
    """
    try:
        logger.info(f"Creando producto con SKU: {producto_data.sku}")

        # Verificar que SKU no existe
        stmt = select(Product).where(Product.sku == producto_data.sku)
        result = await db.execute(stmt)
        existing_product = result.scalar_one_or_none()

        if existing_product:
            logger.warning(
                f"Intento de crear producto con SKU duplicado: {producto_data.sku}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Producto con SKU {producto_data.sku} ya existe",
            )

        # Crear nuevo producto
        db_product = Product(**producto_data.model_dump())
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)

        logger.info(
            f"Producto creado exitosamente: SKU={db_product.sku}, ID={db_product.id}"
        )

        # Convertir a ProductResponse
        return ProductResponse.model_validate(db_product)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando producto: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.get(
    "/",
    response_model=List[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar productos",
    description="Obtener lista de productos con filtros avanzados y paginación",
    tags=["productos"],
)
async def get_productos(
    # Filtros de búsqueda
    search: Optional[str] = Query(
        None, description="Búsqueda por nombre, descripción o SKU"
    ),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    status_filter: Optional[str] = Query(
        None, alias="status", description="Filtrar por estado"
    ),
    # Filtros de precio
    precio_min: Optional[float] = Query(None, ge=0, description="Precio mínimo"),
    precio_max: Optional[float] = Query(None, ge=0, description="Precio máximo"),
    # Ordenamiento
    sort_by: Optional[str] = Query("created_at", description="Campo para ordenar"),
    sort_order: Optional[str] = Query(
        "desc", regex="^(asc|desc)$", description="Orden de clasificación"
    ),
    # Paginación básica
    skip: int = Query(0, ge=0, description="Elementos a saltar"),
    limit: int = Query(100, ge=1, le=500, description="Límite de elementos"),
    db: AsyncSession = Depends(get_db),
) -> List[ProductResponse]:
    """
    Obtener lista de productos con paginación básica.
    """
    try:
        # Construir query base
        stmt = select(Product)

        # Lista para condiciones WHERE
        where_conditions = []
        # Siempre excluir productos eliminados (soft delete)
        where_conditions.append(Product.deleted_at.is_(None))

        # Aplicar filtro de búsqueda
        if search:
            search_filter = or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%"),
            )
            where_conditions.append(search_filter)

        # Filtros específicos
        if categoria:
            where_conditions.append(Product.categoria.ilike(f"%{categoria}%"))

        if status_filter:
            where_conditions.append(Product.status == status_filter)

        # Filtros de precio
        if precio_min is not None:
            where_conditions.append(Product.precio_venta >= precio_min)
        if precio_max is not None:
            where_conditions.append(Product.precio_venta <= precio_max)

        # Aplicar condiciones WHERE si existen
        if where_conditions:
            stmt = stmt.where(and_(*where_conditions))

        # Aplicar ordenamiento
        if sort_by == "precio_venta":
            order_field = Product.precio_venta
        elif sort_by == "name":
            order_field = Product.name
        elif sort_by == "created_at":
            order_field = Product.created_at
        else:
            order_field = Product.created_at

        if sort_order == "desc":
            stmt = stmt.order_by(desc(order_field))
        else:
            stmt = stmt.order_by(asc(order_field))

        # Aplicar paginación
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        productos = result.scalars().all()

        logger.info(f"Obtenidos {len(productos)} productos con filtros aplicados")

        return [ProductResponse.model_validate(producto) for producto in productos]

    except Exception as e:
        logger.error(f"Error al obtener productos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener productos",
        )


@router.get(
    "/{producto_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener producto por ID",
    description="Obtener detalles específicos de un producto por su ID único",
    tags=["productos"],
)
async def get_producto_by_id(
    producto_id: UUID, db: AsyncSession = Depends(get_db)
) -> ProductResponse:
    """
    Obtener un producto específico por su ID.

    Args:
        producto_id: UUID del producto a obtener
        db: Sesión de base de datos async

    Returns:
        ProductResponse: Producto con información completa

    Raises:
        HTTPException 404: Producto no encontrado
        HTTPException 500: Error interno del servidor
    """
    try:
        logger.info(f"Buscando producto con ID: {producto_id}")

        # Buscar producto por ID
        stmt = select(Product).where(
            Product.id == producto_id,
            Product.deleted_at.is_(None)  # Excluir productos eliminados
        )
        result = await db.execute(stmt)
        producto = result.scalar_one_or_none()

        if not producto:
            logger.warning(f"Producto no encontrado: ID={producto_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {producto_id} no encontrado",
            )

        logger.info(f"Producto encontrado: SKU={producto.sku}, ID={producto.id}")

        # Convertir a ProductResponse
        return ProductResponse.model_validate(producto)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error al obtener producto {producto_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.put(
    "/{producto_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar producto",
    description="Actualizar un producto existente por su ID con datos parciales o completos",
    tags=["productos"],
)
async def update_producto(
    producto_id: UUID, 
    producto_data: ProductUpdate, 
    db: AsyncSession = Depends(get_db)
) -> ProductResponse:
    """
    Actualizar un producto existente.

    Args:
        producto_id: ID único del producto a actualizar
        producto_data: Datos del producto a actualizar (campos opcionales)
        db: Sesión de base de datos

    Returns:
        ProductResponse: Producto actualizado

    Raises:
        HTTPException: 404 si el producto no existe,
                      400 si hay errores de validación,
                      500 si hay error interno
    """
    try:
        logger.info(f"Actualizando producto con ID: {producto_id}")

        # Buscar producto existente
        result = await db.execute(select(Product).where(Product.id == producto_id))
        producto = result.scalar_one_or_none()

        if not producto:
            logger.warning(f"Producto no encontrado: {producto_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {producto_id} no encontrado",
            )

        # Actualizar solo campos proporcionados (no None)
        update_data = producto_data.model_dump(exclude_unset=True, exclude_none=True)

        if not update_data:
            logger.warning(f"No se proporcionaron datos para actualizar: {producto_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron datos para actualizar",
            )

        # Validar SKU único si se está actualizando
        if "sku" in update_data and update_data["sku"] != producto.sku:
            existing_sku = await db.execute(
                select(Product).where(
                    Product.sku == update_data["sku"], 
                    Product.id != producto_id
                )
            )
            if existing_sku.scalar_one_or_none():
                logger.warning(f"SKU ya existe: {update_data['sku']}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El SKU {update_data['sku']} ya está en uso",
                )

        # Aplicar actualizaciones
        for field, value in update_data.items():
            setattr(producto, field, value)

        # Actualizar metadatos de tracking si el método existe
        if hasattr(producto, "update_tracking"):
            producto.update_tracking(user_id=None)  # TODO: Obtener user_id del token

        # Guardar cambios
        await db.commit()
        await db.refresh(producto)

        logger.info(f"Producto actualizado exitosamente: {producto_id}")
        return ProductResponse.model_validate(producto)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error al actualizar producto {producto_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.patch(
    "/{producto_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Modificación rápida de producto",
    description="Operaciones PATCH específicas para cambios rápidos sin validaciones complejas de business logic",
    tags=["productos"],
)
async def patch_producto(
    producto_id: UUID, 
    producto_data: ProductPatch, 
    db: AsyncSession = Depends(get_db)
) -> ProductResponse:
    """
    Operaciones PATCH rápidas para producto.
    Diferente de PUT: enfocado en cambios específicos sin validaciones complejas.

    Args:
        producto_id: ID único del producto
        producto_data: Datos específicos para PATCH
        db: Sesión de base de datos
    Returns:
        ProductResponse: Producto modificado
    """
    try:
        logger.info(f"Aplicando PATCH a producto ID: {producto_id}")

        # Buscar producto existente
        result = await db.execute(select(Product).where(Product.id == producto_id))
        producto = result.scalar_one_or_none()

        if not producto:
            logger.warning(f"Producto no encontrado para PATCH: {producto_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {producto_id} no encontrado",
            )

        # Obtener solo campos PATCH enviados
        patch_data = producto_data.model_dump(exclude_unset=True, exclude_none=True)

        if not patch_data:
            logger.warning(f"No se proporcionaron datos PATCH: {producto_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron datos para PATCH",
            )

        # Aplicar cambios PATCH directos (sin validaciones complejas)
        for field, value in patch_data.items():
            setattr(producto, field, value)
            logger.info(f"PATCH aplicado - {field}: {value}")

        # Guardar cambios
        await db.commit()
        await db.refresh(producto)

        logger.info(f"PATCH exitoso para producto: {producto_id}")
        return ProductResponse.model_validate(producto)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error en PATCH producto {producto_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor en operación PATCH",
        )


@router.delete(
    "/{producto_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar producto (soft delete)",
    description="Eliminación lógica de producto - no se borra físicamente, se marca como eliminado",
    tags=["productos"]
)
async def delete_producto(
    producto_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ProductResponse:
    """
    Soft delete de un producto existente.
    
    Args:
        producto_id: ID único del producto a eliminar
        db: Sesión de base de datos
    Returns:
        ProductResponse: Producto marcado como eliminado
    """
    try:
        logger.info(f"Eliminando producto (soft delete) ID: {producto_id}")

        # Buscar producto existente (solo activos - excluir ya eliminados)
        result = await db.execute(
            select(Product).where(
                Product.id == producto_id,
                Product.deleted_at.is_(None)  # Solo productos activos
            )
        )
        producto = result.scalar_one_or_none()

        if not producto:
            logger.warning(f"Producto no encontrado o ya eliminado: {producto_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {producto_id} no encontrado o ya eliminado"
            )

        # Aplicar soft delete - marcar deleted_at
        producto.deleted_at = datetime.utcnow()

        # Guardar cambios
        await db.commit()
        await db.refresh(producto)

        logger.info(f"Producto eliminado exitosamente (soft delete): {producto_id}")
        return ProductResponse.model_validate(producto)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error al eliminar producto {producto_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor en eliminación"
        )


@router.post(
    "/{producto_id}/imagenes",
    response_model=ProductImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload múltiple de imágenes",
    description="Subir múltiples imágenes para un producto específico (máx 10 archivos, 5MB c/u)",
    tags=["productos"]
)
async def upload_producto_imagenes(
    producto_id: UUID,
    files: List[UploadFile] = File(
        ...,
        description="Lista de archivos de imagen (JPEG, PNG, WebP, GIF)"
    ),
    db: AsyncSession = Depends(get_db)
) -> ProductImageUploadResponse:
    """
    Upload múltiple de imágenes para un producto.
    
    Validaciones:
    - Producto debe existir
    - Máximo 10 archivos por request
    - Máximo 5MB por archivo
    - Solo formatos: JPEG, PNG, WebP, GIF
    
    Args:
        producto_id: ID del producto
        files: Lista de archivos de imagen
        db: Sesión de base de datos
        
    Returns:
        ProductImageUploadResponse: Resultado del upload con detalles
        
    Raises:
        HTTPException: Si el producto no existe o hay errores de validación
    """
    try:
        logger.info(f"Iniciando upload de {len(files)} archivos para producto {producto_id}")
        
        # 1. Verificar que el producto existe
        result = await db.execute(
            select(Product).where(
                Product.id == producto_id,
                Product.deleted_at.is_(None)
            )
        )
        producto = result.scalar_one_or_none()
        
        if not producto:
            logger.warning(f"Producto no encontrado para upload: {producto_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {producto_id} no encontrado"
            )
        
        # 2. Validar archivos
        valid_files, validation_errors = await validate_multiple_files(files)
        
        if not valid_files:
            logger.warning(f"No hay archivos válidos para upload: {validation_errors}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No hay archivos válidos. Errores: {'; '.join(validation_errors)}"
            )
        
        logger.info(f"Validación completada: {len(valid_files)} válidos, {len(validation_errors)} errores")
        
        # 3. Procesar y comprimir imágenes válidas
        processed_images = []
        save_directory = f"uploads/productos/imagenes"
        
        for i, file in enumerate(valid_files):
            try:
                logger.info(f"Procesando imagen {i+1}/{len(valid_files)}: {file.filename}")
                
                # Generar nombre único para archivo
                file_extension = file.filename.split('.')[-1].lower()
                unique_filename = f"{uuid.uuid4().hex}"
                
                # Comprimir en múltiples resoluciones
                resolutions_info = await compress_image_multiple_resolutions(
                    file, unique_filename, save_directory
                )
                
                # Crear registro para cada resolución
                for resolution_data in resolutions_info:
                    try:
                        # Crear instancia ProductImage para cada resolución
                        product_image = ProductImage(
                            product_id=producto_id,
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
                        processed_images.append(product_image)
                        
                    except Exception as e:
                        logger.error(f"Error creando registro para resolución {resolution_data['resolution']}: {str(e)}")
                        continue
                
                logger.info(f"Imagen {file.filename} procesada en {len(resolutions_info)} resoluciones")
                
            except Exception as e:
                print(f"Error procesando imagen {file.filename}: {str(e)}")
                validation_errors.append(f"Error procesando {file.filename}: {str(e)}")
                continue
        
        # 4. Confirmar transacción
        try:
            await db.commit()
            logger.info(f"Upload completado: {len(processed_images)} imágenes guardadas")
        except Exception as e:
            await db.rollback()
            logger.error(f"Error en commit de upload: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error guardando imágenes en base de datos"
            )
        
        # 5. Preparar respuesta con imágenes procesadas
        images_response = []
        for img in processed_images:
            if img.resolution == "original":  # Solo mostrar originales en respuesta
                images_response.append(ProductImageResponse(
                    id=img.id,
                    product_id=img.product_id,
                    filename=img.filename,
                    original_filename=img.original_filename,
                    file_path=img.file_path,
                    file_size=img.file_size,
                    mime_type=img.mime_type,
                    width=img.width,
                    height=img.height,
                    order_index=img.order_index,
                    resolution=img.resolution,
                    is_primary=img.is_primary,
                    created_at=img.created_at,
                    updated_at=img.updated_at
                ))
        
        return ProductImageUploadResponse(
            success=True,
            uploaded_count=len([img for img in processed_images if img.resolution == "original"]),
            total_files=len(files),
            images=images_response,
            errors=validation_errors,
            resolutions_created=["original", "large", "medium", "thumbnail", "small"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en upload producto {producto_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor en upload"
        )



@router.delete(
    "/imagenes/{imagen_id}",
    response_model=ProductImageDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar imagen de producto",
    description="Eliminación de imagen específica (soft delete + archivos físicos)",
    tags=["productos"]
)
async def delete_producto_imagen(
    imagen_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Eliminar imagen de producto."""
    try:
        # Buscar imagen existente (solo activas)
        result = await db.execute(
            select(ProductImage).where(
                ProductImage.id == imagen_id,
                ProductImage.deleted_at.is_(None)
            )
        )
        imagen = result.scalar_one_or_none()

        if not imagen:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Imagen con ID {imagen_id} no encontrada"
            )

        # Soft delete en BD
        imagen.deleted_at = datetime.utcnow()

        # Eliminar archivos físicos
        await delete_image_files(imagen.file_path)

        # Confirmar transacción
        await db.commit()

        return ProductImageDeleteResponse(
            success=True,
            message="Imagen eliminada exitosamente",
            deleted_image_id=imagen_id
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error eliminando imagen {imagen_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )