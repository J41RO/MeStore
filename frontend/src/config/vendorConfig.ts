// ~/frontend/src/config/vendorConfig.ts
// ---------------------------------------------------------------------------------------------
// MESTORE - Vendor Configuration (PRODUCTION_READY)
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

/**
 * PRODUCTION_READY: Configuración dinámica vendor orders para hosting
 *
 * Configuración automática según entorno:
 * - Desarrollo: localhost con configuración flexible
 * - Producción: URLs dinámicas desde variables de entorno
 * - Staging: Configuración intermedia para pruebas
 */

interface VendorConfig {
  API_BASE_URL: string;
  ORDER_REFRESH_INTERVAL: number;
  ORDERS_PER_PAGE: number;
  ENABLE_REALTIME: boolean;
  API_TIMEOUT: number;
  RETRY_ATTEMPTS: number;
  CACHE_DURATION: number;
  WEBSOCKET_URL: string;
}

// PRODUCTION_READY: Configuración dinámica por entorno
const getVendorConfig = (): VendorConfig => {
  const isDevelopment = import.meta.env.MODE === 'development';
  const isProduction = import.meta.env.MODE === 'production';

  // TODO_HOSTING: Variables críticas para despliegue
  const baseUrl = import.meta.env.VITE_API_BASE_URL ||
    (isProduction
      ? import.meta.env.VITE_PROD_API_URL || 'https://api.tudominio.com'
      : `http://${import.meta.env.VITE_HOST || 'localhost'}:${import.meta.env.VITE_PORT || '8001'}`
    );

  const wsUrl = import.meta.env.VITE_WEBSOCKET_URL ||
    (isProduction
      ? 'wss://ws.tudominio.com'
      : `ws://${import.meta.env.VITE_HOST || 'localhost'}:${import.meta.env.VITE_PORT || '8001'}/ws`
    );

  return {
    API_BASE_URL: baseUrl,
    ORDER_REFRESH_INTERVAL: parseInt(import.meta.env.VITE_ORDER_REFRESH || '30000'),
    ORDERS_PER_PAGE: parseInt(import.meta.env.VITE_ORDERS_PER_PAGE || '20'),
    ENABLE_REALTIME: import.meta.env.VITE_ENABLE_REALTIME !== 'false',
    API_TIMEOUT: parseInt(import.meta.env.VITE_API_TIMEOUT || '10000'),
    RETRY_ATTEMPTS: parseInt(import.meta.env.VITE_RETRY_ATTEMPTS || '3'),
    CACHE_DURATION: parseInt(import.meta.env.VITE_CACHE_DURATION || '300000'), // 5 minutes
    WEBSOCKET_URL: wsUrl,
  };
};

// Global config instance
export const VENDOR_CONFIG = getVendorConfig();

// Types para TypeScript
export interface VendorOrder {
  id: number;
  order_number: string;
  status: string;
  total_amount: number;
  created_at: string;
  buyer_name?: string;
  items_count?: number;
}

export interface VendorOrderFilters {
  status?: string;
  page?: number;
  limit?: number;
  search?: string;
}

export interface VendorOrderResponse {
  vendor_email: string;
  total_orders: number;
  orders: VendorOrder[];
}

// Status mapping para UI
export const ORDER_STATUS_MAP = {
  pending: {
    label: 'Pendiente',
    color: 'warning',
    bgColor: 'bg-yellow-100',
    textColor: 'text-yellow-800'
  },
  confirmed: {
    label: 'Confirmada',
    color: 'info',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-800'
  },
  processing: {
    label: 'Procesando',
    color: 'primary',
    bgColor: 'bg-purple-100',
    textColor: 'text-purple-800'
  },
  shipped: {
    label: 'Enviada',
    color: 'success',
    bgColor: 'bg-green-100',
    textColor: 'text-green-800'
  },
  delivered: {
    label: 'Entregada',
    color: 'success',
    bgColor: 'bg-emerald-100',
    textColor: 'text-emerald-800'
  },
  cancelled: {
    label: 'Cancelada',
    color: 'danger',
    bgColor: 'bg-red-100',
    textColor: 'text-red-800'
  }
};

export default VENDOR_CONFIG;