import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuthContext } from '../contexts/AuthContext';
import {
  CheckCircle,
  Package,
  Truck,
  MapPin,
  Calendar,
  ShoppingBag,
  ArrowRight,
  Loader2,
  AlertCircle
} from 'lucide-react';

interface OrderDetails {
  id: number;
  order_number: string;
  status: string;
  subtotal: number;
  tax_amount: number;
  shipping_cost: number;
  total_amount: number;
  created_at: string;
  shipping_info: {
    name: string;
    phone: string;
    email: string;
    address: string;
    city: string;
    state: string;
    postal_code?: string;
  };
  items: Array<{
    id: number;
    product_id: string;
    product_name: string;
    product_sku: string;
    product_image_url?: string;
    unit_price: number;
    quantity: number;
    total_price: number;
  }>;
  notes?: string;
}

const OrderConfirmationPage: React.FC = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const { getToken } = useAuthContext();

  const [order, setOrder] = useState<OrderDetails | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchOrderDetails = async () => {
      if (!orderId) {
        setError('No se encontró el ID del pedido');
        setIsLoading(false);
        return;
      }

      try {
        const token = getToken();
        if (!token) {
          throw new Error('No se encontró token de autenticación');
        }

        const BACKEND_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${BACKEND_URL}/api/v1/orders/${orderId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('No se pudo cargar la información del pedido');
        }

        const data = await response.json();
        setOrder(data);
      } catch (err) {
        console.error('Error fetching order:', err);
        setError(err instanceof Error ? err.message : 'Error al cargar el pedido');
      } finally {
        setIsLoading(false);
      }
    };

    fetchOrderDetails();
  }, [orderId, getToken]);

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('es-CO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  const getEstimatedDelivery = (): string => {
    const deliveryDate = new Date();
    deliveryDate.setDate(deliveryDate.getDate() + 5); // 5 days from now
    return new Intl.DateTimeFormat('es-CO', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(deliveryDate);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Cargando detalles del pedido...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !order) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md mx-auto text-center p-8">
          <div className="mx-auto w-24 h-24 bg-red-100 rounded-full flex items-center justify-center mb-6">
            <AlertCircle className="w-12 h-12 text-red-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Error al cargar el pedido</h1>
          <p className="text-gray-600 mb-6">{error || 'No se encontró el pedido'}</p>
          <button
            onClick={() => navigate('/marketplace')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Volver al Marketplace
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Success Header */}
        <div className="bg-white rounded-lg shadow-sm p-8 mb-8 text-center">
          <div className="mx-auto w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mb-6">
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>

          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            ¡Pedido Confirmado!
          </h1>
          <p className="text-lg text-gray-600 mb-4">
            Gracias por tu compra. Tu pedido ha sido recibido y está siendo procesado.
          </p>

          <div className="inline-flex items-center gap-2 bg-blue-50 px-6 py-3 rounded-lg">
            <Package className="w-5 h-5 text-blue-600" />
            <span className="text-sm font-medium text-gray-700">
              Número de pedido:
            </span>
            <span className="text-lg font-bold text-blue-600">
              {order.order_number}
            </span>
          </div>
        </div>

        {/* Order Timeline */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Estado del Pedido</h2>

          <div className="relative">
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>

            <div className="space-y-6">
              {/* Step 1: Order Received */}
              <div className="relative flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-green-600 rounded-full flex items-center justify-center z-10">
                  <CheckCircle className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">Pedido Recibido</h3>
                  <p className="text-sm text-gray-500">{formatDate(order.created_at)}</p>
                </div>
              </div>

              {/* Step 2: Processing */}
              <div className="relative flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center z-10">
                  <Package className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">En Proceso</h3>
                  <p className="text-sm text-gray-500">Preparando tu pedido para envío</p>
                </div>
              </div>

              {/* Step 3: Shipping */}
              <div className="relative flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center z-10">
                  <Truck className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-gray-500">En Camino</h3>
                  <p className="text-sm text-gray-400">Entrega estimada: {getEstimatedDelivery()}</p>
                </div>
              </div>

              {/* Step 4: Delivered */}
              <div className="relative flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center z-10">
                  <MapPin className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-gray-500">Entregado</h3>
                  <p className="text-sm text-gray-400">Te notificaremos cuando tu pedido sea entregado</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Shipping Information */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <MapPin className="w-5 h-5" />
            Información de Envío
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Nombre</p>
              <p className="font-medium text-gray-900">{order.shipping_info.name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Teléfono</p>
              <p className="font-medium text-gray-900">{order.shipping_info.phone}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Email</p>
              <p className="font-medium text-gray-900">{order.shipping_info.email}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Ciudad</p>
              <p className="font-medium text-gray-900">
                {order.shipping_info.city}, {order.shipping_info.state}
              </p>
            </div>
            <div className="md:col-span-2">
              <p className="text-sm text-gray-500">Dirección</p>
              <p className="font-medium text-gray-900">{order.shipping_info.address}</p>
            </div>
          </div>

          {order.notes && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-500">Notas del pedido</p>
              <p className="text-gray-900">{order.notes}</p>
            </div>
          )}
        </div>

        {/* Order Items */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <ShoppingBag className="w-5 h-5" />
            Artículos del Pedido
          </h2>

          <div className="space-y-4">
            {order.items.map(item => (
              <div key={item.id} className="flex gap-4 pb-4 border-b border-gray-100 last:border-b-0">
                {/* Product Image */}
                <div className="w-20 h-20 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                  {item.product_image_url ? (
                    <img
                      src={item.product_image_url}
                      alt={item.product_name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <Package className="w-8 h-8 text-gray-400" />
                    </div>
                  )}
                </div>

                {/* Product Info */}
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{item.product_name}</h3>
                  <p className="text-sm text-gray-500">SKU: {item.product_sku}</p>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-sm text-gray-600">
                      Cantidad: <span className="font-medium">{item.quantity}</span>
                    </span>
                    <span className="text-sm text-gray-600">
                      {formatCurrency(item.unit_price)} c/u
                    </span>
                  </div>
                </div>

                {/* Price */}
                <div className="text-right">
                  <p className="font-bold text-gray-900">
                    {formatCurrency(item.total_price)}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Order Totals */}
          <div className="mt-6 pt-6 border-t border-gray-200 space-y-2">
            <div className="flex justify-between text-gray-600">
              <span>Subtotal</span>
              <span>{formatCurrency(order.subtotal)}</span>
            </div>
            <div className="flex justify-between text-gray-600">
              <span>IVA (19%)</span>
              <span>{formatCurrency(order.tax_amount)}</span>
            </div>
            <div className="flex justify-between text-gray-600">
              <span>Envío</span>
              <span>
                {order.shipping_cost === 0 ? (
                  <span className="text-green-600 font-medium">GRATIS</span>
                ) : (
                  formatCurrency(order.shipping_cost)
                )}
              </span>
            </div>
            <div className="flex justify-between text-xl font-bold text-gray-900 pt-2 border-t border-gray-200">
              <span>Total</span>
              <span>{formatCurrency(order.total_amount)}</span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => navigate('/marketplace')}
            className="flex items-center justify-center gap-2 bg-white border-2 border-gray-300 hover:border-gray-400 text-gray-700 px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Seguir Comprando
            <ArrowRight className="w-5 h-5" />
          </button>

          <button
            onClick={() => navigate(`/buyer/orders/${order.id}`)}
            className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Ver Detalles del Pedido
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>

        {/* Help Section */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-bold text-gray-900 mb-2">¿Necesitas ayuda?</h3>
          <p className="text-gray-600 mb-4">
            Si tienes alguna pregunta sobre tu pedido, no dudes en contactarnos.
          </p>
          <div className="flex flex-wrap gap-4">
            <a
              href="mailto:soporte@mestore.com"
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              soporte@mestore.com
            </a>
            <a
              href="tel:+573001234567"
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              +57 300 123 4567
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderConfirmationPage;
