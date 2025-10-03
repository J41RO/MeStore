"""fix_order_transaction_decimal_types

Revision ID: fix_order_tx_decimal_3
Revises: fix_order_item_decimal_2
Create Date: 2025-10-02 10:20:00.000000

Fix OrderTransaction model Float to DECIMAL for amount field.
This migration converts the transaction amount from Float to DECIMAL(10, 2)
to ensure precise payment amount tracking.

Affected columns:
- amount: Float → DECIMAL(10, 2)

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite, postgresql

# revision identifiers, used by Alembic.
revision = 'fix_order_tx_decimal_3'
down_revision = 'fix_order_item_decimal_2'
branch_labels = None
depends_on = None


def upgrade():
    # Determine the database type
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == 'postgresql':
        # PostgreSQL: Use NUMERIC type directly
        op.alter_column('order_transactions', 'amount',
                       existing_type=sa.REAL(),
                       type_=sa.NUMERIC(precision=10, scale=2),
                       existing_nullable=False)

    elif dialect_name == 'sqlite':
        # SQLite: Update column type using batch mode
        with op.batch_alter_table('order_transactions', schema=None) as batch_op:
            batch_op.alter_column('amount',
                                 existing_type=sa.REAL(),
                                 type_=sa.NUMERIC(precision=10, scale=2),
                                 existing_nullable=False)


def downgrade():
    # Determine the database type
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == 'postgresql':
        # Rollback to Float (REAL in PostgreSQL)
        op.alter_column('order_transactions', 'amount',
                       existing_type=sa.NUMERIC(precision=10, scale=2),
                       type_=sa.REAL(),
                       existing_nullable=False)

    elif dialect_name == 'sqlite':
        # Rollback for SQLite
        with op.batch_alter_table('order_transactions', schema=None) as batch_op:
            batch_op.alter_column('amount',
                                 existing_type=sa.NUMERIC(precision=10, scale=2),
                                 type_=sa.REAL(),
                                 existing_nullable=False)
