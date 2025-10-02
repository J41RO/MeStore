#!/usr/bin/env python3
"""
Script de seed para productos de prueba - MeStore
Crea productos de ejemplo para testing del catálogo público.

Uso:
    python scripts/seed_products.py

Características:
    - Crea 15-20 productos con diversidad de categorías y precios
    - Verifica/crea vendedor de prueba si no existe
    - Idempotente: puede ejecutarse múltiples veces sin duplicar
    - Status APPROVED para catálogo público
    - Imágenes placeholder
"""

import asyncio
import sys
import os
from decimal import Decimal
from typing import List, Dict, Any
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.product import Product, ProductStatus
from app.models.user import User, UserType
from app.services.auth_service import AuthService
from app.core.types import generate_uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductSeeder:
    """Seeder for creating test products."""

    def __init__(self):
        self.auth_service = AuthService()
        self.vendor_email = "vendor@mestore.com"
        self.vendor_password = "Vendor123456"

    async def get_or_create_vendor(self, db: AsyncSession) -> User:
        """Get existing vendor or create new one for products."""
        try:
            # Check if vendor exists
            result = await db.execute(
                select(User).where(User.email == self.vendor_email)
            )
            vendor = result.scalar_one_or_none()

            if vendor:
                logger.info(f"Found existing vendor: {self.vendor_email}")
                return vendor

            # Create new vendor
            logger.info(f"Creating new vendor: {self.vendor_email}")
            vendor = await self.auth_service.create_user(
                db=db,
                email=self.vendor_email,
                password=self.vendor_password,
                user_type=UserType.VENDOR,
                is_active=True,
                nombre="Test",
                apellido="Vendor",
                business_name="Test Store"
            )

            logger.info(f"Vendor created successfully: {vendor.id}")
            return vendor

        except Exception as e:
            logger.error(f"Error getting/creating vendor: {e}")
            raise

    def get_product_data(self, vendor_id: str) -> List[Dict[str, Any]]:
        """Get list of product data to seed."""
        return [
            # Electronics
            {
                "sku": "IPHONE13-256-BLU",
                "name": "iPhone 13 Pro 256GB Azul",
                "description": "iPhone 13 Pro en color azul con 256GB de almacenamiento. Triple cámara, pantalla Super Retina XDR de 6.1 pulgadas, chip A15 Bionic.",
                "precio_venta": Decimal("2500000"),
                "precio_costo": Decimal("2100000"),
                "comision_mestocker": Decimal("250000"),
                "categoria": "Electronics",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("0.240"),
                "vendedor_id": vendor_id
            },
            {
                "sku": "LAPTOP-HP-15-I7",
                "name": "Laptop HP Pavilion 15 Intel i7",
                "description": "Laptop HP Pavilion 15.6 pulgadas, Intel Core i7 11th Gen, 16GB RAM, 512GB SSD, Windows 11.",
                "precio_venta": Decimal("1850000"),
                "precio_costo": Decimal("1600000"),
                "comision_mestocker": Decimal("185000"),
                "categoria": "Electronics",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("1.750"),
                "vendedor_id": vendor_id
            },
            {
                "sku": "AIRPODS-PRO-2",
                "name": "AirPods Pro 2da Generación",
                "description": "AirPods Pro con cancelación activa de ruido, audio espacial, resistente al agua.",
                "precio_venta": Decimal("890000"),
                "precio_costo": Decimal("750000"),
                "comision_mestocker": Decimal("89000"),
                "categoria": "Electronics",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("0.050"),
                "vendedor_id": vendor_id
            },
            {
                "sku": "TV-SAMSUNG-55-4K",
                "name": "Smart TV Samsung 55 pulgadas 4K",
                "description": "Smart TV Samsung Crystal UHD 55 pulgadas, resolución 4K, HDR, Tizen OS.",
                "precio_venta": Decimal("1650000"),
                "precio_costo": Decimal("1400000"),
                "comision_mestocker": Decimal("165000"),
                "categoria": "Electronics",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("15.500"),
                "vendedor_id": vendor_id
            },

            # Fashion
            {
                "sku": "POLO-LACOSTE-M-BLU",
                "name": "Camisa Polo Lacoste Hombre Azul M",
                "description": "Camisa polo 100% algodón Lacoste, color azul marino, talla M, corte clásico.",
                "precio_venta": Decimal("185000"),
                "precio_costo": Decimal("130000"),
                "comision_mestocker": Decimal("18500"),
                "categoria": "Fashion",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("0.250"),
                "vendedor_id": vendor_id
            },
            {
                "sku": "JEANS-LEVIS-501-32",
                "name": "Jeans Levi's 501 Original Fit Talla 32",
                "description": "Jeans Levi's 501 Original Fit, talla 32, color índigo, corte clásico.",
                "precio_venta": Decimal("220000"),
                "precio_costo": Decimal("160000"),
                "comision_mestocker": Decimal("22000"),
                "categoria": "Fashion",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("0.600"),
                "vendedor_id": vendor_id
            },
            {
                "sku": "ZAPATILLAS-NIKE-AIR-42",
                "name": "Zapatillas Nike Air Max 270 Talla 42",
                "description": "Zapatillas Nike Air Max 270, talla 42, color negro/blanco, tecnología Air.",
                "precio_venta": Decimal("420000"),
                "precio_costo": Decimal("320000"),
                "comision_mestocker": Decimal("42000"),
                "categoria": "Fashion",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("0.800"),
                "vendedor_id": vendor_id
            },
            {
                "sku": "VESTIDO-ZARA-M-NEG",
                "name": "Vestido Zara Negro Elegante Talla M",
                "description": "Vestido negro elegante Zara, talla M, perfecto para ocasiones especiales.",
                "precio_venta": Decimal("150000"),
                "precio_costo": Decimal("95000"),
                "comision_mestocker": Decimal("15000"),
                "categoria": "Fashion",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("0.350"),
                "vendedor_id": vendor_id
            },

            # Home & Garden
            {
                "sku": "COLCHON-SPRING-DOBLE",
                "name": "Colchón Spring Doble 140x190",
                "description": "Colchón Spring doble, 140x190 cm, espuma de alta densidad, garantía 5 años.",
                "precio_venta": Decimal("850000"),
                "precio_costo": Decimal("650000"),
                "comision_mestocker": Decimal("85000"),
                "categoria": "Home",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("25.000"),
                "vendedor_id": vendor_id
            },
            {
                "sku": "JUEGO-OLLAS-12PZ",
                "name": "Juego de Ollas 12 Piezas Acero Inoxidable",
                "description": "Set completo de 12 piezas en acero inoxidable, apto para todas las estufas.",
                "precio_venta": Decimal("280000"),
                "precio_costo": Decimal("200000"),
                "comision_mestocker": Decimal("28000"),
                "categoria": "Home",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("6.500"),
                "vendedor_id": vendor_id
            },
            {
                "sku": "LAMPARA-LED-SALA",
                "name": "Lámpara LED Moderna para Sala",
                "description": "Lámpara de techo LED moderna, diseño minimalista, luz regulable.",
                "precio_venta": Decimal("195000"),
                "precio_costo": Decimal("140000"),
                "comision_mestocker": Decimal("19500"),
                "categoria": "Home",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("2.300"),
                "vendedor_id": vendor_id
            },
            {
                "sku": "ASPIRADORA-ROBOT-XR10",
                "name": "Aspiradora Robot Inteligente XR10",
                "description": "Aspiradora robot con mapeo inteligente, control por app, batería de larga duración.",
                "precio_venta": Decimal("980000"),
                "precio_costo": Decimal("750000"),
                "comision_mestocker": Decimal("98000"),
                "categoria": "Home",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("3.200"),
                "vendedor_id": vendor_id
            },

            # Sports & Outdoors
            {
                "sku": "BICICLETA-MTB-27",
                "name": "Bicicleta Montaña MTB Aro 27.5",
                "description": "Bicicleta de montaña aro 27.5, 21 velocidades, frenos de disco, suspensión.",
                "precio_venta": Decimal("1200000"),
                "precio_costo": Decimal("950000"),
                "comision_mestocker": Decimal("120000"),
                "categoria": "Sports",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("14.500"),
                "vendedor_id": vendor_id
            },
            {
                "sku": "PESAS-SET-20KG",
                "name": "Set de Pesas 20kg con Mancuernas",
                "description": "Set completo de pesas 20kg, incluye mancuernas ajustables y discos.",
                "precio_venta": Decimal("320000"),
                "precio_costo": Decimal("230000"),
                "comision_mestocker": Decimal("32000"),
                "categoria": "Sports",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("20.000"),
                "vendedor_id": vendor_id
            },
            {
                "sku": "YOGA-MAT-PRO",
                "name": "Tapete Yoga Profesional Antideslizante",
                "description": "Mat de yoga profesional, 6mm grosor, antideslizante, incluye correa.",
                "precio_venta": Decimal("85000"),
                "precio_costo": Decimal("55000"),
                "comision_mestocker": Decimal("8500"),
                "categoria": "Sports",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("1.200"),
                "vendedor_id": vendor_id
            },

            # Books & Media
            {
                "sku": "LIBRO-SAPIENS",
                "name": "Libro: Sapiens de Yuval Noah Harari",
                "description": "Best-seller internacional, tapa dura, español, 496 páginas.",
                "precio_venta": Decimal("89000"),
                "precio_costo": Decimal("60000"),
                "comision_mestocker": Decimal("8900"),
                "categoria": "Books",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("0.800"),
                "vendedor_id": vendor_id
            },
            {
                "sku": "AUDIF-SONY-WH1000",
                "name": "Audífonos Sony WH-1000XM5 Cancelación Ruido",
                "description": "Audífonos premium con mejor cancelación de ruido del mercado, 30h batería.",
                "precio_venta": Decimal("1180000"),
                "precio_costo": Decimal("950000"),
                "comision_mestocker": Decimal("118000"),
                "categoria": "Electronics",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("0.250"),
                "vendedor_id": vendor_id
            },

            # Beauty & Personal Care
            {
                "sku": "PERFUME-DIOR-100ML",
                "name": "Perfume Dior Sauvage 100ml",
                "description": "Perfume Dior Sauvage eau de toilette 100ml, fragancia masculina.",
                "precio_venta": Decimal("450000"),
                "precio_costo": Decimal("340000"),
                "comision_mestocker": Decimal("45000"),
                "categoria": "Beauty",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("0.350"),
                "vendedor_id": vendor_id
            },
            {
                "sku": "SECADOR-PHILIPS-2300W",
                "name": "Secador de Pelo Philips 2300W Profesional",
                "description": "Secador profesional 2300W, tecnología iónica, 3 velocidades.",
                "precio_venta": Decimal("185000"),
                "precio_costo": Decimal("130000"),
                "comision_mestocker": Decimal("18500"),
                "categoria": "Beauty",
                "status": ProductStatus.APPROVED,
                "peso": Decimal("0.650"),
                "vendedor_id": vendor_id
            }
        ]

    async def check_product_exists(self, db: AsyncSession, sku: str) -> bool:
        """Check if product with SKU already exists."""
        result = await db.execute(
            select(Product).where(Product.sku == sku)
        )
        return result.scalar_one_or_none() is not None

    async def create_product(self, db: AsyncSession, product_data: Dict[str, Any]) -> Product:
        """Create a single product."""
        try:
            # Check if already exists
            if await self.check_product_exists(db, product_data['sku']):
                logger.info(f"Product {product_data['sku']} already exists, skipping")
                return None

            # Create product
            product = Product(**product_data)
            db.add(product)

            logger.info(f"Created product: {product.sku} - {product.name}")
            return product

        except Exception as e:
            logger.error(f"Error creating product {product_data.get('sku')}: {e}")
            raise

    async def seed_products(self, db: AsyncSession) -> Dict[str, int]:
        """Seed all products and return statistics."""
        stats = {
            "created": 0,
            "skipped": 0,
            "errors": 0
        }

        try:
            # Get or create vendor
            vendor = await self.get_or_create_vendor(db)

            # Get product data
            products_data = self.get_product_data(vendor.id)
            logger.info(f"Seeding {len(products_data)} products...")

            # Create each product
            for product_data in products_data:
                try:
                    product = await self.create_product(db, product_data)
                    if product:
                        stats["created"] += 1
                    else:
                        stats["skipped"] += 1
                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Error with product {product_data.get('sku')}: {e}")

            # Commit all changes
            await db.commit()
            logger.info("All products committed successfully")

        except Exception as e:
            logger.error(f"Error during seeding: {e}")
            await db.rollback()
            raise

        return stats

    async def get_product_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """Get statistics about products in database."""
        try:
            # Total products
            total_result = await db.execute(select(func.count(Product.id)))
            total = total_result.scalar()

            # Products by status
            approved_result = await db.execute(
                select(func.count(Product.id)).where(Product.status == ProductStatus.APPROVED)
            )
            approved = approved_result.scalar()

            # Products by category
            category_result = await db.execute(
                select(Product.categoria, func.count(Product.id))
                .group_by(Product.categoria)
            )
            by_category = dict(category_result.all())

            return {
                "total": total,
                "approved": approved,
                "by_category": by_category
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}


