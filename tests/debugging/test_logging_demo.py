#!/usr/bin/env python3
"""
Script de demostración para probar la configuración de logging estructurado.
Muestra logs en modo desarrollo y producción.
"""

import os
import sys

# Agregar el directorio actual al path para imports
sys.path.insert(0, '.')

from app.core.logger import get_logger, log_startup_info, log_shutdown_info, log_error, log_request_info
from app.core.config import settings

def test_development_logging():
    """Probar logging en modo desarrollo."""
    print("=== 🔧 MODO DESARROLLO (logs legibles y coloreados) ===")
    
    # Forzar modo desarrollo
    os.environ['ENVIRONMENT'] = 'development'
    settings.ENVIRONMENT = 'development'
    
    # Obtener logger
    logger = get_logger("test.development")
    
    # Probar diferentes niveles de log
    logger.info("Aplicación iniciando", version="0.2.6", mode="development")
    logger.warning("Advertencia de prueba", component="logger_test")
    logger.error("Error de prueba (simulado)", error_code=500)
    
    # Probar funciones específicas
    log_request_info("GET", "/api/health", 200, 45.2, user_id="test_user")
    
    print("\n")

def test_production_logging():
    """Probar logging en modo producción."""
    print("=== 🏭 MODO PRODUCCIÓN (logs en formato JSON) ===")
    
    # Forzar modo producción
    os.environ['ENVIRONMENT'] = 'production'
    settings.ENVIRONMENT = 'production'
    
    # Reconfigurar logger para producción
    from app.core.logger import configure_logging
    configure_logging()
    
    # Obtener logger
    logger = get_logger("test.production")
    
    # Probar diferentes niveles de log
    logger.info("Aplicación iniciando", version="0.2.6", mode="production")
    logger.warning("Advertencia de prueba", component="logger_test")
    logger.error("Error de prueba (simulado)", error_code=500)
    
    # Probar funciones específicas
    log_request_info("POST", "/api/users", 201, 123.5, user_id="prod_user")
    
    print("\n")

def test_error_logging():
    """Probar logging de errores con contexto."""
    print("=== ❌ PRUEBA DE LOGGING DE ERRORES ===")
    
    logger = get_logger("test.errors")
    
    try:
        # Simular error
        resultado = 1 / 0
    except Exception as e:
        log_error(
            e,
            context={
                "operation": "division",
                "input_values": {"numerator": 1, "denominator": 0},
                "user_id": "test_user"
            }
        )
    
    print("\n")

if __name__ == "__main__":
    print("🧪 PROBANDO CONFIGURACIÓN DE LOGGING ESTRUCTURADO")
    print("=" * 60)
    
    test_development_logging()
    test_production_logging()
    test_error_logging()
    
    print("✅ PRUEBAS DE LOGGING COMPLETADAS")
    print("📋 VERIFICA QUE:")
    print("   - Logs de desarrollo sean legibles y coloreados")
    print("   - Logs de producción sean JSON válido")
    print("   - Errores incluyan contexto estructurado")
