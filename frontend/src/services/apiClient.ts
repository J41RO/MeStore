import axios, { AxiosInstance } from 'axios';

// Configuración de baseURL que funciona tanto en Vite como en Jest
const baseURL = process.env.VITE_API_BASE_URL || 'http://192.168.1.137:8000';

// Cliente axios con configuración base
export const apiClient: AxiosInstance = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});
