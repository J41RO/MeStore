/**
 * Order Types for MeStore Frontend
 * Matches backend Order model and API schemas
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

import type { Product } from './product.types';
import type { User } from './auth.types';

// ========================================
// ORDER ENTITY TYPES
// ========================================

/**
 * OrderStatus - Order status enum
 * Matches backend OrderStatus enum
 */
export enum OrderStatus {
  PENDING = 'PENDING',
  CONFIRMED = 'CONFIRMED',
  PROCESSING = 'PROCESSING',
  SHIPPED = 'SHIPPED',
  DELIVERED = 'DELIVERED',
  CANCELLED = 'CANCELLED',
  REFUNDED = 'REFUNDED',
}

/**
 * PaymentStatus - Payment status enum
 */
export enum PaymentStatus {
  PENDING = 'PENDING',
  PROCESSING = 'PROCESSING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  CANCELLED = 'CANCELLED',
  REFUNDED = 'REFUNDED',
}

/**
 * PaymentMethod - Payment method enum
 */
export enum PaymentMethod {
  CREDIT_CARD = 'CREDIT_CARD',
  DEBIT_CARD = 'DEBIT_CARD',
  PSE = 'PSE',
  NEQUI = 'NEQUI',
  DAVIPLATA = 'DAVIPLATA',
  CASH_ON_DELIVERY = 'CASH_ON_DELIVERY',
}

/**
 * Order - Main order entity
 * Matches backend Order model
 */
export interface Order extends BaseEntity {
  id: EntityId;
  order_number: string; // Unique order identifier for customers

  // Customer information
  user_id: EntityId; // Foreign key to User (buyer)
  customer_email: string;
  customer_name: string;
  customer_phone?: string;

  // Order details
  status: OrderStatus;
  total_amount: number;
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  shipping_cost: number;
  currency: string;

  // Payment information
  payment_status: PaymentStatus;
  payment_method?: PaymentMethod;
  payment_reference?: string;
  payment_gateway_id?: string;

  // Shipping information
  shipping_address: ShippingAddress;
  billing_address?: BillingAddress;
  shipping_method?: string;
  tracking_number?: string;
  estimated_delivery?: string;
  delivered_at?: string;

  // Order items
  items: OrderItem[];

  // Processing information
  processing_at?: string;
  processed_by?: EntityId; // Admin/Vendor who processed
  notes?: string;
  customer_notes?: string;

  // Timestamps inherited from BaseEntity
}

/**
 * OrderItem - Individual items within an order
 */
export interface OrderItem extends BaseEntity {
  id: EntityId;
  order_id: EntityId;
  product_id: EntityId;
  vendor_id: EntityId; // For commission tracking

  // Product details (snapshot at time of order)
  product_name: string;
  product_sku: string;
  product_description?: string;
  product_image_url?: string;

  // Pricing and quantity
  quantity: number;
  unit_price: number;
  total_price: number;
  discount_amount: number;

  // Commission tracking
  commission_rate: number;
  commission_amount: number;

  // Product snapshot
  product_snapshot?: Product; // Full product data at time of order
}

/**
 * ShippingAddress - Shipping address information
 */
export interface ShippingAddress {
  recipient_name: string;
  phone?: string;
  address_line_1: string;
  address_line_2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  delivery_instructions?: string;
}

/**
 * BillingAddress - Billing address information
 */
export interface BillingAddress {
  name: string;
  email: string;
  phone?: string;
  address_line_1: string;
  address_line_2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  tax_id?: string; // For business customers
}

// ========================================
// REQUEST/RESPONSE TYPES
// ========================================

/**
 * CreateOrderRequest - Request for creating new order
 */
export interface CreateOrderRequest {
  // Customer info (usually from auth context)
  customer_email?: string;
  customer_name?: string;
  customer_phone?: string;

  // Order items
  items: CreateOrderItemRequest[];

  // Addresses
  shipping_address: ShippingAddress;
  billing_address?: BillingAddress;

