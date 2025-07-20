"""
Router para gestión de agentes de IA.

Este módulo maneja todas las operaciones relacionadas con:
- Agentes de atención al cliente
- Agentes de recomendación
- Agentes de análisis de datos
- Configuración y entrenamiento de agentes
"""

from fastapi import APIRouter

router = APIRouter(
    tags=["agents"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def agents_status():
    """
    Endpoint base del módulo de agents.

    Returns:
        dict: Estado del módulo de agents
    """
    return {"module": "agents", "status": "ok"}


@router.get("/health")
async def agents_health():
    """
    Health check específico del módulo de agents.

    Returns:
        dict: Estado de salud del módulo
    """
    return {
        "module": "agents",
        "status": "healthy",
        "services": {
            "customer_service": "operational",
            "recommendations": "operational",
            "analytics": "operational",
            "training": "operational"
        }
    }
