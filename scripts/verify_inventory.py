#!/usr/bin/env python3
"""
Script to verify inventory records and stock calculation.

Database Architect AI - Stock Verification
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.models.product import Product
from app.models.inventory import Inventory


async def verify_inventory():
    """Verify inventory records and stock."""

    async with AsyncSessionLocal() as session:
        try:
            # Query products with their inventory (eager loading)
            result = await session.execute(
                select(Product)
                .options(selectinload(Product.ubicaciones_inventario))
                .limit(10)
            )
            products = result.scalars().all()

            print(f"Verifying {len(products)} products...\n")

            for idx, product in enumerate(products, start=1):
                # Count inventory records
                inventory_count = len(product.ubicaciones_inventario) if product.ubicaciones_inventario else 0

                # Calculate stock using model methods
                stock_total = sum(inv.cantidad for inv in product.ubicaciones_inventario) if product.ubicaciones_inventario else 0
                stock_disponible = sum(inv.cantidad_disponible() for inv in product.ubicaciones_inventario) if product.ubicaciones_inventario else 0
                stock_reservado = sum(inv.cantidad_reservada for inv in product.ubicaciones_inventario) if product.ubicaciones_inventario else 0

                print(f"[{idx}] Product: {product.name}")
                print(f"    SKU: {product.sku}")
                print(f"    Inventory Records: {inventory_count}")
                print(f"    Stock Total: {stock_total}")
                print(f"    Stock Available: {stock_disponible}")
                print(f"    Stock Reserved: {stock_reservado}")

                if product.ubicaciones_inventario:
                    for inv in product.ubicaciones_inventario:
                        print(f"    - Location: {inv.get_ubicacion_completa()}, Qty: {inv.cantidad}, Reserved: {inv.cantidad_reservada}, Status: {inv.status.value}")

                print()

            # Summary
            products_with_stock = sum(1 for p in products if p.ubicaciones_inventario)
            products_without_stock = len(products) - products_with_stock

            print("=" * 60)
            print("Summary:")
            print(f"  Total Products: {len(products)}")
            print(f"  With Stock: {products_with_stock}")
            print(f"  Without Stock: {products_without_stock}")
            print("=" * 60)

        except Exception as e:
            print(f"Error verifying inventory: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Main execution."""
    print("=" * 60)
    print("Stock Inventory Verification")
    print("Database Architect AI")
    print("=" * 60)
    print()

    await verify_inventory()


if __name__ == "__main__":
    asyncio.run(main())
