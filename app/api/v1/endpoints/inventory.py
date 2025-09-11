from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status, Path, Body
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database import get_async_db as get_db
from app.core.auth import get_current_user
from sqlalchemy import or_, and_, func
from enum import Enum

class TipoAlerta(str, Enum):
    """Tipos de alertas de inventario"""
    STOCK_BAJO = "STOCK_BAJO"
    SIN_MOVIMIENTO = "SIN_MOVIMIENTO"
    STOCK_AGOTADO = "STOCK_AGOTADO"
    CRITICO = "CRITICO"  # Combinación de stock bajo + sin movimiento
    PERDIDO = "PERDIDO"  # Producto perdido o extraviado
    DAÑADO = "DAÑADO"    # Producto dañado o defectuoso
from app.models.inventory import Inventory
from app.models.incidente_inventario import IncidenteInventario, TipoIncidente as TipoIncidenteModel, EstadoIncidente
from app.models.movimiento_stock import MovimientoStock, TipoMovimiento as TipoMovimientoModel
from app.models.movement_tracker import MovementTracker
from app.models.discrepancy_report import DiscrepancyReport, ReportType, ExportFormat, ReportStatus
from app.models.incoming_product_queue import IncomingProductQueue, QueuePriority, VerificationStatus, DelayReason
from app.schemas.inventory import InventoryResponse, MovimientoStockCreate, TipoMovimiento, MovimientoResponse, InventoryUpdate, AlertasResponse, ReservaStockCreate, ReservaResponse, LocationUpdateRequest, IncidenteCreate, IncidenteResponse, MovementTrackerResponse, DateRange, MovementAnalyticsResponse, IncomingProductQueueCreate, IncomingProductQueueUpdate, IncomingProductQueueResponse, QueueAssignmentRequest, QueueProcessingRequest, QueueCompletionRequest, QueueDelayRequest, QueueStatsResponse, QueueAnalyticsResponse
from app.models.inventory_audit import InventoryAudit, InventoryAuditItem, AuditStatus
from app.schemas.inventory_audit import (
    InventoryAuditCreate, InventoryAuditResponse, InventoryAuditDetailResponse,
    ConteoFisicoData, ProcesarConteo, ReconciliarDiscrepancia, AuditStatsResponse,
    DiscrepancyReportCreate, DiscrepancyReportResponse, DiscrepancyReportWithAnalysis,
    DiscrepancyReportListResponse, ReportStatsResponse
)
from app.utils.crud import DatabaseUtils

import logging
import io

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

        # Para PERDIDO: productos con incidentes de tipo PERDIDO
        if not tipo_alerta or tipo_alerta == TipoAlerta.PERDIDO:
            stmt_perdidos = select(IncidenteInventario.inventory_id).where(
                and_(
                    IncidenteInventario.tipo_incidente == TipoIncidenteModel.PERDIDO,
                    IncidenteInventario.estado != EstadoIncidente.CERRADO
                )
            )
            condiciones_alertas.append(Inventory.id.in_(stmt_perdidos))

        # Para DAÑADO: productos con incidentes de tipo DAÑADO
        if not tipo_alerta or tipo_alerta == TipoAlerta.DAÑADO:
            stmt_danados = select(IncidenteInventario.inventory_id).where(
                and_(
                    IncidenteInventario.tipo_incidente == TipoIncidenteModel.DAÑADO,
                    IncidenteInventario.estado != EstadoIncidente.CERRADO
                )
            )
            condiciones_alertas.append(Inventory.id.in_(stmt_danados))

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

        # Calcular conteos de incidentes activos
        stmt_perdidos_count = select(func.count()).select_from(IncidenteInventario).where(
            and_(
                IncidenteInventario.tipo_incidente == TipoIncidenteModel.PERDIDO,
                IncidenteInventario.estado != EstadoIncidente.CERRADO
            )
        )
        stmt_danados_count = select(func.count()).select_from(IncidenteInventario).where(
            and_(
                IncidenteInventario.tipo_incidente == TipoIncidenteModel.DAÑADO,
                IncidenteInventario.estado != EstadoIncidente.CERRADO
            )
        )
        
        perdidos_count = (await db.execute(stmt_perdidos_count)).scalar()
        danados_count = (await db.execute(stmt_danados_count)).scalar()

        # Calcular metadata por tipo de alerta
        metadata = AlertasMetadata(
            total_alertas=len(alertas),
            stock_bajo=len([a for a in alertas if 0 < a.cantidad <= stock_minimo]),
            sin_movimiento=len([a for a in alertas if a.dias_desde_ultimo_movimiento() >= dias_sin_movimiento]),
            stock_agotado=len([a for a in alertas if a.cantidad == 0]),
            criticos=len([a for a in alertas if 0 < a.cantidad <= stock_minimo and a.dias_desde_ultimo_movimiento() >= dias_sin_movimiento]),
            perdidos=perdidos_count,
            danados=danados_count
        )

        return AlertasResponse(alertas=inventario_responses, metadata=metadata)


    except Exception as e:
        logger.error(f"Error consultando alertas de inventario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno consultando alertas de inventario"
        )



# ===== ENDPOINTS DE AUDITORÍA =====

