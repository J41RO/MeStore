// ~/frontend/src/components/admin/IncomingProductsQueue.tsx
// Componente simplificado para evitar conflictos de imports
import React, { useState, useEffect, useCallback } from 'react';
import { 
  Clock, Package, AlertTriangle, CheckCircle, 
  User, TrendingUp, Filter, 
  RefreshCw, Plus, Edit, Eye, Truck,
  BarChart3, Activity, CheckSquare
} from 'lucide-react';
import { ProductVerificationWorkflow } from './ProductVerificationWorkflow';

// Tipos TypeScript para la cola de productos
interface QueueItem {
  id: string;
  product_id: string;
  vendor_id: string;
  expected_arrival?: string;
  actual_arrival?: string;
  verification_status: 'PENDING' | 'ASSIGNED' | 'IN_PROGRESS' | 'QUALITY_CHECK' | 'APPROVED' | 'REJECTED' | 'ON_HOLD' | 'COMPLETED';
  priority: 'LOW' | 'NORMAL' | 'HIGH' | 'CRITICAL' | 'EXPEDITED';
  assigned_to?: string;
  assigned_at?: string;
  deadline?: string;
  tracking_number?: string;
  carrier?: string;
  is_delayed: boolean;
  delay_reason?: 'TRANSPORT' | 'CUSTOMS' | 'DOCUMENTATION' | 'VENDOR_DELAY' | 'QUALITY_ISSUES' | 'CAPACITY' | 'OTHER';
  verification_notes?: string;
  quality_score?: number;
  quality_issues?: string;
  verification_attempts: number;
  created_at: string;
  updated_at: string;
  is_overdue: boolean;
  days_in_queue: number;
  processing_time_hours?: number;
  is_high_priority: boolean;
  status_display: string;
  priority_display: string;
}

interface QueueStats {
  total_items: number;
  pending: number;
  assigned: number;
  in_progress: number;
  completed: number;
  overdue: number;
  delayed: number;
  average_processing_time: number;
  queue_efficiency: number;
}

