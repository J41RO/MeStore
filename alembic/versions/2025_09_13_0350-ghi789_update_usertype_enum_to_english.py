"""Update UserType enum to use English values (BUYER/VENDOR instead of COMPRADOR/VENDEDOR)

Revision ID: ghi789
Revises: def456
Create Date: 2025-09-13 08:50:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'ghi789'
down_revision = 'def456'
branch_labels = None
depends_on = None

def upgrade():
    """Update UserType enum to English values and migrate existing data"""

    # Add new English enum values
    op.execute("ALTER TYPE usertype ADD VALUE 'BUYER'")
    op.execute("ALTER TYPE usertype ADD VALUE 'VENDOR'")

    # Update existing data to use new English values
    op.execute("UPDATE users SET user_type = 'BUYER' WHERE user_type = 'COMPRADOR'")
    op.execute("UPDATE users SET user_type = 'VENDOR' WHERE user_type = 'VENDEDOR'")

    # Note: We keep the old values for now to maintain backward compatibility
    # They can be removed in a future migration after confirming all systems use new values

def downgrade():
    """Revert to Spanish enum values"""

    # Update data back to Spanish values
    op.execute("UPDATE users SET user_type = 'COMPRADOR' WHERE user_type = 'BUYER'")
    op.execute("UPDATE users SET user_type = 'VENDEDOR' WHERE user_type = 'VENDOR'")

    # Note: We don't remove the English enum values in downgrade
    # to avoid enum value deletion complexity