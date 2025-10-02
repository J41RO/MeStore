# Product Seeder Script - MeStore

## Overview

Script for seeding test products into the MeStore database. Creates a diverse catalog of 19 APPROVED products across multiple categories for testing the public catalog functionality.

## Location

```
/home/admin-jairo/MeStore/scripts/seed_products.py
```

## Features

### Product Diversity
- **19 Products** with APPROVED status (ready for public catalog)
- **7 Categories**: Electronics, Fashion, Home, Sports, Books, Beauty
- **Price Range**: $20,000 - $2,500,000 COP
- **Weight Range**: 0.05kg - 25kg (realistic shipping calculations)

### Technical Features
- **Idempotent Execution**: Can run multiple times without creating duplicates
- **Async SQLAlchemy**: Full async/await implementation
- **Automatic Vendor Creation**: Creates test vendor if not exists
- **Comprehensive Logging**: Detailed progress and statistics
- **Transaction Safety**: Proper commit/rollback handling

## Usage

### Basic Execution

```bash
cd /home/admin-jairo/MeStore
python scripts/seed_products.py
```

### Expected Output

```
============================================================
Starting MeStore Product Seeder
============================================================

Initial database state:
Total products: 0
Approved products: 0

============================================================
Seeding products...
============================================================
Creating new vendor: vendor@mestore.com
Vendor created successfully: f17079cc-dc33-43dd-8a60-8b2962a2e837
Seeding 19 products...
Created product: IPHONE13-256-BLU - iPhone 13 Pro 256GB Azul
Created product: LAPTOP-HP-15-I7 - Laptop HP Pavilion 15 Intel i7
...

Results:
  - Created: 19 products
  - Skipped: 0 products (already exist)
  - Errors: 0 products

Final database state:
  - Total products: 19
  - Approved products: 19

Products by category:
    Electronics: 5
    Fashion: 4
    Home: 4
    Sports: 3
    Beauty: 2
    Books: 1

============================================================
Seed process completed successfully!
============================================================

Vendor credentials:
  Email: vendor@mestore.com
  Password: Vendor123456
```

## Created Vendor

The script creates a test vendor account:

- **Email**: `vendor@mestore.com`
- **Password**: `Vendor123456`
- **Type**: VENDOR
- **Status**: ACTIVE
- **Business Name**: Test Store

## Product Categories & Examples

### Electronics (5 products)
- iPhone 13 Pro 256GB - $2,500,000
- Laptop HP Pavilion 15 i7 - $1,850,000
- AirPods Pro 2nd Gen - $890,000
- Smart TV Samsung 55" 4K - $1,650,000
- Sony WH-1000XM5 Headphones - $1,180,000

### Fashion (4 products)
- Lacoste Polo Shirt - $185,000
- Levi's 501 Jeans - $220,000
- Nike Air Max 270 - $420,000
- Zara Black Dress - $150,000

### Home (4 products)
- Spring Double Mattress - $850,000
- 12-Piece Cookware Set - $280,000
- LED Modern Lamp - $195,000
- Robot Vacuum XR10 - $980,000

### Sports (3 products)
- Mountain Bike MTB 27.5 - $1,200,000
- 20kg Weight Set - $320,000
- Professional Yoga Mat - $85,000

### Beauty (2 products)
- Dior Sauvage 100ml - $450,000
- Philips Hair Dryer 2300W - $185,000

### Books (1 product)
- Sapiens by Yuval Noah Harari - $89,000

## Product Data Structure

Each product includes:

```python
{
    "sku": "UNIQUE-SKU-CODE",           # Unique identifier
    "name": "Product Name",              # Display name
    "description": "Detailed description...",
    "precio_venta": Decimal("price"),   # Sale price (COP)
    "precio_costo": Decimal("cost"),    # Cost price (COP)
    "comision_mestocker": Decimal("commission"),
    "categoria": "Category",             # Electronics, Fashion, etc.
    "status": ProductStatus.APPROVED,    # Ready for catalog
    "peso": Decimal("weight"),          # Weight in kg
    "vendedor_id": "vendor_uuid"        # Assigned vendor
}
```

