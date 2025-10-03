# Error Handling System - Guía de Uso

Sistema comprehensivo de manejo de errores para la aplicación MeStore.

## Componentes del Sistema

### 1. Error Handler Utility (`utils/errorHandler.ts`)

Utilidad centralizada para manejar errores de API con formato estandarizado.

```typescript
import { errorHandler, AppError } from '../utils/errorHandler';

// Handle API errors
const handleApiCall = async () => {
  try {
    const response = await api.get('/endpoint');
    return response.data;
  } catch (error) {
    const appError = errorHandler.handleApiError(error);
    console.error('Error occurred:', appError);

    // Check if should logout
    if (errorHandler.shouldLogout(appError)) {
      // Handle logout
    }

    throw appError;
  }
};
```

### 2. Retry Logic (`utils/retry.ts`)

Lógica de reintentos automáticos con exponential backoff.

```typescript
import { retryRequest, retryAxiosRequest } from '../utils/retry';

// Retry a function with default options
const result = await retryRequest(
  () => api.get('/endpoint'),
  {
    maxRetries: 3,
    initialDelay: 1000,
    shouldRetry: (error, attemptNumber) => {
      // Custom retry logic
      return error.response?.status >= 500;
    }
  }
);

// Retry axios request with smart defaults
const data = await retryAxiosRequest(
  () => api.post('/endpoint', payload)
);
```

#### Circuit Breaker Pattern

```typescript
import { apiCircuitBreaker, retryWithCircuitBreaker } from '../utils/retry';

// Use circuit breaker to prevent cascading failures
const result = await retryWithCircuitBreaker(
  () => api.get('/endpoint')
);

// Check circuit breaker state
console.log(apiCircuitBreaker.getState()); // 'closed' | 'open' | 'half-open'
```

### 3. Toast Notifications (`components/common/Toast.tsx`)

Sistema de notificaciones user-friendly con auto-dismiss.

#### Setup in App Root

```typescript
import { ToastProvider } from './contexts/ToastContext';

function App() {
  return (
    <ToastProvider
      maxToasts={5}
      defaultDuration={5000}
      position="top-right"
    >
      <YourApp />
    </ToastProvider>
  );
}
```

#### Using Toast in Components

```typescript
import { useToast } from '../contexts/ToastContext';

function MyComponent() {
  const { showSuccess, showError, showWarning, showInfo } = useToast();

  const handleSubmit = async () => {
    try {
      await api.post('/endpoint', data);
      showSuccess('Operación exitosa');
    } catch (error) {
      showError('Error al procesar la solicitud');
    }
  };

  return <button onClick={handleSubmit}>Submit</button>;
}
```

### 4. Error Boundary (`components/ErrorBoundary.tsx`)

Captura errores de React no manejados.

```typescript
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary
      severity="critical"
      onError={(error, errorInfo) => {
        // Custom error handling
        console.error('Caught by boundary:', error);
      }}
    >
      <YourApp />
    </ErrorBoundary>
  );
}
```

### 5. API Interceptor Enhancement

El interceptor de axios ahora maneja automáticamente:

- Reintentos de token con refresh token
- Mensajes de error user-friendly
- Auto-logout en errores 401
- Logging en desarrollo
- Toast notifications automáticas

## Patrones de Uso Comunes

### Patrón 1: API Call con Error Handling Completo

```typescript
import { useToast, useApiErrorToast } from '../contexts/ToastContext';
import { retryAxiosRequest } from '../utils/retry';

function MyComponent() {
  const { showSuccess } = useToast();
  const handleApiError = useApiErrorToast();

  const fetchData = async () => {
    try {
      // Auto-retry on failures
      const response = await retryAxiosRequest(
        () => api.get('/data')
      );

      showSuccess('Datos cargados exitosamente');
      return response.data;
    } catch (error) {
      // Show user-friendly error and handle logout if needed
      handleApiError(error, 'MyComponent.fetchData');
    }
  };

  return <button onClick={fetchData}>Load Data</button>;
}
```

### Patrón 2: Form Submission con Validación

```typescript
import { useToast } from '../contexts/ToastContext';
import { errorHandler } from '../utils/errorHandler';

function FormComponent() {
  const { showSuccess, showError } = useToast();

  const handleSubmit = async (formData: FormData) => {
    try {
      const response = await api.post('/submit', formData);
      showSuccess('Formulario enviado exitosamente');
      return response.data;
    } catch (error: any) {
      // Handle validation errors
      if (error.response?.status === 422) {
        const appError = errorHandler.handleApiError(error);
        const validationErrors = errorHandler.formatValidationErrors(
          appError.details
        );

        validationErrors.forEach(err => showError(err));
      } else {
        showError('Error al enviar el formulario');
      }
    }
  };

  return <form onSubmit={handleSubmit}>...</form>;
}
```

