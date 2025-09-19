# ~/app/schemas/inventory.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Pydantic Schemas para Inventory y Movimientos de Stock
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: inventory.py
# Ruta: ~/app/schemas/inventory.py
# Autor: Jairo
# Fecha de Creación: 2025-07-28
# Última Actualización: 2025-07-28
# Versión: 1.0.0
# Propósito: Schemas Pydantic para modelo Inventory con validaciones de negocio,
#            computed fields para métodos business y schemas para tracking de
#            movimientos de stock con auditoría completa
#
# Modificaciones:
# 2025-07-28 - Implementación inicial con 5 schemas Inventory + 3 MovimientoStock
#
# ---------------------------------------------------------------------------------------------

"""
Schemas Pydantic para Inventory y Movimientos de Stock.

Este módulo contiene schemas completos para el modelo Inventory incluyendo:
- InventoryBase: Schema base con campos compartidos y validaciones business
- InventoryCreate: Schema para creación con validaciones específicas  
- InventoryUpdate: Schema para actualizaciones parciales con validaciones
- InventoryRead: Schema para respuestas con computed fields y metadatos completos
- InventoryResponse: Alias descriptivo para APIs
- MovimientoStock schemas: Para tracking y auditoría de cambios de inventario
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator, UUID4, computed_field, ConfigDict

# Importar enums desde models
from app.models.inventory import InventoryStatus, CondicionProducto


# Enum para tipos de movimientos de stock
from enum import Enum

class TipoMovimiento(str, Enum):
    """Tipos de movimientos de stock para auditoría"""
    INGRESO = "INGRESO"
    AJUSTE_POSITIVO = "AJUSTE_POSITIVO"
    AJUSTE_NEGATIVO = "AJUSTE_NEGATIVO"
    RESERVA = "RESERVA"
    LIBERACION_RESERVA = "LIBERACION_RESERVA"
    PICKING = "PICKING"
    CAMBIO_STATUS = "CAMBIO_STATUS"
    CAMBIO_CONDICION = "CAMBIO_CONDICION"
    CAMBIO_UBICACION = "CAMBIO_UBICACION"


class InventoryBase(BaseModel):
    """Schema base con campos compartidos para operaciones Inventory"""

    # Campos ubicación (4)
    product_id: UUID4 = Field(..., description="ID del producto en inventario")
    zona: str = Field(..., min_length=1, max_length=10, description="Zona del almacén")
    estante: str = Field(..., min_length=1, max_length=20, description="Estante dentro de la zona")
    posicion: str = Field(..., min_length=1, max_length=20, description="Posición en el estante")

    # Campos cantidad (2)
    cantidad: int = Field(..., ge=0, description="Cantidad total en inventario")
    cantidad_reservada: int = Field(0, ge=0, description="Cantidad reservada")

    # Campos status y calidad (2)
    status: InventoryStatus = Field(default=InventoryStatus.DISPONIBLE, description="Estado del inventario")
    condicion_producto: CondicionProducto = Field(default=CondicionProducto.NUEVO, description="Condición física del producto")
    notas_almacen: Optional[str] = Field(None, max_length=1000, description="Observaciones del almacén")

    @field_validator("zona")
    @classmethod
    def validate_zona(cls, v: str) -> str:
        """Validar formato zona almacén"""
        if not v.isalnum():
            raise ValueError("Zona debe ser alfanumérica")
        return v.upper()

    @field_validator("estante")
    @classmethod
    def validate_estante(cls, v: str) -> str:
        """Validar formato estante"""
        import re
        if not re.match(r'^[0-9A-Z\-]{1,20}$', v):
            raise ValueError("Estante debe contener solo números, letras y guiones")
        return v.upper()

    @field_validator("notas_almacen")
    @classmethod
    def validate_notas_almacen(cls, v: Optional[str]) -> Optional[str]:
        """Validar y limpiar notas"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v

    @model_validator(mode='after')
    def validate_inventory_consistency(self):
        """Validar coherencia del inventario"""
        # cantidad_reservada <= cantidad
        if self.cantidad_reservada > self.cantidad:
            raise ValueError("Cantidad reservada no puede ser mayor que cantidad total")

        # Status coherente con cantidades
        if self.status == InventoryStatus.DISPONIBLE and self.cantidad == 0:
            raise ValueError("Inventario DISPONIBLE debe tener cantidad > 0")

        return self


