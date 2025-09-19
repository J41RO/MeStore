# ~/app/models/product.py
# ---------------------------------------------------------------------------------------------
# MeStore - Modelo Product para gestión de productos
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: product.py
# Ruta: ~/app/models/product.py
# Autor: Jairo
# Fecha de Creación: 2025-07-27
# Última Actualización: 2025-07-28
# Versión: 1.2.0
# Propósito: Modelo SQLAlchemy para entidad Product con campos básicos, pricing y fulfillment
#            Gestión de productos del marketplace (sku, name, description, pricing, logística)
#
# Modificaciones:
# 2025-07-27 - Creación inicial del modelo Product básico
# 2025-07-28 - Añadidos campos de pricing (precio_venta, precio_costo, comision_mestocker)
# 2025-07-28 - Añadidos campos de fulfillment (peso, dimensiones, categoria, tags)
#
# ---------------------------------------------------------------------------------------------

"""
Modelo Product para MeStore.

Este módulo contiene el modelo SQLAlchemy para la entidad Product:
- Product: Modelo principal con campos básicos (sku, name, description)
- Campos de pricing: precio_venta, precio_costo, comision_mestocker
- Campos de fulfillment: peso, dimensiones, categoria, tags
- Herencia de BaseModel: str, timestamps automáticos y soft delete
- Métodos personalizados: __repr__, __str__, to_dict()
- Métodos de negocio: calcular_margen(), calcular_porcentaje_margen()
- Métodos de fulfillment: calcular_volumen(), tiene_tag()
- Índices para optimización: sku (unique), name (búsquedas), categoria
"""

from datetime import datetime, timedelta
from enum import Enum as PyEnum
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.inventory import Inventory

