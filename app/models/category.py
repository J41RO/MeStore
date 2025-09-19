# ~/app/models/category.py
# ---------------------------------------------------------------------------------------------
# MeStore - Category Models for Hierarchical Product Categorization
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: category.py
# Ruta: ~/app/models/category.py
# Autor: Database Architect AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: Modelo SQLAlchemy para sistema de categorías jerárquicas del marketplace
#            Soporte para categorías anidadas ilimitadas con materialized path optimization
#
# Características:
# - Estructura jerárquica self-referencing con parent_id
# - Materialized path para queries optimizadas de árboles
# - Support para metadatos (SEO, imágenes, orden de display)
# - Validaciones de integridad referencial
# - Índices optimizados para performance en miles de productos
# - Soft delete support heredado de BaseModel
#
# ---------------------------------------------------------------------------------------------

"""
Category Models para MeStore Marketplace.

Este módulo contiene los modelos para el sistema de categorías jerárquicas:
- Category: Modelo principal con estructura self-referencing
- ProductCategory: Tabla de relación many-to-many con Product
- Optimizaciones de performance con materialized path
- Métodos de utilidad para navegación del árbol de categorías
- Support para metadatos SEO y configuración de display
"""

from typing import Dict, List, Optional, Set
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
import json
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property

from app.models.base import BaseModel


class CategoryStatus(PyEnum):
    """
    Estados de categoría en el marketplace.

    ACTIVE: Categoría activa y visible
    INACTIVE: Categoría inactiva pero preservada
    HIDDEN: Categoría oculta temporalmente
    """
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    HIDDEN = "HIDDEN"


