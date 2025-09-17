// frontend/src/components/vendor/VendorOrderDashboard.tsx
// PRODUCTION_READY: Dashboard específico para órdenes de vendedores

import React, { useState, useEffect, useCallback } from 'react';
import {
  Package,
  Filter,
  RefreshCw,
  Download,
  Eye,
  CheckCircle,
  Truck,
  Clock,
  DollarSign,
  TrendingUp,
  AlertCircle,
  User,
  MoreVertical
} from 'lucide-react';
import { useVendorOrders, useVendorsList } from '../../hooks/useVendorOrders';
import { VENDOR_CONFIG, ORDER_STATUS_MAP, VendorOrder } from '../../config/vendorConfig';

interface VendorOrderDashboardProps {
  className?: string;
  vendorId?: string; // Para testing, normalmente viene del auth context
}

export const VendorOrderDashboard: React.FC<VendorOrderDashboardProps> = ({
  className = '',
  vendorId: propVendorId
}) => {
  // TODO_HOSTING: En producción, obtener vendorId del auth context
  const [selectedVendorId, setSelectedVendorId] = useState<string>(propVendorId || '');
  const [selectedOrder, setSelectedOrder] = useState<VendorOrder | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    search: '',
    page: 1,
    limit: VENDOR_CONFIG.ORDERS_PER_PAGE
  });

  // Hooks para datos
  const { vendors, isLoading: vendorsLoading } = useVendorsList();
  const {
    orders,
    isLoading,
    error,
    totalOrders,
    vendorEmail,
    lastUpdated,
    refresh,
    updateFilters,
    updateOrderStatus,
    clearError
  } = useVendorOrders(selectedVendorId, filters, true);

  // PRODUCTION_READY: Seleccionar vendor automáticamente en desarrollo
  React.useEffect(() => {
    if (!selectedVendorId && vendors.length > 0 && !propVendorId) {
      setSelectedVendorId(vendors[0].id);
    }
  }, [vendors, selectedVendorId, propVendorId]);

  // Handlers
  const handleStatusUpdate = async (orderId: number, newStatus: string) => {
    const success = await updateOrderStatus(orderId, newStatus);
    if (success && selectedOrder?.id === orderId) {
      setSelectedOrder(prev => prev ? { ...prev, status: newStatus } : null);
    }
  };

  const handleFilterChange = (key: string, value: any) => {
    const newFilters = { ...filters, [key]: value };
    if (key !== 'page') newFilters.page = 1; // Reset page on filter change
    setFilters(newFilters);
    updateFilters(newFilters);
  };

  // PERFORMANCE_CRITICAL: Métricas calculadas del dashboard
  const stats = React.useMemo(() => {
    const pending = orders.filter(o => o.status === 'pending').length;
    const confirmed = orders.filter(o => o.status === 'confirmed').length;
    const shipped = orders.filter(o => o.status === 'shipped').length;
    const delivered = orders.filter(o => o.status === 'delivered').length;
    const totalRevenue = orders.reduce((sum, order) => sum + order.total_amount, 0);

    return {
      totalOrders: orders.length,
      pending,
      confirmed,
      shipped,
      delivered,
      totalRevenue
    };
  }, [orders]);

  // Status options for vendor
  const statusOptions = [
    { value: 'all', label: 'Todas' },
    { value: 'pending', label: 'Pendientes' },
    { value: 'confirmed', label: 'Confirmadas' },
    { value: 'processing', label: 'Procesando' },
    { value: 'shipped', label: 'Enviadas' },
    { value: 'delivered', label: 'Entregadas' }
  ];

  // Get available status transitions for vendor
  const getVendorStatusTransitions = (currentStatus: string) => {
    switch (currentStatus) {
      case 'confirmed':
        return ['processing'];
      case 'processing':
        return ['shipped'];
      default:
        return [];
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // RENDER: Status badge component
  const getStatusBadge = (status: string) => {
    const statusConfig = ORDER_STATUS_MAP[status as keyof typeof ORDER_STATUS_MAP] || {
      label: status,
      bgColor: 'bg-gray-100',
      textColor: 'text-gray-800'
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusConfig.bgColor} ${statusConfig.textColor}`}>
        {statusConfig.label}
      </span>
    );
  };

  return (
    <div className={`min-h-screen bg-gray-50 ${className}`}>
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <Package className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Mis Órdenes
                </h1>
                <p className="text-sm text-gray-500">
                  Gestiona las órdenes de tus productos
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              {/* Selector de vendor (solo para development/testing) */}
              {vendors.length > 1 && (
                <select
                  value={selectedVendorId}
                  onChange={(e) => setSelectedVendorId(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Seleccionar vendor</option>
                  {vendors.map(vendor => (
                    <option key={vendor.id} value={vendor.id}>
                      {vendor.full_name} ({vendor.email})
                    </option>
                  ))}
                </select>
              )}

              <button
                onClick={refresh}
                disabled={isLoading}
                className="flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                Actualizar
              </button>

              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Package className="h-5 w-5 text-blue-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Total Órdenes</p>
                <p className="text-lg font-semibold text-gray-900">{stats.totalOrders}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Clock className="h-5 w-5 text-yellow-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Pendientes</p>
                <p className="text-lg font-semibold text-gray-900">{stats.pending}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <CheckCircle className="h-5 w-5 text-purple-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Confirmadas</p>
                <p className="text-lg font-semibold text-gray-900">{stats.confirmed}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <Truck className="h-5 w-5 text-indigo-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Enviadas</p>
                <p className="text-lg font-semibold text-gray-900">{stats.shipped}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <DollarSign className="h-5 w-5 text-green-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Ingresos</p>
                <p className="text-lg font-semibold text-gray-900">{formatCurrency(stats.totalRevenue)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="bg-white rounded-lg shadow-sm mb-6 p-4">
            <div className="flex items-center space-x-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Estado
                </label>
                <select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                >
                  {statusOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={() => setShowFilters(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Orders List */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Órdenes Recientes</h3>
          </div>

          {loading ? (
            <div className="p-12 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-500 mt-2">Cargando órdenes...</p>
            </div>
          ) : orders.length === 0 ? (
            <div className="p-12 text-center">
              <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No hay órdenes
              </h3>
              <p className="text-gray-500">
                {filters.status !== ''
                  ? `No hay órdenes con estado "${statusOptions.find(s => s.value === filters.status)?.label}"`
                  : 'Aún no tienes órdenes de tus productos'
                }
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Orden
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cliente
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Estado
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Items
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fecha
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {orders.map((order) => (
                    <tr key={order.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          #{order.order_number}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{order.buyer_name || 'Cliente N/A'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(order.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {order.items_count || 0} {(order.items_count || 0) === 1 ? 'item' : 'items'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {formatCurrency(order.total_amount)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {formatDate(order.created_at)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => setSelectedOrder(order)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            <Eye className="h-4 w-4" />
                          </button>

                          {/* Status update buttons for vendor */}
                          {getVendorStatusTransitions(order.status).map((nextStatus) => (
                            <button
                              key={nextStatus}
                              onClick={() => handleStatusUpdate(order.id, nextStatus)}
                              className="text-green-600 hover:text-green-900 text-xs px-2 py-1 bg-green-50 rounded"
                              title={`Marcar como ${ORDER_STATUS_MAP[nextStatus as keyof typeof ORDER_STATUS_MAP]?.label || nextStatus}`}
                            >
                              {nextStatus === 'processing' ? 'Procesar' :
                               nextStatus === 'shipped' ? 'Enviar' :
                               ORDER_STATUS_MAP[nextStatus as keyof typeof ORDER_STATUS_MAP]?.label || nextStatus}
                            </button>
                          ))}
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

      {/* Order Detail Modal */}
      {selectedOrder && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Orden #{selectedOrder.order_number}
                </h3>
                <button
                  onClick={() => setSelectedOrder(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="sr-only">Cerrar</span>
                  ×
                </button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-500">Cliente</label>
                    <p className="text-sm text-gray-900">{selectedOrder.buyer_name}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-500">Estado</label>
                    {getStatusBadge(selectedOrder.status)}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-500">Total</label>
                    <p className="text-sm font-medium text-gray-900">
                      {formatCurrency(selectedOrder.total_amount)}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-500">Items</label>
                    <p className="text-sm text-gray-900">
                      {selectedOrder.items_count || 0} {(selectedOrder.items_count || 0) === 1 ? 'item' : 'items'}
                    </p>
                  </div>
                </div>

                <div className="border-t pt-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Acciones disponibles</h4>
                  <div className="flex space-x-2">
                    {getVendorStatusTransitions(selectedOrder.status).map((nextStatus) => (
                      <button
                        key={nextStatus}
                        onClick={() => {
                          handleStatusUpdate(selectedOrder.id, nextStatus);
                          setSelectedOrder(null);
                        }}
                        className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
                      >
                        Marcar como {ORDER_STATUS_MAP[nextStatus as keyof typeof ORDER_STATUS_MAP]?.label || nextStatus}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VendorOrderDashboard;