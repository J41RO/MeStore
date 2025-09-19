"""
FastAPI v1 API Router - Punto central de unificación de routers
==============================================================
Este módulo centraliza todos los routers de la API v1 bajo un único APIRouter
que será incluido en main.py con el prefijo /api/v1
"""

from fastapi import APIRouter

# Importar todos los routers desde endpoints/
from app.api.v1.endpoints.agents import router as agents_router
from app.api.v1.endpoints.alerts import router as alerts_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.categories import router as categories_router
from app.api.v1.endpoints.comisiones import router as comisiones_router
from app.api.v1.endpoints.commissions import router as commissions_router
from app.api.v1.endpoints.embeddings import router as embeddings_router
from app.api.v1.endpoints.fulfillment import router as fulfillment_router
from app.api.v1.endpoints.health import router as health_simple_router
from app.api.v1.endpoints.health_complete import router as health_complete_router
from app.api.v1.endpoints.inventory import router as inventory_router
from app.api.v1.endpoints.logs import router as logs_router
from app.api.v1.endpoints.marketplace import router as marketplace_router
from app.api.v1.endpoints.pagos import router as pagos_router
from app.api.v1.endpoints.perfil import router as perfil_router
from app.api.v1.endpoints.productos import router as productos_router
from app.api.v1.endpoints.products_bulk import router as products_bulk_router
import os
if not os.getenv("DISABLE_SEARCH_SERVICE"):
    from app.api.v1.endpoints.search import router as search_router
from app.api.v1.endpoints.vendedores import router as vendedores_router
from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.leads import router as leads_router
from app.api.v1.endpoints.system_config import router as system_config_router
from app.api.v1.endpoints.vendor_profile import router as vendor_profile_router
from app.api.v1.endpoints.payments import router as payments_router
from app.api.v1.endpoints.orders import router as orders_router

# Router principal que unifica todos los endpoints v1
api_router = APIRouter()

# STANDARDIZED ROUTER REGISTRATION - API v1
# ==================================================
# Organized by business domain with consistent patterns
# Deprecated routers removed to eliminate language conflicts

# ===== CORE BUSINESS ENDPOINTS =====
# Authentication (English standard)
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Products (Spanish - comprehensive implementation kept as primary)
api_router.include_router(productos_router, prefix="/productos", tags=["products"])

# Products (English - comprehensive implementation with advanced features)
from app.api.v1.endpoints.products import router as products_router_en
api_router.include_router(products_router_en, prefix="/products", tags=["products-en"])

# Product bulk operations (English - specialized functionality)
api_router.include_router(products_bulk_router, prefix="/products", tags=["products-bulk"])

# Orders (English standard)
api_router.include_router(orders_router, prefix="/orders", tags=["orders"])

# Commissions (English - production-ready version)
api_router.include_router(commissions_router, prefix="/commissions", tags=["commissions"])

# Payments (English - integrated payment processing)
api_router.include_router(payments_router, prefix="/payments", tags=["payments"])

# ===== VENDOR & CUSTOMER MANAGEMENT =====
# Vendor management (consolidated)
api_router.include_router(vendor_profile_router, prefix="/vendors", tags=["vendors"])

# Categories (hierarchical system)
api_router.include_router(categories_router, prefix="/categories", tags=["categories"])

# Inventory management
api_router.include_router(inventory_router, prefix="/inventory", tags=["inventory"])

# ===== MARKETPLACE & DISCOVERY =====
# Search functionality (conditional)
if not os.getenv("DISABLE_SEARCH_SERVICE"):
    api_router.include_router(search_router, prefix="/search", tags=["search"])

# Marketplace operations
api_router.include_router(marketplace_router, prefix="/marketplace", tags=["marketplace"])

# ===== ADMIN & SYSTEM =====
# Admin operations
api_router.include_router(admin_router, prefix="/admin", tags=["administration"])

# System configuration
api_router.include_router(system_config_router, prefix="/system", tags=["system"])

# Alerts and notifications
api_router.include_router(alerts_router, prefix="/alerts", tags=["alerts"])

# Leads management
api_router.include_router(leads_router, prefix="/leads", tags=["leads"])

# ===== UTILITY & MONITORING =====
# Health checks
api_router.include_router(health_simple_router, prefix="/health", tags=["health"])
api_router.include_router(health_complete_router, prefix="/health/complete", tags=["health"])

# System logging
api_router.include_router(logs_router, prefix="/logs", tags=["logging"])

# ===== ADVANCED FEATURES =====
# AI/ML features
api_router.include_router(embeddings_router, prefix="/embeddings", tags=["ai-ml"])
api_router.include_router(agents_router, prefix="/agents", tags=["ai-agents"])

# Fulfillment operations
api_router.include_router(fulfillment_router, prefix="/fulfillment", tags=["fulfillment"])

# Legacy profile endpoint (to be migrated to /vendors)
api_router.include_router(perfil_router, prefix="/profile", tags=["profile-legacy"])

# ===== TEMPORARY VENDOR REGISTRATION TESTING =====
# Adding vendedores router back for testing purposes
api_router.include_router(vendedores_router, prefix="/vendedores", tags=["vendedores-testing"])

# ==================================================
# DEPRECATED ROUTERS (partially restored for testing):
# - comisiones_router (Spanish) -> Use /commissions
# - pagos_router (Spanish) -> Use /payments
# - vendedores_router (Spanish) -> Use /vendors (but also available for testing)
# ==================================================