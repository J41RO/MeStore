// ~/frontend/src/components/orders/OrderDetails.tsx
// PRODUCTION_READY: Detalles completos de orden con tracking y acciones

import React, { useState } from 'react';
import { 
  X, 
  Package, 
  User, 
  MapPin, 
  CreditCard,
  Truck,
  Edit,
  MessageSquare,
  ExternalLink,
  Copy,
  CheckCircle2
} from 'lucide-react';
import { 
  Order, 
  OrderStatus, 
  ORDER_STATUS_LABELS, 
  ORDER_STATUS_COLORS,
  VALID_STATUS_TRANSITIONS
} from '../../types/orders';

interface OrderDetailsProps {
  order: Order;
  onStatusUpdate: (orderId: string, status: OrderStatus, notes?: string) => void;
  onClose: () => void;
  userRole?: 'admin' | 'vendor' | 'buyer';
}

export const OrderDetails: React.FC<OrderDetailsProps> = ({
  order,
  onStatusUpdate,
  onClose,
  userRole = 'admin'
}) => {
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState<OrderStatus>(order.status);
  const [statusNotes, setStatusNotes] = useState('');
  const [copying, setCopying] = useState<string | null>(null);

  // Format currency
  const formatCurrency = (amount: number, currency = 'COP'): string => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency,
      minimumFractionDigits: 0
    }).format(amount);
  };

  // Format date
  const formatDateTime = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Copy to clipboard
  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopying(label);
      setTimeout(() => setCopying(null), 2000);
    } catch (err) {
      console.error('Error copying to clipboard:', err);
    }
  };

  // Handle status update
  const handleStatusUpdate = () => {
    if (selectedStatus !== order.status) {
      onStatusUpdate(order.id, selectedStatus, statusNotes || undefined);
    }
    setShowStatusModal(false);
    setStatusNotes('');
  };

  // Get available status transitions
  const availableTransitions = VALID_STATUS_TRANSITIONS[order.status] || [];
  const canUpdateStatus = userRole !== 'buyer' && availableTransitions.length > 0;

  // Calculate order progress
  const getOrderProgress = (): { percentage: number; steps: string[] } => {
    const allSteps = [
      'Creada',
      'Confirmada', 
      'Procesando',
      'Enviada',
      'Entregada'
    ];
    
    const statusToStep = {
      [OrderStatus.PENDING]: 0,
      [OrderStatus.CONFIRMED]: 1,
      [OrderStatus.PROCESSING]: 2,
      [OrderStatus.SHIPPED]: 3,
      [OrderStatus.DELIVERED]: 4,
      [OrderStatus.CANCELLED]: -1,
      [OrderStatus.REFUNDED]: -1
    };
    
    const currentStep = statusToStep[order.status];
    if (currentStep === -1) return { percentage: 0, steps: ['Cancelada/Reembolsada'] };
    
    const percentage = ((currentStep + 1) / allSteps.length) * 100;
    return { percentage, steps: allSteps };
  };

  const orderProgress = getOrderProgress();

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center">
          <Package className="h-5 w-5 text-gray-400 mr-2" />
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              {order.order_number}
            </h3>
            <p className="text-sm text-gray-500">
              Detalles de la orden
            </p>
          </div>
        </div>
        
        <button
          onClick={onClose}
          className="p-1 text-gray-400 hover:text-gray-600"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Status and Progress */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full ${ORDER_STATUS_COLORS[order.status]}`}>
              {ORDER_STATUS_LABELS[order.status]}
            </span>
            
            {canUpdateStatus && (
              <button
                onClick={() => setShowStatusModal(true)}
                className="flex items-center px-3 py-1 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100"
              >
                <Edit className="h-4 w-4 mr-1" />
                Actualizar
              </button>
            )}
          </div>
          
          {/* Progress Bar */}
          {order.status !== OrderStatus.CANCELLED && order.status !== OrderStatus.REFUNDED && (
            <div>
              <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${orderProgress.percentage}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-xs text-gray-500">
                {orderProgress.steps.map((step, index) => (
                  <span 
                    key={step}
                    className={orderProgress.percentage >= ((index + 1) / orderProgress.steps.length) * 100 ? 'text-blue-600 font-medium' : ''}
                  >
                    {step}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Order Summary */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3">Resumen de Orden</h4>
          
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Total:</span>
              <span className="font-semibold">{formatCurrency(order.total_amount, order.currency)}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-600">Artículos:</span>
              <span>{order.items.length}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-600">Creada:</span>
              <span>{formatDateTime(order.created_at)}</span>
            </div>
            
            {order.tracking_number && (
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Tracking:</span>
                <div className="flex items-center">
                  <span className="font-mono text-sm">{order.tracking_number}</span>
                  <button
                    onClick={() => copyToClipboard(order.tracking_number!, 'tracking')}
                    className="ml-2 p-1 text-gray-400 hover:text-gray-600"
                  >
                    {copying === 'tracking' ? (
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Customer Information */}
        <div>
          <div className="flex items-center mb-3">
            <User className="h-4 w-4 text-gray-400 mr-2" />
            <h4 className="font-medium text-gray-900">Información del Cliente</h4>
          </div>
          
          <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-2 text-sm">
            <div>
              <span className="text-gray-600">Nombre:</span>
              <span className="ml-2 font-medium">{order.buyer.nombre}</span>
            </div>
            
            <div>
              <span className="text-gray-600">Email:</span>
              <span className="ml-2">{order.buyer.email}</span>
            </div>
            
            {order.buyer.telefono && (
              <div>
                <span className="text-gray-600">Teléfono:</span>
                <span className="ml-2">{order.buyer.telefono}</span>
              </div>
            )}
          </div>
        </div>

        {/* Shipping Information */}
        <div>
          <div className="flex items-center mb-3">
            <MapPin className="h-4 w-4 text-gray-400 mr-2" />
            <h4 className="font-medium text-gray-900">Información de Envío</h4>
          </div>
          
          <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-2 text-sm">
            <div>
              <span className="text-gray-600">Nombre:</span>
              <span className="ml-2 font-medium">{order.shipping_name}</span>
            </div>
            
            <div>
              <span className="text-gray-600">Dirección:</span>
              <span className="ml-2">{order.shipping_address}</span>
            </div>
            
            {order.shipping_city && (
              <div>
                <span className="text-gray-600">Ciudad:</span>
                <span className="ml-2">{order.shipping_city}</span>
              </div>
            )}
            
            {order.shipping_phone && (
              <div>
                <span className="text-gray-600">Teléfono:</span>
                <span className="ml-2">{order.shipping_phone}</span>
              </div>
            )}
            
            {order.estimated_delivery_days && (
              <div>
                <span className="text-gray-600">Entrega estimada:</span>
                <span className="ml-2">{order.estimated_delivery_days} días</span>
              </div>
            )}
          </div>
        </div>

        {/* Order Items */}
        <div>
          <h4 className="font-medium text-gray-900 mb-3">Artículos ({order.items.length})</h4>
          
          <div className="space-y-3">
            {order.items.map((item) => (
              <div key={item.id} className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-start space-x-4">
                  {item.product.image_url ? (
                    <img
                      src={item.product.image_url}
                      alt={item.product.name}
                      className="w-12 h-12 object-cover rounded-lg"
                    />
                  ) : (
                    <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                      <Package className="h-6 w-6 text-gray-400" />
                    </div>
                  )}
                  
                  <div className="flex-1 min-w-0">
                    <h5 className="text-sm font-medium text-gray-900 truncate">
                      {item.product.name}
                    </h5>
                    
                    {item.product.sku && (
                      <p className="text-xs text-gray-500 mt-1">SKU: {item.product.sku}</p>
                    )}
                    
                    {item.variant_attributes && Object.keys(item.variant_attributes).length > 0 && (
                      <div className="mt-1">
                        {Object.entries(item.variant_attributes).map(([key, value]) => (
                          <span key={key} className="inline-block px-2 py-1 mr-1 mt-1 text-xs bg-gray-100 text-gray-600 rounded">
                            {key}: {value}
                          </span>
                        ))}
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-sm text-gray-600">
                        {formatCurrency(item.unit_price)} × {item.quantity}
                      </span>
                      <span className="text-sm font-semibold text-gray-900">
                        {formatCurrency(item.total_price)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Payment Information */}
        {order.payment_method && (
          <div>
            <div className="flex items-center mb-3">
              <CreditCard className="h-4 w-4 text-gray-400 mr-2" />
              <h4 className="font-medium text-gray-900">Información de Pago</h4>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-2 text-sm">
              <div>
                <span className="text-gray-600">Método:</span>
                <span className="ml-2 font-medium">{order.payment_method}</span>
              </div>
              
              {order.payment_reference && (
                <div>
                  <span className="text-gray-600">Referencia:</span>
                  <span className="ml-2 font-mono text-sm">{order.payment_reference}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Notes */}
        {order.notes && (
          <div>
            <div className="flex items-center mb-3">
              <MessageSquare className="h-4 w-4 text-gray-400 mr-2" />
              <h4 className="font-medium text-gray-900">Notas</h4>
            </div>
            
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-sm text-gray-700">{order.notes}</p>
            </div>
          </div>
        )}

        {/* Tracking Link */}
        {order.tracking_number && (
          <div className="flex justify-center">
            <a
              href={`/track/${order.order_number}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <Truck className="h-4 w-4 mr-2" />
              Ver Tracking Completo
              <ExternalLink className="h-4 w-4 ml-2" />
            </a>
          </div>
        )}
      </div>

      {/* Status Update Modal */}
      {showStatusModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                Actualizar Estado
              </h3>
            </div>
            
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nuevo Estado
                </label>
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value as OrderStatus)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value={order.status}>{ORDER_STATUS_LABELS[order.status]} (actual)</option>
                  {availableTransitions.map((status) => (
                    <option key={status} value={status}>
                      {ORDER_STATUS_LABELS[status]}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notas (opcional)
                </label>
                <textarea
                  value={statusNotes}
                  onChange={(e) => setStatusNotes(e.target.value)}
                  placeholder="Agrega comentarios sobre el cambio de estado..."
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  rows={3}
                />
              </div>
            </div>
            
            <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => setShowStatusModal(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancelar
              </button>
              
              <button
                onClick={handleStatusUpdate}
                disabled={selectedStatus === order.status}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Actualizar Estado
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrderDetails;