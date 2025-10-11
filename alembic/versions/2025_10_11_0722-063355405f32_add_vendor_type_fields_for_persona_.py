"""add_vendor_type_fields_for_persona_juridica

Revision ID: 063355405f32
Revises: eed5e29cc9eb
Create Date: 2025-10-11 07:22:00.026549+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '063355405f32'
down_revision: Union[str, Sequence[str], None] = 'eed5e29cc9eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add Persona Jurídica fields to users table."""
    # === CAMPOS ESPECÍFICOS PARA PERSONA JURÍDICA ===

    # Razón Social (nombre legal de la empresa)
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('razon_social', sa.String(length=200), nullable=True, comment='Razón social de la empresa (Persona Jurídica)'))
        batch_op.add_column(sa.Column('nombre_comercial', sa.String(length=200), nullable=True, comment='Nombre comercial del negocio'))
        batch_op.add_column(sa.Column('nit', sa.String(length=20), nullable=True, comment='NIT de la empresa (formato: 123456789-0)'))
        batch_op.add_column(sa.Column('representante_legal', sa.String(length=100), nullable=True, comment='Nombre completo del representante legal'))
        batch_op.add_column(sa.Column('cedula_representante', sa.String(length=20), nullable=True, comment='Cédula del representante legal'))
        batch_op.add_column(sa.Column('email_representante', sa.String(length=255), nullable=True, comment='Email del representante legal'))
        batch_op.add_column(sa.Column('telefono_empresa', sa.String(length=20), nullable=True, comment='Teléfono corporativo de la empresa'))

        # === CAMPOS PARA AMBOS TIPOS DE VENDOR (Natural y Jurídica) ===
        batch_op.add_column(sa.Column('direccion_fiscal', sa.String(length=300), nullable=True, comment='Dirección fiscal del vendedor'))
        batch_op.add_column(sa.Column('ciudad_fiscal', sa.String(length=100), nullable=True, comment='Ciudad fiscal'))
        batch_op.add_column(sa.Column('departamento_fiscal', sa.String(length=100), nullable=True, comment='Departamento fiscal'))
        batch_op.add_column(sa.Column('departamento', sa.String(length=100), nullable=True, comment='Departamento de residencia'))
        batch_op.add_column(sa.Column('codigo_postal', sa.String(length=10), nullable=True, comment='Código postal colombiano'))
        batch_op.add_column(sa.Column('tipo_vendedor', sa.String(length=20), nullable=True, comment='Tipo de vendedor: persona_natural o persona_juridica'))

        # Add unique constraint for NIT
        batch_op.create_unique_constraint('uq_users_nit', ['nit'])

        # Create indexes for optimization
        batch_op.create_index('idx_users_nit', ['nit'], unique=False)
        batch_op.create_index('idx_users_tipo_vendedor', ['tipo_vendedor'], unique=False)
        batch_op.create_index('idx_users_vendor_type_status', ['user_type', 'vendor_status', 'tipo_vendedor'], unique=False)


def downgrade() -> None:
    """Downgrade schema - Remove Persona Jurídica fields."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        # Drop indexes first
        batch_op.drop_index('idx_users_vendor_type_status')
        batch_op.drop_index('idx_users_tipo_vendedor')
        batch_op.drop_index('idx_users_nit')

        # Drop unique constraint
        batch_op.drop_constraint('uq_users_nit', type_='unique')

        # Drop columns
        batch_op.drop_column('tipo_vendedor')
        batch_op.drop_column('codigo_postal')
        batch_op.drop_column('departamento')
        batch_op.drop_column('departamento_fiscal')
        batch_op.drop_column('ciudad_fiscal')
        batch_op.drop_column('direccion_fiscal')
        batch_op.drop_column('telefono_empresa')
        batch_op.drop_column('email_representante')
        batch_op.drop_column('cedula_representante')
        batch_op.drop_column('representante_legal')
        batch_op.drop_column('nit')
        batch_op.drop_column('nombre_comercial')
        batch_op.drop_column('razon_social')