class InventoryCreate(InventoryBase):
    """Schema para crear inventario con validaciones business"""

    model_config = ConfigDict(from_attributes=True)



class MovimientoResponse(BaseModel):
    """Schema para respuesta de movimientos de stock"""

    model_config = ConfigDict(from_attributes=True)

    success: bool = Field(..., description="Indica si el movimiento fue exitoso")
    message: str = Field(..., description="Mensaje de confirmación")
    inventory_id: UUID4 = Field(..., description="ID del inventario afectado")
    cantidad_anterior: int = Field(..., ge=0, description="Cantidad antes del movimiento")
    cantidad_nueva: int = Field(..., ge=0, description="Cantidad después del movimiento")


class ReservaStockCreate(BaseModel):
    """Schema para crear reserva de stock"""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "inventory_id": "123e4567-e89b-12d3-a456-426614174000",
                "cantidad": 5,
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "motivo": "Reserva para pre-venta cliente premium"
            }
        }
    )

    inventory_id: UUID4 = Field(..., description="ID del inventario a reservar")
    cantidad: int = Field(..., ge=1, le=10000, description="Cantidad a reservar")
    user_id: UUID4 = Field(..., description="ID del usuario que realiza la reserva")
    motivo: Optional[str] = Field(None, max_length=500, description="Motivo de la reserva")


class ReservaResponse(BaseModel):
    """Schema para respuesta de reserva de stock"""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Reserva realizada exitosamente",
                "inventory_id": "123e4567-e89b-12d3-a456-426614174000",
                "cantidad_reservada": 25,
                "cantidad_disponible": 75,
                "cantidad_solicitada": 5,
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "fecha_reserva": "2025-08-06T10:30:00Z"
            }
        }
    )

    success: bool = Field(..., description="Indica si la reserva fue exitosa")
    message: str = Field(..., description="Mensaje de confirmación")
    inventory_id: UUID4 = Field(..., description="ID del inventario reservado")
    cantidad_reservada: int = Field(..., ge=0, description="Cantidad total reservada después de la operación")
    cantidad_disponible: int = Field(..., ge=0, description="Cantidad disponible restante")
    cantidad_solicitada: int = Field(..., ge=0, description="Cantidad que se solicitó reservar")
    user_id: UUID4 = Field(..., description="ID del usuario que realizó la reserva")
    fecha_reserva: datetime = Field(..., description="Fecha y hora de la reserva")


class InventoryUpdate(BaseModel):
    """Schema para actualizaciones parciales"""

    # Todos los campos de InventoryBase como Optional
    product_id: Optional[UUID4] = Field(None, description="ID del producto en inventario")
    zona: Optional[str] = Field(None, min_length=1, max_length=10, description="Zona del almacén")
    estante: Optional[str] = Field(None, min_length=1, max_length=20, description="Estante dentro de la zona")
    posicion: Optional[str] = Field(None, min_length=1, max_length=20, description="Posición en el estante")
    cantidad: Optional[int] = Field(None, ge=0, description="Cantidad total en inventario")
    cantidad_reservada: Optional[int] = Field(None, ge=0, description="Cantidad reservada")
    status: Optional[InventoryStatus] = Field(None, description="Estado del inventario")
    condicion_producto: Optional[CondicionProducto] = Field(None, description="Condición física del producto")
    notas_almacen: Optional[str] = Field(None, max_length=1000, description="Observaciones del almacén")

    @field_validator("zona")
    @classmethod
    def validate_zona(cls, v: Optional[str]) -> Optional[str]:
        """Validar formato zona almacén"""
        if v is not None and not v.isalnum():
            raise ValueError("Zona debe ser alfanumérica")
        return v.upper() if v else v

    @field_validator("estante")
    @classmethod
    def validate_estante(cls, v: Optional[str]) -> Optional[str]:
        """Validar formato estante"""
        if v is not None:
            import re
            if not re.match(r'^[0-9A-Z\-]{1,20}$', v):
                raise ValueError("Estante debe contener solo números, letras y guiones")
            return v.upper()
        return v

    @model_validator(mode='after')
    def validate_update_consistency(self):
        """Validar coherencia en actualizaciones"""
        # Solo validar si ambos campos están presentes
        if (self.cantidad is not None and 
            self.cantidad_reservada is not None and 
            self.cantidad_reservada > self.cantidad):
            raise ValueError("Cantidad reservada no puede ser mayor que cantidad total")

        return self

    model_config = ConfigDict(from_attributes=True)

