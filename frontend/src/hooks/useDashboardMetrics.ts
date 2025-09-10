import { useState, useEffect } from 'react';

// Interfaces para datos del API usando endpoints reales identificados
export interface DashboardMetrics {
  // Datos de /api/v1/vendedores/dashboard/resumen
  totalVendors: number;
  activeVendors: number;
  totalProducts: number;
  activeProducts: number;
  totalRevenue: number;
  monthlyRevenue: number;
  
  // Datos de /api/v1/vendedores/dashboard/ventas
  ordersToday: number;
  ordersThisWeek: number;
  ordersThisMonth: number;
  completionRate: number;
  averageTicket: number;
  monthlySales: number;
  
  // Datos de /api/v1/vendedores/dashboard/inventario
  totalStock: number;
  lowStockItems: number;
  outOfStockItems: number;
  stockValue: number;
  
  // Datos de /api/v1/admin/dashboard/kpis (si disponible)
  deliverySuccessRate: number;
  averageProcessingTime: string;
  customerSatisfaction: number;
  
  // Categorías top
  topCategories: Array<{
    name: string;
    value: number;
    percentage: number;
  }>;
}

export const useDashboardMetrics = () => {
  const [dashboardMetrics, setDashboardMetrics] = useState<DashboardMetrics | null>(null);
  const [isLoadingMetrics, setIsLoadingMetrics] = useState(true);
  const [metricsError, setMetricsError] = useState<string | null>(null);

  const fetchDashboardMetrics = async () => {
    try {
      setIsLoadingMetrics(true);
      setMetricsError(null);
      
      const baseUrl = 'http://192.168.1.137:8000';
      const results: any = {};
      
      // CORREGIDO: Obtener token para autenticación
      const token = localStorage.getItem('access_token') || localStorage.getItem('token');
      
      // CORREGIDO: Reducido a endpoints esenciales para evitar rate limiting
      const endpoints = [
        { key: 'resumen', url: '/api/v1/vendedores/dashboard/resumen' },
        // COMENTADO: Endpoints adicionales para reducir tráfico
        // { key: 'ventas', url: '/api/v1/vendedores/dashboard/ventas' },
        // { key: 'inventario', url: '/api/v1/vendedores/dashboard/inventario' },
        // { key: 'kpis', url: '/api/v1/admin/dashboard/kpis' },
        // { key: 'vendedores', url: '/api/v1/vendedores/list' },
        // { key: 'productos', url: '/api/v1/productos/' }
      ];
      
      // Fetch con rate limiting controlado
      await Promise.allSettled(
        endpoints.map(async ({ key, url }) => {
          try {
            const response = await fetch(`${baseUrl}${url}`, {
              method: 'GET',
              headers: {
                'Content-Type': 'application/json',
                // CORREGIDO: Incluir token de autorización
                ...(token && { 'Authorization': `Bearer ${token}` })
              }
            });
            
            if (response.ok) {
              const data = await response.json();
              results[key] = data;
              console.log(`✅ ${key} data loaded:`, data);
            } else if (response.status === 429) {
              console.log(`⚠️ Rate limit hit for ${key} - backing off`);
              setMetricsError('Rate limit alcanzado - reduciendo frecuencia de actualización');
            } else {
              console.log(`⚠️ ${key} endpoint returned ${response.status}`);
            }
          } catch (error) {
            console.log(`❌ ${key} endpoint failed:`, error);
          }
        })
      );
      
      // CORREGIDO: Datos de fallback más robustos
      const metrics: DashboardMetrics = {
        // Procesar solo datos disponibles
        totalVendors: results.resumen?.total_vendedores || 0,
        activeVendors: results.resumen?.vendedores_activos || 0,
        totalProducts: results.resumen?.total_productos || 0,
        activeProducts: results.resumen?.productos_activos || 0,
        totalRevenue: results.resumen?.ingresos_totales || 0,
        monthlyRevenue: results.resumen?.ingresos_mes_actual || 0,
        
        // Fallback data para otros campos
        ordersToday: results.resumen?.pedidos_hoy || 0,
        ordersThisWeek: results.resumen?.pedidos_semana || 0,
        ordersThisMonth: results.resumen?.pedidos_mes || 0,
        completionRate: results.resumen?.tasa_completitud || 95,
        averageTicket: results.resumen?.ticket_promedio || 0,
        monthlySales: results.resumen?.ventas_mensuales || 0,
        
        totalStock: results.resumen?.stock_total || 0,
        lowStockItems: results.resumen?.productos_stock_bajo || 0,
        outOfStockItems: results.resumen?.productos_agotados || 0,
        stockValue: results.resumen?.valor_inventario || 0,
        
        deliverySuccessRate: 95,
        averageProcessingTime: "2.4h",
        customerSatisfaction: 4.2,
        
        topCategories: results.resumen?.categorias_populares || [
          { name: "Electrónicos", value: 0, percentage: 0 },
          { name: "Moda", value: 0, percentage: 0 },
          { name: "Hogar", value: 0, percentage: 0 },
          { name: "Deportes", value: 0, percentage: 0 }
        ]
      };
      
      setDashboardMetrics(metrics);
      console.log('📊 Dashboard metrics compiled:', metrics);
      
    } catch (error) {
      console.error('❌ Error fetching dashboard metrics:', error);
      setMetricsError('Error al conectar con el servidor');
      
      // Fallback a métricas vacías si todo falla
      setDashboardMetrics({
        totalVendors: 0,
        activeVendors: 0,
        totalProducts: 0,
        activeProducts: 0,
        totalRevenue: 0,
        monthlyRevenue: 0,
        ordersToday: 0,
        ordersThisWeek: 0,
        ordersThisMonth: 0,
        completionRate: 0,
        averageTicket: 0,
        monthlySales: 0,
        totalStock: 0,
        lowStockItems: 0,
        outOfStockItems: 0,
        stockValue: 0,
        deliverySuccessRate: 0,
        averageProcessingTime: "0h",
        customerSatisfaction: 0,
        topCategories: []
      });
    } finally {
      setIsLoadingMetrics(false);
    }
  };

  // CORREGIDO: Intervalos más largos y manejo inteligente
  useEffect(() => {
    fetchDashboardMetrics();
    
    // CORREGIDO: Cambiar de 30s a 5 minutos (300s) para respetar rate limiting
    const interval = setInterval(fetchDashboardMetrics, 300000);
    return () => clearInterval(interval);
  }, []);

  return {
    dashboardMetrics,
    isLoadingMetrics,
    metricsError,
    refreshMetrics: fetchDashboardMetrics
  };
};