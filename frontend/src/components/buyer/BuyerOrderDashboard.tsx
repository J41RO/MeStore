// frontend/src/components/buyer/BuyerOrderDashboard.tsx
// PRODUCTION_READY: Dashboard de órdenes mejorado para compradores

import React, { useState, useEffect, useCallback } from 'react';
import {
  ShoppingBag,
  Search,
  Filter,
  RefreshCw,
  Eye,
  Truck,
  Package,
  CheckCircle,
  Clock,
  MapPin,
  Calendar,
  AlertCircle
} from 'lucide-react';
import { orderService } from '../../services/orderService';
import { useAuthStore } from '../../stores/authStore';
import { Order, TrackingInfo } from '../../types/orders';
import { ORDER_STATUS_LABELS, ORDER_STATUS_COLORS } from '../../types/orders';
import { OrderTimeline } from './OrderTimeline';

interface BuyerOrderDashboardProps {
  className?: string;
}

export const BuyerOrderDashboard: React.FC<BuyerOrderDashboardProps> = ({
  className = ''
}) => {
  const { user } = useAuthStore();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [trackingInfo, setTrackingInfo] = useState<TrackingInfo | null>(null);
  const [loadingTracking, setLoadingTracking] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showFilters, setShowFilters] = useState(false);

  // Load buyer orders
  const loadBuyerOrders = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const filters: any = {};

      if (statusFilter !== 'all') {
        filters.status = statusFilter;
      }

      if (searchTerm) {
        filters.search = searchTerm;
      }

      const response = await orderService.getMyOrders(filters);
      setOrders(response.data.orders);
    } catch (err: any) {
      console.error('Error loading buyer orders:', err);
      setError(err.message || 'Error al cargar las órdenes');
      setOrders([]);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, searchTerm]);

  // Load tracking information
  const loadTrackingInfo = async (orderId: string) => {
    try {
      setLoadingTracking(true);
      const response = await orderService.getBuyerOrderTracking(orderId);
      setTrackingInfo(response.data);
    } catch (err: any) {
      console.error('Error loading tracking info:', err);
      setTrackingInfo(null);
    } finally {
      setLoadingTracking(false);
    }
  };

  // Initial load and filter changes
  useEffect(() => {
    loadBuyerOrders();
  }, [loadBuyerOrders]);

  // Handle order selection and load tracking
  const handleOrderSelect = (order: Order) => {
    setSelectedOrder(order);
    setTrackingInfo(null);
    if (order.id) {
      loadTrackingInfo(order.id);
    }
  };

  // Handle search
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadBuyerOrders();
  };

  // Calculate stats
  const stats = {
    total: orders.length,
    pending: orders.filter(o => o.status === 'pending').length,
    processing: orders.filter(o => ['confirmed', 'processing'].includes(o.status)).length,
    shipped: orders.filter(o => o.status === 'shipped').length,
    delivered: orders.filter(o => o.status === 'delivered').length,
    totalSpent: orders.reduce((sum, order) => sum + order.total_amount, 0),
  };

  // Status options for buyers
  const statusOptions = [
    { value: 'all', label: 'Todas' },
    { value: 'pending', label: 'Pendientes' },
    { value: 'confirmed', label: 'Confirmadas' },
    { value: 'processing', label: 'Procesando' },
    { value: 'shipped', label: 'Enviadas' },
    { value: 'delivered', label: 'Entregadas' },
    { value: 'cancelled', label: 'Canceladas' }
  ];

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

  const getStatusBadge = (status: string) => {
    const statusKey = status as keyof typeof ORDER_STATUS_COLORS;
    const colorClass = ORDER_STATUS_COLORS[statusKey] || 'bg-gray-100 text-gray-800';
    const label = ORDER_STATUS_LABELS[statusKey] || status;

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>
        {label}
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
              <ShoppingBag className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Mis Compras
                </h1>
                <p className="text-sm text-gray-500">
                  Historial y seguimiento de pedidos
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <form onSubmit={handleSearch} className="flex items-center">
                <div className="relative">
                  <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Buscar orden..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-9 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <button
                  type="submit"
                  className="ml-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
                >
                  Buscar
                </button>
              </form>

              <button
                onClick={loadBuyerOrders}
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
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <ShoppingBag className="h-5 w-5 text-blue-600" />
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
                <Package className="h-5 w-5 text-purple-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Procesando</p>
                <p className="text-lg font-semibold text-gray-900">{stats.processing}</p>
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
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Entregadas</p>
                <p className="text-lg font-semibold text-gray-900">{stats.delivered}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <div className="p-2 bg-emerald-100 rounded-lg">
                <span className="h-5 w-5 text-emerald-600 text-xs font-bold">$</span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Total Gastado</p>
                <p className="text-lg font-semibold text-gray-900">{formatCurrency(stats.totalSpent)}</p>
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
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
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

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Orders List */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Historial de Pedidos</h3>
              </div>

              {loading ? (
                <div className="p-12 text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="text-gray-500 mt-2">Cargando pedidos...</p>
                </div>
              ) : orders.length === 0 ? (
                <div className="p-12 text-center">
                  <ShoppingBag className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    No hay pedidos
                  </h3>
                  <p className="text-gray-500">
                    {searchTerm || statusFilter !== 'all'
                      ? 'No se encontraron pedidos con los filtros aplicados'
                      : 'Aún no has realizado ningún pedido'
                    }
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {orders.map((order) => (
                    <div
                      key={order.id}
                      className={`p-6 hover:bg-gray-50 cursor-pointer transition-colors ${
                        selectedOrder?.id === order.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                      }`}
                      onClick={() => handleOrderSelect(order)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-3">
                          <h4 className="text-lg font-medium text-gray-900">
                            #{order.order_number}
                          </h4>
                          {getStatusBadge(order.status)}
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-semibold text-gray-900">
                            {formatCurrency(order.total_amount)}
                          </p>
                          <p className="text-sm text-gray-500">
                            {formatDate(order.created_at)}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span className="flex items-center">
                            <Package className="h-4 w-4 mr-1" />
                            {order.items.length} {order.items.length === 1 ? 'producto' : 'productos'}
                          </span>
                          {order.shipping_address && (
                            <span className="flex items-center">
                              <MapPin className="h-4 w-4 mr-1" />
                              {order.shipping_city || 'Dirección registrada'}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center space-x-2">
                          {order.tracking_number && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              <Truck className="h-3 w-3 mr-1" />
                              Con seguimiento
                            </span>
                          )}
                          <Eye className="h-4 w-4 text-gray-400" />
                        </div>
                      </div>

                      {/* Order Items Preview */}
                      <div className="mt-3 border-t pt-3">
                        <div className="flex -space-x-2 overflow-hidden">
                          {order.items.slice(0, 3).map((item, idx) => (
                            <div
                              key={idx}
                              className="inline-block h-8 w-8 rounded-full ring-2 ring-white bg-gray-200 flex items-center justify-center text-xs font-medium text-gray-600"
                              title={item.product.name}
                            >
                              {item.product.name.charAt(0)}
                            </div>
                          ))}
                          {order.items.length > 3 && (
                            <div className="inline-block h-8 w-8 rounded-full ring-2 ring-white bg-gray-300 flex items-center justify-center text-xs font-medium text-gray-600">
                              +{order.items.length - 3}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Order Details & Tracking */}
          <div className="lg:col-span-1">
            {selectedOrder ? (
              <div className="space-y-6">
                {/* Order Details */}
                <div className="bg-white rounded-lg shadow-sm sticky top-6">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h3 className="text-lg font-medium text-gray-900">
                      Detalles de la Orden
                    </h3>
                  </div>

                  <div className="p-6 space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-gray-500">Número:</span>
                        <p className="text-gray-900">#{selectedOrder.order_number}</p>
                      </div>
                      <div>
                        <span className="font-medium text-gray-500">Estado:</span>
                        <div className="mt-1">{getStatusBadge(selectedOrder.status)}</div>
                      </div>
                      <div>
                        <span className="font-medium text-gray-500">Total:</span>
                        <p className="text-gray-900 font-medium">
                          {formatCurrency(selectedOrder.total_amount)}
                        </p>
                      </div>
                      <div>
                        <span className="font-medium text-gray-500">Fecha:</span>
                        <p className="text-gray-900">{formatDate(selectedOrder.created_at)}</p>
                      </div>
                    </div>

                    {selectedOrder.tracking_number && (
                      <div className="border-t pt-4">
                        <span className="font-medium text-gray-500">Número de seguimiento:</span>
                        <p className="text-gray-900 font-mono text-sm">
                          {selectedOrder.tracking_number}
                        </p>
                      </div>
                    )}

                    <div className="border-t pt-4">
                      <span className="font-medium text-gray-500">Dirección de entrega:</span>
                      <div className="mt-1 text-sm text-gray-900">
                        <p>{selectedOrder.shipping_name}</p>
                        <p>{selectedOrder.shipping_address}</p>
                        {selectedOrder.shipping_city && <p>{selectedOrder.shipping_city}</p>}
                      </div>
                    </div>

                    <div className="border-t pt-4">
                      <span className="font-medium text-gray-500">Productos ({selectedOrder.items.length}):</span>
                      <div className="mt-2 space-y-2">
                        {selectedOrder.items.map((item) => (
                          <div key={item.id} className="flex items-center justify-between text-sm">
                            <span className="text-gray-900">{item.product.name}</span>
                            <span className="text-gray-500">x{item.quantity}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Order Tracking */}
                {loadingTracking ? (
                  <div className="bg-white rounded-lg shadow-sm p-6 text-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="text-gray-500 mt-2 text-sm">Cargando seguimiento...</p>
                  </div>
                ) : trackingInfo ? (
                  <OrderTimeline trackingInfo={trackingInfo} />
                ) : (
                  <div className="bg-white rounded-lg shadow-sm p-6 text-center">
                    <MapPin className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-500 text-sm">
                      {selectedOrder.tracking_number
                        ? 'Información de seguimiento no disponible'
                        : 'Esta orden aún no tiene número de seguimiento'
                      }
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm p-6 text-center sticky top-6">
                <ShoppingBag className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Selecciona una orden
                </h3>
                <p className="text-sm text-gray-500">
                  Haz clic en cualquier pedido para ver sus detalles y seguimiento
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BuyerOrderDashboard;