@router.post("/audits", response_model=InventoryAuditResponse)
async def crear_auditoria(
    audit_data: InventoryAuditCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Crear nueva auditoría de inventario"""
    try:
        # Crear auditoría
        new_audit = InventoryAudit(
            nombre=audit_data.nombre,
            descripcion=audit_data.descripcion,
            auditor_id=current_user.id,
            status=AuditStatus.INICIADA
        )
        db.add(new_audit)
        await db.flush()
        
        # Crear items de auditoría para inventarios seleccionados
        for inventory_id in audit_data.inventarios_ids:
            # Obtener datos del inventory
            inventory_result = await db.execute(
                select(Inventory).where(Inventory.id == inventory_id)
            )
            inventory = inventory_result.scalar_one_or_none()
            
            if inventory:
                audit_item = InventoryAuditItem(
                    audit_id=new_audit.id,
                    inventory_id=inventory_id,
                    cantidad_sistema=inventory.cantidad,
                    ubicacion_sistema=inventory.get_ubicacion_completa(),
                    condicion_sistema=inventory.condicion_producto
                )
                db.add(audit_item)
        
        # Cambiar status a EN_PROCESO
        new_audit.status = AuditStatus.EN_PROCESO
        await db.commit()
        await db.refresh(new_audit)
        
        return InventoryAuditResponse(
            id=new_audit.id,
            nombre=new_audit.nombre,
            descripcion=new_audit.descripcion,
            status=new_audit.status,
            fecha_inicio=new_audit.fecha_inicio,
            fecha_fin=new_audit.fecha_fin,
            total_items_auditados=new_audit.total_items_auditados,
            discrepancias_encontradas=new_audit.discrepancias_encontradas,
            valor_discrepancias=new_audit.valor_discrepancias,
            auditor_nombre=current_user.nombre
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando auditoría: {str(e)}"
        )



@router.get("/audits", response_model=List[InventoryAuditResponse])
async def listar_auditorias(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Listar auditorías con filtros"""
    from sqlalchemy import func
    
    query = select(InventoryAudit).order_by(InventoryAudit.fecha_inicio.desc())
    
    if status_filter:
        query = query.where(InventoryAudit.status == status_filter)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    audits = result.scalars().all()
    
    return [
        InventoryAuditResponse(
            id=audit.id,
            nombre=audit.nombre,
            descripcion=audit.descripcion,
            status=audit.status,
            fecha_inicio=audit.fecha_inicio,
            fecha_fin=audit.fecha_fin,
            total_items_auditados=audit.total_items_auditados,
            discrepancias_encontradas=audit.discrepancias_encontradas,
            valor_discrepancias=audit.valor_discrepancias,
            auditor_nombre=audit.auditor.nombre if audit.auditor else "Unknown"
        )
        for audit in audits
    ]

@router.post("/audits/{audit_id}/conteo", response_model=dict)
async def procesar_conteo_fisico(
    audit_id: UUID,
    conteo_data: ProcesarConteo,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Procesar conteo físico de un item"""
    # Obtener audit item
    result = await db.execute(
        select(InventoryAuditItem)
        .where(
            and_(
                InventoryAuditItem.audit_id == audit_id,
                InventoryAuditItem.id == conteo_data.audit_item_id
            )
        )
    )
    audit_item = result.scalar_one_or_none()
    
    if not audit_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item de auditoría no encontrado"
        )
    
    # Procesar conteo
    audit_item.procesar_conteo(
        cantidad_fisica=conteo_data.conteo_data.cantidad_fisica,
        ubicacion_fisica=conteo_data.conteo_data.ubicacion_fisica,
        condicion_fisica=conteo_data.conteo_data.condicion_fisica,
        notas=conteo_data.conteo_data.notas_conteo
    )
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Conteo procesado exitosamente",
        "tiene_discrepancia": audit_item.tiene_discrepancia,
        "tipo_discrepancia": audit_item.tipo_discrepancia
    }



@router.get("/audits/stats", response_model=AuditStatsResponse)
async def obtener_estadisticas_auditorias(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener estadísticas generales de auditorías"""
    from sqlalchemy import func
    
    # Total de auditorías
    total_result = await db.execute(select(func.count(InventoryAudit.id)))
    total_auditorias = total_result.scalar()
    
    # Auditorías pendientes
    pendientes_result = await db.execute(
        select(func.count(InventoryAudit.id))
        .where(InventoryAudit.status.in_(['INICIADA', 'EN_PROCESO']))
    )
    auditorias_pendientes = pendientes_result.scalar()
    
    # Última auditoría
    ultima_result = await db.execute(
        select(InventoryAudit.fecha_inicio)
        .order_by(InventoryAudit.fecha_inicio.desc())
        .limit(1)
    )
    ultima_auditoria = ultima_result.scalar()
    
    return AuditStatsResponse(
        total_auditorias=total_auditorias or 0,
        auditorias_pendientes=auditorias_pendientes or 0,
        discrepancias_sin_reconciliar=0,  # TODO: Implementar consulta específica
        valor_total_discrepancias=0.0,    # TODO: Implementar consulta específica
        ultima_auditoria=ultima_auditoria
    )


@router.put("/{inventory_id}/location", response_model=InventoryResponse)
async def update_inventory_location(
    inventory_id: UUID,
    location_data: LocationUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Actualizar ubicación de un elemento de inventario
    
    Permite cambiar la ubicación física de un producto en el almacén,
    validando que la nueva ubicación esté disponible y registrando
    el movimiento para auditoría.
    """
    logger.info(f"Actualizando ubicación de inventario {inventory_id} por usuario {current_user.id}")
    
    try:
        # 1. Buscar el item de inventario existente
        result = await db.execute(
            select(Inventory).where(Inventory.id == inventory_id)
        )
        inventory_item = result.scalar_one_or_none()
        
        if not inventory_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item de inventario no encontrado"
            )
        
        # 2. Validar que la nueva ubicación no esté ocupada por otro producto
        nueva_ubicacion = f"{location_data.zona}-{location_data.estante}-{location_data.posicion}"
        
        existing_location = await db.execute(
            select(Inventory).where(
                and_(
                    Inventory.zona == location_data.zona,
                    Inventory.estante == location_data.estante,
                    Inventory.posicion == location_data.posicion,
                    Inventory.id != inventory_id,  # Excluir el item actual
                    Inventory.cantidad > 0  # Solo verificar ubicaciones con stock
                )
            )
        )
        
        if existing_location.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La ubicación {nueva_ubicacion} ya está ocupada por otro producto"
            )
        
        # 3. Guardar ubicación anterior para auditoría
        ubicacion_anterior = inventory_item.get_ubicacion_completa()
        
        # 4. Actualizar la ubicación
        inventory_item.zona = location_data.zona
        inventory_item.estante = location_data.estante
        inventory_item.posicion = location_data.posicion
        inventory_item.updated_by_id = current_user.id
        
        # 5. Agregar observaciones si se proporcionaron
        if location_data.observaciones:
            notas_actuales = inventory_item.notas_almacen or ""
            nueva_nota = f"[{inventory_item.updated_at.strftime('%Y-%m-%d %H:%M')}] Cambio ubicación: {ubicacion_anterior} → {nueva_ubicacion}. {location_data.observaciones}"
            inventory_item.notas_almacen = f"{notas_actuales}\n{nueva_nota}".strip()
        
        # 6. Registrar movimiento de stock para auditoría
        movimiento = MovimientoStock(
            inventory_id=inventory_item.id,
            tipo_movimiento=TipoMovimiento.CAMBIO_UBICACION,
            cantidad_anterior=inventory_item.cantidad,
            cantidad_nueva=inventory_item.cantidad,  # La cantidad no cambia
            observaciones=f"Cambio de ubicación: {ubicacion_anterior} → {nueva_ubicacion}. {location_data.observaciones or ''}",
            user_id=current_user.id
        )
        db.add(movimiento)
        
        # 7. Guardar cambios
        await db.commit()
        await db.refresh(inventory_item)
        
        logger.info(f"Ubicación actualizada exitosamente: {ubicacion_anterior} → {nueva_ubicacion}")
        
        # 8. Retornar el item actualizado
        return InventoryResponse.model_validate(inventory_item)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error actualizando ubicación de inventario {inventory_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al actualizar ubicación"
        )


# Endpoints para Incidentes de Inventario
@router.post("/incidentes", response_model=IncidenteResponse)
async def reportar_incidente(
    incidente_data: IncidenteCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Reportar un nuevo incidente de inventario (producto perdido o dañado)
    """
    try:
        # 1. Verificar que el inventario existe
        inventory_result = await db.execute(
            select(Inventory).where(Inventory.id == str(incidente_data.inventory_id))
        )
        inventory_item = inventory_result.scalar_one_or_none()
        
        if not inventory_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventario con ID {incidente_data.inventory_id} no encontrado"
            )
        
        # 2. Crear el incidente
        nuevo_incidente = IncidenteInventario(
            inventory_id=str(incidente_data.inventory_id),
            tipo_incidente=incidente_data.tipo_incidente,
            descripcion=incidente_data.descripcion,
            reportado_por=current_user.email,
            fecha_incidente=incidente_data.fecha_incidente,
            estado=EstadoIncidente.REPORTADO
        )
        
        db.add(nuevo_incidente)
        
        # 3. Crear alerta automática
        # (Se podría implementar una lógica más compleja aquí)
        
        # 4. Actualizar estado del inventario si es necesario
        # Para productos perdidos, podríamos marcar cantidad como 0
        if incidente_data.tipo_incidente == TipoIncidenteModel.PERDIDO:
            # Registrar movimiento de ajuste
            movimiento = MovimientoStock(
                inventory_id=str(incidente_data.inventory_id),
                tipo_movimiento=TipoMovimiento.AJUSTE_NEGATIVO,
                cantidad_anterior=inventory_item.cantidad,
                cantidad_nueva=0,
                observaciones=f"Producto perdido - {incidente_data.descripcion}",
                user_id=current_user.id
            )
            db.add(movimiento)
            inventory_item.cantidad = 0
        
        # 5. Guardar cambios
        await db.commit()
        await db.refresh(nuevo_incidente)
        
        logger.info(f"Incidente reportado: {incidente_data.tipo_incidente} para inventario {incidente_data.inventory_id}")
        
        return IncidenteResponse.model_validate(nuevo_incidente)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error reportando incidente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al reportar incidente"
        )


@router.get("/incidentes", response_model=List[IncidenteResponse])
async def listar_incidentes(
    estado: Optional[EstadoIncidente] = None,
    tipo: Optional[TipoIncidenteModel] = None,
    skip: int = Query(default=0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(default=50, ge=1, le=100, description="Límite de registros a retornar"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Listar incidentes de inventario con filtros opcionales
    """
    try:
        # Construir la consulta base
        query = select(IncidenteInventario).order_by(IncidenteInventario.created_at.desc())
        
        # Aplicar filtros
        if estado:
            query = query.where(IncidenteInventario.estado == estado)
        
        if tipo:
            query = query.where(IncidenteInventario.tipo_incidente == tipo)
        
        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        
        # Ejecutar consulta
        result = await db.execute(query)
        incidentes = result.scalars().all()
        
        logger.info(f"Listados {len(incidentes)} incidentes con filtros: estado={estado}, tipo={tipo}")
        
        return [IncidenteResponse.model_validate(incidente) for incidente in incidentes]
        
    except Exception as e:
        logger.error(f"Error listando incidentes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al listar incidentes"
        )


@router.get("/movements/tracker/{movement_id}", response_model=List[MovementTrackerResponse])
async def get_movement_history(
    movement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtener historial detallado de un movimiento específico
    """
    try:
        # Verificar que el movimiento existe
        movement_query = select(MovimientoStock).where(MovimientoStock.id == movement_id)
        movement_result = await db.execute(movement_query)
        movement = movement_result.scalar_one_or_none()
        
        if not movement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movimiento no encontrado"
            )
        
        # Obtener historial de tracking
        query = select(MovementTracker).where(
            MovementTracker.movement_id == movement_id
        ).order_by(MovementTracker.action_timestamp.desc())
        
        result = await db.execute(query)
        tracking_history = result.scalars().all()
        
        logger.info(f"Obtenido historial de {len(tracking_history)} entradas para movimiento {movement_id}")
        
        return [MovementTrackerResponse.model_validate(track) for track in tracking_history]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo historial de movimiento {movement_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener historial"
        )


@router.get("/movements/analytics", response_model=MovementAnalyticsResponse)
async def get_movement_analytics(
    start_date: Optional[date] = Query(default=None, description="Fecha inicio (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="Fecha fin (YYYY-MM-DD)"),
    movement_type: Optional[str] = Query(default=None, description="Tipo de movimiento"),
    user_id: Optional[UUID] = Query(default=None, description="ID del usuario"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtener analytics de movimientos con filtros opcionales
    """
    try:
        # Construir query base
        query = select(MovimientoStock).join(MovementTracker)
        
        # Aplicar filtros de fecha
        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            query = query.where(MovimientoStock.fecha_movimiento >= start_datetime)
        
        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.where(MovimientoStock.fecha_movimiento <= end_datetime)
        
        # Aplicar filtros adicionales
        if movement_type:
            query = query.where(MovimientoStock.tipo_movimiento == movement_type)
        
        if user_id:
            query = query.where(MovimientoStock.user_id == user_id)
        
        # Ejecutar query
        result = await db.execute(query)
        movements = result.scalars().all()
        
        # Calcular analytics
        total_movements = len(movements)
        
        # Agrupar por tipo de movimiento
        movements_by_type = {}
        movements_by_user = {}
        movements_by_date = {}
        
        for movement in movements:
            # Por tipo
            tipo_key = movement.tipo_movimiento.value
            if tipo_key not in movements_by_type:
                movements_by_type[tipo_key] = 0
            movements_by_type[tipo_key] += 1
            
            # Por usuario
            user_key = str(movement.user_id) if movement.user_id else "Sistema"
            if user_key not in movements_by_user:
                movements_by_user[user_key] = 0
            movements_by_user[user_key] += 1
            
            # Por fecha
            date_key = movement.fecha_movimiento.strftime('%Y-%m-%d')
            if date_key not in movements_by_date:
                movements_by_date[date_key] = 0
            movements_by_date[date_key] += 1
        
        # Query para obtener el período de análisis
        date_range_query = select(
            func.min(MovimientoStock.fecha_movimiento).label('start_date'),
            func.max(MovimientoStock.fecha_movimiento).label('end_date')
        )
        
        if start_date or end_date or movement_type or user_id:
            if start_date:
                start_datetime = datetime.combine(start_date, datetime.min.time())
                date_range_query = date_range_query.where(MovimientoStock.fecha_movimiento >= start_datetime)
            if end_date:
                end_datetime = datetime.combine(end_date, datetime.max.time())
                date_range_query = date_range_query.where(MovimientoStock.fecha_movimiento <= end_datetime)
            if movement_type:
                date_range_query = date_range_query.where(MovimientoStock.tipo_movimiento == movement_type)
            if user_id:
                date_range_query = date_range_query.where(MovimientoStock.user_id == user_id)
        
        date_range_result = await db.execute(date_range_query)
        date_range = date_range_result.first()
        
        analytics = MovementAnalyticsResponse(
            date_range=DateRange(
                start_date=date_range.start_date.date() if date_range.start_date else None,
                end_date=date_range.end_date.date() if date_range.end_date else None
            ),
            total_movements=total_movements,
            movements_by_type=movements_by_type,
            movements_by_user=movements_by_user,
            movements_by_date=movements_by_date,
            filters_applied={
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "movement_type": movement_type,
                "user_id": str(user_id) if user_id else None
            }
        )
        
        logger.info(f"Analytics generado: {total_movements} movimientos analizados")
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error generando analytics de movimientos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al generar analytics"
        )


@router.get("/movements/export")
async def export_movements_history(
    format: str = Query("csv", pattern="^(csv|excel|json)$", description="Formato de exportación"),
    start_date: Optional[date] = Query(default=None, description="Fecha inicio (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="Fecha fin (YYYY-MM-DD)"),
    movement_type: Optional[str] = Query(default=None, description="Tipo de movimiento"),
    user_id: Optional[UUID] = Query(default=None, description="ID del usuario"),
    include_tracker: bool = Query(default=True, description="Incluir historial de tracking"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Exportar historial de movimientos en formato CSV, Excel o JSON
    """
    try:
        from fastapi.responses import StreamingResponse
        import io
        import csv
        import json
        
        # Construir query base para movimientos
        movements_query = select(MovimientoStock).order_by(MovimientoStock.fecha_movimiento.desc())
        
        # Aplicar filtros
        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            movements_query = movements_query.where(MovimientoStock.fecha_movimiento >= start_datetime)
        
        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            movements_query = movements_query.where(MovimientoStock.fecha_movimiento <= end_datetime)
        
        if movement_type:
            movements_query = movements_query.where(MovimientoStock.tipo_movimiento == movement_type)
        
        if user_id:
            movements_query = movements_query.where(MovimientoStock.user_id == user_id)
        
        # Ejecutar query
        movements_result = await db.execute(movements_query)
        movements = movements_result.scalars().all()
        
        # Preparar datos para exportación
        export_data = []
        
        for movement in movements:
            movement_data = {
                "id": str(movement.id),
                "inventory_id": str(movement.inventory_id),
                "tipo_movimiento": movement.tipo_movimiento.value,
                "cantidad_anterior": movement.cantidad_anterior,
                "cantidad_nueva": movement.cantidad_nueva,
                "diferencia": movement.cantidad_nueva - movement.cantidad_anterior,
                "user_id": str(movement.user_id) if movement.user_id else None,
                "observaciones": movement.observaciones,
                "fecha_movimiento": movement.fecha_movimiento.isoformat(),
                "referencia_externa": movement.referencia_externa,
                "lote": movement.lote,
                "ubicacion_origen": movement.ubicacion_origen,
                "ubicacion_destino": movement.ubicacion_destino,
                "created_at": movement.created_at.isoformat() if movement.created_at else None,
                "updated_at": movement.updated_at.isoformat() if movement.updated_at else None
            }
            
            # Incluir datos de tracking si se solicita
            if include_tracker:
                tracker_query = select(MovementTracker).where(
                    MovementTracker.movement_id == movement.id
                ).order_by(MovementTracker.action_timestamp.desc())
                
                tracker_result = await db.execute(tracker_query)
                trackers = tracker_result.scalars().all()
                
                # Agregar datos de tracking
                if trackers:
                    movement_data.update({
                        "total_tracking_entries": len(trackers),
                        "last_action": trackers[0].action_type if trackers else None,
                        "last_action_timestamp": trackers[0].action_timestamp.isoformat() if trackers else None,
                        "last_action_user": trackers[0].user_name if trackers else None,
                        "tracking_history": [
                            {
                                "action_type": track.action_type,
                                "user_name": track.user_name,
                                "action_timestamp": track.action_timestamp.isoformat(),
                                "ip_address": track.ip_address,
                                "notes": track.notes,
                                "changes": track.get_changes()
                            } for track in trackers
                        ]
                    })
            
            export_data.append(movement_data)
        
        # Generar el archivo según el formato
        if format == "json":
            output = io.StringIO()
            json.dump(export_data, output, indent=2, ensure_ascii=False)
            output.seek(0)
            
            response = StreamingResponse(
                io.BytesIO(output.getvalue().encode('utf-8')),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=movimientos_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                }
            )
            
        elif format == "csv":
            output = io.StringIO()
            
            if export_data:
                # Para CSV, aplanar los datos de tracking
                flattened_data = []
                for item in export_data:
                    base_item = {k: v for k, v in item.items() if k != 'tracking_history'}
                    
                    if include_tracker and 'tracking_history' in item and item['tracking_history']:
                        # Crear una fila por cada entrada de tracking
                        for i, track in enumerate(item['tracking_history']):
                            row = base_item.copy()
                            row.update({
                                f"tracking_{i+1}_action": track['action_type'],
                                f"tracking_{i+1}_user": track['user_name'],
                                f"tracking_{i+1}_timestamp": track['action_timestamp'],
                                f"tracking_{i+1}_ip": track['ip_address'],
                                f"tracking_{i+1}_notes": track['notes'],
                                f"tracking_{i+1}_changes": json.dumps(track['changes'], ensure_ascii=False)
                            })
                            flattened_data.append(row)
                    else:
                        flattened_data.append(base_item)
                
                if flattened_data:
                    fieldnames = flattened_data[0].keys()
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(flattened_data)
            
            output.seek(0)
            
            response = StreamingResponse(
                io.BytesIO(output.getvalue().encode('utf-8')),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=movimientos_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                }
            )
            
        elif format == "excel":
            try:
                import pandas as pd
                
                # Aplanar datos para Excel similar a CSV
                flattened_data = []
                for item in export_data:
                    base_item = {k: v for k, v in item.items() if k != 'tracking_history'}
                    
                    if include_tracker and 'tracking_history' in item and item['tracking_history']:
                        for i, track in enumerate(item['tracking_history']):
                            row = base_item.copy()
                            row.update({
                                f"tracking_{i+1}_action": track['action_type'],
                                f"tracking_{i+1}_user": track['user_name'],
                                f"tracking_{i+1}_timestamp": track['action_timestamp'],
                                f"tracking_{i+1}_ip": track['ip_address'],
                                f"tracking_{i+1}_notes": track['notes'],
                                f"tracking_{i+1}_changes": json.dumps(track['changes'], ensure_ascii=False)
                            })
                            flattened_data.append(row)
                    else:
                        flattened_data.append(base_item)
                
                # Crear DataFrame y exportar a Excel
                df = pd.DataFrame(flattened_data)
                output = io.BytesIO()
                
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Movimientos', index=False)
                
                output.seek(0)
                
                response = StreamingResponse(
                    output,
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={
                        "Content-Disposition": f"attachment; filename=movimientos_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    }
                )
                
            except ImportError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Pandas no está disponible para exportación Excel. Use CSV o JSON."
                )
        
        logger.info(f"Exportación {format} generada con {len(export_data)} movimientos")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en exportación de movimientos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al generar exportación"
        )


@router.get("/movements/recent", response_model=List[MovimientoResponse])
async def get_recent_movements(
    limit: int = Query(default=20, ge=1, le=100, description="Límite de movimientos a retornar"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtener movimientos recientes de inventario
    """
    try:
        # Construir query para movimientos recientes
        query = select(MovimientoStock).order_by(
            MovimientoStock.fecha_movimiento.desc()
        ).limit(limit)
        
        result = await db.execute(query)
        movements = result.scalars().all()
        
        logger.info(f"Obtenidos {len(movements)} movimientos recientes")
        
        return [MovimientoResponse.model_validate(movement) for movement in movements]
        
    except Exception as e:
        logger.error(f"Error obteniendo movimientos recientes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener movimientos recientes"
        )


# ============================================================================
# ENDPOINTS PARA REPORTES DE DISCREPANCIAS
# ============================================================================

@router.post("/audits/{audit_id}/reports", response_model=DiscrepancyReportResponse)
async def generate_discrepancy_report(
    audit_id: UUID,
    report_config: DiscrepancyReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Generar reporte de discrepancias para una auditoría específica
    """
    try:
        # Verificar que la auditoría existe
        audit_query = select(InventoryAudit).where(InventoryAudit.id == audit_id)
        audit_result = await db.execute(audit_query)
        audit = audit_result.scalar_one_or_none()
        
        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Auditoría no encontrada"
            )
        
        # Verificar que la auditoría está completada
        if audit.status not in [AuditStatus.COMPLETADA, AuditStatus.RECONCILIADA]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La auditoría debe estar completada para generar reportes"
            )
        
        # Crear registro del reporte
        new_report = DiscrepancyReport(
            audit_id=audit_id,
            report_type=report_config.report_type,
            report_name=report_config.report_name,
            description=report_config.description,
            generated_by_id=current_user.id,
            generated_by_name=current_user.full_name or current_user.email,
            date_range_start=report_config.date_range_start or audit.fecha_inicio,
            date_range_end=report_config.date_range_end or audit.fecha_fin or datetime.utcnow(),
            file_format=report_config.file_format,
            status=ReportStatus.GENERATING,
            report_config={
                "include_charts": report_config.include_charts,
                "include_recommendations": report_config.include_recommendations,
                "group_by_location": report_config.group_by_location,
                "group_by_category": report_config.group_by_category
            }
        )
        
        db.add(new_report)
        await db.flush()  # Para obtener el ID
        await db.refresh(new_report)
        
        # Aquí normalmente se iniciaría la generación asíncrona del reporte
        # Por ahora, vamos a simular la generación inmediata
        
        # Calcular métricas básicas desde los items de auditoría
        audit_items_query = select(InventoryAuditItem).where(
            InventoryAuditItem.audit_id == audit_id
        )
        audit_items_result = await db.execute(audit_items_query)
        audit_items = audit_items_result.scalars().all()
        
        # Calcular estadísticas
        total_discrepancies = sum(1 for item in audit_items if item.tiene_discrepancia)
        total_adjustments = sum(1 for item in audit_items if item.discrepancia_reconciliada)
        financial_impact = sum(item.valor_discrepancia or 0 for item in audit_items)
        items_analyzed = len(audit_items)
        accuracy_percentage = ((items_analyzed - total_discrepancies) / items_analyzed * 100) if items_analyzed > 0 else 100.0
        
        # Actualizar el reporte con las métricas calculadas
        new_report.total_discrepancies = total_discrepancies
        new_report.total_adjustments = total_adjustments
        new_report.financial_impact = financial_impact
        new_report.accuracy_percentage = accuracy_percentage
        new_report.items_analyzed = items_analyzed
        
        # Marcar como completado (simulando generación exitosa)
        import time
        generation_start = time.time()
        
        # Simular generación del archivo
        file_path = f"/tmp/discrepancy_report_{new_report.id}.{report_config.file_format.value.lower()}"
        file_size = 1024  # Simulado
        
        generation_time = time.time() - generation_start
        new_report.mark_as_completed(file_path, file_size, generation_time)
        
        await db.commit()
        
        logger.info(f"Reporte de discrepancias generado: {new_report.id} para auditoría {audit_id}")
        
        return DiscrepancyReportResponse.model_validate(new_report)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando reporte de discrepancias: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al generar reporte"
        )


@router.get("/reports/discrepancies", response_model=DiscrepancyReportListResponse)
async def list_discrepancy_reports(
    audit_id: Optional[UUID] = Query(None, description="Filtrar por auditoría"),
    report_type: Optional[ReportType] = Query(None, description="Filtrar por tipo de reporte"),
    status: Optional[ReportStatus] = Query(None, description="Filtrar por estado"),
    start_date: Optional[date] = Query(None, description="Fecha inicio creación"),
    end_date: Optional[date] = Query(None, description="Fecha fin creación"), 
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(20, ge=1, le=100, description="Elementos por página"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Listar reportes de discrepancias con filtros opcionales
    """
    try:
        # Construir la consulta base
        query = select(DiscrepancyReport).order_by(DiscrepancyReport.created_at.desc())
        count_query = select(func.count(DiscrepancyReport.id))
        
        # Aplicar filtros
        conditions = []
        
        if audit_id:
            conditions.append(DiscrepancyReport.audit_id == audit_id)
        
        if report_type:
            conditions.append(DiscrepancyReport.report_type == report_type)
        
        if status:
            conditions.append(DiscrepancyReport.status == status)
        
        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            conditions.append(DiscrepancyReport.created_at >= start_datetime)
        
        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            conditions.append(DiscrepancyReport.created_at <= end_datetime)
        
        # Aplicar condiciones si existen
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Obtener total de registros
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        # Aplicar paginación
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # Ejecutar consulta
        result = await db.execute(query)
        reports = result.scalars().all()
        
        # Calcular información de paginación
        has_next = (offset + page_size) < total_count
        has_previous = page > 1
        
        logger.info(f"Listados {len(reports)} reportes de discrepancias")
        
        return DiscrepancyReportListResponse(
            reports=[DiscrepancyReportResponse.model_validate(report) for report in reports],
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_next=has_next,
            has_previous=has_previous
        )
        
    except Exception as e:
        logger.error(f"Error listando reportes de discrepancias: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al listar reportes"
        )


@router.get("/reports/{report_id}", response_model=DiscrepancyReportWithAnalysis)
async def get_discrepancy_report_detail(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtener detalles completos de un reporte de discrepancias
    """
    try:
        # Buscar el reporte
        query = select(DiscrepancyReport).where(DiscrepancyReport.id == report_id)
        result = await db.execute(query)
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reporte no encontrado"
            )
        
        logger.info(f"Obtenido detalle de reporte: {report_id}")
        
        return DiscrepancyReportWithAnalysis.model_validate(report)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo detalle de reporte {report_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener reporte"
        )


@router.get("/reports/stats", response_model=ReportStatsResponse)
async def get_reports_statistics(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtener estadísticas generales de reportes de discrepancias
    """
    try:
        # Total de reportes
        total_reports_query = select(func.count(DiscrepancyReport.id))
        total_reports_result = await db.execute(total_reports_query)
        total_reports = total_reports_result.scalar()
        
        # Reportes por tipo
        reports_by_type_query = select(
            DiscrepancyReport.report_type,
            func.count(DiscrepancyReport.id).label('count')
        ).group_by(DiscrepancyReport.report_type)
        
        reports_by_type_result = await db.execute(reports_by_type_query)
        reports_by_type = {
            row.report_type.value: row.count 
            for row in reports_by_type_result.all()
        }
        
        # Reportes por estado
        reports_by_status_query = select(
            DiscrepancyReport.status,
            func.count(DiscrepancyReport.id).label('count')
        ).group_by(DiscrepancyReport.status)
        
        reports_by_status_result = await db.execute(reports_by_status_query)
        reports_by_status = {
            row.status.value: row.count 
            for row in reports_by_status_result.all()
        }
        
        # Tiempo promedio de generación
        avg_generation_query = select(
            func.avg(DiscrepancyReport.generation_time_seconds)
        ).where(
            DiscrepancyReport.generation_time_seconds.isnot(None)
        )
        avg_generation_result = await db.execute(avg_generation_query)
        avg_generation_time = avg_generation_result.scalar() or 0.0
        
        # Total de descargas
        total_downloads_query = select(func.sum(DiscrepancyReport.download_count))
        total_downloads_result = await db.execute(total_downloads_query)
        total_downloads = total_downloads_result.scalar() or 0
        
        # Espacio en disco utilizado
        disk_space_query = select(func.sum(DiscrepancyReport.file_size))
        disk_space_result = await db.execute(disk_space_query)
        disk_space_used = disk_space_result.scalar() or 0
        
        # Reportes este mes
        from datetime import datetime, timedelta
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        reports_this_month_query = select(func.count(DiscrepancyReport.id)).where(
            DiscrepancyReport.created_at >= start_of_month
        )
        reports_this_month_result = await db.execute(reports_this_month_query)
        reports_this_month = reports_this_month_result.scalar()
        
        stats = ReportStatsResponse(
            total_reports=total_reports,
            reports_by_type=reports_by_type,
            reports_by_status=reports_by_status,
            avg_generation_time=avg_generation_time,
            total_downloads=total_downloads,
            disk_space_used=disk_space_used,
            reports_this_month=reports_this_month
        )
        
        logger.info(f"Estadísticas de reportes generadas: {total_reports} reportes totales")
        
        return stats
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de reportes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener estadísticas"
        )


@router.get("/reports/{report_id}/download")
async def download_discrepancy_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Descargar archivo de reporte de discrepancias generado
    """
    try:
        from fastapi.responses import StreamingResponse, FileResponse
        import os
        from app.services.discrepancy_analyzer import DiscrepancyAnalyzer
        
        # Buscar el reporte
        query = select(DiscrepancyReport).where(DiscrepancyReport.id == report_id)
        result = await db.execute(query)
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reporte no encontrado"
            )
        
        # Verificar que está completado
        if not report.is_completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El reporte aún no está disponible para descarga"
            )
        
        # Verificar si el archivo existe, si no generarlo dinámicamente
        if not report.file_path or not report.file_exists:
            # Generar el archivo dinámicamente
            await _generate_report_file(report, db)
        
        # Verificar expiración
        if report.is_expired:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="El reporte ha expirado"
            )
        
        # Incrementar contador de descargas
        report.increment_download_count()
        await db.commit()
        
        # Generar contenido del archivo según el formato
        if report.file_format == ExportFormat.PDF:
            file_content = await _generate_pdf_content(report, db)
            media_type = "application/pdf"
            filename = f"reporte_discrepancias_{report.id}.pdf"
            
        elif report.file_format == ExportFormat.EXCEL:
            file_content = await _generate_excel_content(report, db)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"reporte_discrepancias_{report.id}.xlsx"
            
        elif report.file_format == ExportFormat.CSV:
            file_content = await _generate_csv_content(report, db)
            media_type = "text/csv"
            filename = f"reporte_discrepancias_{report.id}.csv"
            
        elif report.file_format == ExportFormat.JSON:
            file_content = await _generate_json_content(report, db)
            media_type = "application/json"
            filename = f"reporte_discrepancias_{report.id}.json"
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de reporte no soportado"
            )
        
        logger.info(f"Reporte descargado: {report_id} por usuario {current_user.email}")
        
        # Retornar archivo como streaming response
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(file_content))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error descargando reporte {report_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al descargar reporte"
        )


