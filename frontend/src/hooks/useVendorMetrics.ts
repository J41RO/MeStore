import { useState, useEffect, useCallback } from 'react';
// import { vendorApi } from '../services/api_vendor';

export interface VendorMetrics {
  // Productos
  totalProductos?: number;
  productosActivos?: number;
  productosInactivos?: number;
  productosChange?: number;
  
  // Ventas
  totalVentas?: number;
  ventasDelMes?: number;
  ventasDiarias?: number;
  ventasChange?: number;
  
  // Ingresos
  ingresosTotales?: number;
  ingresosMes?: number;
  ingresosPromedioDiario?: number;
  ingresosChange?: number;
  comisionesTotales?: number;
  
  // Órdenes
  ordenesPendientes?: number;
  ordenesCompletadas?: number;
  ordenesTotales?: number;
  ordenesChange?: number;
  
  // Performance
  puntuacionVendedor?: number;
  satisfaccionCliente?: number;
  tiempoPromedioEntrega?: number;
  
  // Estadísticas adicionales
  clientesUnicos?: number;
  productoMasVendido?: string;
  categoriaTopVentas?: string;
  
  // Fechas
  ultimaVenta?: string;
  ultimaActualizacion?: string;
}

interface UseVendorMetricsResult {
  metrics: VendorMetrics | null;
  loading: boolean;
  error: string | null;
  refreshMetrics: () => Promise<void>;
  isRefreshing: boolean;
}

export const useVendorMetrics = (vendorId?: string): UseVendorMetricsResult => {
  const [metrics, setMetrics] = useState<VendorMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const fetchMetrics = useCallback(async (showRefreshing = false) => {
    try {
      if (showRefreshing) {
        setIsRefreshing(true);
      } else {
        setLoading(true);
      }
      
      setError(null);
      
      // Datos simulados temporalmente hasta que la API esté funcionando
      // TODO: Reemplazar con llamada real a vendorApi.auth.dashboard.resumen()
      const mappedMetrics: VendorMetrics = {
        // Productos
        totalProductos: 24,
        productosActivos: 18,
        productosInactivos: 6,
        productosChange: 15.2,
        
        // Ventas 
        totalVentas: 1250000,
        ventasDelMes: 320000,
        ventasDiarias: 12500,
        ventasChange: 8.7,
        
        // Ingresos
        ingresosTotales: 1250000,
        ingresosMes: 320000,
        ingresosPromedioDiario: 12500,
        ingresosChange: 8.7,
        comisionesTotales: 125000,
        
        // Órdenes
        ordenesPendientes: 5,
        ordenesCompletadas: 47,
        ordenesTotales: 52,
        ordenesChange: 12.5,
        
        // Performance
        puntuacionVendedor: 4.3,
        satisfaccionCliente: 4.5,
        tiempoPromedioEntrega: 3,
        
        // Estadísticas adicionales
        clientesUnicos: 18,
        productoMasVendido: 'Smartphone Galaxy A54',
        categoriaTopVentas: 'Electrónicos',
        
        // Fechas
        ultimaVenta: new Date(Date.now() - 2 * 3600000).toISOString(),
        ultimaActualizacion: new Date().toISOString()
      };
      
      setMetrics(mappedMetrics);
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 
                          err.message || 
                          'Error al cargar métricas del vendedor';
      setError(errorMessage);
      console.error('Error fetching vendor metrics:', err);
      
      // En caso de error, establecer métricas por defecto
      setMetrics({
        totalProductos: 0,
        productosActivos: 0,
        productosInactivos: 0,
        totalVentas: 0,
        ventasDelMes: 0,
        ingresosTotales: 0,
        ingresosMes: 0,
        ordenesPendientes: 0,
        ordenesCompletadas: 0,
        puntuacionVendedor: 0,
        satisfaccionCliente: 0,
        clientesUnicos: 0,
        productoMasVendido: 'N/A',
        categoriaTopVentas: 'N/A',
        ultimaActualizacion: new Date().toISOString()
      });
    } finally {
      setLoading(false);
      if (showRefreshing) {
        setIsRefreshing(false);
      }
    }
  }, [vendorId]);

  const refreshMetrics = useCallback(async () => {
    await fetchMetrics(true);
  }, [fetchMetrics]);

  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  // Auto-refresh deshabilitado temporalmente para evitar rate limiting
  // TODO: Rehabilitar cuando la API esté estable
  // useEffect(() => {
  //   const interval = setInterval(() => {
  //     refreshMetrics();
  //   }, 5 * 60 * 1000); // 5 minutos

  //   return () => clearInterval(interval);
  // }, [refreshMetrics]);

  return {
    metrics,
    loading,
    error,
    refreshMetrics,
    isRefreshing
  };
};

// Hook adicional para métricas en tiempo real
export const useVendorMetricsRealtime = (vendorId?: string) => {
  const baseMetrics = useVendorMetrics(vendorId);
  const [realtimeData, _setRealtimeData] = useState<Partial<VendorMetrics>>({});

  // Aquí se podría implementar WebSocket para datos en tiempo real
  useEffect(() => {
    // Placeholder para conexión WebSocket
    // const ws = new WebSocket(`ws://localhost:8000/ws/vendor/${vendorId}/metrics`);
    // ws.onmessage = (event) => {
    //   const data = JSON.parse(event.data);
    //   setRealtimeData(data);
    // };
    // return () => ws.close();
  }, [vendorId]);

  return {
    ...baseMetrics,
    metrics: baseMetrics.metrics ? {
      ...baseMetrics.metrics,
      ...realtimeData
    } : null
  };
};