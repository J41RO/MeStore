"""
FastAPI v1 API Router - Punto central de unificación de routers
==============================================================
Este módulo centraliza todos los routers de la API v1 bajo un único APIRouter
que será incluido en main.py con el prefijo /api/v1
"""

from fastapi import APIRouter

# Importar todos los routers desde endpoints/
from app.api.v1.endpoints.agents import router as agents_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.embeddings import router as embeddings_router
from app.api.v1.endpoints.fulfillment import router as fulfillment_router
from app.api.v1.endpoints.inventory import router as inventory_router
from app.api.v1.endpoints.health import router as health_simple_router
from app.api.v1.endpoints.health_complete import router as health_complete_router
from app.api.v1.endpoints.logs import router as logs_router
from app.api.v1.endpoints.marketplace import router as marketplace_router
from app.api.v1.endpoints.productos import router as productos_router
from app.api.v1.endpoints.vendedores import router as vendedores_router
from app.api.v1.endpoints.comisiones import router as comisiones_router

# Router principal que unifica todos los endpoints v1
api_router = APIRouter()

# Registrar todos los routers con sus prefijos específicos
api_router.include_router(
    health_simple_router, prefix="/health", tags=["health-simple"]
)

api_router.include_router(
    health_complete_router, prefix="/health-complete", tags=["health-complete"]
)

api_router.include_router(logs_router, prefix="/logs", tags=["logs"])

api_router.include_router(embeddings_router, prefix="/embeddings", tags=["embeddings"])

api_router.include_router(
    fulfillment_router, prefix="/fulfillment", tags=["fulfillment"]
)

api_router.include_router(
    marketplace_router, prefix="/marketplace", tags=["marketplace"]
)

api_router.include_router(agents_router, prefix="/agents", tags=["agents"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(vendedores_router, tags=["vendedores"])
api_router.include_router(comisiones_router, tags=["comisiones"])
api_router.include_router(productos_router, prefix="/productos", tags=["productos"])
api_router.include_router(inventory_router, prefix="/inventario", tags=["inventory"])