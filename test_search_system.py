#!/usr/bin/env python3
"""
Test script para verificar el sistema de búsqueda avanzada.
"""

import asyncio
import json
import logging
from pathlib import Path
import sys

# Agregar root al path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.chroma_service import chroma_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_chroma_service():
    """Test básico de ChromaDB service."""
    try:
        logger.info("🧪 Testing ChromaDB service...")

        # Inicializar
        await chroma_service.initialize()

        # Obtener estadísticas
        stats = await chroma_service.get_collection_stats()
        logger.info(f"✅ ChromaDB stats: {json.dumps(stats, indent=2)}")

        # Test de embedding
        test_text = ["laptop gaming", "celular smartphone", "auriculares bluetooth"]
        embeddings = await chroma_service.generate_embeddings(test_text)

        logger.info(f"✅ Generated {len(embeddings)} embeddings")
        logger.info(f"✅ Embedding dimension: {len(embeddings[0]) if embeddings else 0}")

        return True

    except Exception as e:
        logger.error(f"❌ ChromaDB test failed: {e}")
        return False


async def test_product_embedding():
    """Test embedding de producto."""
    try:
        logger.info("🧪 Testing product embedding...")

        # Datos de producto de prueba
        test_product = {
            "id": "test-product-123",
            "name": "Laptop Gaming ASUS ROG",
            "description": "Potente laptop para gaming con RTX 4060",
            "categoria": "Electronics",
            "precio_venta": 1899.99,
            "tags": ["gaming", "laptop", "asus", "rtx"],
            "status": "DISPONIBLE",
            "tiene_stock": True
        }

        # Agregar embedding
        success = await chroma_service.add_product_embedding(
            test_product["id"],
            test_product
        )

        if success:
            logger.info("✅ Product embedding added successfully")

            # Test búsqueda
            results = await chroma_service.search_products(
                query="computadora para juegos",
                max_results=5
            )

            logger.info(f"✅ Search results: {len(results)} products found")
            for result in results:
                logger.info(f"  - {result['product_id']}: {result['similarity_score']:.3f}")

            return True
        else:
            logger.error("❌ Failed to add product embedding")
            return False

    except Exception as e:
        logger.error(f"❌ Product embedding test failed: {e}")
        return False


async def main():
    """Ejecutar todos los tests."""
    logger.info("🚀 Iniciando tests del sistema de búsqueda...")

    tests = [
        test_chroma_service,
        test_product_embedding
    ]

    results = []
    for test in tests:
        result = await test()
        results.append(result)

    passed = sum(results)
    total = len(results)

    logger.info(f"📊 Tests completados: {passed}/{total} exitosos")

    if passed == total:
        logger.info("🎉 Todos los tests pasaron!")
        return 0
    else:
        logger.error("❌ Algunos tests fallaron")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)