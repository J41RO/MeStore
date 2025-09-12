// Vendor-specific API endpoints for MeStocker
import { AxiosResponse } from 'axios';
import { apiClient } from './authInterceptors';
import { LoginCredentials, AuthResponse } from '../types/api.types';

// API endpoints específicos para vendedores
export const vendorApi = {
  // Autenticación de vendedores
  auth: {
    login: (
      credentials: LoginCredentials
    ): Promise<AxiosResponse<AuthResponse>> =>
      apiClient.post('/api/v1/vendedores/login', credentials),
    
    register: (userData: any): Promise<AxiosResponse<AuthResponse>> =>
      apiClient.post('/api/v1/vendedores/register', userData),
    
    dashboard: {
      resumen: (): Promise<AxiosResponse<any>> =>
        apiClient.get('/api/v1/vendedores/dashboard/resumen'),
      
      ordenes: (): Promise<AxiosResponse<any>> =>
        apiClient.get('/api/v1/vendedores/dashboard/ordenes'),
    },
  },
  
  // Productos del vendedor
  products: {
    list: (): Promise<AxiosResponse<any>> =>
      apiClient.get('/api/v1/vendedores/productos'),
    
    create: (productData: any): Promise<AxiosResponse<any>> =>
      apiClient.post('/api/v1/vendedores/productos', productData),
  },
};