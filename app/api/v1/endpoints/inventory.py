from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status, Path, Body
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from sqlalchemy import or_, and_
from enum import Enum

class TipoAlerta(str, Enum):
    """Tipos de alertas de inventario"""
    STOCK_BAJO = "STOCK_BAJO"
    SIN_MOVIMIENTO = "SIN_MOVIMIENTO"
    STOCK_AGOTADO = "STOCK_AGOTADO"
    CRITICO = "CRITICO"  # Combinación de stock bajo + sin movimiento
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryResponse, MovimientoStockCreate, TipoMovimiento, MovimientoResponse, InventoryUpdate, AlertasResponse, ReservaStockCreate, ReservaResponse
from app.utils.crud import DatabaseUtils

import logging

logger = logging.getLogger(__name__)

# Crear router
router = APIRouter()


@router.get(
    "/",
    response_model=List[InventoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Consultar inventario por vendedor",
    description="Obtener stock por vendedor con filtros opcionales",
    tags=["inventory"]
)
async def get_inventario(
    vendedor_id: Optional[UUID] = Query(None, description="ID del vendedor (updated_by_id)"),
    product_id: Optional[UUID] = Query(None, description="Filtrar por producto específico"),
    limit: int = Query(50, ge=1, le=100, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    db: AsyncSession = Depends(get_db)
) -> List[InventoryResponse]:
    """
    Consultar stock de inventario por vendedor.

    Args:
        vendedor_id: ID del vendedor para filtrar
        product_id: Filtro opcional por producto
        limit: Límite de resultados (1-100)
        offset: Offset para paginación
        db: Sesión de base de datos

    Returns:
        List[InventoryResponse]: Lista de inventario con stock
    """
    try:
        logger.info(f"Consultando inventario - vendedor: {vendedor_id}, producto: {product_id}")

        # Construir query base
        stmt = select(Inventory)

        # Filtros
        if vendedor_id:
            stmt = stmt.where(Inventory.updated_by_id == vendedor_id)
        if product_id:
            stmt = stmt.where(Inventory.product_id == product_id)

        # Solo mostrar inventario con stock disponible
        stmt = stmt.where(Inventory.cantidad > 0)

        # Paginación y orden
        stmt = stmt.order_by(Inventory.updated_at.desc()).offset(offset).limit(limit)

        # Ejecutar query
        result = await db.execute(stmt)
        inventario = result.scalars().all()

        logger.info(f"Inventario encontrado: {len(inventario)} registros")

        # Convertir a schema response
        return [InventoryResponse.model_validate(item) for item in inventario]

    except HTTPException:
        raise
    except ValueError as e:
        await db.rollback()
        logger.error(f"Error de validación en reserva: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en reserva: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error consultando inventario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno consultando inventario"
        )



@router.post(
    "/reserva",
    response_model=ReservaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Reservar stock para pre-venta",
    description="Reservar cantidad específica de inventario para pre-venta o apartado",
    tags=["inventory"]
)
async def reservar_stock(
    reserva: ReservaStockCreate,
    db: AsyncSession = Depends(get_db)
) -> ReservaResponse:
    """
    Reservar stock específico para pre-venta o apartado.

    Args:
        reserva: Datos de la reserva (inventory_id, cantidad, user_id, motivo)
        db: Sesión de base de datos

    Returns:
        ReservaResponse: Confirmación de reserva con cantidades actualizadas
    """
    try:
        logger.info(f"Reservando stock - inventory: {reserva.inventory_id}, cantidad: {reserva.cantidad}, user: {reserva.user_id}")
# Obtener inventario existente
        inventario = await DatabaseUtils.get_by_id(db, Inventory, reserva.inventory_id)
        
        if not inventario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventario con ID {reserva.inventory_id} no encontrado"
            )

        # Agregar motivo como nota si se proporciona
        if reserva.motivo:
            inventario.agregar_nota_almacen(
                f"[RESERVA] {reserva.motivo}",
                reserva.user_id
            )

        # Confirmar transacción
        await db.commit()
        await db.refresh(inventario)

        logger.info(f"Reserva exitosa - Reservado: {inventario.cantidad_reservada}, Disponible: {inventario.cantidad_disponible()}")

        # Construir response exitosa
        from datetime import datetime

        return ReservaResponse(
            success=True,
            message="Reserva realizada exitosamente",
            inventory_id=reserva.inventory_id,
            cantidad_reservada=inventario.cantidad_reservada,
            cantidad_disponible=inventario.cantidad_disponible(),
            cantidad_solicitada=reserva.cantidad,
            user_id=reserva.user_id,
            fecha_reserva=datetime.utcnow()
        )
            
        logger.info(f"Inventario encontrado: {inventario.get_ubicacion_completa()}, disponible: {inventario.cantidad_disponible()}")

        # Validar que hay stock suficiente disponible
        if not inventario.puede_satisfacer(reserva.cantidad):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente. Disponible: {inventario.cantidad_disponible()}, solicitado: {reserva.cantidad}"
            )

        # Realizar reserva usando método del modelo
        reserva_exitosa = inventario.reservar_cantidad(reserva.cantidad, reserva.user_id)

        if not reserva_exitosa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo realizar la reserva. Verifique disponibilidad."
            )
        
    except Exception as e:
        logger.error(f"Error en reserva de stock: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno procesando reserva de stock"
        )