class Category(BaseModel):
    """
    Modelo Category para estructura jerárquica de categorías.

    Implementa un sistema de categorías anidadas con:
    - Self-referencing para jerarquía padre-hijo
    - Materialized path para queries optimizadas
    - Level tracking para profundidad del árbol
    - Metadatos para SEO y display
    - Sort order para control de ordenamiento

    Campos principales:
    - name: Nombre de la categoría
    - slug: URL-friendly identifier único
    - description: Descripción de la categoría
    - parent_id: Referencia al padre (nullable para root categories)
    - path: Materialized path (e.g., "/electronics/phones/smartphones/")
    - level: Nivel en el árbol (0 = root, 1 = child, etc.)
    - sort_order: Orden de display dentro del nivel
    - is_active: Estado activo/inactivo
    - status: Estado detallado de la categoría

    Metadatos:
    - meta_title: Título SEO
    - meta_description: Descripción SEO
    - meta_keywords: Keywords SEO
    - icon_url: URL del ícono de categoría
    - banner_url: URL del banner de categoría
    - display_config: Configuración JSON para display frontend
    """

    __tablename__ = "categories"

    # Campos principales
    name = Column(
        String(200),
        nullable=False,
        index=True,
        comment="Nombre de la categoría"
    )

    slug = Column(
        String(200),
        nullable=False,
        unique=True,
        index=True,
        comment="URL-friendly identifier único"
    )

    description = Column(
        Text,
        nullable=True,
        comment="Descripción detallada de la categoría"
    )

    # Jerarquía
    parent_id = Column(
        String(36),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID de la categoría padre (NULL para root categories)"
    )

    # Materialized path optimization
    path = Column(
        String(1000),
        nullable=False,
        index=True,
        comment="Materialized path del árbol (e.g., '/electronics/phones/')"
    )

    level = Column(
        Integer,
        nullable=False,
        default=0,
        index=True,
        comment="Nivel en el árbol de categorías (0 = root)"
    )

    # Display y ordenamiento
    sort_order = Column(
        Integer,
        nullable=False,
        default=0,
        index=True,
        comment="Orden de display dentro del nivel"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Estado activo de la categoría"
    )

    status = Column(
        String(20),
        nullable=False,
        default=CategoryStatus.ACTIVE.value,
        index=True,
        comment="Estado detallado de la categoría"
    )

    # Metadatos SEO
    meta_title = Column(
        String(255),
        nullable=True,
        comment="Título SEO de la categoría"
    )

    meta_description = Column(
        String(500),
        nullable=True,
        comment="Descripción SEO de la categoría"
    )

    meta_keywords = Column(
        Text,
        nullable=True,
        comment="Keywords SEO separadas por comas"
    )

    # Assets visuales
    icon_url = Column(
        String(500),
        nullable=True,
        comment="URL del ícono de la categoría"
    )

    banner_url = Column(
        String(500),
        nullable=True,
        comment="URL del banner de la categoría"
    )

    # Configuración frontend - SQLite compatible
    display_config = Column(
        Text,
        nullable=True,
        comment="Configuración JSON serializada para display frontend"
    )

    # Estadísticas de uso
    product_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Contador de productos en esta categoría"
    )

    # Relationships
    parent = relationship(
        "Category",
        remote_side="Category.id",
        back_populates="children"
    )

    children = relationship(
        "Category",
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="Category.sort_order"
    )

    # Many-to-many con Product a través de ProductCategory
    products = relationship(
        "Product",
        secondary="product_categories",
        back_populates="categories"
    )

    # Índices compuestos para optimización
    __table_args__ = (
        # Unique constraint para slug
        UniqueConstraint("slug", name="uq_category_slug"),

        # Índice compuesto para jerarquía
        Index("ix_category_parent_level", "parent_id", "level"),
        Index("ix_category_parent_sort", "parent_id", "sort_order"),

        # Índice para path queries (ancestros/descendientes)
        Index("ix_category_path_level", "path", "level"),

        # Índice para queries activas
        Index("ix_category_active_status", "is_active", "status"),
        Index("ix_category_active_sort", "is_active", "sort_order"),

        # Índice para búsquedas por nombre
        Index("ix_category_name_active", "name", "is_active"),

        # Índice compuesto para display ordenado
        Index("ix_category_parent_active_sort", "parent_id", "is_active", "sort_order"),
    )

    def __init__(self, **kwargs):
        """
        Inicializar Category con path y level automáticos.

        Args:
            **kwargs: Argumentos para crear la categoría
        """
        # Si no se especifica status, usar default
        if "status" not in kwargs:
            kwargs["status"] = CategoryStatus.ACTIVE.value

        super().__init__(**kwargs)

        # Generar path automáticamente si no se especifica
        if not hasattr(self, "path") or not self.path:
            self.update_path()

    @validates("name")
    def validate_name(self, key, name):
        """Validar nombre de categoría."""
        if not name or len(name.strip()) == 0:
            raise ValueError("Nombre de categoría no puede estar vacío")
        if len(name) > 200:
            raise ValueError("Nombre no puede exceder 200 caracteres")
        return name.strip()

    @validates("slug")
    def validate_slug(self, key, slug):
        """Validar slug de categoría."""
        if not slug or len(slug.strip()) == 0:
            raise ValueError("Slug no puede estar vacío")
        if len(slug) > 200:
            raise ValueError("Slug no puede exceder 200 caracteres")

        # Normalizar slug: lowercase, replace spaces/special chars
        import re
        normalized_slug = re.sub(r'[^a-z0-9\-_]', '-', slug.lower().strip())
        normalized_slug = re.sub(r'-+', '-', normalized_slug)  # Multiple dashes to single
        normalized_slug = normalized_slug.strip('-')  # Remove leading/trailing dashes

        return normalized_slug

    @validates("path")
    def validate_path(self, key, path):
        """Validar materialized path."""
        if not path:
            return "/"

        # Asegurar que path empiece y termine con /
        if not path.startswith("/"):
            path = "/" + path
        if not path.endswith("/"):
            path = path + "/"

        return path

    def update_path(self):
        """
        Actualizar materialized path basado en jerarquía.

        El path se construye desde la raíz hasta esta categoría:
        - Root category: "/"
        - Child category: "/parent_slug/"
        - Grandchild: "/grandparent_slug/parent_slug/"
        """
        if self.parent_id is None:
            # Root category
            self.path = f"/{self.slug}/" if hasattr(self, "slug") and self.slug else "/"
            self.level = 0
        else:
            # Child category - necesita parent.path
            if self.parent:
                self.path = f"{self.parent.path}{self.slug}/"
                self.level = self.parent.level + 1
            else:
                # Fallback si parent no está cargado
                self.path = f"/{self.slug}/"
                self.level = 1

    def update_children_paths(self):
        """
        Actualizar paths de todos los hijos recursivamente.
        Útil cuando se cambia el slug de una categoría.
        """
        for child in self.children:
            child.update_path()
            child.update_children_paths()

    @hybrid_property
    def full_name(self) -> str:
        """
        Nombre completo con jerarquía.

        Returns:
            str: Nombre con path completo (e.g., "Electrónicos > Teléfonos > Smartphones")
        """
        if self.parent_id is None:
            return self.name

        # Construir desde path
        path_parts = [part for part in self.path.split("/") if part]
        if len(path_parts) <= 1:
            return self.name

        # Para efficiency, podrían cachearse los nombres en el path
        return " > ".join(path_parts[:-1]) + f" > {self.name}"

    def get_ancestors(self, session) -> List["Category"]:
        """
        Obtener todas las categorías ancestro ordenadas desde root.

        Args:
            session: SQLAlchemy session

        Returns:
            List[Category]: Lista de ancestros desde root hasta parent
        """
        if self.level == 0:
            return []

        # Query usando materialized path para efficiency
        ancestors = (
            session.query(Category)
            .filter(
                Category.path != self.path,  # Excluir self
                self.path.startswith(Category.path),  # Self path starts with ancestor path
                Category.is_active == True
            )
            .order_by(Category.level)
            .all()
        )

        return ancestors

    def get_descendants(self, session, max_depth: Optional[int] = None) -> List["Category"]:
        """
        Obtener todas las categorías descendientes.

        Args:
            session: SQLAlchemy session
            max_depth: Profundidad máxima (optional)

        Returns:
            List[Category]: Lista de descendientes ordenados por level y sort_order
        """
        query = (
            session.query(Category)
            .filter(
                Category.path != self.path,  # Excluir self
                Category.path.startswith(self.path),  # Descendant path starts with self path
                Category.is_active == True
            )
        )

        if max_depth is not None:
            max_level = self.level + max_depth
            query = query.filter(Category.level <= max_level)

        descendants = query.order_by(Category.level, Category.sort_order).all()
        return descendants

    def get_siblings(self, session) -> List["Category"]:
        """
        Obtener categorías hermanas (mismo parent).

        Args:
            session: SQLAlchemy session

        Returns:
            List[Category]: Lista de hermanas ordenadas por sort_order
        """
        siblings = (
            session.query(Category)
            .filter(
                Category.parent_id == self.parent_id,
                Category.id != self.id,
                Category.is_active == True
            )
            .order_by(Category.sort_order)
            .all()
        )

        return siblings

    def get_breadcrumb(self, session) -> List[Dict]:
        """
        Obtener breadcrumb completo para navigation.

        Args:
            session: SQLAlchemy session

        Returns:
            List[Dict]: Lista de breadcrumb items con name, slug, url
        """
        ancestors = self.get_ancestors(session)
        breadcrumb = []

        # Agregar ancestros
        for ancestor in ancestors:
            breadcrumb.append({
                "id": str(ancestor.id),
                "name": ancestor.name,
                "slug": ancestor.slug,
                "url": f"/categories/{ancestor.slug}",
                "level": ancestor.level
            })

        # Agregar self
        breadcrumb.append({
            "id": str(self.id),
            "name": self.name,
            "slug": self.slug,
            "url": f"/categories/{self.slug}",
            "level": self.level
        })

        return breadcrumb

    def get_product_count_recursive(self, session) -> int:
        """
        Obtener conteo de productos incluyendo subcategorías.

        Args:
            session: SQLAlchemy session

        Returns:
            int: Total de productos en esta categoría y subcategorías
        """
        from app.models.product import Product

        # Obtener IDs de esta categoría y descendientes
        descendant_categories = self.get_descendants(session)
        category_ids = [self.id] + [cat.id for cat in descendant_categories]

        # Query products count
        count = (
            session.query(func.count(Product.id.distinct()))
            .join(ProductCategory)
            .filter(ProductCategory.category_id.in_(category_ids))
            .scalar()
        )

        return count or 0

    def is_ancestor_of(self, other_category: "Category") -> bool:
        """
        Verificar si esta categoría es ancestro de otra.

        Args:
            other_category: Categoría a verificar

        Returns:
            bool: True si es ancestro
        """
        return (
            other_category.path.startswith(self.path) and
            other_category.path != self.path and
            other_category.level > self.level
        )

    def is_descendant_of(self, other_category: "Category") -> bool:
        """
        Verificar si esta categoría es descendiente de otra.

        Args:
            other_category: Categoría a verificar

        Returns:
            bool: True si es descendiente
        """
        return other_category.is_ancestor_of(self)

    def can_have_parent(self, parent_category: Optional["Category"]) -> bool:
        """
        Verificar si puede tener un parent específico (evitar loops).

        Args:
            parent_category: Categoría padre candidata

        Returns:
            bool: True si puede ser parent sin crear loop
        """
        if parent_category is None:
            return True  # Root category is always valid

        # No puede ser parent de sí mismo
        if parent_category.id == self.id:
            return False

        # No puede ser parent si esta categoría es ancestro del parent candidato
        return not self.is_ancestor_of(parent_category)

    def to_dict(self, include_hierarchy: bool = False, session=None) -> dict:
        """
        Serializar categoría a diccionario.

        Args:
            include_hierarchy: Incluir datos de jerarquía
            session: SQLAlchemy session para hierarchy data

        Returns:
            dict: Representación completa de la categoría
        """
        base_dict = super().to_dict()

        category_dict = {
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "path": self.path,
            "level": self.level,
            "sort_order": self.sort_order,
            "is_active": self.is_active,
            "status": self.status,
            "meta_title": self.meta_title,
            "meta_description": self.meta_description,
            "meta_keywords": self.meta_keywords,
            "icon_url": self.icon_url,
            "banner_url": self.banner_url,
            "display_config": self.display_config,
            "product_count": self.product_count,
            "full_name": self.full_name,
        }

        if include_hierarchy and session:
            category_dict.update({
                "ancestors": [cat.to_dict() for cat in self.get_ancestors(session)],
                "breadcrumb": self.get_breadcrumb(session),
                "children_count": len(self.children) if self.children else 0,
                "product_count_recursive": self.get_product_count_recursive(session),
            })

        return {**base_dict, **category_dict}

    def __repr__(self) -> str:
        """Representación técnica de la categoría."""
        return f"<Category(id={self.id}, slug='{self.slug}', name='{self.name}', level={self.level})>"

    def __str__(self) -> str:
        """Representación amigable de la categoría."""
        return f"Categoría {self.name} (Level {self.level})"

    @classmethod
    def get_root_categories(cls, session, active_only: bool = True):
        """
        Obtener categorías raíz.

        Args:
            session: SQLAlchemy session
            active_only: Solo categorías activas

        Returns:
            List[Category]: Lista de categorías raíz ordenadas por sort_order
        """
        query = session.query(cls).filter(cls.parent_id.is_(None))

        if active_only:
            query = query.filter(cls.is_active == True)

        return query.order_by(cls.sort_order).all()

    @classmethod
    def get_category_tree(cls, session, max_depth: Optional[int] = None, active_only: bool = True):
        """
        Obtener árbol completo de categorías.

        Args:
            session: SQLAlchemy session
            max_depth: Profundidad máxima
            active_only: Solo categorías activas

        Returns:
            List[Dict]: Árbol de categorías con children anidados
        """
        query = session.query(cls)

        if active_only:
            query = query.filter(cls.is_active == True)

        if max_depth is not None:
            query = query.filter(cls.level <= max_depth)

        categories = query.order_by(cls.level, cls.sort_order).all()

        # Construir árbol
        category_map = {cat.id: cat.to_dict() for cat in categories}
        tree = []

        for cat in categories:
            cat_dict = category_map[cat.id]
            cat_dict["children"] = []

            if cat.parent_id is None:
                tree.append(cat_dict)
            else:
                parent_dict = category_map.get(cat.parent_id)
                if parent_dict:
                    parent_dict["children"].append(cat_dict)

        return tree