### Patrón 3: Protected Route con Error Handling

```typescript
import { useToast } from '../contexts/ToastContext';
import { Navigate } from 'react-router-dom';
import ErrorBoundary from '../components/ErrorBoundary';

function ProtectedRoute({ children }) {
  const { showWarning } = useToast();
  const isAuthenticated = checkAuth();

  if (!isAuthenticated) {
    showWarning('Debes iniciar sesión para acceder');
    return <Navigate to="/login" />;
  }

  return (
    <ErrorBoundary severity="error">
      {children}
    </ErrorBoundary>
  );
}
```

### Patrón 4: Async Operation con Loading y Error States

```typescript
import { useState } from 'react';
import { useToast } from '../contexts/ToastContext';
import { retryAxiosRequest } from '../utils/retry';

function DataLoader() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { showError, showSuccess } = useToast();

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await retryAxiosRequest(
        () => api.get('/data'),
        { maxRetries: 3 }
      );

      showSuccess('Datos cargados');
      return response.data;
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Error al cargar datos';
      setError(message);
      showError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {loading && <Spinner />}
      {error && <ErrorMessage message={error} />}
      <button onClick={loadData}>Load</button>
    </div>
  );
}
```

## Mejores Prácticas

### 1. Siempre usar try-catch en llamadas API

```typescript
// ✅ CORRECTO
try {
  const response = await api.get('/endpoint');
  return response.data;
} catch (error) {
  handleApiError(error);
}

// ❌ INCORRECTO
const response = await api.get('/endpoint');
return response.data; // No error handling
```

### 2. Mostrar mensajes user-friendly

```typescript
// ✅ CORRECTO
showError('No se pudo guardar el producto. Por favor intenta nuevamente.');

// ❌ INCORRECTO
showError('Error 500: Internal Server Error');
```

### 3. Usar retry logic para errores transitorios

```typescript
// ✅ CORRECTO - Retry automático en errores 5xx
const data = await retryAxiosRequest(() => api.get('/data'));

// ⚠️ CUIDADO - No usar retry en operaciones no idempotentes sin consideración
const data = await retryAxiosRequest(() => api.post('/create')); // Puede crear duplicados
```

### 4. Log errors apropiadamente

```typescript
// ✅ CORRECTO - Log con contexto
if (import.meta.env.MODE === 'development') {
  console.error('Failed to load products:', error, {
    userId: currentUser.id,
    filters: appliedFilters
  });
}

// ❌ INCORRECTO - Log sin contexto
console.error(error); // Difícil de debuggear
```

### 5. Handle diferentes tipos de errores

```typescript
try {
  const response = await api.post('/endpoint', data);
} catch (error: any) {
  if (error.response) {
    // Server responded with error
    const status = error.response.status;
    if (status === 422) {
      // Validation error
      handleValidationErrors(error.response.data);
    } else if (status === 403) {
      // Permission error
      showError('No tienes permisos');
    }
  } else if (error.request) {
    // Network error
    showError('Error de conexión');
  } else {
    // Other error
    showError('Error inesperado');
  }
}
```

## Testing Error Handling

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { ToastProvider } from '../contexts/ToastContext';
import MyComponent from './MyComponent';

test('shows error toast on API failure', async () => {
  // Mock API failure
  jest.spyOn(api, 'get').mockRejectedValue({
    response: { status: 500, data: { detail: 'Server error' } }
  });

  render(
    <ToastProvider>
      <MyComponent />
    </ToastProvider>
  );

  // Trigger API call
  const button = screen.getByText('Load Data');
  button.click();

  // Wait for error toast
  await waitFor(() => {
    expect(screen.getByText(/error del servidor/i)).toBeInTheDocument();
  });
});
```

## Troubleshooting

### Toast no aparece

1. Verifica que `ToastProvider` esté en el root de tu app
2. Asegúrate de que no hay múltiples `ToastProvider` anidados
3. Revisa la consola por errores de React

### Errores no se capturan en Error Boundary

1. Error Boundary solo captura errores en render, no en event handlers
2. Usa try-catch en event handlers y async operations
3. Error Boundary no captura errores en callbacks de setTimeout

### Retry infinito

1. Verifica la función `shouldRetry` en retry options
2. Asegúrate de que `maxRetries` está configurado
3. Revisa que el circuit breaker no esté abierto

## Referencias

- [React Error Boundaries](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)
- [Axios Interceptors](https://axios-http.com/docs/interceptors)
- [Exponential Backoff](https://en.wikipedia.org/wiki/Exponential_backoff)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
