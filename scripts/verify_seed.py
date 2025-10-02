#!/usr/bin/env python3
"""
Quick verification script for seeded products.
Checks database directly to confirm products are accessible.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models.product import Product, ProductStatus
from app.models.user import User
from sqlalchemy import select, func


async def verify_seed():
    """Verify seeded products are in database."""

    async with AsyncSessionLocal() as db:
        print("=" * 70)
        print("PRODUCT SEED VERIFICATION")
        print("=" * 70)

        # Check vendor
        print("\n1. VENDOR CHECK")
        result = await db.execute(
            select(User).where(User.email == 'vendor@mestore.com')
        )
        vendor = result.scalar_one_or_none()

        if vendor:
            print(f"   ✓ Vendor exists: {vendor.email}")
            print(f"   ✓ Vendor ID: {vendor.id}")
            print(f"   ✓ Type: {vendor.user_type.value}")
            print(f"   ✓ Active: {vendor.is_active}")
        else:
            print("   ✗ Vendor NOT found")
            return

        # Check total products
        print("\n2. PRODUCT COUNT")
        result = await db.execute(select(func.count(Product.id)))
        total = result.scalar()
        print(f"   Total products: {total}")

        # Check approved products
        result = await db.execute(
            select(func.count(Product.id)).where(Product.status == ProductStatus.APPROVED)
        )
        approved = result.scalar()
        print(f"   Approved products: {approved}")

        # Check by category
        print("\n3. PRODUCTS BY CATEGORY")
        result = await db.execute(
            select(Product.categoria, func.count(Product.id))
            .group_by(Product.categoria)
            .order_by(func.count(Product.id).desc())
        )
        categories = result.all()

        for cat, count in categories:
            print(f"   {cat:15} : {count:2} products")

        # Check price range
        print("\n4. PRICE ANALYSIS")
        result = await db.execute(
            select(
                func.min(Product.precio_venta),
                func.max(Product.precio_venta),
                func.avg(Product.precio_venta)
            ).where(Product.status == ProductStatus.APPROVED)
        )
        min_price, max_price, avg_price = result.one()

        print(f"   Min price: ${min_price:,.0f} COP")
        print(f"   Max price: ${max_price:,.0f} COP")
        print(f"   Avg price: ${avg_price:,.0f} COP")

        # Sample products
        print("\n5. SAMPLE PRODUCTS (First 5)")
        result = await db.execute(
            select(Product)
            .where(Product.status == ProductStatus.APPROVED)
            .limit(5)
        )
        products = result.scalars().all()

        for i, p in enumerate(products, 1):
            print(f"   {i}. {p.sku}")
            print(f"      Name: {p.name}")
            print(f"      Category: {p.categoria}")
            print(f"      Price: ${p.precio_venta:,.0f} COP")
            print(f"      Status: {p.status.value}")
            print()

        # Verification summary
        print("=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70)

        checks = [
            ("Vendor created", vendor is not None),
            ("Products created", total > 0),
            ("APPROVED products", approved > 0),
            ("Multiple categories", len(categories) >= 5),
            ("Price range valid", min_price and max_price and min_price < max_price)
        ]

        all_passed = True
        for check_name, passed in checks:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status:8} : {check_name}")
            if not passed:
                all_passed = False

        print("\n" + "=" * 70)
        if all_passed:
            print("✓ ALL CHECKS PASSED - Seed successful!")
            print("\nProducts are ready for the public catalog.")
            print(f"\nVendor login: vendor@mestore.com / Vendor123456")
        else:
            print("✗ SOME CHECKS FAILED - Review above")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(verify_seed())