@router.post(
    "/movimiento",
    response_model=MovimientoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar movimiento de inventario",
    description="Registrar entrada/salida de stock con actualización automática",
    tags=["inventory"]
)
async def registrar_movimiento(
    movimiento: MovimientoStockCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Registrar movimiento de entrada/salida en inventario.
    
    Args:
        movimiento: Datos del movimiento a registrar
        db: Sesión de base de datos
    
    Returns:
        Confirmación del movimiento registrado
    """
    try:
        logger.info(f"Registrando movimiento {movimiento.tipo_movimiento} para inventario {movimiento.inventory_id}")
        
        # 1. Buscar inventario existente
        result = await db.execute(
            select(Inventory).where(Inventory.id == movimiento.inventory_id)
        )
        inventario = result.scalar_one_or_none()
        
        if not inventario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventario con ID {movimiento.inventory_id} no encontrado"
            )
        
        # 2. Validar cantidad anterior coincide
        if inventario.cantidad != movimiento.cantidad_anterior:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cantidad anterior no coincide. Esperado: {inventario.cantidad}, Recibido: {movimiento.cantidad_anterior}"
            )
        
        # 3. Aplicar movimiento según tipo
        if movimiento.tipo_movimiento in [TipoMovimiento.INGRESO, TipoMovimiento.AJUSTE_POSITIVO]:
            # Entrada: diferencia positiva
            diferencia = movimiento.cantidad_nueva - movimiento.cantidad_anterior
            inventario.ajustar_stock(diferencia, movimiento.user_id)
        elif movimiento.tipo_movimiento == TipoMovimiento.AJUSTE_NEGATIVO:
            # Salida: diferencia negativa  
            diferencia = movimiento.cantidad_nueva - movimiento.cantidad_anterior
            inventario.ajustar_stock(diferencia, movimiento.user_id)
        else:
            # Otros tipos: actualización directa
            inventario.actualizar_stock(movimiento.cantidad_nueva, movimiento.user_id)
        
        # 4. Agregar observaciones si existen
        if movimiento.observaciones:
            inventario.agregar_nota_almacen(
                f"[{movimiento.tipo_movimiento}] {movimiento.observaciones}", 
                movimiento.user_id
            )
        
        # 5. Confirmar transacción
        await db.commit()
        await db.refresh(inventario)
        
        logger.info(f"Movimiento registrado exitosamente: {movimiento.tipo_movimiento}")
        
        return MovimientoResponse(
            success=True,
            message="Movimiento registrado exitosamente",
            inventory_id=movimiento.inventory_id,
            tipo_movimiento=movimiento.tipo_movimiento,
            cantidad_anterior=movimiento.cantidad_anterior,
            cantidad_nueva=inventario.cantidad,
            cantidad_disponible=inventario.cantidad_disponible(),
            fecha_movimiento=inventario.fecha_ultimo_movimiento
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en movimiento: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error registrando movimiento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno registrando movimiento"
        )


@router.get(
    "/ubicaciones",
    response_model=List[InventoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Consultar posiciones físicas de inventario",
    description="Obtener ubicaciones físicas disponibles en el almacén",
    tags=["inventory"]
)
async def get_ubicaciones(
    zona: Optional[str] = Query(None, description="Filtrar por zona específica"),
    disponible_solo: bool = Query(True, description="Solo ubicaciones con stock disponible"),
    limit: int = Query(100, ge=1, le=500, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    db: AsyncSession = Depends(get_db)
) -> List[InventoryResponse]:
    """
    Consultar posiciones físicas de inventario disponibles.

    Args:
        zona: Filtro opcional por zona del almacén
        disponible_solo: Si True, solo muestra ubicaciones con stock > 0
        limit: Límite de resultados (1-500)
        offset: Offset para paginación
        db: Sesión de base de datos

    Returns:
        List[InventoryResponse]: Lista de ubicaciones físicas con inventario
    """
    try:
        logger.info(f"Consultando ubicaciones - zona: {zona}, disponible_solo: {disponible_solo}")

        # Construir query base para ubicaciones
        stmt = select(Inventory).distinct(Inventory.zona, Inventory.estante, Inventory.posicion)

        # Filtro por zona si se especifica
        if zona:
            stmt = stmt.where(Inventory.zona == zona.upper())

        # Filtro por disponibilidad
        if disponible_solo:
            stmt = stmt.where(Inventory.cantidad > 0)

        # Paginación y orden por zona-estante-posicion
        stmt = stmt.order_by(Inventory.zona, Inventory.estante, Inventory.posicion)
        stmt = stmt.offset(offset).limit(limit)

        # Ejecutar query
        result = await db.execute(stmt)
        ubicaciones = result.scalars().all()

        logger.info(f"Ubicaciones encontradas: {len(ubicaciones)} registros")

        # Convertir a schema response
        return [InventoryResponse.model_validate(item) for item in ubicaciones]

    except Exception as e:
        logger.error(f"Error consultando ubicaciones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno consultando ubicaciones físicas"
        )


@router.put(
    "/{id}/ubicacion",
    response_model=InventoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Cambiar ubicación física de inventario",
    description="Actualizar posición física (zona, estante, posición) de un registro de inventario",
    tags=["inventory"]
)
async def cambiar_ubicacion(
    id: UUID = Path(..., description="ID del registro de inventario"),
    ubicacion_data: InventoryUpdate = Body(..., description="Nueva ubicación (zona, estante, posicion)"),
    db: AsyncSession = Depends(get_db)
) -> InventoryResponse:
    """
    Cambiar ubicación física de un registro de inventario.

    Args:
        id: ID del registro de inventario a actualizar
        ubicacion_data: Datos de la nueva ubicación (solo zona, estante, posicion)
        db: Sesión de base de datos
    """
    try:
        logger.info(f"Cambiando ubicación inventario ID: {id}")
        
        # Validar que se proporcionan campos de ubicación
        ubicacion_fields = ['zona', 'estante', 'posicion']
        provided_fields = [field for field in ubicacion_fields 
                          if getattr(ubicacion_data, field) is not None]
        
        if not provided_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe proporcionar al menos zona, estante o posición"
            )
        
        # Obtener inventario existente
        inventario = await DatabaseUtils.get_by_id(db, Inventory, id)
        
        if not inventario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventario con ID {id} no encontrado"
            )
            
        logger.info(f"Inventario encontrado: {inventario.get_ubicacion_completa()}")
        
        # Preparar datos para actualización (solo campos de ubicación)
        update_data = {}
        if ubicacion_data.zona is not None:
            update_data['zona'] = ubicacion_data.zona
        if ubicacion_data.estante is not None:
            update_data['estante'] = ubicacion_data.estante  
        if ubicacion_data.posicion is not None:
            update_data['posicion'] = ubicacion_data.posicion
            
        nueva_ubicacion = f"{update_data.get('zona', inventario.zona)}-{update_data.get('estante', inventario.estante)}-{update_data.get('posicion', inventario.posicion)}"
        logger.info(f"Nueva ubicación: {nueva_ubicacion}")
        
        # Actualizar inventario con manejo de constraint violation
        try:
            inventario_actualizado = await DatabaseUtils.update_record(
                db, Inventory, id, update_data
            )
            
            await db.commit()
            await db.refresh(inventario_actualizado)
            
            logger.info(f"Ubicación actualizada exitosamente: {inventario_actualizado.get_ubicacion_completa()}")
            return InventoryResponse.model_validate(inventario_actualizado)
            
        except IntegrityError as e:
            await db.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'uq_product_location' in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"La ubicación {nueva_ubicacion} ya está ocupada por este producto"
                )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Conflicto de integridad en la base de datos"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cambiando ubicación inventario {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno actualizando ubicación"
        )


@router.get(
    "/alertas",
    response_model=AlertasResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar alertas de inventario",
    description="Obtener productos con stock bajo y sin movimiento reciente",
    tags=["inventory"]
)
async def get_alertas_inventario(
    stock_minimo: int = Query(10, ge=1, le=1000, description="Umbral para stock bajo"),
    dias_sin_movimiento: int = Query(30, ge=1, le=365, description="Días sin movimiento para alerta"),
    tipo_alerta: Optional[TipoAlerta] = Query(None, description="Filtrar por tipo específico de alerta"),
    limit: int = Query(100, ge=1, le=500, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    db: AsyncSession = Depends(get_db)
) -> AlertasResponse:
    """
    Consultar alertas de inventario por stock bajo y productos sin movimiento.

    Args:
        stock_minimo: Umbral mínimo de stock disponible para generar alerta
        dias_sin_movimiento: Días sin movimiento para considerar producto inactivo
        tipo_alerta: Tipo específico de alerta a consultar
        limit: Límite de resultados (1-500)
        offset: Offset para paginación
        db: Sesión de base de datos

    Returns:
        AlertasResponse: Lista de alertas con metadatos por tipo
    """
    try:
        logger.info(f"Consultando alertas - stock_min: {stock_minimo}, dias: {dias_sin_movimiento}, tipo: {tipo_alerta}")

        # Importar datetime para cálculos
        from datetime import datetime, timedelta

        # Calcular fecha límite para "sin movimiento"
        fecha_limite = datetime.utcnow() - timedelta(days=dias_sin_movimiento)

        # Construir query base
        stmt = select(Inventory)

        # Condiciones de alertas
        condiciones_alertas = []

        # Definir condiciones según tipo de alerta
        if not tipo_alerta or tipo_alerta == TipoAlerta.STOCK_BAJO:
            condiciones_alertas.append(
                and_(Inventory.cantidad > 0, Inventory.cantidad <= stock_minimo)
            )

        if not tipo_alerta or tipo_alerta == TipoAlerta.SIN_MOVIMIENTO:
            condiciones_alertas.append(Inventory.fecha_ultimo_movimiento <= fecha_limite)

        if not tipo_alerta or tipo_alerta == TipoAlerta.STOCK_AGOTADO:
            condiciones_alertas.append(Inventory.cantidad == 0)

        # Para CRITICO: stock bajo Y sin movimiento
        if not tipo_alerta or tipo_alerta == TipoAlerta.CRITICO:
            condiciones_alertas.append(
                and_(
                    Inventory.cantidad > 0,
                    Inventory.cantidad <= stock_minimo,
                    Inventory.fecha_ultimo_movimiento <= fecha_limite
                )
            )

        # Aplicar condiciones con OR
        if condiciones_alertas:
            stmt = stmt.where(or_(*condiciones_alertas))
        else:
            # Si no hay condiciones, devolver empty
            stmt = stmt.where(Inventory.id == None)  # Resultado vacío

        # Paginación y orden
        stmt = stmt.order_by(Inventory.updated_at.desc()).offset(offset).limit(limit)

        # Ejecutar query
        result = await db.execute(stmt)
        alertas = result.scalars().all()

        logger.info(f"Alertas encontradas: {len(alertas)} registros")

        # Convertir a response schemas
        inventario_responses = [InventoryResponse.model_validate(item) for item in alertas]

        # Calcular metadata por tipo de alerta
        metadata = AlertasMetadata(
            total_alertas=len(alertas),
            stock_bajo=len([a for a in alertas if 0 < a.cantidad <= stock_minimo]),
            sin_movimiento=len([a for a in alertas if a.dias_desde_ultimo_movimiento() >= dias_sin_movimiento]),
            stock_agotado=len([a for a in alertas if a.cantidad == 0]),
            criticos=len([a for a in alertas if 0 < a.cantidad <= stock_minimo and a.dias_desde_ultimo_movimiento() >= dias_sin_movimiento])
        )

        return AlertasResponse(alertas=inventario_responses, metadata=metadata)


    except Exception as e:
        logger.error(f"Error consultando alertas de inventario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno consultando alertas de inventario"
        )