class InventoryRead(InventoryBase):
    """Schema para respuestas API con campos completos"""
    
# Campos base heredados + metadatos
    id: Optional[UUID4] = Field(None, description="ID del registro (None si no persistido)")
    updated_by_id: Optional[UUID4] = Field(None, description="ID del usuario que realizó la última actualización")
    fecha_ingreso: datetime = Field(..., description="Fecha de ingreso al inventario")
    fecha_ultimo_movimiento: datetime = Field(..., description="Fecha del último movimiento de stock")
    created_at: Optional[datetime] = Field(None, description="Fecha de creación del registro (None si no persistido)")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización (None si no persistido)")
    deleted_at: Optional[datetime] = Field(None, description="Fecha de eliminación lógica")
    
# Campos calculados (computed fields basados en métodos del modelo)
    @computed_field
    @property
    def ubicacion_completa(self) -> str:
        """Ubicación completa zona-estante-posicion"""
        return f"{self.zona}-{self.estante}-{self.posicion}"
    
    @computed_field
    @property
    def cantidad_disponible(self) -> int:
        """Cantidad disponible (total - reservada)"""
        return self.cantidad - self.cantidad_reservada
    
    @computed_field
    @property
    def condicion_descripcion(self) -> str:
        """Descripción legible de la condición"""
        condicion_map = {
            'NUEVO': 'Nuevo',
            'USADO_EXCELENTE': 'Usado - Excelente',
            'USADO_BUENO': 'Usado - Bueno', 
            'USADO_REGULAR': 'Usado - Regular',
            'DAÑADO': 'Dañado'
        }
        return condicion_map.get(self.condicion_producto.value, 'Desconocido')
    
    @computed_field
    @property
    def nivel_calidad(self) -> int:
        """Nivel numérico de calidad 1-5"""
        calidad_map = {
            'NUEVO': 5,
            'USADO_EXCELENTE': 4,
            'USADO_BUENO': 3,
            'USADO_REGULAR': 2,
            'DAÑADO': 1
        }
        return calidad_map.get(self.condicion_producto.value, 1)
    
    @computed_field
    @property
    def es_nuevo(self) -> bool:
        """Si el producto está en condición nueva"""
        return self.condicion_producto.value == 'NUEVO'
    
    @computed_field
    @property
    def es_vendible(self) -> bool:
        """Si el producto es vendible"""
        return self.condicion_producto.value != 'DAÑADO' and self.cantidad > 0
    
    @computed_field
    @property
    def requiere_inspeccion(self) -> bool:
        """Si requiere inspección especial"""
        return self.condicion_producto.value in ['USADO_REGULAR', 'DAÑADO']
    
    @computed_field
    @property
    def tiene_notas(self) -> bool:
        """Si tiene observaciones del almacén"""
        return self.notas_almacen is not None and len(self.notas_almacen.strip()) > 0
    
    @computed_field
    @property
    def transiciones_disponibles(self) -> List[str]:
        """Estados a los que puede transicionar"""
        if self.status.value == 'DISPONIBLE':
            return ['RESERVADO', 'EN_PICKING'] if self.cantidad > 0 else ['AGOTADO']
        elif self.status.value == 'RESERVADO':
            return ['DISPONIBLE', 'EN_PICKING']
        elif self.status.value == 'EN_PICKING':
            return ['DESPACHADO', 'DISPONIBLE']
        else:
            return []
    
    @computed_field
    @property
    def dias_desde_ingreso(self) -> int:
        """Días desde el ingreso"""
        from datetime import datetime
        if isinstance(self.fecha_ingreso, datetime):
            return (datetime.now() - self.fecha_ingreso).days
        return 0
    
    @computed_field
    @property
    def dias_desde_ultimo_movimiento(self) -> int:
        """Días desde último movimiento"""
        from datetime import datetime
        if isinstance(self.fecha_ultimo_movimiento, datetime):
            return (datetime.now() - self.fecha_ultimo_movimiento).days
        return 0

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "product_id": "123e4567-e89b-12d3-a456-426614174001",
                "zona": "A",
                "estante": "001",
                "posicion": "01",
                "cantidad": 100,
                "cantidad_reservada": 20,
                "status": "DISPONIBLE",
                "condicion_producto": "NUEVO",
                "notas_almacen": "Producto verificado",
                "fecha_ingreso": "2025-07-28T10:00:00Z",
                "fecha_ultimo_movimiento": "2025-07-28T15:30:00Z",
                "created_at": "2025-07-28T10:00:00Z",
                "updated_at": "2025-07-28T15:30:00Z",
                "ubicacion_completa": "A-001-01",
                "cantidad_disponible": 80,
                "condicion_descripcion": "Nuevo",
                "nivel_calidad": 5,
                "es_nuevo": True,
                "es_vendible": True,
                "requiere_inspeccion": False,
                "tiene_notas": True,
                "transiciones_disponibles": ["RESERVADO", "AGOTADO"],
                "dias_desde_ingreso": 0,
                "dias_desde_ultimo_movimiento": 0
            }
        }
    )


