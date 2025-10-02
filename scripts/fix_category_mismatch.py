#!/usr/bin/env python3
"""
Category-Product Mismatch Fix Script
====================================

PROBLEM DETECTED:
- Categories table has English names: Electronics, Phones, Computers, Clothing, Home
- All categories show product_count = 0
- Products use different categoria values: Beauty, Books, Sports, Fashion, etc.
- Result: Categories page shows "0 productos" for all categories

SOLUTION:
1. Create missing categories that products are using
2. Update existing categories to Spanish names for Colombian market
3. Recalculate product_count for all categories
4. Standardize product categoria field values

Author: Database Architect AI
Date: 2025-10-01
"""

import asyncio
import sys
from typing import Dict, List
from sqlalchemy import text
from app.database import get_async_db

# Mapping from current product categoria values to standardized Spanish names
CATEGORY_MAPPING = {
    # Existing in categories table (needs translation to Spanish)
    "Electronics": "Electrónica",
    "Phones": "Teléfonos",
    "Computers": "Computadores",
    "Clothing": "Ropa",
    "Home": "Hogar",

    # Missing categories (needs creation)
    "Beauty": "Belleza",
    "Books": "Libros",
    "Fashion": "Moda",
    "Sports": "Deportes",
    "toys": "Juguetes",
}

# Slugs for new categories
CATEGORY_SLUGS = {
    "Electrónica": "electronica",
    "Teléfonos": "telefonos",
    "Computadores": "computadores",
    "Ropa": "ropa",
    "Hogar": "hogar",
    "Belleza": "belleza",
    "Libros": "libros",
    "Moda": "moda",
    "Deportes": "deportes",
    "Juguetes": "juguetes",
}

# Descriptions for new categories
CATEGORY_DESCRIPTIONS = {
    "Electrónica": "Productos electrónicos y accesorios tecnológicos",
    "Teléfonos": "Teléfonos móviles y smartphones",
    "Computadores": "Computadores, laptops y accesorios",
    "Ropa": "Ropa y accesorios de vestir",
    "Hogar": "Productos para el hogar y decoración",
    "Belleza": "Productos de belleza y cuidado personal",
    "Libros": "Libros y material de lectura",
    "Moda": "Moda y accesorios fashion",
    "Deportes": "Artículos deportivos y fitness",
    "Juguetes": "Juguetes y entretenimiento infantil",
}


async def get_current_state(session):
    """Get current state of categories and products"""
    print("📊 ANALYZING CURRENT STATE...")
    print("=" * 70)

    # Get categories
    result = await session.execute(text(
        "SELECT name, slug, product_count FROM categories ORDER BY name"
    ))
    categories = result.fetchall()

    print("\n🗂️  CURRENT CATEGORIES:")
    for cat in categories:
        print(f"  - {cat[0]:20} | slug: {cat[1]:20} | products: {cat[2]}")

    # Get product categoria values
    result = await session.execute(text(
        "SELECT DISTINCT categoria FROM products WHERE deleted_at IS NULL ORDER BY categoria"
    ))
    product_cats = result.fetchall()

    print("\n📦 PRODUCT CATEGORIA VALUES:")
    for cat in product_cats:
        count_result = await session.execute(
            text("SELECT COUNT(*) FROM products WHERE categoria = :cat AND deleted_at IS NULL"),
            {"cat": cat[0]}
        )
        count = count_result.scalar()
        print(f"  - {cat[0]:30} | count: {count}")

    print("\n" + "=" * 70)
    return categories, product_cats


async def create_missing_categories(session):
    """Create missing categories in the database"""
    print("\n🔧 STEP 1: CREATING MISSING CATEGORIES...")
    print("=" * 70)

    # Get existing category names
    result = await session.execute(text("SELECT name FROM categories"))
    existing = {row[0] for row in result.fetchall()}

    created_count = 0

    for old_name, new_name in CATEGORY_MAPPING.items():
        # Skip if already exists (in English or Spanish)
        if new_name in existing or old_name in existing:
            if old_name in existing and new_name not in existing:
                # Need to rename
                print(f"  ℹ️  Category '{old_name}' exists (will update to Spanish)")
            continue

        # Create new category
        slug = CATEGORY_SLUGS[new_name]
        description = CATEGORY_DESCRIPTIONS[new_name]

        await session.execute(text("""
            INSERT INTO categories (id, name, slug, description, path, level, sort_order, is_active, status, product_count, created_at, updated_at)
            VALUES (
                lower(hex(randomblob(16))),
                :name,
                :slug,
                :description,
                :path,
                0,
                :sort_order,
                1,
                'ACTIVE',
                0,
                datetime('now'),
                datetime('now')
            )
        """), {
            "name": new_name,
            "slug": slug,
            "description": description,
            "path": f"/{slug}/",
            "sort_order": created_count
        })

        print(f"  ✅ Created category: {new_name} (slug: {slug})")
        created_count += 1

    await session.commit()
    print(f"\n📊 Total categories created: {created_count}")
    print("=" * 70)


