import { AxiosResponse } from 'axios';
import { apiClient } from './authInterceptors';
import {
  LoginCredentials,
  RegisterData,
  AuthResponse,
  UserProfile,
  UpdateUserData,
  Product,
  CreateProductData,
  UpdateProductData,
  PaginatedResponse,
  ProductFilters,
} from '../types/api.types';

// Servicio API tipado que usa el cliente con interceptores
export const api = {
  // Métodos de autenticación
  auth: {
    login: (
      credentials: LoginCredentials
    ): Promise<AxiosResponse<AuthResponse>> =>
      apiClient.post('/api/auth/login', credentials),

    register: (userData: RegisterData): Promise<AxiosResponse<AuthResponse>> =>
      apiClient.post('/api/auth/register', userData),

    refresh: (refreshToken: string): Promise<AxiosResponse<AuthResponse>> =>
      apiClient.post('/api/auth/refresh', { refresh_token: refreshToken }),

    logout: (): Promise<AxiosResponse<void>> =>
      apiClient.post('/api/auth/logout'),
  },

  // Métodos de usuarios
  users: {
    getProfile: (): Promise<AxiosResponse<UserProfile>> =>
      apiClient.get('/api/users/profile'),

    updateProfile: (
      userData: UpdateUserData
    ): Promise<AxiosResponse<UserProfile>> =>
      apiClient.put('/api/users/profile', userData),

    getAllUsers: (): Promise<AxiosResponse<UserProfile[]>> =>
      apiClient.get('/api/users'),
  },

  // Métodos de productos
  products: {
    getAll: (): Promise<AxiosResponse<Product[]>> =>
      apiClient.get('/api/products'),

    getById: (id: string): Promise<AxiosResponse<Product>> =>
      apiClient.get(`/api/products/${id}`),

    create: (productData: CreateProductData): Promise<AxiosResponse<Product>> =>
      apiClient.post('/api/products', productData),

    update: (
      id: string,
      productData: UpdateProductData
    ): Promise<AxiosResponse<Product>> =>
      apiClient.put(`/api/products/${id}`, productData),

    delete: (id: string): Promise<AxiosResponse<void>> =>
      apiClient.delete(`/api/products/${id}`),
    getWithFilters: (
      filters: ProductFilters,
      page: number = 1,
      limit: number = 10
    ): Promise<AxiosResponse<PaginatedResponse<Product>>> =>
      apiClient.get('/api/products/search', {
        params: { ...filters, page, limit },
      }),
  },
};
