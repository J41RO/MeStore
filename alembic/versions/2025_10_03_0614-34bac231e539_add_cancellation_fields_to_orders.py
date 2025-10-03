"""add_cancellation_fields_to_orders

Revision ID: 34bac231e539
Revises: 2a1280396cea
Create Date: 2025-10-03 06:14:44.197270+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34bac231e539'
down_revision: Union[str, Sequence[str], None] = '2a1280396cea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Add cancellation fields to orders table."""
    # Add cancelled_at timestamp column
    op.add_column('orders', sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True))

    # Add cancellation_reason text column
    op.add_column('orders', sa.Column('cancellation_reason', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema: Remove cancellation fields from orders table."""
    # Remove cancellation columns
    op.drop_column('orders', 'cancellation_reason')
    op.drop_column('orders', 'cancelled_at')
