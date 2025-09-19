"""standardize usertype enum values to lowercase english

Revision ID: 2025_09_17_2100
Revises: c58467fecce8
Create Date: 2025-09-17 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2025_09_17_2100'
down_revision = 'c58467fecce8'
branch_labels = None
depends_on = None


def upgrade():
    """
    Standardize UserType enum values from Spanish uppercase to English lowercase.

    Migration mappings:
    - COMPRADOR -> buyer
    - VENDEDOR -> vendor
    - ADMIN -> admin
    - SUPERUSER -> superuser
    """
    # SQLite doesn't support enum modifications directly
    # We need to update the data values

    # Update Spanish enum values to English lowercase
    op.execute("UPDATE users SET user_type = 'buyer' WHERE user_type = 'COMPRADOR'")
    op.execute("UPDATE users SET user_type = 'vendor' WHERE user_type = 'VENDEDOR'")
    op.execute("UPDATE users SET user_type = 'admin' WHERE user_type = 'ADMIN'")
    op.execute("UPDATE users SET user_type = 'superuser' WHERE user_type = 'SUPERUSER'")

def downgrade():
    """
    Revert UserType enum values from English lowercase to Spanish uppercase.
    """
    # Revert English lowercase to Spanish uppercase
    op.execute("UPDATE users SET user_type = 'COMPRADOR' WHERE user_type = 'buyer'")
    op.execute("UPDATE users SET user_type = 'VENDEDOR' WHERE user_type = 'vendor'")
    op.execute("UPDATE users SET user_type = 'ADMIN' WHERE user_type = 'admin'")
    op.execute("UPDATE users SET user_type = 'SUPERUSER' WHERE user_type = 'superuser'")