# Sistema de Rotación de Logs - MeStore

## 📋 Resumen
Sistema completo de logging con rotación automática implementado para MeStore, proporcionando observabilidad diferenciada por ambiente.

## 🔧 Configuración Implementada

### Variables de Entorno (.env)
```bash
# Niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=DEBUG

# Ambientes: development, staging, production
ENVIRONMENT=development

# Configuración de rotación
LOG_ROTATION_SIZE=10MB
LOG_ROTATION_COUNT=5
LOG_ROTATION_TIME=midnight
LOG_ROTATION_INTERVAL=1

# Estructura de archivos
LOG_DIR=logs
LOG_FILE_PREFIX=mestocker
Configuración por Ambiente
🔧 Development

Nivel de log: DEBUG y superior
Salida: Consola + Archivo
Formato: Legible y coloreado para consola
Archivo: logs/mestocker-development.log

🚀 Staging

Nivel de log: INFO y superior
Salida: Solo archivo
Formato: JSON estructurado
Archivo: logs/mestocker-staging.log

🏭 Production

Nivel de log: WARNING y superior
Salida: Solo archivo
Formato: JSON estructurado
Archivo: logs/mestocker-production.log

📁 Estructura de Archivos
logs/
├── mestocker-development.log
├── mestocker-staging.log
├── mestocker-production.log
├── README.md
└── .gitkeep
Rotación Automática

Por tamaño: Máximo 10MB por archivo
Archivos de backup: 5 archivos rotados
Por tiempo: Rotación diaria a medianoche
Formato rotado: mestocker-{env}.log.YYYY-MM-DD_HH-MM-SS

🚀 Uso en Código
Obtener Logger
pythonfrom app.core.logging_rotation import get_logger

logger = get_logger(__name__)
logger.info("Mensaje de información", extra_data="valor")
Funciones de Conveniencia
pythonfrom app.core.logging_rotation import log_info, log_warning, log_error, log_debug

log_info("Operación completada", user_id=123, operation="login")
log_warning("Recurso bajo", resource="memory", usage=85)
log_error("Error procesando", error_code=500, endpoint="/api/users")
log_debug("Debug info", step=1, data_size=100)
Configuración Manual
pythonfrom app.core.logging_rotation import setup_log_rotation

# Configurar sistema (automático en startup)
manager = setup_log_rotation()

# Obtener información de configuración
config = manager.get_environment_info()
print(f"Logging en {config['environment']} - Nivel: {config['log_level']}")
🧪 Testing y Verificación
Script de Prueba
bash# Ejecutar tests completos
python3 test_log_rotation.py

# Verificar archivos generados
ls -la logs/mestocker-*.log

# Probar diferentes ambientes
ENVIRONMENT=staging python3 test_log_rotation.py
ENVIRONMENT=production python3 test_log_rotation.py
Verificar Rotación
bash# Generar logs grandes para probar rotación
for i in {1..1000}; do
  echo "Log entry $i with lots of data $(date)" >> logs/test.log
done
📊 Integración con FastAPI
El sistema se integra automáticamente en el startup de FastAPI:
python# app/main.py
from app.core.logging_rotation import setup_log_rotation

@app.on_event("startup")
async def startup_event():
    setup_log_rotation()  # ← Configuración automática
    log_startup_info()
🔍 Monitoreo y Observabilidad
Métricas Disponibles

Ambiente actual: Detectado automáticamente
Nivel de log activo: Según configuración por ambiente
Archivos de log: Ubicación y tamaño actual
Estado de rotación: Archivos backup disponibles

Logs Estructurados (JSON)
json{
  "environment": "production",
  "level": "warning",
  "timestamp": "2025-07-20T07:11:12.813895Z",
  "event": "Recurso bajo",
  "resource": "memory",
  "usage": 85
}
🔧 Troubleshooting
Problemas Comunes
No se generan logs

Verificar permisos del directorio logs/
Comprobar configuración en .env
Verificar que setup_log_rotation() se ejecuta en startup

Archivos de log vacíos

Verificar nivel de log vs mensajes enviados
En production: solo WARNING+ aparecen
Verificar handlers configurados para el ambiente

Rotación no funciona

Verificar espacio en disco disponible
Comprobar permisos de escritura
Verificar configuración de tamaño en bytes

Comandos de Diagnóstico
bash# Verificar configuración actual
python3 -c "
from app.core.logging_rotation import log_rotation_manager
import json
print(json.dumps(log_rotation_manager.get_environment_info(), indent=2))
"

# Probar niveles de log
python3 -c "
from app.core.logging_rotation import get_logger
logger = get_logger('test')
logger.debug('Test DEBUG')
logger.info('Test INFO')  
logger.warning('Test WARNING')
logger.error('Test ERROR')
"
📈 Próximos Pasos

Integración con ELK Stack: Para centralización de logs
Métricas de observabilidad: Prometheus/Grafana
Alertas automáticas: Basadas en niveles ERROR/CRITICAL
Logs de audit: Para acciones críticas de usuarios
Compresión automática: Para archivos rotados antiguos


✅ Verificación de Implementación

✅ Rotación por tamaño (RotatingFileHandler)
✅ Rotación por tiempo (TimedRotatingFileHandler)
✅ Configuración por variables de entorno
✅ Diferenciación por ambiente (dev/staging/prod)
✅ Archivos nombrados como mestocker-{env}.log
✅ Directorio central logs/
✅ Integración con FastAPI
✅ Sistema de pruebas completo
✅ Documentación técnica

Estado: ✅ COMPLETAMENTE IMPLEMENTADO Y FUNCIONAL
