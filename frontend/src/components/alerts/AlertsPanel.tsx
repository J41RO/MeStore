// ~/src/components/alerts/AlertsPanel.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Componente AlertsPanel corregido y funcional
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------

import React, { useState } from 'react';
import { useStockAlerts } from '../../hooks/useStockAlerts';
import { useQualityAlerts } from '../../hooks/useQualityAlerts';
import { useVendorAlerts } from '../../hooks/useVendorAlerts';
import { useSystemAlerts } from '../../hooks/useSystemAlerts';
import {
  AlertsPanelProps,
  AlertsPanelAlert,
  AlertType,
  AlertCategory,
  AlertSeverity,
} from '../../types/alerts.types';
import { Bell, Package, RefreshCw, Filter, User, AlertTriangle } from 'lucide-react';

const AlertsPanel: React.FC<AlertsPanelProps> = ({
  className = '',
  maxAlerts = 50,
  showFilters = false,
  onAlertClick,
}) => {
  const [isLoading, setIsLoading] = useState(false);

  const { stockAlerts, markStockAlertAsRead, refreshStockAlerts } = useStockAlerts();
  const { qualityAlerts, markQualityAlertAsRead } = useQualityAlerts();
  const { vendorAlerts } = useVendorAlerts();
  const { systemAlerts } = useSystemAlerts();

  const allAlerts: AlertsPanelAlert[] = [...stockAlerts, ...qualityAlerts, ...vendorAlerts, ...systemAlerts];
  const displayAlerts = allAlerts.slice(0, maxAlerts);
  const unreadCount = displayAlerts.filter(a => a.isRead === false).length;
  const criticalCount = displayAlerts.filter(a => a.severity === AlertSeverity.CRITICAL && a.isRead === false).length;

  // Función getAlertIcon movida al nivel superior del componente
  const getAlertIcon = (alert: AlertsPanelAlert) => {
    const iconClass = 'h-5 w-5 text-gray-600';
    switch (alert.type) {
      case AlertType.STOCK:
        return <Package className={iconClass} />;
      case AlertType.QUALITY:
        return <Package className={iconClass} />;
      case AlertType.VENDOR:
        return <User className={iconClass} />;
      case AlertType.SYSTEM:
        return <AlertTriangle className={iconClass} />;
      default:
        return <Package className={iconClass} />;
    }
  };

  const refreshAlerts = () => {
    setIsLoading(true);
    try {
      refreshStockAlerts();
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-refresh cada 60 segundos
  React.useEffect(() => {
    const interval = setInterval(() => {
      refreshAlerts();
    }, 60000);
    
    return () => clearInterval(interval);
  }, []);

  const markAsRead = (alertId: string) => {
    if (alertId.includes('stock-')) {
      markStockAlertAsRead(alertId);
    } else {
      markQualityAlertAsRead(alertId);
    }
  };

  const markAllAsRead = () => {
    displayAlerts
      .filter(a => a.isRead === false)
      .forEach(alert => markAsRead(alert.id));
  };

  const handleAlertClick = (alert: AlertsPanelAlert) => {
    markAsRead(alert.id);
    if (onAlertClick) onAlertClick(alert);
  };

  const getSeverityClass = (alert: AlertsPanelAlert) => {
    const base = 'p-4 rounded-lg border-l-4 cursor-pointer transition-all hover:shadow-md ';
    const severity =
      alert.severity === AlertSeverity.CRITICAL
        ? 'border-l-red-500 bg-red-50'
        : alert.severity === AlertSeverity.HIGH
          ? 'border-l-orange-500 bg-orange-50'
          : alert.severity === AlertSeverity.MEDIUM
            ? 'border-l-yellow-500 bg-yellow-50'
            : 'border-l-blue-500 bg-blue-50';
    const opacity = alert.isRead === false ? ' shadow-sm' : ' opacity-75';
    return base + severity + opacity;
  };

  // Función getAlertContent corregida y simplificada
  const getAlertContent = (alert: AlertsPanelAlert) => {
    if (alert.type === AlertType.STOCK) {
      if (alert.category === AlertCategory.OUT_OF_STOCK) {
        return 'Stock agotado';
      } else if (alert.category === AlertCategory.LOW_STOCK) {
        const stockAlert = alert as any;
        return `Stock bajo: ${stockAlert.currentStock || 0}/${stockAlert.minStock || 0}`;
      }
      return 'Alerta de stock';
    } else if (alert.type === AlertType.QUALITY) {
      const qualityAlert = alert as any;
      return qualityAlert.issueDescription || 'Alerta de calidad';
    } else if (alert.type === AlertType.VENDOR) {
      const vendorAlert = alert as any;
      return vendorAlert.issueDescription || 'Alerta de vendedor';
    } else if (alert.type === AlertType.SYSTEM) {
      const systemAlert = alert as any;
      return systemAlert.issueDescription || 'Alerta del sistema';
    }
    return 'Alerta';
  };

  // Función para obtener el nombre apropiado dependiendo del tipo de alerta
  const getAlertTitle = (alert: AlertsPanelAlert) => {
    if (alert.type === AlertType.STOCK) {
      const stockAlert = alert as any;
      return stockAlert.productName || 'Producto';
    } else if (alert.type === AlertType.QUALITY) {
      const qualityAlert = alert as any;
      return qualityAlert.productName || 'Producto';
    } else if (alert.type === AlertType.VENDOR) {
      const vendorAlert = alert as any;
      return vendorAlert.vendorName || 'Vendedor';
    } else if (alert.type === AlertType.SYSTEM) {
      const systemAlert = alert as any;
      return systemAlert.systemComponent || 'Sistema';
    }
    return 'Alerta';
  };

  return (
    <div className={'bg-white rounded-lg shadow-sm border p-6 ' + className}>
      <div className='flex items-center justify-between mb-6'>
        <div className='flex items-center gap-3'>
          <Bell className='h-6 w-6 text-blue-600' />
          <h2 className='text-lg font-semibold text-gray-900'>
            Alertas del Sistema
          </h2>
          <span className='bg-red-100 text-red-800 px-2 py-1 rounded-full text-sm font-medium'>
            {unreadCount}
          </span>
          {criticalCount > 0 && (
            <span className='bg-orange-100 text-orange-800 px-2 py-1 rounded-full text-xs font-bold border border-orange-300'>
              {criticalCount} CRÍTICAS
            </span>
          )}
        </div>

        <div className='flex items-center gap-2'>
          <button
            onClick={refreshAlerts}
            disabled={isLoading}
            aria-label='actualizar alertas'
            className='p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50'
          >
            <RefreshCw
              className={isLoading ? 'h-4 w-4 animate-spin' : 'h-4 w-4'}
            />
          </button>
          {showFilters && (
            <button
              aria-label='filtros'
              className='p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors'
            >
              <Filter className='h-4 w-4' />
            </button>
          )}
        </div>
      </div>

      {unreadCount > 0 && (
        <div className='mb-4'>
          <button
            onClick={markAllAsRead}
            className='text-sm text-blue-600 hover:text-blue-800 font-medium'
          >
            Marcar todas como leídas
          </button>
        </div>
      )}

      {isLoading && (
        <div className='flex items-center justify-center py-8'>
          <div className='animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600'></div>
          <span className='ml-2 text-sm text-gray-500'>
            Cargando alertas...
          </span>
        </div>
      )}

      {isLoading === false && displayAlerts.length === 0 && (
        <div className='text-center py-8'>
          <Bell className='h-12 w-12 text-gray-300 mx-auto mb-4' />
          <h3 className='text-sm font-medium text-gray-900 mb-2'>
            No hay alertas
          </h3>
        </div>
      )}

      {isLoading === false && displayAlerts.length > 0 && (
        <div className='space-y-3'>
          {displayAlerts.map(alert => (
            <div
              key={alert.id}
              onClick={() => handleAlertClick(alert)}
              className={getSeverityClass(alert)}
            >
              <div className='flex items-start gap-3'>
                {getAlertIcon(alert)}
                <div className='flex-1'>
                  <h4 className='text-sm font-medium text-gray-900'>
                    {getAlertTitle(alert)}
                  </h4>
                  <p className='text-sm text-gray-600 mt-1'>
                    {getAlertContent(alert)}
                  </p>
                  <div className='flex items-center gap-4 mt-2 text-xs text-gray-500'>
                    <span>{alert.timestamp.toLocaleTimeString()}</span>
                    {alert.actionRequired && (
                      <span className='px-2 py-1 bg-red-100 text-red-700 rounded-full'>
                        Acción requerida
                      </span>
                    )}
                  </div>
                  <div className='flex items-center gap-2 mt-2'>
                    <button
                      onClick={e => {
                        e.stopPropagation();
                      }}
                      className='text-xs px-2 py-1 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded'
                    >
                      Ver producto
                    </button>
                    {alert.type === AlertType.STOCK && (
                      <button
                        onClick={e => {
                          e.stopPropagation();
                        }}
                        className='text-xs px-2 py-1 text-green-600 hover:text-green-800 hover:bg-green-50 rounded'
                      >
                        Ajustar stock
                      </button>
                    )}
                  </div>
                </div>
                {alert.isRead === false && (
                  <div className='h-2 w-2 bg-blue-600 rounded-full'></div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AlertsPanel;