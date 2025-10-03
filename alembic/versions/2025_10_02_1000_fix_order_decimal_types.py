"""fix_order_decimal_types

Revision ID: fix_order_decimal_1
Revises: 953052bf3be8
Create Date: 2025-10-02 10:00:00.000000

Fix Order model Float to DECIMAL for financial fields.
This migration converts all order amount fields from Float to DECIMAL(10, 2)
to ensure precise financial calculations without rounding errors.

Affected columns:
- subtotal: Float → DECIMAL(10, 2)
- tax_amount: Float → DECIMAL(10, 2)
- shipping_cost: Float → DECIMAL(10, 2)
- discount_amount: Float → DECIMAL(10, 2)
- total_amount: Float → DECIMAL(10, 2)

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite, postgresql

# revision identifiers, used by Alembic.
revision = 'fix_order_decimal_1'
down_revision = '953052bf3be8'
branch_labels = None
depends_on = None


def upgrade():
    # Determine the database type
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == 'postgresql':
        # PostgreSQL: Use NUMERIC type directly
        op.alter_column('orders', 'subtotal',
                       existing_type=sa.REAL(),
                       type_=sa.NUMERIC(precision=10, scale=2),
                       existing_nullable=False)

        op.alter_column('orders', 'tax_amount',
                       existing_type=sa.REAL(),
                       type_=sa.NUMERIC(precision=10, scale=2),
                       existing_nullable=False)

        op.alter_column('orders', 'shipping_cost',
                       existing_type=sa.REAL(),
                       type_=sa.NUMERIC(precision=10, scale=2),
                       existing_nullable=False)

        op.alter_column('orders', 'discount_amount',
                       existing_type=sa.REAL(),
                       type_=sa.NUMERIC(precision=10, scale=2),
                       existing_nullable=False)

        op.alter_column('orders', 'total_amount',
                       existing_type=sa.REAL(),
                       type_=sa.NUMERIC(precision=10, scale=2),
                       existing_nullable=False)

    elif dialect_name == 'sqlite':
        # SQLite: Float and Decimal are stored the same, but we update for consistency
        # SQLite doesn't support direct ALTER COLUMN TYPE, so we recreate the table
        with op.batch_alter_table('orders', schema=None) as batch_op:
            batch_op.alter_column('subtotal',
                                 existing_type=sa.REAL(),
                                 type_=sa.NUMERIC(precision=10, scale=2),
                                 existing_nullable=False)

            batch_op.alter_column('tax_amount',
                                 existing_type=sa.REAL(),
                                 type_=sa.NUMERIC(precision=10, scale=2),
                                 existing_nullable=False)

            batch_op.alter_column('shipping_cost',
                                 existing_type=sa.REAL(),
                                 type_=sa.NUMERIC(precision=10, scale=2),
                                 existing_nullable=False)

            batch_op.alter_column('discount_amount',
                                 existing_type=sa.REAL(),
                                 type_=sa.NUMERIC(precision=10, scale=2),
                                 existing_nullable=False)

            batch_op.alter_column('total_amount',
                                 existing_type=sa.REAL(),
                                 type_=sa.NUMERIC(precision=10, scale=2),
                                 existing_nullable=False)


def downgrade():
    # Determine the database type
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == 'postgresql':
        # Rollback to Float (REAL in PostgreSQL)
        op.alter_column('orders', 'total_amount',
                       existing_type=sa.NUMERIC(precision=10, scale=2),
                       type_=sa.REAL(),
                       existing_nullable=False)

        op.alter_column('orders', 'discount_amount',
                       existing_type=sa.NUMERIC(precision=10, scale=2),
                       type_=sa.REAL(),
                       existing_nullable=False)

        op.alter_column('orders', 'shipping_cost',
                       existing_type=sa.NUMERIC(precision=10, scale=2),
                       type_=sa.REAL(),
                       existing_nullable=False)

        op.alter_column('orders', 'tax_amount',
                       existing_type=sa.NUMERIC(precision=10, scale=2),
                       type_=sa.REAL(),
                       existing_nullable=False)

        op.alter_column('orders', 'subtotal',
                       existing_type=sa.NUMERIC(precision=10, scale=2),
                       type_=sa.REAL(),
                       existing_nullable=False)

    elif dialect_name == 'sqlite':
        # Rollback for SQLite
        with op.batch_alter_table('orders', schema=None) as batch_op:
            batch_op.alter_column('total_amount',
                                 existing_type=sa.NUMERIC(precision=10, scale=2),
                                 type_=sa.REAL(),
                                 existing_nullable=False)

            batch_op.alter_column('discount_amount',
                                 existing_type=sa.NUMERIC(precision=10, scale=2),
                                 type_=sa.REAL(),
                                 existing_nullable=False)

            batch_op.alter_column('shipping_cost',
                                 existing_type=sa.NUMERIC(precision=10, scale=2),
                                 type_=sa.REAL(),
                                 existing_nullable=False)

            batch_op.alter_column('tax_amount',
                                 existing_type=sa.NUMERIC(precision=10, scale=2),
                                 type_=sa.REAL(),
                                 existing_nullable=False)

            batch_op.alter_column('subtotal',
                                 existing_type=sa.NUMERIC(precision=10, scale=2),
                                 type_=sa.REAL(),
                                 existing_nullable=False)
