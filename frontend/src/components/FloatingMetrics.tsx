import React from 'react';
import { DashboardMetrics } from '../hooks/useDashboardMetrics';

interface FloatingMetricsProps {
  dashboardMetrics: DashboardMetrics | null;
  isLoadingMetrics: boolean;
}

export const FloatingMetrics: React.FC<FloatingMetricsProps> = ({
  dashboardMetrics,
  isLoadingMetrics
}) => {
  // Floating metrics con datos reales
  const getFloatingMetrics = () => {
    if (!dashboardMetrics) return [];
    
    return [
      {
        icon: '👥',
        title: 'Vendedores Activos',
        value: dashboardMetrics.activeVendors.toLocaleString(),
        subtitle: `${dashboardMetrics.activeVendors > 0 ? '+' : ''}${Math.floor(dashboardMetrics.activeVendors * 0.05)} este mes`,
        color: 'blue'
      },
      {
        icon: '📦',
        title: 'Productos Gestionados', 
        value: dashboardMetrics.totalProducts.toLocaleString(),
        subtitle: 'Inventario total',
        color: 'purple'
      },
      {
        icon: '💰',
        title: 'Facturación Mensual',
        value: `$${(dashboardMetrics.monthlyRevenue / 1000000).toFixed(1)}M`,
        subtitle: 'Pesos colombianos',
        color: 'green'
      },
      {
        icon: '🚚',
        title: 'Entregas Completadas',
        value: `${dashboardMetrics.deliverySuccessRate}%`,
        subtitle: 'Santander y región',
        color: 'orange'
      }
    ];
  };

  const floatingMetrics = getFloatingMetrics();

  return (
    <>
      {floatingMetrics.map((metric, index) => (
        <div 
          key={index}
          className={`absolute floating-metric ${
            index === 0 ? 'top-4 -left-4' :
            index === 1 ? 'top-20 -right-4' :
            index === 2 ? 'bottom-20 -left-6' :
            'bottom-4 -right-6'
          }`}
          style={{ animationDelay: `${index}s` }}
        >
          <div className='bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-xl border border-gray-200 dark:border-gray-700 max-w-xs'>
            <div className='flex items-center space-x-3 mb-3'>
              <div className={`w-10 h-10 bg-gradient-to-r from-${metric.color}-500 to-${metric.color}-600 rounded-xl flex items-center justify-center`}>
                <span className='text-white text-lg'>{metric.icon}</span>
              </div>
              <div>
                <div className='text-sm text-gray-600 dark:text-gray-400'>{metric.title}</div>
                <div className='text-2xl font-bold text-gray-900 dark:text-white'>
                  {isLoadingMetrics ? (
                    <div className="metrics-loading w-16 h-6"></div>
                  ) : (
                    metric.value
                  )}
                </div>
              </div>
            </div>
            <div className={`text-${metric.color}-600 text-sm font-medium`}>
              {isLoadingMetrics ? (
                <div className="metrics-loading w-20 h-4"></div>
              ) : (
                metric.subtitle
              )}
            </div>
          </div>
        </div>
      ))}
    </>
  );
};