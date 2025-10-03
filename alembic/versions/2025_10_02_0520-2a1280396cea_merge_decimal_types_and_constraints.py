"""merge_decimal_types_and_constraints

Revision ID: 2a1280396cea
Revises: fix_order_tx_decimal_3, add_critical_constraints
Create Date: 2025-10-02 05:20:57.559002+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a1280396cea'
down_revision: Union[str, Sequence[str], None] = ('fix_order_tx_decimal_3', 'add_critical_constraints')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