from sqlalchemy import (
    DECIMAL,
    Column,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
import json
from sqlalchemy.orm import relationship, validates

from app.models.base import BaseModel


class ProductStatus(PyEnum):
    """
    Enumeración para estados del producto en el marketplace.

    Estados del flujo de vida del producto:
        TRANSITO: Producto en tránsito hacia almacén
        VERIFICADO: Producto verificado y en proceso de catalogación
        DISPONIBLE: Producto disponible para venta
        VENDIDO: Producto vendido y no disponible
    """

    TRANSITO = "TRANSITO"
    VERIFICADO = "VERIFICADO"
    DISPONIBLE = "DISPONIBLE"
    VENDIDO = "VENDIDO"


class Product(BaseModel):
    """
    Modelo Product para gestión de productos del marketplace.

    Hereda de BaseModel los campos:
    - id: str primary key
    - created_at: Timestamp de creación
    - updated_at: Timestamp de última actualización
    - deleted_at: Timestamp de soft delete (nullable)

    Campos específicos:
    - sku: Código único del producto (String 50 chars, unique, indexed)
    - name: Nombre del producto (String 200 chars, indexed)
    - description: Descripción detallada (Text, optional)
    - status: Estado del producto (Enum ProductStatus)

    Campos de pricing:
    - precio_venta: Precio de venta al público (DECIMAL 10,2)
    - precio_costo: Precio de costo/compra (DECIMAL 10,2)
    - comision_mestocker: Comisión de MeStore (DECIMAL 10,2)

    Campos de fulfillment:
    - peso: Peso del producto en kilogramos (DECIMAL 8,3)
    - dimensiones: Dimensiones del producto en JSON {largo, ancho, alto} cm
    - categoria: Categoría del producto (String 100 chars, indexed)
    - tags: Tags del producto como array JSON para búsquedas
    """

    __tablename__ = "products"

    # Campos específicos del producto
    sku = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Código único del producto para identificación",
    )

    # === MÉTODOS DE STOCK TRACKING AGREGADO ===
    def get_stock_total(self) -> int:
        """Obtener stock total sumando todas las ubicaciones"""
        if not self.ubicaciones_inventario:
            return 0
        return sum(ubicacion.cantidad for ubicacion in self.ubicaciones_inventario)

    def get_stock_disponible(self) -> int:
        """Obtener stock disponible sumando todas las ubicaciones"""
        if not self.ubicaciones_inventario:
            return 0
        return sum(
            ubicacion.cantidad_disponible() for ubicacion in self.ubicaciones_inventario
        )

    def get_stock_reservado(self) -> int:
        """Obtener stock reservado sumando todas las ubicaciones"""
        if not self.ubicaciones_inventario:
            return 0
        return sum(
            ubicacion.cantidad_reservada for ubicacion in self.ubicaciones_inventario
        )

    def get_ubicaciones_stock(self) -> List[Dict]:
        """Obtener resumen de stock por ubicación"""
        if not self.ubicaciones_inventario:
            return []

        return [
            {
                "ubicacion": ubicacion.get_ubicacion_completa(),
                "zona": ubicacion.zona,
                "estante": ubicacion.estante,
                "posicion": ubicacion.posicion,
                "cantidad_total": ubicacion.cantidad,
                "cantidad_reservada": ubicacion.cantidad_reservada,
                "cantidad_disponible": ubicacion.cantidad_disponible(),
            }
            for ubicacion in self.ubicaciones_inventario
        ]

    def tiene_stock_disponible(self) -> bool:
        """Verificar si hay stock disponible en cualquier ubicación"""
        return self.get_stock_disponible() > 0

    # ===== MÉTODOS DE ALERTAS =====

    def is_low_stock(self, umbral: int) -> bool:
        """
        Verificar si el producto tiene stock bajo.
        Args:
            umbral: Umbral mínimo de stock
        Returns:
            bool: True si el stock está por debajo del umbral
        """
        stock_total = self.get_stock_total()
        return stock_total < umbral

    def days_since_last_movement(self) -> int:
        """
        Calcular días desde el último movimiento del producto.
        Returns:
            int: Días desde la última actualización de inventory
        """
        from sqlalchemy import func
        from sqlalchemy.orm import Session

        from app.models.inventory import Inventory

        # Buscar la última actualización en inventory para este producto
        if hasattr(self, "_sa_instance_state") and self._sa_instance_state.session:
            session = self._sa_instance_state.session
            ultima_actualizacion = (
                session.query(func.max(Inventory.updated_at))
                .filter(Inventory.product_id == self.id)
                .scalar()
            )

            if ultima_actualizacion:
                delta = datetime.now() - ultima_actualizacion
                return delta.days

        # Si no hay datos de inventory, retornar días desde creación del producto
        if self.created_at:
            delta = datetime.now() - self.created_at
            return delta.days

        return 0

    @classmethod
    def get_low_stock_products(cls, session, umbral: int):
        """
        Obtener productos con stock bajo.
        Args:
            session: Sesión de SQLAlchemy
            umbral: Umbral mínimo de stock
        Returns:
            List[Product]: Lista de productos con stock bajo
        """
        from sqlalchemy import func

        from app.models.inventory import Inventory

        # Subquery para calcular stock total por producto
        stock_subquery = (
            session.query(
                Inventory.product_id,
                func.coalesce(func.sum(Inventory.cantidad), 0).label("stock_total"),
            )
            .group_by(Inventory.product_id)
            .subquery()
        )

        # Query principal con join
        productos_bajo_stock = (
            session.query(cls)
            .join(stock_subquery, cls.id == stock_subquery.c.product_id)
            .filter(stock_subquery.c.stock_total < umbral)
            .all()
        )

        return productos_bajo_stock

    @classmethod
    def get_inactive_products(cls, session, dias: int):
        """
        Obtener productos sin movimiento en X días.
        Args:
            session: Sesión de SQLAlchemy
            dias: Número de días para considerar inactivo
        Returns:
            List[Product]: Lista de productos sin movimiento
        """
        from sqlalchemy import func

        from app.models.inventory import Inventory

        fecha_limite = datetime.now() - timedelta(days=dias)

        # Subquery para última actualización por producto
        ultima_actualizacion_subquery = (
            session.query(
                Inventory.product_id,
                func.max(Inventory.updated_at).label("ultima_actualizacion"),
            )
            .group_by(Inventory.product_id)
            .subquery()
        )

        # Productos sin movimiento reciente
        productos_inactivos = (
            session.query(cls)
            .join(
                ultima_actualizacion_subquery,
                cls.id == ultima_actualizacion_subquery.c.product_id,
            )
            .filter(ultima_actualizacion_subquery.c.ultima_actualizacion < fecha_limite)
            .all()
        )

        # También incluir productos que nunca han tenido inventory
        productos_sin_inventory = (
            session.query(cls)
            .outerjoin(Inventory, cls.id == Inventory.product_id)
            .filter(Inventory.product_id.is_(None), cls.created_at < fecha_limite)
            .all()
        )

        return productos_inactivos + productos_sin_inventory

    def buscar_ubicacion_disponible(
        self, cantidad_requerida: int
    ) -> Optional["Inventory"]:
        """Encontrar ubicación con stock suficiente"""
        for ubicacion in self.ubicaciones_inventario:
            if ubicacion.cantidad_disponible() >= cantidad_requerida:
                return ubicacion
        return None

    # === CATEGORY MANAGEMENT METHODS ===

    def get_primary_category(self) -> Optional["Category"]:
        """
        Obtener la categoría principal del producto.

        Returns:
            Optional[Category]: Categoría principal o None si no tiene
        """
        for association in self.category_associations:
            if association.is_primary:
                return association.category
        return None

    def get_secondary_categories(self) -> List["Category"]:
        """
        Obtener categorías secundarias del producto.

        Returns:
            List[Category]: Lista de categorías secundarias
        """
        secondary_cats = []
        for association in self.category_associations:
            if not association.is_primary:
                secondary_cats.append(association.category)
        return secondary_cats

    def add_category(self, category: "Category", is_primary: bool = False, sort_order: int = 0, assigned_by_id: Optional[str] = None) -> None:
        """
        Agregar categoría al producto.

        Args:
            category: Categoría a agregar
            is_primary: Si es la categoría principal
            sort_order: Orden de la categoría
            assigned_by_id: ID del usuario que asigna la categoría
        """
        from app.models.category import ProductCategory

        # Si se está marcando como primary, desmarcar otras primary categories
        if is_primary:
            for association in self.category_associations:
                if association.is_primary:
                    association.is_primary = False

        # Crear nueva asociación
        new_association = ProductCategory(
            product_id=self.id,
            category_id=category.id,
            is_primary=is_primary,
            sort_order=sort_order,
            assigned_by_id=assigned_by_id
        )

        self.category_associations.append(new_association)

    def remove_category(self, category: "Category") -> bool:
        """
        Remover categoría del producto.

        Args:
            category: Categoría a remover

        Returns:
            bool: True si se removió exitosamente
        """
        for association in self.category_associations:
            if association.category_id == category.id:
                self.category_associations.remove(association)
                return True
        return False

    def set_primary_category(self, category: "Category", assigned_by_id: Optional[str] = None) -> None:
        """
        Establecer categoría principal del producto.

        Args:
            category: Categoría a establecer como principal
            assigned_by_id: ID del usuario que asigna
        """
        # Verificar si la categoría ya está asignada
        existing_association = None
        for association in self.category_associations:
            if association.category_id == category.id:
                existing_association = association
                break

        # Desmarcar otras categorías como primary
        for association in self.category_associations:
            if association.is_primary:
                association.is_primary = False

        # Si la categoría ya existe, marcarla como primary
        if existing_association:
            existing_association.is_primary = True
            if assigned_by_id:
                existing_association.assigned_by_id = assigned_by_id
        else:
            # Agregar nueva categoría como primary
            self.add_category(category, is_primary=True, assigned_by_id=assigned_by_id)

    def has_category(self, category: "Category") -> bool:
        """
        Verificar si el producto tiene una categoría específica.

        Args:
            category: Categoría a verificar

        Returns:
            bool: True si el producto tiene la categoría
        """
        for association in self.category_associations:
            if association.category_id == category.id:
                return True
        return False

    def has_category_in_hierarchy(self, category: "Category") -> bool:
        """
        Verificar si el producto tiene una categoría o alguna de sus subcategorías.

        Args:
            category: Categoría raíz a verificar

        Returns:
            bool: True si el producto está en la jerarquía de la categoría
        """
        for association in self.category_associations:
            # Verificar si la categoría del producto es descendiente de la categoría dada
            if (association.category.path.startswith(category.path) and
                association.category.level >= category.level):
                return True
        return False

    def get_category_breadcrumbs(self, session) -> List[List[Dict]]:
        """
        Obtener breadcrumbs de todas las categorías del producto.

        Args:
            session: SQLAlchemy session

        Returns:
            List[List[Dict]]: Lista de breadcrumbs para cada categoría
        """
        breadcrumbs = []
        for association in self.category_associations:
            category_breadcrumb = association.category.get_breadcrumb(session)
            breadcrumbs.append(category_breadcrumb)
        return breadcrumbs

    def migrate_from_old_categoria(self, session, assigned_by_id: Optional[str] = None) -> None:
        """
        Migrar del campo categoria string al nuevo sistema de categorías.

        Args:
            session: SQLAlchemy session
            assigned_by_id: ID del usuario que realiza la migración
        """
        if not self.categoria:
            return

        from app.models.category import Category

        # Buscar categoría existente por nombre
        existing_category = (
            session.query(Category)
            .filter(Category.name.ilike(f"%{self.categoria}%"))
            .first()
        )

        if existing_category:
            # Asignar categoría existente como primary
            self.set_primary_category(existing_category, assigned_by_id)
        else:
            # Crear nueva categoría desde string
            import re
            slug = re.sub(r'[^a-z0-9\-_]', '-', self.categoria.lower().strip())
            slug = re.sub(r'-+', '-', slug).strip('-')

            new_category = Category(
                name=self.categoria,
                slug=slug,
                description=f"Categoría migrada desde producto: {self.categoria}",
                path=f"/{slug}/",
                level=0,
                is_active=True
            )

            session.add(new_category)
            session.flush()  # Para obtener el ID

            # Asignar nueva categoría como primary
            self.set_primary_category(new_category, assigned_by_id)

    # Relationship con User (vendedor)
    vendedor_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
        comment="ID del usuario vendedor que registró el producto",
    )

    # Tracking de cambios
    created_by_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
        comment="ID del usuario que creó el producto",
    )

    updated_by_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
        comment="ID del usuario que actualizó por última vez",
    )

    version = Column(
        Integer,
        default=1,
        nullable=False,
        comment="Versión del producto para control de cambios",
    )
    # Relationships
    vendedor = relationship(
        "User", foreign_keys=[vendedor_id], back_populates="productos_vendidos"
    )

    created_by = relationship(
        "User", foreign_keys=[created_by_id], backref="productos_creados"
    )

    updated_by = relationship(
        "User", foreign_keys=[updated_by_id], backref="productos_actualizados"
    )

    # Inventory relationship
    ubicaciones_inventario = relationship("Inventory", back_populates="product")

    # Transaction relationship
    transacciones = relationship("Transaction", back_populates="product")
    name = Column(
        String(200),
        nullable=False,
        index=True,
        comment="Nombre del producto para búsquedas",
    )

    description = Column(
        Text, nullable=True, comment="Descripción detallada del producto"
    )

    status = Column(
        Enum(ProductStatus),
        nullable=False,
        default=ProductStatus.TRANSITO,
        comment="Estado actual del producto en el marketplace",
    )

    # Campos de pricing
    precio_venta = Column(
        DECIMAL(10, 2), nullable=True, comment="Precio de venta al público (COP)"
    )

    precio_costo = Column(
        DECIMAL(10, 2),
        nullable=True,
        comment="Precio de costo/compra del producto (COP)",
    )

    comision_mestocker = Column(
        DECIMAL(10, 2),
        nullable=True,
        comment="Comisión de MeStore por venta del producto (COP)",
    )

    # Campos de fulfillment
    peso = Column(
        DECIMAL(8, 3), nullable=True, comment="Peso del producto en kilogramos"
    )

    dimensiones = Column(
        Text,
        nullable=True,
        comment="Dimensiones del producto: {largo, ancho, alto} en cm - JSON serializado",
    )

    categoria = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Categoría del producto para organización",
    )

    tags = Column(
        Text, nullable=True, comment="Tags del producto como array JSON serializado para búsquedas"
    )

    # Índices adicionales para optimización
    __table_args__ = (
        Index("ix_product_name_sku", "name", "sku"),  # Índice compuesto
        Index("ix_product_created_at", "created_at"),  # Para ordenamiento temporal
        Index(
            "ix_product_vendedor_status", "vendedor_id", "status"
        ),  # Productos por vendedor
        Index("ix_product_status_created", "status", "created_at"),  # Estado temporal
        Index(
            "ix_product_vendedor_status_created", "vendedor_id", "status", "created_at"
        ),  # Query compleja
        # Índices GIN para búsqueda de texto optimizada
        # Index('ix_product_name_gin', text('name gin_trgm_ops'), postgresql_using='gin'),  # Búsqueda similitud nombre (deshabilitado para compatibilidad SQLite)
        # Index('ix_product_description_gin', text('description gin_trgm_ops'), postgresql_using='gin'),  # Búsqueda similitud descripción (deshabilitado para compatibilidad SQLite)
        # Index('ix_product_name_fulltext', func.to_tsvector('spanish', 'name'), postgresql_using='gin'),  # Búsqueda full-text nombre (deshabilitado para compatibilidad SQLite)
        # Index('ix_product_description_fulltext', func.to_tsvector('spanish', 'description'), postgresql_using='gin'),  # Búsqueda full-text descripción (deshabilitado para compatibilidad SQLite)
    )

    def __init__(self, **kwargs):
        """
        Inicializar Product con default status si no se especifica.

        Args:
            **kwargs: Argumentos para crear el producto
        """
        # Si no se especifica status, aplicar default
        if "status" not in kwargs:
            kwargs["status"] = ProductStatus.TRANSITO

        # Llamar al __init__ de BaseModel
        super().__init__(**kwargs)

    @validates("sku")
    def validate_sku(self, key, sku):
        """Validar formato de SKU."""
        if not sku or len(sku.strip()) == 0:
            raise ValueError("SKU no puede estar vacío")
        if len(sku) > 50:
            raise ValueError("SKU no puede exceder 50 caracteres")
        return sku.strip().upper()  # Normalizar a mayúsculas

    @validates("name")
    def validate_name(self, key, name):
        """Validar nombre del producto."""
        if not name or len(name.strip()) == 0:
            raise ValueError("Nombre del producto no puede estar vacío")
        if len(name) > 200:
            raise ValueError("Nombre no puede exceder 200 caracteres")
        return name.strip()

    def set_vendedor(self, user_id: str) -> None:
        """Asignar vendedor al producto"""
        self.vendedor_id = user_id
        self.increment_version()

    def increment_version(self) -> None:
        """Incrementar versión para tracking"""
        if self.version is None:
            self.version = 1
        else:
            self.version += 1

    def update_tracking(self, user_id: str) -> None:
        """Actualizar tracking de cambios"""
        self.updated_by_id = user_id
        self.increment_version()

    def is_vendido_por(self, user_id: str) -> bool:
        """Verificar si producto es vendido por usuario específico"""
        return self.vendedor_id == user_id

    def __repr__(self) -> str:
        """
        Representación técnica del objeto Product.

        Returns:
            str: Representación técnica con SKU y name
        """
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}')>"

    def __str__(self) -> str:
        """
        Representación amigable del producto.

        Returns:
            str: String amigable del producto
        """
        return f"Producto {self.sku}: {self.name}"

    def to_dict(self) -> dict:
        """
        Serializar producto a diccionario.

        Returns:
            dict: Representación completa del producto incluyendo fulfillment
        """
        # Usar método base y extender con campos específicos
        base_dict = super().to_dict()
        product_dict = {
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
            "status": self.status.value if self.status else None,
            "precio_venta": float(self.precio_venta) if self.precio_venta else None,
            "precio_costo": float(self.precio_costo) if self.precio_costo else None,
            "comision_mestocker": (
                float(self.comision_mestocker) if self.comision_mestocker else None
            ),
            "peso": float(self.peso) if self.peso else None,
            "dimensiones": self.dimensiones,
            "categoria": self.categoria,
            "tags": self.tags,
            "vendedor_id": str(self.vendedor_id) if self.vendedor_id else None,
            "created_by_id": str(self.created_by_id) if self.created_by_id else None,
            "updated_by_id": str(self.updated_by_id) if self.updated_by_id else None,
            "version": self.version,
            "stock_total": self.get_stock_total(),
            "stock_disponible": self.get_stock_disponible(),
            "stock_reservado": self.get_stock_reservado(),
            "tiene_stock": self.tiene_stock_disponible(),
            "ubicaciones_count": (
                len(self.ubicaciones_inventario) if self.ubicaciones_inventario else 0
            ),
            # Nueva información de categorías
            "primary_category": (
                {
                    "id": str(self.get_primary_category().id),
                    "name": self.get_primary_category().name,
                    "slug": self.get_primary_category().slug,
                    "path": self.get_primary_category().path,
                    "level": self.get_primary_category().level
                } if self.get_primary_category() else None
            ),
            "categories_count": len(self.category_associations) if self.category_associations else 0,
            "secondary_categories": [
                {
                    "id": str(cat.id),
                    "name": cat.name,
                    "slug": cat.slug,
                    "path": cat.path,
                    "level": cat.level
                } for cat in self.get_secondary_categories()
            ] if self.category_associations else [],
        }
        return {**base_dict, **product_dict}

    def calcular_margen(self) -> float:
        """
        Calcular margen de ganancia.

        Returns:
            float: Margen en COP (precio_venta - precio_costo)
        """
        if self.precio_venta and self.precio_costo:
            return float(self.precio_venta - self.precio_costo)
        return 0.0

    def calcular_porcentaje_margen(self) -> float:
        """
        Calcular porcentaje de margen.

        Returns:
            float: Porcentaje de margen sobre precio_costo
        """
        if self.precio_venta and self.precio_costo and self.precio_costo > 0:
            return float(
                (self.precio_venta - self.precio_costo) / self.precio_costo * 100
            )
        return 0.0

    def calcular_volumen(self) -> float:
        """
        Calcular volumen en cm³ desde dimensiones.

        Returns:
            float: Volumen en cm³ o 0.0 si no hay dimensiones válidas
        """
        if self.dimensiones and all(
            k in self.dimensiones for k in ["largo", "ancho", "alto"]
        ):
            return float(
                self.dimensiones["largo"]
                * self.dimensiones["ancho"]
                * self.dimensiones["alto"]
            )
        return 0.0

    def tiene_tag(self, tag: str) -> bool:
        """
        Verificar si producto tiene un tag específico.

        Args:
            tag: Tag a buscar (case insensitive)

        Returns:
            bool: True si el producto tiene el tag especificado
        """
        if self.tags and isinstance(self.tags, list):
            return tag.lower() in [t.lower() for t in self.tags]
        return False

    def has_description(self) -> bool:
        """
        Verificar si el producto tiene descripción.

        Returns:
            bool: True si tiene descripción no vacía
        """
        return self.description is not None and len(self.description.strip()) > 0

    def get_display_name(self) -> str:
        """
        Obtener nombre para mostrar con SKU.

        Returns:
            str: Formato 'SKU - Name' para displays
        """
        return f"{self.sku} - {self.name}"

    # Relación con imágenes
    images = relationship(
        "ProductImage", back_populates="product", cascade="all, delete-orphan"
    )
    
    # Relación con cola de productos entrantes
    queue_entries = relationship(
        "IncomingProductQueue", back_populates="product", cascade="all, delete-orphan"
    )

    # === CATEGORY RELATIONSHIPS ===
    # Many-to-many relationship con Category a través de ProductCategory
    categories = relationship(
        "Category",
        secondary="product_categories",
        back_populates="products"
    )

    # Direct access a ProductCategory associations para control granular
    category_associations = relationship(
        "ProductCategory",
        back_populates="product",
        cascade="all, delete-orphan"
    )
