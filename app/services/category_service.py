# ~/app/services/category_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - Category Management Service
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: category_service.py
# Ruta: ~/app/services/category_service.py
# Autor: Database Architect AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: Service layer para gestión de categorías jerárquicas del marketplace
#            Operaciones optimizadas para alta performance con miles de productos
#
# Características:
# - CRUD operations optimizadas para Category y ProductCategory
# - Tree navigation con materialized path optimization
# - Bulk operations para asignación masiva de categorías
# - Category migration utilities
# - Performance monitoring y analytics
# - Cache-friendly operations para frontend
#
# ---------------------------------------------------------------------------------------------

"""
Category Management Service para MeStore Marketplace.

Este servicio proporciona operaciones optimizadas para el sistema de categorías:
- Gestión del árbol de categorías con materialized path
- Asignación y remoción de categorías de productos
- Navegación eficiente del árbol (ancestros, descendientes, hermanos)
- Operaciones masivas para migration y administración
- Queries optimizadas para frontend con cache support
- Analytics y reportes de uso de categorías
"""

from typing import List, Optional, Dict, Set, Tuple, Any
from uuid import UUID
import re

from sqlalchemy import func, and_, or_, desc, asc, text
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy.exc import IntegrityError

from app.models.category import Category, CategoryStatus, ProductCategory
from app.models.product import Product
from app.models.user import User


