// ~/MeStore/frontend/src/pages/Dashboard.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Dashboard Page
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: Dashboard.tsx
// Ruta: ~/MeStore/frontend/src/pages/Dashboard.tsx
// Autor: Jairo
// Fecha de Creación: 2025-08-14
// Última Actualización: 2025-08-14
// Versión: 1.1.1
// Propósito: Página principal del dashboard del vendedor con QuickActions integrado
//
// Modificaciones:
// 2025-08-14 - Integración de QuickActions en ubicación estratégica
// 2025-08-14 - Corrección de propiedades TypeScript (missingFields, activeProducts)
//
// ---------------------------------------------------------------------------------------------

import React, { useEffect } from 'react';
import { useVendor } from '../hooks/useVendor';
import SalesChart from '../components/charts/SalesChart';
import MonthlySalesChart from '../components/charts/MonthlySalesChart';
import TopProductsWidget from '../components/widgets/TopProductsWidget';
import QuickActions from '../components/QuickActions';

const Dashboard: React.FC = () => {
  const {
    storeName,
    metrics,
    isLoading,
    getCompletionStatus,
    refreshMetrics,
    salesHistory,
    monthlySales,
  } = useVendor();

  const completionStatus = getCompletionStatus();

  useEffect(() => {
    refreshMetrics();
  }, [refreshMetrics]);

  if (isLoading) {
    return (
      <div className="p-4 md:p-6 lg:p-8 max-w-7xl mx-auto">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 md:p-6 lg:p-8 max-w-7xl mx-auto">
      {/* Header con bienvenida */}
      <div className="mb-6">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">
          Bienvenido, {storeName || 'Vendedor'}
        </h1>
        <p className="text-gray-600">
          Gestiona tu tienda y monitorea tu rendimiento desde aquí
        </p>
      </div>

      {/* MICRO-FASE 3: QuickActions prominente al inicio */}
      <QuickActions className="mb-6" />

      {/* MICRO-FASE 5: Alerta responsive con icono oculto en pantallas pequeñas */}
      {completionStatus.missingFields.length > 0 && (
        <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
          <div className="flex items-start">
            <div className="flex-shrink-0 hidden sm:block">
              <svg className="h-5 w-5 text-amber-400 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-0 sm:ml-3">
              <h3 className="text-sm font-medium text-amber-800">
                Completa tu perfil para mejor rendimiento
              </h3>
              <div className="mt-2 text-sm text-amber-700">
                <p>Elementos pendientes: {completionStatus.missingFields.join(', ')}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Métricas principales */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4 gap-3 md:gap-4 lg:gap-6 mb-6">
        <div className="bg-white p-4 md:p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Ventas Totales</p>
              <p className="text-xl md:text-2xl font-semibold text-gray-900">
                ${metrics?.totalSales?.toLocaleString() || '0'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-4 md:p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Comisiones</p>
              <p className="text-xl md:text-2xl font-semibold text-gray-900">
                ${metrics?.totalCommissions?.toLocaleString() || '0'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-4 md:p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Productos</p>
              <p className="text-xl md:text-2xl font-semibold text-gray-900">
                {metrics?.activeProducts || '0'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-4 md:p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Órdenes</p>
              <p className="text-xl md:text-2xl font-semibold text-gray-900">
                {metrics?.totalOrders || '0'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Widgets y componentes */}
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-4">
          <div className="lg:col-span-2">
            <div className="bg-white p-4 md:p-6 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Ventas Mensuales</h2>
              <MonthlySalesChart data={monthlySales} />
            </div>
          </div>
          
          <div>
            <TopProductsWidget />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-4 md:p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Historial de Ventas</h2>
            <SalesChart data={salesHistory} />
          </div>
          
          <div className="bg-white p-4 md:p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Actividad Reciente</h2>
            <div className="space-y-3">
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-md">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-sm text-gray-600">Nueva venta registrada</span>
                <span className="text-xs text-gray-400 ml-auto">Hace 2 horas</span>
              </div>
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-md">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <span className="text-sm text-gray-600">Producto actualizado</span>
                <span className="text-xs text-gray-400 ml-auto">Hace 4 horas</span>
              </div>
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-md">
                <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                <span className="text-sm text-gray-600">Comisión procesada</span>
                <span className="text-xs text-gray-400 ml-auto">Hace 1 día</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
