"""Add critical database constraints for data integrity

Revision ID: add_critical_constraints
Revises: 953052bf3be8
Create Date: 2025-10-02 00:00:00.000000

This migration adds comprehensive CHECK constraints, FK cascades, and indexes
to ensure data integrity across critical tables: orders, order_items, payments,
products, and users.

IMPORTANT: Run scripts/validate_constraint_data.py BEFORE applying this migration
to identify and fix any existing data violations.

Author: Database Architect AI
Status: DRAFT - DO NOT EXECUTE WITHOUT VALIDATION
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_critical_constraints'
down_revision: Union[str, Sequence[str], None] = '953052bf3be8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Apply critical database constraints.

    WARNING: This will fail if existing data violates constraints!
    Run validation script first: python scripts/validate_constraint_data.py
    """

    # =========================================================================
    # PHASE 1: ADD CHECK CONSTRAINTS TO ORDERS TABLE
    # =========================================================================
    print("Adding CHECK constraints to orders table...")

    # Ensure all financial amounts are non-negative
    op.create_check_constraint(
        'ck_order_subtotal_non_negative',
        'orders',
        'subtotal >= 0',
        comment='Subtotal must be non-negative'
    )

    op.create_check_constraint(
        'ck_order_tax_non_negative',
        'orders',
        'tax_amount >= 0',
        comment='Tax amount must be non-negative'
    )

    op.create_check_constraint(
        'ck_order_shipping_non_negative',
        'orders',
        'shipping_cost >= 0',
        comment='Shipping cost must be non-negative'
    )

    op.create_check_constraint(
        'ck_order_discount_non_negative',
        'orders',
        'discount_amount >= 0',
        comment='Discount amount must be non-negative'
    )

    # Total must be positive (at least 0.01)
    op.create_check_constraint(
        'ck_order_total_positive',
        'orders',
        'total_amount > 0',
        comment='Order total must be positive'
    )

    # Validate total calculation matches components
    # Allow 0.01 tolerance for float precision issues
    op.create_check_constraint(
        'ck_order_total_calculation',
        'orders',
        'ABS(total_amount - (subtotal + tax_amount + shipping_cost - discount_amount)) <= 0.01',
        comment='Total must equal subtotal + tax + shipping - discount'
    )

    # Ensure shipping info is present
    op.create_check_constraint(
        'ck_order_shipping_name_not_empty',
        'orders',
        "LENGTH(TRIM(shipping_name)) > 0",
        comment='Shipping name cannot be empty'
    )

    op.create_check_constraint(
        'ck_order_shipping_phone_not_empty',
        'orders',
        "LENGTH(TRIM(shipping_phone)) > 0",
        comment='Shipping phone cannot be empty'
    )

    # =========================================================================
    # PHASE 2: ADD CHECK CONSTRAINTS TO ORDER_ITEMS TABLE
    # =========================================================================
    print("Adding CHECK constraints to order_items table...")

    # Quantity must be positive
    op.create_check_constraint(
        'ck_order_item_quantity_positive',
        'order_items',
        'quantity > 0',
        comment='Order item quantity must be positive'
    )

    # Unit price must be positive
    op.create_check_constraint(
        'ck_order_item_unit_price_positive',
        'order_items',
        'unit_price > 0',
        comment='Order item unit price must be positive'
    )

    # Total price must match calculation
    op.create_check_constraint(
        'ck_order_item_total_calculation',
        'order_items',
        'ABS(total_price - (unit_price * quantity)) <= 0.01',
        comment='Total price must equal unit_price * quantity'
    )

    # Product info must be present
    op.create_check_constraint(
        'ck_order_item_product_name_not_empty',
        'order_items',
        "LENGTH(TRIM(product_name)) > 0",
        comment='Product name cannot be empty'
    )

    op.create_check_constraint(
        'ck_order_item_product_sku_not_empty',
        'order_items',
        "LENGTH(TRIM(product_sku)) > 0",
        comment='Product SKU cannot be empty'
    )

    # =========================================================================
    # PHASE 3: ADD CHECK CONSTRAINTS TO PAYMENTS TABLE
    # =========================================================================
    print("Adding CHECK constraints to payments table...")

    # Payment amount must be positive
    op.create_check_constraint(
        'ck_payment_amount_positive',
        'payments',
        'amount_in_cents > 0',
        comment='Payment amount must be positive (in cents)'
    )

    # Currency code must be exactly 3 characters
    op.create_check_constraint(
        'ck_payment_currency_format',
        'payments',
        "LENGTH(currency) = 3",
        comment='Currency code must be 3 characters (ISO 4217)'
    )

    # Payment method type cannot be empty
    op.create_check_constraint(
        'ck_payment_method_type_not_empty',
        'payments',
        "LENGTH(TRIM(payment_method_type)) > 0",
        comment='Payment method type cannot be empty'
    )

    # Status cannot be empty
    op.create_check_constraint(
        'ck_payment_status_not_empty',
        'payments',
        "LENGTH(TRIM(status)) > 0",
        comment='Payment status cannot be empty'
    )

    # =========================================================================
    # PHASE 4: ADD CHECK CONSTRAINTS TO PRODUCTS TABLE
    # =========================================================================
    print("Adding CHECK constraints to products table...")

    # Prices must be non-negative when set
    op.create_check_constraint(
        'ck_product_precio_venta_non_negative',
        'products',
        'precio_venta IS NULL OR precio_venta >= 0',
        comment='Sale price must be non-negative when set'
    )

    op.create_check_constraint(
        'ck_product_precio_costo_non_negative',
        'products',
        'precio_costo IS NULL OR precio_costo >= 0',
        comment='Cost price must be non-negative when set'
    )

    op.create_check_constraint(
        'ck_product_comision_non_negative',
        'products',
        'comision_mestocker IS NULL OR comision_mestocker >= 0',
        comment='Commission must be non-negative when set'
    )

    # Weight must be non-negative
    op.create_check_constraint(
        'ck_product_peso_non_negative',
        'products',
        'peso IS NULL OR peso >= 0',
        comment='Weight must be non-negative when set'
    )

    # SKU cannot be empty
    op.create_check_constraint(
        'ck_product_sku_not_empty',
        'products',
        "LENGTH(TRIM(sku)) > 0",
        comment='Product SKU cannot be empty'
    )

    # Name cannot be empty
    op.create_check_constraint(
        'ck_product_name_not_empty',
        'products',
        "LENGTH(TRIM(name)) > 0",
        comment='Product name cannot be empty'
    )

    # =========================================================================
    # PHASE 5: ADD CHECK CONSTRAINTS TO USERS TABLE
    # =========================================================================
    print("Adding CHECK constraints to users table...")

    # Email format basic validation
    op.create_check_constraint(
        'ck_user_email_format',
        'users',
        "email LIKE '%@%.%'",
        comment='Email must have valid format (basic check)'
    )

    # Security clearance must be between 1 and 5
    op.create_check_constraint(
        'ck_user_security_clearance_range',
        'users',
        'security_clearance_level BETWEEN 1 AND 5',
        comment='Security clearance must be between 1 and 5'
    )

    # Performance score must be between 0 and 100
    op.create_check_constraint(
        'ck_user_performance_score_range',
        'users',
        'performance_score BETWEEN 0 AND 100',
        comment='Performance score must be between 0 and 100'
    )

    # Failed login attempts cannot be negative
    op.create_check_constraint(
        'ck_user_failed_logins_non_negative',
        'users',
        'failed_login_attempts >= 0',
        comment='Failed login attempts cannot be negative'
    )

    # OTP attempts cannot be negative
    op.create_check_constraint(
        'ck_user_otp_attempts_non_negative',
        'users',
        'otp_attempts >= 0',
        comment='OTP attempts cannot be negative'
    )

    # Reset attempts cannot be negative
    op.create_check_constraint(
        'ck_user_reset_attempts_non_negative',
        'users',
        'reset_attempts >= 0',
        comment='Reset attempts cannot be negative'
    )

    # =========================================================================
    # PHASE 6: FIX FOREIGN KEY CASCADES
    # =========================================================================
    print("Fixing foreign key cascade configurations...")

    # Drop and recreate FK constraints with proper cascades
    # Note: This section depends on your database engine and existing constraints
    # For SQLite, FKs cannot be altered, so this would require table recreation
    # For PostgreSQL, we can alter constraints

    # ORDERS.buyer_id - Should RESTRICT deletion of buyers with orders
    with op.batch_alter_table('orders') as batch_op:
        batch_op.drop_constraint('orders_buyer_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_orders_buyer_id',
            'users',
            ['buyer_id'],
            ['id'],
            ondelete='RESTRICT',
            comment='Prevent deletion of buyers with orders'
        )

    # ORDER_TRANSACTIONS.order_id - Should CASCADE deletion (delete transactions with order)
    with op.batch_alter_table('order_transactions') as batch_op:
        batch_op.drop_constraint('order_transactions_order_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_order_transactions_order_id',
            'orders',
            ['order_id'],
            ['id'],
            ondelete='CASCADE',
            comment='Delete transactions when order is deleted'
        )

    # ORDER_TRANSACTIONS.payment_method_id - Should SET NULL (allow method deletion)
    with op.batch_alter_table('order_transactions') as batch_op:
        batch_op.drop_constraint('order_transactions_payment_method_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_order_transactions_payment_method_id',
            'payment_methods',
            ['payment_method_id'],
            ['id'],
            ondelete='SET NULL',
            comment='Allow payment method deletion without breaking transactions'
        )

    # PAYMENTS.transaction_id - Should RESTRICT (protect transaction history)
    with op.batch_alter_table('payments') as batch_op:
        batch_op.drop_constraint('payments_transaction_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_payments_transaction_id',
            'order_transactions',
            ['transaction_id'],
            ['id'],
            ondelete='RESTRICT',
            comment='Prevent deletion of transactions with payments'
        )

    # ORDER_ITEMS.product_id - Should RESTRICT (prevent deletion of products in orders)
    with op.batch_alter_table('order_items') as batch_op:
        batch_op.drop_constraint('order_items_product_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_order_items_product_id',
            'products',
            ['product_id'],
            ['id'],
            ondelete='RESTRICT',
            comment='Prevent deletion of products that are in orders'
        )

    # ORDER_ITEMS.order_id - Already CASCADE (correct)
    # PAYMENT_METHODS.buyer_id - Should CASCADE
    with op.batch_alter_table('payment_methods') as batch_op:
        batch_op.drop_constraint('payment_methods_buyer_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_payment_methods_buyer_id',
            'users',
            ['buyer_id'],
            ['id'],
            ondelete='CASCADE',
            comment='Delete payment methods when user is deleted'
        )

    # PRODUCTS.vendedor_id - Should RESTRICT (prevent vendor deletion with products)
    with op.batch_alter_table('products') as batch_op:
        batch_op.drop_constraint('products_vendedor_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_products_vendedor_id',
            'users',
            ['vendedor_id'],
            ['id'],
            ondelete='RESTRICT',
            comment='Prevent deletion of vendors with products'
        )

    # =========================================================================
    # PHASE 7: ADD PERFORMANCE INDEXES FOR FK COLUMNS
    # =========================================================================
    print("Adding performance indexes...")

    # Index on payments.transaction_id for faster joins
    op.create_index(
        'ix_payments_transaction_id',
        'payments',
        ['transaction_id']
    )

    # Index on order_transactions.order_id for faster lookups
    op.create_index(
        'ix_order_transactions_order_id',
        'order_transactions',
        ['order_id']
    )

    # Index on order_transactions.payment_method_id
    op.create_index(
        'ix_order_transactions_payment_method_id',
        'order_transactions',
        ['payment_method_id']
    )

    # Composite index for payment lookups by status
    op.create_index(
        'ix_payments_status_created',
        'payments',
        ['status', 'created_at']
    )

    # Composite index for order status lookups
    op.create_index(
        'ix_orders_status_created',
        'orders',
        ['status', 'created_at']
    )

    # =========================================================================
    # PHASE 8: ADD PARTIAL UNIQUE INDEXES FOR NULLABLE UNIQUE FIELDS
    # =========================================================================
    print("Adding partial unique indexes for Wompi IDs...")

    # Partial unique index for wompi_transaction_id (only when not null)
    # Note: This is PostgreSQL-specific syntax
    op.execute("""
        CREATE UNIQUE INDEX ix_payments_wompi_transaction_id_unique
        ON payments (wompi_transaction_id)
        WHERE wompi_transaction_id IS NOT NULL;
    """)

    # Partial unique index for wompi_payment_id (only when not null)
    op.execute("""
        CREATE UNIQUE INDEX ix_payments_wompi_payment_id_unique
        ON payments (wompi_payment_id)
        WHERE wompi_payment_id IS NOT NULL;
    """)

    # Partial unique index for gateway_transaction_id in order_transactions
    op.execute("""
        CREATE UNIQUE INDEX ix_order_transactions_gateway_id_unique
        ON order_transactions (gateway_transaction_id)
        WHERE gateway_transaction_id IS NOT NULL;
    """)

    print("✅ All critical constraints and indexes added successfully!")


