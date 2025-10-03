import React, { useState, useEffect } from 'react';
import vendorOrderService, {
  VendorOrder,
  VendorOrderItem,
  VendorOrderStats
} from '../../services/vendorOrderService';

/**
 * VendorOrders - Main page for vendor order management
 *
 * Features:
 * - List all orders for the vendor
 * - Filter by status
 * - Update order item status (preparing, ready_to_ship)
 * - Responsive grid layout
 * - Real-time stats
 */

const VendorOrders: React.FC = () => {
  const [orders, setOrders] = useState<VendorOrder[]>([]);
  const [stats, setStats] = useState<VendorOrderStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [updatingItem, setUpdatingItem] = useState<string | null>(null);

  // Fetch orders and stats
  useEffect(() => {
    loadOrders();
    loadStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter]);

  const loadOrders = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await vendorOrderService.getOrders(
        0,
        50,
        statusFilter === 'all' ? null : statusFilter
      );
      setOrders(response.orders);
    } catch (err) {
      const errorMessage = err instanceof Error && 'response' in err
        ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : 'Error al cargar órdenes';
      setError(errorMessage || 'Error al cargar órdenes');
      console.error('Error loading orders:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const statsData = await vendorOrderService.getStats();
      setStats(statsData);
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  };

  const handleUpdateItemStatus = async (
    orderId: string,
    itemId: string,
    newStatus: VendorOrderItem['status']
  ) => {
    try {
      setUpdatingItem(itemId);
      setError(null);

      await vendorOrderService.updateItemStatus(orderId, itemId, newStatus);

      // Update local state
      setOrders(prevOrders =>
        prevOrders.map(order => {
          if (order.id === orderId) {
            return {
              ...order,
              items: order.items.map(item =>
                item.id === itemId ? { ...item, status: newStatus } : item
              )
            };
          }
          return order;
        })
      );

      // Reload stats
      await loadStats();
    } catch (err) {
      const errorMessage = err instanceof Error && 'response' in err
        ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : 'Error al actualizar estado';
      setError(errorMessage || 'Error al actualizar estado');
      console.error('Error updating item status:', err);
    } finally {
      setUpdatingItem(null);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
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

  if (loading && orders.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando órdenes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Mis Órdenes</h1>
          <p className="mt-2 text-gray-600">
            Gestiona las órdenes de tus productos
          </p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600">Total Órdenes</div>
              <div className="text-2xl font-bold text-gray-900 mt-1">
                {stats.total_orders}
              </div>
            </div>
            <div className="bg-gradient-to-br from-amber-500 to-amber-600 text-white rounded-lg shadow p-6">
              <div className="text-sm text-amber-100">Pendientes</div>
              <div className="text-2xl font-bold mt-1">{stats.pending_items}</div>
            </div>
            <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-lg shadow p-6">
              <div className="text-sm text-red-100">Preparando</div>
              <div className="text-2xl font-bold mt-1">{stats.preparing_items}</div>
            </div>
            <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg shadow p-6">
              <div className="text-sm text-green-100">Listos</div>
              <div className="text-2xl font-bold mt-1">{stats.ready_to_ship_items}</div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium text-gray-700">
              Filtrar por estado:
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="all">Todos</option>
              <option value="pending">Pendiente</option>
              <option value="preparing">Preparando</option>
              <option value="ready_to_ship">Listo para Envío</option>
              <option value="shipped">Enviado</option>
              <option value="delivered">Entregado</option>
            </select>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Orders Grid */}
        {orders.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              No hay órdenes
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              {statusFilter === 'all'
                ? 'Aún no has recibido ninguna orden.'
                : 'No hay órdenes con el filtro seleccionado.'}
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {orders.map((order) => (
              <div
                key={order.id}
                className="bg-white rounded-lg shadow overflow-hidden"
              >
                {/* Order Header */}
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-gray-200">
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        Orden #{order.order_number}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {formatDate(order.order_date)}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-600">Cliente</div>
                      <div className="font-medium text-gray-900">
                        {order.customer_name}
                      </div>
                      {order.customer_phone && (
                        <div className="text-sm text-gray-600">
                          {order.customer_phone}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Order Items */}
                <div className="px-6 py-4 space-y-4">
                  {order.items.map((item) => (
                    <div
                      key={item.id}
                      className="flex flex-col sm:flex-row gap-4 p-4 bg-gray-50 rounded-lg"
                      style={{
                        borderLeft: `4px solid ${vendorOrderService.getStatusColor(item.status)}`
                      }}
                    >
                      {/* Item Info */}
                      <div className="flex-1">
                        <div className="flex items-start gap-4">
                          {item.product_image_url && (
                            <img
                              src={item.product_image_url}
                              alt={item.product_name}
                              className="w-16 h-16 object-cover rounded"
                            />
                          )}
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-900">
                              {item.product_name}
                            </h4>
                            <p className="text-sm text-gray-600">
                              SKU: {item.product_sku}
                            </p>
                            <div className="mt-2 flex items-center gap-4 text-sm">
                              <span className="text-gray-600">
                                Cantidad: <span className="font-medium">{item.quantity}</span>
                              </span>
                              <span className="text-gray-600">
                                Precio: <span className="font-medium">{formatCurrency(item.unit_price)}</span>
                              </span>
                              <span className="text-gray-900 font-semibold">
                                Total: {formatCurrency(item.total_price)}
                              </span>
                            </div>
                            <div className="mt-2">
                              <span
                                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white"
                                style={{
                                  backgroundColor: vendorOrderService.getStatusColor(item.status)
                                }}
                              >
                                {vendorOrderService.getStatusLabel(item.status)}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex sm:flex-col gap-2 sm:min-w-[140px]">
                        <button
                          onClick={() => handleUpdateItemStatus(order.id, item.id, 'preparing')}
                          disabled={
                            updatingItem === item.id ||
                            item.status === 'preparing' ||
                            item.status === 'ready_to_ship' ||
                            item.status === 'shipped' ||
                            item.status === 'delivered'
                          }
                          className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                            item.status === 'preparing' ||
                            item.status === 'ready_to_ship' ||
                            item.status === 'shipped' ||
                            item.status === 'delivered'
                              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                              : 'bg-amber-500 text-white hover:bg-amber-600'
                          }`}
                        >
                          {updatingItem === item.id ? (
                            <span className="flex items-center justify-center">
                              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                              </svg>
                            </span>
                          ) : (
                            'Preparando'
                          )}
                        </button>
                        <button
                          onClick={() => handleUpdateItemStatus(order.id, item.id, 'ready_to_ship')}
                          disabled={
                            updatingItem === item.id ||
                            item.status === 'pending' ||
                            item.status === 'ready_to_ship' ||
                            item.status === 'shipped' ||
                            item.status === 'delivered'
                          }
                          className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                            item.status === 'pending' ||
                            item.status === 'ready_to_ship' ||
                            item.status === 'shipped' ||
                            item.status === 'delivered'
                              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                              : 'bg-green-500 text-white hover:bg-green-600'
                          }`}
                        >
                          {updatingItem === item.id ? (
                            <span className="flex items-center justify-center">
                              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                              </svg>
                            </span>
                          ) : (
                            'Listo'
                          )}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Order Footer */}
                <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <div className="text-sm text-gray-600">
                      <div className="font-medium">Dirección de Envío:</div>
                      <div>
                        {order.shipping_address}, {order.shipping_city}, {order.shipping_state}
                      </div>
                      {order.notes && (
                        <div className="mt-2">
                          <span className="font-medium">Notas:</span> {order.notes}
                        </div>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-600">Total de la Orden</div>
                      <div className="text-2xl font-bold text-gray-900">
                        {formatCurrency(order.total_amount)}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default VendorOrders;