class InventoryResponse(InventoryRead):
    """Alias más descriptivo para APIs"""
    pass


# Schemas para Movimientos de Stock
class MovimientoStockBase(BaseModel):
    """Schema base para movimientos de stock"""
    
    inventory_id: UUID4 = Field(..., description="ID del inventario")
    tipo_movimiento: TipoMovimiento = Field(..., description="Tipo de movimiento")
    cantidad_anterior: int = Field(..., ge=0, description="Cantidad antes del movimiento")
    cantidad_nueva: int = Field(..., ge=0, description="Cantidad después del movimiento")
    observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones del movimiento")


class MovimientoStockCreate(MovimientoStockBase):
    """Schema para registrar movimientos"""
    
    user_id: Optional[UUID4] = Field(None, description="Usuario que realizó el movimiento")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "inventory_id": "123e4567-e89b-12d3-a456-426614174000",
                "tipo_movimiento": "INGRESO",
                "cantidad_anterior": 50,
                "cantidad_nueva": 100,
                "observaciones": "Ingreso de mercancía nueva",
                "user_id": "123e4567-e89b-12d3-a456-426614174002"
            }
        }
    )


class MovimientoStockRead(MovimientoStockBase):
    """Schema para leer movimientos"""
    
    id: UUID4
    user_id: Optional[UUID4] = Field(None, description="Usuario que realizó el movimiento")
    fecha_movimiento: datetime = Field(..., description="Fecha y hora del movimiento")
    created_at: datetime = Field(..., description="Fecha de creación del registro")
    
    # Campos calculados
    @computed_field
    @property
    def diferencia_cantidad(self) -> int:
        """Diferencia en cantidad"""
        return self.cantidad_nueva - self.cantidad_anterior
    
    @computed_field
    @property
    def tipo_descripcion(self) -> str:
        """Descripción del tipo de movimiento"""
        descripciones = {
            'INGRESO': 'Ingreso de stock',
            'AJUSTE_POSITIVO': 'Ajuste positivo de inventario',
            'AJUSTE_NEGATIVO': 'Ajuste negativo de inventario',
            'RESERVA': 'Reserva de productos',
            'LIBERACION_RESERVA': 'Liberación de reserva',
            'PICKING': 'Picking para despacho',
            'CAMBIO_STATUS': 'Cambio de estado',
            'CAMBIO_CONDICION': 'Cambio de condición'
        }
        return descripciones.get(self.tipo_movimiento.value, 'Movimiento desconocido')

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174003",
                "inventory_id": "123e4567-e89b-12d3-a456-426614174000",
                "tipo_movimiento": "INGRESO",
                "cantidad_anterior": 50,
                "cantidad_nueva": 100,
                "observaciones": "Ingreso de mercancía nueva",
                "user_id": "123e4567-e89b-12d3-a456-426614174002",
                "fecha_movimiento": "2025-07-28T15:30:00Z",
                "created_at": "2025-07-28T15:30:00Z",
                "diferencia_cantidad": 50,
                "tipo_descripcion": "Ingreso de stock"
            }
        }
    )

class AlertasMetadata(BaseModel):
    """Metadata para response de alertas"""
    total_alertas: int = Field(..., description="Total de alertas encontradas")
    stock_bajo: int = Field(..., description="Cantidad de alertas por stock bajo")
    sin_movimiento: int = Field(..., description="Cantidad de alertas por sin movimiento")
    stock_agotado: int = Field(..., description="Cantidad de alertas por stock agotado")
    criticos: int = Field(..., description="Productos críticos (ambas condiciones)")
    perdidos: int = Field(default=0, description="Cantidad de productos perdidos")
    danados: int = Field(default=0, description="Cantidad de productos dañados")