  // Payment and shipping
  payment_method: PaymentMethod;
  shipping_method?: string;

  // Optional fields
  customer_notes?: string;
  discount_code?: string;
}

/**
 * CreateOrderItemRequest - Request for order item
 */
export interface CreateOrderItemRequest {
  product_id: EntityId;
  quantity: number;
  // unit_price calculated by backend from current product price
}

/**
 * UpdateOrderRequest - Request for updating order
 */
export interface UpdateOrderRequest extends PartialEntity<Order> {
  id: EntityId;
  // Most fields optional for updates
  status?: OrderStatus;
  tracking_number?: string;
  notes?: string;
  shipping_address?: Partial<ShippingAddress>;
}

/**
 * OrderSearchRequest - Request for searching orders
 */
export interface OrderSearchRequest {
  user_id?: EntityId; // Filter by customer
  vendor_id?: EntityId; // Filter by vendor (for vendor dashboard)
  status?: OrderStatus[];
  payment_status?: PaymentStatus[];
  payment_method?: PaymentMethod[];
  order_number?: string;
  customer_email?: string;
  date_from?: string;
  date_to?: string;
  min_amount?: number;
  max_amount?: number;
  sort_by?: OrderSortField;
  sort_order?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

/**
 * OrderResponse - Single order response
 */
export interface OrderResponse extends StandardResponse<Order> {}

/**
 * OrderListResponse - Order list response
 */
export interface OrderListResponse extends PaginatedResponse<Order> {}

// ========================================
// FILTER AND SORT TYPES
// ========================================

/**
 * OrderSortField - Available fields for sorting orders
 */
export type OrderSortField =
  | 'created_at'
  | 'updated_at'
  | 'order_number'
  | 'total_amount'
  | 'status'
  | 'customer_name'
  | 'customer_email';

/**
 * OrderFilters - Filters for order lists
 */
export interface OrderFilters {
  status?: OrderStatus[];
  payment_status?: PaymentStatus[];
  payment_method?: PaymentMethod[];
  customer_search?: string; // Search by name or email
  order_number?: string;
  date_range?: {
    from: string;
    to: string;
  };
  amount_range?: {
    min: number;
    max: number;
  };
}

/**
 * OrderSort - Sorting configuration
 */
export interface OrderSort {
  field: OrderSortField;
  direction: 'asc' | 'desc';
}

// ========================================
// STATE MANAGEMENT TYPES
// ========================================

/**
 * OrderState - State for order management
 */
export interface OrderState extends AsyncState<EntityCollection<Order>> {
  // Selected order for details/editing
  selectedOrder: Order | null;

  // Filters and search
  filters: OrderFilters;
  sort: OrderSort;
  searchQuery: string;

  // UI state
  showFilters: boolean;

  // Form state
  isCreating: boolean;
  isUpdating: boolean;
  createError: string | null;
  updateError: string | null;

  // Current user context (buyer, vendor, admin)
  userRole?: 'buyer' | 'vendor' | 'admin';
  currentUserId?: EntityId;
}

/**
 * OrderActions - Actions for order management
 */
export interface OrderActions {
  // Fetch operations
  fetchOrders: (params?: OrderSearchRequest) => Promise<void>;
  fetchOrder: (id: EntityId) => Promise<Order | null>;
  fetchUserOrders: (userId: EntityId) => Promise<void>;
  fetchVendorOrders: (vendorId: EntityId) => Promise<void>;

  // CRUD operations
  createOrder: (data: CreateOrderRequest) => Promise<Order | null>;
  updateOrder: (id: EntityId, data: UpdateOrderRequest) => Promise<Order | null>;
  cancelOrder: (id: EntityId, reason?: string) => Promise<boolean>;

  // Status updates
  updateOrderStatus: (id: EntityId, status: OrderStatus) => Promise<boolean>;
  updatePaymentStatus: (id: EntityId, status: PaymentStatus) => Promise<boolean>;
  addTrackingNumber: (id: EntityId, trackingNumber: string) => Promise<boolean>;

