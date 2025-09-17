"""Add vendor_id column to orders table for vendor order management

Revision ID: def456
Revises: abc123
Create Date: 2025-09-13 08:45:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision = 'def456'
down_revision = 'abc123'
branch_labels = None
depends_on = None

def upgrade():
    """Add vendor_id column to orders table with foreign key constraint and indexes"""

    # Add vendor_id column to orders table
    op.add_column('orders', sa.Column('vendor_id', UUID(as_uuid=True), nullable=True))

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_orders_vendor_id',
        'orders',
        'users',
        ['vendor_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Create index for performance on vendor order queries
    op.create_index('idx_orders_vendor_id', 'orders', ['vendor_id'])

    # Create composite index for vendor status queries
    op.create_index('idx_orders_vendor_status', 'orders', ['vendor_id', 'status'])

    # Create composite index for vendor creation date queries
    op.create_index('idx_orders_vendor_created', 'orders', ['vendor_id', 'created_at'])

def downgrade():
    """Remove vendor_id column and related constraints/indexes"""

    # Drop indexes
    op.drop_index('idx_orders_vendor_created', table_name='orders')
    op.drop_index('idx_orders_vendor_status', table_name='orders')
    op.drop_index('idx_orders_vendor_id', table_name='orders')

    # Drop foreign key constraint
    op.drop_constraint('fk_orders_vendor_id', 'orders', type_='foreignkey')

    # Drop column
    op.drop_column('orders', 'vendor_id')