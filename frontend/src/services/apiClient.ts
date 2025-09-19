import axios, { AxiosInstance } from 'axios';

// Configuración de baseURL que funciona tanto en Vite como en Jest
const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://192.168.1.137:8000/api/v1';

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
