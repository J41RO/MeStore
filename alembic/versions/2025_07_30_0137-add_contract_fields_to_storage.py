"""Add contract fields to Storage model

Revision ID: contract_fields_20250730_0137
Revises: 6db2652485c7
Create Date: $(date -Iseconds)

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'contract_fields_20250730_0137'
down_revision = '6db2652485c7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add contract fields to storages table"""
    
    # Add fecha_inicio column
    op.add_column('storages', sa.Column('fecha_inicio', sa.DateTime(), nullable=True, 
                                       comment='Fecha de inicio del contrato de almacenamiento'))
    
    # Add fecha_fin column  
    op.add_column('storages', sa.Column('fecha_fin', sa.DateTime(), nullable=True,
                                       comment='Fecha de finalización del contrato de almacenamiento'))
    
    # Add renovacion_automatica column
    op.add_column('storages', sa.Column('renovacion_automatica', sa.Boolean(), 
                                       nullable=False, server_default=sa.text('false'),
                                       comment='Indica si el contrato se renueva automáticamente'))
    
    # Add check constraint for valid dates
    op.create_check_constraint(
        'ck_storage_fechas_validas',
        'storages', 
        'fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin > fecha_inicio'
    )


def downgrade() -> None:
    """Remove contract fields from storages table"""
    
    # Drop check constraint
    op.drop_constraint('ck_storage_fechas_validas', 'storages', type_='check')
    
    # Drop columns
    op.drop_column('storages', 'renovacion_automatica')
    op.drop_column('storages', 'fecha_fin')
    op.drop_column('storages', 'fecha_inicio')