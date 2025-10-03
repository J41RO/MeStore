"""add_shipping_tracking_fields_to_orders

Revision ID: db108145b492
Revises: 34bac231e539
Create Date: 2025-10-03 07:16:44.851947+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db108145b492'
down_revision: Union[str, Sequence[str], None] = '34bac231e539'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add shipping tracking fields to orders table
    op.add_column('orders', sa.Column('tracking_number', sa.String(length=100), nullable=True))
    op.add_column('orders', sa.Column('courier', sa.String(length=100), nullable=True))
    op.add_column('orders', sa.Column('estimated_delivery', sa.DateTime(timezone=True), nullable=True))
    op.add_column('orders', sa.Column('shipping_events', sa.JSON(), nullable=True))

    # Create index on tracking_number for faster lookups
    op.create_index('ix_orders_tracking_number', 'orders', ['tracking_number'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove index
    op.drop_index('ix_orders_tracking_number', table_name='orders')

    # Remove shipping tracking fields
    op.drop_column('orders', 'shipping_events')
    op.drop_column('orders', 'estimated_delivery')
    op.drop_column('orders', 'courier')
    op.drop_column('orders', 'tracking_number')
