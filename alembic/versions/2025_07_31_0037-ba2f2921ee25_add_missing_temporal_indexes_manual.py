"""add_missing_temporal_indexes_manual

Revision ID: ba2f2921ee25
Revises: 9164fb08a156
Create Date: 2025-07-31 00:37:32.423774+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba2f2921ee25'
down_revision: Union[str, Sequence[str], None] = '9164fb08a156'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # ### Agregando índices de fecha para reportes temporales ###
    
    # users - índices faltantes
    op.create_index('ix_users_created_at', 'users', ['created_at'])
    op.create_index('ix_users_updated_at', 'users', ['updated_at'])
    
    # products - índice faltante (created_at ya existe)
    op.create_index('ix_products_updated_at', 'products', ['updated_at'])
    
    # inventory - índices faltantes
    op.create_index('ix_inventory_created_at', 'inventory', ['created_at'])
    
    # storages - índices faltantes
    op.create_index('ix_storages_created_at', 'storages', ['created_at'])
    op.create_index('ix_storages_updated_at', 'storages', ['updated_at'])
    
    # transactions - índices faltantes individuales
    op.create_index('ix_transactions_created_at', 'transactions', ['created_at'])
    op.create_index('ix_transactions_updated_at', 'transactions', ['updated_at'])
    
    # Índices compuestos para reportes avanzados
    op.create_index('ix_users_type_created', 'users', ['user_type', 'created_at'])
    op.create_index('ix_products_status_updated', 'products', ['status', 'updated_at'])
    
    # ### end Alembic commands ###
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### Eliminando índices de fecha agregados ###
    
    # Eliminar índices compuestos primero
    op.drop_index('ix_products_status_updated', 'products')
    op.drop_index('ix_users_type_created', 'users')
    
    # Eliminar índices individuales
    op.drop_index('ix_transactions_updated_at', 'transactions')
    op.drop_index('ix_transactions_created_at', 'transactions')
    op.drop_index('ix_storages_updated_at', 'storages')
    op.drop_index('ix_storages_created_at', 'storages')
    op.drop_index('ix_inventory_created_at', 'inventory')
    op.drop_index('ix_products_updated_at', 'products')
    op.drop_index('ix_users_updated_at', 'users')
    op.drop_index('ix_users_created_at', 'users')
    
    # ### end Alembic commands ###
    # ### end Alembic commands ###
