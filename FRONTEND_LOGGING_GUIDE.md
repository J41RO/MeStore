# 🔧 Sistema de Logging Frontend - MeStore

## 📋 Descripción General

Sistema de logging dual que funciona tanto en desarrollo (consola) como en producción (remoto), con captura automática de errores globales y contexto enriquecido.

## 🎯 Características Principales

### ✅ Logging Dual
- **Desarrollo**: Logs coloridos y legibles en consola del navegador
- **Producción**: Envío automático de logs al backend (/api/v1/logs)

### ✅ Captura Automática de Errores
- Errores JavaScript no manejados (`window.onerror`)
- Promesas rechazadas (`unhandledrejection`)
- Contexto automático (URL, timestamp, User-Agent)

### ✅ Contexto Enriquecido
- Timestamp ISO automático
- URL actual de la página
- User-Agent del navegador
- Session ID único por sesión
- User ID (si el usuario está logueado)
- Componente y acción específicos

## 🚀 Uso Básico

### Importación Simple
```typescript
import logger from '@/utils/logger';

// Logs básicos
logger.info('Usuario inició sesión', { userId: '123' });
logger.warn('Advertencia de validación', { field: 'email' });
logger.error('Error de conexión', { endpoint: '/api/users' });
```

### Hook Personalizado para Componentes
```typescript
import { useLogger } from '@/hooks/useLogger';

const MiComponente = () => {
  const { logInfo, logError, logUserAction } = useLogger({
    component: 'MiComponente',
    autoLogMount: true,
    autoLogUnmount: true
  });

  const handleClick = () => {
    logUserAction('button_click', { buttonId: 'submit' });
    // Lógica del botón...
  };

  return <button onClick={handleClick}>Enviar</button>;
};
```

## 📊 Niveles de Log

| Nivel | Desarrollo | Producción | Uso Recomendado |
|-------|------------|------------|------------------|
| `debug` | ✅ Consola | ❌ Filtrado | Debugging detallado |
| `info` | ✅ Consola | ❌ Filtrado | Información general |
| `warn` | ✅ Consola | ✅ Remoto | Advertencias importantes |
| `error` | ✅ Consola | ✅ Remoto | Errores que requieren atención |

## ⚙️ Configuración

### Variables de Entorno

#### Desarrollo (`.env.development`)
```env
VITE_LOG_REMOTE=false
VITE_LOG_ENDPOINT=http://localhost:8000/api/v1/logs
VITE_APP_ENV=development
```

#### Producción (`.env.production`)
```env
VITE_LOG_REMOTE=true
VITE_LOG_ENDPOINT=/api/v1/logs
VITE_APP_ENV=production
```

## 🎯 Casos de Uso Específicos

### 1. Logging de Acciones de Usuario
```typescript
// En un componente de e-commerce
logger.logUserAction('add_to_cart', { productId: '123', quantity: 2 });
logger.logUserAction('checkout_start', { cartValue: 99.99 });
```

### 2. Logging de Llamadas API
```typescript
// Antes de la llamada
const startTime = Date.now();

try {
  const response = await fetch('/api/products');
  const duration = Date.now() - startTime;

  logger.logApiCall('/api/products', 'GET', duration, response.status);
} catch (error) {
  logger.logApiCall('/api/products', 'GET', Date.now() - startTime, 0);
  logger.error('API call failed', { error, endpoint: '/api/products' });
}
```

### 3. Logging de Navegación
```typescript
// En un router o componente de página
useEffect(() => {
  logger.logPageView('/dashboard');
}, []);
```

### 4. Configuración de Usuario
```typescript
// Al hacer login
logger.setUserId('user_12345');
```

## 🔍 Debugging en Desarrollo

### Consola del Navegador
Los logs aparecen con formato enriquecido:
```
[MeStore 14:32:56] 🚀 Usuario inició sesión { userId: '123', timestamp: '2025-07-19T19:32:56.454Z' }
[MeStore 14:32:57] ⚠️ Validación fallida { field: 'email', value: 'invalid' }
```

### DevTools Network Tab
En producción, verificar que los logs se envían a `/api/v1/logs`

## 🚨 Captura de Errores Globales

### Errores JavaScript
```javascript
// Este error será capturado automáticamente
throw new Error('Algo salió mal');
```

### Promesas Rechazadas
```javascript
// Esta promesa rechazada será capturada automáticamente
Promise.reject('Error de API');
```

## 📱 Formato de Logs Enviados

### Estructura JSON
```json
{
  "level": "error",
  "message": "Error de conexión API",
  "timestamp": "2025-07-19T19:32:56.454Z",
  "url": "https://mestore.com/dashboard",
  "userAgent": "Mozilla/5.0...",
  "userId": "user_12345",
  "sessionId": "session_1721425976454_abc123",
  "component": "UserDashboard",
  "action": "load_data",
  "data": {
    "endpoint": "/api/user/profile",
    "status": 500
  },
  "error": {
    "message": "Network request failed",
    "stack": "Error: Network request failed
    at...",
    "name": "NetworkError"
  }
}
```

## 🛠️ Mantenimiento

### Limpiar Logs Antiguos
El backend puede implementar limpieza automática basada en:
- Fecha (logs > 30 días)
- Nivel (mantener solo errors y warnings)
- Volumen (mantener últimos 10,000 logs)

### Monitoreo de Performance
- Verificar que el envío de logs no afecte UX
- Implementar rate limiting si es necesario
- Considerar batching para logs muy frecuentes

## 🔗 Integración con Herramientas Externas

### Sentry, LogRocket, etc.
```typescript
// Extender el logger para integrar con herramientas externas
logger.error('Critical error', { error }, 'PaymentFlow', 'process_payment');
// Automáticamente se puede enviar también a Sentry
```

## 📈 Análisis de Logs

### Métricas Útiles
- Errores más frecuentes por componente
- Páginas con más errores
- Usuarios que experimentan más problemas
- Performance de APIs desde el frontend

### Queries de Ejemplo (Backend)
```sql
-- Errores más comunes
SELECT message, COUNT(*) as count 
FROM frontend_logs 
WHERE level = 'error' 
GROUP BY message 
ORDER BY count DESC;

-- Usuarios con más errores
SELECT user_id, COUNT(*) as error_count
FROM frontend_logs 
WHERE level = 'error' AND user_id IS NOT NULL
GROUP BY user_id 
ORDER BY error_count DESC;
```

---

## 🎉 Demo y Testing

Visita la aplicación en desarrollo y abre la consola del navegador para ver los logs en acción. El componente `LoggerExample` proporciona botones para testear todos los tipos de logs.

**¡El sistema está listo para usar en desarrollo y producción📝