async def update_existing_categories_to_spanish(session):
    """Update existing English categories to Spanish names"""
    print("\n🔧 STEP 2: UPDATING EXISTING CATEGORIES TO SPANISH...")
    print("=" * 70)

    updates = [
        ("Electronics", "Electrónica", "electronica"),
        ("Phones", "Teléfonos", "telefonos"),
        ("Computers", "Computadores", "computadores"),
        ("Clothing", "Ropa", "ropa"),
        ("Home", "Hogar", "hogar"),
    ]

    updated_count = 0
    for old_name, new_name, new_slug in updates:
        # Check if category exists
        result = await session.execute(
            text("SELECT id FROM categories WHERE name = :old_name"),
            {"old_name": old_name}
        )
        category = result.fetchone()

        if category:
            await session.execute(text("""
                UPDATE categories
                SET name = :new_name,
                    slug = :new_slug,
                    path = :new_path,
                    description = :description,
                    updated_at = datetime('now')
                WHERE name = :old_name
            """), {
                "old_name": old_name,
                "new_name": new_name,
                "new_slug": new_slug,
                "new_path": f"/{new_slug}/",
                "description": CATEGORY_DESCRIPTIONS[new_name]
            })
            print(f"  ✅ Updated: {old_name} → {new_name} (slug: {new_slug})")
            updated_count += 1
        else:
            print(f"  ℹ️  Category '{old_name}' not found (might have been deleted)")

    await session.commit()
    print(f"\n📊 Total categories updated: {updated_count}")
    print("=" * 70)


async def standardize_product_categories(session):
    """Update products to use standardized Spanish category names"""
    print("\n🔧 STEP 3: STANDARDIZING PRODUCT CATEGORIES...")
    print("=" * 70)

    updated_count = 0

    for old_name, new_name in CATEGORY_MAPPING.items():
        # Update products with this old categoria
        result = await session.execute(text("""
            UPDATE products
            SET categoria = :new_name,
                updated_at = datetime('now')
            WHERE categoria = :old_name
              AND deleted_at IS NULL
        """), {
            "old_name": old_name,
            "new_name": new_name
        })

        rows_affected = result.rowcount
        if rows_affected > 0:
            print(f"  ✅ Updated {rows_affected} products: {old_name} → {new_name}")
            updated_count += rows_affected

    await session.commit()
    print(f"\n📊 Total products updated: {updated_count}")
    print("=" * 70)


async def recalculate_product_counts(session):
    """Recalculate product_count for all categories"""
    print("\n🔧 STEP 4: RECALCULATING PRODUCT COUNTS...")
    print("=" * 70)

    # Get all categories
    result = await session.execute(text("SELECT name FROM categories"))
    categories = result.fetchall()

    for (category_name,) in categories:
        # Count products with this categoria
        count_result = await session.execute(text("""
            SELECT COUNT(*)
            FROM products
            WHERE categoria = :cat_name
              AND deleted_at IS NULL
        """), {"cat_name": category_name})

        count = count_result.scalar()

        # Update category product_count
        await session.execute(text("""
            UPDATE categories
            SET product_count = :count,
                updated_at = datetime('now')
            WHERE name = :cat_name
        """), {
            "count": count,
            "cat_name": category_name
        })

        print(f"  ✅ {category_name:20} → {count} productos")

    await session.commit()
    print("\n📊 Product counts recalculated successfully")
    print("=" * 70)


async def verify_fix(session):
    """Verify that the fix was successful"""
    print("\n✅ VERIFICATION: CHECKING RESULTS...")
    print("=" * 70)

    # Get categories with product counts
    result = await session.execute(text("""
        SELECT name, slug, product_count
        FROM categories
        ORDER BY product_count DESC, name
    """))
    categories = result.fetchall()

    print("\n🎯 FINAL CATEGORY STATE:")
    total_products = 0
    for cat in categories:
        print(f"  - {cat[0]:20} | slug: {cat[1]:20} | products: {cat[2]}")
        total_products += cat[2]

    print(f"\n📊 SUMMARY:")
    print(f"  - Total categories: {len(categories)}")
    print(f"  - Total products assigned: {total_products}")
    print(f"  - Categories with 0 products: {sum(1 for c in categories if c[2] == 0)}")

    # Verify no products without matching category
    result = await session.execute(text("""
        SELECT DISTINCT p.categoria
        FROM products p
        LEFT JOIN categories c ON p.categoria = c.name
        WHERE p.deleted_at IS NULL
          AND c.id IS NULL
    """))
    orphaned = result.fetchall()

    if orphaned:
        print(f"\n⚠️  WARNING: Found {len(orphaned)} orphaned categoria values:")
        for (cat,) in orphaned:
            print(f"    - {cat}")
    else:
        print("\n✅ All products have matching categories")

    print("=" * 70)
    return len(categories), total_products


async def main():
    """Main execution function"""
    print("\n" + "=" * 70)
    print("🔧 CATEGORY-PRODUCT MISMATCH FIX SCRIPT")
    print("=" * 70)
    print("\nThis script will:")
    print("  1. Create missing categories (Beauty, Books, Fashion, Sports, toys)")
    print("  2. Update existing categories to Spanish names")
    print("  3. Standardize product categoria field values")
    print("  4. Recalculate product_count for all categories")
    print("\n" + "=" * 70)

    try:
        async for session in get_async_db():
            # Step 0: Get current state
            await get_current_state(session)

            # Step 1: Create missing categories
            await create_missing_categories(session)

            # Step 2: Update existing categories to Spanish
            await update_existing_categories_to_spanish(session)

            # Step 3: Standardize product categories
            await standardize_product_categories(session)

            # Step 4: Recalculate product counts
            await recalculate_product_counts(session)

            # Step 5: Verify fix
            cat_count, prod_count = await verify_fix(session)

            print("\n" + "=" * 70)
            print("✅ FIX COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            print(f"\n📊 Results: {cat_count} categories, {prod_count} products assigned")
            print("\n🔍 Next step: Verify with API:")
            print('  curl "http://192.168.1.137:8000/api/v1/categories/" | jq \'.categories[] | {name, products_count}\'')
            print("\n" + "=" * 70)

            break

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
