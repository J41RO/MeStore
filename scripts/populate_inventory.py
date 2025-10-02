#!/usr/bin/env python3
"""
Script to populate inventory records for products with zero stock.

This script:
1. Queries all products from the database
2. Creates inventory records for products without stock
3. Assigns warehouse locations (zone, shelf, position)
4. Sets initial stock quantity to 50 units per product

Database Architect AI - Stock Inventory Population
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


async def populate_inventory():
    """Populate inventory records for products."""

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

            # Create inventory for first 10 products (or all if less than 10)
            products_to_process = products[:10] if len(products) > 10 else products

            for idx, product in enumerate(products_to_process, start=1):
                # Check if inventory already exists
                existing_inventory = await session.execute(
                    select(Inventory).where(Inventory.product_id == product.id)
                )

                if existing_inventory.scalars().first():
                    print(f"  [{idx}] Product '{product.name}' (SKU: {product.sku}) - Already has inventory, skipping")
                    skipped_count += 1
                    continue

                # Create inventory record
                # Assign warehouse location: Zone A, Shelf incrementing, Position 1
                zone = "A"
                estante = str(idx)
                posicion = "1"

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

                print(f"  [{idx}] Created inventory for '{product.name}' (SKU: {product.sku})")
                print(f"      Location: {zone}-{estante}-{posicion}")
                print(f"      Stock: 50 units available")

            # Commit all inventory records
            await session.commit()

            print(f"\nInventory Population Complete!")
            print(f"  ✅ Created: {created_count} inventory records")
            print(f"  ⏭️  Skipped: {skipped_count} products (already have inventory)")

            # Verify stock calculation
            print(f"\nVerifying stock calculation...")
            for product in products_to_process:
                await session.refresh(product)
                stock_total = product.get_stock_total()
                stock_disponible = product.get_stock_disponible()
                print(f"  - {product.name}: Stock Total={stock_total}, Available={stock_disponible}")

        except Exception as e:
            await session.rollback()
            print(f"Error populating inventory: {e}")
            import traceback
            traceback.print_exc()
            raise


async def main():
    """Main execution."""
    print("=" * 60)
    print("Stock Inventory Population Script")
    print("Database Architect AI")
    print("=" * 60)
    print()

    await populate_inventory()

    print()
    print("=" * 60)
    print("Next Steps:")
    print("1. Verify stock in API: GET /api/v1/productos/")
    print("2. Test cart functionality in frontend")
    print("3. Verify 'Agregar al carrito' button is enabled")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
