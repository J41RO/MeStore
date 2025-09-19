"""Add full-text search indexes for products

Revision ID: add_fulltext_search_indexes
Revises: ghi789_update_usertype_enum_to_english
Create Date: 2025-09-17 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_fulltext_search_indexes'
down_revision = 'ghi789'
branch_labels = None
depends_on = None


def upgrade():
    """
    Agregar índices GIN para búsqueda full-text optimizada en PostgreSQL.

    Estos índices mejoran significativamente el performance de búsquedas de texto
    en productos usando PostgreSQL full-text search capabilities.
    """

    # Verificar que estamos en PostgreSQL antes de crear índices específicos
    connection = op.get_bind()
    if connection.dialect.name == 'postgresql':

        # 1. Habilitar extensión pg_trgm para búsqueda por similitud
        op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')

        # 2. Habilitar extensión unaccent para búsqueda sin acentos
        op.execute('CREATE EXTENSION IF NOT EXISTS unaccent;')

        # 3. Índice GIN para búsqueda full-text en nombre del producto (español)
        op.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_product_name_fulltext_gin
            ON products USING gin(to_tsvector('spanish', name));
        """)

        # 4. Índice GIN para búsqueda full-text en descripción del producto (español)
        op.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_product_description_fulltext_gin
            ON products USING gin(to_tsvector('spanish', COALESCE(description, '')));
        """)

        # 5. Índice GIN para búsqueda por similitud trigram en nombre
        op.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_product_name_trgm_gin
            ON products USING gin(name gin_trgm_ops);
        """)

        # 6. Índice GIN para búsqueda por similitud trigram en descripción
        op.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_product_description_trgm_gin
            ON products USING gin(description gin_trgm_ops);
        """)

        # 7. Índice GIN combinado para búsqueda full-text en nombre y descripción
        op.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_product_combined_fulltext_gin
            ON products USING gin(
                (to_tsvector('spanish', name) || to_tsvector('spanish', COALESCE(description, '')))
            );
        """)

        # 8. Índice para búsqueda en tags JSON
        op.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_product_tags_gin
            ON products USING gin(tags);
        """)

        # 9. Índice compuesto para búsquedas con filtros comunes
        op.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_product_search_filters
            ON products (status, vendedor_id, categoria)
            WHERE deleted_at IS NULL;
        """)

        # 10. Índice para búsquedas por precio con productos disponibles
        op.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_product_price_available
            ON products (precio_venta, created_at)
            WHERE status = 'DISPONIBLE' AND deleted_at IS NULL;
        """)

        print("✅ Índices GIN para búsqueda full-text creados exitosamente en PostgreSQL")

    else:
        print("⚠️  Los índices GIN son específicos de PostgreSQL. Saltando creación para otras bases de datos.")


def downgrade():
    """
    Remover índices GIN de búsqueda full-text.
    """

    connection = op.get_bind()
    if connection.dialect.name == 'postgresql':

        # Remover índices en orden inverso
        indices_to_drop = [
            'ix_product_price_available',
            'ix_product_search_filters',
            'ix_product_tags_gin',
            'ix_product_combined_fulltext_gin',
            'ix_product_description_trgm_gin',
            'ix_product_name_trgm_gin',
            'ix_product_description_fulltext_gin',
            'ix_product_name_fulltext_gin'
        ]

        for index_name in indices_to_drop:
            op.execute(f'DROP INDEX CONCURRENTLY IF EXISTS {index_name};')

        # Nota: No removemos las extensiones pg_trgm y unaccent ya que podrían
        # estar siendo usadas por otras partes de la aplicación

        print("✅ Índices GIN para búsqueda full-text removidos exitosamente")

    else:
        print("⚠️  Saltando removal de índices GIN en bases de datos no-PostgreSQL")