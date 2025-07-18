#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, '.')

# Forzar modo desarrollo desde el inicio
os.environ['ENVIRONMENT'] = 'development'

from app.core.logger import configure_logging, get_logger

def test_fixed_logging():
    print("=== 🔧 PROBANDO CONFIGURACIÓN CORREGIDA ===")
    
    # Reconfigurar completamente
    logger = configure_logging()
    test_logger = get_logger("test.fixed")
    
    print("📋 Logs en modo desarrollo (deberían ser legibles):")
    test_logger.info("Test de log legible", component="testing", status="success")
    test_logger.warning("Advertencia de prueba", level="warning")
    test_logger.error("Error simulado", error_code=500, action="testing")

if __name__ == "__main__":
    test_fixed_logging()
