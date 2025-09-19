/**
 * Product API Service for MeStore Frontend
 * Handles all product-related API operations with consistent EntityId types
 */

import { BaseApiService } from './baseApiService';
import type {
  EntityId,
  PaginatedResponse,
  Product,
  CreateProductRequest,
  UpdateProductRequest,
  ProductSearchRequest,
  ProductResponse,
  ProductListResponse,
  ProductFilters,
} from '../types';

// ========================================
// PRODUCT API ENDPOINTS
// ========================================

const PRODUCT_ENDPOINTS = {
  BASE: '/products',
  SEARCH: '/products/search',
  VENDOR_PRODUCTS: '/products/vendor',
  FEATURED: '/products/featured',
  CATEGORIES: '/products/categories',
  BULK_UPDATE: '/products/bulk-update',
  BULK_DELETE: '/products/bulk-delete',
  UPLOAD_IMAGES: '/products/upload-images',
} as const;

// ========================================
// PRODUCT API SERVICE
// ========================================

/**
 * ProductApiService - Complete product API integration
 */
export class ProductApiService extends BaseApiService {
  private readonly endpoints = PRODUCT_ENDPOINTS;

  // ========================================
  // BASIC CRUD OPERATIONS
  // ========================================

  /**
   * Get all products with optional pagination and filters
   */
  async getProducts(params?: ProductSearchRequest): Promise<ProductListResponse> {
    return this.getList<Product>(this.endpoints.BASE, params);
  }

  /**
   * Get a single product by ID
   */
  async getProduct(id: EntityId): Promise<Product> {
    return this.getById<Product>(this.endpoints.BASE, id);
  }

  /**
   * Create a new product
   */
  async createProduct(data: CreateProductRequest): Promise<Product> {
    return this.post<Product, CreateProductRequest>(this.endpoints.BASE, data);
  }

  /**
   * Update an existing product
   */
  async updateProduct(id: EntityId, data: UpdateProductRequest): Promise<Product> {
    return this.put<Product, UpdateProductRequest>(this.endpoints.BASE, id, data);
  }

  /**
   * Partially update a product
   */
  async patchProduct(id: EntityId, data: Partial<UpdateProductRequest>): Promise<Product> {
    return this.patch<Product, Partial<UpdateProductRequest>>(this.endpoints.BASE, id, data);
  }

  /**
   * Delete a product
   */
  async deleteProduct(id: EntityId): Promise<boolean> {
    return this.delete(this.endpoints.BASE, id);
  }

  // ========================================
  // SEARCH AND FILTERING
  // ========================================

  /**
   * Search products with advanced filters
   */
  async searchProducts(request: ProductSearchRequest): Promise<ProductListResponse> {
    const params = this.buildSearchParams(request);
    return this.getList<Product>(this.endpoints.SEARCH, params);
  }

  /**
   * Get products by category
   */
  async getProductsByCategory(categoryId: EntityId, params?: ProductSearchRequest): Promise<ProductListResponse> {
    const searchParams = {
      ...params,
      category_id: categoryId,
    };
    return this.getList<Product>(this.endpoints.BASE, searchParams);
  }

  /**
   * Get featured products
   */
  async getFeaturedProducts(limit: number = 10): Promise<ProductListResponse> {
    return this.getList<Product>(this.endpoints.FEATURED, { limit });
  }

  /**
   * Get products by vendor
   */
  async getVendorProducts(vendorId: EntityId, params?: ProductSearchRequest): Promise<ProductListResponse> {
    const searchParams = {
      ...params,
      vendor_id: vendorId,
    };
    return this.getList<Product>(`${this.endpoints.VENDOR_PRODUCTS}/${vendorId}`, searchParams);
  }

  // ========================================
  // BULK OPERATIONS
  // ========================================

  /**
   * Bulk update multiple products
   */
  async bulkUpdateProducts(updates: Array<{ id: EntityId; data: Partial<UpdateProductRequest> }>): Promise<Product[]> {
    return this.post<Product[], typeof updates>(this.endpoints.BULK_UPDATE, updates);
  }

  /**
   * Bulk delete multiple products
   */
  async bulkDeleteProducts(ids: EntityId[]): Promise<boolean> {
    await this.post<void, { ids: EntityId[] }>(this.endpoints.BULK_DELETE, { ids });
    return true;
  }

  // ========================================
  // IMAGE MANAGEMENT
  // ========================================

