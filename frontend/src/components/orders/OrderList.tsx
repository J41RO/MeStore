// ~/frontend/src/components/orders/OrderList.tsx
// PRODUCTION_READY: Lista de órdenes con paginación y acciones enterprise

import React from 'react';
import { 
  Eye, 
  Clock, 
  Package, 
  Truck, 
  CheckCircle, 
  XCircle, 
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { 
  Order, 
  OrderStatus, 
  ORDER_STATUS_LABELS, 
  ORDER_STATUS_COLORS 
} from '../../types/orders';

interface OrderListProps {
  orders: Order[];
  loading: boolean;
  selectedOrderId?: string;
  onOrderSelect: (order: Order) => void;
  onStatusUpdate: (orderId: string, status: OrderStatus, notes?: string) => void;
  onPageChange: (page: number) => void;
  currentPage: number;
  totalOrders: number;
  pageSize: number;
  userRole?: 'admin' | 'vendor' | 'buyer';
}

const StatusIcon: React.FC<{ status: OrderStatus; className?: string }> = ({ status, className = "h-4 w-4" }) => {
  switch (status) {
    case OrderStatus.PENDING:
      return <Clock className={`${className} text-yellow-500`} />;
    case OrderStatus.CONFIRMED:
    case OrderStatus.PROCESSING:
      return <Package className={`${className} text-blue-500`} />;
    case OrderStatus.SHIPPED:
      return <Truck className={`${className} text-purple-500`} />;
    case OrderStatus.DELIVERED:
      return <CheckCircle className={`${className} text-green-500`} />;
    case OrderStatus.CANCELLED:
    case OrderStatus.REFUNDED:
      return <XCircle className={`${className} text-red-500`} />;
    default:
      return <Package className={`${className} text-gray-500`} />;
  }
};

export const OrderList: React.FC<OrderListProps> = ({
  orders,
  loading,
  selectedOrderId,
  onOrderSelect,
  onStatusUpdate,
  onPageChange,
  currentPage,
  totalOrders,
  pageSize,
  userRole = 'admin'
}) => {
  // Calculate pagination
  const totalPages = Math.ceil(totalOrders / pageSize);
  const startIndex = (currentPage - 1) * pageSize + 1;
  const endIndex = Math.min(currentPage * pageSize, totalOrders);

  // Format currency
  const formatCurrency = (amount: number, currency = 'COP'): string => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency,
      minimumFractionDigits: 0
    }).format(amount);
  };

  // Format date
  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Handle quick status changes (for admin/vendor)
  const handleQuickStatusChange = (order: Order, newStatus: OrderStatus) => {
    if (userRole === 'buyer') return; // Buyers can't change status
    onStatusUpdate(order.id, newStatus);
  };

  // Get available status transitions
  const getAvailableTransitions = (currentStatus: OrderStatus): OrderStatus[] => {
    switch (currentStatus) {
      case OrderStatus.PENDING:
        return [OrderStatus.CONFIRMED, OrderStatus.CANCELLED];
      case OrderStatus.CONFIRMED:
        return [OrderStatus.PROCESSING, OrderStatus.CANCELLED];
      case OrderStatus.PROCESSING:
        return [OrderStatus.SHIPPED, OrderStatus.CANCELLED];
      case OrderStatus.SHIPPED:
        return [OrderStatus.DELIVERED];
      default:
        return [];
    }
  };

  if (loading && orders.length === 0) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="mb-4 p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-8 h-8 bg-gray-200 rounded"></div>
                  <div>
                    <div className="w-32 h-4 bg-gray-200 rounded mb-2"></div>
                    <div className="w-48 h-3 bg-gray-200 rounded"></div>
                  </div>
                </div>
                <div className="w-20 h-6 bg-gray-200 rounded"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">
            Órdenes ({totalOrders})
          </h3>
          <div className="text-sm text-gray-500">
            {totalOrders > 0 ? `${startIndex}-${endIndex} de ${totalOrders}` : '0 órdenes'}
          </div>
        </div>
      </div>

      {/* Orders List */}
      <div className="divide-y divide-gray-200">
        {orders.length === 0 ? (
          <div className="p-12 text-center">
            <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No se encontraron órdenes
            </h3>
            <p className="text-gray-500">
              {loading ? 'Cargando órdenes...' : 'Intenta ajustar los filtros o crear una nueva orden'}
            </p>
          </div>
        ) : (
          orders.map((order) => (
            <div
              key={order.id}
              className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                selectedOrderId === order.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
              }`}
              onClick={() => onOrderSelect(order)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 flex-1 min-w-0">
                  <StatusIcon status={order.status} className="h-5 w-5 flex-shrink-0" />
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {order.order_number}
                      </p>
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${ORDER_STATUS_COLORS[order.status]}`}>
                        {ORDER_STATUS_LABELS[order.status]}
                      </span>
                    </div>
                    
                    <div className="mt-1 flex items-center text-sm text-gray-500 space-x-4">
                      <span>{order.buyer.nombre}</span>
                      <span>•</span>
                      <span>{order.items.length} {order.items.length === 1 ? 'artículo' : 'artículos'}</span>
                      <span>•</span>
                      <span>{formatDate(order.created_at)}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm font-semibold text-gray-900">
                      {formatCurrency(order.total_amount, order.currency)}
                    </p>
                    {order.tracking_number && (
                      <p className="text-xs text-gray-500">
                        #{order.tracking_number}
                      </p>
                    )}
                  </div>

                  {/* Quick Actions */}
                  {userRole !== 'buyer' && (
                    <div className="flex items-center space-x-1">
                      {getAvailableTransitions(order.status).slice(0, 2).map((status) => (
                        <button
                          key={status}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleQuickStatusChange(order, status);
                          }}
                          className="p-1 text-gray-400 hover:text-gray-600 rounded"
                          title={`Cambiar a ${ORDER_STATUS_LABELS[status]}`}
                        >
                          <StatusIcon status={status} className="h-4 w-4" />
                        </button>
                      ))}
                    </div>
                  )}

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onOrderSelect(order);
                    }}
                    className="p-1 text-gray-400 hover:text-gray-600 rounded"
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Additional Info Row */}
              <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center space-x-4">
                  <span>📍 {order.shipping_city || 'Ciudad no especificada'}</span>
                  {order.estimated_delivery_days && (
                    <span>⏰ {order.estimated_delivery_days} días estimados</span>
                  )}
                </div>
                
                {order.notes && (
                  <div className="flex items-center">
                    <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                      📝 Con notas
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="px-6 py-4 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Mostrando <span className="font-medium">{startIndex}</span> a{' '}
              <span className="font-medium">{endIndex}</span> de{' '}
              <span className="font-medium">{totalOrders}</span> órdenes
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => onPageChange(currentPage - 1)}
                disabled={currentPage <= 1}
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="h-4 w-4 mr-1" />
                Anterior
              </button>
              
              <div className="flex items-center space-x-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNumber;
                  if (totalPages <= 5) {
                    pageNumber = i + 1;
                  } else if (currentPage <= 3) {
                    pageNumber = i + 1;
                  } else if (currentPage >= totalPages - 2) {
                    pageNumber = totalPages - 4 + i;
                  } else {
                    pageNumber = currentPage - 2 + i;
                  }
                  
                  return (
                    <button
                      key={pageNumber}
                      onClick={() => onPageChange(pageNumber)}
                      className={`px-3 py-2 text-sm font-medium rounded-md ${
                        pageNumber === currentPage
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      {pageNumber}
                    </button>
                  );
                })}
              </div>
              
              <button
                onClick={() => onPageChange(currentPage + 1)}
                disabled={currentPage >= totalPages}
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Siguiente
                <ChevronRight className="h-4 w-4 ml-1" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Loading overlay */}
      {loading && orders.length > 0 && (
        <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <span className="text-sm text-gray-600">Actualizando...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrderList;