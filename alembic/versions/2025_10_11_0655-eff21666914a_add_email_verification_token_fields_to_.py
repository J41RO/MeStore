"""add email verification token fields to users table

Revision ID: eff21666914a
Revises: fe0b5dec2fb2
Create Date: 2025-10-11 06:55:35.894905+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eff21666914a'
down_revision: Union[str, Sequence[str], None] = 'fe0b5dec2fb2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add email_verification_token field
    op.add_column('users', sa.Column(
        'email_verification_token',
        sa.String(100),
        nullable=True,
        comment='Token único para verificación de email por link'
    ))

    # Add email_verification_expires field
    op.add_column('users', sa.Column(
        'email_verification_expires',
        sa.DateTime(timezone=True),
        nullable=True,
        comment='Fecha y hora de expiración del token de verificación de email'
    ))

    # Create indexes for better performance
    op.create_index(
        'ix_users_email_verification_token',
        'users',
        ['email_verification_token'],
        unique=False
    )

    op.create_index(
        'ix_users_email_verification_expires',
        'users',
        ['email_verification_expires'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes first
    op.drop_index('ix_users_email_verification_expires', table_name='users')
    op.drop_index('ix_users_email_verification_token', table_name='users')

    # Drop columns
    op.drop_column('users', 'email_verification_expires')
    op.drop_column('users', 'email_verification_token')