# Funciones auxiliares para generación de archivos

async def _generate_report_file(report: DiscrepancyReport, db: AsyncSession):
    """Generar archivo de reporte si no existe"""
    # Esta función sería llamada para generar archivos faltantes
    pass

async def _generate_pdf_content(report: DiscrepancyReport, db: AsyncSession) -> bytes:
    """Generar contenido PDF del reporte"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        import io
        from datetime import datetime
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph(f"Reporte de Discrepancias: {report.report_name}", title_style))
        story.append(Spacer(1, 12))
        
        # Información del reporte
        info_data = [
            ["Tipo de Reporte:", report.report_type.value],
            ["Generado por:", report.generated_by_name],
            ["Fecha de generación:", format(report.created_at, '%d/%m/%Y %H:%M')],
            ["Período analizado:", f"{format(report.date_range_start, '%d/%m/%Y')} - {format(report.date_range_end, '%d/%m/%Y')}"],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Resumen ejecutivo
        story.append(Paragraph("Resumen Ejecutivo", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        summary_data = [
            ["Métrica", "Valor"],
            ["Items Analizados", str(report.items_analyzed)],
            ["Total de Discrepancias", str(report.total_discrepancies)],
            ["Total de Ajustes", str(report.total_adjustments)],
            ["Porcentaje de Precisión", f"{report.accuracy_percentage:.2f}%"],
            ["Impacto Financiero", f"${report.financial_impact:.2f}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Análisis detallado (si existe)
        if report.analysis_data:
            story.append(Paragraph("Análisis Detallado", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Aquí se agregarían más detalles del análisis
            story.append(Paragraph("Los datos de análisis detallado están disponibles en el sistema.", styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=1
        )
        story.append(Paragraph("Generado con MeStore - Sistema de Gestión de Inventario", footer_style))
        
        # Construir PDF
        doc.build(story)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
        
    except ImportError:
        # Si reportlab no está disponible, generar PDF simple
        simple_content = f"""
