"""add_account_status_to_users

Revision ID: fe0b5dec2fb2
Revises: db108145b492
Create Date: 2025-10-08 21:41:38.089631+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe0b5dec2fb2'
down_revision: Union[str, Sequence[str], None] = 'db108145b492'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add account_status column to users table."""
    # Create enum type for account_status
    account_status_enum = sa.Enum('pending', 'active', 'suspended', 'deleted', name='accountstatus')

    # For PostgreSQL, create the enum type
    # For SQLite, this will be a string with CHECK constraint
    try:
        account_status_enum.create(op.get_bind(), checkfirst=True)
    except Exception:
        # SQLite doesn't support ENUM, will use VARCHAR with CHECK constraint
        pass

    # Add account_status column
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(
            sa.Column(
                'account_status',
                account_status_enum,
                nullable=False,
                server_default='pending',
                comment='Estado general de la cuenta: pending, active, suspended, deleted'
            )
        )


def downgrade() -> None:
    """Remove account_status column from users table."""
    # Drop the column
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('account_status')

    # Drop the enum type (for PostgreSQL)
    try:
        sa.Enum(name='accountstatus').drop(op.get_bind(), checkfirst=True)
    except Exception:
        # SQLite doesn't have ENUMs to drop
        pass
