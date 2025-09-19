/**
 * Product Types for MeStore Frontend
 * Matches backend Product model and API schemas
 */

import type {
  EntityId,
  BaseEntity,
  CreateEntity,
  PartialEntity,
  StandardResponse,
  PaginatedResponse,
  EntityCollection,
  AsyncState,
} from './core.types';

// ========================================
// PRODUCT ENTITY TYPES
// ========================================

/**
 * Product - Main product entity
 * Matches backend Product model
 */
export interface Product extends BaseEntity {
  id: EntityId;
  vendor_id: EntityId; // Foreign key to User (vendor)
  sku: string;
  name: string;
  description: string;
  price: number;
  stock: number;
  category_id?: EntityId; // Foreign key to Category
  category_name?: string; // Denormalized for display

  // Pricing fields
  precio_venta: number;
  precio_costo?: number;
  comision_mestocker?: number;

  // Physical properties
  peso?: number;
  dimensiones?: ProductDimensions;

  // Status and flags
  is_active: boolean;
  is_featured: boolean;
  is_digital: boolean;

  // SEO and metadata
  slug?: string;
  meta_title?: string;
  meta_description?: string;
  tags?: string[];

  // Images
  images: ProductImage[];
  main_image_url?: string;

  // Business metrics
  sales_count: number;
  view_count: number;
  rating: number;
  review_count: number;

  // Timestamps inherited from BaseEntity
}

/**
 * ProductImage - Product image entity
 */
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
  alt_text?: string;
  is_primary: boolean;
}

/**
 * ProductDimensions - Product physical dimensions
 */
export interface ProductDimensions {
  length: number;
  width: number;
  height: number;
  unit: 'cm' | 'inch' | 'm';
}

/**
 * ProductVariant - Product variants (size, color, etc.)
 */
export interface ProductVariant extends BaseEntity {
  id: EntityId;
  product_id: EntityId;
  name: string;
  value: string;
  price_adjustment: number;
  stock_adjustment: number;
  sku_suffix?: string;
  is_active: boolean;
}

// ========================================
// REQUEST/RESPONSE TYPES
// ========================================

/**
 * CreateProductRequest - Request for creating new product
 */
export interface CreateProductRequest extends CreateEntity<Product> {
  // Excludes auto-generated fields
  vendor_id: EntityId;
  sku: string;
  name: string;
  description: string;
  price: number;
  stock: number;
  category_id?: EntityId;

  // Optional fields
  precio_costo?: number;
  peso?: number;
  dimensiones?: ProductDimensions;
  tags?: string[];
  is_featured?: boolean;
  is_digital?: boolean;

  // Image upload
  image_files?: File[];
}

/**
 * UpdateProductRequest - Request for updating existing product
 */
export interface UpdateProductRequest extends PartialEntity<Product> {
  id: EntityId;
  // All other fields optional
}

/**
 * ProductSearchRequest - Request for searching products
 */
export interface ProductSearchRequest {
  query?: string;
  category_id?: EntityId;
  vendor_id?: EntityId;
  min_price?: number;
  max_price?: number;
  in_stock?: boolean;
  is_featured?: boolean;
  tags?: string[];
  sort_by?: ProductSortField;
  sort_order?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

/**
 * ProductResponse - Single product response
 */
export interface ProductResponse extends StandardResponse<Product> {}

/**
 * ProductListResponse - Product list response
 */
export interface ProductListResponse extends PaginatedResponse<Product> {}

// ========================================
// FILTER AND SORT TYPES
// ========================================

/**
 * ProductSortField - Available fields for sorting products
 */
export type ProductSortField =
  | 'name'
  | 'price'
  | 'created_at'
  | 'updated_at'
  | 'sales_count'
  | 'rating'
  | 'view_count';

/**
 * ProductFilters - Filters for product lists
 */
export interface ProductFilters {
  search?: string;
  category_id?: EntityId;
  vendor_id?: EntityId;
  price_range?: {
    min: number;
    max: number;
  };
  in_stock?: boolean;
  is_featured?: boolean;
  is_active?: boolean;
  tags?: string[];
  rating_min?: number;
}

/**
 * ProductSort - Sorting configuration
 */
export interface ProductSort {
  field: ProductSortField;
  direction: 'asc' | 'desc';
}

// ========================================
// STATE MANAGEMENT TYPES
// ========================================

/**
 * ProductState - State for product management
 */
export interface ProductState extends AsyncState<EntityCollection<Product>> {
  // Selected product for details/editing
  selectedProduct: Product | null;