REPORTE DE DISCREPANCIAS
========================

Reporte: {report.report_name}
Tipo: {report.report_type.value}
Generado por: {report.generated_by_name}
Fecha: {format(report.created_at, '%d/%m/%Y %H:%M')}

RESUMEN:
- Items Analizados: {report.items_analyzed}
- Discrepancias: {report.total_discrepancies}
- Ajustes: {report.total_adjustments}
- Precisión: {report.accuracy_percentage:.2f}%
- Impacto Financiero: ${report.financial_impact:.2f}

Generado con MeStore
"""
        return simple_content.encode('utf-8')

async def _generate_excel_content(report: DiscrepancyReport, db: AsyncSession) -> bytes:
    """Generar contenido Excel del reporte"""
    try:
        import pandas as pd
        import io
        from datetime import datetime
        
        # Crear DataFrame con datos del reporte
        summary_data = {
            'Métrica': [
                'Items Analizados',
                'Total de Discrepancias', 
                'Total de Ajustes',
                'Porcentaje de Precisión',
                'Impacto Financiero'
            ],
            'Valor': [
                report.items_analyzed,
                report.total_discrepancies,
                report.total_adjustments,
                f"{report.accuracy_percentage:.2f}%",
                f"${report.financial_impact:.2f}"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        
        # Información del reporte
        info_data = {
            'Campo': [
                'Nombre del Reporte',
                'Tipo de Reporte',
                'Generado por',
                'Fecha de Generación',
                'Período Inicio',
                'Período Fin'
            ],
            'Valor': [
                report.report_name,
                report.report_type.value,
                report.generated_by_name,
                report.created_at.strftime('%d/%m/%Y %H:%M'),
                report.date_range_start.strftime('%d/%m/%Y'),
                report.date_range_end.strftime('%d/%m/%Y')
            ]
        }
        
        info_df = pd.DataFrame(info_data)
        
        # Crear archivo Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            info_df.to_excel(writer, sheet_name='Información', index=False)
            summary_df.to_excel(writer, sheet_name='Resumen', index=False)
            
            # Si hay datos de análisis, agregarlos
            if report.analysis_data:
                analysis_df = pd.DataFrame([{
                    'Análisis': 'Datos disponibles',
                    'Estado': 'Completado'
                }])
                analysis_df.to_excel(writer, sheet_name='Análisis', index=False)
        
        return output.getvalue()
        
    except ImportError:
        # Fallback a CSV si pandas no está disponible
        return await _generate_csv_content(report, db)

async def _generate_csv_content(report: DiscrepancyReport, db: AsyncSession) -> bytes:
    """Generar contenido CSV del reporte"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['REPORTE DE DISCREPANCIAS'])
    writer.writerow([])
    
    # Información del reporte
    writer.writerow(['INFORMACIÓN DEL REPORTE'])
    writer.writerow(['Nombre', report.report_name])
    writer.writerow(['Tipo', report.report_type.value])
    writer.writerow(['Generado por', report.generated_by_name])
    writer.writerow(['Fecha', report.created_at.strftime('%d/%m/%Y %H:%M')])
    writer.writerow(['Período', f"{report.date_range_start.strftime('%d/%m/%Y')} - {report.date_range_end.strftime('%d/%m/%Y')}"])
    writer.writerow([])
    
    # Resumen
    writer.writerow(['RESUMEN'])
    writer.writerow(['Métrica', 'Valor'])
    writer.writerow(['Items Analizados', report.items_analyzed])
    writer.writerow(['Total de Discrepancias', report.total_discrepancies])
    writer.writerow(['Total de Ajustes', report.total_adjustments])
    writer.writerow(['Porcentaje de Precisión', f"{report.accuracy_percentage:.2f}%"])
    writer.writerow(['Impacto Financiero', f"${report.financial_impact:.2f}"])
    
    return output.getvalue().encode('utf-8')

