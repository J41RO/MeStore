"""add quality fields to inventory

Revision ID: 720d7c9fb58f
Revises: 71fc98eda510
Create Date: 2025-07-28 18:32:22.728945

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '720d7c9fb58f'
down_revision = '71fc98eda510'
branch_labels = None
depends_on = None


def upgrade():
    # Crear enum CondicionProducto en PostgreSQL
    condicion_producto_enum = postgresql.ENUM(
        'NUEVO', 'USADO_EXCELENTE', 'USADO_BUENO', 'USADO_REGULAR', 'DAÑADO',
        name='condicionproducto'
    )
    condicion_producto_enum.create(op.get_bind())
    
    # Agregar campos de calidad
    op.add_column('inventory', sa.Column('condicion_producto', condicion_producto_enum, nullable=False, server_default='NUEVO', comment='Condición física del producto en inventario'))
    op.add_column('inventory', sa.Column('notas_almacen', sa.Text(), nullable=True, comment='Observaciones y notas del personal de almacén'))


def downgrade():
    # Eliminar campos de calidad
    op.drop_column('inventory', 'notas_almacen')
    op.drop_column('inventory', 'condicion_producto')
    
    # Eliminar enum CondicionProducto
    condicion_producto_enum = postgresql.ENUM(name='condicionproducto')
    condicion_producto_enum.drop(op.get_bind())
