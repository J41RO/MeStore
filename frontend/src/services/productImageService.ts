// ~/frontend/src/services/productImageService.ts
// ---------------------------------------------------------------------------------------------
// MESTORE - Product Image Service
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

/**
 * Servicio para gestión de imágenes de productos.
 * 
 * Maneja upload, eliminación y obtención de imágenes de productos
 * utilizando las APIs del backend.
 */

interface ProductImage {
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

interface ProductImageUploadResponse {
  success: boolean;
  uploaded_count: number;
  total_files: number;
  images: ProductImage[];
  errors: string[];
}

interface ProductImageDeleteResponse {
  success: boolean;
  message: string;
  deleted_image_id: string;
}

class ProductImageService {
  private baseURL = '/api/v1/productos';

  /**
   * Obtener token de autenticación del localStorage
   */
  private getAuthToken(): string | null {
    return localStorage.getItem('authToken') || localStorage.getItem('token');
  }

  /**
   * Upload múltiple de imágenes para un producto
   */
  async uploadProductImages(productId: string, files: File[]): Promise<ProductImage[]> {
    const formData = new FormData();
    
    files.forEach((file) => {
      formData.append(`files`, file);
    });

    const token = this.getAuthToken();
    const response = await fetch(`${this.baseURL}/${productId}/imagenes`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Error uploading images: ${response.statusText}`);
    }

    const result: ProductImageUploadResponse = await response.json();
    
    if (!result.success) {
      throw new Error(`Upload failed: ${result.errors.join(', ')}`);
    }

    return result.images;
  }

  /**
   * Obtener todas las imágenes de un producto
   */
  async getProductImages(productId: string): Promise<ProductImage[]> {
    const response = await fetch(`${this.baseURL}/${productId}/imagenes`);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Error fetching images: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Eliminar una imagen específica de un producto
   */
  async deleteProductImage(imageId: string): Promise<void> {
    const token = this.getAuthToken();
    const response = await fetch(
      `${this.baseURL}/imagenes/${imageId}`,
      {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Error deleting image: ${response.statusText}`);
    }

    const result: ProductImageDeleteResponse = await response.json();
    
    if (!result.success) {
      throw new Error(`Delete failed: ${result.message}`);
    }
  }

  /**
   * Crear FormData para upload de imágenes
   */
  createImageFormData(files: File[]): FormData {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    return formData;
  }

  /**
   * Validar archivos antes del upload
   */
  validateFiles(files: File[], maxFiles: number = 5, maxSize: number = 5 * 1024 * 1024): string[] {
    const errors: string[] = [];

    if (files.length > maxFiles) {
      errors.push(`Máximo ${maxFiles} archivos permitidos`);
    }

    files.forEach((file, index) => {
      // Validar tamaño
      if (file.size > maxSize) {
        errors.push(`Archivo ${index + 1}: Tamaño máximo 5MB`);
      }

      // Validar tipo
      const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
      if (!allowedTypes.includes(file.type)) {
        errors.push(`Archivo ${index + 1}: Formato no permitido. Use JPG, PNG, WebP o GIF`);
      }
    });

    return errors;
  }

  /**
   * Obtener URL pública de una imagen
   */
  getPublicImageUrl(imagePath: string): string {
    // La URL pública ya viene en el campo public_url del backend
    // pero podemos agregar lógica adicional si es necesario
    if (imagePath.startsWith('http')) {
      return imagePath;
    }
    return `${window.location.origin}${imagePath}`;
  }
}

// Crear instancia del servicio
export const productImageService = new ProductImageService();

// Helper functions para uso directo en componentes
export const uploadProductImages = (productId: string, files: File[]) =>
  productImageService.uploadProductImages(productId, files);

export const getProductImages = (productId: string) =>
  productImageService.getProductImages(productId);

export const deleteProductImage = (imageId: string) =>
  productImageService.deleteProductImage(imageId);

export const validateProductImageFiles = (files: File[], maxFiles?: number, maxSize?: number) =>
  productImageService.validateFiles(files, maxFiles, maxSize);

// Types exports
export type { ProductImage, ProductImageUploadResponse, ProductImageDeleteResponse };