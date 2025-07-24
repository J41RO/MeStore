# Ejemplo de Logs del Middleware de Logging

## Logs de Startup del Sistema
```json
{
  "environment": "testing",
  "debug": true,
  "database_url": "postgresql+psycopg://postgres:postgres@***",
  "redis_url": "redis://localhost:6379/0",
  "version": "0.2.6",
  "event": "MeStore API iniciando",
  "logger": "app.startup",
  "level": "info",
  "timestamp": "2025-07-19T05:38:49.441700Z"
}
Ejemplo de Request Logging (Formato esperado)
Request Received (event=request_started)
json{
  "method": "GET",
  "path": "/",
  "client_ip": "127.0.0.1",
  "user_agent": "curl/7.81.0",
  "event": "Request received",
  "logger": "app.middleware.logging",
  "level": "info",
  "timestamp": "2025-07-19T05:38:50.123456Z"
}
Request Completed (event=request_completed)
json{
  "method": "GET",
  "path": "/",
  "client_ip": "127.0.0.1",
  "user_agent": "curl/7.81.0",
  "status_code": 200,
  "duration_ms": 15.23,
  "event": "Request completed",
  "logger": "app.middleware.logging",
  "level": "info",
  "timestamp": "2025-07-19T05:38:50.138686Z"
}
Request con Usuario Autenticado
json{
  "method": "POST",
  "path": "/api/v1/users",
  "client_ip": "192.168.1.100",
  "user_agent": "MeStore-Frontend/1.0.0",
  "user": "admin@mestore.com",
  "status_code": 201,
  "duration_ms": 87.45,
  "event": "Request completed",
  "logger": "app.middleware.logging",
  "level": "info",
  "timestamp": "2025-07-19T05:38:51.123456Z"
}
Request con Error (event=request_error)
json{
  "method": "GET",
  "path": "/nonexistent-endpoint",
  "client_ip": "127.0.0.1",
  "user_agent": "curl/7.81.0",
  "duration_ms": 5.12,
  "error_type": "HTTPException",
  "error_message": "404: Not Found",
  "event": "Request failed with exception",
  "logger": "app.middleware.logging",
  "level": "error",
  "timestamp": "2025-07-19T05:38:52.123456Z"
}
Headers Agregados por el Middleware
El middleware agrega automáticamente el header:

X-Process-Time: Duración del procesamiento en milisegundos

Funcionalidades Implementadas
✅ Captura automática de todas las requests HTTP
✅ Logging estructurado con structlog en formato JSON
✅ Medición de performance con duración en milisegundos
✅ Extracción de IP real considerando proxies (X-Forwarded-For, X-Real-IP)
✅ Detección de usuario autenticado desde request.state.user
✅ Manejo de errores con logging detallado de excepciones
✅ Headers de respuesta con tiempo de procesamiento
✅ Logging de contexto completo (método, path, IP, User-Agent, query params)
