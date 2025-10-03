# Error Handling System - Quick Reference

Referencia rápida para el sistema de manejo de errores de MeStore.

---

## Importaciones Comunes

```typescript
// Toast notifications
import { useToast, useApiErrorToast } from './contexts/ToastContext';

// Retry logic
import { retryRequest, retryAxiosRequest, retryWithCircuitBreaker } from './utils/retry';

// Error handler
import { errorHandler } from './utils/errorHandler';

// Error boundary
import ErrorBoundary from './components/ErrorBoundary';
```

---

## Uso Rápido

### Toast Notifications

```typescript
function MyComponent() {
  const { showSuccess, showError, showWarning, showInfo } = useToast();

  // Show toasts
  showSuccess('Operación exitosa');
  showError('Error al procesar');
  showWarning('Atención requerida');
  showInfo('Información importante');
}
```

### API Call con Error Handling

```typescript
function MyComponent() {
  const { showSuccess } = useToast();
  const handleApiError = useApiErrorToast();

  const loadData = async () => {
    try {
      const response = await retryAxiosRequest(() => api.get('/data'));
      showSuccess('Datos cargados');
      return response.data;
    } catch (error) {
      handleApiError(error, 'MyComponent.loadData');
    }
  };
}
```

### Form Submission con Validación

```typescript
function FormComponent() {
  const { showSuccess, showError } = useToast();

  const handleSubmit = async (data: FormData) => {
    try {
      await api.post('/submit', data);
      showSuccess('Formulario enviado exitosamente');
    } catch (error: any) {
      if (error.response?.status === 422) {
        // Validation errors
        const errors = error.response.data?.detail || [];
        errors.forEach((err: any) => {
          showError(`${err.loc.join('.')}: ${err.msg}`);
        });
      } else {
        showError('Error al enviar formulario');
      }
    }
  };
}
```

### Error Boundary para Secciones Críticas

```typescript
function CriticalSection() {
  return (
    <ErrorBoundary severity="critical">
      <YourComponent />
    </ErrorBoundary>
  );
}
```

### Retry con Circuit Breaker

```typescript
import { retryWithCircuitBreaker, apiCircuitBreaker } from './utils/retry';

async function fetchData() {
  // Check circuit breaker first
  if (apiCircuitBreaker.getState() === 'open') {
    console.warn('Circuit breaker is open');
    return;
  }

  try {
    const response = await retryWithCircuitBreaker(() => api.get('/data'));
    return response.data;
  } catch (error) {
    console.error('All retries failed');
  }
}
```

---

## Patrones Comunes

### Patrón 1: Simple API Call

```typescript
const { showSuccess, showError } = useToast();

const fetchData = async () => {
  try {
    const { data } = await api.get('/endpoint');
    showSuccess('Success');
    return data;
  } catch (error) {
    showError('Failed to load');
  }
};
```

### Patrón 2: Con Auto-Retry

```typescript
const { showSuccess } = useToast();
const handleApiError = useApiErrorToast();

const fetchData = async () => {
  try {
    const { data } = await retryAxiosRequest(() => api.get('/endpoint'));
    showSuccess('Data loaded');
    return data;
  } catch (error) {
    handleApiError(error, 'Component.fetchData');
  }
};
```

### Patrón 3: Custom Hook

```typescript
function useDataLoader<T>(endpoint: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const handleApiError = useApiErrorToast();

  const load = async () => {
    setLoading(true);
    try {
      const response = await retryAxiosRequest(() => api.get(endpoint));
      setData(response.data);
    } catch (error) {
      handleApiError(error, `useDataLoader(${endpoint})`);
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, load };
}
```

---

## Tipos de Toast

| Tipo      | Color  | Uso                                  |
|-----------|--------|--------------------------------------|
| `success` | Verde  | Operaciones exitosas                 |
| `error`   | Rojo   | Errores que requieren atención       |
| `warning` | Amarillo | Advertencias no críticas           |
| `info`    | Azul   | Información general                  |

---

## HTTP Status Codes Handling

| Code | Handling                          | Toast Auto |
|------|-----------------------------------|------------|
| 401  | Auto-refresh token → Logout       | ✅ Yes     |
| 403  | Forbidden                         | ✅ Yes     |
| 404  | Not found                         | ✅ Yes     |
| 422  | Validation error                  | ✅ Yes     |
| 429  | Rate limit                        | ✅ Yes     |
| 5xx  | Server error                      | ✅ Yes     |

---

## Retry Options

```typescript
{
  maxRetries: 3,           // Max retry attempts
  initialDelay: 1000,      // Initial delay in ms
  maxDelay: 10000,         // Max delay in ms
  backoffMultiplier: 2,    // Exponential multiplier
  shouldRetry: (error) => boolean,  // Custom retry logic
  onRetry: (error, attempt) => void // Callback on retry
}
```

---

## Circuit Breaker States

| State        | Meaning                           | Behavior                |
|--------------|-----------------------------------|-------------------------|
| `closed`     | Normal operation                  | Allows all requests     |
| `open`       | Too many failures                 | Blocks all requests     |
| `half-open`  | Testing recovery                  | Allows limited requests |

---

## Error Boundary Props

```typescript
<ErrorBoundary
  severity="critical"  // 'critical' | 'error' | 'warning'
  showDetails={true}   // Show technical details in dev
  fallback={<CustomUI />}  // Custom fallback UI
  onError={(error, errorInfo) => {
    // Custom error handler
  }}
>
  <YourComponent />
</ErrorBoundary>
```

---

## Global Error Handler Setup

```typescript
// In main.tsx
import { setupGlobalErrorHandler } from './utils/errorHandler';

setupGlobalErrorHandler(); // Setup before rendering
```

---

## Tips

1. **Siempre usar try-catch** en async operations
2. **Prefer useApiErrorToast** sobre showError manual para API errors
3. **Use retryAxiosRequest** para operaciones idempotentes (GET, PUT idempotente)
4. **No usar retry** en operaciones no idempotentes sin consideración (POST create)
5. **Error Boundary** solo captura errores en render, no en event handlers
6. **Circuit breaker** es útil para endpoints problemáticos específicos
7. **Mensajes user-friendly** siempre en español
8. **Log context** para debugging más fácil

---

## Troubleshooting

### Toast no aparece
1. Verificar que `ToastProvider` esté en el root
2. Confirmar que no hay múltiples providers
3. Revisar console por errores

### Retry infinito
1. Verificar función `shouldRetry`
2. Confirmar `maxRetries` configurado
3. Revisar estado del circuit breaker

### Errors no se capturan
1. Error Boundary solo captura en render
2. Usar try-catch en async/event handlers
3. Verificar que error se propaga correctamente

---

## Archivos de Referencia

- **Guía completa**: `src/docs/ERROR_HANDLING_GUIDE.md`
- **Ejemplos**: `src/docs/ERROR_HANDLING_INTEGRATION_EXAMPLE.tsx`
- **Resumen**: `ERROR_HANDLING_SYSTEM_SUMMARY.md`
