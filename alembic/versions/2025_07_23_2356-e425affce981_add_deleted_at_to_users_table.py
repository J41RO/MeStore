"""add_deleted_at_to_users_table

Revision ID: e425affce981
Revises: c779d8204e95
Create Date: 2025-07-23 23:56:25.438193+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e425affce981'
down_revision: Union[str, Sequence[str], None] = 'c779d8204e95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Agregar campo deleted_at a tabla users para soft delete
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(), nullable=True, comment='Fecha de eliminación lógica (soft delete)'))
    
    # Renombrar campo is_active a active_status para consistencia con modelo
    op.alter_column('users', 'is_active', new_column_name='active_status')


def downgrade() -> None:
    """Downgrade schema."""
    # Renombrar campo active_status de vuelta a is_active
    op.alter_column('users', 'active_status', new_column_name='is_active')
    
    # Eliminar campo deleted_at
    op.drop_column('users', 'deleted_at')
