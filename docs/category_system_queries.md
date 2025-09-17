# Category System - Query Patterns for Frontend

## Overview

Este documento describe los patrones de consulta comunes para el sistema de categorías jerárquicas de MeStore, optimizados para performance con miles de productos y cientos de categorías.

## Arquitectura del Sistema

### Modelos Principales

1. **Category**: Modelo principal con estructura jerárquica
   - Self-referencing con `parent_id`
   - Materialized path para queries optimizadas
   - Level tracking para control de profundidad
   - Soft delete support

2. **ProductCategory**: Tabla many-to-many
   - Permite múltiples categorías por producto
   - Support para categoría principal vs secundarias
   - Tracking de asignación

3. **Product**: Modelo actualizado con relationships
   - Backwards compatibility con campo `categoria` string
   - Nuevas relaciones con Category system

### Índices de Performance

```sql
-- Hierarchy navigation
CREATE INDEX ix_category_parent_level ON categories(parent_id, level);
CREATE INDEX ix_category_path_level ON categories(path, level);
CREATE INDEX ix_category_parent_active_sort ON categories(parent_id, is_active, sort_order);

-- Product-category lookups
CREATE INDEX ix_product_category_product_primary ON product_categories(product_id, is_primary);
CREATE INDEX ix_product_category_category_primary ON product_categories(category_id, is_primary);
```

## Common Query Patterns

### 1. Category Navigation Queries

#### Obtener Categorías Raíz (Menu Principal)

```python
# Service method
def get_main_menu_categories():
    """Obtener categorías raíz para menu principal"""
    return category_service.get_root_categories(
        active_only=True,
        include_counts=True
    )

# Direct SQLAlchemy query
root_categories = (
    session.query(Category)
    .filter(
        Category.parent_id.is_(None),
        Category.is_active == True,
        Category.deleted_at.is_(None)
    )
    .order_by(Category.sort_order, Category.name)
    .all()
)
```

#### Obtener Árbol Completo de Categorías

```python
# Service method (recomendado)
def get_category_tree_for_sidebar():
    """Árbol completo para sidebar navigation"""
    return category_service.get_category_tree(
        max_depth=3,
        active_only=True,
        include_product_counts=True
    )

# Response format:
[
    {
        "id": "uuid",
        "name": "Electrónicos",
        "slug": "electronicos",
        "level": 0,
        "product_count": 150,
        "children": [
            {
                "id": "uuid",
                "name": "Teléfonos",
                "slug": "telefonos",
                "level": 1,
                "product_count": 45,
                "children": [...]
            }
        ]
    }
]
```

#### Breadcrumb Navigation

```python
# Service method
def get_category_breadcrumb(category_id: UUID):
    """Breadcrumb optimizado con materialized path"""
    return category_service.get_category_path_breadcrumb(category_id)

# Response format:
[
    {"id": "uuid", "name": "Inicio", "slug": "", "url": "/", "level": -1},
    {"id": "uuid", "name": "Electrónicos", "slug": "electronicos", "url": "/categories/electronicos", "level": 0},
    {"id": "uuid", "name": "Teléfonos", "slug": "telefonos", "url": "/categories/telefonos", "level": 1},
    {"id": "uuid", "name": "Smartphones", "slug": "smartphones", "url": "/categories/smartphones", "level": 2}
]
```

### 2. Product Listing by Category

#### Products by Category (con Paginación)

```python
# Service method
def get_category_products_paginated(category_slug: str, page: int = 1, per_page: int = 20):
    """Productos de categoría con paginación"""
    category = category_service.get_category_by_slug(category_slug)
    if not category:
        return [], 0

    offset = (page - 1) * per_page
    products, total = category_service.get_products_by_category(
        category.id,
        include_subcategories=True,
        active_only=True,
        limit=per_page,
        offset=offset
    )

    return {
        "products": [p.to_dict() for p in products],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
        "category": category.to_dict()
    }
```

#### Products with Category Information