async def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("Starting MeStore Product Seeder")
    logger.info("=" * 60)

    seeder = ProductSeeder()

    async with AsyncSessionLocal() as db:
        try:
            # Get initial stats
            logger.info("\nInitial database state:")
            initial_stats = await seeder.get_product_stats(db)
            logger.info(f"Total products: {initial_stats.get('total', 0)}")
            logger.info(f"Approved products: {initial_stats.get('approved', 0)}")

            # Seed products
            logger.info("\n" + "=" * 60)
            logger.info("Seeding products...")
            logger.info("=" * 60)
            stats = await seeder.seed_products(db)

            # Get final stats
            logger.info("\n" + "=" * 60)
            logger.info("Seeding completed!")
            logger.info("=" * 60)
            logger.info(f"\nResults:")
            logger.info(f"  - Created: {stats['created']} products")
            logger.info(f"  - Skipped: {stats['skipped']} products (already exist)")
            logger.info(f"  - Errors: {stats['errors']} products")

            final_stats = await seeder.get_product_stats(db)
            logger.info(f"\nFinal database state:")
            logger.info(f"  - Total products: {final_stats.get('total', 0)}")
            logger.info(f"  - Approved products: {final_stats.get('approved', 0)}")
            logger.info(f"\nProducts by category:")
            for category, count in final_stats.get('by_category', {}).items():
                logger.info(f"    {category}: {count}")

            logger.info("\n" + "=" * 60)
            logger.info("Seed process completed successfully!")
            logger.info("=" * 60)
            logger.info(f"\nVendor credentials:")
            logger.info(f"  Email: {seeder.vendor_email}")
            logger.info(f"  Password: {seeder.vendor_password}")
            logger.info("\nYou can now view the products in the public catalog")

        except Exception as e:
            logger.error(f"\n{'=' * 60}")
            logger.error(f"SEEDING FAILED: {e}")
            logger.error(f"{'=' * 60}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
