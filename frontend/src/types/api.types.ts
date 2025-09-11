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
export interface ProductImage {
  id: string;
  product_id: string;
  filename: string;
  original_filename: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  width?: number;
  height?: number;
  order_index: number;
  created_at: string;
  updated_at: string;
  public_url: string;
}

export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  stock: number;
  category: string;
  imageUrl?: string; // Legacy field - keeping for backward compatibility
  images?: ProductImage[]; // New field for multiple images
  main_image_url?: string; // First image URL for convenience
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
