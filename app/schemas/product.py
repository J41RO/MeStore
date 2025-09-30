# ~/app/schemas/product.py
# ---------------------------------------------------------------------------------------------
# MeStore - Product Pydantic Schemas
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: product.py
# Ruta: ~/app/schemas/product.py
# Autor: Jairo
# Fecha de Creación: 2025-07-28
# Última Actualización: 2025-07-28
# Versión: 1.0.0
# Propósito: Schemas Pydantic para Product con validaciones de negocio empresariales
#            Incluye validaciones SKU, pricing coherence, fulfillment rules
#
# Modificaciones:
# 2025-07-28 - Creación inicial con 5 schemas y validaciones business
#
# ---------------------------------------------------------------------------------------------

"""
Schemas Pydantic para Product con validaciones de negocio empresariales.

Este módulo define los schemas de validación para productos del marketplace:
- ProductBase: Campos compartidos con validaciones core
- ProductCreate: Schema para creación con reglas business
- ProductUpdate: Schema para actualizaciones parciales
- ProductRead: Schema para respuestas API completas
- ProductResponse: Alias descriptivo para APIs

Validaciones implementadas:
- SKU format empresarial (alfanumérico + guiones)
- Pricing coherence (venta >= costo, comisión <= 30%)
- Fulfillment rules (peso, dimensiones logísticas)
- Status transitions válidas
- Tags format y cantidad
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import UUID4, BaseModel, Field, field_validator, model_validator, model_serializer

from app.models.product import ProductStatus


# Configuración base para todos los schemas Product
class ProductConfig:
    """Configuración común para schemas Product"""

    from_attributes = True
    json_encoders = {
        Decimal: float,  # Convertir Decimal a float para JSON
        UUID: str,  # Convertir UUID a string para JSON
    }


class ProductBase(BaseModel):
    """
    Schema base con campos compartidos para operaciones Product.

    Incluye campos core, pricing y fulfillment sin campos de tracking.
    Usado como base para ProductCreate y ProductUpdate.
    """

    # === CAMPOS BÁSICOS ===
    sku: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="SKU único del producto (formato empresarial)",
    )
    name: str = Field(
        ..., min_length=2, max_length=200, description="Nombre del producto"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Descripción detallada del producto"
    )
    status: ProductStatus = Field(
        default=ProductStatus.TRANSITO, description="Estado actual del producto"
    )

    # === CAMPOS PRICING ===
    precio_venta: Optional[Decimal] = Field(
        None, ge=100, le=100000000, description="Precio de venta en COP (100 - 100M)"
    )
    precio_costo: Optional[Decimal] = Field(
        None, ge=0, le=100000000, description="Precio de costo en COP"
    )
    comision_mestocker: Optional[Decimal] = Field(
        None, ge=0, description="Comisión MeStocker en COP"
    )

    # === CAMPOS FULFILLMENT ===
    peso: Optional[Decimal] = Field(
        None, ge=0.001, le=1000, description="Peso en kilogramos (0.001 - 1000 kg)"
    )
    dimensiones: Optional[Dict[str, float]] = Field(
        None, description="Dimensiones en cm: {largo, ancho, alto}"
    )
    categoria: Optional[str] = Field(
        None, max_length=100, description="Categoría del producto"
    )
    tags: Optional[List[str]] = Field(
        None, max_items=10, description="Tags del producto (máximo 10)"
    )

    class Config(ProductConfig):
        json_schema_extra = {
            "example": {
                "sku": "ELEC-LAPTOP-001",
                "name": "Laptop Gaming RGB",
                "description": "Laptop gaming de alta gama con iluminación RGB",
                "status": "disponible",
                "precio_venta": 2500000.00,
                "precio_costo": 2000000.00,
                "comision_mestocker": 250000.00,
                "peso": 2.500,
                "dimensiones": {"largo": 35.0, "ancho": 25.0, "alto": 3.0},
                "categoria": "Electronics",
                "tags": ["laptop", "gaming", "rgb"],
            }
        }

    # === VALIDACIONES DE NEGOCIO ===

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, v: str) -> str:
        """
        Validar formato SKU empresarial.

        Formato: Alfanumérico con guiones, 3-50 caracteres.
        Sugerido: PREFIX-CATEGORY-###
        """
        import re

        if not re.match(r"^[A-Za-z0-9\-]+$", v):
            raise ValueError("SKU debe contener solo letras, números y guiones")

        if v.count("-") < 1:
            raise ValueError("SKU debe tener formato PREFIX-CATEGORY-### (con guiones)")

        return v.upper()  # Normalizar a mayúsculas

    @field_validator("precio_venta")
    @classmethod
    def validate_precio_venta(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validar precio venta razonable para marketplace."""
        if v is not None:
            if v < 100:
                raise ValueError("Precio venta mínimo: 100 COP")
            if v > 100000000:
                raise ValueError("Precio venta máximo: 100,000,000 COP")
        return v

    @field_validator("peso")
    @classmethod
    def validate_peso(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validar peso logístico razonable."""
        if v is not None:
            if v < 0.001:
                raise ValueError("Peso mínimo: 0.001 kg")
            if v > 1000:
                raise ValueError("Peso máximo: 1000 kg")
        return v

    @field_validator("dimensiones")
    @classmethod
    def validate_dimensiones(
        cls, v: Optional[Dict[str, float]]
    ) -> Optional[Dict[str, float]]:
        """
        Validar estructura y valores de dimensiones.

        Estructura requerida: {largo, ancho, alto}
        Cada dimensión: 0.1 - 500 cm
        """
        if v is not None:
            required_keys = {"largo", "ancho", "alto"}
            provided_keys = set(v.keys())

            if not required_keys.issubset(provided_keys):
                missing = required_keys - provided_keys
                raise ValueError(f"Dimensiones faltantes: {missing}")

            for key, value in v.items():
                if key in required_keys:
                    if not isinstance(value, (int, float)) or value <= 0:
                        raise ValueError(f"Dimensión {key} debe ser positiva")
                    if value > 500:
                        raise ValueError(f"Dimensión {key} máxima: 500 cm")

        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """
        Validar array de tags.

        Reglas: Máximo 10 tags, 2-30 caracteres cada uno,
        sin caracteres especiales, lowercase normalizado.
        """
        if v is not None:
            if len(v) > 10:
                raise ValueError("Máximo 10 tags permitidos")

            import re

            validated_tags = []

            for tag in v:
                if not isinstance(tag, str):
                    raise ValueError("Todos los tags deben ser strings")

                tag_clean = tag.strip().lower()

                if len(tag_clean) < 2:
                    raise ValueError("Tags mínimo 2 caracteres")
                if len(tag_clean) > 30:
                    raise ValueError("Tags máximo 30 caracteres")

                if not re.match(r"^[a-z0-9\-_]+$", tag_clean):
                    raise ValueError(
                        f"Tag '{tag}' contiene caracteres inválidos (solo a-z, 0-9, -, _)"
                    )

                validated_tags.append(tag_clean)

            # Remover duplicados manteniendo orden
            seen = set()
            unique_tags = []
            for tag in validated_tags:
                if tag not in seen:
                    seen.add(tag)
                    unique_tags.append(tag)

            return unique_tags

        return v

    @model_validator(mode="after")
    def validate_pricing_coherence(self):
        """
        Validar coherencia entre precios del marketplace.

        Reglas business:
        - precio_venta >= precio_costo (no pérdidas)
        - comision_mestocker <= precio_venta * 0.30 (máximo 30%)
        """
        if self.precio_venta and self.precio_costo:
            if self.precio_venta < self.precio_costo:
                raise ValueError("Precio venta debe ser >= precio costo")

        if self.precio_venta and self.comision_mestocker:
            max_comision = self.precio_venta * Decimal("0.30")
            if self.comision_mestocker > max_comision:
                raise ValueError(
                    f"Comisión máxima permitida: {max_comision} COP (30% precio venta)"
                )

        return self


class ProductCreate(ProductBase):
    """
    Schema para crear productos con validaciones business específicas.

    Hereda ProductBase con campos obligatorios para creación.
    Incluye validaciones adicionales para nuevos productos.
    Acepta alias para compatibilidad con frontend (price, category).
    """

    # Campos obligatorios para creación
    sku: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="SKU único del producto (obligatorio)",
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Nombre del producto (obligatorio)",
    )

    # Alias para compatibilidad con frontend
    price: Optional[Decimal] = Field(None, description="Alias de precio_venta")
    category: Optional[str] = Field(None, description="Alias de categoria")
    category_id: Optional[str] = Field(None, description="UUID de categoría (se convertirá a nombre)")
    stock_quantity: Optional[int] = Field(None, ge=0, description="Cantidad en stock")

    @model_validator(mode='before')
    @classmethod
    def map_frontend_fields(cls, data: Any) -> Any:
        """
        Mapear campos del frontend a campos del backend.
        Convierte price → precio_venta y category → categoria si vienen.
        Nota: category_id se manejará en el endpoint para buscar el nombre.
        """
        if isinstance(data, dict):
            # Mapear price → precio_venta
            if 'price' in data and data['price'] is not None and 'precio_venta' not in data:
                data['precio_venta'] = data['price']

            # Mapear category → categoria
            if 'category' in data and data['category'] and 'categoria' not in data:
                data['categoria'] = data['category']

        return data

    class Config(ProductConfig):
        json_schema_extra = {
            "example": {
                "sku": "ELEC-LAPTOP-002",
                "name": "Laptop Gaming RGB Pro",
                "description": "Laptop gaming profesional con iluminación RGB avanzada",
                "precio_venta": 3500000.00,
                "precio_costo": 2800000.00,
                "comision_mestocker": 350000.00,
                "peso": 2.800,
                "dimensiones": {"largo": 38.0, "ancho": 26.0, "alto": 3.5},
                "categoria": "Electronics",
                "tags": ["laptop", "gaming", "rgb", "professional"],
            }
        }


class ProductUpdate(BaseModel):
    """
    Schema para actualizaciones parciales de productos.

    Todos los campos opcionales para permitir actualizaciones parciales.
    Incluye validaciones de transiciones de estado.
    """

    # === CAMPOS OPCIONALES PARA UPDATE ===
    sku: Optional[str] = Field(
        None, min_length=3, max_length=50, description="SKU del producto"
    )
    name: Optional[str] = Field(
        None, min_length=2, max_length=200, description="Nombre del producto"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Descripción del producto"
    )
    status: Optional[ProductStatus] = Field(None, description="Estado del producto")
    precio_venta: Optional[Decimal] = Field(
        None, ge=100, le=100000000, description="Precio de venta en COP"
    )
    precio_costo: Optional[Decimal] = Field(
        None, ge=0, le=100000000, description="Precio de costo en COP"
    )
    comision_mestocker: Optional[Decimal] = Field(
        None, ge=0, description="Comisión MeStocker en COP"
    )
    peso: Optional[Decimal] = Field(
        None, ge=0.001, le=1000, description="Peso en kilogramos"
    )
    dimensiones: Optional[Dict[str, float]] = Field(
        None, description="Dimensiones en cm"
    )
    categoria: Optional[str] = Field(
        None, max_length=100, description="Categoría del producto"
    )
    tags: Optional[List[str]] = Field(
        None, max_items=10, description="Tags del producto"
    )

    class Config(ProductConfig):
        json_schema_extra = {
            "example": {
                "name": "Laptop Gaming RGB Pro Updated",
                "precio_venta": 3200000.00,
                "status": "disponible",
                "tags": ["laptop", "gaming", "rgb", "updated"],
            }
        }

    # === VALIDACIONES ESPECÍFICAS PARA UPDATE ===

    @field_validator("sku")
    @classmethod
    def validate_sku_update(cls, v: Optional[str]) -> Optional[str]:
        """Validar formato SKU en updates."""
        if v is not None:
            import re

            if not re.match(r"^[A-Za-z0-9\-]+$", v):
                raise ValueError("SKU debe contener solo letras, números y guiones")
            if v.count("-") < 1:
                raise ValueError("SKU debe tener formato PREFIX-CATEGORY-###")
            return v.upper()
        return v

    @field_validator("status")
    @classmethod
    def validate_status_transition(
        cls, v: Optional[ProductStatus]
    ) -> Optional[ProductStatus]:
        """
        Validar transiciones de estado válidas.

        Flujo normal: TRANSITO → VERIFICADO → DISPONIBLE → VENDIDO
        Reversa permitida: DISPONIBLE ↔ VENDIDO
        """
        # Nota: Para validación completa de transiciones necesitaríamos el estado actual
        # Esta validación se puede expandir con contexto del estado previo
        if v is not None:
            valid_statuses = [
                ProductStatus.TRANSITO,
                ProductStatus.VERIFICADO,
                ProductStatus.DISPONIBLE,
                ProductStatus.VENDIDO,
            ]
            if v not in valid_statuses:
                raise ValueError(f"Estado inválido: {v}")
        return v

    # Reutilizar validaciones de ProductBase
    @field_validator("precio_venta")
    @classmethod
    def validate_precio_venta_update(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validar precio venta en updates."""
        if v is not None:
            if v < 100:
                raise ValueError("Precio venta mínimo: 100 COP")
            if v > 100000000:
                raise ValueError("Precio venta máximo: 100,000,000 COP")
        return v

    @field_validator("peso")
    @classmethod
    def validate_peso_update(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validar peso en updates."""
        if v is not None:
            if v < 0.001:
                raise ValueError("Peso mínimo: 0.001 kg")
            if v > 1000:
                raise ValueError("Peso máximo: 1000 kg")
        return v

    @field_validator("dimensiones")
    @classmethod
    def validate_dimensiones_update(
        cls, v: Optional[Dict[str, float]]
    ) -> Optional[Dict[str, float]]:
        """Validar dimensiones en updates."""
        if v is not None:
            required_keys = {"largo", "ancho", "alto"}
            provided_keys = set(v.keys())

            if not required_keys.issubset(provided_keys):
                missing = required_keys - provided_keys
                raise ValueError(f"Dimensiones faltantes: {missing}")

            for key, value in v.items():
                if key in required_keys:
                    if not isinstance(value, (int, float)) or value <= 0:
                        raise ValueError(f"Dimensión {key} debe ser positiva")
                    if value > 500:
                        raise ValueError(f"Dimensión {key} máxima: 500 cm")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags_update(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validar tags en updates."""
        if v is not None:
            if len(v) > 10:
                raise ValueError("Máximo 10 tags permitidos")

            import re

            validated_tags = []

            for tag in v:
                if not isinstance(tag, str):
                    raise ValueError("Todos los tags deben ser strings")

                tag_clean = tag.strip().lower()

                if len(tag_clean) < 2:
                    raise ValueError("Tags mínimo 2 caracteres")
                if len(tag_clean) > 30:
                    raise ValueError("Tags máximo 30 caracteres")

                if not re.match(r"^[a-z0-9\-_]+$", tag_clean):
                    raise ValueError(f"Tag '{tag}' contiene caracteres inválidos")

                validated_tags.append(tag_clean)

            # Remover duplicados
            seen = set()
            unique_tags = []
            for tag in validated_tags:
                if tag not in seen:
                    seen.add(tag)
                    unique_tags.append(tag)

            return unique_tags
        return v

    @model_validator(mode="after")
    def validate_pricing_coherence_update(self):
        """Validar coherencia pricing en updates parciales."""
        if self.precio_venta and self.precio_costo:
            if self.precio_venta < self.precio_costo:
                raise ValueError("Precio venta debe ser >= precio costo")

        if self.precio_venta and self.comision_mestocker:
            max_comision = self.precio_venta * Decimal("0.30")
            if self.comision_mestocker > max_comision:
                raise ValueError(
                    f"Comisión máxima: {max_comision} COP (30% precio venta)"
                )

        return self


class ProductRead(ProductBase):
    """
    Schema para respuestas API con campos completos.

    Incluye ProductBase + campos de tracking (id, timestamps, version).
    Usado para serializar respuestas de la base de datos.
    """

    # === CAMPOS DE TRACKING Y METADATA ===
    id: UUID4 = Field(..., description="ID único del producto")
    vendedor_id: Optional[UUID4] = Field(
        None, description="ID del vendedor propietario"
    )
    created_by_id: Optional[UUID4] = Field(
        None, description="ID del usuario que creó el producto"
    )
    updated_by_id: Optional[UUID4] = Field(
        None, description="ID del usuario que actualizó por última vez"
    )
    version: int = Field(
        ..., description="Versión del producto para optimistic locking"
    )
    created_at: datetime = Field(..., description="Fecha y hora de creación")
    updated_at: datetime = Field(
        ..., description="Fecha y hora de última actualización"
    )
    deleted_at: Optional[datetime] = Field(
        None, description="Fecha y hora de eliminación (soft delete)"
    )

    class Config(ProductConfig):
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "sku": "ELEC-LAPTOP-001",
                "name": "Laptop Gaming RGB",
                "description": "Laptop gaming de alta gama con iluminación RGB",
                "status": "disponible",
                "precio_venta": 2500000.00,
                "precio_costo": 2000000.00,
                "comision_mestocker": 250000.00,
                "peso": 2.500,
                "dimensiones": {"largo": 35.0, "ancho": 25.0, "alto": 3.0},
                "categoria": "Electronics",
                "tags": ["laptop", "gaming", "rgb"],
                "vendedor_id": "550e8400-e29b-41d4-a716-446655440001",
                "version": 1,
                "created_at": "2025-01-28T10:30:00",
                "updated_at": "2025-01-28T10:30:00",
                "deleted_at": None,
            }
        }