```python
# Direct query con category info
products_with_categories = (
    session.query(Product)
    .options(
        selectinload(Product.category_associations)
        .selectinload(ProductCategory.category)
    )
    .filter(Product.deleted_at.is_(None))
    .limit(20)
    .all()
)

# Product.to_dict() ya incluye category information:
{
    "id": "uuid",
    "name": "iPhone 15",
    "primary_category": {
        "id": "uuid",
        "name": "Smartphones",
        "slug": "smartphones",
        "path": "/electronicos/telefonos/smartphones/",
        "level": 2
    },
    "categories_count": 2,
    "secondary_categories": [
        {
            "id": "uuid",
            "name": "Apple Products",
            "slug": "apple-products",
            "path": "/electronicos/marcas/apple/",
            "level": 2
        }
    ]
}
```

### 3. Category Management Queries

#### Search Categories

```python
# Service method
def search_categories_autocomplete(query: str):
    """Búsqueda de categorías para autocomplete"""
    return category_service.search_categories(
        query=query,
        active_only=True,
        limit=10
    )

# Direct query
categories = (
    session.query(Category)
    .filter(
        Category.name.ilike(f"%{query}%"),
        Category.is_active == True,
        Category.deleted_at.is_(None)
    )
    .order_by(Category.name)
    .limit(10)
    .all()
)
```

#### Category Analytics

```python
# Service method
def get_category_dashboard_data(category_id: UUID):
    """Analytics completos para dashboard"""
    return category_service.get_category_analytics(category_id)

# Response includes:
{
    "category": {...},
    "direct_products_count": 45,
    "recursive_products_count": 150,
    "children_count": 3,
    "descendants_count": 12,
    "product_status_distribution": {
        "DISPONIBLE": 120,
        "TRANSITO": 25,
        "VENDIDO": 5
    },
    "top_vendors": [
        {"username": "vendor1", "count": 30},
        {"username": "vendor2", "count": 25}
    ]
}
```

### 4. Product-Category Assignment

#### Assign Product to Categories

```python
# Service methods
def assign_product_categories(product_id: UUID, category_assignments: List[Dict]):
    """Asignar múltiples categorías a producto"""
    for assignment in category_assignments:
        category_service.assign_product_to_category(
            product_id=product_id,
            category_id=assignment["category_id"],
            is_primary=assignment.get("is_primary", False),
            assigned_by_id=current_user.id
        )

# Bulk assignment
def bulk_categorize_products(product_ids: List[UUID], category_id: UUID):
    """Asignación masiva de productos a categoría"""
    return category_service.bulk_assign_products_to_category(
        product_ids=product_ids,
        category_id=category_id,
        assigned_by_id=current_user.id
    )
```

### 5. Performance Optimization Patterns

#### Efficient Tree Loading

```python
# Load categories with minimal queries
def load_category_tree_optimized():
    """Carga optimizada del árbol completo"""
    # Single query para todas las categorías
    categories = (
        session.query(Category)
        .filter(
            Category.deleted_at.is_(None),
            Category.is_active == True
        )
        .order_by(Category.level, Category.sort_order)
        .all()
    )

    # Build tree in memory (O(n) complexity)
    category_map = {cat.id: cat.to_dict() for cat in categories}
    tree = []

    for cat in categories:
        cat_dict = category_map[cat.id]
        cat_dict["children"] = []

        if cat.parent_id is None:
            tree.append(cat_dict)
        else:
            parent = category_map.get(cat.parent_id)
            if parent:
                parent["children"].append(cat_dict)

    return tree
```

#### Cached Category Queries

```python
# Redis caching pattern
import redis
import json

redis_client = redis.Redis()

def get_cached_category_tree():
    """Category tree con Redis cache"""
    cache_key = "category_tree:active"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    # Load from database
    tree = category_service.get_category_tree(active_only=True)

    # Cache for 1 hour
    redis_client.setex(cache_key, 3600, json.dumps(tree, default=str))

    return tree

def invalidate_category_cache():
    """Invalidar cache cuando se actualicen categorías"""
    redis_client.delete("category_tree:active")
```

