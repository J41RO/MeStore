#!/usr/bin/env python3
"""
Inicio de backend simplificado sin Redis para desarrollo
"""

import os
import sys

# Desactivar Redis y búsqueda para desarrollo
os.environ["DISABLE_REDIS"] = "1"
os.environ["DISABLE_SEARCH_SERVICE"] = "1"
os.environ["USE_SIMPLE_AUTH"] = "1"
os.environ["ENVIRONMENT"] = "development"

# Configurar la aplicación
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn

    print("🚀 Iniciando backend MeStore simplificado...")
    print("📍 Host: 192.168.1.137:8000")
    print("🔧 Redis: DESACTIVADO")
    print("🔍 Search Service: DESACTIVADO")
    print("🔐 Auth: SIMPLE MODE")
    print("=" * 50)

    uvicorn.run(
        "app.main:app",
        host="192.168.1.137",
        port=8000,
        reload=True,
        log_level="info"
    )