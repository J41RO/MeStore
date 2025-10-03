"""fix_order_item_decimal_types

Revision ID: fix_order_item_decimal_2
Revises: fix_order_decimal_1
Create Date: 2025-10-02 10:10:00.000000

Fix OrderItem model Float to DECIMAL for pricing fields.
This migration converts OrderItem pricing fields from Float to DECIMAL(10, 2)
to ensure precise price calculations in line items.

Affected columns:
- unit_price: Float → DECIMAL(10, 2)
- total_price: Float → DECIMAL(10, 2)

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite, postgresql

# revision identifiers, used by Alembic.
revision = 'fix_order_item_decimal_2'
down_revision = 'fix_order_decimal_1'
branch_labels = None
depends_on = None


def upgrade():
    # Determine the database type
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == 'postgresql':
        # PostgreSQL: Use NUMERIC type directly
        op.alter_column('order_items', 'unit_price',
                       existing_type=sa.REAL(),
                       type_=sa.NUMERIC(precision=10, scale=2),
                       existing_nullable=False)

        op.alter_column('order_items', 'total_price',
                       existing_type=sa.REAL(),
                       type_=sa.NUMERIC(precision=10, scale=2),
                       existing_nullable=False)

    elif dialect_name == 'sqlite':
        # SQLite: Update column types using batch mode
        with op.batch_alter_table('order_items', schema=None) as batch_op:
            batch_op.alter_column('unit_price',
                                 existing_type=sa.REAL(),
                                 type_=sa.NUMERIC(precision=10, scale=2),
                                 existing_nullable=False)

            batch_op.alter_column('total_price',
                                 existing_type=sa.REAL(),
                                 type_=sa.NUMERIC(precision=10, scale=2),
                                 existing_nullable=False)


def downgrade():
    # Determine the database type
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == 'postgresql':
        # Rollback to Float (REAL in PostgreSQL)
        op.alter_column('order_items', 'total_price',
                       existing_type=sa.NUMERIC(precision=10, scale=2),
                       type_=sa.REAL(),
                       existing_nullable=False)

        op.alter_column('order_items', 'unit_price',
                       existing_type=sa.NUMERIC(precision=10, scale=2),
                       type_=sa.REAL(),
                       existing_nullable=False)

    elif dialect_name == 'sqlite':
        # Rollback for SQLite
        with op.batch_alter_table('order_items', schema=None) as batch_op:
            batch_op.alter_column('total_price',
                                 existing_type=sa.NUMERIC(precision=10, scale=2),
                                 type_=sa.REAL(),
                                 existing_nullable=False)

            batch_op.alter_column('unit_price',
                                 existing_type=sa.NUMERIC(precision=10, scale=2),
                                 type_=sa.REAL(),
                                 existing_nullable=False)