const IncomingProductsQueue: React.FC = () => {
  const [queueItems, setQueueItems] = useState<QueueItem[]>([]);
  const [stats, setStats] = useState<QueueStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<QueueItem | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [showVerificationWorkflow, setShowVerificationWorkflow] = useState(false);
  const [currentView, setCurrentView] = useState<'list' | 'analytics'>('list');
  const [refreshing, setRefreshing] = useState(false);

  const [filters, setFilters] = useState({
    verification_status: '',
    priority: '',
    assigned_to: '',
    vendor_id: '',
    overdue_only: false,
    delayed_only: false
  });

  const fetchQueueData = useCallback(async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true);
    
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value && value !== '') {
          params.append(key, value.toString());
        }
      });

      const response = await fetch(`/api/v1/inventory/queue/incoming-products?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Error fetching queue data');
      }

      const data = await response.json();
      setQueueItems(data);
    } catch (error) {
      console.error('Error fetching queue:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [filters]);

  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/inventory/queue/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  }, []);

  useEffect(() => {
    fetchQueueData();
    fetchStats();
  }, [fetchQueueData, fetchStats]);

  useEffect(() => {
    const interval = setInterval(() => {
      fetchQueueData();
      fetchStats();
    }, 30000);
    return () => clearInterval(interval);
  }, [fetchQueueData, fetchStats]);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'CRITICAL': return 'bg-red-500 text-white px-2 py-1 rounded text-xs';
      case 'EXPEDITED': return 'bg-purple-500 text-white px-2 py-1 rounded text-xs';
      case 'HIGH': return 'bg-orange-500 text-white px-2 py-1 rounded text-xs';
      case 'NORMAL': return 'bg-blue-500 text-white px-2 py-1 rounded text-xs';
      case 'LOW': return 'bg-gray-500 text-white px-2 py-1 rounded text-xs';
      default: return 'bg-gray-400 text-white px-2 py-1 rounded text-xs';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED': return 'bg-green-500 text-white px-2 py-1 rounded text-xs';
      case 'APPROVED': return 'bg-green-400 text-white px-2 py-1 rounded text-xs';
      case 'IN_PROGRESS': return 'bg-blue-500 text-white px-2 py-1 rounded text-xs';
      case 'ASSIGNED': return 'bg-indigo-500 text-white px-2 py-1 rounded text-xs';
      case 'QUALITY_CHECK': return 'bg-yellow-500 text-white px-2 py-1 rounded text-xs';
      case 'REJECTED': return 'bg-red-500 text-white px-2 py-1 rounded text-xs';
      case 'ON_HOLD': return 'bg-orange-500 text-white px-2 py-1 rounded text-xs';
      case 'PENDING': return 'bg-gray-500 text-white px-2 py-1 rounded text-xs';
      default: return 'bg-gray-400 text-white px-2 py-1 rounded text-xs';
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleRefresh = () => {
    fetchQueueData(true);
    fetchStats();
  };

  const handleWorkflowStepComplete = (step: string, result: any) => {
    console.log('Workflow step completed:', step, result);
    // Refresh data to show updated status
    fetchQueueData();
    fetchStats();
  };

  const handleOpenVerificationWorkflow = (item: QueueItem) => {
    setSelectedItem(item);
    setShowVerificationWorkflow(true);
  };

  return (
    <div className="space-y-6 p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="flex justify-between items-center bg-white p-6 rounded-lg shadow">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Cola de Productos Entrantes</h1>
          <p className="text-gray-600 mt-2">
            Gestión completa de productos en tránsito y verificación
          </p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Actualizar
          </button>
          <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700">
            <Plus className="w-4 h-4 mr-2" />
            Agregar Producto
          </button>
        </div>
      </div>

      {/* Estadísticas */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-8 gap-4">
          {[
            { label: 'Total', value: stats.total_items, icon: Package, color: 'text-blue-600' },
            { label: 'Pendientes', value: stats.pending, icon: Clock, color: 'text-gray-600' },
            { label: 'En Proceso', value: stats.in_progress, icon: Activity, color: 'text-blue-600' },
            { label: 'Completados', value: stats.completed, icon: CheckCircle, color: 'text-green-600' },
            { label: 'Vencidos', value: stats.overdue, icon: AlertTriangle, color: 'text-red-600' },
            { label: 'Retrasados', value: stats.delayed, icon: Truck, color: 'text-orange-600' },
            { label: 'Eficiencia', value: `${stats.queue_efficiency}%`, icon: TrendingUp, color: 'text-purple-600' },
            { label: 'Tiempo Avg', value: `${stats.average_processing_time}h`, icon: Clock, color: 'text-indigo-600' }
          ].map((stat, index) => (
            <div key={index} className="bg-white p-4 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{stat.label}</p>
                  <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
                </div>
                <stat.icon className={`w-8 h-8 ${stat.color.replace('text-', 'text-').replace('-600', '-500')}`} />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Navegación por pestañas */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setCurrentView('list')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                currentView === 'list'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Package className="w-4 h-4 mr-2 inline" />
              Lista de Cola
            </button>
            <button
              onClick={() => setCurrentView('analytics')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                currentView === 'analytics'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <BarChart3 className="w-4 h-4 mr-2 inline" />
              Analytics
            </button>
          </nav>
        </div>

        {/* Contenido */}
        <div className="p-6">
          {currentView === 'list' && (
            <div className="space-y-6">
              {/* Filtros */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center mb-4">
                  <Filter className="w-5 h-5 mr-2" />
                  <h3 className="text-lg font-semibold">Filtros</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
                  <select
                    value={filters.verification_status}
                    onChange={(e) => setFilters(prev => ({ ...prev, verification_status: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="">Todos los estados</option>
                    <option value="PENDING">Pendiente</option>
                    <option value="ASSIGNED">Asignado</option>
                    <option value="IN_PROGRESS">En Proceso</option>
                    <option value="QUALITY_CHECK">Control Calidad</option>
                    <option value="APPROVED">Aprobado</option>
                    <option value="REJECTED">Rechazado</option>
                    <option value="ON_HOLD">En Espera</option>
                    <option value="COMPLETED">Completado</option>
                  </select>

                  <select
                    value={filters.priority}
                    onChange={(e) => setFilters(prev => ({ ...prev, priority: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="">Todas las prioridades</option>
                    <option value="CRITICAL">Crítica</option>
                    <option value="EXPEDITED">Expedita</option>
                    <option value="HIGH">Alta</option>
                    <option value="NORMAL">Normal</option>
                    <option value="LOW">Baja</option>
                  </select>

                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="overdue_only"
                      checked={filters.overdue_only}
                      onChange={(e) => setFilters(prev => ({ ...prev, overdue_only: e.target.checked }))}
                      className="rounded"
                    />
                    <label htmlFor="overdue_only" className="text-sm">Solo vencidos</label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="delayed_only"
                      checked={filters.delayed_only}
                      onChange={(e) => setFilters(prev => ({ ...prev, delayed_only: e.target.checked }))}
                      className="rounded"
                    />
                    <label htmlFor="delayed_only" className="text-sm">Solo retrasados</label>
                  </div>

                  <button
                    onClick={() => setFilters({ verification_status: '', priority: '', assigned_to: '', vendor_id: '', overdue_only: false, delayed_only: false })}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Limpiar Filtros
                  </button>

                  <button
                    onClick={() => fetchQueueData()}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700"
                  >
                    Aplicar Filtros
                  </button>
                </div>
              </div>

              {/* Lista de productos */}
              <div>
                <h3 className="text-lg font-semibold mb-4">
                  Productos en Cola ({queueItems.length})
                </h3>
                {loading ? (
                  <div className="flex justify-center items-center py-8">
                    <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
                    <span className="ml-2">Cargando cola...</span>
                  </div>
                ) : queueItems.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Package className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                    <h3 className="text-lg font-semibold mb-2">Cola vacía</h3>
                    <p>No hay productos en cola que coincidan con los filtros seleccionados.</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full bg-white border border-gray-200 rounded-lg">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Producto</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Prioridad</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Llegada Esperada</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Días en Cola</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Asignado</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {queueItems.map((item) => (
                          <tr key={item.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center space-x-3">
                                <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                                <div>
                                  <p className="font-medium text-sm">{item.product_id}</p>
                                  {item.is_delayed && (
                                    <span className="inline-block bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded mt-1">
                                      Retrasado
                                    </span>
                                  )}
                                  {item.is_overdue && (
                                    <span className="inline-block bg-red-100 text-red-800 text-xs px-2 py-1 rounded mt-1 ml-1">
                                      Vencido
                                    </span>
                                  )}
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={getStatusColor(item.verification_status)}>
                                {item.status_display}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={getPriorityColor(item.priority)}>
                                {item.priority_display}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {formatDate(item.expected_arrival)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {item.days_in_queue} días
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {item.assigned_to ? (
                                <div className="flex items-center">
                                  <User className="w-4 h-4 mr-1" />
                                  Asignado
                                </div>
                              ) : (
                                <span className="text-gray-400">No asignado</span>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                              <div className="flex space-x-2">
                                <button
                                  onClick={() => {
                                    setSelectedItem(item);
                                    setShowDetails(true);
                                  }}
                                  className="text-blue-600 hover:text-blue-900"
                                  title="Ver detalles"
                                >
                                  <Eye className="w-4 h-4" />
                                </button>
                                <button 
                                  className="text-indigo-600 hover:text-indigo-900"
                                  title="Editar"
                                >
                                  <Edit className="w-4 h-4" />
                                </button>
                                {/* Botón de verificación solo para items que requieren verificación */}
                                {item.verification_status !== 'COMPLETED' && item.verification_status !== 'REJECTED' && (
                                  <button
                                    onClick={() => handleOpenVerificationWorkflow(item)}
                                    className="text-green-600 hover:text-green-900"
                                    title="Iniciar/Continuar verificación"
                                  >
                                    <CheckSquare className="w-4 h-4" />
                                  </button>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}

          {currentView === 'analytics' && (
            <div className="text-center py-8 text-gray-500">
              <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-semibold mb-2">Analytics</h3>
              <p>Los gráficos y análisis detallados estarán disponibles próximamente.</p>
            </div>
          )}
        </div>
      </div>

      {/* Modal de detalles */}
      {showDetails && selectedItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl max-h-screen overflow-y-auto w-full">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Detalles del Producto en Cola</h2>
                <button
                  onClick={() => setShowDetails(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <div className="grid grid-cols-2 gap-6 mb-6">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-3">Información General</h3>
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm text-gray-600">ID del Producto</label>
                      <p className="font-medium">{selectedItem.product_id}</p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-600">Estado</label>
                      <div className="mt-1">
                        <span className={getStatusColor(selectedItem.verification_status)}>
                          {selectedItem.status_display}
                        </span>
                      </div>
                    </div>
                    <div>
                      <label className="text-sm text-gray-600">Prioridad</label>
                      <div className="mt-1">
                        <span className={getPriorityColor(selectedItem.priority)}>
                          {selectedItem.priority_display}
                        </span>
                      </div>
                    </div>
                    <div>
                      <label className="text-sm text-gray-600">Días en Cola</label>
                      <p className="font-medium">{selectedItem.days_in_queue} días</p>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-3">Fechas y Tiempos</h3>
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm text-gray-600">Creado</label>
                      <p className="font-medium">{formatDate(selectedItem.created_at)}</p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-600">Llegada Esperada</label>
                      <p className="font-medium">{formatDate(selectedItem.expected_arrival)}</p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-600">Llegada Real</label>
                      <p className="font-medium">{formatDate(selectedItem.actual_arrival)}</p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-600">Deadline</label>
                      <p className={`font-medium ${selectedItem.is_overdue ? 'text-red-600' : ''}`}>
                        {formatDate(selectedItem.deadline)}
                        {selectedItem.is_overdue && (
                          <span className="ml-2 bg-red-100 text-red-800 text-xs px-2 py-1 rounded">
                            Vencido
                          </span>
                        )}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {selectedItem.is_delayed && (
                <div className="mb-6 p-4 border border-orange-200 bg-orange-50 rounded-lg">
                  <div className="flex items-center">
                    <AlertTriangle className="w-4 h-4 text-orange-600 mr-2" />
                    <span className="text-orange-800">
                      Este producto está retrasado
                      {selectedItem.delay_reason && (
                        <span className="ml-2">
                          - Razón: <strong>{selectedItem.delay_reason}</strong>
                        </span>
                      )}
                    </span>
                  </div>
                </div>
              )}

              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold mb-3">Estadísticas</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm text-gray-600">Intentos de Verificación</label>
                    <p className="font-medium">{selectedItem.verification_attempts}</p>
                  </div>
                  {selectedItem.processing_time_hours && (
                    <div>
                      <label className="text-sm text-gray-600">Tiempo de Procesamiento</label>
                      <p className="font-medium">{selectedItem.processing_time_hours} horas</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de workflow de verificación */}
      {showVerificationWorkflow && selectedItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-6xl max-h-screen overflow-y-auto w-full">
            <ProductVerificationWorkflow
              queueId={selectedItem.id}
              onStepComplete={handleWorkflowStepComplete}
              onClose={() => setShowVerificationWorkflow(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default IncomingProductsQueue;