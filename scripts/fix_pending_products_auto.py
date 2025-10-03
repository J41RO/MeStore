#!/usr/bin/env python
"""
Automated version - updates PENDING products to APPROVED without prompts.
"""

import asyncio
from datetime import datetime
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload

import sys
sys.path.append('/home/admin-jairo/MeStore')

from app.database import AsyncSessionLocal
from app.models.product import Product, ProductStatus


async def update_pending_to_approved():
    """Update PENDING products to APPROVED status."""
    print("\n" + "="*70)
    print("UPDATING PENDING PRODUCTS TO APPROVED (AUTOMATED)")
    print("="*70)

    async with AsyncSessionLocal() as session:
        try:
            # Get count before
            result = await session.execute(
                select(func.count(Product.id)).where(
                    Product.status == ProductStatus.PENDING,
                    Product.deleted_at.is_(None)
                )
            )
            count_before = result.scalar()

            if count_before == 0:
                print("\n✅ No PENDING products to update.")
                return

            print(f"\n📋 Found {count_before} PENDING products")

            # Get details of products to update
            stmt = select(Product).where(
                Product.status == ProductStatus.PENDING,
                Product.deleted_at.is_(None)
            )
            result = await session.execute(stmt)
            products = result.scalars().all()

            print("\n📦 Products to update:")
            for p in products:
                print(f"  - {p.sku}: {p.name}")

            # Update PENDING to APPROVED
            stmt = (
                update(Product)
                .where(
                    Product.status == ProductStatus.PENDING,
                    Product.deleted_at.is_(None)
                )
                .values(
                    status=ProductStatus.APPROVED,
                    updated_at=datetime.utcnow()
                )
            )

            result = await session.execute(stmt)
            affected_rows = result.rowcount
            await session.commit()

            # Verify
            result = await session.execute(
                select(func.count(Product.id)).where(
                    Product.status == ProductStatus.APPROVED,
                    Product.deleted_at.is_(None)
                )
            )
            count_approved = result.scalar()

            print(f"\n✅ SUCCESS!")
            print(f"  ✓ Updated: {affected_rows} products")
            print(f"  ✓ Total APPROVED: {count_approved}")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ ERROR: {str(e)}")
            raise


async def main():
    print("\n" + "="*70)
    print("STOCK FIX: PENDING → APPROVED (AUTOMATED)")
    print("="*70)
    print(f"Timestamp: {datetime.utcnow().isoformat()}")

    try:
        await update_pending_to_approved()

        print("\n" + "="*70)
        print("✅ STOCK FIX COMPLETED")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
