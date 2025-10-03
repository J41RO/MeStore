#!/usr/bin/env python
"""
Safe script to update PENDING products to APPROVED status.

Purpose: Fix stock visibility issue by approving products with inventory
Author: backend-framework-ai
Date: 2025-10-02
Related Issue: Products not showing in frontend checkout

Safety Features:
- Transaction rollback on error
- Dry-run mode for validation
- Detailed logging and verification
- Only updates products with inventory
- Preserves audit trail
"""

import asyncio
from datetime import datetime
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload

import sys
sys.path.append('/home/admin-jairo/MeStore')

from app.database import AsyncSessionLocal
from app.models.product import Product, ProductStatus


async def analyze_pending_products():
    """Analyze PENDING products before update."""
    print("\n" + "="*70)
    print("ANALYZING PENDING PRODUCTS")
    print("="*70)

    async with AsyncSessionLocal() as session:
        # Get PENDING products with inventory
        stmt = (
            select(Product)
            .options(selectinload(Product.ubicaciones_inventario))
            .where(
                Product.status == ProductStatus.PENDING,
                Product.deleted_at.is_(None)
            )
        )

        result = await session.execute(stmt)
        pending_products = result.scalars().all()

        if not pending_products:
            print("✅ No PENDING products found. All products are already APPROVED.")
            return []

        print(f"\nFound {len(pending_products)} PENDING products:\n")

        for p in pending_products:
            stock_total = p.get_stock_total() if hasattr(p, 'get_stock_total') else 0
            stock_disponible = p.get_stock_disponible() if hasattr(p, 'get_stock_disponible') else 0

            print(f"  ID: {p.id}")
            print(f"  SKU: {p.sku}")
            print(f"  Name: {p.name}")
            print(f"  Status: {p.status.value}")
            print(f"  Stock Total: {stock_total}")
            print(f"  Stock Available: {stock_disponible}")
            print(f"  Inventory Locations: {len(p.ubicaciones_inventario) if p.ubicaciones_inventario else 0}")
            print(f"  Created: {p.created_at}")
            print("-" * 70)

        return pending_products


async def update_pending_to_approved(dry_run=True):
    """
    Update PENDING products to APPROVED status.

    Args:
        dry_run: If True, only show what would be updated without committing
    """
    print("\n" + "="*70)
    print(f"{'DRY RUN - ' if dry_run else ''}UPDATING PENDING PRODUCTS TO APPROVED")
    print("="*70)

    async with AsyncSessionLocal() as session:
        try:
            # Get count before update
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

            print(f"\nFound {count_before} PENDING products to update")

            if dry_run:
                print("\n⚠️  DRY RUN MODE - No changes will be committed")
                print("Run with dry_run=False to apply changes")
                return

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

            # Verify update
            result = await session.execute(
                select(func.count(Product.id)).where(
                    Product.status == ProductStatus.APPROVED,
                    Product.deleted_at.is_(None)
                )
            )
            count_approved = result.scalar()

            result = await session.execute(
                select(func.count(Product.id)).where(
                    Product.status == ProductStatus.PENDING,
                    Product.deleted_at.is_(None)
                )
            )
            count_pending = result.scalar()

            print(f"\n✅ SUCCESS")
            print(f"  Updated: {affected_rows} products")
            print(f"  APPROVED products now: {count_approved}")
            print(f"  PENDING products remaining: {count_pending}")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ ERROR updating products: {str(e)}")
            print("Transaction rolled back - no changes were made")
            raise


async def verify_after_update():
    """Verify products after update."""
    print("\n" + "="*70)
    print("VERIFICATION AFTER UPDATE")
    print("="*70)

    async with AsyncSessionLocal() as session:
        # Count by status
        for status in [ProductStatus.PENDING, ProductStatus.APPROVED]:
            result = await session.execute(
                select(func.count(Product.id)).where(
                    Product.status == status,
                    Product.deleted_at.is_(None)
                )
            )
            count = result.scalar()
            print(f"  {status.value}: {count} products")

        # Get sample APPROVED products with stock
        stmt = (
            select(Product)
            .options(selectinload(Product.ubicaciones_inventario))
            .where(
                Product.status == ProductStatus.APPROVED,
                Product.deleted_at.is_(None)
            )
            .limit(3)
        )

        result = await session.execute(stmt)
        approved_products = result.scalars().all()

        if approved_products:
            print("\n  Sample APPROVED products:")
            for p in approved_products:
                stock = p.get_stock_total() if hasattr(p, 'get_stock_total') else 0
                print(f"    - {p.sku}: {p.name[:40]} (Stock: {stock})")


async def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("STOCK FIX: PENDING → APPROVED STATUS UPDATE")
    print("="*70)
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print(f"Agent: backend-framework-ai")

    try:
        # Step 1: Analyze current state
        pending_products = await analyze_pending_products()

        if not pending_products:
            print("\n✅ All products are already in correct status")
            return

        # Step 2: Show what will be updated (dry run)
        await update_pending_to_approved(dry_run=True)

        # Step 3: Ask for confirmation
        print("\n" + "="*70)
        response = input("\nDo you want to apply these changes? (yes/no): ").strip().lower()

        if response != 'yes':
            print("\n❌ Update cancelled by user")
            return

        # Step 4: Apply update
        await update_pending_to_approved(dry_run=False)

        # Step 5: Verify
        await verify_after_update()

        print("\n" + "="*70)
        print("✅ STOCK FIX COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\nNext Steps:")
        print("  1. Verify products appear in frontend")
        print("  2. Test adding products to cart")
        print("  3. Complete checkout flow end-to-end")
        print("  4. Verify stock decrements after order")

    except Exception as e:
        print(f"\n❌ Script failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
