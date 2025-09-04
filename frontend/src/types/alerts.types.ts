// ~/src/types/alerts.types.ts
// ---------------------------------------------------------------------------------------------
// MESTORE - Tipos específicos para AlertsPanel - Sistema de Alertas Completo
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------

// Enums para categorización de alertas
export enum AlertType {
  STOCK = 'stock',
  QUALITY = 'quality',
  SYSTEM = 'system',
  VENDOR = 'vendor',
  // Vendor categories
  PAYMENT_PENDING = 'payment_pending',
  DOCUMENTS_MISSING = 'documents_missing',
  ACTIVATION_REQUIRED = 'activation_required',
  VERIFICATION_PENDING = 'verification_pending',
  // System categories
  API_ERROR = 'api_error',
  DATABASE_ERROR = 'database_error',
  AUTHENTICATION_ERROR = 'authentication_error',
  PERFORMANCE_ISSUE = 'performance_issue',
}

export enum AlertSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum AlertCategory {
  LOW_STOCK = 'low_stock',
  OUT_OF_STOCK = 'out_of_stock',
  EXPIRED_PRODUCT = 'expired_product',
  LOW_RATING = 'low_rating',
  DAMAGED_PRODUCT = 'damaged_product',
}

// Interfaces para alertas específicas
export interface StockAlert {
  id: string;
  type: AlertType.STOCK;
  category: AlertCategory.LOW_STOCK | AlertCategory.OUT_OF_STOCK;
  severity: AlertSeverity;
  productId: string;
  productName: string;
  currentStock: number;
  minStock: number;
  location: string;
  timestamp: Date;
  isRead: boolean;
  actionRequired: boolean;
}

export interface QualityAlert {
  id: string;
  type: AlertType.QUALITY;
  category:
    | AlertCategory.EXPIRED_PRODUCT
    | AlertCategory.LOW_RATING
    | AlertCategory.DAMAGED_PRODUCT;
  severity: AlertSeverity;
  productId: string;
  productName: string;
  issueDescription: string;
  expirationDate?: Date;
  rating?: number;
  timestamp: Date;
  isRead: boolean;
  actionRequired: boolean;
}

export interface VendorAlert {
  id: string;
  type: AlertType.VENDOR;
  category: AlertType.PAYMENT_PENDING | AlertType.DOCUMENTS_MISSING | AlertType.ACTIVATION_REQUIRED | AlertType.VERIFICATION_PENDING;
  severity: AlertSeverity;
  vendorId: string;
  vendorName: string;
  issueDescription: string;
  timestamp: Date;
  isRead: boolean;
  actionRequired: boolean;
}

export interface SystemAlert {
  id: string;
  type: AlertType.SYSTEM;
  category: AlertType.API_ERROR | AlertType.DATABASE_ERROR | AlertType.AUTHENTICATION_ERROR | AlertType.PERFORMANCE_ISSUE;
  severity: AlertSeverity;
  systemComponent: string;
  errorCode?: string;
  issueDescription: string;
  timestamp: Date;
  isRead: boolean;
  actionRequired: boolean;
}

// Tipo base para compatibilidad
export type Alert = StockAlert | QualityAlert | VendorAlert | SystemAlert;

// Union type para todas las alertas (CORREGIDO - incluye todos los tipos)
export type AlertsPanelAlert = StockAlert | QualityAlert | VendorAlert | SystemAlert;

// Props para el componente AlertsPanel
export interface AlertsPanelProps {
  className?: string;
  maxAlerts?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
  showFilters?: boolean;
  onAlertClick?: (alert: AlertsPanelAlert) => void;
}

// Filtros para el panel
export interface AlertsFilter {
  types: AlertType[];
  severities: AlertSeverity[];
  categories: AlertCategory[];
  showRead: boolean;
  showUnread: boolean;
}

// Estadísticas de alertas
export interface AlertsStats {
  total: number;
  unread: number;
  byType: Record<AlertType, number>;
  bySeverity: Record<AlertSeverity, number>;
}