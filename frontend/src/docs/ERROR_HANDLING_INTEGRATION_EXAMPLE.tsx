/**
 * ERROR HANDLING SYSTEM - Integration Example
 *
 * This file demonstrates how to integrate the comprehensive error handling system
 * into your MeStore application.
 */

// ============================================================================
// STEP 1: Wrap your app with ToastProvider in main.tsx
// ============================================================================

/*
import { StrictMode, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ToastProvider } from './contexts/ToastContext';
import { setupGlobalErrorHandler } from './utils/errorHandler';
import App from './App';

// Setup global error handler for unhandled errors
setupGlobalErrorHandler();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ToastProvider
        maxToasts={5}
        defaultDuration={5000}
        position="top-right"
      >
        <App />
      </ToastProvider>
    </BrowserRouter>
  </StrictMode>
);
*/

// ============================================================================
// STEP 2: Make showToast available globally (optional)
// ============================================================================

/*
// In ToastContext.tsx, add this after the ToastProvider:

export const ToastProvider: React.FC<ToastProviderProps> = (props) => {
  // ... existing code ...

  // Make showToast available globally for axios interceptor
  useEffect(() => {
    window.showToast = showToast;
    return () => {
      delete window.showToast;
    };
  }, [showToast]);

  // ... rest of code ...
};
*/

// ============================================================================
// STEP 3: Example Component with Error Handling
// ============================================================================

import { useState, useCallback } from 'react';
import { useToast, useApiErrorToast } from '../contexts/ToastContext';
import { retryAxiosRequest } from '../utils/retry';
import api from '../services/api';

interface Product {
  id: string;
  name: string;
  price: number;
}