class AlertasResponse(BaseModel):
    """Response completa para alertas de inventario"""
    alertas: List[InventoryResponse] = Field(..., description="Lista de inventario con alertas")
    metadata: AlertasMetadata = Field(..., description="Metadatos de las alertas")

    model_config = ConfigDict(from_attributes=True)


class LocationUpdateRequest(BaseModel):
    """Schema para actualización de ubicación de inventario"""
    zona: str = Field(..., min_length=1, max_length=10, description="Nueva zona del almacén")
    estante: str = Field(..., min_length=1, max_length=20, description="Nuevo estante dentro de la zona")
    posicion: str = Field(..., min_length=1, max_length=20, description="Nueva posición en el estante")
    observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones del cambio de ubicación")

    @field_validator("zona")
    @classmethod
    def validate_zona(cls, v: str) -> str:
        """Validar formato zona almacén"""
        if not v.isalnum():
            raise ValueError("Zona debe ser alfanumérica")
        return v.upper()

    @field_validator("estante")
    @classmethod
    def validate_estante(cls, v: str) -> str:
        """Validar formato estante"""
        import re
        if not re.match(r'^[0-9A-Z\-]{1,20}$', v):
            raise ValueError("Estante debe contener solo números, letras y guiones")
        return v.upper()

    @field_validator("posicion")
    @classmethod
    def validate_posicion(cls, v: str) -> str:
        """Validar formato posición"""
        import re
        if not re.match(r'^[0-9A-Z\-]{1,20}$', v):
            raise ValueError("Posición debe contener solo números, letras y guiones")
        return v.upper()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "zona": "A",
                "estante": "A1",
                "posicion": "A1-01",
                "observaciones": "Reubicación por reorganización de almacén"
            }
        }
    )


# Schemas para Incidentes de Inventario
from app.models.incidente_inventario import TipoIncidente, EstadoIncidente

class IncidenteCreate(BaseModel):
    """Schema para reportar un nuevo incidente"""
    inventory_id: UUID4 = Field(..., description="ID del inventario afectado")
    tipo_incidente: TipoIncidente = Field(..., description="Tipo de incidente")
    descripcion: str = Field(..., min_length=10, max_length=1000, description="Descripción detallada del incidente")
    fecha_incidente: Optional[datetime] = Field(None, description="Fecha estimada cuando ocurrió el incidente")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "inventory_id": "123e4567-e89b-12d3-a456-426614174000",
                "tipo_incidente": "PERDIDO",
                "descripcion": "Producto no encontrado durante inventario físico",
                "fecha_incidente": "2025-01-15T10:30:00Z"
            }
        }
    )

class IncidenteResponse(BaseModel):
    """Schema para respuesta de incidentes"""
    id: UUID4 = Field(..., description="ID del incidente")
    inventory_id: UUID4 = Field(..., description="ID del inventario afectado")
    tipo_incidente: TipoIncidente = Field(..., description="Tipo de incidente")
    estado: EstadoIncidente = Field(..., description="Estado actual del incidente")
    descripcion: str = Field(..., description="Descripción del incidente")
    reportado_por: str = Field(..., description="Usuario que reportó el incidente")
    fecha_incidente: Optional[datetime] = Field(None, description="Fecha del incidente")
    created_at: datetime = Field(..., description="Fecha de creación del reporte")
    updated_at: datetime = Field(..., description="Fecha de última actualización")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174004",
                "inventory_id": "123e4567-e89b-12d3-a456-426614174000",
                "tipo_incidente": "PERDIDO",
                "estado": "REPORTADO",
                "descripcion": "Producto no encontrado durante inventario físico",
                "reportado_por": "admin@mestore.com",
                "fecha_incidente": "2025-01-15T10:30:00Z",
                "created_at": "2025-01-15T14:30:00Z",
                "updated_at": "2025-01-15T14:30:00Z"
            }
        }
    )