  // Filters and search
  filters: ProductFilters;
  sort: ProductSort;
  searchQuery: string;

  // UI state
  viewMode: 'grid' | 'list';
  showFilters: boolean;

  // Form state
  isCreating: boolean;
  isUpdating: boolean;
  createError: string | null;
  updateError: string | null;
}

/**
 * ProductActions - Actions for product management
 */
export interface ProductActions {
  // Fetch operations
  fetchProducts: (params?: ProductSearchRequest) => Promise<void>;
  fetchProduct: (id: EntityId) => Promise<Product | null>;

  // CRUD operations
  createProduct: (data: CreateProductRequest) => Promise<Product | null>;
  updateProduct: (id: EntityId, data: UpdateProductRequest) => Promise<Product | null>;
  deleteProduct: (id: EntityId) => Promise<boolean>;

  // Selection and UI
  selectProduct: (product: Product | null) => void;
  setFilters: (filters: Partial<ProductFilters>) => void;
  setSort: (sort: ProductSort) => void;
  setSearchQuery: (query: string) => void;
  setViewMode: (mode: 'grid' | 'list') => void;
  toggleFilters: () => void;

  // State management
  clearProducts: () => void;
  clearErrors: () => void;
  reset: () => void;
}

/**
 * ProductStore - Complete product store interface
 */
export interface ProductStore extends ProductState, ProductActions {}

// ========================================
// COMPONENT PROPS TYPES
// ========================================

/**
 * ProductCardProps - Product card component props
 */
export interface ProductCardProps {
  product: Product;
  showVendor?: boolean;
  showActions?: boolean;
  onClick?: (product: Product) => void;
  onEdit?: (product: Product) => void;
  onDelete?: (product: Product) => void;
  className?: string;
}

/**
 * ProductListProps - Product list component props
 */
export interface ProductListProps {
  products: Product[];
  loading?: boolean;
  error?: string | null;
  viewMode?: 'grid' | 'list';
  showVendor?: boolean;
  showActions?: boolean;
  onProductClick?: (product: Product) => void;
  onProductEdit?: (product: Product) => void;
  onProductDelete?: (product: Product) => void;
  className?: string;
}

/**
 * ProductFormProps - Product form component props
 */
export interface ProductFormProps {
  product?: Product | null; // null for create, Product for edit
  loading?: boolean;
  error?: string | null;
  onSubmit: (data: CreateProductRequest | UpdateProductRequest) => void;
  onCancel?: () => void;
  className?: string;
}

/**
 * ProductFiltersProps - Product filters component props
 */
export interface ProductFiltersProps {
  filters: ProductFilters;
  onFiltersChange: (filters: Partial<ProductFilters>) => void;
  onReset?: () => void;
  className?: string;
}

// ========================================
// BUSINESS LOGIC TYPES
// ========================================

/**
 * ProductPricing - Product pricing calculations
 */
export interface ProductPricing {
  precio_venta: number;
  precio_costo: number;
  comision_mestocker: number;
  margen_bruto: number;
  porcentaje_margen: number;
}

/**
 * ProductMetrics - Product performance metrics
 */
export interface ProductMetrics {
  sales_count: number;
  revenue_total: number;
  view_count: number;
  conversion_rate: number;
  rating: number;
  review_count: number;
  stock_level: number;
  low_stock_threshold: number;
  is_low_stock: boolean;
}

/**
 * ProductInventory - Product inventory status
 */
export interface ProductInventory {
  stock_current: number;
  stock_reserved: number;
  stock_available: number;
  low_stock_threshold: number;
  is_low_stock: boolean;
  is_out_of_stock: boolean;
  reorder_point: number;
  reorder_quantity: number;
}

// Export all types
export type {
  Product,
  ProductImage,
  ProductDimensions,
  ProductVariant,
  CreateProductRequest,
  UpdateProductRequest,
  ProductSearchRequest,
  ProductResponse,
  ProductListResponse,
  ProductSortField,
  ProductFilters,
  ProductSort,
  ProductState,
  ProductActions,
  ProductStore,
  ProductCardProps,
  ProductListProps,
  ProductFormProps,
  ProductFiltersProps,
  ProductPricing,
  ProductMetrics,
  ProductInventory,
};