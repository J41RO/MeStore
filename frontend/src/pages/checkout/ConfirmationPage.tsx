import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useCheckoutStore, formatCOP } from '../../stores/checkoutStore';
import {
  CheckCircle,
  Truck,
  Package,
  Printer,
  Mail,
  Clock,
  ShoppingBag,
  MapPin,
  Phone,
  CreditCard
} from 'lucide-react';

const ConfirmationPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const orderNumber = searchParams.get('orderNumber');

  const {
    cart_items,
    shipping_address,
    payment_info,
    order_id,
    order_notes,
    getSubtotal,
    getIVA,
    getShipping,
    getTotal,
    clearCart
  } = useCheckoutStore();

  const [emailSent, setEmailSent] = useState(false);

  useEffect(() => {
    // Clear cart after successful order confirmation
    if (order_id || orderNumber) {
      clearCart();

      // Simulate email confirmation sent
      setTimeout(() => {
        setEmailSent(true);
      }, 1000);
    }

    // If no order data, redirect to home
    if (!order_id && !orderNumber && cart_items.length === 0) {
      navigate('/');
    }
  }, [order_id, orderNumber, cart_items.length, navigate, clearCart]);

  const handlePrintReceipt = () => {
    window.print();
  };

  const handleViewOrders = () => {
    navigate('/app/mis-compras');
  };

  const handleContinueShopping = () => {
    navigate('/marketplace');
  };

  // Format order number for display
  const displayOrderNumber = orderNumber || order_id || 'N/A';
  const estimatedDeliveryDate = new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toLocaleDateString('es-CO', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  // Get payment method display name
  const getPaymentMethodName = () => {
    if (!payment_info) return 'Método de pago';

    switch (payment_info.method) {
      case 'pse':
        return 'PSE - Pago Seguro en Línea';
      case 'credit_card':
        return 'Tarjeta de Crédito/Débito';
      case 'bank_transfer':
        return 'Transferencia Bancaria';
      case 'cash_on_delivery':
        return 'Pago Contraentrega';
      default:
        return 'Método de pago';
    }
  };

  return (
    <div className="confirmation-page min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Success Header */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-6 text-center">
          <div className="success-icon mb-4">
            <CheckCircle className="h-20 w-20 text-green-500 mx-auto animate-bounce" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            ¡Pago Exitoso!
          </h1>
          <p className="text-gray-600 mb-4">
            Tu pedido ha sido confirmado y está siendo procesado
          </p>
          <div className="order-number-box bg-blue-50 border-2 border-blue-200 rounded-lg p-4 inline-block">
            <p className="text-sm text-gray-600 mb-1">Número de Orden</p>
            <p className="text-2xl font-bold text-blue-600">#{displayOrderNumber}</p>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Order Items & Delivery Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Order Items */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <ShoppingBag className="h-5 w-5 mr-2 text-blue-600" />
                Productos Ordenados
              </h2>
              <div className="space-y-4">
                {cart_items.length > 0 ? (
                  cart_items.map((item) => (
                    <div key={item.id} className="flex items-center border-b pb-4 last:border-b-0">
                      {item.image_url && (
                        <img
                          src={item.image_url}
                          alt={item.name}
                          className="w-16 h-16 object-cover rounded mr-4 bg-gray-100"
                          onError={(e) => {
                            (e.target as HTMLImageElement).src = 'https://via.placeholder.com/64?text=Producto';
                          }}
                        />
                      )}
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900">{item.name}</h3>
                        <p className="text-sm text-gray-600">Cantidad: {item.quantity}</p>
                        {item.sku && (
                          <p className="text-xs text-gray-500">SKU: {item.sku}</p>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-gray-900">{formatCOP(item.price * item.quantity)}</p>
                        <p className="text-sm text-gray-600">{formatCOP(item.price)} c/u</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <Package className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-gray-500">Información del pedido confirmada</p>
                  </div>
                )}
              </div>
            </div>

            {/* Delivery Information */}
            {shipping_address && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4 flex items-center">
                  <Truck className="h-5 w-5 mr-2 text-blue-600" />
                  Información de Envío
                </h2>
                <div className="space-y-3">
                  <div className="flex items-start">
                    <MapPin className="h-5 w-5 text-gray-400 mr-3 mt-0.5" />
                    <div>
                      <p className="font-semibold text-gray-900">{shipping_address.name}</p>
                      <p className="text-gray-600">{shipping_address.address}</p>
                      <p className="text-gray-600">
                        {shipping_address.city}
                        {shipping_address.department && `, ${shipping_address.department}`}
                      </p>
                      {shipping_address.postal_code && (
                        <p className="text-gray-600">CP: {shipping_address.postal_code}</p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center">
                    <Phone className="h-5 w-5 text-gray-400 mr-3" />
                    <p className="text-gray-600">{shipping_address.phone}</p>
                  </div>

                  {shipping_address.additional_info && (
                    <div className="mt-3 p-3 bg-gray-50 rounded">
                      <p className="text-sm text-gray-600">
                        <strong>Información adicional:</strong> {shipping_address.additional_info}
                      </p>
                    </div>
                  )}

                  <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                    <div className="flex items-center text-blue-800">
                      <Clock className="h-5 w-5 mr-2" />
                      <div>
                        <p className="font-semibold">Entrega Estimada</p>
                        <p className="text-sm">{estimatedDeliveryDate}</p>
                        <p className="text-xs mt-1 text-blue-600">3-5 días hábiles</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Order Notes */}
            {order_notes && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="font-semibold text-gray-900 mb-2">Notas del Pedido</h3>
                <p className="text-gray-600">{order_notes}</p>
              </div>
            )}
          </div>

          {/* Right Column - Order Summary & Actions */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6 sticky top-4 space-y-6">
              <h2 className="text-xl font-semibold">Resumen del Pedido</h2>

              {/* Cost Breakdown */}
              <div className="space-y-3">
                <div className="flex justify-between text-gray-600">
                  <span>Subtotal</span>
                  <span>{formatCOP(getSubtotal())}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>IVA (19%)</span>
                  <span>{formatCOP(getIVA())}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Envío</span>
                  <span>{getShipping() === 0 ? 'GRATIS' : formatCOP(getShipping())}</span>
                </div>
                <div className="border-t pt-3">
                  <div className="flex justify-between text-lg font-bold">
                    <span>Total Pagado</span>
                    <span className="text-green-600">{formatCOP(getTotal())}</span>
                  </div>
                </div>
              </div>

              {/* Payment Status */}
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center mb-2">
                  <CheckCircle className="h-5 w-5 text-green-600 mr-2 flex-shrink-0" />
                  <span className="font-semibold text-green-800">Pago Confirmado</span>
                </div>
                <div className="flex items-start ml-7">
                  <CreditCard className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-green-700">
                    {getPaymentMethodName()}
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-3">
                <button
                  onClick={handlePrintReceipt}
                  className="no-print w-full py-2 px-4 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center justify-center transition-colors"
                >
                  <Printer className="h-5 w-5 mr-2" />
                  Imprimir Recibo
                </button>

                <button
                  onClick={handleViewOrders}
                  className="no-print w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center transition-colors"
                >
                  <Package className="h-5 w-5 mr-2" />
                  Ver Mis Pedidos
                </button>

                <button
                  onClick={handleContinueShopping}
                  className="no-print w-full py-2 px-4 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Seguir Comprando
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Email Confirmation Notice */}
        {emailSent && shipping_address && (
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mt-6 rounded">
            <div className="flex">
              <Mail className="h-5 w-5 text-blue-500 mr-3 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-blue-900">Confirmación Enviada</h3>
                <p className="text-sm text-blue-800 mt-1">
                  Hemos enviado un correo de confirmación con los detalles de tu pedido.
                  Revisa tu bandeja de entrada y carpeta de spam.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Print Styles */}
        <style>
          {`
            @media print {
              .no-print {
                display: none !important;
              }
              .confirmation-page {
                background: white !important;
              }
              .shadow, .shadow-lg {
                box-shadow: none !important;
              }
            }
          `}
        </style>
      </div>
    </div>
  );
};

export default ConfirmationPage;
