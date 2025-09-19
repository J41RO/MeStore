import type { EntityId, Timestamp, BaseEntity, StandardResponse, PaginatedResponse } from './core.types';

// Legacy tipos base para respuestas API - migrating to StandardResponse
export interface ApiResponse<T> extends StandardResponse<T> {
  // Deprecated: Use StandardResponse instead
  status: number; // Legacy field, will be removed
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
export interface UserProfile extends BaseEntity {
  id: EntityId;
  email: string;
  name: string;
  role: 'admin' | 'vendedor' | 'cliente';
  // createdAt/updatedAt handled by BaseEntity timestamps
}

export interface UpdateUserData {
  name?: string;
  email?: string;
  phone?: string;
}

// Tipos de productos
export interface ProductImage extends BaseEntity {
  id: EntityId;
  product_id: EntityId;
  filename: string;
  original_filename: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  width?: number;
  height?: number;
  order_index: number;
  public_url: string;
  // created_at, updated_at inherited from BaseEntity
}

export interface Product extends BaseEntity {
  id: EntityId;
  vendor_id?: EntityId; // Foreign key to user (vendor)
  name: string;
  description: string;
  price: number;
  stock: number;
  category: string;
  imageUrl?: string; // Legacy field - keeping for backward compatibility
  images?: ProductImage[]; // New field for multiple images
  main_image_url?: string; // First image URL for convenience
  // createdAt/updatedAt handled by BaseEntity timestamps
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
  id: EntityId;
}

// Legacy pagination - use core.types.PaginatedResponse instead
export interface LegacyPaginatedResponse<T> {
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