class CategoryService:
    """
    Service class para gestión avanzada de categorías jerárquicas.

    Proporciona operaciones optimizadas para:
    - Tree operations con materialized path
    - Product-category associations
    - Bulk operations y migrations
    - Performance analytics
    - Cache-friendly queries
    """

    def __init__(self, session: Session):
        """
        Inicializar CategoryService.

        Args:
            session: SQLAlchemy session
        """
        self.session = session

    # === CATEGORY CRUD OPERATIONS ===

    def create_category(
        self,
        name: str,
        slug: Optional[str] = None,
        description: Optional[str] = None,
        parent_id: Optional[UUID] = None,
        meta_data: Optional[Dict] = None,
        display_config: Optional[Dict] = None,
        sort_order: int = 0
    ) -> Category:
        """
        Crear nueva categoría con validaciones y path automático.

        Args:
            name: Nombre de la categoría
            slug: URL slug (se genera automáticamente si no se proporciona)
            description: Descripción opcional
            parent_id: ID de categoría padre (None para root)
            meta_data: Metadatos SEO (meta_title, meta_description, meta_keywords)
            display_config: Configuración de display para frontend
            sort_order: Orden de display

        Returns:
            Category: Nueva categoría creada

        Raises:
            ValueError: Si los datos son inválidos
            IntegrityError: Si el slug ya existe
        """

        # Generar slug automáticamente si no se proporciona
        if not slug:
            slug = self._generate_slug(name)

        # Validar que el slug sea único
        existing = self.get_category_by_slug(slug)
        if existing:
            raise ValueError(f"Ya existe una categoría con slug '{slug}'")

        # Obtener categoría padre si se especifica
        parent = None
        if parent_id:
            parent = self.get_category_by_id(parent_id)
            if not parent:
                raise ValueError(f"Categoría padre con ID {parent_id} no encontrada")

        # Crear categoría
        category_data = {
            "name": name,
            "slug": slug,
            "description": description,
            "parent_id": parent_id,
            "sort_order": sort_order,
            "is_active": True,
            "status": CategoryStatus.ACTIVE.value,
            "product_count": 0
        }

        # Agregar metadatos SEO si se proporcionan
        if meta_data:
            category_data.update({
                "meta_title": meta_data.get("meta_title"),
                "meta_description": meta_data.get("meta_description"),
                "meta_keywords": meta_data.get("meta_keywords")
            })

        # Agregar configuración de display
        if display_config:
            category_data["display_config"] = display_config

        category = Category(**category_data)

        # Actualizar path y level basado en parent
        if parent:
            category.path = f"{parent.path}{slug}/"
            category.level = parent.level + 1
        else:
            category.path = f"/{slug}/"
            category.level = 0

        try:
            self.session.add(category)
            self.session.flush()  # Para obtener ID sin commit
            return category

        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Error creando categoría: {str(e)}")

    def update_category(
        self,
        category_id: UUID,
        updates: Dict[str, Any],
        update_children_paths: bool = True
    ) -> Optional[Category]:
        """
        Actualizar categoría existente.

        Args:
            category_id: ID de la categoría
            updates: Diccionario con campos a actualizar
            update_children_paths: Si actualizar paths de hijos cuando cambie slug

        Returns:
            Optional[Category]: Categoría actualizada o None si no existe
        """
        category = self.get_category_by_id(category_id)
        if not category:
            return None

        # Campos que requieren tratamiento especial
        slug_changed = False
        old_slug = category.slug

        # Aplicar actualizaciones
        for field, value in updates.items():
            if hasattr(category, field):
                if field == "slug" and value != category.slug:
                    # Validar nuevo slug
                    if self.get_category_by_slug(value) and value != category.slug:
                        raise ValueError(f"Slug '{value}' ya está en uso")
                    slug_changed = True

                setattr(category, field, value)

        # Recalcular path si cambió el slug
        if slug_changed:
            category.update_path()

            if update_children_paths:
                category.update_children_paths()

        try:
            self.session.flush()
            return category

        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Error actualizando categoría: {str(e)}")

    def delete_category(
        self,
        category_id: UUID,
        move_products_to: Optional[UUID] = None,
        move_children_to: Optional[UUID] = None
    ) -> bool:
        """
        Eliminar categoría (soft delete) con manejo de productos y subcategorías.

        Args:
            category_id: ID de la categoría a eliminar
            move_products_to: ID de categoría destino para productos
            move_children_to: ID de categoría destino para subcategorías

        Returns:
            bool: True si se eliminó exitosamente
        """
        category = self.get_category_by_id(category_id)
        if not category:
            return False

        # Mover productos si se especifica
        if move_products_to:
            destination = self.get_category_by_id(move_products_to)
            if destination:
                self.move_category_products(category_id, move_products_to)

        # Mover subcategorías si se especifica
        if move_children_to:
            destination = self.get_category_by_id(move_children_to)
            if destination:
                for child in category.children:
                    child.parent_id = move_children_to
                    child.update_path()

        # Soft delete
        from datetime import datetime
        category.deleted_at = datetime.utcnow()
        category.is_active = False
        category.status = CategoryStatus.INACTIVE.value

        self.session.flush()
        return True

    # === CATEGORY RETRIEVAL OPERATIONS ===

    def get_category_by_id(self, category_id: UUID) -> Optional[Category]:
        """Obtener categoría por ID."""
        return (
            self.session.query(Category)
            .filter(Category.id == category_id, Category.deleted_at.is_(None))
            .first()
        )

    def get_category_by_slug(self, slug: str) -> Optional[Category]:
        """Obtener categoría por slug."""
        return (
            self.session.query(Category)
            .filter(Category.slug == slug, Category.deleted_at.is_(None))
            .first()
        )

    def get_root_categories(self, active_only: bool = True, include_counts: bool = False) -> List[Category]:
        """
        Obtener categorías raíz ordenadas.

        Args:
            active_only: Solo categorías activas
            include_counts: Incluir conteo de productos

        Returns:
            List[Category]: Lista de categorías raíz
        """
        query = (
            self.session.query(Category)
            .filter(Category.parent_id.is_(None), Category.deleted_at.is_(None))
        )

        if active_only:
            query = query.filter(Category.is_active == True)

        if include_counts:
            query = query.options(selectinload(Category.products))

        return query.order_by(Category.sort_order, Category.name).all()

    def get_category_tree(
        self,
        max_depth: Optional[int] = None,
        active_only: bool = True,
        include_product_counts: bool = False
    ) -> List[Dict]:
        """
        Obtener árbol completo de categorías optimizado.

        Args:
            max_depth: Profundidad máxima (None = ilimitada)
            active_only: Solo categorías activas
            include_product_counts: Incluir conteos recursivos

        Returns:
            List[Dict]: Árbol de categorías con children anidados
        """
        query = self.session.query(Category).filter(Category.deleted_at.is_(None))

        if active_only:
            query = query.filter(Category.is_active == True)

        if max_depth is not None:
            query = query.filter(Category.level <= max_depth)

        categories = query.order_by(Category.level, Category.sort_order).all()

        # Construir árbol eficientemente
        category_map = {}
        tree = []

        for cat in categories:
            cat_dict = cat.to_dict()
            cat_dict["children"] = []

            if include_product_counts:
                cat_dict["product_count_recursive"] = cat.get_product_count_recursive(self.session)

            category_map[cat.id] = cat_dict

            if cat.parent_id is None:
                tree.append(cat_dict)
            else:
                parent_dict = category_map.get(cat.parent_id)
                if parent_dict:
                    parent_dict["children"].append(cat_dict)

        return tree

    def get_category_path_breadcrumb(self, category_id: UUID) -> List[Dict]:
        """
        Obtener breadcrumb optimizado usando materialized path.

        Args:
            category_id: ID de la categoría

        Returns:
            List[Dict]: Breadcrumb desde root hasta categoría
        """
        category = self.get_category_by_id(category_id)
        if not category:
            return []

        return category.get_breadcrumb(self.session)

    def search_categories(
        self,
        query: str,
        active_only: bool = True,
        limit: int = 50
    ) -> List[Category]:
        """
        Buscar categorías por nombre y descripción.

        Args:
            query: Texto de búsqueda
            active_only: Solo categorías activas
            limit: Límite de resultados

        Returns:
            List[Category]: Categorías encontradas ordenadas por relevancia
        """
        search_query = self.session.query(Category).filter(Category.deleted_at.is_(None))

        if active_only:
            search_query = search_query.filter(Category.is_active == True)

        # Búsqueda por nombre y descripción
        search_term = f"%{query.lower()}%"
        search_query = search_query.filter(
            or_(
                Category.name.ilike(search_term),
                Category.description.ilike(search_term),
                Category.meta_keywords.ilike(search_term)
            )
        )

        return search_query.order_by(Category.name).limit(limit).all()

    # === PRODUCT-CATEGORY OPERATIONS ===

    def assign_product_to_category(
        self,
        product_id: UUID,
        category_id: UUID,
        is_primary: bool = False,
        sort_order: int = 0,
        assigned_by_id: Optional[UUID] = None
    ) -> ProductCategory:
        """
        Asignar producto a categoría.

        Args:
            product_id: ID del producto
            category_id: ID de la categoría
            is_primary: Si es categoría principal
            sort_order: Orden de la categoría
            assigned_by_id: ID del usuario que asigna

        Returns:
            ProductCategory: Asociación creada

        Raises:
            ValueError: Si la asociación ya existe o datos inválidos
        """
        # Verificar que producto y categoría existen
        product = self.session.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Producto con ID {product_id} no encontrado")

        category = self.get_category_by_id(category_id)
        if not category:
            raise ValueError(f"Categoría con ID {category_id} no encontrada")

        # Verificar que no existe la asociación
        existing = (
            self.session.query(ProductCategory)
            .filter(
                ProductCategory.product_id == product_id,
                ProductCategory.category_id == category_id,
                ProductCategory.deleted_at.is_(None)
            )
            .first()
        )

        if existing:
            raise ValueError("El producto ya está asignado a esta categoría")

        # Si es primary, desmarcar otras como primary
        if is_primary:
            self.session.query(ProductCategory).filter(
                ProductCategory.product_id == product_id,
                ProductCategory.is_primary == True,
                ProductCategory.deleted_at.is_(None)
            ).update({"is_primary": False})

        # Crear asociación
        association = ProductCategory(
            product_id=product_id,
            category_id=category_id,
            is_primary=is_primary,
            sort_order=sort_order,
            assigned_by_id=assigned_by_id
        )

        self.session.add(association)

        # Actualizar contador de productos en categoría
        category.product_count += 1

        self.session.flush()
        return association

    def remove_product_from_category(
        self,
        product_id: UUID,
        category_id: UUID
    ) -> bool:
        """
        Remover producto de categoría.

        Args:
            product_id: ID del producto
            category_id: ID de la categoría

        Returns:
            bool: True si se removió exitosamente
        """
        association = (
            self.session.query(ProductCategory)
            .filter(
                ProductCategory.product_id == product_id,
                ProductCategory.category_id == category_id,
                ProductCategory.deleted_at.is_(None)
            )
            .first()
        )

        if not association:
            return False

        # Soft delete
        from datetime import datetime
        association.deleted_at = datetime.utcnow()

        # Actualizar contador
        category = self.get_category_by_id(category_id)
        if category and category.product_count > 0:
            category.product_count -= 1

        self.session.flush()
        return True

    def set_product_primary_category(
        self,
        product_id: UUID,
        category_id: UUID,
        assigned_by_id: Optional[UUID] = None
    ) -> bool:
        """
        Establecer categoría principal de un producto.

        Args:
            product_id: ID del producto
            category_id: ID de la categoría
            assigned_by_id: ID del usuario que asigna

        Returns:
            bool: True si se estableció exitosamente
        """
        # Desmarcar categorías primary actuales
        self.session.query(ProductCategory).filter(
            ProductCategory.product_id == product_id,
            ProductCategory.is_primary == True,
            ProductCategory.deleted_at.is_(None)
        ).update({"is_primary": False})

        # Buscar asociación existente
        association = (
            self.session.query(ProductCategory)
            .filter(
                ProductCategory.product_id == product_id,
                ProductCategory.category_id == category_id,
                ProductCategory.deleted_at.is_(None)
            )
            .first()
        )

        if association:
            # Marcar como primary
            association.is_primary = True
            if assigned_by_id:
                association.assigned_by_id = assigned_by_id
        else:
            # Crear nueva asociación como primary
            self.assign_product_to_category(
                product_id, category_id, is_primary=True, assigned_by_id=assigned_by_id
            )

        self.session.flush()
        return True

    def get_products_by_category(
        self,
        category_id: UUID,
        include_subcategories: bool = False,
        active_only: bool = True,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> Tuple[List[Product], int]:
        """
        Obtener productos de una categoría con paginación.

        Args:
            category_id: ID de la categoría
            include_subcategories: Incluir productos de subcategorías
            active_only: Solo productos activos
            limit: Límite de resultados
            offset: Offset para paginación

        Returns:
            Tuple[List[Product], int]: (productos, total_count)
        """
        if include_subcategories:
            # Obtener categoría y descendientes
            category = self.get_category_by_id(category_id)
            if not category:
                return [], 0

            descendants = category.get_descendants(self.session)
            category_ids = [category.id] + [cat.id for cat in descendants]
        else:
            category_ids = [category_id]

        # Query base
        query = (
            self.session.query(Product)
            .join(ProductCategory)
            .filter(
                ProductCategory.category_id.in_(category_ids),
                ProductCategory.deleted_at.is_(None),
                Product.deleted_at.is_(None)
            )
        )

        if active_only:
            from app.models.product import ProductStatus
            query = query.filter(Product.status != ProductStatus.VENDIDO)

        # Contar total
        total_count = query.count()

        # Aplicar paginación
        query = query.order_by(Product.created_at.desc())
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        products = query.all()
        return products, total_count

    # === BULK OPERATIONS ===

    def bulk_assign_products_to_category(
        self,
        product_ids: List[UUID],
        category_id: UUID,
        assigned_by_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Asignar múltiples productos a una categoría.

        Args:
            product_ids: Lista de IDs de productos
            category_id: ID de la categoría
            assigned_by_id: ID del usuario que asigna

        Returns:
            Dict: Resultado con estadísticas de la operación
        """
        category = self.get_category_by_id(category_id)
        if not category:
            raise ValueError(f"Categoría con ID {category_id} no encontrada")

        results = {
            "assigned": 0,
            "skipped": 0,
            "errors": [],
            "product_ids_assigned": []
        }

        for product_id in product_ids:
            try:
                # Verificar que producto existe
                product = self.session.query(Product).filter(Product.id == product_id).first()
                if not product:
                    results["errors"].append(f"Producto {product_id} no encontrado")
                    continue

                # Verificar que no está ya asignado
                existing = (
                    self.session.query(ProductCategory)
                    .filter(
                        ProductCategory.product_id == product_id,
                        ProductCategory.category_id == category_id,
                        ProductCategory.deleted_at.is_(None)
                    )
                    .first()
                )

                if existing:
                    results["skipped"] += 1
                    continue

                # Crear asociación
                association = ProductCategory(
                    product_id=product_id,
                    category_id=category_id,
                    is_primary=False,
                    sort_order=0,
                    assigned_by_id=assigned_by_id
                )

                self.session.add(association)
                results["assigned"] += 1
                results["product_ids_assigned"].append(product_id)

            except Exception as e:
                results["errors"].append(f"Error asignando producto {product_id}: {str(e)}")

        # Actualizar contador de categoría
        if results["assigned"] > 0:
            category.product_count += results["assigned"]

        self.session.flush()
        return results

    def move_category_products(
        self,
        source_category_id: UUID,
        target_category_id: UUID,
        assigned_by_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Mover todos los productos de una categoría a otra.

        Args:
            source_category_id: ID de categoría origen
            target_category_id: ID de categoría destino
            assigned_by_id: ID del usuario que realiza la operación

        Returns:
            Dict: Resultado de la operación
        """
        source_category = self.get_category_by_id(source_category_id)
        target_category = self.get_category_by_id(target_category_id)

        if not source_category:
            raise ValueError(f"Categoría origen {source_category_id} no encontrada")
        if not target_category:
            raise ValueError(f"Categoría destino {target_category_id} no encontrada")

        # Obtener productos de categoría origen
        products, _ = self.get_products_by_category(source_category_id, include_subcategories=False)
        product_ids = [p.id for p in products]

        # Remover de categoría origen
        moved_count = 0
        for product_id in product_ids:
            if self.remove_product_from_category(product_id, source_category_id):
                moved_count += 1

        # Asignar a categoría destino (bulk)
        if product_ids:
            assign_results = self.bulk_assign_products_to_category(
                product_ids, target_category_id, assigned_by_id
            )
        else:
            assign_results = {"assigned": 0, "skipped": 0, "errors": []}

        return {
            "moved_count": moved_count,
            "assign_results": assign_results,
            "source_category": source_category.name,
            "target_category": target_category.name
        }

    # === ANALYTICS AND REPORTING ===

    def get_category_analytics(self, category_id: UUID) -> Dict[str, Any]:
        """
        Obtener analytics detallados de una categoría.

        Args:
            category_id: ID de la categoría

        Returns:
            Dict: Analytics completos de la categoría
        """
        category = self.get_category_by_id(category_id)
        if not category:
            return {}

        # Conteos básicos
        direct_products, _ = self.get_products_by_category(category_id, include_subcategories=False)
        recursive_products, _ = self.get_products_by_category(category_id, include_subcategories=True)

        # Subcategorías
        children = category.children
        descendants = category.get_descendants(self.session)

        # Productos por estado
        product_status_counts = (
            self.session.query(Product.status, func.count(Product.id))
            .join(ProductCategory)
            .filter(
                ProductCategory.category_id == category_id,
                ProductCategory.deleted_at.is_(None),
                Product.deleted_at.is_(None)
            )
            .group_by(Product.status)
            .all()
        )

        # Top vendors en esta categoría
        top_vendors = (
            self.session.query(User.username, func.count(Product.id).label('product_count'))
            .join(Product, User.id == Product.vendedor_id)
            .join(ProductCategory)
            .filter(
                ProductCategory.category_id == category_id,
                ProductCategory.deleted_at.is_(None),
                Product.deleted_at.is_(None)
            )
            .group_by(User.id, User.username)
            .order_by(desc('product_count'))
            .limit(10)
            .all()
        )

        return {
            "category": category.to_dict(),
            "direct_products_count": len(direct_products),
            "recursive_products_count": len(recursive_products),
            "children_count": len(children),
            "descendants_count": len(descendants),
            "product_status_distribution": dict(product_status_counts),
            "top_vendors": [{"username": vendor, "count": count} for vendor, count in top_vendors],
            "depth_level": category.level,
            "path": category.path
        }

    # === UTILITY METHODS ===

    def _generate_slug(self, name: str) -> str:
        """
        Generar slug URL-friendly desde nombre.

        Args:
            name: Nombre de la categoría

        Returns:
            str: Slug generado
        """
        # Convertir a lowercase y reemplazar caracteres especiales
        slug = re.sub(r'[^a-z0-9\s\-_]', '', name.lower())
        # Reemplazar espacios y múltiples guiones
        slug = re.sub(r'[\s\-_]+', '-', slug)
        # Remover guiones al inicio y final
        slug = slug.strip('-')

        # Si el slug ya existe, agregar sufijo numérico
        base_slug = slug
        counter = 1
        while self.get_category_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def validate_category_hierarchy(self, category_id: UUID, parent_id: Optional[UUID]) -> bool:
        """
        Validar que una asignación de parent no cree loops.

        Args:
            category_id: ID de la categoría
            parent_id: ID del parent propuesto

        Returns:
            bool: True si la jerarquía es válida
        """
        if parent_id is None:
            return True

        category = self.get_category_by_id(category_id)
        parent = self.get_category_by_id(parent_id)

        if not category or not parent:
            return False

        return category.can_have_parent(parent)

    def rebuild_materialized_paths(self) -> Dict[str, Any]:
        """
        Reconstruir todos los materialized paths (útil para maintenance).

        Returns:
            Dict: Resultado de la operación
        """
        updated_count = 0
        errors = []

        # Obtener todas las categorías ordenadas por level
        categories = (
            self.session.query(Category)
            .filter(Category.deleted_at.is_(None))
            .order_by(Category.level)
            .all()
        )

        for category in categories:
            try:
                old_path = category.path
                category.update_path()

                if old_path != category.path:
                    updated_count += 1

            except Exception as e:
                errors.append(f"Error actualizando categoría {category.id}: {str(e)}")

        self.session.flush()

        return {
            "categories_processed": len(categories),
            "paths_updated": updated_count,
            "errors": errors
        }