  // Selection and UI
  selectOrder: (order: Order | null) => void;
  setFilters: (filters: Partial<OrderFilters>) => void;
  setSort: (sort: OrderSort) => void;
  setSearchQuery: (query: string) => void;
  toggleFilters: () => void;

  // State management
  clearOrders: () => void;
  clearErrors: () => void;
  reset: () => void;
}

/**
 * OrderStore - Complete order store interface
 */
export interface OrderStore extends OrderState, OrderActions {}

// ========================================
// COMPONENT PROPS TYPES
// ========================================

/**
 * OrderCardProps - Order card component props
 */
export interface OrderCardProps {
  order: Order;
  showCustomer?: boolean;
  showActions?: boolean;
  onClick?: (order: Order) => void;
  onStatusUpdate?: (order: Order, status: OrderStatus) => void;
  onCancel?: (order: Order) => void;
  className?: string;
}

/**
 * OrderListProps - Order list component props
 */
export interface OrderListProps {
  orders: Order[];
  loading?: boolean;
  error?: string | null;
  showCustomer?: boolean;
  showActions?: boolean;
  userRole?: 'buyer' | 'vendor' | 'admin';
  onOrderClick?: (order: Order) => void;
  onStatusUpdate?: (order: Order, status: OrderStatus) => void;
  onCancel?: (order: Order) => void;
  className?: string;
}

/**
 * OrderDetailsProps - Order details component props
 */
export interface OrderDetailsProps {
  order: Order;
  loading?: boolean;
  error?: string | null;
  userRole?: 'buyer' | 'vendor' | 'admin';
  onStatusUpdate?: (status: OrderStatus) => void;
  onCancel?: (reason?: string) => void;
  onAddTracking?: (trackingNumber: string) => void;
  className?: string;
}

/**
 * OrderStatusIndicatorProps - Order status indicator props
 */
export interface OrderStatusIndicatorProps {
  status: OrderStatus;
  paymentStatus?: PaymentStatus;
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  className?: string;
}

/**
 * OrderFiltersProps - Order filters component props
 */
export interface OrderFiltersProps {
  filters: OrderFilters;
  userRole?: 'buyer' | 'vendor' | 'admin';
  onFiltersChange: (filters: Partial<OrderFilters>) => void;
  onReset?: () => void;
  className?: string;
}

// ========================================
// BUSINESS LOGIC TYPES
// ========================================

/**
 * OrderSummary - Order summary calculations
 */
export interface OrderSummary {
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  shipping_cost: number;
  total_amount: number;
  item_count: number;
  currency: string;
}

/**
 * OrderMetrics - Order performance metrics
 */
export interface OrderMetrics {
  total_orders: number;
  total_revenue: number;
  average_order_value: number;
  orders_by_status: Record<OrderStatus, number>;
  orders_by_payment_status: Record<PaymentStatus, number>;
  recent_orders_count: number;
  pending_orders_count: number;
}

/**
 * Commission tracking for vendors
 */
export interface OrderCommission {
  order_id: EntityId;
  vendor_id: EntityId;
  total_commission: number;
  commission_rate: number;
  commission_status: 'pending' | 'calculated' | 'paid';
  items: OrderItem[];
}

// Export all types
export type {
  OrderStatus,
  PaymentStatus,
  PaymentMethod,
  Order,
  OrderItem,
  ShippingAddress,
  BillingAddress,
  CreateOrderRequest,
  CreateOrderItemRequest,
  UpdateOrderRequest,
  OrderSearchRequest,
  OrderResponse,
  OrderListResponse,
  OrderSortField,
  OrderFilters,
  OrderSort,
  OrderState,
  OrderActions,
  OrderStore,
  OrderCardProps,
  OrderListProps,
  OrderDetailsProps,
  OrderStatusIndicatorProps,
  OrderFiltersProps,
  OrderSummary,
  OrderMetrics,
  OrderCommission,
};