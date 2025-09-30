import axios, { AxiosInstance } from 'axios';

// Configuración de baseURL: priorizar VITE_API_BASE_URL si está configurado
const baseURL = import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? undefined : 'http://192.168.1.137:8000');

// Cliente axios con configuración base optimizada para CORS
export const apiClient: AxiosInstance = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
    // REMOVIDO: 'User-Agent' - No permitido en navegadores (causa error "Refused to set unsafe header")
  },
  withCredentials: true, // Importante para CORS con credenciales
  maxRedirects: 5,
  validateStatus: (status) => {
    // Considerar 2xx y 3xx como exitosos
    return status >= 200 && status < 400;
  },
});
