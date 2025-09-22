import axios, { AxiosInstance } from 'axios';

// Configuración de baseURL: usar proxy en desarrollo, URL directa en producción
const baseURL = import.meta.env.DEV
  ? undefined  // Use Vite proxy in development
  : (import.meta.env.VITE_API_BASE_URL || 'http://192.168.1.137:8000');

// Cliente axios con configuración base optimizada para CORS
export const apiClient: AxiosInstance = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
  withCredentials: true, // Importante para CORS con credenciales
  maxRedirects: 5,
  validateStatus: (status) => {
    // Considerar 2xx y 3xx como exitosos
    return status >= 200 && status < 400;
  },
});