## Idempotent Behavior

The script checks for existing products by SKU before creating:

```python
async def check_product_exists(self, db: AsyncSession, sku: str) -> bool:
    """Check if product with SKU already exists."""
    result = await db.execute(
        select(Product).where(Product.sku == sku)
    )
    return result.scalar_one_or_none() is not None
```

**Running twice:**
- First run: Creates 19 products
- Second run: Skips 19 products (already exist)

## Verification Commands

### Check total products
```bash
python -c "
import asyncio
from app.database import AsyncSessionLocal
from app.models.product import Product, ProductStatus
from sqlalchemy import select, func

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(func.count(Product.id)))
        print(f'Total: {result.scalar()}')

        result = await db.execute(
            select(func.count(Product.id)).where(Product.status == ProductStatus.APPROVED)
        )
        print(f'Approved: {result.scalar()}')

asyncio.run(check())
"
```

### View sample products
```bash
python -c "
import asyncio
from app.database import AsyncSessionLocal
from app.models.product import Product, ProductStatus
from sqlalchemy import select

async def show():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Product).where(Product.status == ProductStatus.APPROVED).limit(5)
        )
        for p in result.scalars():
            print(f'{p.sku}: {p.name} - \${p.precio_venta:,.0f}')

asyncio.run(show())
"
```

## Integration with Public Catalog

These products are APPROVED and will appear in:

1. **Public Catalog** (`/productos`)
   - All 19 products visible
   - Category filters working
   - Price range filters functional

2. **Product Details** (`/productos/{id}`)
   - Individual product pages
   - Full product information

3. **Search & Filters**
   - Search by name/description
   - Filter by category
   - Filter by price range

## Testing Scenarios

### Category Filtering
```
Electronics → 5 products
Fashion → 4 products
Home → 4 products
Sports → 3 products
Beauty → 2 products
Books → 1 product
```

### Price Range Testing
```
Under $100,000 → 1 product (Yoga Mat)
$100,000 - $500,000 → 9 products
$500,000 - $1,000,000 → 3 products
Over $1,000,000 → 6 products
```

### Vendor Products
All 19 products assigned to `vendor@mestore.com`

## Troubleshooting

### Products not showing in catalog?

Check product status:
```python
from app.models.product import ProductStatus
# Products must be APPROVED to show in public catalog
```

### Vendor not found?

The script auto-creates vendor. Check:
```bash
python -c "
import asyncio
from app.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == 'vendor@mestore.com')
        )
        vendor = result.scalar_one_or_none()
        print(f'Vendor exists: {vendor is not None}')
        if vendor:
            print(f'ID: {vendor.id}')
            print(f'Type: {vendor.user_type}')

asyncio.run(check())
"
```

### Duplicate SKU errors?

Script is idempotent - it skips existing SKUs. If you get errors:
1. Check database for corrupt data
2. Review logs for specific SKU causing issue
3. Consider clearing database and re-seeding

## File Structure

```
scripts/
├── seed_products.py           # Main seeder script
├── README_SEED_PRODUCTS.md    # This documentation
└── create_test_user.py        # Reference implementation
```

## Dependencies

- Python 3.10+
- SQLAlchemy 2.0+ (async)
- FastAPI models (Product, User)
- AsyncPG (PostgreSQL) or aiosqlite (SQLite)

## Author

Backend Framework AI - MeStore Development Team

## Version

1.0.0 - Initial release (2025-10-01)

## Related Documentation

- `/home/admin-jairo/MeStore/CLAUDE.md` - Project overview
- `/home/admin-jairo/MeStore/app/models/product.py` - Product model
- `/home/admin-jairo/MeStore/app/models/user.py` - User model
