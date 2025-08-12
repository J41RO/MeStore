import React, { useEffect } from 'react';
import { useVendor } from '../hooks/useVendor';

const Dashboard: React.FC = () => {
  const { 
    storeName, 
    metrics, 
    isLoading, 
    getBusinessSummary, 
    getCompletionStatus,
    refreshMetrics 
  } = useVendor();

  const businessSummary = getBusinessSummary();
  const completionStatus = getCompletionStatus();

      {/* MICRO-FASE 5: Alerta responsive con icono oculto en pantallas pequeñas */}

  useEffect(() => {
    refreshMetrics();
  }, []);

  if (isLoading) {
    return (
      <div className="p-4 md:p-6 lg:p-8 max-w-7xl mx-auto">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="bg-white p-3 md:p-4 lg:p-6 rounded-lg shadow">
                <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/3"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 md:p-6 lg:p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-4 md:mb-6">
        <h1 className="text-2xl font-bold">Dashboard - {storeName}</h1>
        <button
          onClick={refreshMetrics}
          className="px-3 py-2 md:px-4 md:py-2 text-sm md:text-base bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Actualizar
        </button>
      </div>

      {!completionStatus.isComplete && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 md:p-4 mb-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 hidden sm:block">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">
                Completa tu perfil ({completionStatus.percentage}%)
              </h3>
              <p className="text-sm text-yellow-700 mt-1">
                Faltan: {completionStatus.missingFields.join(', ')}
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4 gap-3 md:gap-4 lg:gap-6 mb-6">
        <div className="bg-white p-3 md:p-4 rounded-lg shadow">
          <h3 className="font-semibold text-gray-600">Ventas Totales</h3>
          <p className="text-xl md:text-2xl font-bold text-green-600">{metrics.totalSales}</p>
          <p className="text-sm text-gray-500">+5% vs mes anterior</p>
        </div>
        
        <div className="bg-white p-3 md:p-4 rounded-lg shadow">
          <h3 className="font-semibold text-gray-600">Ingresos</h3>
          <p className="text-xl md:text-2xl font-bold text-blue-600">{businessSummary.revenue}</p>
          <p className="text-sm text-gray-500">Total acumulado</p>
        </div>
        
        <div className="bg-white p-3 md:p-4 rounded-lg shadow">
          <h3 className="font-semibold text-gray-600">Productos Activos</h3>
          <p className="text-2xl font-bold text-purple-600">{metrics.activeProducts}</p>
          <p className="text-sm text-gray-500">En catálogo</p>
        </div>
        
        <div className="bg-white p-3 md:p-4 rounded-lg shadow">
          <h3 className="font-semibold text-gray-600">Calificación</h3>
          <p className="text-2xl font-bold text-yellow-600">{businessSummary.rating} ⭐</p>
          <p className="text-sm text-gray-500">{metrics.totalOrders} reseñas</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-4 md:p-6">
        <h2 className="text-lg font-semibold mb-4">Acciones Rápidas</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-4">
          <button className="p-3 md:p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors text-left">
            <h3 className="font-medium text-sm md:text-base">Agregar Producto</h3>
            <p className="text-xs sm:text-sm text-gray-600">Crear nuevo producto en tu catálogo</p>
          </button>
          
          <button className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors text-left">
            <h3 className="font-medium">Ver Órdenes</h3>
            <p className="text-sm text-gray-600">Gestionar pedidos pendientes</p>
          </button>
          
          <button className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors text-left">
            <h3 className="font-medium">Configurar Tienda</h3>
            <p className="text-sm text-gray-600">Personalizar tu perfil de vendedor</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;