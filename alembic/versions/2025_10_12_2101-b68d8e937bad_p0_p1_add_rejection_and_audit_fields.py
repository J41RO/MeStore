"""P0_P1_add_rejection_and_audit_fields

Revision ID: b68d8e937bad
Revises: 7fa3d3be7e02
Create Date: 2025-10-12 21:01:39.133427+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b68d8e937bad'
down_revision: Union[str, Sequence[str], None] = '7fa3d3be7e02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade schema.

    P0 BLOCKER: Add rejection_reason fields to users table
    P1 HIGH: Add audit compliance fields to vendor_audit_logs table
    """
    # P0: Add rejection fields to users table
    op.add_column('users', sa.Column('rejection_reason', sa.Text(), nullable=True, comment='Detailed reason for vendor rejection by admin'))
    op.add_column('users', sa.Column('rejected_at', sa.DateTime(timezone=True), nullable=True, comment='Timestamp when vendor was rejected'))
    op.add_column('users', sa.Column('rejected_by_id', sa.String(length=36), nullable=True, comment='Admin user ID who rejected this vendor'))

    # P1: Add audit compliance fields to vendor_audit_logs table
    op.add_column('vendor_audit_logs', sa.Column('reason', sa.Text(), nullable=True, comment='Detailed reason for the action (required for rejections)'))
    op.add_column('vendor_audit_logs', sa.Column('notes', sa.Text(), nullable=True, comment='Additional notes or context'))
    op.add_column('vendor_audit_logs', sa.Column('previous_status', sa.String(length=50), nullable=True, comment='Vendor status before action'))
    op.add_column('vendor_audit_logs', sa.Column('new_status', sa.String(length=50), nullable=True, comment='Vendor status after action'))
    op.add_column('vendor_audit_logs', sa.Column('ip_address', sa.String(length=45), nullable=True, comment='IP address of admin performing action'))
    op.add_column('vendor_audit_logs', sa.Column('user_agent', sa.String(length=255), nullable=True, comment='Browser/client user agent'))


def downgrade() -> None:
    """Downgrade schema - remove P0+P1 fields."""
    # Remove P1 fields from vendor_audit_logs
    op.drop_column('vendor_audit_logs', 'user_agent')
    op.drop_column('vendor_audit_logs', 'ip_address')
    op.drop_column('vendor_audit_logs', 'new_status')
    op.drop_column('vendor_audit_logs', 'previous_status')
    op.drop_column('vendor_audit_logs', 'notes')
    op.drop_column('vendor_audit_logs', 'reason')

    # Remove P0 fields from users
    op.drop_column('users', 'rejected_by_id')
    op.drop_column('users', 'rejected_at')
    op.drop_column('users', 'rejection_reason')
