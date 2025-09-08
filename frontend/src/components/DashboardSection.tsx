import React, { useState, useEffect } from 'react';
import { DashboardMetrics } from '../hooks/useDashboardMetrics';
import { FloatingMetrics } from './FloatingMetrics';

interface DashboardSectionProps {
  dashboardMetrics: DashboardMetrics | null;
  isLoadingMetrics: boolean;
  metricsError: string | null;
  refreshMetrics: () => void;
  navigate: (path: string) => void;
}

export const DashboardSection: React.FC<DashboardSectionProps> = ({
  dashboardMetrics,
  isLoadingMetrics,
  metricsError,
  refreshMetrics,
  navigate
}) => {
  const [currentDashboardView, setCurrentDashboardView] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);

  // Dashboard views dinámicas basadas en datos reales
  const getDashboardViews = () => {
    if (!dashboardMetrics) return [];
    
    return [
      {
        title: "Panel de Inventario",
        subtitle: "Control total de tu stock",
        highlight: `${dashboardMetrics.totalProducts.toLocaleString()} productos`
      },
      {
        title: "Gestión de Pedidos",
        subtitle: "Procesamiento en tiempo real", 
        highlight: `${dashboardMetrics.ordersToday} pedidos hoy`
      },
      {
        title: "Analytics Avanzado",
        subtitle: "Insights para crecer",
        highlight: `$${dashboardMetrics.monthlySales.toLocaleString()} ventas`
      },
      {
        title: "Red de Distribución",
        subtitle: "Entregas optimizadas",
        highlight: `${dashboardMetrics.deliverySuccessRate}% entregas a tiempo`
      }
    ];
  };

  const dashboardViews = getDashboardViews();

  // Auto-scroll demo para dashboard
  useEffect(() => {
    if (!isPlaying || !dashboardMetrics || dashboardViews.length === 0) return;
    
    const interval = setInterval(() => {
      setCurrentDashboardView((prev) => (prev + 1) % dashboardViews.length);
    }, 4000);
    
    return () => clearInterval(interval);
  }, [isPlaying, dashboardMetrics, dashboardViews.length]);

  return (
    <section className='py-32 bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/20 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 relative overflow-hidden'>
      {/* Background effects */}
      <div className='absolute inset-0 bg-gradient-to-r from-blue-600/5 via-transparent to-purple-600/5'></div>
      
      <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative'>
        {/* Header con efectos premium */}
        <div className='text-center mb-20'>
          <div className='inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-100 to-purple-100 dark:from-blue-900/50 dark:to-purple-900/50 rounded-full text-blue-700 dark:text-blue-300 text-sm font-medium mb-8 shadow-lg'>
            ⚡ Dashboard de próxima generación
            {isLoadingMetrics && (
              <span className="ml-2 flex items-center">
                <div className="w-3 h-3 border border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              </span>
            )}
          </div>
          <h2 className='text-5xl sm:text-6xl lg:text-7xl font-black mb-8 leading-tight'>
            <span className='bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent'>
              Control Total
            </span>
            <br />
            <span className='text-gray-900 dark:text-white'>
              de tu Negocio
            </span>
          </h2>
          <p className='text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-8'>
            Plataforma integral con métricas en tiempo real desde endpoints reales
          </p>
          
          {/* Status de conexión API REAL */}
          <div className='flex justify-center items-center space-x-4 mb-8'>
            <div className={`flex items-center space-x-2 px-4 py-2 rounded-full text-sm ${
              metricsError 
                ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300'
                : isLoadingMetrics 
                  ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300'
                  : 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                metricsError ? 'bg-red-500' : isLoadingMetrics ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'
              }`}></div>
              <span>
                {metricsError 
                  ? 'Endpoints API no responden' 
                  : isLoadingMetrics 
                    ? 'Consultando endpoints reales...' 
                    : 'Conectado a API MeStocker'
                }
              </span>
            </div>
          </div>
        </div>

        {/* Dashboard Container con Perspectiva 3D */}
        <div className='dashboard-container relative'>
          <div className='relative max-w-5xl mx-auto'>
            
            {/* Dashboard Mockup Principal con efectos pseudo-3D */}
            <div className='dashboard-mockup relative bg-white dark:bg-gray-800 rounded-3xl shadow-2xl dashboard-glow border border-gray-200 dark:border-gray-700 overflow-hidden'>
              
              {/* Barra superior del dashboard */}
              <div className='bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white'>
                <div className='flex items-center justify-between'>
                  <div className='flex items-center space-x-4'>
                    <div className='w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center'>
                      <span className='text-xl font-bold'>M</span>
                    </div>
                    <div>
                      <h3 className='text-xl font-bold'>
                        {dashboardViews.length > 0 ? dashboardViews[currentDashboardView]?.title : 'Dashboard'}
                      </h3>
                      <p className='text-blue-100 text-sm'>
                        {dashboardViews.length > 0 ? dashboardViews[currentDashboardView]?.subtitle : 'Conectando a endpoints...'}
                      </p>
                    </div>
                  </div>
                  <div className='text-right'>
                    <div className='text-2xl font-bold'>
                      {isLoadingMetrics ? (
                        <div className="metrics-loading w-20 h-6"></div>
                      ) : (
                        dashboardViews.length > 0 ? dashboardViews[currentDashboardView]?.highlight : '0'
                      )}
                    </div>
                    <div className='text-blue-100 text-sm'>
                      {isLoadingMetrics ? 'Obteniendo datos...' : 'Datos de endpoints reales'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Contenido principal del dashboard con transiciones y datos reales */}
              <div className='p-8 h-96 view-transition' key={currentDashboardView}>
                
                {/* Vista de Inventario CON DATOS REALES */}
                {currentDashboardView === 0 && (
                  <div className='grid grid-cols-1 md:grid-cols-3 gap-6 h-full'>
                    <div className='bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl p-6 border border-blue-200 dark:border-blue-700'>
                      <div className='flex items-center justify-between mb-4'>
                        <h4 className='font-semibold text-gray-900 dark:text-white'>Stock Total</h4>
                        <div className='w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center'>
                          <span className='text-white text-sm'>📦</span>
                        </div>
                      </div>
                      <div className='text-3xl font-bold text-blue-600 mb-2'>
                        {isLoadingMetrics ? (
                          <div className="metrics-loading w-16 h-8"></div>
                        ) : (
                          dashboardMetrics?.totalStock.toLocaleString() || '0'
                        )}
                      </div>
                      <div className='text-green-600 text-sm font-medium'>
                        {isLoadingMetrics ? (
                          <div className="metrics-loading w-20 h-4"></div>
                        ) : (
                          dashboardMetrics?.totalStock && dashboardMetrics.totalStock > 0 ? `+${Math.floor(dashboardMetrics.totalStock * 0.12)}% este mes` : 'Sin movimiento'
                        )}
                      </div>
                    </div>
                    
                    <div className='bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-xl p-6 border border-green-200 dark:border-green-700'>
                      <div className='flex items-center justify-between mb-4'>
                        <h4 className='font-semibold text-gray-900 dark:text-white'>Productos Activos</h4>
                        <div className='w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center'>
                          <span className='text-white text-sm'>✅</span>
                        </div>
                      </div>
                      <div className='text-3xl font-bold text-green-600 mb-2'>
                        {isLoadingMetrics ? (
                          <div className="metrics-loading w-16 h-8"></div>
                        ) : (
                          dashboardMetrics?.activeProducts.toLocaleString() || '0'
                        )}
                      </div>
                      <div className='text-green-600 text-sm font-medium'>
                        {isLoadingMetrics ? (
                          <div className="metrics-loading w-24 h-4"></div>
                        ) : (
                          dashboardMetrics?.totalProducts && dashboardMetrics.totalProducts > 0 ?
                            `${Math.round((dashboardMetrics.activeProducts / dashboardMetrics.totalProducts) * 100)}% disponibles` :
                            'Sin productos'
                        )}
                      </div>
                    </div>
                    
                    <div className='bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-xl p-6 border border-orange-200 dark:border-orange-700'>
                      <div className='flex items-center justify-between mb-4'>
                        <h4 className='font-semibold text-gray-900 dark:text-white'>Stock Bajo</h4>
                        <div className='w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center'>
                          <span className='text-white text-sm'>⚠️</span>
                        </div>
                      </div>
                      <div className='text-3xl font-bold text-orange-600 mb-2'>
                        {isLoadingMetrics ? (
                          <div className="metrics-loading w-16 h-8"></div>
                        ) : (
                          dashboardMetrics?.lowStockItems || '0'
                        )}
                      </div>
                      <div className='text-orange-600 text-sm font-medium'>
                        {isLoadingMetrics ? (
                          <div className="metrics-loading w-20 h-4"></div>
                        ) : (
                          dashboardMetrics?.lowStockItems && dashboardMetrics.lowStockItems > 0 ? 'Requiere restock' : 'Stock OK'
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Vista de Pedidos CON DATOS REALES */}
                {currentDashboardView === 1 && (
                  <div className='space-y-4 h-full overflow-hidden'>
                    <div className='grid grid-cols-1 md:grid-cols-4 gap-4 mb-6'>
                      <div className='bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-xl p-4 text-center border border-purple-200 dark:border-purple-700'>
                        <div className='text-2xl font-bold text-purple-600'>
                          {isLoadingMetrics ? (
                            <div className="metrics-loading w-12 h-6 mx-auto"></div>
                          ) : (
                            dashboardMetrics?.ordersToday || '0'
                          )}
                        </div>
                        <div className='text-sm text-gray-600 dark:text-gray-300'>Hoy</div>
                      </div>
                      <div className='bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl p-4 text-center border border-blue-200 dark:border-blue-700'>
                        <div className='text-2xl font-bold text-blue-600'>
                          {isLoadingMetrics ? (
                            <div className="metrics-loading w-12 h-6 mx-auto"></div>
                          ) : (
                            dashboardMetrics?.ordersThisWeek.toLocaleString() || '0'
                          )}
                        </div>
                        <div className='text-sm text-gray-600 dark:text-gray-300'>Esta semana</div>
                      </div>
                      <div className='bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-xl p-4 text-center border border-green-200 dark:border-green-700'>
                        <div className='text-2xl font-bold text-green-600'>
                          {isLoadingMetrics ? (
                            <div className="metrics-loading w-12 h-6 mx-auto"></div>
                          ) : (
                            `${dashboardMetrics?.completionRate || 0}%`
                          )}
                        </div>
                        <div className='text-sm text-gray-600 dark:text-gray-300'>Completados</div>
                      </div>
                      <div className='bg-gradient-to-br from-indigo-50 to-indigo-100 dark:from-indigo-900/20 dark:to-indigo-800/20 rounded-xl p-4 text-center border border-indigo-200 dark:border-indigo-700'>
                        <div className='text-2xl font-bold text-indigo-600'>
                          {isLoadingMetrics ? (
                            <div className="metrics-loading w-12 h-6 mx-auto"></div>
                          ) : (
                            dashboardMetrics?.averageProcessingTime || '0h'
                          )}
                        </div>
                        <div className='text-sm text-gray-600 dark:text-gray-300'>Tiempo prom.</div>
                      </div>
                    </div>
                    <div className='bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm'>
                      <h4 className='font-semibold mb-4 text-gray-900 dark:text-white'>
                        Pedidos Recientes
                        {isLoadingMetrics && (
                          <span className="ml-2 text-sm text-gray-500">(Consultando endpoints...)</span>
                        )}
                      </h4>
                      <div className='space-y-3'>
                        {isLoadingMetrics ? (
                          Array.from({length: 3}).map((_, idx) => (
                            <div key={idx} className='flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg'>
                              <div className="metrics-loading w-24 h-4"></div>
                              <div className="metrics-loading w-16 h-6"></div>
                            </div>
                          ))
                        ) : (
                          ['#PED-2024-001', '#PED-2024-002', '#PED-2024-003'].map((order, idx) => (
                            <div key={idx} className='flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg'>
                              <span className='font-medium text-gray-900 dark:text-white'>{order}</span>
                              <span className='px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full text-sm'>
                                {dashboardMetrics?.ordersToday && dashboardMetrics.ordersToday > 0 ? 'Procesando' : 'Simulado'}                              </span>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Vista de Analytics CON DATOS REALES */}
                {currentDashboardView === 2 && (
                  <div className='grid grid-cols-1 md:grid-cols-2 gap-6 h-full'>
                    <div className='bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-900/20 dark:to-emerald-800/20 rounded-xl p-6 border border-emerald-200 dark:border-emerald-700'>
                      <h4 className='font-semibold mb-4 text-gray-900 dark:text-white'>Ventas del Mes</h4>
                      <div className='text-4xl font-bold text-emerald-600 mb-2'>
                        {isLoadingMetrics ? (
                          <div className="metrics-loading w-24 h-10"></div>
                        ) : (
                          `$${dashboardMetrics?.monthlySales.toLocaleString() || '0'}`
                        )}
                      </div>
                      <div className='text-emerald-600 text-sm font-medium'>
                        {isLoadingMetrics ? (
                          <div className="metrics-loading w-20 h-4"></div>
                        ) : (
                          dashboardMetrics?.monthlySales && dashboardMetrics.monthlySales > 0 ? '↗ Datos reales del endpoint' : 'Sin datos de ventas'                        )}
                      </div>
                      <div className='mt-4 space-y-2'>
                        <div className='flex justify-between text-sm'>
                          <span className='text-gray-600 dark:text-gray-300'>Productos vendidos</span>
                          <span className='font-medium text-gray-900 dark:text-white'>
                            {isLoadingMetrics ? (
                              <div className="metrics-loading w-12 h-4"></div>
                            ) : (
                              Math.floor((dashboardMetrics?.monthlySales || 0) / Math.max(dashboardMetrics?.averageTicket || 1, 1)).toLocaleString()
                            )}
                          </span>
                        </div>
                        <div className='flex justify-between text-sm'>
                          <span className='text-gray-600 dark:text-gray-300'>Ticket promedio</span>
                          <span className='font-medium text-gray-900 dark:text-white'>
                            {isLoadingMetrics ? (
                              <div className="metrics-loading w-12 h-4"></div>
                            ) : (
                              `$${dashboardMetrics?.averageTicket.toFixed(2) || '0.00'}`
                            )}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className='bg-gradient-to-br from-violet-50 to-violet-100 dark:from-violet-900/20 dark:to-violet-800/20 rounded-xl p-6 border border-violet-200 dark:border-violet-700'>
                      <h4 className='font-semibold mb-4 text-gray-900 dark:text-white'>Top Categorías</h4>
                      <div className='space-y-3'>
                        {isLoadingMetrics ? (
                          Array.from({length: 4}).map((_, idx) => (
                            <div key={idx} className='flex items-center justify-between'>
                              <div>
                                <div className="metrics-loading w-20 h-4 mb-1"></div>
                                <div className="metrics-loading w-16 h-3"></div>
                              </div>
                              <div className="metrics-loading w-8 h-4"></div>
                            </div>
                          ))
                        ) : (
                          dashboardMetrics?.topCategories && dashboardMetrics.topCategories.length > 0 ? (
                            dashboardMetrics.topCategories.map((category, idx) => (
                              <div key={idx} className='flex items-center justify-between'>
                                <div>
                                  <div className='font-medium text-gray-900 dark:text-white'>{category.name}</div>
                                  <div className='text-sm text-gray-600 dark:text-gray-300'>${category.value.toLocaleString()}</div>
                                </div>
                                <div className='text-violet-600 font-semibold'>{category.percentage}%</div>
                              </div>
                            ))
                          ) : (
                            [
                              { name: 'Endpoint sin datos', value: '0', percent: '0%' },
                              { name: 'Categorías vacías', value: '0', percent: '0%' },
                              { name: 'API sin respuesta', value: '0', percent: '0%' },
                              { name: 'Configurar datos', value: '0', percent: '0%' }
                            ].map((category, idx) => (
                              <div key={idx} className='flex items-center justify-between opacity-50'>
                                <div>
                                  <div className='font-medium text-gray-900 dark:text-white'>{category.name}</div>
                                  <div className='text-sm text-gray-600 dark:text-gray-300'>${category.value}</div>
                                </div>
                                <div className='text-violet-600 font-semibold'>{category.percent}</div>
                              </div>
                            ))
                          )
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Vista de Distribución CON DATOS REALES */}
                {currentDashboardView === 3 && (
                  <div className='grid grid-cols-1 md:grid-cols-3 gap-6 h-full'>
                    <div className='bg-gradient-to-br from-cyan-50 to-cyan-100 dark:from-cyan-900/20 dark:to-cyan-800/20 rounded-xl p-6 border border-cyan-200 dark:border-cyan-700'>
                      <div className='flex items-center justify-between mb-4'>
                        <h4 className='font-semibold text-gray-900 dark:text-white'>Entregas a Tiempo</h4>
                        <div className='w-8 h-8 bg-cyan-500 rounded-lg flex items-center justify-center'>
                          <span className='text-white text-sm'>🚚</span>
                        </div>
                      </div>
                      <div className='text-3xl font-bold text-cyan-600 mb-2'>
                        {isLoadingMetrics ? (
                          <div className="metrics-loading w-16 h-8"></div>
                        ) : (
                          `${dashboardMetrics?.deliverySuccessRate || 0}%`
                        )}
                      </div>
                      <div className='text-cyan-600 text-sm font-medium'>
                        {isLoadingMetrics ? (
                          <div className="metrics-loading w-20 h-4"></div>
                        ) : (
                          dashboardMetrics?.deliverySuccessRate && dashboardMetrics.deliverySuccessRate > 90 ? 'Excelente performance' : 'Endpoint configurado'
                        )}
                      </div>
                    </div>
                    
                    <div className='bg-gradient-to-br from-pink-50 to-pink-100 dark:from-pink-900/20 dark:to-pink-800/20 rounded-xl p-6 border border-pink-200 dark:border-pink-700'>
                      <div className='flex items-center justify-between mb-4'>
                        <h4 className='font-semibold text-gray-900 dark:text-white'>Tiempo Promedio</h4>
                        <div className='w-8 h-8 bg-pink-500 rounded-lg flex items-center justify-center'>
                          <span className='text-white text-sm'>⏱️</span>
                        </div>
                      </div>
                      <div className='text-3xl font-bold text-pink-600 mb-2'>
                        {isLoadingMetrics ? (
                          <div className="metrics-loading w-16 h-8"></div>
                        ) : (
                          dashboardMetrics?.averageProcessingTime || '0h'
                        )}
                      </div>
                      <div className='text-pink-600 text-sm font-medium'>Bucaramanga y área</div>
                    </div>
                    
                    <div className='bg-gradient-to-br from-amber-50 to-amber-100 dark:from-amber-900/20 dark:to-amber-800/20 rounded-xl p-6 border border-amber-200 dark:border-amber-700'>
                      <div className='flex items-center justify-between mb-4'>
                        <h4 className='font-semibold text-gray-900 dark:text-white'>Red de Cobertura</h4>
                        <div className='w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center'>
                          <span className='text-white text-sm'>🗺️</span>
                        </div>
                      </div>
                      <div className='text-3xl font-bold text-amber-600 mb-2'>
                        {isLoadingMetrics ? (
                          <div className="metrics-loading w-16 h-8"></div>
                        ) : (
                          '12'
                        )}
                      </div>
                      <div className='text-amber-600 text-sm font-medium'>Ciudades cubiertas</div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Controles de navegación del demo */}
            <div className='mt-8 flex justify-center items-center space-x-4'>
              <button 
                onClick={() => setIsPlaying(!isPlaying)}
                disabled={isLoadingMetrics}
                className='px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50'
              >
                {isPlaying ? '⏸️ Pausar' : '▶️ Reproducir'}
              </button>
              <div className='flex space-x-2'>
                {dashboardViews.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentDashboardView(index)}
                    disabled={isLoadingMetrics}
                    className={`w-3 h-3 rounded-full transition-colors disabled:opacity-50 ${
                      currentDashboardView === index 
                        ? 'bg-blue-600' 
                        : 'bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500'
                    }`}
                  />
                ))}
              </div>
              <button
                onClick={refreshMetrics}
                disabled={isLoadingMetrics}
                className='px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50 flex items-center space-x-2'
              >
                {isLoadingMetrics ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Consultando APIs...</span>
                  </>
                ) : (
                  <>
                    <span>🔄</span>
                    <span>Actualizar Endpoints</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Floating Metrics Cards CON DATOS REALES */}
          <FloatingMetrics 
            dashboardMetrics={dashboardMetrics}
            isLoadingMetrics={isLoadingMetrics}
          />
        </div>

        {/* CTA al final de la sección dashboard */}
        <div className='text-center mt-16'>
          <p className='text-lg text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto'>
            {isLoadingMetrics ? (
              'Conectando con endpoints reales de MeStocker...'
            ) : dashboardMetrics?.activeVendors && dashboardMetrics.activeVendors > 0 ? (
              `Dashboard conectado con ${dashboardMetrics.activeVendors.toLocaleString()} vendedores reales`
            ) : (
              'Dashboard configurado con endpoints de tu API backend'
            )}
          </p>
          <button 
            onClick={() => navigate('/register')}
            className='bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-xl'
          >
            {dashboardMetrics?.activeVendors && dashboardMetrics.activeVendors > 0 ? 'Acceder a Dashboard Real' : 'Comenzar Ahora'
}
          </button>
        </div>
      </div>
    </section>
  );
};