class ProductResponse(ProductRead):
    """
    Alias más descriptivo para respuestas API.

    Idéntico a ProductRead pero con nombre más semántico para APIs.
    Usado en endpoints que retornan productos completos.
    Incluye alias para compatibilidad con frontend.
    """

    stock_quantity: Optional[int] = Field(
        default=0,
        description="Cantidad en stock (viene de inventario)"
    )

    @model_serializer(mode='wrap')
    def serialize_model(self, serializer: Any) -> Dict[str, Any]:
        """
        Custom serializer para agregar alias de compatibilidad con frontend.
        Agrega campos: price, category, stock como alias de los campos backend.
        """
        data = serializer(self)

        # Agregar alias para compatibilidad frontend
        data['price'] = float(data.get('precio_venta', 0)) if data.get('precio_venta') else None
        data['category'] = data.get('categoria')
        data['stock'] = data.get('stock_quantity', 0)

        return data

    class Config(ProductConfig):
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "sku": "ELEC-LAPTOP-001",
                "name": "Laptop Gaming RGB",
                "description": "Laptop gaming de alta gama con iluminación RGB",
                "status": "disponible",
                "precio_venta": 2500000.00,
                "price": 2500000.00,  # Alias
                "precio_costo": 2000000.00,
                "comision_mestocker": 250000.00,
                "peso": 2.500,
                "dimensiones": {"largo": 35.0, "ancho": 25.0, "alto": 3.0},
                "categoria": "Electronics",
                "category": "Electronics",  # Alias
                "tags": ["laptop", "gaming", "rgb"],
                "stock_quantity": 12,
                "stock": 12,  # Alias
                "vendedor_id": "550e8400-e29b-41d4-a716-446655440001",
                "version": 1,
                "created_at": "2025-01-28T10:30:00",
                "updated_at": "2025-01-28T10:30:00",
                "deleted_at": None,
            }
        }


class ProductPatch(BaseModel):
    """
    Schema para operaciones PATCH específicas en productos.
    Enfocado en cambios rápidos sin validaciones complejas de business logic.
    Diferente de ProductUpdate: menos validaciones, más directo.
    """

    # Campos para operaciones PATCH rápidas
    precio_venta: Optional[Decimal] = Field(
        None, gt=0, description="Cambio rápido de precio de venta"
    )
    stock_quantity: Optional[int] = Field(
        None, ge=0, description="Ajuste directo de cantidad en stock"
    )
    is_active: Optional[bool] = Field(
        None, description="Cambio de estado activo/inactivo"
    )
    peso: Optional[Decimal] = Field(
        None, gt=0, description="Peso del producto en kilogramos"
    )
    categoria: Optional[str] = Field(
        None, max_length=100, description="Categoría del producto"
    )

    class Config(ProductConfig):
        json_schema_extra = {
            "example": {
                "precio_venta": 150000.0,
                "stock_quantity": 25,
                "is_active": True,
            }
        }
