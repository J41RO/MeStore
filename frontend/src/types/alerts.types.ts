// Tipos específicos para AlertsPanel - Sistema de Alertas de Stock y Calidad

// Enums para categorización de alertas
export enum AlertType {
  STOCK = 'stock',
  QUALITY = 'quality',
  SYSTEM = 'system',
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

// Union type para todas las alertas
export type AlertsPanelAlert = StockAlert | QualityAlert;

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