# Schemas para MovementTracker
class MovementTrackerBase(BaseModel):
    """Schema base para tracking de movimientos"""
    
    movement_id: UUID4 = Field(..., description="ID del movimiento trackeado")
    user_id: UUID4 = Field(..., description="ID del usuario que realizó la acción")
    user_name: str = Field(..., max_length=100, description="Nombre del usuario")
    action_type: str = Field(..., max_length=20, description="Tipo de acción realizada")
    new_data: dict = Field(..., description="Estado nuevo del movimiento")
    previous_data: Optional[dict] = Field(None, description="Estado anterior del movimiento")
    notes: Optional[str] = Field(None, description="Notas adicionales")


class MovementTrackerCreate(MovementTrackerBase):
    """Schema para crear registro de tracking"""
    
    ip_address: Optional[str] = Field(None, max_length=45, description="Dirección IP")
    user_agent: Optional[str] = Field(None, description="User Agent del navegador")
    session_id: Optional[str] = Field(None, max_length=100, description="ID de sesión")
    location_from: Optional[dict] = Field(None, description="Ubicación origen")
    location_to: Optional[dict] = Field(None, description="Ubicación destino")
    batch_id: Optional[UUID4] = Field(None, description="ID de lote")

    model_config = ConfigDict(from_attributes=True)


class MovementTrackerResponse(MovementTrackerBase):
    """Schema para respuesta de tracking"""
    
    id: UUID4
    ip_address: Optional[str]
    user_agent: Optional[str] 
    session_id: Optional[str]
    location_from: Optional[dict]
    location_to: Optional[dict]
    batch_id: Optional[UUID4]
    action_timestamp: datetime = Field(..., description="Timestamp de la acción")
    created_at: datetime
    updated_at: datetime
    
    # Campos calculados
    changes: dict = Field(default_factory=dict, description="Cambios realizados")
    is_create_action: bool = Field(default=False, description="Es acción de creación")
    is_update_action: bool = Field(default=False, description="Es acción de actualización")
    has_location_change: bool = Field(default=False, description="Hubo cambio de ubicación")
    
    model_config = ConfigDict(from_attributes=True)


# Schemas para Analytics
class DateRange(BaseModel):
    """Schema para rango de fechas"""
    
    start_date: datetime = Field(..., description="Fecha de inicio")
    end_date: datetime = Field(..., description="Fecha de fin")


class MovementAnalytics(BaseModel):
    """Schema para analytics de movimientos"""
    
    total_movements: int = Field(..., description="Total de movimientos")
    movements_by_type: dict = Field(..., description="Movimientos por tipo")
    movements_by_user: dict = Field(..., description="Movimientos por usuario")
    movements_by_date: dict = Field(..., description="Movimientos por fecha")
    top_products: list = Field(..., description="Productos más movidos")
    average_movements_per_day: float = Field(..., description="Promedio de movimientos por día")


class MovementAnalyticsResponse(BaseModel):
    """Schema para respuesta de analytics"""
    
    date_range: DateRange
    analytics: MovementAnalytics
    metadata: dict = Field(default_factory=dict, description="Metadata adicional")
    
    model_config = ConfigDict(from_attributes=True)


# Schemas para IncomingProductQueue
from app.models.incoming_product_queue import QueuePriority, VerificationStatus, DelayReason


class IncomingProductQueueBase(BaseModel):
    """Schema base para cola de productos entrantes"""
    
    product_id: UUID4 = Field(..., description="ID del producto en tránsito")
    vendor_id: UUID4 = Field(..., description="ID del vendor responsable")
    expected_arrival: Optional[datetime] = Field(None, description="Fecha esperada de llegada")
    priority: QueuePriority = Field(default=QueuePriority.NORMAL, description="Prioridad en la cola")
    tracking_number: Optional[str] = Field(None, max_length=100, description="Número de tracking")
    carrier: Optional[str] = Field(None, max_length=50, description="Empresa transportadora")
    notes: Optional[str] = Field(None, description="Notas generales")


class IncomingProductQueueCreate(IncomingProductQueueBase):
    """Schema para crear entrada en cola"""
    
    deadline: Optional[datetime] = Field(None, description="Fecha límite para verificación")
    
    @field_validator('expected_arrival')
    @classmethod
    def validate_expected_arrival(cls, v):
        if v and v < datetime.now():
            raise ValueError('La fecha esperada debe ser futura')
        return v


