// ====================================================================
// COMMISSION TYPES - Sistema completo de tipos para comisiones
// ====================================================================

// Enums para tipos de comisiones
export enum CommissionType {
  SALE = 'sale',
  PRODUCT = 'product', 
  VOLUME = 'volume',
  BONUS = 'bonus',
  TIER = 'tier'
}
export enum PaymentMethod {
  CREDIT_CARD = 'credit_card',
  DEBIT_CARD = 'debit_card', 
  CASH = 'cash',
  BANK_TRANSFER = 'bank_transfer',
  PAYPAL = 'paypal'
}

export enum CommissionStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  PAID = 'paid',
  CANCELLED = 'cancelled'
}

// ====================================================================
// INTERFACES PRINCIPALES
// ====================================================================

// Interface principal para una comisión individual
export interface Commission {
  id: string;
  productId: string;
  productName: string;
  productCategory: string;
  saleAmount: number;
  commissionRate: number;
  commissionAmount: number;
  commissionType: CommissionType;
  status: CommissionStatus;
  saleDate: Date;
  paidDate?: Date;
  vendorId: string;
  vendorName: string;
  orderId: string;
  customerName?: string;
  notes?: string;
}

// ====================================================================
// BREAKDOWN INTERFACES - Por diferentes dimensiones
// ====================================================================

// Breakdown por producto
export interface CommissionBreakdownByProduct {
  productId: string;
  productName: string;
  category: string;
  totalSales: number;
  totalCommissions: number;
  commissionCount: number;
  averageCommissionRate: number;
  topCommissionAmount: number;
}

// Breakdown por período temporal
export interface CommissionBreakdownByPeriod {
  period: string; // "2025-01" o "2025-01-15"
  periodType: 'month' | 'week' | 'day';
  totalCommissions: number;
  commissionCount: number;
  totalSales: number;
  averageCommissionRate: number;
  topProduct: string;
}

// Breakdown por tipo de comisión
export interface CommissionBreakdownByType {
  type: CommissionType;
  totalCommissions: number;
  commissionCount: number;
  percentage: number;
  averageAmount: number;
}

// ====================================================================
// BREAKDOWN PRINCIPAL - Interface completa
// ====================================================================

export interface CommissionBreakdown {
  byProduct: CommissionBreakdownByProduct[];
  byPeriod: CommissionBreakdownByPeriod[];
  byType: CommissionBreakdownByType[];
  byCategory: { [category: string]: number };
  totals: {
    totalCommissions: number;
    totalSales: number;
    commissionCount: number;
    averageCommissionRate: number;
    topProduct: string;
    topCategory: string;
  };
}

// ====================================================================
// FILTROS Y CONFIGURACIÓN
// ====================================================================

// Interface para filtros avanzados
export interface CommissionFilters {
  dateRange?: {
    start: Date;
    end: Date;
  };
  productIds?: string[];
  categories?: string[];
  types?: CommissionType[];
  statuses?: CommissionStatus[];
  minAmount?: number;
  maxAmount?: number;
  searchTerm?: string;  paymentMethods?: PaymentMethod[];
}

// Props para el componente principal
export interface CommissionReportProps {
  className?: string;
  showExport?: boolean;
  showFilters?: boolean;
  defaultFilters?: CommissionFilters;
}

// ====================================================================
// TIPOS AUXILIARES - Para charts y exportación
// ====================================================================

export interface ChartDataPoint {
  name: string;
  value: number;
  label: string;
  color?: string;
}

export interface ExportOptions {
  format: 'csv' | 'xlsx' | 'pdf';
  includeCharts: boolean;
  dateRange?: {
    start: Date;
    end: Date;
  };
}

// ====================================================================
// TYPE GUARDS - Para validación en runtime
// ====================================================================

export const isCommission = (obj: any): obj is Commission => {
  return obj && 
    typeof obj.id === 'string' &&
    typeof obj.productName === 'string' &&
    typeof obj.commissionAmount === 'number' &&
    Object.values(CommissionType).includes(obj.commissionType);
};

export const isCommissionStatus = (status: string): status is CommissionStatus => {
  return Object.values(CommissionStatus).includes(status as CommissionStatus);
};

export const isCommissionType = (type: string): type is CommissionType => {
  return Object.values(CommissionType).includes(type as CommissionType);
};