// ~/frontend/src/services/commissionService.ts
// ---------------------------------------------------------------------------------------------
// MESTORE - Commission Service (PRODUCTION_READY)
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

/**
 * PRODUCTION_READY: Commission Service para integración frontend con API
 * 
 * Proporciona interfaces TypeScript tipadas para:
 * - Gestión de comisiones de vendor
 * - Reportes de earnings y analytics
 * - Historial de transacciones
 * - Cálculos automáticos de comisiones
 */

import axios, { AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.MODE === 'production'
    ? 'https://api.tudominio.com'
    : 'http://localhost:8000');

// Configuración de axios con interceptores
const commissionApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'User-Agent': 'MeStore-Frontend/1.0'
  }
});

// Interceptor para token automático
commissionApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para manejo de errores
commissionApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// =============================================================================
// INTERFACES TYPESCRIPT
// =============================================================================

export interface Commission {
  id: string;
  commission_number: string;
  order_id: number;
  vendor_id: string;
  order_amount: number;
  commission_rate: number;
  commission_amount: number;
  vendor_amount: number;
  platform_amount: number;
  commission_type: 'STANDARD' | 'PREMIUM' | 'PROMOTIONAL' | 'CATEGORY_BASED';
  status: 'PENDING' | 'APPROVED' | 'PAID' | 'DISPUTED' | 'REFUNDED' | 'CANCELLED';
  currency: string;
  calculated_at: string;
  approved_at?: string;
  paid_at?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CommissionListFilters {
  vendor_id?: string;
  status?: string[];
  commission_type?: string[];
  date_from?: string;
  date_to?: string;
  min_amount?: number;
  max_amount?: number;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface CommissionListResponse {
  commissions: Commission[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  summary: {
    total_commission_amount: number;
    total_vendor_earnings: number;
    total_platform_earnings: number;
    pending_count: number;
    paid_count: number;
  };
}

export interface VendorEarningsReport {
  vendor_id: string;
  period: {
    start_date: string;
    end_date: string;
    period_type: string;
  };
  summary: {
    total_commissions: number;
    total_order_amount: number;
    total_commission_amount: number;
    total_vendor_earnings: number;
    paid_earnings: number;
    pending_earnings: number;
    average_commission_rate: number;
  };
  breakdown_by_status: Record<string, {
    count: number;
    total_amount: number;
    commission_amount: number;
  }>;
  currency: string;
}

export interface TransactionHistoryItem {
  id: string;
  transaction_number: string;
  commission_id: string;
  transaction_type: string;
  amount: number;
  status: string;
  processed_at: string;
  gateway_reference?: string;
  commission: {
    commission_number: string;
    order_id: number;
    commission_amount: number;
  };
}

export interface CommissionCalculationRequest {
  order_id: number;
  commission_type?: 'STANDARD' | 'PREMIUM' | 'PROMOTIONAL' | 'CATEGORY_BASED';
  custom_rate?: number;
  notes?: string;
}

export interface ApiError {
  detail: string;
  error_code?: string;
  timestamp?: string;
}

// =============================================================================
// SERVICE CLASS
// =============================================================================

export class CommissionService {
  
  /**
   * Lista comisiones con filtros opcionales
   */
  static async getCommissions(filters: CommissionListFilters = {}): Promise<CommissionListResponse> {
    try {
      const response: AxiosResponse<CommissionListResponse> = await commissionApi.get('/commissions', {
        params: filters
      });
      return response.data;
    } catch (error: any) {
      console.error('Error fetching commissions:', error);
      throw new Error(error.response?.data?.detail || 'Error al obtener comisiones');
    }
  }

  /**
   * Obtiene detalles de una comisión específica
   */
  static async getCommissionById(commissionId: string): Promise<Commission> {
    try {
      const response: AxiosResponse<Commission> = await commissionApi.get(`/commissions/${commissionId}`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching commission details:', error);
      throw new Error(error.response?.data?.detail || 'Error al obtener detalles de comisión');
    }
  }

  /**
   * Obtiene reporte de earnings para un vendor
   */
  static async getVendorEarnings(
    vendorId?: string,
    startDate?: string,
    endDate?: string,
    periodType: string = 'monthly'
  ): Promise<VendorEarningsReport> {
    try {
      const params: any = {
        period_type: periodType
      };
      
      if (vendorId) params.vendor_id = vendorId;
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;

      const response: AxiosResponse<VendorEarningsReport> = await commissionApi.get('/commissions/earnings/summary', {
        params
      });
      return response.data;
    } catch (error: any) {
      console.error('Error fetching vendor earnings:', error);
      throw new Error(error.response?.data?.detail || 'Error al obtener reporte de earnings');
    }
  }

  /**
   * Obtiene historial de transacciones de comisiones
   */
  static async getTransactionHistory(
    commissionId?: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<TransactionHistoryItem[]> {
    try {
      const params: any = {
        limit,
        offset
      };
      
      if (commissionId) params.commission_id = commissionId;

      const response: AxiosResponse<{ transactions: TransactionHistoryItem[] }> = 
        await commissionApi.get('/commissions/transactions/history', { params });
      
      return response.data.transactions;
    } catch (error: any) {
      console.error('Error fetching transaction history:', error);
      throw new Error(error.response?.data?.detail || 'Error al obtener historial de transacciones');
    }
  }

  /**
   * Calcula comisión para una orden (solo admins)
   */
  static async calculateCommission(request: CommissionCalculationRequest): Promise<Commission> {
    try {
      const response: AxiosResponse<Commission> = await commissionApi.post('/commissions/calculate', request);
      return response.data;
    } catch (error: any) {
      console.error('Error calculating commission:', error);
      throw new Error(error.response?.data?.detail || 'Error al calcular comisión');
    }
  }

  /**
   * Aprueba una comisión (solo admins)
   */
  static async approveCommission(commissionId: string, notes?: string): Promise<Commission> {
    try {
      const response: AxiosResponse<Commission> = await commissionApi.patch(`/commissions/${commissionId}/approve`, {
        notes
      });
      return response.data;
    } catch (error: any) {
      console.error('Error approving commission:', error);
      throw new Error(error.response?.data?.detail || 'Error al aprobar comisión');
    }
  }

  // =============================================================================
  // UTILITY METHODS
  // =============================================================================

  /**
   * Formatea un monto a moneda COP
   */
  static formatCurrency(amount: number, currency: string = 'COP'): string {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }

  /**
   * Formatea un porcentaje de comisión
   */
  static formatCommissionRate(rate: number): string {
    return `${(rate * 100).toFixed(2)}%`;
  }

  /**
   * Obtiene el color del estado de comisión para UI
   */
  static getStatusColor(status: Commission['status']): string {
    const colors = {
      PENDING: '#f59e0b',     // amber
      APPROVED: '#10b981',    // emerald
      PAID: '#059669',        // emerald-600
      DISPUTED: '#dc2626',    // red
      REFUNDED: '#6b7280',    // gray
      CANCELLED: '#374151'    // gray-700
    };
    return colors[status] || colors.PENDING;
  }

  /**
   * Obtiene etiqueta legible del estado
   */
  static getStatusLabel(status: Commission['status']): string {
    const labels = {
      PENDING: 'Pendiente',
      APPROVED: 'Aprobada',
      PAID: 'Pagada',
      DISPUTED: 'En Disputa',
      REFUNDED: 'Reembolsada',
      CANCELLED: 'Cancelada'
    };
    return labels[status] || status;
  }

  /**
   * Obtiene etiqueta legible del tipo de comisión
   */
  static getCommissionTypeLabel(type: Commission['commission_type']): string {
    const labels = {
      STANDARD: 'Estándar',
      PREMIUM: 'Premium',
      PROMOTIONAL: 'Promocional',
      CATEGORY_BASED: 'Por Categoría'
    };
    return labels[type] || type;
  }

  /**
   * Valida si el usuario puede ver comisiones
   */
  static canViewCommissions(): boolean {
    const token = localStorage.getItem('access_token');
    if (!token) return false;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return ['admin', 'vendor'].includes(payload.user_type);
    } catch {
      return false;
    }
  }

  /**
   * Valida si el usuario puede calcular comisiones manualmente
   */
  static canCalculateCommissions(): boolean {
    const token = localStorage.getItem('access_token');
    if (!token) return false;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.user_type === 'admin';
    } catch {
      return false;
    }
  }
}

export default CommissionService;