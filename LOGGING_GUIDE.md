# Guía de Logging Estructurado - MeStore API

## Configuración Implementada

El sistema utiliza **structlog** para logging estructurado con configuración automática por entorno.

### Formatos de Salida

#### Desarrollo (`ENVIRONMENT=development`)
2025-07-18T18:57:39.681424Z [info     ] Test de log legible            [test.fixed] component=testing status=success
- **Legible por humanos**
- **Coloreado** (cuando el terminal lo soporta)
- **Campos estructurados** visibles al final

#### Producción (`ENVIRONMENT=production`)
```json
{"component": "logger_test", "event": "Advertencia de prueba", "logger": "test.production", "level": "warning", "timestamp": "2025-07-18T18:56:51.238748Z"}

Formato JSON para integración con herramientas de monitoreo
Campos estructurados en JSON válido
Compatible con ELK Stack, CloudWatch, etc.

Uso en el Código
Logger Básico
pythonfrom app.core.logger import get_logger

logger = get_logger("mi.modulo")
logger.info("Operación exitosa", user_id="123", duration_ms=45.2)
logger.warning("Advertencia detectada", component="auth")
logger.error("Error procesando", error_code=500)
Logging de Requests HTTP
pythonfrom app.core.logger import log_request_info

log_request_info(
    method="POST",
    url="/api/users",
    status_code=201,
    duration_ms=123.5,
    user_id="user123"
)
Logging de Errores con Contexto
pythonfrom app.core.logger import log_error

try:
    # operación que puede fallar
    result = risky_operation()
except Exception as e:
    log_error(
        e,
        context={
            "operation": "user_creation",
            "input_data": {"email": user.email},
            "user_id": current_user.id
        }
    )
Configuración de Entorno
Variables de Entorno

ENVIRONMENT: development | production | testing

Cambiar Modo de Logging
bash# Desarrollo (logs legibles)
export ENVIRONMENT=development

# Producción (logs JSON)
export ENVIRONMENT=production
Event Handlers Configurados
Startup

Log automático al iniciar la aplicación
Incluye información de entorno y configuración

Shutdown

Log automático al cerrar la aplicación

Exception Handler Global

Captura automáticamente todas las excepciones no manejadas
Incluye contexto de request (URL, método, headers)

Ejemplos de Logs Generados
Startup
[info] MeStore API iniciando [app.startup] environment=development debug=True version=0.2.6
Request Exitoso
[info] Request completed successfully [app.requests] method=GET url=/api/health status_code=200 duration_ms=45.2
Error con Contexto
[error] Error occurred [app.error] error_type=ValueError error_message=Invalid input operation=user_creation
Integración con Herramientas de Monitoreo
Para Producción
Los logs en formato JSON son compatibles con:

ELK Stack (Elasticsearch, Logstash, Kibana)
AWS CloudWatch
Google Cloud Logging
Datadog
Splunk

Campos Estándar
Todos los logs incluyen:

timestamp: ISO 8601 timestamp
level: info, warning, error, debug
event: Mensaje descriptivo
logger: Nombre del logger/módulo

Testing
Para probar la configuración:
bashpython3 test_logging_demo.py
Este script muestra ejemplos de logs en ambos formatos.
