"""Add commission system tables and relationships

Revision ID: abc123
Revises: 
Create Date: 2025-09-13 16:30:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision = 'abc123'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create commissions table
    op.create_table('commissions',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('commission_number', sa.String(length=50), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_id', UUID(as_uuid=True), nullable=True),
        sa.Column('order_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('commission_rate', sa.DECIMAL(precision=5, scale=4), nullable=False),
        sa.Column('commission_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('vendor_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('platform_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('commission_type', sa.Enum('STANDARD', 'PREMIUM', 'PROMOTIONAL', 'CATEGORY_BASED', name='commissiontype'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'PAID', 'DISPUTED', 'REFUNDED', 'CANCELLED', name='commissionstatus'), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('calculation_method', sa.String(length=100), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('disputed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_by_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('order_amount > 0', name='check_order_amount_positive'),
        sa.CheckConstraint('commission_amount >= 0', name='check_commission_amount_non_negative'),
        sa.CheckConstraint('vendor_amount >= 0', name='check_vendor_amount_non_negative'),
        sa.CheckConstraint('platform_amount >= 0', name='check_platform_amount_non_negative'),
        sa.CheckConstraint('commission_rate >= 0 AND commission_rate <= 1', name='check_commission_rate_valid'),
        sa.CheckConstraint('vendor_amount + platform_amount = order_amount', name='check_amounts_balance'),
        sa.ForeignKeyConstraint(['approved_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['vendor_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('commission_number')
    )
    
    # Create indexes for performance
    op.create_index('idx_commission_calculation_date', 'commissions', ['calculated_at'])
    op.create_index('idx_commission_order_vendor', 'commissions', ['order_id', 'vendor_id'])
    op.create_index('idx_commission_vendor_status', 'commissions', ['vendor_id', 'status'])
    op.create_index(op.f('ix_commissions_id'), 'commissions', ['id'])
    op.create_index(op.f('ix_commissions_commission_number'), 'commissions', ['commission_number'])
    op.create_index(op.f('ix_commissions_order_id'), 'commissions', ['order_id'])
    op.create_index(op.f('ix_commissions_vendor_id'), 'commissions', ['vendor_id'])
    op.create_index(op.f('ix_commissions_transaction_id'), 'commissions', ['transaction_id'])
    op.create_index(op.f('ix_commissions_status'), 'commissions', ['status'])

def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_commissions_status'), table_name='commissions')
    op.drop_index(op.f('ix_commissions_transaction_id'), table_name='commissions')
    op.drop_index(op.f('ix_commissions_vendor_id'), table_name='commissions')
    op.drop_index(op.f('ix_commissions_order_id'), table_name='commissions')
    op.drop_index(op.f('ix_commissions_commission_number'), table_name='commissions')
    op.drop_index(op.f('ix_commissions_id'), table_name='commissions')
    op.drop_index('idx_commission_vendor_status', table_name='commissions')
    op.drop_index('idx_commission_order_vendor', table_name='commissions')
    op.drop_index('idx_commission_calculation_date', table_name='commissions')
    
    # Drop table
    op.drop_table('commissions')