  /**
   * Upload product images
   */
  async uploadProductImages(productId: EntityId, files: File[]): Promise<string[]> {
    this.validateEntityId(productId, 'productId');

    const formData = new FormData();
    files.forEach((file, index) => {
      formData.append(`images`, file);
    });
    formData.append('product_id', productId);

    const response = await this.client.post<{ data: string[] }>(
      `${this.endpoints.UPLOAD_IMAGES}/${productId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data.data;
  }

  /**
   * Delete product image
   */
  async deleteProductImage(productId: EntityId, imageId: EntityId): Promise<boolean> {
    this.validateEntityId(productId, 'productId');
    this.validateEntityId(imageId, 'imageId');

    await this.client.delete(`${this.endpoints.BASE}/${productId}/images/${imageId}`);
    return true;
  }

  /**
   * Update image order
   */
  async updateImageOrder(productId: EntityId, imageIds: EntityId[]): Promise<boolean> {
    this.validateEntityId(productId, 'productId');

    await this.client.patch(`${this.endpoints.BASE}/${productId}/images/order`, {
      image_ids: imageIds,
    });
    return true;
  }

  // ========================================
  // BUSINESS OPERATIONS
  // ========================================

  /**
   * Update product stock
   */
  async updateStock(id: EntityId, stock: number): Promise<Product> {
    return this.patch<Product, { stock: number }>(this.endpoints.BASE, id, { stock });
  }

  /**
   * Update product price
   */
  async updatePrice(id: EntityId, price: number): Promise<Product> {
    return this.patch<Product, { price: number }>(this.endpoints.BASE, id, { price });
  }

  /**
   * Toggle product featured status
   */
  async toggleFeatured(id: EntityId): Promise<Product> {
    return this.patch<Product, {}>(this.endpoints.BASE, id, {});
  }

  /**
   * Toggle product active status
   */
  async toggleActive(id: EntityId): Promise<Product> {
    const url = `${this.endpoints.BASE}/${id}/toggle-active`;
    const response = await this.client.patch<ProductResponse>(url);
    return this.extractResponseData(response);
  }

  // ========================================
  // ANALYTICS AND METRICS
  // ========================================

  /**
   * Get product metrics
   */
  async getProductMetrics(id: EntityId): Promise<any> {
    const url = `${this.endpoints.BASE}/${id}/metrics`;
    return this.get<any>(url);
  }

  /**
   * Get vendor product analytics
   */
  async getVendorAnalytics(vendorId: EntityId, period: string = '30d'): Promise<any> {
    const url = `${this.endpoints.VENDOR_PRODUCTS}/${vendorId}/analytics`;
    return this.get<any>(url, { period });
  }

  /**
   * Track product view
   */
  async trackView(id: EntityId): Promise<void> {
    const url = `${this.endpoints.BASE}/${id}/view`;
    await this.client.post(url);
  }

  // ========================================
  // HELPER METHODS
  // ========================================

  /**
   * Build search parameters from ProductSearchRequest
   */
  private buildSearchParams(request: ProductSearchRequest): Record<string, any> {
    const params: Record<string, any> = {};

    if (request.query) params.query = request.query;
    if (request.category_id) params.category_id = request.category_id;
    if (request.vendor_id) params.vendor_id = request.vendor_id;
    if (request.min_price !== undefined) params.min_price = request.min_price;
    if (request.max_price !== undefined) params.max_price = request.max_price;
    if (request.in_stock !== undefined) params.in_stock = request.in_stock;
    if (request.is_featured !== undefined) params.is_featured = request.is_featured;
    if (request.tags && request.tags.length > 0) params.tags = request.tags.join(',');
    if (request.sort_by) params.sort_by = request.sort_by;
    if (request.sort_order) params.sort_order = request.sort_order;
    if (request.page) params.page = request.page;
    if (request.limit) params.limit = request.limit;

    return params;
  }

  /**
   * Build filter parameters from ProductFilters
   */
  private buildFilterParams(filters: ProductFilters): Record<string, any> {
    const params: Record<string, any> = {};

    if (filters.search) params.search = filters.search;
    if (filters.category_id) params.category_id = filters.category_id;
    if (filters.vendor_id) params.vendor_id = filters.vendor_id;
    if (filters.price_range) {
      params.min_price = filters.price_range.min;
      params.max_price = filters.price_range.max;
    }
    if (filters.in_stock !== undefined) params.in_stock = filters.in_stock;
    if (filters.is_featured !== undefined) params.is_featured = filters.is_featured;
    if (filters.is_active !== undefined) params.is_active = filters.is_active;
    if (filters.tags && filters.tags.length > 0) params.tags = filters.tags.join(',');
    if (filters.rating_min !== undefined) params.rating_min = filters.rating_min;

    return params;
  }
}

// ========================================
// SINGLETON INSTANCE
// ========================================

/**
 * Default product API service instance
 */
export const productApiService = new ProductApiService();

// ========================================
// EXPORTS
// ========================================

export default productApiService;