def downgrade() -> None:
    """
    Remove all constraints and indexes added by this migration.

    Use this carefully - removing constraints may allow invalid data!
    """

    # =========================================================================
    # REMOVE PARTIAL UNIQUE INDEXES
    # =========================================================================
    print("Removing partial unique indexes...")
    op.execute("DROP INDEX IF EXISTS ix_order_transactions_gateway_id_unique;")
    op.execute("DROP INDEX IF EXISTS ix_payments_wompi_payment_id_unique;")
    op.execute("DROP INDEX IF EXISTS ix_payments_wompi_transaction_id_unique;")

    # =========================================================================
    # REMOVE PERFORMANCE INDEXES
    # =========================================================================
    print("Removing performance indexes...")
    op.drop_index('ix_orders_status_created', table_name='orders')
    op.drop_index('ix_payments_status_created', table_name='payments')
    op.drop_index('ix_order_transactions_payment_method_id', table_name='order_transactions')
    op.drop_index('ix_order_transactions_order_id', table_name='order_transactions')
    op.drop_index('ix_payments_transaction_id', table_name='payments')

    # =========================================================================
    # REVERT FK CASCADES TO ORIGINAL (NO CASCADE)
    # =========================================================================
    print("Reverting FK cascades...")

    with op.batch_alter_table('products') as batch_op:
        batch_op.drop_constraint('fk_products_vendedor_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'products_vendedor_id_fkey',
            'users',
            ['vendedor_id'],
            ['id']
        )

    with op.batch_alter_table('payment_methods') as batch_op:
        batch_op.drop_constraint('fk_payment_methods_buyer_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'payment_methods_buyer_id_fkey',
            'users',
            ['buyer_id'],
            ['id']
        )

    with op.batch_alter_table('order_items') as batch_op:
        batch_op.drop_constraint('fk_order_items_product_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'order_items_product_id_fkey',
            'products',
            ['product_id'],
            ['id']
        )

    with op.batch_alter_table('payments') as batch_op:
        batch_op.drop_constraint('fk_payments_transaction_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'payments_transaction_id_fkey',
            'order_transactions',
            ['transaction_id'],
            ['id']
        )

    with op.batch_alter_table('order_transactions') as batch_op:
        batch_op.drop_constraint('fk_order_transactions_payment_method_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'order_transactions_payment_method_id_fkey',
            'payment_methods',
            ['payment_method_id'],
            ['id']
        )

    with op.batch_alter_table('order_transactions') as batch_op:
        batch_op.drop_constraint('fk_order_transactions_order_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'order_transactions_order_id_fkey',
            'orders',
            ['order_id'],
            ['id']
        )

    with op.batch_alter_table('orders') as batch_op:
        batch_op.drop_constraint('fk_orders_buyer_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'orders_buyer_id_fkey',
            'users',
            ['buyer_id'],
            ['id']
        )

    # =========================================================================
    # REMOVE CHECK CONSTRAINTS - USERS TABLE
    # =========================================================================
    print("Removing CHECK constraints from users table...")
    op.drop_constraint('ck_user_reset_attempts_non_negative', 'users')
    op.drop_constraint('ck_user_otp_attempts_non_negative', 'users')
    op.drop_constraint('ck_user_failed_logins_non_negative', 'users')
    op.drop_constraint('ck_user_performance_score_range', 'users')
    op.drop_constraint('ck_user_security_clearance_range', 'users')
    op.drop_constraint('ck_user_email_format', 'users')

    # =========================================================================
    # REMOVE CHECK CONSTRAINTS - PRODUCTS TABLE
    # =========================================================================
    print("Removing CHECK constraints from products table...")
    op.drop_constraint('ck_product_name_not_empty', 'products')
    op.drop_constraint('ck_product_sku_not_empty', 'products')
    op.drop_constraint('ck_product_peso_non_negative', 'products')
    op.drop_constraint('ck_product_comision_non_negative', 'products')
    op.drop_constraint('ck_product_precio_costo_non_negative', 'products')
    op.drop_constraint('ck_product_precio_venta_non_negative', 'products')

    # =========================================================================
    # REMOVE CHECK CONSTRAINTS - PAYMENTS TABLE
    # =========================================================================
    print("Removing CHECK constraints from payments table...")
    op.drop_constraint('ck_payment_status_not_empty', 'payments')
    op.drop_constraint('ck_payment_method_type_not_empty', 'payments')
    op.drop_constraint('ck_payment_currency_format', 'payments')
    op.drop_constraint('ck_payment_amount_positive', 'payments')

    # =========================================================================
    # REMOVE CHECK CONSTRAINTS - ORDER_ITEMS TABLE
    # =========================================================================
    print("Removing CHECK constraints from order_items table...")
    op.drop_constraint('ck_order_item_product_sku_not_empty', 'order_items')
    op.drop_constraint('ck_order_item_product_name_not_empty', 'order_items')
    op.drop_constraint('ck_order_item_total_calculation', 'order_items')
    op.drop_constraint('ck_order_item_unit_price_positive', 'order_items')
    op.drop_constraint('ck_order_item_quantity_positive', 'order_items')

    # =========================================================================
    # REMOVE CHECK CONSTRAINTS - ORDERS TABLE
    # =========================================================================
    print("Removing CHECK constraints from orders table...")
    op.drop_constraint('ck_order_shipping_phone_not_empty', 'orders')
    op.drop_constraint('ck_order_shipping_name_not_empty', 'orders')
    op.drop_constraint('ck_order_total_calculation', 'orders')
    op.drop_constraint('ck_order_total_positive', 'orders')
    op.drop_constraint('ck_order_discount_non_negative', 'orders')
    op.drop_constraint('ck_order_shipping_non_negative', 'orders')
    op.drop_constraint('ck_order_tax_non_negative', 'orders')
    op.drop_constraint('ck_order_subtotal_non_negative', 'orders')

    print("✅ All constraints and indexes removed successfully!")
