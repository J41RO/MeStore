#!/usr/bin/env python3
"""
Script to populate inventory records for ALL products.

This script creates inventory for any product that doesn't have stock,
making the entire marketplace ready for cart testing.

Database Architect AI - Complete Stock Population
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.product import Product
from app.models.inventory import Inventory, InventoryStatus, CondicionProducto


async def populate_all_inventory():
    """Populate inventory records for ALL products without stock."""

    async with AsyncSessionLocal() as session:
        try:
            # Query all products
            result = await session.execute(
                select(Product)
            )
            products = result.scalars().all()

            print(f"Found {len(products)} products in database")

            if not products:
                print("No products found. Please create products first.")
                return

            # Counter for tracking
            created_count = 0
            skipped_count = 0
            zone_idx = 1

            for idx, product in enumerate(products, start=1):
                # Check if inventory already exists
                existing_inventory = await session.execute(
                    select(Inventory).where(Inventory.product_id == product.id)
                )

                if existing_inventory.scalars().first():
                    print(f"  [{idx}] {product.name[:50]:50} | SKU: {product.sku:30} | ⏭️  Already has inventory")
                    skipped_count += 1
                    continue

                # Create inventory record
                # Cycle through zones A-F
                zones = ["A", "B", "C", "D", "E", "F"]
                zone = zones[zone_idx % len(zones)]
                estante = str((zone_idx // len(zones)) + 1)
                posicion = str((zone_idx % 5) + 1)

                inventory = Inventory(
                    product_id=product.id,
                    zona=zone,
                    estante=estante,
                    posicion=posicion,
                    cantidad=50,  # Initial stock: 50 units
                    cantidad_reservada=0,
                    status=InventoryStatus.DISPONIBLE,
                    condicion_producto=CondicionProducto.NUEVO
                )

                session.add(inventory)
                created_count += 1
                zone_idx += 1

                print(f"  [{idx}] {product.name[:50]:50} | SKU: {product.sku:30} | ✅ {zone}-{estante}-{posicion} | Stock: 50")

            # Commit all inventory records
            await session.commit()

            print(f"\n{'='*100}")
            print(f"Inventory Population Complete!")
            print(f"  ✅ Created: {created_count} inventory records")
            print(f"  ⏭️  Skipped: {skipped_count} products (already have inventory)")
            print(f"  📊 Total Products: {len(products)}")
            print(f"  📦 Products with Stock: {skipped_count + created_count}")
            print(f"{'='*100}")

        except Exception as e:
            await session.rollback()
            print(f"Error populating inventory: {e}")
            import traceback
            traceback.print_exc()
            raise


async def main():
    """Main execution."""
    print("=" * 100)
    print("Complete Stock Inventory Population")
    print("Database Architect AI - Populate ALL Products")
    print("=" * 100)
    print()

    await populate_all_inventory()

    print()
    print("=" * 100)
    print("Next Steps:")
    print("1. Verify stock in API: GET /api/v1/productos/")
    print("2. Test cart functionality in frontend with any product")
    print("3. All products should now be available for purchase")
    print("=" * 100)


if __name__ == "__main__":
    asyncio.run(main())
