"""
Router para gestión del marketplace.

Este módulo maneja todas las operaciones relacionadas con:
- Gestión de productos
- Categorías y catálogos
- Vendedores y compradores
- Transacciones del marketplace
"""

from fastapi import APIRouter
from fastapi import Depends
from app.core.auth import get_current_user, require_user_type

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



@router.get("/protected")
async def protected_endpoint(current_user: dict = Depends(get_current_user)):
    """
    Endpoint protegido que requiere autenticación.

    Returns:
        dict: Datos del usuario autenticado
    """
    return {
        "message": "Access granted to protected marketplace endpoint",
        "user": current_user
    }


@router.get("/sellers-only")
async def sellers_only_endpoint(
    current_user: dict = Depends(require_user_type("VENDEDOR"))
):
    """
    Endpoint solo para vendedores.

    Returns:
        dict: Funcionalidad específica para vendedores
    """
    return {
        "message": "Welcome seller!",
        "user": current_user,
        "features": ["manage_products", "view_sales", "analytics"]
    }
    }