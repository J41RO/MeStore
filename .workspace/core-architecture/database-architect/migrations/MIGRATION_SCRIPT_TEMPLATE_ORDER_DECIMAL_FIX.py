"""
Fix Order model Float to Decimal for financial fields

Revision ID: fix_order_decimal_2025_10_02
Revises: [PREVIOUS_REVISION]
Create Date: 2025-10-02

CRITICAL FIX: Convert Float to DECIMAL for order financial fields
- Blocking payment system
- Causing precision loss in currency calculations
- Mismatch with Pydantic schemas

Changes:
- Order.subtotal: Float → DECIMAL(10, 2)
- Order.tax_amount: Float → DECIMAL(10, 2)
- Order.shipping_cost: Float → DECIMAL(10, 2)
- Order.discount_amount: Float → DECIMAL(10, 2)
- Order.total_amount: Float → DECIMAL(10, 2)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fix_order_decimal_2025_10_02'
down_revision = '[PREVIOUS_REVISION]'  # Update with actual previous revision
branch_labels = None
depends_on = None


def upgrade():
    """
    Convert Order financial fields from Float to DECIMAL(10, 2)

    Safe conversion: Float → DECIMAL preserves precision
    No data loss expected
    """
    # Bind connection for transaction management
    conn = op.get_bind()

    print("Starting Order model Float → DECIMAL conversion...")

    # Convert each financial field
    # Using NUMERIC instead of DECIMAL for PostgreSQL compatibility
    with op.batch_alter_table('orders', schema=None) as batch_op:
        # subtotal
        batch_op.alter_column(
            'subtotal',
            existing_type=sa.Float(),
            type_=sa.NUMERIC(precision=10, scale=2),
            existing_nullable=False,
            existing_server_default=sa.text('0.0')
        )

        # tax_amount
        batch_op.alter_column(
            'tax_amount',
            existing_type=sa.Float(),
            type_=sa.NUMERIC(precision=10, scale=2),
            existing_nullable=False,
            existing_server_default=sa.text('0.0')
        )

        # shipping_cost
        batch_op.alter_column(
            'shipping_cost',
            existing_type=sa.Float(),
            type_=sa.NUMERIC(precision=10, scale=2),
            existing_nullable=False,
            existing_server_default=sa.text('0.0')
        )

        # discount_amount
        batch_op.alter_column(
            'discount_amount',
            existing_type=sa.Float(),
            type_=sa.NUMERIC(precision=10, scale=2),
            existing_nullable=False,
            existing_server_default=sa.text('0.0')
        )

        # total_amount
        batch_op.alter_column(
            'total_amount',
            existing_type=sa.Float(),
            type_=sa.NUMERIC(precision=10, scale=2),
            existing_nullable=False
        )

    print("✅ Successfully converted Order financial fields to DECIMAL(10, 2)")

    # Verify conversion (optional but recommended)
    result = conn.execute(sa.text("""
        SELECT column_name, data_type, numeric_precision, numeric_scale
        FROM information_schema.columns
        WHERE table_name = 'orders'
        AND column_name IN ('subtotal', 'tax_amount', 'shipping_cost', 'discount_amount', 'total_amount')
        ORDER BY column_name;
    """))

    print("\nVerification - Column types after migration:")
    for row in result:
        print(f"  {row[0]}: {row[1]} ({row[2]}, {row[3]})")


def downgrade():
    """
    Revert DECIMAL back to Float

    WARNING: This may cause precision loss
    Only use for emergency rollback
    """
    print("Rolling back Order model DECIMAL → Float conversion...")

    with op.batch_alter_table('orders', schema=None) as batch_op:
        # Revert each field back to Float
        batch_op.alter_column(
            'subtotal',
            existing_type=sa.NUMERIC(precision=10, scale=2),
            type_=sa.Float(),
            existing_nullable=False,
            existing_server_default=sa.text('0.0')
        )

        batch_op.alter_column(
            'tax_amount',
            existing_type=sa.NUMERIC(precision=10, scale=2),
            type_=sa.Float(),
            existing_nullable=False,
            existing_server_default=sa.text('0.0')
        )

        batch_op.alter_column(
            'shipping_cost',
            existing_type=sa.NUMERIC(precision=10, scale=2),
            type_=sa.Float(),
            existing_nullable=False,
            existing_server_default=sa.text('0.0')
        )

        batch_op.alter_column(
            'discount_amount',
            existing_type=sa.NUMERIC(precision=10, scale=2),
            type_=sa.Float(),
            existing_nullable=False,
            existing_server_default=sa.text('0.0')
        )

        batch_op.alter_column(
            'total_amount',
            existing_type=sa.NUMERIC(precision=10, scale=2),
            type_=sa.Float(),
            existing_nullable=False
        )

    print("⚠️ Rolled back to Float (precision may be lost)")


# Testing helper functions
def test_conversion():
    """
    Test helper to verify migration
    Run after upgrade() to confirm changes
    """
    from app.models.order import Order
    from app.database import SessionLocal
    from decimal import Decimal

    db = SessionLocal()
    try:
        # Create test order
        test_order = Order(
            order_number="TEST-DECIMAL-001",
            buyer_id="test-buyer-uuid",
            subtotal=Decimal("1234.56"),
            tax_amount=Decimal("123.45"),
            shipping_cost=Decimal("50.00"),
            discount_amount=Decimal("10.00"),
            total_amount=Decimal("1398.01"),
            shipping_name="Test User",
            shipping_phone="1234567890",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db.add(test_order)
        db.commit()

        # Verify types
        assert isinstance(test_order.subtotal, Decimal), "subtotal must be Decimal"
        assert isinstance(test_order.total_amount, Decimal), "total_amount must be Decimal"

        # Verify precision preserved
        assert test_order.subtotal == Decimal("1234.56"), "Precision lost"

        print("✅ Migration test passed")

        # Cleanup
        db.delete(test_order)
        db.commit()

    except Exception as e:
        print(f"❌ Migration test failed: {e}")
        db.rollback()
    finally:
        db.close()


# Pre-migration checks
def pre_migration_check():
    """
    Run this before executing migration
    Checks for potential issues
    """
    from app.database import SessionLocal
    import sqlalchemy as sa

    db = SessionLocal()
    try:
        # Check if orders table exists
        result = db.execute(sa.text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'orders'
            );
        """))

        if not result.scalar():
            print("❌ Orders table does not exist")
            return False

        # Check current data types
        result = db.execute(sa.text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'orders'
            AND column_name IN ('subtotal', 'tax_amount', 'total_amount');
        """))

        print("\nCurrent column types:")
        for row in result:
            print(f"  {row[0]}: {row[1]}")

        # Check for NULL values that might cause issues
        result = db.execute(sa.text("""
            SELECT COUNT(*) FROM orders
            WHERE subtotal IS NULL
               OR tax_amount IS NULL
               OR total_amount IS NULL;
        """))

        null_count = result.scalar()
        if null_count > 0:
            print(f"⚠️ Found {null_count} orders with NULL financial values")
            print("   Migration may fail - clean data first")
            return False

        # Check for extreme values that won't fit in DECIMAL(10,2)
        result = db.execute(sa.text("""
            SELECT COUNT(*) FROM orders
            WHERE ABS(total_amount) > 99999999.99;
        """))

        extreme_count = result.scalar()
        if extreme_count > 0:
            print(f"⚠️ Found {extreme_count} orders with amounts > 99,999,999.99")
            print("   These won't fit in DECIMAL(10,2) - increase precision or clean data")
            return False

        print("✅ Pre-migration checks passed")
        return True

    except Exception as e:
        print(f"❌ Pre-migration check failed: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    """
    Direct execution for testing
    DO NOT run in production - use alembic upgrade instead
    """
    print("=" * 60)
    print("MIGRATION TEST MODE")
    print("=" * 60)

    print("\n1. Running pre-migration checks...")
    if not pre_migration_check():
        print("\n❌ Pre-migration checks failed - cannot proceed")
        exit(1)

    print("\n2. Checks passed - ready for migration")
    print("\nTo execute migration:")
    print("  alembic upgrade head")
    print("\nTo test conversion:")
    print("  python -c 'from [this_file] import test_conversion; test_conversion()'")
