// ~/frontend/src/types/orders.ts
// PRODUCTION_READY: Tipos TypeScript para sistema de órdenes enterprise

export enum OrderStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed', 
  PROCESSING = 'processing',
  SHIPPED = 'shipped',
  DELIVERED = 'delivered',
  CANCELLED = 'cancelled',
  REFUNDED = 'refunded'
}

export interface OrderItem {
  id: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  product: {
    id: string;
    name: string;
    image_url?: string;
    sku?: string;
  };
  variant_attributes?: Record<string, string>;
}

export interface Order {
  id: string;
  order_number: string;
  status: OrderStatus;
  total_amount: number;
  currency: string;
  
  // Buyer information
  buyer_id: string;
  buyer: {
    id: string;
    email: string;
    nombre: string;
    telefono?: string;
  };
  
  // Shipping information
  shipping_name: string;
  shipping_address: string;
  shipping_city?: string;
  shipping_phone?: string;
  
  // Order items
  items: OrderItem[];
  
  // Timestamps
  created_at: string;
  updated_at: string;
  confirmed_at?: string;
  shipped_at?: string;
  delivered_at?: string;
  
  // Tracking
  tracking_number?: string;
  carrier?: string;
  
  // Payment
  payment_method?: string;
  payment_reference?: string;
  
  // Additional fields
  notes?: string;
  estimated_delivery_days?: number;
}

export interface OrderFilters {
  status?: OrderStatus | 'all';
  search?: string;
  date_from?: string;
  date_to?: string;
  buyer_id?: string;
  page?: number;
  limit?: number;
}

export interface OrdersResponse {
  success: boolean;
  data: {
    orders: Order[];
    total: number;
    page: number;
    limit: number;
    total_pages: number;
  };
  message?: string;
}

export interface OrderResponse {
  success: boolean;
  data: Order;
  message?: string;
}

export interface CreateOrderRequest {
  items: {
    product_id: string;
    quantity: number;
    variant_attributes?: Record<string, string>;
  }[];
  shipping_name: string;
  shipping_address: string;
  shipping_city?: string;
  shipping_phone?: string;
  notes?: string;
}

export interface UpdateOrderStatusRequest {
  status: OrderStatus;
  notes?: string;
  tracking_number?: string;
  carrier?: string;
}

// Tracking types
export interface TrackingEvent {
  type: string;
  timestamp: string;
  date: string;
  time: string;
  location?: string;
  description: string;
  is_estimated: boolean;
  metadata?: Record<string, any>;
  carrier_info?: Record<string, any>;
}

export interface TrackingInfo {
  order_number: string;
  status: string;
  current_location: string;
  estimated_delivery: {
    status: string;
    estimated_date?: string;
    estimated_range?: string;
    confidence?: string;
  };
  tracking_events: TrackingEvent[];
  carrier_info?: {
    name: string;
    tracking_number: string;
    contact: {
      phone: string;
      website: string;
    };
  };
  delivery_address?: {
    city: string;
  };
  tracking_urls: {
    public_url: string;
    carrier_url?: string;
  };
  last_updated: string;
}

export interface TrackingResponse {
  success: boolean;
  data: TrackingInfo;
  message?: string;
}

// API Configuration - PRODUCTION_READY
export const getApiBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_URL;
  const mode = import.meta.env.MODE;
  
  if (envUrl) {
    return envUrl;
  }
  
  if (mode === 'production') {
    // TODO_HOSTING: Configurar dominio real para producción
    return 'https://api.tudominio.com';
  }
  
  return import.meta.env.VITE_API_URL || 
    (import.meta.env.MODE === 'production' 
      ? 'https://api.tudominio.com'  // TODO_HOSTING: Configurar dominio real
      : 'http://192.168.1.137:8000'
    );
};

// Status display configurations
export const ORDER_STATUS_LABELS: Record<OrderStatus, string> = {
  [OrderStatus.PENDING]: 'Pendiente',
  [OrderStatus.CONFIRMED]: 'Confirmada',
  [OrderStatus.PROCESSING]: 'Procesando',
  [OrderStatus.SHIPPED]: 'Enviada',
  [OrderStatus.DELIVERED]: 'Entregada',
  [OrderStatus.CANCELLED]: 'Cancelada',
  [OrderStatus.REFUNDED]: 'Reembolsada'
};

export const ORDER_STATUS_COLORS: Record<OrderStatus, string> = {
  [OrderStatus.PENDING]: 'bg-yellow-100 text-yellow-800',
  [OrderStatus.CONFIRMED]: 'bg-blue-100 text-blue-800',
  [OrderStatus.PROCESSING]: 'bg-purple-100 text-purple-800',
  [OrderStatus.SHIPPED]: 'bg-indigo-100 text-indigo-800',
  [OrderStatus.DELIVERED]: 'bg-green-100 text-green-800',
  [OrderStatus.CANCELLED]: 'bg-gray-100 text-gray-800',
  [OrderStatus.REFUNDED]: 'bg-orange-100 text-orange-800'
};

export const VALID_STATUS_TRANSITIONS: Record<OrderStatus, OrderStatus[]> = {
  [OrderStatus.PENDING]: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
  [OrderStatus.CONFIRMED]: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
  [OrderStatus.PROCESSING]: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
  [OrderStatus.SHIPPED]: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
  [OrderStatus.DELIVERED]: [OrderStatus.REFUNDED],
  [OrderStatus.CANCELLED]: [],
  [OrderStatus.REFUNDED]: []
};