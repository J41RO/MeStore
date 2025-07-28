"""add inventory status enum field

Revision ID: 71fc98eda510
Revises: 0983629ac57a
Create Date: 2025-07-28 12:31:51.831175

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '71fc98eda510'
down_revision: Union[str, None] = '0983629ac57a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crear el tipo ENUM en PostgreSQL primero
    inventorystatus_enum = postgresql.ENUM('DISPONIBLE', 'RESERVADO', 'EN_PICKING', 'DESPACHADO', name='inventorystatus')
    inventorystatus_enum.create(op.get_bind())
    
    # Agregar columna status con el enum creado
    op.add_column('inventory', sa.Column('status', 
                                        sa.Enum('DISPONIBLE', 'RESERVADO', 'EN_PICKING', 'DESPACHADO', name='inventorystatus'), 
                                        nullable=False, 
                                        server_default='DISPONIBLE',
                                        comment='Estado del inventario en el proceso de fulfillment'))


def downgrade() -> None:
    # Eliminar columna
    op.drop_column('inventory', 'status')
    
    # Eliminar el tipo ENUM
    inventorystatus_enum = postgresql.ENUM('DISPONIBLE', 'RESERVADO', 'EN_PICKING', 'DESPACHADO', name='inventorystatus')
    inventorystatus_enum.drop(op.get_bind())