export function ProductListExample() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const { showSuccess, showError, showWarning } = useToast();
  const handleApiError = useApiErrorToast();

  // Example 1: Simple API call with error handling
  const fetchProducts = useCallback(async () => {
    setLoading(true);

    try {
      // API call with automatic retry on failures
      const response = await retryAxiosRequest(
        () => api.get('/api/v1/products/'),
        {
          maxRetries: 3,
          initialDelay: 1000
        }
      );

      setProducts(response.data);
      showSuccess('Productos cargados exitosamente');
    } catch (error) {
      // Show user-friendly error toast and handle logout if needed
      handleApiError(error, 'ProductList.fetchProducts');
    } finally {
      setLoading(false);
    }
  }, [showSuccess, handleApiError]);

  // Example 2: Form submission with validation error handling
  const createProduct = useCallback(async (productData: Partial<Product>) => {
    try {
      const response = await api.post('/api/v1/products/', productData);

      showSuccess('Producto creado exitosamente');
      setProducts((prev) => [...prev, response.data]);
    } catch (error: any) {
      // Handle validation errors specifically
      if (error.response?.status === 422) {
        const validationErrors = error.response.data?.detail || [];
        if (Array.isArray(validationErrors)) {
          validationErrors.forEach((err: any) => {
            showError(`${err.loc.join('.')}: ${err.msg}`);
          });
        } else {
          showError('Error de validación en los datos proporcionados');
        }
      } else {
        handleApiError(error, 'ProductList.createProduct');
      }
    }
  }, [showSuccess, showError, handleApiError]);

  // Example 3: Delete operation with confirmation
  const deleteProduct = useCallback(async (productId: string) => {
    const confirmed = window.confirm('¿Estás seguro de eliminar este producto?');
    if (!confirmed) return;

    try {
      await api.delete(`/api/v1/products/${productId}`);

      setProducts((prev) => prev.filter((p) => p.id !== productId));
      showSuccess('Producto eliminado exitosamente');
    } catch (error) {
      handleApiError(error, 'ProductList.deleteProduct');
    }
  }, [showSuccess, handleApiError]);

  // Example 4: Bulk operation with partial success handling
  const bulkDeleteProducts = useCallback(async (productIds: string[]) => {
    const results = await Promise.allSettled(
      productIds.map((id) => api.delete(`/api/v1/products/${id}`))
    );

    const successes = results.filter((r) => r.status === 'fulfilled').length;
    const failures = results.filter((r) => r.status === 'rejected').length;

    if (successes > 0) {
      showSuccess(`${successes} productos eliminados exitosamente`);
      setProducts((prev) => prev.filter((p) => !productIds.includes(p.id)));
    }

    if (failures > 0) {
      showWarning(`${failures} productos no pudieron ser eliminados`);
    }
  }, [showSuccess, showWarning]);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Productos</h1>

      <div className="mb-4 space-x-2">
        <button
          onClick={fetchProducts}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Cargando...' : 'Cargar Productos'}
        </button>
      </div>

      {products.length === 0 ? (
        <p className="text-gray-500">No hay productos</p>
      ) : (
        <div className="grid gap-4">
          {products.map((product) => (
            <div key={product.id} className="border p-4 rounded">
              <h3 className="font-semibold">{product.name}</h3>
              <p className="text-gray-600">${product.price}</p>
              <button
                onClick={() => deleteProduct(product.id)}
                className="mt-2 px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
              >
                Eliminar
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// STEP 4: Example with ErrorBoundary for critical sections
// ============================================================================

import ErrorBoundary from '../components/ErrorBoundary';

export function CriticalSectionExample() {
  return (
    <ErrorBoundary
      severity="critical"
      onError={(error, errorInfo) => {
        // Send to monitoring service
        console.error('Critical error in dashboard:', error, errorInfo);
      }}
    >
      <div>
        {/* Your critical component */}
        <ProductListExample />
      </div>
    </ErrorBoundary>
  );
}

// ============================================================================
// STEP 5: Example with Circuit Breaker for unreliable endpoints
// ============================================================================

import { retryWithCircuitBreaker, apiCircuitBreaker } from '../utils/retry';

export function UnreliableEndpointExample() {
  const { showError, showWarning } = useToast();

  const fetchFromUnreliableAPI = useCallback(async () => {
    try {
      // Check circuit breaker state
      if (apiCircuitBreaker.getState() === 'open') {
        showWarning('Servicio temporalmente no disponible. Intenta más tarde.');
        return;
      }

      const response = await retryWithCircuitBreaker(
        () => api.get('/api/v1/unreliable-endpoint')
      );

      return response.data;
    } catch (error: any) {
      if (error.message?.includes('Circuit breaker is open')) {
        showError('Demasiados errores. El servicio se ha pausado temporalmente.');
      } else {
        showError('Error al obtener datos');
      }
    }
  }, [showError, showWarning]);

  return (
    <div>
      <button onClick={fetchFromUnreliableAPI}>
        Cargar desde API no confiable
      </button>
      <p className="text-sm text-gray-500 mt-2">
        Estado del circuit breaker: {apiCircuitBreaker.getState()}
      </p>
    </div>
  );
}

// ============================================================================
// STEP 6: Example Custom Hook for consistent error handling
// ============================================================================

export function useAsyncOperation<T>() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<T | null>(null);
  const handleApiError = useApiErrorToast();

  const execute = useCallback(
    async (operation: () => Promise<T>, options?: { silent?: boolean }) => {
      setLoading(true);
      setError(null);

      try {
        const result = await operation();
        setData(result);
        return result;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
        setError(errorMessage);

        if (!options?.silent) {
          handleApiError(err, 'AsyncOperation');
        }

        throw err;
      } finally {
        setLoading(false);
      }
    },
    [handleApiError]
  );

  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
    setData(null);
  }, []);

  return { loading, error, data, execute, reset };
}

// Usage of custom hook
export function ComponentUsingAsyncHook() {
  const { loading, error, data, execute } = useAsyncOperation<Product[]>();
  const { showSuccess } = useToast();

  const loadProducts = () => {
    execute(
      async () => {
        const response = await retryAxiosRequest(() => api.get('/api/v1/products/'));
        return response.data;
      }
    ).then((products) => {
      showSuccess(`${products.length} productos cargados`);
    });
  };

  return (
    <div>
      <button onClick={loadProducts} disabled={loading}>
        {loading ? 'Cargando...' : 'Cargar Productos'}
      </button>

      {error && (
        <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded text-red-800">
          {error}
        </div>
      )}

      {data && (
        <div className="mt-4">
          <h3>Productos: {data.length}</h3>
        </div>
      )}
    </div>
  );
}

export default {
  ProductListExample,
  CriticalSectionExample,
  UnreliableEndpointExample,
  ComponentUsingAsyncHook
};
