// Tipos base para respuestas API
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

export interface ApiError {
  message: string;
  status: number;
  errors?: Record<string, string[]>;
}

// Tipos de autenticación
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  name: string;
  confirmPassword: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: UserProfile;
}

// Tipos de usuario
export interface UserProfile {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'vendedor' | 'cliente';
  createdAt: string;
  updatedAt: string;
}

export interface UpdateUserData {
  name?: string;
  email?: string;
  phone?: string;
}

// Tipos de productos
export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  stock: number;
  category: string;
  imageUrl?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateProductData {
  name: string;
  description: string;
  price: number;
  stock: number;
  category: string;
  imageUrl?: string;
  sku?: string;
  dimensions?: { length: number; width: number; height: number; unit: string };
  weight?: { value: number; unit: string };
}

export interface UpdateProductData extends Partial<CreateProductData> {
  id: number;
}

// Tipos para paginación
export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Tipos para filtros de productos
export interface ProductFilters {
  search?: string;
  category?: string;
  minPrice?: number;
  maxPrice?: number;
  sortBy?: 'name' | 'price' | 'salesCount' | 'rating';
  sortOrder?: 'asc' | 'desc';
}
