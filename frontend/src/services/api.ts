import { apiClient } from './authInterceptors';

// Servicio API que usa el cliente con interceptores
export const api = {
  // Métodos de autenticación
  auth: {
    login: (credentials: { email: string; password: string }) => 
      apiClient.post('/api/auth/login', credentials),
    
    register: (userData: any) => 
      apiClient.post('/api/auth/register', userData),
    
    refresh: (refreshToken: string) => 
      apiClient.post('/api/auth/refresh', { refresh_token: refreshToken }),
    
    logout: () => 
      apiClient.post('/api/auth/logout'),
  },

  // Métodos de usuarios (con token automático)
  users: {
    getProfile: () => 
      apiClient.get('/api/users/me'),
    
    updateProfile: (data: any) => 
      apiClient.put('/api/users/me', data),
  },

  // Métodos de productos (con token automático)
  products: {
    getAll: () => 
      apiClient.get('/api/products'),
    
    getById: (id: string) => 
      apiClient.get(`/api/products/${id}`),
    
    create: (productData: any) => 
      apiClient.post('/api/products', productData),
    
    update: (id: string, productData: any) => 
      apiClient.put(`/api/products/${id}`, productData),
    
    delete: (id: string) => 
      apiClient.delete(`/api/products/${id}`),
  },
};

export default api;
