import { useState, useEffect, useMemo } from 'react';
import { QualityAlert, AlertType, AlertSeverity, AlertCategory } from '../types/alerts.types';

/**
 * Hook para generar y gestionar alertas de calidad de productos
 */
export const useQualityAlerts = () => {
  // Mock data hasta que products esté disponible en store
  const products: any[] = [];
  const [qualityAlerts, setQualityAlerts] = useState<QualityAlert[]>([]);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  /**
   * Genera alertas de calidad basadas en productos
   */
  const generateQualityAlerts = useMemo((): QualityAlert[] => {
    const alerts: QualityAlert[] = [];
    const now = new Date();

    products.forEach((product: any) => {
      const alertId = `quality-${product.id}-${Date.now()}`;
      const timestamp = new Date();

      // Alertas de productos vencidos o próximos a vencer
      if (product.expirationDate) {
        const expDate = new Date(product.expirationDate);
        const daysUntilExpiration = Math.ceil((expDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

        if (daysUntilExpiration <= 0) {
          // Producto vencido
          alerts.push({
            id: `expired-${alertId}`,
            type: AlertType.QUALITY,
            category: AlertCategory.EXPIRED_PRODUCT,
            severity: AlertSeverity.CRITICAL,
            productId: product.id,
            productName: product.name,
            issueDescription: `Producto vencido hace ${Math.abs(daysUntilExpiration)} días`,
            expirationDate: expDate,
            timestamp,
            isRead: false,
            actionRequired: true
          });
        } else if (daysUntilExpiration <= 7) {
          // Producto próximo a vencer (7 días o menos)
          alerts.push({
            id: `expired-${alertId}`,
            type: AlertType.QUALITY,
            category: AlertCategory.EXPIRED_PRODUCT,
            severity: daysUntilExpiration <= 3 ? AlertSeverity.HIGH : AlertSeverity.MEDIUM,
            productId: product.id,
            productName: product.name,
            issueDescription: `Producto vencido hace ${Math.abs(daysUntilExpiration)} días`,
            expirationDate: expDate,
            timestamp,
            isRead: false,
            actionRequired: daysUntilExpiration <= 3
          });
        }
      }

      // Alertas de rating bajo
      if (product.rating && product.rating < 3.0) {
        const severity = product.rating < 2.0 ? AlertSeverity.HIGH : 
                        product.rating < 2.5 ? AlertSeverity.MEDIUM : AlertSeverity.LOW;

        alerts.push({
          id: `rating-${alertId}`,
          type: AlertType.QUALITY,
          category: AlertCategory.LOW_RATING,
          severity,
          productId: product.id,
          productName: product.name,
          issueDescription: `Rating bajo: ${product.rating}/5.0 estrellas`,
          rating: product.rating,
          timestamp,
          isRead: false,
          actionRequired: product.rating < 2.5
        });
      }

      // Alertas de productos dañados (si existe el campo)
      if (product.damaged || product.condition === 'damaged') {
        alerts.push({
          id: `rating-${alertId}`,
          type: AlertType.QUALITY,
          category: AlertCategory.DAMAGED_PRODUCT,
          severity: AlertSeverity.HIGH,
          productId: product.id,
          productName: product.name,
          issueDescription: 'Producto reportado como dañado',
          timestamp,
          isRead: false,
          actionRequired: true
        });
      }
    });

    return alerts.sort((a, b) => {
      const severityOrder = {
        [AlertSeverity.CRITICAL]: 4,
        [AlertSeverity.HIGH]: 3,
        [AlertSeverity.MEDIUM]: 2,
        [AlertSeverity.LOW]: 1
      };
      
      if (severityOrder[a.severity] !== severityOrder[b.severity]) {
        return severityOrder[b.severity] - severityOrder[a.severity];
      }
      
      return b.timestamp.getTime() - a.timestamp.getTime();
    });
  }, [products]);

  // Actualizar alertas cuando cambien los productos
  useEffect(() => {
    setQualityAlerts(generateQualityAlerts);
    setLastUpdate(new Date());
  }, [generateQualityAlerts]);

  /**
   * Estadísticas de alertas de calidad
   */
  const qualityStats = useMemo(() => ({
    total: qualityAlerts.length,
    expired: qualityAlerts.filter(alert => alert.category === AlertCategory.EXPIRED_PRODUCT).length,
    lowRating: qualityAlerts.filter(alert => alert.category === AlertCategory.LOW_RATING).length,
    damaged: qualityAlerts.filter(alert => alert.category === AlertCategory.DAMAGED_PRODUCT).length,
    critical: qualityAlerts.filter(alert => alert.severity === AlertSeverity.CRITICAL).length,
    actionRequired: qualityAlerts.filter(alert => alert.actionRequired).length
  }), [qualityAlerts]);

  /**
   * Marcar alerta como leída
   */
  const markQualityAlertAsRead = (alertId: string) => {
    setQualityAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, isRead: true } : alert
    ));
  };

  return {
    qualityAlerts,
    qualityStats,
    lastUpdate,
    markQualityAlertAsRead,
    hasQualityAlerts: qualityAlerts.length > 0,
    hasCriticalQualityAlerts: qualityStats.critical > 0
  };
};

export default useQualityAlerts;