#!/usr/bin/env python3
"""
Script de demostración de loguru para desarrollo.
Muestra la diferencia entre logs en development vs production.
"""

import os
import sys
sys.path.append('.')

def test_development_logs():
    """Prueba logs en modo development (loguru activo)."""
    print("\n🔧 MODO DEVELOPMENT - LOGURU ACTIVO:")
    print("=" * 50)
    
    # Forzar environment development
    os.environ['ENVIRONMENT'] = 'development'
    
    # Limpiar caché y recargar
    modules_to_clear = [mod for mod in sys.modules.keys() if 'app.core' in mod]
    for mod in modules_to_clear:
        if mod in sys.modules:
            del sys.modules[mod]
    
    from app.core.logger import get_logger
    
    # Crear loggers de prueba
    api_logger = get_logger('api.test')
    db_logger = get_logger('database.test')
    auth_logger = get_logger('auth.test')
    
    # Diferentes tipos de logs
    api_logger.info('🚀 API iniciada correctamente')
    api_logger.debug('🔍 Procesando request GET /api/products')
    db_logger.info('💾 Conectando a base de datos PostgreSQL')
    db_logger.warning('⚠️ Pool de conexiones al 80% de capacidad')
    auth_logger.info('👤 Usuario autenticado: jairo@mestore.com')
    auth_logger.error('❌ Intento de login fallido: credenciales inválidas')
    
    print("=" * 50)

def test_production_logs():
    """Prueba logs en modo production (structlog JSON)."""
    print("\n🏭 MODO PRODUCTION - STRUCTLOG JSON:")
    print("=" * 50)
    
    # Forzar environment production
    os.environ['ENVIRONMENT'] = 'production'
    
    # Limpiar caché y recargar
    modules_to_clear = [mod for mod in sys.modules.keys() if 'app.core' in mod]
    for mod in modules_to_clear:
        if mod in sys.modules:
            del sys.modules[mod]
    
    from app.core.logger import get_logger
    
    # Crear logger de prueba
    prod_logger = get_logger('production.test')
    
    # Logs en formato JSON para production
    prod_logger.info('Sistema iniciado en producción')
    prod_logger.error('Error crítico en producción', 
                     error_code='ERR_001', 
                     user_id='12345',
                     ip_address='192.168.1.100')
    
    print("=" * 50)

if __name__ == '__main__':
    print("🎯 DEMOSTRACIÓN DE LOGURU vs STRUCTLOG")
    print("=====================================")
    
    # Mostrar ambos modos
    test_development_logs()
    test_production_logs()
    
    print("\n✅ DEMOSTRACIÓN COMPLETADA")
    print("\n📋 RESUMEN:")
    print("• Development: Logs coloridos y legibles con loguru")
    print("• Production: Logs JSON estructurados con structlog")
    print("• Sin conflictos: Ambos sistemas coexisten perfectamente")
