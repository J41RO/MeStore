"""add_email_verification_token_fields

Revision ID: 7fa3d3be7e02
Revises: 063355405f32
Create Date: 2025-10-11 07:47:52.388532+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7fa3d3be7e02'
down_revision: Union[str, Sequence[str], None] = '063355405f32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add email verification token fields."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email_verification_token', sa.String(length=100), nullable=True, comment='Token for email verification link'))
        batch_op.add_column(sa.Column('email_verification_expires', sa.DateTime(), nullable=True, comment='Expiration timestamp for email verification token'))

        # Add index for faster token lookups
        batch_op.create_index('idx_users_email_verification_token', ['email_verification_token'], unique=False)


def downgrade() -> None:
    """Downgrade schema - Remove email verification token fields."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index('idx_users_email_verification_token')
        batch_op.drop_column('email_verification_expires')
        batch_op.drop_column('email_verification_token')
