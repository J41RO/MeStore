import React, { useState, useEffect } from 'react';
import { useCheckoutStore } from '../../../stores/checkoutStore';
import { useAuthStore } from '../../../stores/authStore';
import { orderService } from '../../../services/orderService';
import { paymentService, PaymentRequest } from '../../../services/paymentService';
import { usePaymentNotifications } from '../../notifications/PaymentNotifications';
import { CreateOrderRequest } from '../../../types/orders';

const ConfirmationStep: React.FC = () => {
  const {
    cart_items,
    shipping_address,
    shipping_cost,
    payment_info,
    order_notes,
    order_id,
    setOrderId,
    getTotalWithShipping,
    goToPreviousStep,
    setError,
    setProcessing,
    is_processing,
    resetCheckout,
    clearCart,
    getSubtotal,
    getIVA,
    getShipping,
    getTotal
  } = useCheckoutStore();

  const { user } = useAuthStore();
  const [isPlacingOrder, setIsPlacingOrder] = useState(false);
  const [orderConfirmed, setOrderConfirmed] = useState(false);
  const { notifyPaymentProcessing, notifyPaymentSuccess, notifyPaymentError } = usePaymentNotifications();

  useEffect(() => {
    // If we already have an order ID, the order has been placed
    if (order_id) {
      setOrderConfirmed(true);
    }
  }, [order_id]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const calculateTotals = () => {
    // Use store methods for consistent calculations (same as Cart and CheckoutSummary)
    const subtotal = getSubtotal();
    const tax = getIVA();
    const shipping = getShipping(); // Always calculate based on subtotal, not shipping_cost state
    const total = getTotal(); // subtotal + IVA + shipping

    return { subtotal, tax, shipping, total };
  };

  const handlePlaceOrder = async () => {
    if (!shipping_address || !payment_info || cart_items.length === 0) {
      setError('Información incompleta. Por favor revisa todos los pasos.');
      return;
    }

    setIsPlacingOrder(true);
    setProcessing(true);

    try {
      // Prepare order data
      const orderData: CreateOrderRequest = {
        items: cart_items.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity,
          variant_attributes: item.variant_attributes
        })),
        shipping_name: shipping_address.name,
        shipping_address: shipping_address.address,
        shipping_city: shipping_address.city,
        shipping_phone: shipping_address.phone,
        notes: order_notes
      };

      // Create the order
      const orderResponse = await orderService.createOrder(orderData);

      if (orderResponse.success && orderResponse.data) {
        const order = orderResponse.data;
        setOrderId(order.id);

        // Process payment based on method
        if (payment_info.method === 'pse' || payment_info.method === 'credit_card') {
          // For PSE and credit card, redirect to payment gateway
          await processPayment(order.id);
        } else {
          // For bank transfer and cash on delivery, order is confirmed
          setOrderConfirmed(true);
          clearCart(); // Clear cart after successful order
        }
      } else {
        throw new Error(orderResponse.message || 'Error creando la orden');
      }
    } catch (error) {
      console.error('Error placing order:', error);
      setError(error instanceof Error ? error.message : 'Error procesando el pedido');
    } finally {
      setIsPlacingOrder(false);
      setProcessing(false);
    }
  };

  const processPayment = async (orderId: string) => {
    try {
      // Show processing notification
      const notificationId = notifyPaymentProcessing(orderId, getTotalWithShipping());

      // Prepare payment data based on method
      let paymentData: any = {
        redirect_url: `${window.location.origin}/orders/${orderId}/payment-result`
      };

      if (payment_info.method === 'pse') {
        paymentData = {
          ...paymentData,
          user_type: payment_info.user_type,
          user_legal_id: payment_info.identification_number,
          financial_institution_code: payment_info.bank_code,
          payment_description: `Pago orden #${orderId}`
        };
      } else if (payment_info.method === 'credit_card') {
        paymentData = {
          ...paymentData,
          card_number: payment_info.card_number,
          card_holder: payment_info.card_holder_name,
          expiration_month: payment_info.expiry_month,
          expiration_year: payment_info.expiry_year,
          cvv: payment_info.cvv,
          installments: 1
        };
      }

      // Use the payment service
      const paymentRequest: PaymentRequest = {
        order_id: parseInt(orderId),
        payment_method: payment_info.method,
        payment_data: paymentData,
        save_payment_method: false
      };

      const result = await paymentService.processPayment(paymentRequest);

      if (result.payment_url && (payment_info.method === 'pse' || payment_info.method === 'credit_card')) {
        // Redirect to payment gateway
        window.location.href = result.payment_url;
      } else if (result.success) {
        notifyPaymentSuccess(orderId, getTotalWithShipping(), result.transaction_id);
        setOrderConfirmed(true);
        clearCart();
      } else {
        throw new Error(result.message || 'Error en el procesamiento del pago');
      }
    } catch (error) {
      console.error('Error processing payment:', error);
      const errorMessage = error instanceof Error ? error.message : 'Error procesando el pago';
      notifyPaymentError(orderId, errorMessage);
      setError(errorMessage);
    }
  };

  const handleStartNewOrder = () => {
    resetCheckout();
    window.location.href = '/products';
  };

  const handleViewOrder = () => {
    if (order_id) {
      window.location.href = `/orders/${order_id}`;
    }
  };

  const { subtotal, tax, shipping, total } = calculateTotals();

  // Order confirmed view
  if (orderConfirmed) {
    return (
      <div className="p-6 text-center">
        <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-6">
          <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>

        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          ¡Pedido Confirmado!
        </h2>

        <p className="text-gray-600 mb-6">
          Tu pedido ha sido procesado exitosamente.
          {order_id && (
            <>
              <br />
              <span className="font-medium">Número de pedido: #{order_id}</span>
            </>
          )}
        </p>

        <div className="bg-gray-50 rounded-lg p-6 mb-6 text-left max-w-md mx-auto">
          <h3 className="font-medium text-gray-900 mb-3">Detalles de entrega:</h3>
          <div className="space-y-1 text-sm text-gray-600">
            <p><span className="font-medium">Para:</span> {shipping_address?.name}</p>
            <p><span className="font-medium">Dirección:</span> {shipping_address?.address}</p>
            <p><span className="font-medium">Ciudad:</span> {shipping_address?.city}</p>
            <p><span className="font-medium">Teléfono:</span> {shipping_address?.phone}</p>
          </div>
        </div>

        <div className="bg-blue-50 rounded-lg p-4 mb-6 text-sm">
          {payment_info?.method === 'bank_transfer' && (
            <p className="text-blue-800">
              Hemos enviado las instrucciones de transferencia bancaria a tu correo electrónico.
              El pedido será procesado una vez confirmemos el pago.
            </p>
          )}
          {payment_info?.method === 'cash_on_delivery' && (
            <p className="text-blue-800">
              Tu pedido será enviado y podrás pagar en efectivo al momento de la entrega.
              Tiempo estimado de entrega: 3-5 días hábiles.
            </p>
          )}
          {(payment_info?.method === 'pse' || payment_info?.method === 'credit_card') && (
            <p className="text-blue-800">
              Tu pago ha sido procesado. Recibirás un correo de confirmación en breve.
              Tiempo estimado de entrega: 3-5 días hábiles.
            </p>
          )}
        </div>

        <div className="space-y-3">
          <button
            onClick={handleViewOrder}
            className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md font-medium transition-colors"
          >
            Ver Detalles del Pedido
          </button>

          <br />

          <button
            onClick={handleStartNewOrder}
            className="w-full sm:w-auto text-blue-600 hover:text-blue-800 font-medium"
          >
            Realizar Nuevo Pedido
          </button>
        </div>
      </div>
    );
  }

  // Order confirmation view
  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Confirmar Pedido
        </h2>
        <p className="text-gray-600">
          Revisa tu pedido antes de confirmar la compra
        </p>
      </div>

      {/* Order Summary */}
      <div className="space-y-6 mb-8">
        {/* Items */}
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-4">
            Productos ({cart_items.length} artículos)
          </h3>

          <div className="space-y-3">
            {cart_items.map((item) => (
              <div key={item.id} className="flex items-center space-x-3">
                {item.image_url && (
                  <img
                    src={item.image_url}
                    alt={item.name}
                    className="w-12 h-12 object-cover rounded bg-gray-100"
                  />
                )}

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{item.name}</p>
                  {item.variant_attributes && Object.keys(item.variant_attributes).length > 0 && (
                    <p className="text-xs text-gray-500">
                      {Object.entries(item.variant_attributes).map(([key, value]) => (
                        `${key}: ${value}`
                      )).join(', ')}
                    </p>
                  )}
                  <p className="text-xs text-gray-500">Cantidad: {item.quantity}</p>
                </div>

                <div className="text-sm font-medium text-gray-900">
                  {formatCurrency(item.price * item.quantity)}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Shipping Address */}
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-3">Dirección de Envío</h3>
          <div className="text-sm space-y-1 text-gray-600">
            <p className="font-medium text-gray-900">{shipping_address?.name}</p>
            <p>{shipping_address?.address}</p>
            <p>{shipping_address?.city}</p>
            <p>{shipping_address?.phone}</p>
          </div>
        </div>

        {/* Payment Method */}
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-3">Método de Pago</h3>
          <div className="text-sm text-gray-600">
            {payment_info?.method === 'pse' && (
              <div>
                <p className="font-medium">PSE - Pago Seguro en Línea</p>
                <p>{payment_info.bank_name}</p>
              </div>
            )}

            {payment_info?.method === 'credit_card' && (
              <div>
                <p className="font-medium">Tarjeta de Crédito</p>
                <p>**** **** **** {payment_info.card_number?.slice(-4)}</p>
              </div>
            )}

            {payment_info?.method === 'bank_transfer' && (
              <p className="font-medium">Transferencia Bancaria</p>
            )}

            {payment_info?.method === 'cash_on_delivery' && (
              <p className="font-medium">Pago Contraentrega</p>
            )}
          </div>
        </div>

        {/* Order Notes */}
        {order_notes && (
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-3">Notas del Pedido</h3>
            <p className="text-sm text-gray-600">{order_notes}</p>
          </div>
        )}
      </div>

      {/* Order Totals */}
      <div className="border-t border-gray-200 pt-6 mb-8">
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Subtotal</span>
            <span>{formatCurrency(subtotal)}</span>
          </div>

          <div className="flex justify-between">
            <span className="text-gray-600">IVA (19%)</span>
            <span>{formatCurrency(tax)}</span>
          </div>

          <div className="flex justify-between">
            <span className="text-gray-600">Envío</span>
            <span className={shipping === 0 ? 'text-green-600 font-semibold' : ''}>
              {shipping === 0 ? 'GRATIS' : formatCurrency(shipping)}
            </span>
          </div>

          <div className="flex justify-between text-lg font-semibold border-t pt-2">
            <span>Total</span>
            <span>{formatCurrency(total)}</span>
          </div>
        </div>
      </div>

      {/* Terms and Conditions */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg text-sm text-gray-600">
        <p>
          Al confirmar tu pedido, aceptas nuestros{' '}
          <a href="/terms" className="text-blue-600 hover:text-blue-800">
            términos y condiciones
          </a>{' '}
          y nuestra{' '}
          <a href="/privacy" className="text-blue-600 hover:text-blue-800">
            política de privacidad
          </a>.
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-between items-center pt-6 border-t border-gray-200">
        <button
          onClick={goToPreviousStep}
          disabled={isPlacingOrder}
          className="text-gray-600 hover:text-gray-800 font-medium disabled:opacity-50"
        >
          ← Volver al Pago
        </button>

        <button
          onClick={handlePlaceOrder}
          disabled={isPlacingOrder || is_processing}
          className={`
            px-8 py-3 rounded-md font-medium transition-colors flex items-center space-x-2
            ${isPlacingOrder || is_processing
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-green-600 hover:bg-green-700 text-white'
            }
          `}
        >
          {isPlacingOrder && (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          )}
          <span>
            {isPlacingOrder ? 'Procesando Pedido...' : 'Confirmar Pedido'}
          </span>
        </button>
      </div>
    </div>
  );
};

export default ConfirmationStep;