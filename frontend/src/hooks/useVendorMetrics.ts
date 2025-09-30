import { useState, useEffect, useCallback } from 'react';
import { vendorApi } from '../services/api_vendor';

export interface VendorMetrics {
  // Productos - con estados de aprobación
  totalProductos?: number;
  productosAprobados?: number;      // Productos aprobados por admin
  productosPendientes?: number;      // Productos esperando aprobación
  productosRechazados?: number;      // Productos rechazados por admin
  productosActivos?: number;         // Legacy - mantener compatibilidad
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

      // Llamada real a la API del backend
      const response = await vendorApi.auth.dashboard.resumen();
      const apiData = response.data;

      // Mapear la respuesta de la API a la interfaz VendorMetrics
      const mappedMetrics: VendorMetrics = {
        // Productos - desde API con estados de aprobación
        totalProductos: apiData.total_productos || 0,
        productosAprobados: apiData.productos_aprobados || 0,
        productosPendientes: apiData.productos_pendientes || 0,
        productosRechazados: apiData.productos_rechazados || 0,
        productosActivos: apiData.productos_activos || 0,  // Legacy
        productosInactivos: (apiData.total_productos || 0) - (apiData.productos_aprobados || 0),
        productosChange: 0, // TODO: Calcular cambio vs período anterior cuando esté disponible

        // Ventas - desde API
        totalVentas: parseFloat(apiData.ingresos_mes || '0'),
        ventasDelMes: apiData.ventas_mes || 0,
        ventasDiarias: 0, // TODO: Agregar este campo al backend cuando esté disponible
        ventasChange: 0, // TODO: Calcular cambio vs período anterior

        // Ingresos - desde API
        ingresosTotales: parseFloat(apiData.ingresos_mes || '0'),
        ingresosMes: parseFloat(apiData.ingresos_mes || '0'),
        ingresosPromedioDiario: 0, // TODO: Calcular cuando esté disponible
        ingresosChange: 0, // TODO: Calcular cambio vs período anterior
        comisionesTotales: parseFloat(apiData.comision_total || '0'),

        // Órdenes - valores por defecto (TODO: agregar al backend)
        ordenesPendientes: 0,
        ordenesCompletadas: 0,
        ordenesTotales: 0,
        ordenesChange: 0,

        // Performance - valores por defecto (TODO: agregar al backend)
        puntuacionVendedor: 0,
        satisfaccionCliente: 0,
        tiempoPromedioEntrega: 0,

        // Estadísticas adicionales - valores por defecto (TODO: agregar al backend)
        clientesUnicos: 0,
        productoMasVendido: 'N/A',
        categoriaTopVentas: 'N/A',

        // Fechas
        ultimaVenta: undefined,
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