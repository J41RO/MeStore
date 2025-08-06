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

from pydantic import BaseModel, Field, field_validator, model_validator, UUID4, computed_field

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

    class Config:
        from_attributes = True



class MovimientoResponse(BaseModel):
    """Schema para respuesta de movimientos."""

    success: bool = Field(..., description="Indica si el movimiento fue exitoso")
    message: str = Field(..., description="Mensaje de confirmación")
    inventory_id: UUID4 = Field(..., description="ID del inventario actualizado")
    tipo_movimiento: TipoMovimiento = Field(..., description="Tipo de movimiento realizado")
    cantidad_anterior: int = Field(..., ge=0, description="Cantidad antes del movimiento")
    cantidad_nueva: int = Field(..., ge=0, description="Cantidad después del movimiento")
    cantidad_disponible: int = Field(..., ge=0, description="Cantidad disponible actual")
    fecha_movimiento: datetime = Field(..., description="Fecha y hora del movimiento")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "product_id": "123e4567-e89b-12d3-a456-426614174000",
                "zona": "A",
                "estante": "001",
                "posicion": "01",
                "cantidad": 100,
                "cantidad_reservada": 20,
                "status": "DISPONIBLE",
                "condicion_producto": "NUEVO",
                "notas_almacen": "Producto verificado, sin observaciones"
            }
        }


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

    class Config:
        from_attributes = True

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

    class Config:
        from_attributes = True
        json_schema_extra = {
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

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "inventory_id": "123e4567-e89b-12d3-a456-426614174000",
                "tipo_movimiento": "INGRESO",
                "cantidad_anterior": 50,
                "cantidad_nueva": 100,
                "observaciones": "Ingreso de mercancía nueva",
                "user_id": "123e4567-e89b-12d3-a456-426614174002"
            }
        }


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

    class Config:
        from_attributes = True
        json_schema_extra = {
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

class AlertasMetadata(BaseModel):
    """Metadata para response de alertas"""
    total_alertas: int = Field(..., description="Total de alertas encontradas")
    stock_bajo: int = Field(..., description="Cantidad de alertas por stock bajo")
    sin_movimiento: int = Field(..., description="Cantidad de alertas por sin movimiento")
    stock_agotado: int = Field(..., description="Cantidad de alertas por stock agotado")
    criticos: int = Field(..., description="Productos críticos (ambas condiciones)")

class AlertasResponse(BaseModel):
    """Response completa para alertas de inventario"""
    alertas: List[InventoryResponse] = Field(..., description="Lista de inventario con alertas")
    metadata: AlertasMetadata = Field(..., description="Metadatos de las alertas")

    class Config:
        from_attributes = True