async def _generate_json_content(report: DiscrepancyReport, db: AsyncSession) -> bytes:
    """Generar contenido JSON del reporte"""
    import json
    
    report_data = {
        "report_info": {
            "id": str(report.id),
            "name": report.report_name,
            "type": report.report_type.value,
            "generated_by": report.generated_by_name,
            "generated_at": report.created_at.isoformat(),
            "period": {
                "start": report.date_range_start.isoformat(),
                "end": report.date_range_end.isoformat()
            }
        },
        "summary": {
            "items_analyzed": report.items_analyzed,
            "total_discrepancies": report.total_discrepancies,
            "total_adjustments": report.total_adjustments,
            "accuracy_percentage": round(report.accuracy_percentage, 2),
            "financial_impact": round(report.financial_impact, 2)
        },
        "analysis_data": report.analysis_data,
        "report_config": report.report_config,
        "metadata": {
            "download_count": report.download_count,
            "file_format": report.file_format.value,
            "generation_time_seconds": report.generation_time_seconds,
            "file_size": report.file_size
        }
    }
    
    return json.dumps(report_data, indent=2, ensure_ascii=False).encode('utf-8')


# ================================================================================================
# INCOMING PRODUCT QUEUE ENDPOINTS - Sistema de Gestión de Cola de Productos Entrantes
# ================================================================================================

