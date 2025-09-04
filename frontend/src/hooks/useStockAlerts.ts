import { useState, useEffect, useMemo } from 'react';
import { InventoryItem } from '../types/inventory.types';
import {
  StockAlert,
  AlertType,
  AlertSeverity,
  AlertCategory,
} from '../types/alerts.types';

/**
 * Hook personalizado para generar y gestionar alertas de stock
 * Analiza el inventario y genera alertas automáticamente
 */
export const useStockAlerts = () => {
  // Mock data hasta que inventory esté disponible en store
  const inventory: InventoryItem[] = [];
  const [stockAlerts, setStockAlerts] = useState<StockAlert[]>([]);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  /**
   * Genera alertas de stock basadas en el inventario actual
   */
  const generateStockAlerts = useMemo((): StockAlert[] => {
    const alerts: StockAlert[] = [];

    inventory.forEach((item: InventoryItem) => {
      const alertId = `stock-${item.id}-${Date.now()}`;
      const location = `${item.location.zone} - ${item.location.aisle}-${item.location.shelf}`;
      const timestamp = new Date();

      // Alertas de stock agotado (CRÍTICAS)
      if (item.quantity === 0) {
        alerts.push({
          id: `out-${alertId}`,
          type: AlertType.STOCK,
          category: AlertCategory.OUT_OF_STOCK,
          severity: AlertSeverity.CRITICAL,
          productId: item.productId,
          productName: item.productName,
          currentStock: item.quantity,
          minStock: item.minStock,
          location,
          timestamp,
          isRead: false,
          actionRequired: true,
        });
      }
      // Alertas de stock bajo
      else if (item.quantity <= item.minStock) {
        // Determinar severidad basada en qué tan bajo está el stock
        let severity: AlertSeverity;
        const stockPercentage = (item.quantity / item.minStock) * 100;

        if (stockPercentage <= 25) {
          severity = AlertSeverity.HIGH; // Stock muy bajo (≤25% del mínimo)
        } else if (stockPercentage <= 50) {
          severity = AlertSeverity.MEDIUM; // Stock bajo (≤50% del mínimo)
        } else {
          severity = AlertSeverity.LOW; // Stock en el límite mínimo
        }

        alerts.push({
          id: `out-${alertId}`,
          type: AlertType.STOCK,
          category: AlertCategory.LOW_STOCK,
          severity,
          productId: item.productId,
          productName: item.productName,
          currentStock: item.quantity,
          minStock: item.minStock,
          location,
          timestamp,
          isRead: false,
          actionRequired:
            severity === AlertSeverity.HIGH ||
            severity === AlertSeverity.MEDIUM,
        });
      }
    });

    return alerts.sort((a, b) => {
      // Ordenar por severidad (críticas primero) y luego por timestamp
      const severityOrder = {
        [AlertSeverity.CRITICAL]: 4,
        [AlertSeverity.HIGH]: 3,
        [AlertSeverity.MEDIUM]: 2,
        [AlertSeverity.LOW]: 1,
      };

      if (severityOrder[a.severity] !== severityOrder[b.severity]) {
        return severityOrder[b.severity] - severityOrder[a.severity];
      }

      return b.timestamp.getTime() - a.timestamp.getTime();
    });
  }, [inventory]);

  // Actualizar alertas cuando cambie el inventario
  useEffect(() => {
    setStockAlerts(generateStockAlerts);
    setLastUpdate(new Date());
  }, [generateStockAlerts]);

  /**
   * Estadísticas de alertas de stock
   */
  const stockStats = useMemo(() => {
    const stats = {
      total: stockAlerts.length,
      outOfStock: stockAlerts.filter(
        alert => alert.category === AlertCategory.OUT_OF_STOCK
      ).length,
      lowStock: stockAlerts.filter(
        alert => alert.category === AlertCategory.LOW_STOCK
      ).length,
      critical: stockAlerts.filter(
        alert => alert.severity === AlertSeverity.CRITICAL
      ).length,
      high: stockAlerts.filter(alert => alert.severity === AlertSeverity.HIGH)
        .length,
      medium: stockAlerts.filter(
        alert => alert.severity === AlertSeverity.MEDIUM
      ).length,
      low: stockAlerts.filter(alert => alert.severity === AlertSeverity.LOW)
        .length,
      actionRequired: stockAlerts.filter(alert => alert.actionRequired).length,
    };

    return stats;
  }, [stockAlerts]);

  /**
   * Marcar alerta específica como leída
   */
  const markStockAlertAsRead = (alertId: string) => {
    setStockAlerts(prev =>
      prev.map(alert =>
        alert.id === alertId ? { ...alert, isRead: true } : alert
      )
    );
  };

  /**
   * Marcar todas las alertas como leídas
   */
  const markAllStockAlertsAsRead = () => {
    setStockAlerts(prev => prev.map(alert => ({ ...alert, isRead: true })));
  };

  /**
   * Obtener alertas por severidad
   */
  const getAlertsBySeverity = (severity: AlertSeverity): StockAlert[] => {
    return stockAlerts.filter(alert => alert.severity === severity);
  };

  /**
   * Obtener alertas por categoría
   */
  const getAlertsByCategory = (category: AlertCategory): StockAlert[] => {
    return stockAlerts.filter(alert => alert.category === category);
  };

  /**
   * Refrescar alertas manualmente
   */
  const refreshStockAlerts = () => {
    const newAlerts = generateStockAlerts;
    setStockAlerts(newAlerts);
    setLastUpdate(new Date());
    return newAlerts;
  };

  return {
    // Estado
    stockAlerts,
    stockStats,
    lastUpdate,

    // Métodos
    markStockAlertAsRead,
    markAllStockAlertsAsRead,
    getAlertsBySeverity,
    getAlertsByCategory,
    refreshStockAlerts,

    // Utilidades
    hasStockAlerts: stockAlerts.length > 0,
    hasCriticalAlerts: stockStats.critical > 0,
    hasUnreadAlerts: stockAlerts.some(a => !a.isRead),
  };
};

export default useStockAlerts;
