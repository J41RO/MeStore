import axios, { AxiosInstance } from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://192.168.1.137:8000';

// Cliente axios con configuración base
export const apiClient: AxiosInstance = axios.create({
  baseURL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Nota: Los interceptores se configuran en authInterceptors.ts
export default apiClient;
