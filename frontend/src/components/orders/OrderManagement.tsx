// ~/frontend/src/components/orders/OrderManagement.tsx
// PRODUCTION_READY: Componente principal de gestión de órdenes enterprise

import React, { useState, useEffect, useCallback } from 'react';
import { Package, Filter, RefreshCw, Download, Plus } from 'lucide-react';
import { OrderList } from './OrderList';
import { OrderFilters } from './OrderFilters';
import { OrderDetails } from './OrderDetails';
import { CreateOrderModal } from './CreateOrderModal';
import { OrderErrorBoundary } from './OrderErrorBoundary';
import { orderService } from '../../services/orderService';
import { Order, OrderFilters as OrderFiltersType, OrderStatus } from '../../types/orders';

interface OrderManagementProps {
  userRole?: 'admin' | 'vendor' | 'buyer';
  buyerId?: string;
}

export const OrderManagement: React.FC<OrderManagementProps> = ({
  userRole = 'admin',
  buyerId
}) => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [totalOrders, setTotalOrders] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  
  // Filters state
  const [filters, setFilters] = useState<OrderFiltersType>({
    status: 'all',
    page: 1,
    limit: 20
  });

  // Load orders with error handling and retry
  const loadOrders = useCallback(async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      setError(null);

      // Apply buyer filter for buyer role
      const queryFilters = userRole === 'buyer' && buyerId
        ? { ...filters, buyer_id: buyerId }
        : filters;

      const response = await orderService.getOrdersWithRetry(queryFilters);
      
      setOrders(response.data.orders);
      setTotalOrders(response.data.total);
      setCurrentPage(response.data.page);
    } catch (err: any) {
      console.error('Error loading orders:', err);
      setError(err.message || 'Error al cargar las órdenes');
      setOrders([]);
    } finally {
      setLoading(false);
    }
  }, [filters, userRole, buyerId]);

  // Initial load and filter changes
  useEffect(() => {
    loadOrders();
  }, [loadOrders]);

  // Handle filter changes
  const handleFilterChange = useCallback((newFilters: Partial<OrderFiltersType>) => {
    setFilters(prev => ({
      ...prev,
      ...newFilters,
      page: newFilters.page || 1 // Reset to first page on filter change
    }));
  }, []);

  // Handle page changes
  const handlePageChange = useCallback((page: number) => {
    setFilters(prev => ({ ...prev, page }));
  }, []);

  // Handle order selection
  const handleOrderSelect = useCallback((order: Order) => {
    setSelectedOrder(order);
  }, []);

  // Handle order status update
  const handleStatusUpdate = useCallback(async (orderId: string, status: OrderStatus, notes?: string) => {
    try {
      await orderService.updateOrderStatus(orderId, { status, notes });
      
      // Update local state
      setOrders(prev => prev.map(order => 
        order.id === orderId 
          ? { ...order, status, updated_at: new Date().toISOString() }
          : order
      ));

      // Update selected order if it matches
      if (selectedOrder?.id === orderId) {
        setSelectedOrder(prev => prev ? { ...prev, status, updated_at: new Date().toISOString() } : null);
      }

      // Show success message (you can integrate with a toast library)
      console.log('Estado actualizado exitosamente');
    } catch (err: any) {
      console.error('Error updating order status:', err);
      setError(err.message || 'Error al actualizar el estado');
    }
  }, [selectedOrder]);

  // Handle order creation
  const handleOrderCreate = useCallback(async () => {
    setShowCreateModal(false);
    await loadOrders(); // Reload orders after creation
  }, [loadOrders]);

  // Export orders
  const handleExport = useCallback(async () => {
    try {
      // For now, just log - you can implement actual export functionality
      console.log('Exporting orders with filters:', filters);
      
      // Future: implement CSV/Excel export
      // const exportData = await orderService.exportOrders(filters);
      // downloadFile(exportData, 'orders.csv');
      
    } catch (err: any) {
      console.error('Error exporting orders:', err);
      setError(err.message || 'Error al exportar órdenes');
    }
  }, [filters]);

  // Calculate stats
  const stats = {
    total: totalOrders,
    pending: orders.filter(o => o.status === OrderStatus.PENDING).length,
    processing: orders.filter(o => [OrderStatus.CONFIRMED, OrderStatus.PROCESSING].includes(o.status)).length,
    shipped: orders.filter(o => o.status === OrderStatus.SHIPPED).length,
    delivered: orders.filter(o => o.status === OrderStatus.DELIVERED).length
  };

  return (
    <OrderErrorBoundary>
      <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <Package className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Gestión de Órdenes
                </h1>
                <p className="text-sm text-gray-500">
                  {userRole === 'buyer' ? 'Mis pedidos' : 'Panel de administración'}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={() => loadOrders()}
                disabled={loading}
                className="flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Actualizar
              </button>

              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </button>

              <button
                onClick={handleExport}
                className="flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </button>

              {(userRole === 'admin' || userRole === 'vendor') && (
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Nueva Orden
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-gray-100 rounded-lg">
                <Package className="h-5 w-5 text-gray-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Total</p>
                <p className="text-lg font-semibold text-gray-900">{stats.total}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Package className="h-5 w-5 text-yellow-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Pendientes</p>
                <p className="text-lg font-semibold text-gray-900">{stats.pending}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Package className="h-5 w-5 text-blue-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Procesando</p>
                <p className="text-lg font-semibold text-gray-900">{stats.processing}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Package className="h-5 w-5 text-purple-600" />
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
                <Package className="h-5 w-5 text-green-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Entregadas</p>
                <p className="text-lg font-semibold text-gray-900">{stats.delivered}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="bg-white rounded-lg shadow-sm mb-6">
            <OrderFilters
              filters={filters}
              onFiltersChange={handleFilterChange}
              onClose={() => setShowFilters(false)}
            />
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Orders List */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm">
              {error && (
                <div className="p-4 border-b border-red-200 bg-red-50">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              <OrderList
                orders={orders}
                loading={loading}
                selectedOrderId={selectedOrder?.id}
                onOrderSelect={handleOrderSelect}
                onStatusUpdate={handleStatusUpdate}
                onPageChange={handlePageChange}
                currentPage={currentPage}
                totalOrders={totalOrders}
                pageSize={filters.limit || 20}
                userRole={userRole}
              />
            </div>
          </div>

          {/* Order Details */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm sticky top-6">
              {selectedOrder ? (
                <OrderDetails
                  order={selectedOrder}
                  onStatusUpdate={handleStatusUpdate}
                  onClose={() => setSelectedOrder(null)}
                  userRole={userRole}
                />
              ) : (
                <div className="p-6 text-center">
                  <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Selecciona una orden
                  </h3>
                  <p className="text-sm text-gray-500">
                    Haz clic en cualquier orden de la lista para ver sus detalles
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Create Order Modal */}
      {showCreateModal && (
        <CreateOrderModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSuccess={handleOrderCreate}
        />
      )}
      </div>
    </OrderErrorBoundary>
  );
};

export default OrderManagement;