import { AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { apiClient } from './apiClient';

// Función para transformar errores para la UI
const transformErrorForUI = (error: AxiosError) => {
  const transformedError = {
    ...error,
    userMessage: 'Error desconocido',
    statusCode: error.response?.status || 0,
    timestamp: new Date().toISOString()
  };

  if (error.response) {
    const status = error.response.status;
    transformedError.userMessage = status >= 500 
      ? 'Error del servidor. Intenta más tarde.'
      : (error.response.data as any)?.message || 'Error en la solicitud';
  }

  return transformedError;
};


// Flag para evitar loops infinitos durante refresh
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: any) => void;
  reject: (error?: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });
  
  failedQueue = [];
};

// Interceptor de Request: Agregar token automáticamente
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    // Manejo de otros códigos de error HTTP
      // Manejo de errores de red y timeout
      if (!error.response) {  // ← AGREGAR ESTA LÍNEA
        if (error.code === 'ECONNABORTED') {
        console.error('Request timeout:', error.message);
        error.message = 'La solicitud ha tardado demasiado. Intenta de nuevo.';
      } else if (error.message === 'Network Error') {
        console.error('Network error:', error.message);
        error.message = 'Error de conexión. Verifica tu conexión a internet.';
      } else {
        console.error('Request error:', error.message);
        error.message = 'Error de solicitud. Intenta de nuevo más tarde.';
      }
      return Promise.reject(transformErrorForUI(error));
    }
    if (error.response) {
      const status = error.response.status;
      const message = (error.response.data as any)?.message || error.message;
      
      switch (status) {
        case 403:
          console.error('Acceso denegado:', message);
          break;
        case 404:
          console.error('Recurso no encontrado:', message);
          break;
        case 500:
          console.error('Error interno del servidor:', message);
          break;
        default:
          if (status >= 500) {
            console.error('Error del servidor:', message);
          }
      }
    }
    
    return Promise.reject(error);
  }
);

// Interceptor de Response: Manejar refresh automático
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Si ya está refreshing, agregar a la cola
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(() => {
          return apiClient(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // Llamar endpoint de refresh
        const response = await apiClient.post('/api/auth/refresh', {
          refresh_token: refreshToken
        });

        const { access_token, refresh_token: newRefreshToken } = response.data;

        // Actualizar tokens en localStorage
        localStorage.setItem('access_token', access_token);
        if (newRefreshToken) {
          localStorage.setItem('refresh_token', newRefreshToken);
        }

        // Procesar cola de requests fallidos
        processQueue(null, access_token);

        // Reintentar request original
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
        }
        
        return apiClient(originalRequest);

      } catch (refreshError) {
        // Refresh falló - limpiar tokens y redirigir a login
        processQueue(refreshError, null);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        
        // Disparar evento para que AuthContext maneje logout
        window.dispatchEvent(new CustomEvent('auth:logout'));
        
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export { apiClient };