class IncomingProductQueueUpdate(BaseModel):
    """Schema para actualizar entrada en cola"""
    
    actual_arrival: Optional[datetime] = Field(None, description="Fecha real de llegada")
    verification_status: Optional[VerificationStatus] = Field(None, description="Estado de verificación")
    priority: Optional[QueuePriority] = Field(None, description="Prioridad en la cola")
    assigned_to: Optional[UUID4] = Field(None, description="Usuario asignado para verificación")
    tracking_number: Optional[str] = Field(None, max_length=100, description="Número de tracking")
    carrier: Optional[str] = Field(None, max_length=50, description="Empresa transportadora")
    notes: Optional[str] = Field(None, description="Notas generales")
    verification_notes: Optional[str] = Field(None, description="Notas de verificación")
    quality_score: Optional[int] = Field(None, ge=1, le=10, description="Puntuación de calidad (1-10)")
    quality_issues: Optional[str] = Field(None, description="Problemas de calidad identificados")
    is_delayed: Optional[bool] = Field(None, description="Indica si está retrasado")
    delay_reason: Optional[DelayReason] = Field(None, description="Razón del retraso")


class IncomingProductQueueResponse(IncomingProductQueueBase):
    """Schema para respuesta de cola"""
    
    id: UUID4
    actual_arrival: Optional[datetime]
    verification_status: VerificationStatus
    assigned_to: Optional[UUID4]
    assigned_at: Optional[datetime]
    deadline: Optional[datetime]
    is_delayed: bool
    delay_reason: Optional[DelayReason]
    verification_notes: Optional[str]
    quality_score: Optional[int]
    quality_issues: Optional[str]
    processing_started_at: Optional[datetime]
    processing_completed_at: Optional[datetime]
    verification_attempts: int
    created_at: datetime
    updated_at: datetime
    
    # Campos calculados
    is_overdue: bool = Field(default=False, description="Está vencido")
    days_in_queue: int = Field(default=0, description="Días en la cola")
    processing_time_hours: Optional[float] = Field(None, description="Tiempo de procesamiento en horas")
    is_high_priority: bool = Field(default=False, description="Es alta prioridad")
    status_display: str = Field(default="", description="Texto legible del estado")
    priority_display: str = Field(default="", description="Texto legible de la prioridad")
    
    model_config = ConfigDict(from_attributes=True)


class QueueAssignmentRequest(BaseModel):
    """Schema para asignación de tarea en cola"""
    
    assigned_to: UUID4 = Field(..., description="Usuario a asignar")
    notes: Optional[str] = Field(None, description="Notas de asignación")


class QueueProcessingRequest(BaseModel):
    """Schema para iniciar procesamiento"""
    
    notes: Optional[str] = Field(None, description="Notas al iniciar procesamiento")


class QueueCompletionRequest(BaseModel):
    """Schema para completar verificación"""
    
    approved: bool = Field(..., description="Aprobado o rechazado")
    quality_score: Optional[int] = Field(None, ge=1, le=10, description="Puntuación de calidad")
    notes: Optional[str] = Field(None, description="Notas de finalización")


class QueueDelayRequest(BaseModel):
    """Schema para marcar como retrasado"""
    
    delay_reason: DelayReason = Field(..., description="Razón del retraso")
    notes: Optional[str] = Field(None, description="Notas del retraso")


class QueueStatsResponse(BaseModel):
    """Schema para estadísticas de cola"""
    
    total_items: int = Field(..., description="Total de elementos en cola")
    pending: int = Field(..., description="Elementos pendientes")
    assigned: int = Field(..., description="Elementos asignados")
    in_progress: int = Field(..., description="Elementos en proceso")
    completed: int = Field(..., description="Elementos completados")
    overdue: int = Field(..., description="Elementos vencidos")
    delayed: int = Field(..., description="Elementos retrasados")
    average_processing_time: float = Field(..., description="Tiempo promedio de procesamiento")
    queue_efficiency: float = Field(..., description="Eficiencia de la cola (%)")


class QueueAnalyticsResponse(BaseModel):
    """Schema para analytics de cola"""
    
    stats: QueueStatsResponse
    priority_distribution: dict = Field(..., description="Distribución por prioridad")
    status_distribution: dict = Field(..., description="Distribución por estado")
    vendor_performance: dict = Field(..., description="Performance por vendor")
    processing_trends: dict = Field(..., description="Tendencias de procesamiento")
    top_delays: list = Field(..., description="Principales causas de retraso")