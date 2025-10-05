#!/usr/bin/env python3
"""
Test Data Seeding Script for E2E Testing
Creates sample orders for buyer journey validation
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
import random

DB_PATH = "/home/admin-jairo/MeStore/mestore.db"
BUYER_ID = "655c3dee-7879-4380-8fbd-151f7f80187a"  # comprador@test.com

def create_test_orders():
    """Create sample orders for E2E testing"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # First, get or create a test product
    cursor.execute("SELECT id, nombre, precio FROM products LIMIT 1")
    product = cursor.fetchone()

    if not product:
        print("❌ No products found in database. Cannot create test orders.")
        print("   Please create at least one product first.")
        conn.close()
        return False

    product_id, product_name, product_price = product
    print(f"✅ Using product: {product_name} (ID: {product_id}, Price: ${product_price})")

    # Create 5 test orders in different states
    order_states = [
        ("pending", "Pending", None),
        ("confirmed", "Confirmed", datetime.now() - timedelta(days=2)),
        ("processing", "Processing", datetime.now() - timedelta(days=1)),
        ("shipped", "Shipped", datetime.now() - timedelta(hours=12)),
        ("delivered", "Delivered", datetime.now() - timedelta(hours=2))
    ]

    orders_created = []

    for idx, (status, status_label, confirmed_at) in enumerate(order_states, 1):
        order_number = f"TEST-{datetime.now().strftime('%Y%m%d')}-{idx:04d}"
        quantity = random.randint(1, 3)
        subtotal = Decimal(str(product_price)) * quantity
        tax = subtotal * Decimal("0.19")  # 19% IVA Colombia
        shipping = Decimal("15000.00")  # $15,000 COP shipping
        total = subtotal + tax + shipping

        # Insert order
        order_insert = """
        INSERT INTO orders (
            order_number, buyer_id, subtotal, tax_amount, shipping_cost,
            discount_amount, total_amount, status, created_at, confirmed_at,
            shipping_name, shipping_phone, shipping_address, shipping_city,
            shipping_state, shipping_country
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(order_insert, (
            order_number,
            BUYER_ID,
            float(subtotal),
            float(tax),
            float(shipping),
            0.0,
            float(total),
            status,
            datetime.now() - timedelta(days=3-idx),
            confirmed_at,
            "Test Buyer",
            "+57 300 123 4567",
            "Calle 123 #45-67",
            "Bogotá",
            "Cundinamarca",
            "CO"
        ))

        order_id = cursor.lastrowid

        # Insert order item
        item_insert = """
        INSERT INTO order_items (
            order_id, product_id, quantity, unit_price, total_price
        ) VALUES (?, ?, ?, ?, ?)
        """

        cursor.execute(item_insert, (
            order_id,
            product_id,
            quantity,
            float(product_price),
            float(subtotal)
        ))

        # Add shipping tracking for shipped/delivered orders
        if status in ["shipped", "delivered"]:
            tracking_number = f"TRACK-{order_number}"
            cursor.execute("""
                UPDATE orders
                SET tracking_number = ?, courier = ?, shipped_at = ?
                WHERE id = ?
            """, (tracking_number, "Coordinadora", datetime.now() - timedelta(hours=24), order_id))

        orders_created.append({
            "order_number": order_number,
            "status": status_label,
            "total": total
        })

        print(f"✅ Created order {order_number} - Status: {status_label} - Total: ${total:,.2f}")

    conn.commit()
    conn.close()

    print(f"\n🎉 Successfully created {len(orders_created)} test orders!")
    print(f"   Buyer ID: {BUYER_ID}")
    print(f"   Buyer Email: comprador@test.com")
    print("\n📊 Orders Summary:")
    for order in orders_created:
        print(f"   - {order['order_number']}: {order['status']} (${order['total']:,.2f})")

    return True


if __name__ == "__main__":
    print("🚀 E2E Test Data Seeding Script")
    print("=" * 50)
    print(f"Database: {DB_PATH}")
    print(f"Buyer: comprador@test.com")
    print("=" * 50)
    print()

    success = create_test_orders()

    if success:
        print("\n✅ Test data created successfully!")
        print("   You can now run E2E tests with real order data.")
    else:
        print("\n❌ Failed to create test data.")
        print("   Please check the error messages above.")
