import axios from 'axios';

const API_BASE_URL = 'http://192.168.1.137:8000/api/v1';

// Configuración base de axios
const baseApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
  }
});

baseApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Endpoints específicos para productos
export const productsAPI = {
  create: (data: any) => baseApi.post('/productos', data),
  update: (id: string, data: any) => baseApi.put(`/productos/${id}`, data),
  getWithFilters: (filters: any) => baseApi.get('/productos', { params: filters })
};

// API extendida con tipado explícito
const api = Object.assign(baseApi, {
  products: productsAPI
});

export default api;