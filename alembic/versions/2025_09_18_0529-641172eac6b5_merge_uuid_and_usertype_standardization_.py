"""merge uuid and usertype standardization migrations

Revision ID: 641172eac6b5
Revises: d4f3e8c9b2a1, 2025_09_17_2100
Create Date: 2025-09-18 05:29:06.829398+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '641172eac6b5'
down_revision: Union[str, Sequence[str], None] = ('d4f3e8c9b2a1', '2025_09_17_2100')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
