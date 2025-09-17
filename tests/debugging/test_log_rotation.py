#!/usr/bin/env python3
"""
Script de prueba para el sistema de rotación de logs.

Demuestra el funcionamiento del sistema de rotación en diferentes
ambientes y genera logs de prueba para verificar la rotación.
"""

import os
import sys
import time
from pathlib import Path

# Agregar app al path para imports
sys.path.insert(0, '.')

from app.core.logging_rotation import setup_log_rotation, get_logger, log_rotation_manager


def test_environment_detection():
    """Prueba la detección del ambiente actual."""
    print("=== 🔍 PRUEBA: DETECCIÓN DE AMBIENTE ===")
    
    config_info = log_rotation_manager.get_environment_info()
    
    print(f"📋 Ambiente detectado: {config_info['environment']}")
    print(f"📊 Nivel de log: {config_info['log_level']}")
    print(f"📁 Archivo de log: {config_info['log_file']}")
    print(f"🖥️ Consola habilitada: {config_info['console_enabled']}")
    print(f"🔄 Tamaño de rotación: {config_info['rotation_size']}")
    print(f"📦 Archivos de backup: {config_info['rotation_count']}")
    print(f"⏰ Rotación por tiempo: {config_info['rotation_time']}")
    print(f"🎛️ Handlers: {config_info['handlers']}")
    print()


def test_log_levels():
    """Prueba todos los niveles de log."""
    print("=== 🧪 PRUEBA: NIVELES DE LOG ===")
    
    logger = get_logger("test_rotation")
    
    # Generar logs de diferentes niveles
    logger.debug("Mensaje DEBUG - Solo visible en development", 
                test_type="debug", component="rotation_test")
    
    logger.info("Mensaje INFO - Visible en staging y development",
               test_type="info", component="rotation_test")
    
    logger.warning("Mensaje WARNING - Visible en todos los ambientes",
                  test_type="warning", component="rotation_test")
    
    logger.error("Mensaje ERROR - Siempre visible",
                test_type="error", component="rotation_test")
    
    logger.critical("Mensaje CRITICAL - Máxima prioridad",
                   test_type="critical", component="rotation_test")
    
    print("✅ Logs de prueba generados en todos los niveles")
    print()


def test_log_rotation():
    """Prueba la rotación de logs generando volumen."""
    print("=== 🔄 PRUEBA: ROTACIÓN DE LOGS ===")
    
    logger = get_logger("rotation_stress_test")
    
    # Generar logs para probar rotación
    print("📝 Generando logs para probar rotación...")
    
    for i in range(100):
        logger.info(
            f"Log de prueba de rotación #{i:03d}",
            iteration=i,
            test_phase="rotation",
            data_size="medium",
            extra_data="A" * 100  # Agregar datos para aumentar tamaño
        )
        
        if i % 20 == 0:
            print(f"   📊 Generados {i} logs...")
    
    print("✅ Logs de rotación generados")
    
    # Verificar archivos creados
    log_file = log_rotation_manager.get_log_file_path()
    if log_file.exists():
        size = log_file.stat().st_size
        print(f"📁 Archivo principal: {log_file.name} ({size:,} bytes)")
        
        # Buscar archivos rotados
        log_dir = log_file.parent
        pattern = f"{log_file.stem}.*"
        rotated_files = list(log_dir.glob(pattern))
        
        if len(rotated_files) > 1:
            print(f"🔄 Archivos rotados encontrados: {len(rotated_files) - 1}")
            for rotated in sorted(rotated_files):
                if rotated != log_file:
                    size = rotated.stat().st_size
                    print(f"   📦 {rotated.name} ({size:,} bytes)")
        else:
            print("ℹ️ No se detectaron archivos rotados (archivo aún no alcanzó límite)")
    
    print()


def test_different_environments():
    """Simula diferentes ambientes cambiando variables."""
    print("=== 🌍 PRUEBA: DIFERENTES AMBIENTES ===")
    
    # Guardar ambiente original
    original_env = os.environ.get('ENVIRONMENT', 'development')
    
    environments_to_test = ['development', 'staging', 'production']
    
    for env in environments_to_test:
        print(f"\n🔧 Probando ambiente: {env}")
        
        # Cambiar ambiente temporalmente
        os.environ['ENVIRONMENT'] = env
        
        # Reimportar para aplicar cambios
        import importlib
        from app.core import config
        importlib.reload(config)
        
        # Crear nuevo manager para el ambiente
        from app.core.logging_rotation import LogRotationManager
        temp_manager = LogRotationManager()
        
        # Mostrar configuración para este ambiente
        config_info = temp_manager.get_environment_info()
        print(f"   📊 Nivel: {config_info['log_level']}")
        print(f"   📁 Archivo: {Path(config_info['log_file']).name}")
        print(f"   🖥️ Consola: {config_info['console_enabled']}")
        print(f"   🎛️ Handlers: {config_info['handlers']}")
    
    # Restaurar ambiente original
    os.environ['ENVIRONMENT'] = original_env
    print(f"\n🔄 Ambiente restaurado a: {original_env}")
    print()


def show_log_files():
    """Muestra los archivos de log creados."""
    print("=== 📂 ARCHIVOS DE LOG CREADOS ===")
    
    log_dir = Path("logs")
    if log_dir.exists():
        print(f"📁 Directorio: {log_dir.absolute()}")
        
        log_files = list(log_dir.glob("*.log*"))
        if log_files:
            print("📋 Archivos encontrados:")
            for log_file in sorted(log_files):
                size = log_file.stat().st_size
                mtime = time.ctime(log_file.stat().st_mtime)
                print(f"   📄 {log_file.name}")
                print(f"      💾 Tamaño: {size:,} bytes")
                print(f"      ⏰ Modificado: {mtime}")
                print()
        else:
            print("ℹ️ No se encontraron archivos de log")
    else:
        print("❌ Directorio logs/ no existe")


def main():
    """Función principal de prueba."""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE ROTACIÓN DE LOGS")
    print("=" * 60)
    
    try:
        # Configurar sistema de rotación
        print("🔧 Configurando sistema de rotación...")
        setup_log_rotation()
        print("✅ Sistema configurado exitosamente\n")
        
        # Ejecutar pruebas
        test_environment_detection()
        test_log_levels()
        test_log_rotation()
        test_different_environments()
        show_log_files()
        
        print("🎉 ✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("🔍 Revisa los archivos en logs/ para verificar el funcionamiento")
        
    except Exception as e:
        print(f"❌ ERROR durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