### 6. Frontend Integration Examples

#### React Component Data Loading

```javascript
// Category tree for navigation
const useCategoryTree = () => {
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/v1/categories/tree?max_depth=3&include_counts=true')
            .then(res => res.json())
            .then(data => {
                setCategories(data);
                setLoading(false);
            });
    }, []);

    return { categories, loading };
};

// Product listing with category filter
const useProductsByCategory = (categorySlug, page = 1) => {
    const [data, setData] = useState(null);

    useEffect(() => {
        fetch(`/api/v1/categories/${categorySlug}/products?page=${page}&per_page=20`)
            .then(res => res.json())
            .then(setData);
    }, [categorySlug, page]);

    return data;
};
```

#### API Endpoints Structure

```python
# FastAPI endpoints
@router.get("/categories/tree")
async def get_category_tree(
    max_depth: Optional[int] = None,
    include_counts: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get complete category tree"""
    service = CategoryService(db)
    return service.get_category_tree(
        max_depth=max_depth,
        include_product_counts=include_counts
    )

@router.get("/categories/{slug}/products")
async def get_category_products(
    slug: str,
    page: int = 1,
    per_page: int = 20,
    include_subcategories: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Get products by category with pagination"""
    service = CategoryService(db)
    category = service.get_category_by_slug(slug)

    if not category:
        raise HTTPException(404, "Category not found")

    offset = (page - 1) * per_page
    products, total = service.get_products_by_category(
        category.id,
        include_subcategories=include_subcategories,
        limit=per_page,
        offset=offset
    )

    return {
        "products": [p.to_dict() for p in products],
        "total": total,
        "page": page,
        "per_page": per_page,
        "category": category.to_dict()
    }
```

## Performance Considerations

### Database Optimization

1. **Materialized Path**: Use path field for ancestor/descendant queries
2. **Level Field**: Quick depth filtering without recursive queries
3. **Composite Indexes**: Optimized for common query patterns
4. **Eager Loading**: Use selectinload() for related data

### Caching Strategy

1. **Category Tree**: Cache complete tree (changes infrequently)
2. **Product Counts**: Cache category product counts with TTL
3. **Breadcrumbs**: Cache category paths
4. **Search Results**: Cache category search results

### Query Optimization

1. **Avoid N+1**: Use selectinload for relationships
2. **Pagination**: Always use LIMIT/OFFSET for large result sets
3. **Filtering**: Filter at database level, not in memory
4. **Aggregations**: Use database functions for counts

### Scaling Considerations

- **Read Replicas**: Route category reads to replicas
- **CDN**: Cache category tree in CDN for global access
- **Async Processing**: Update product counts async
- **Database Partitioning**: Consider partitioning by level for very large hierarchies

## Migration from Legacy System

### Migrating from String Categories

```python
# Migration script
def migrate_legacy_categories():
    """Migrate from Product.categoria string to new system"""
    products = session.query(Product).filter(
        Product.categoria.isnot(None),
        Product.categoria != ''
    ).all()

    for product in products:
        # Try to find existing category
        category = session.query(Category).filter(
            Category.name.ilike(f"%{product.categoria}%")
        ).first()

        if not category:
            # Create new category
            slug = re.sub(r'[^a-z0-9\-_]', '-', product.categoria.lower())
            category = Category(
                name=product.categoria,
                slug=slug,
                path=f"/{slug}/",
                level=0
            )
            session.add(category)
            session.flush()

        # Assign as primary category
        product.set_primary_category(category, assigned_by_id=migration_user_id)

    session.commit()
```

## Best Practices

1. **Always use CategoryService** for business operations
2. **Cache frequently accessed data** (category tree, counts)
3. **Use materialized path** for hierarchy queries
4. **Validate hierarchy integrity** before parent assignments
5. **Soft delete** categories to preserve data integrity
6. **Monitor query performance** with database profiling
7. **Update product counts** efficiently with bulk operations
8. **Use transactions** for multi-step category operations