@router.get(
    "/queue/incoming-products",
    status_code=status.HTTP_200_OK,
    summary="Listar productos en cola de entrada",
    description="Obtener lista de productos en tránsito pendientes de verificación con filtros avanzados"
)
async def get_incoming_products_queue(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    # Filtros de estado y prioridad
    verification_status: Optional[VerificationStatus] = Query(None, description="Filtrar por estado de verificación"),
    priority: Optional[QueuePriority] = Query(None, description="Filtrar por prioridad"),
    assigned_to: Optional[UUID] = Query(None, description="Filtrar por usuario asignado"),
    # Filtros de vendor y fechas
    vendor_id: Optional[UUID] = Query(None, description="Filtrar por vendor"),
    overdue_only: bool = Query(False, description="Solo productos vencidos"),
    delayed_only: bool = Query(False, description="Solo productos retrasados"),
    # Paginación
    skip: int = Query(0, ge=0, description="Elementos a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de elementos")
):
    """
    Obtener lista de productos en cola de entrada con filtros avanzados.
    
    Permite filtrar por estado, prioridad, asignación y fechas.
    Incluye información calculada como días en cola y tiempo de procesamiento.
    """
    try:
        # Construir query base
        query = select(IncomingProductQueue)
        
        # Aplicar filtros
        if verification_status:
            query = query.filter(IncomingProductQueue.verification_status == verification_status)
        
        if priority:
            query = query.filter(IncomingProductQueue.priority == priority)
            
        if assigned_to:
            query = query.filter(IncomingProductQueue.assigned_to == assigned_to)
            
        if vendor_id:
            query = query.filter(IncomingProductQueue.vendor_id == vendor_id)
            
        if overdue_only:
            query = query.filter(IncomingProductQueue.deadline < func.now())
            
        if delayed_only:
            query = query.filter(IncomingProductQueue.is_delayed == True)
        
        # Ordenar por prioridad y fecha de creación
        query = query.order_by(
            IncomingProductQueue.priority.desc(),
            IncomingProductQueue.created_at.desc()
        )
        
        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        
        # Ejecutar query
        result = await db.execute(query)
        queue_items = result.scalars().all()
        
        # Respuesta manual robusta
        response_items = []
        for item in queue_items:
            try:
                # Solo campos básicos sin propiedades calculadas problemáticas
                basic_item = {
                    "id": str(item.id),
                    "product_id": str(item.product_id) if item.product_id else None,
                    "vendor_id": str(item.vendor_id) if item.vendor_id else None,
                    "tracking_number": item.tracking_number,
                    "verification_status": item.verification_status.value if hasattr(item.verification_status, 'value') else str(item.verification_status),
                    "priority": item.priority.value if hasattr(item.priority, 'value') else str(item.priority),
                    "is_delayed": bool(item.is_delayed) if item.is_delayed is not None else False,
                    "verification_attempts": item.verification_attempts or 0,
                    "carrier": item.carrier,
                    "expected_arrival": item.expected_arrival.isoformat() if item.expected_arrival else None,
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                    "updated_at": item.updated_at.isoformat() if item.updated_at else None,
                    "assigned_to": str(item.assigned_to) if item.assigned_to else None,
                    "assigned_at": item.assigned_at.isoformat() if item.assigned_at else None,
                    "deadline": item.deadline.isoformat() if item.deadline else None,
                    "notes": item.notes,
                    "verification_notes": item.verification_notes,
                    "quality_score": item.quality_score,
                    "quality_issues": item.quality_issues,
                    "processing_started_at": item.processing_started_at.isoformat() if item.processing_started_at else None,
                    "processing_completed_at": item.processing_completed_at.isoformat() if item.processing_completed_at else None,
                    "actual_arrival": item.actual_arrival.isoformat() if item.actual_arrival else None,
                    "delay_reason": item.delay_reason.value if item.delay_reason and hasattr(item.delay_reason, 'value') else None,
                    # Campos calculados - versión segura
                    "days_in_queue": 0,
                    "is_overdue": False,
                    "status_display": item.verification_status.value if hasattr(item.verification_status, 'value') else str(item.verification_status),
                    "priority_display": item.priority.value if hasattr(item.priority, 'value') else str(item.priority),
                    "is_high_priority": item.priority.value in ['HIGH', 'CRITICAL', 'EXPEDITED'] if hasattr(item.priority, 'value') else False,
                    "processing_time_hours": None
                }
                response_items.append(basic_item)
            except Exception as e:
                # Skip problematic items but continue
                continue
        
        return response_items
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@router.post(
    "/queue/incoming-products",
    response_model=IncomingProductQueueResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear entrada en cola de productos",
    description="Agregar producto en tránsito a la cola de verificación"
)
async def create_queue_entry(
    queue_data: IncomingProductQueueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Crear nueva entrada en la cola de productos entrantes.
    
    Registra un producto en tránsito para seguimiento y verificación.
    Calcula automáticamente deadline si no se proporciona.
    """
    try:
        logger.info(f"Creando entrada en cola - Producto: {queue_data.product_id}")
        
        # Verificar que el producto existe y está en estado TRANSITO
        from app.models.product import Product, ProductStatus
        
        product_query = select(Product).filter(Product.id == queue_data.product_id)
        product_result = await db.execute(product_query)
        product = product_result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        if product.status != ProductStatus.TRANSITO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo productos en tránsito pueden ser agregados a la cola"
            )
        
        # Verificar que el vendor existe
        from app.models.user import User, UserType
        
        vendor_query = select(User).filter(
            User.id == queue_data.vendor_id,
            User.user_type == UserType.VENDOR
        )
        vendor_result = await db.execute(vendor_query)
        vendor = vendor_result.scalar_one_or_none()
        
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor no encontrado"
            )
        
        # Verificar que no existe ya una entrada para este producto
        existing_query = select(IncomingProductQueue).filter(
            IncomingProductQueue.product_id == queue_data.product_id,
            IncomingProductQueue.verification_status.in_([
                VerificationStatus.PENDING,
                VerificationStatus.ASSIGNED, 
                VerificationStatus.IN_PROGRESS,
                VerificationStatus.QUALITY_CHECK,
                VerificationStatus.APPROVED
            ])
        )
        existing_result = await db.execute(existing_query)
        existing_entry = existing_result.scalar_one_or_none()
        
        if existing_entry:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una entrada activa para este producto en la cola"
            )
        
        # Crear entrada en cola
        queue_entry = IncomingProductQueue(**queue_data.model_dump())
        db.add(queue_entry)
        
        await db.commit()
        await db.refresh(queue_entry)
        
        # Convertir a response
        entry_dict = queue_entry.to_dict()
        response = IncomingProductQueueResponse(**entry_dict)
        
        logger.info(f"Entrada en cola creada exitosamente - ID: {queue_entry.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creando entrada en cola: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/queue/incoming-products/{entry_id}",
    response_model=IncomingProductQueueResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener entrada específica de cola",
    description="Obtener detalles completos de una entrada en la cola de productos"
)
async def get_queue_entry(
    entry_id: UUID = Path(..., description="ID de la entrada en cola"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtener detalles completos de una entrada específica en la cola."""
    try:
        query = select(IncomingProductQueue).filter(IncomingProductQueue.id == entry_id)
        result = await db.execute(query)
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entrada en cola no encontrada"
            )
        
        entry_dict = entry.to_dict()
        return IncomingProductQueueResponse(**entry_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo entrada de cola: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.put(
    "/queue/incoming-products/{entry_id}",
    response_model=IncomingProductQueueResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar entrada de cola",
    description="Actualizar información de una entrada en la cola de productos"
)
async def update_queue_entry(
    entry_id: UUID = Path(..., description="ID de la entrada en cola"),
    update_data: IncomingProductQueueUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Actualizar información de una entrada en la cola."""
    try:
        query = select(IncomingProductQueue).filter(IncomingProductQueue.id == entry_id)
        result = await db.execute(query)
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entrada en cola no encontrada"
            )
        
        # Actualizar campos proporcionados
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(entry, field, value)
        
        # Actualizar timestamp de modificación
        entry.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(entry)
        
        entry_dict = entry.to_dict()
        return IncomingProductQueueResponse(**entry_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error actualizando entrada de cola: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/queue/incoming-products/{entry_id}/assign",
    response_model=IncomingProductQueueResponse,
    status_code=status.HTTP_200_OK,
    summary="Asignar producto a verificador",
    description="Asignar una entrada de cola a un usuario para verificación"
)
async def assign_queue_entry(
    entry_id: UUID = Path(..., description="ID de la entrada en cola"),
    assignment_data: QueueAssignmentRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Asignar producto en cola a un verificador."""
    try:
        query = select(IncomingProductQueue).filter(IncomingProductQueue.id == entry_id)
        result = await db.execute(query)
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entrada en cola no encontrada"
            )
        
        # Verificar que el usuario asignado existe
        from app.models.user import User
        
        user_query = select(User).filter(User.id == assignment_data.assigned_to)
        user_result = await db.execute(user_query)
        assigned_user = user_result.scalar_one_or_none()
        
        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario asignado no encontrado"
            )
        
        # Asignar usando método del modelo
        entry.assign_to_user(assignment_data.assigned_to, assignment_data.notes)
        
        await db.commit()
        await db.refresh(entry)
        
        entry_dict = entry.to_dict()
        return IncomingProductQueueResponse(**entry_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error asignando entrada de cola: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/queue/incoming-products/{entry_id}/start-processing",
    response_model=IncomingProductQueueResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar procesamiento de verificación",
    description="Marcar una entrada como en procesamiento de verificación"
)
async def start_queue_processing(
    entry_id: UUID = Path(..., description="ID de la entrada en cola"),
    processing_data: QueueProcessingRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Iniciar procesamiento de verificación de un producto en cola."""
    try:
        query = select(IncomingProductQueue).filter(IncomingProductQueue.id == entry_id)
        result = await db.execute(query)
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entrada en cola no encontrada"
            )
        
        if entry.verification_status not in [VerificationStatus.ASSIGNED, VerificationStatus.PENDING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden procesar entradas asignadas o pendientes"
            )
        
        # Iniciar procesamiento usando método del modelo
        entry.start_processing(processing_data.notes)
        
        await db.commit()
        await db.refresh(entry)
        
        entry_dict = entry.to_dict()
        return IncomingProductQueueResponse(**entry_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error iniciando procesamiento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/queue/incoming-products/{entry_id}/complete",
    response_model=IncomingProductQueueResponse,
    status_code=status.HTTP_200_OK,
    summary="Completar verificación de producto",
    description="Completar la verificación de un producto (aprobado o rechazado)"
)
async def complete_queue_verification(
    entry_id: UUID = Path(..., description="ID de la entrada en cola"),
    completion_data: QueueCompletionRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Completar verificación de un producto en cola."""
    try:
        query = select(IncomingProductQueue).filter(IncomingProductQueue.id == entry_id)
        result = await db.execute(query)
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entrada en cola no encontrada"
            )
        
        if entry.verification_status not in [VerificationStatus.IN_PROGRESS, VerificationStatus.QUALITY_CHECK]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden completar entradas en proceso"
            )
        
        # Completar verificación usando método del modelo
        entry.complete_verification(
            completion_data.approved,
            completion_data.quality_score,
            completion_data.notes
        )
        
        # Si fue aprobado, actualizar el estado del producto a VERIFICADO
        if completion_data.approved:
            from app.models.product import Product, ProductStatus
            
            product_query = select(Product).filter(Product.id == entry.product_id)
            product_result = await db.execute(product_query)
            product = product_result.scalar_one_or_none()
            
            if product:
                product.status = ProductStatus.VERIFICADO
                product.updated_at = datetime.utcnow()
                
                # Marcar entrada como completada
                entry.verification_status = VerificationStatus.COMPLETED
        
        await db.commit()
        await db.refresh(entry)
        
        entry_dict = entry.to_dict()
        return IncomingProductQueueResponse(**entry_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error completando verificación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/queue/incoming-products/{entry_id}/mark-delayed",
    response_model=IncomingProductQueueResponse,
    status_code=status.HTTP_200_OK,
    summary="Marcar producto como retrasado",
    description="Marcar una entrada como retrasada con razón específica"
)
async def mark_queue_delayed(
    entry_id: UUID = Path(..., description="ID de la entrada en cola"),
    delay_data: QueueDelayRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Marcar un producto en cola como retrasado."""
    try:
        query = select(IncomingProductQueue).filter(IncomingProductQueue.id == entry_id)
        result = await db.execute(query)
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entrada en cola no encontrada"
            )
        
        # Marcar como retrasado usando método del modelo
        entry.mark_as_delayed(delay_data.delay_reason, delay_data.notes)
        
        await db.commit()
        await db.refresh(entry)
        
        entry_dict = entry.to_dict()
        return IncomingProductQueueResponse(**entry_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error marcando como retrasado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/queue/stats",
    response_model=QueueStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener estadísticas de cola",
    description="Obtener métricas y estadísticas de la cola de productos entrantes"
)
async def get_queue_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    vendor_id: Optional[UUID] = Query(None, description="Filtrar por vendor")
):
    """Obtener estadísticas completas de la cola de productos entrantes."""
    try:
        logger.info("Generando estadísticas de cola de productos")
        
        # Query base
        base_query = select(IncomingProductQueue)
        if vendor_id:
            base_query = base_query.filter(IncomingProductQueue.vendor_id == vendor_id)
        
        # Total de elementos
        total_query = select(func.count(IncomingProductQueue.id))
        if vendor_id:
            total_query = total_query.filter(IncomingProductQueue.vendor_id == vendor_id)
        
        total_result = await db.execute(total_query)
        total_items = total_result.scalar()
        
        # Contar por estados
        stats_queries = {
            'pending': base_query.filter(IncomingProductQueue.verification_status == VerificationStatus.PENDING),
            'assigned': base_query.filter(IncomingProductQueue.verification_status == VerificationStatus.ASSIGNED),
            'in_progress': base_query.filter(IncomingProductQueue.verification_status == VerificationStatus.IN_PROGRESS),
            'completed': base_query.filter(IncomingProductQueue.verification_status == VerificationStatus.COMPLETED),
            'overdue': base_query.filter(IncomingProductQueue.deadline < func.now()),
            'delayed': base_query.filter(IncomingProductQueue.is_delayed == True)
        }
        
        stats = {}
        for stat_name, query in stats_queries.items():
            count_query = select(func.count()).select_from(query.subquery())
            result = await db.execute(count_query)
            stats[stat_name] = result.scalar()
        
        # Calcular tiempo promedio de procesamiento
        processing_time_query = select(
            func.avg(
                func.extract('epoch', IncomingProductQueue.processing_completed_at - IncomingProductQueue.processing_started_at) / 3600
            )
        ).filter(
            IncomingProductQueue.processing_completed_at.isnot(None),
            IncomingProductQueue.processing_started_at.isnot(None)
        )
        
        if vendor_id:
            processing_time_query = processing_time_query.filter(IncomingProductQueue.vendor_id == vendor_id)
        
        avg_processing_result = await db.execute(processing_time_query)
        average_processing_time = avg_processing_result.scalar() or 0.0
        
        # Calcular eficiencia de la cola (completados vs totales activos)
        active_items = total_items - stats['completed']
        queue_efficiency = (stats['completed'] / total_items * 100) if total_items > 0 else 100.0
        
        return QueueStatsResponse(
            total_items=total_items,
            pending=stats['pending'],
            assigned=stats['assigned'],
            in_progress=stats['in_progress'],
            completed=stats['completed'],
            overdue=stats['overdue'],
            delayed=stats['delayed'],
            average_processing_time=round(average_processing_time, 2),
            queue_efficiency=round(queue_efficiency, 2)
        )
        
    except Exception as e:
        logger.error(f"Error generando estadísticas de cola: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/queue/analytics",
    response_model=QueueAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener analytics completo de cola",
    description="Obtener análisis completo de tendencias y performance de la cola"
)
async def get_queue_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365, description="Días de análisis"),
    vendor_id: Optional[UUID] = Query(None, description="Filtrar por vendor")
):
    """Obtener analytics completo de la cola de productos entrantes."""
    try:
        logger.info(f"Generando analytics de cola - Últimos {days} días")
        
        # Fecha de inicio para análisis
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Query base con filtro de fechas
        base_query = select(IncomingProductQueue).filter(
            IncomingProductQueue.created_at >= start_date
        )
        
        if vendor_id:
            base_query = base_query.filter(IncomingProductQueue.vendor_id == vendor_id)
        
        # Obtener estadísticas básicas
        stats_response = await get_queue_stats(db, current_user, vendor_id)
        
        # Distribución por prioridad
        priority_query = select(
            IncomingProductQueue.priority,
            func.count(IncomingProductQueue.id).label('count')
        ).filter(
            IncomingProductQueue.created_at >= start_date
        ).group_by(IncomingProductQueue.priority)
        
        if vendor_id:
            priority_query = priority_query.filter(IncomingProductQueue.vendor_id == vendor_id)
        
        priority_result = await db.execute(priority_query)
        priority_distribution = {str(row.priority): row.count for row in priority_result}
        
        # Distribución por estado
        status_query = select(
            IncomingProductQueue.verification_status,
            func.count(IncomingProductQueue.id).label('count')
        ).filter(
            IncomingProductQueue.created_at >= start_date
        ).group_by(IncomingProductQueue.verification_status)
        
        if vendor_id:
            status_query = status_query.filter(IncomingProductQueue.vendor_id == vendor_id)
        
        status_result = await db.execute(status_query)
        status_distribution = {str(row.verification_status): row.count for row in status_result}
        
        # Performance por vendor (si no se filtra por vendor específico)
        vendor_performance = {}
        if not vendor_id:
            from app.models.user import User
            
            vendor_query = select(
                User.nombre.label('vendor_name'),
                func.count(IncomingProductQueue.id).label('total_items'),
                func.avg(
                    func.extract('epoch', IncomingProductQueue.processing_completed_at - IncomingProductQueue.processing_started_at) / 3600
                ).label('avg_processing_time'),
                func.count(
                    func.case((IncomingProductQueue.verification_status == VerificationStatus.COMPLETED, 1))
                ).label('completed_items')
            ).select_from(
                IncomingProductQueue.__table__.join(User.__table__, IncomingProductQueue.vendor_id == User.id)
            ).filter(
                IncomingProductQueue.created_at >= start_date
            ).group_by(User.nombre)
            
            vendor_result = await db.execute(vendor_query)
            for row in vendor_result:
                completion_rate = (row.completed_items / row.total_items * 100) if row.total_items > 0 else 0
                vendor_performance[row.vendor_name] = {
                    'total_items': row.total_items,
                    'completed_items': row.completed_items,
                    'avg_processing_time': round(row.avg_processing_time or 0, 2),
                    'completion_rate': round(completion_rate, 2)
                }
        
        # Tendencias de procesamiento por día
        processing_trends_query = select(
            func.date(IncomingProductQueue.created_at).label('date'),
            func.count(IncomingProductQueue.id).label('created'),
            func.count(
                func.case((IncomingProductQueue.verification_status == VerificationStatus.COMPLETED, 1))
            ).label('completed')
        ).filter(
            IncomingProductQueue.created_at >= start_date
        ).group_by(func.date(IncomingProductQueue.created_at))
        
        if vendor_id:
            processing_trends_query = processing_trends_query.filter(IncomingProductQueue.vendor_id == vendor_id)
        
        trends_result = await db.execute(processing_trends_query)
        processing_trends = {}
        for row in trends_result:
            date_str = row.date.strftime('%Y-%m-%d')
            processing_trends[date_str] = {
                'created': row.created,
                'completed': row.completed
            }
        
        # Top causas de retraso
        delay_query = select(
            IncomingProductQueue.delay_reason,
            func.count(IncomingProductQueue.id).label('count')
        ).filter(
            IncomingProductQueue.is_delayed == True,
            IncomingProductQueue.delay_reason.isnot(None),
            IncomingProductQueue.created_at >= start_date
        ).group_by(IncomingProductQueue.delay_reason).order_by(func.count(IncomingProductQueue.id).desc())
        
        if vendor_id:
            delay_query = delay_query.filter(IncomingProductQueue.vendor_id == vendor_id)
        
        delay_result = await db.execute(delay_query)
        top_delays = [
            {'reason': str(row.delay_reason), 'count': row.count}
            for row in delay_result
        ]
        
        return QueueAnalyticsResponse(
            stats=stats_response,
            priority_distribution=priority_distribution,
            status_distribution=status_distribution,
            vendor_performance=vendor_performance,
            processing_trends=processing_trends,
            top_delays=top_delays
        )
        
    except Exception as e:
        logger.error(f"Error generando analytics de cola: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/queue/notifications/check",
    status_code=status.HTTP_200_OK,
    summary="Verificar notificaciones manualmente",
    description="Forzar verificación inmediata de notificaciones de cola"
)
async def force_notification_check(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Forzar verificación inmediata de notificaciones."""
    try:
        # Solo administradores pueden forzar verificación
        if current_user.get('user_type') != 'ADMIN':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores pueden ejecutar verificaciones manuales"
            )
        
        from app.services.queue_notification_service import queue_notification_service
        
        logger.info(f"Verificación manual de notificaciones iniciada por: {current_user.get('email')}")
        
        notifications_sent = await queue_notification_service.check_and_send_notifications(db)
        
        return {
            "message": "Verificación de notificaciones completada",
            "notifications_sent": notifications_sent,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en verificación manual de notificaciones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/queue/scheduler/status",
    status_code=status.HTTP_200_OK,
    summary="Estado del programador de tareas",
    description="Obtener estado del programador de tareas automáticas"
)
async def get_scheduler_status(
    current_user: dict = Depends(get_current_user)
):
    """Obtener estado del programador de tareas."""
    try:
        # Solo administradores pueden ver el estado del programador
        if current_user.get('user_type') != 'ADMIN':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores pueden ver el estado del programador"
            )
        
        from app.tasks.queue_scheduler import queue_scheduler
        
        status_info = queue_scheduler.get_status()
        
        return {
            "scheduler_status": status_info,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": "Sistema funcionando correctamente" if status_info["running"] else "Sistema detenido"
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del programador: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )