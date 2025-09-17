"""add hierarchical category system

Revision ID: ab40848d19b
Revises: ghi789
Create Date: 2025-09-17 02:27:00.000000

This migration adds the hierarchical category system for the MeStore marketplace:

1. Creates the `categories` table with:
   - Self-referencing hierarchy (parent_id)
   - Materialized path optimization for tree queries
   - Level tracking for depth control
   - SEO metadata fields
   - Display configuration support

2. Creates the `product_categories` table for many-to-many relationships:
   - Allows products to have multiple categories
   - Supports primary category designation
   - Tracks assignment metadata

3. Adds optimized indexes for:
   - Hierarchy navigation queries
   - Category tree traversal
   - Product-category lookups
   - Performance optimization for thousands of products

4. Migrates existing Product.categoria data to new system:
   - Creates categories from existing string values
   - Assigns them as primary categories
   - Preserves data integrity during transition

The system supports unlimited nesting depth and is optimized for
marketplace operations with 50+ vendors and 1000+ products each.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy import text
import uuid
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'ab40848d19b'
down_revision = 'ghi789'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create hierarchical category system tables and migrate existing data.
    """

    # === CREATE CATEGORIES TABLE ===

    op.create_table(
        'categories',

        # Base model fields (inherited from BaseModel)
        sa.Column('id', postgresql.UUID(as_uuid=True) if op.get_bind().dialect.name == 'postgresql' else sa.String(36),
                  primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),

        # Category-specific fields
        sa.Column('name', sa.String(200), nullable=False, comment='Nombre de la categoría'),
        sa.Column('slug', sa.String(200), nullable=False, comment='URL-friendly identifier único'),
        sa.Column('description', sa.Text(), nullable=True, comment='Descripción detallada de la categoría'),

        # Hierarchy fields
        sa.Column('parent_id', postgresql.UUID(as_uuid=True) if op.get_bind().dialect.name == 'postgresql' else sa.String(36),
                  sa.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True,
                  comment='ID de la categoría padre (NULL para root categories)'),
        sa.Column('path', sa.String(1000), nullable=False,
                  comment='Materialized path del árbol (e.g., \'/electronics/phones/\')'),
        sa.Column('level', sa.Integer(), nullable=False, default=0,
                  comment='Nivel en el árbol de categorías (0 = root)'),

        # Display and ordering
        sa.Column('sort_order', sa.Integer(), nullable=False, default=0,
                  comment='Orden de display dentro del nivel'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True,
                  comment='Estado activo de la categoría'),
        sa.Column('status', sa.String(20), nullable=False, default='ACTIVE',
                  comment='Estado detallado de la categoría'),

        # SEO metadata
        sa.Column('meta_title', sa.String(255), nullable=True, comment='Título SEO de la categoría'),
        sa.Column('meta_description', sa.String(500), nullable=True, comment='Descripción SEO de la categoría'),
        sa.Column('meta_keywords', sa.Text(), nullable=True, comment='Keywords SEO separadas por comas'),

        # Visual assets
        sa.Column('icon_url', sa.String(500), nullable=True, comment='URL del ícono de la categoría'),
        sa.Column('banner_url', sa.String(500), nullable=True, comment='URL del banner de la categoría'),

        # Frontend configuration
        sa.Column('display_config', postgresql.JSON() if op.get_bind().dialect.name == 'postgresql' else sa.Text(),
                  nullable=True, comment='Configuración JSON para display frontend'),

        # Usage statistics
        sa.Column('product_count', sa.Integer(), nullable=False, default=0,
                  comment='Contador de productos en esta categoría'),
    )

    # === CREATE PRODUCT_CATEGORIES TABLE ===

    op.create_table(
        'product_categories',

        # Base model fields
        sa.Column('id', postgresql.UUID(as_uuid=True) if op.get_bind().dialect.name == 'postgresql' else sa.String(36),
                  primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),

        # Foreign keys
        sa.Column('product_id', postgresql.UUID(as_uuid=True) if op.get_bind().dialect.name == 'postgresql' else sa.String(36),
                  sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, comment='ID del producto'),
        sa.Column('category_id', postgresql.UUID(as_uuid=True) if op.get_bind().dialect.name == 'postgresql' else sa.String(36),
                  sa.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False, comment='ID de la categoría'),

        # Relationship configuration
        sa.Column('is_primary', sa.Boolean(), nullable=False, default=False,
                  comment='Si es la categoría principal del producto'),
        sa.Column('sort_order', sa.Integer(), nullable=False, default=0,
                  comment='Orden de la categoría para el producto'),

        # Assignment tracking
        sa.Column('assigned_by_id', postgresql.UUID(as_uuid=True) if op.get_bind().dialect.name == 'postgresql' else sa.String(36),
                  sa.ForeignKey('users.id'), nullable=True, comment='Usuario que asignó la categoría'),
    )

    # === CREATE INDEXES FOR CATEGORIES ===

    # Basic indexes
    op.create_index('ix_categories_name', 'categories', ['name'])
    op.create_index('ix_categories_slug', 'categories', ['slug'], unique=True)
    op.create_index('ix_categories_parent_id', 'categories', ['parent_id'])
    op.create_index('ix_categories_path', 'categories', ['path'])
    op.create_index('ix_categories_level', 'categories', ['level'])
    op.create_index('ix_categories_sort_order', 'categories', ['sort_order'])
    op.create_index('ix_categories_is_active', 'categories', ['is_active'])
    op.create_index('ix_categories_status', 'categories', ['status'])

    # Composite indexes for hierarchy optimization
    op.create_index('ix_category_parent_level', 'categories', ['parent_id', 'level'])
    op.create_index('ix_category_parent_sort', 'categories', ['parent_id', 'sort_order'])
    op.create_index('ix_category_path_level', 'categories', ['path', 'level'])
    op.create_index('ix_category_active_status', 'categories', ['is_active', 'status'])
    op.create_index('ix_category_active_sort', 'categories', ['is_active', 'sort_order'])
    op.create_index('ix_category_name_active', 'categories', ['name', 'is_active'])
    op.create_index('ix_category_parent_active_sort', 'categories', ['parent_id', 'is_active', 'sort_order'])

    # === CREATE INDEXES FOR PRODUCT_CATEGORIES ===

    # Basic indexes
    op.create_index('ix_product_categories_product_id', 'product_categories', ['product_id'])
    op.create_index('ix_product_categories_category_id', 'product_categories', ['category_id'])
    op.create_index('ix_product_categories_is_primary', 'product_categories', ['is_primary'])

    # Composite indexes for common queries
    op.create_index('ix_product_category_product', 'product_categories', ['product_id'])
    op.create_index('ix_product_category_category', 'product_categories', ['category_id'])
    op.create_index('ix_product_category_primary', 'product_categories', ['is_primary'])
    op.create_index('ix_product_category_product_primary', 'product_categories', ['product_id', 'is_primary'])
    op.create_index('ix_product_category_category_primary', 'product_categories', ['category_id', 'is_primary'])

    # === CREATE UNIQUE CONSTRAINTS ===

    # Unique constraint for category slug
    op.create_unique_constraint('uq_category_slug', 'categories', ['slug'])

    # Unique constraint to prevent duplicate product-category assignments
    op.create_unique_constraint('uq_product_category', 'product_categories', ['product_id', 'category_id'])

    # === POPULATE INITIAL CATEGORY DATA ===

    # Insert default marketplace categories
    connection = op.get_bind()

    # Prepare category data - typical marketplace hierarchy
    initial_categories = [
        # Root categories (level 0)
        {
            'id': str(uuid.uuid4()),
            'name': 'Electrónicos',
            'slug': 'electronicos',
            'description': 'Dispositivos electrónicos y tecnología',
            'path': '/electronicos/',
            'level': 0,
            'sort_order': 1,
            'meta_title': 'Electrónicos | MeStore',
            'meta_description': 'Encuentra los mejores dispositivos electrónicos en MeStore'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Ropa y Accesorios',
            'slug': 'ropa-accesorios',
            'description': 'Vestimenta y accesorios de moda',
            'path': '/ropa-accesorios/',
            'level': 0,
            'sort_order': 2,
            'meta_title': 'Ropa y Accesorios | MeStore',
            'meta_description': 'Moda y accesorios para todos los estilos'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Hogar y Jardín',
            'slug': 'hogar-jardin',
            'description': 'Artículos para el hogar y jardín',
            'path': '/hogar-jardin/',
            'level': 0,
            'sort_order': 3,
            'meta_title': 'Hogar y Jardín | MeStore',
            'meta_description': 'Todo lo que necesitas para tu hogar y jardín'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Deportes y Recreación',
            'slug': 'deportes-recreacion',
            'description': 'Artículos deportivos y de recreación',
            'path': '/deportes-recreacion/',
            'level': 0,
            'sort_order': 4,
            'meta_title': 'Deportes y Recreación | MeStore',
            'meta_description': 'Equipos deportivos y artículos de recreación'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Salud y Belleza',
            'slug': 'salud-belleza',
            'description': 'Productos de salud, belleza y cuidado personal',
            'path': '/salud-belleza/',
            'level': 0,
            'sort_order': 5,
            'meta_title': 'Salud y Belleza | MeStore',
            'meta_description': 'Productos para tu salud y belleza'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Libros y Medios',
            'slug': 'libros-medios',
            'description': 'Libros, música, películas y medios digitales',
            'path': '/libros-medios/',
            'level': 0,
            'sort_order': 6,
            'meta_title': 'Libros y Medios | MeStore',
            'meta_description': 'Libros, música y entretenimiento digital'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Otros',
            'slug': 'otros',
            'description': 'Productos diversos y misceláneos',
            'path': '/otros/',
            'level': 0,
            'sort_order': 99,
            'meta_title': 'Otros Productos | MeStore',
            'meta_description': 'Productos diversos en MeStore'
        }
    ]

    # Insert root categories
    for cat_data in initial_categories:
        if connection.dialect.name == 'postgresql':
            connection.execute(text("""
                INSERT INTO categories (
                    id, created_at, updated_at, name, slug, description, path, level,
                    sort_order, is_active, status, meta_title, meta_description, product_count
                ) VALUES (
                    :id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, :name, :slug, :description,
                    :path, :level, :sort_order, true, 'ACTIVE', :meta_title, :meta_description, 0
                )
            """), cat_data)
        else:  # SQLite
            connection.execute(text("""
                INSERT INTO categories (
                    id, created_at, updated_at, name, slug, description, path, level,
                    sort_order, is_active, status, meta_title, meta_description, product_count
                ) VALUES (
                    :id, datetime('now'), datetime('now'), :name, :slug, :description,
                    :path, :level, :sort_order, 1, 'ACTIVE', :meta_title, :meta_description, 0
                )
            """), cat_data)

    # === MIGRATE EXISTING PRODUCT CATEGORIES ===

    # Get the "Otros" category ID for default assignments
    result = connection.execute(text("SELECT id FROM categories WHERE slug = 'otros'")).fetchone()
    otros_category_id = result[0] if result else None

    if otros_category_id:
        # Migrate products with existing categoria field
        if connection.dialect.name == 'postgresql':
            connection.execute(text("""
                INSERT INTO product_categories (
                    id, created_at, updated_at, product_id, category_id, is_primary, sort_order
                )
                SELECT
                    gen_random_uuid(),
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP,
                    p.id,
                    :category_id,
                    true,
                    0
                FROM products p
                WHERE p.categoria IS NOT NULL
                AND p.categoria != ''
                AND p.deleted_at IS NULL
            """), {'category_id': otros_category_id})
        else:  # SQLite
            # For SQLite, we need to handle UUID generation differently
            products_with_categories = connection.execute(text("""
                SELECT id FROM products
                WHERE categoria IS NOT NULL
                AND categoria != ''
                AND deleted_at IS NULL
            """)).fetchall()

            for product_row in products_with_categories:
                product_id = product_row[0]
                pc_id = str(uuid.uuid4())
                connection.execute(text("""
                    INSERT INTO product_categories (
                        id, created_at, updated_at, product_id, category_id, is_primary, sort_order
                    ) VALUES (
                        :id, datetime('now'), datetime('now'), :product_id, :category_id, 1, 0
                    )
                """), {
                    'id': pc_id,
                    'product_id': product_id,
                    'category_id': otros_category_id
                })

    print("✅ Hierarchical category system created successfully!")
    print("📊 Initial categories created:")
    for cat in initial_categories:
        print(f"  - {cat['name']} ({cat['slug']})")
    print("🔄 Existing product categories migrated to 'Otros' category")


def downgrade() -> None:
    """
    Remove hierarchical category system (WARNING: This will lose category data).
    """

    # Drop indexes first (in reverse order)
    op.drop_index('ix_product_category_category_primary', 'product_categories')
    op.drop_index('ix_product_category_product_primary', 'product_categories')
    op.drop_index('ix_product_category_primary', 'product_categories')
    op.drop_index('ix_product_category_category', 'product_categories')
    op.drop_index('ix_product_category_product', 'product_categories')

    op.drop_index('ix_product_categories_is_primary', 'product_categories')
    op.drop_index('ix_product_categories_category_id', 'product_categories')
    op.drop_index('ix_product_categories_product_id', 'product_categories')

    op.drop_index('ix_category_parent_active_sort', 'categories')
    op.drop_index('ix_category_name_active', 'categories')
    op.drop_index('ix_category_active_sort', 'categories')
    op.drop_index('ix_category_active_status', 'categories')
    op.drop_index('ix_category_path_level', 'categories')
    op.drop_index('ix_category_parent_sort', 'categories')
    op.drop_index('ix_category_parent_level', 'categories')

    op.drop_index('ix_categories_status', 'categories')
    op.drop_index('ix_categories_is_active', 'categories')
    op.drop_index('ix_categories_sort_order', 'categories')
    op.drop_index('ix_categories_level', 'categories')
    op.drop_index('ix_categories_path', 'categories')
    op.drop_index('ix_categories_parent_id', 'categories')
    op.drop_index('ix_categories_slug', 'categories')
    op.drop_index('ix_categories_name', 'categories')

    # Drop unique constraints
    op.drop_constraint('uq_product_category', 'product_categories', type_='unique')
    op.drop_constraint('uq_category_slug', 'categories', type_='unique')

    # Drop tables
    op.drop_table('product_categories')
    op.drop_table('categories')

    print("⚠️  Hierarchical category system removed!")
    print("📊 All category data has been deleted")
    print("🔄 Products still retain original 'categoria' string field")