class ProductCategory(BaseModel):
    """
    Tabla de relación many-to-many entre Product y Category.

    Permite que un producto pertenezca a múltiples categorías y
    soporta configuración de categoría principal vs secundarias.

    Campos:
    - product_id: ID del producto
    - category_id: ID de la categoría
    - is_primary: Si es la categoría principal del producto
    - sort_order: Orden de la categoría para el producto
    - assigned_by_id: Usuario que asignó la categoría
    - assigned_at: Timestamp de asignación
    """

    __tablename__ = "product_categories"

    # Foreign keys
    product_id = Column(
        String(36),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del producto"
    )

    category_id = Column(
        String(36),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la categoría"
    )

    # Configuración de relación
    is_primary = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Si es la categoría principal del producto"
    )

    sort_order = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Orden de la categoría para el producto"
    )

    # Tracking de asignación
    assigned_by_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
        comment="Usuario que asignó la categoría"
    )

    # Relationships
    product = relationship("Product", back_populates="category_associations")
    category = relationship("Category")
    assigned_by = relationship("User")

    # Constraints e índices
    __table_args__ = (
        # Unique constraint para evitar duplicados
        UniqueConstraint("product_id", "category_id", name="uq_product_category"),

        # Índices para queries comunes
        Index("ix_product_category_product", "product_id"),
        Index("ix_product_category_category", "category_id"),
        Index("ix_product_category_primary", "is_primary"),
        Index("ix_product_category_product_primary", "product_id", "is_primary"),
        Index("ix_product_category_category_primary", "category_id", "is_primary"),
    )

    def __repr__(self) -> str:
        """Representación técnica de la relación."""
        return f"<ProductCategory(product_id={self.product_id}, category_id={self.category_id}, is_primary={self.is_primary})>"

    def to_dict(self) -> dict:
        """Serializar relación a diccionario."""
        base_dict = super().to_dict()

        relation_dict = {
            "product_id": str(self.product_id),
            "category_id": str(self.category_id),
            "is_primary": self.is_primary,
            "sort_order": self.sort_order,
            "assigned_by_id": str(self.assigned_by_id) if self.assigned_by_id else None,
        }

        return {**base_dict, **relation_dict}