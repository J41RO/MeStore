#!/usr/bin/env python3
"""
Script para actualizar sales_count de productos para simular tendencias.
Esto permitirá que la sección "Tendencias del Momento" muestre productos.
"""
import asyncio
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Database URL
DATABASE_URL = "sqlite+aiosqlite:///./mestore.db"

async def update_trending_products():
    """Actualizar sales_count de productos para crear tendencias"""

    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Import models
        import sys
        sys.path.insert(0, '/home/admin-jairo/MeStore')
        from app.models.product import Product

        # Get all products
        result = await session.execute(select(Product))
        products = result.scalars().all()

        if not products:
            print("❌ No hay productos en la base de datos")
            return

        print(f"\n📊 Encontrados {len(products)} productos")
        print("=" * 60)

        # Define trending products with realistic sales counts
        # Based on the products we saw in testing
        trending_updates = {
            "Secador Philips 2300W": 85,
            "Perfume Dior 100ml": 72,
            "Cafetera Oster": 68,
            "Plancha Remington": 54,
            "Audífonos Sony WH-1000XM5": 91,
            "Mouse Gamer RGB": 47,
            "Teclado Mecánico": 39,
            "Monitor LG 27\"": 62,
        }

        updated_count = 0

        for product in products:
            # Check if product is in trending list
            if product.name in trending_updates:
                new_sales = trending_updates[product.name]
                old_sales = product.sales_count or 0

                # Update sales_count
                product.sales_count = new_sales

                # Also update rating for better trending score
                if not product.rating or product.rating == 0:
                    # Assign realistic ratings (4.0 - 4.8)
                    if new_sales > 80:
                        product.rating = 4.8
                    elif new_sales > 60:
                        product.rating = 4.5
                    elif new_sales > 40:
                        product.rating = 4.3
                    else:
                        product.rating = 4.0

                print(f"✅ {product.name}")
                print(f"   Sales: {old_sales} → {new_sales}")
                print(f"   Rating: {product.rating}")
                updated_count += 1
            else:
                # Set random low sales for non-trending products
                if not product.sales_count or product.sales_count == 0:
                    import random
                    product.sales_count = random.randint(1, 25)
                    if not product.rating or product.rating == 0:
                        product.rating = round(random.uniform(3.5, 4.2), 1)

        # Commit changes
        await session.commit()

        print("\n" + "=" * 60)
        print(f"✅ Actualizados {updated_count} productos trending")
        print(f"✅ Total de productos procesados: {len(products)}")

        # Show top trending products
        print("\n🔥 TOP 10 PRODUCTOS EN TENDENCIA:")
        print("=" * 60)

        result = await session.execute(
            select(Product)
            .where(Product.is_active == True)
            .order_by(Product.sales_count.desc())
            .limit(10)
        )
        top_products = result.scalars().all()

        for idx, product in enumerate(top_products, 1):
            print(f"{idx}. {product.name}")
            print(f"   Sales: {product.sales_count}")
            print(f"   Rating: {product.rating}")
            print(f"   Categoría: {product.categoria}")
            print()

if __name__ == "__main__":
    print("🚀 ACTUALIZANDO PRODUCTOS TRENDING")
    print("=" * 60)
    asyncio.run(update_trending_products())
    print("\n✅ SCRIPT COMPLETADO")
