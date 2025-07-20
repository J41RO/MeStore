"""
Router para gestión del marketplace.

Este módulo maneja todas las operaciones relacionadas con:
- Gestión de productos
- Categorías y catálogos
- Vendedores y compradores
- Transacciones del marketplace
"""

from fastapi import APIRouter

router = APIRouter(
    tags=["marketplace"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def marketplace_status():
    """
    Endpoint base del módulo de marketplace.

    Returns:
        dict: Estado del módulo de marketplace
    """
    return {"module": "marketplace", "status": "ok"}


@router.get("/health")
async def marketplace_health():
    """
    Health check específico del módulo de marketplace.

    Returns:
        dict: Estado de salud del módulo
    """
    return {
        "module": "marketplace",
        "status": "healthy",
        "services": {
            "products": "operational",
            "categories": "operational",
            "sellers": "operational",
            "transactions": "operational"
        }
    }
