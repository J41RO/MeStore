#!/usr/bin/env python3
"""
Quick test for vendor orders endpoints
Tests basic functionality without extensive setup
"""

import asyncio
import sys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload

from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User, UserType


async def test_vendor_orders_query():
    """Test the core query logic for vendor orders"""

    # Setup async database connection
    DATABASE_URL = "postgresql+asyncpg://admin_jairo:Qwerty2025!@localhost:5432/mestore"
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        print("🔍 Testing vendor orders query logic...\n")

        # 1. Get a vendor user (assuming first vendor exists)
        vendor_query = select(User).where(User.user_type == UserType.VENDOR).limit(1)
        result = await db.execute(vendor_query)
        vendor = result.scalar_one_or_none()

        if not vendor:
            print("❌ No vendor found in database. Please create a vendor first.")
            return False

        print(f"✅ Found vendor: {vendor.email} (ID: {vendor.id})")

        # 2. Get vendor's products
        products_query = select(Product).where(Product.vendedor_id == vendor.id).limit(5)
        result = await db.execute(products_query)
        products = result.scalars().all()

        print(f"✅ Vendor has {len(products)} products")
        if products:
            for p in products[:3]:
                print(f"   - {p.name} (SKU: {p.sku})")

        # 3. Query orders with vendor's products (same logic as endpoint)
        query = (
            select(Order)
            .join(OrderItem, Order.id == OrderItem.order_id)
            .join(Product, OrderItem.product_id == Product.id)
            .where(Product.vendedor_id == vendor.id)
            .options(
                selectinload(Order.items).joinedload(OrderItem.product),
                selectinload(Order.buyer)
            )
            .distinct()
            .order_by(Order.created_at.desc())
            .limit(10)
        )

        result = await db.execute(query)
        orders = result.unique().scalars().all()

        print(f"\n✅ Found {len(orders)} orders with vendor's products")

        if orders:
            for order in orders[:5]:
                vendor_items = [
                    item for item in order.items
                    if item.product and item.product.vendedor_id == vendor.id
                ]
                vendor_total = sum(float(item.total_price) for item in vendor_items)

                print(f"\n📦 Order #{order.order_number}")
                print(f"   Status: {order.status}")
                print(f"   Vendor items: {len(vendor_items)}")
                print(f"   Vendor total: ${vendor_total:,.2f}")
                print(f"   Created: {order.created_at}")

                for item in vendor_items[:2]:
                    print(f"      - {item.product_name} x{item.quantity} @ ${float(item.unit_price):,.2f}")
        else:
            print("\n⚠️  No orders found for this vendor yet")
            print("   This is normal for a new vendor account")

        # 4. Test statistics calculation
        total_orders = len(orders)
        total_items = 0
        total_revenue = 0.0

        for order in orders:
            vendor_items = [
                item for item in order.items
                if item.product and item.product.vendedor_id == vendor.id
            ]
            total_items += len(vendor_items)
            total_revenue += sum(float(item.total_price) for item in vendor_items)

        print(f"\n📊 Vendor Statistics:")
        print(f"   Total orders: {total_orders}")
        print(f"   Total items: {total_items}")
        print(f"   Total revenue: ${total_revenue:,.2f}")

        print("\n✅ All vendor orders queries working correctly!")
        return True


async def main():
    try:
        success = await test_vendor_orders_query()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
