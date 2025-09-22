import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { CheckCircle, XCircle, AlertCircle, Clock, ArrowLeft, ExternalLink } from 'lucide-react';
import { paymentService, PaymentStatusResponse } from '../services/paymentService';
import { useCheckoutStore } from '../stores/checkoutStore';

const PaymentResultPage: React.FC = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const { clearCart, resetCheckout } = useCheckoutStore();

  const [paymentStatus, setPaymentStatus] = useState<PaymentStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [polling, setPolling] = useState(true);

  useEffect(() => {
    if (!orderId) {
      setError('ID de orden no válido');
      setLoading(false);
      return;
    }

    // Start polling for payment status
    startPaymentStatusPolling();

    // Clean up on unmount
    return () => {
      setPolling(false);
    };
  }, [orderId]);

  const startPaymentStatusPolling = async () => {
    if (!orderId) return;

    try {
      // Use the payment service to poll for status updates
      const finalStatus = await paymentService.pollPaymentStatus(
        parseInt(orderId),
        (status) => {
          setPaymentStatus(status);
          setLoading(false);
        },
        20, // Max 20 polls
        3000 // Poll every 3 seconds
      );

      setPaymentStatus(finalStatus);
      setPolling(false);

      // Clear cart if payment was successful
      if (finalStatus.payment_status === 'APPROVED') {
        clearCart();
      }
    } catch (error) {
      console.error('Payment status polling error:', error);
      setError('Error verificando el estado del pago');
      setPolling(false);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = () => {
    if (!paymentStatus) return <Clock className="w-16 h-16 text-yellow-500" />;

    switch (paymentStatus.payment_status) {
      case 'APPROVED':
        return <CheckCircle className="w-16 h-16 text-green-500" />;
      case 'DECLINED':
      case 'ERROR':
        return <XCircle className="w-16 h-16 text-red-500" />;
      case 'PENDING':
      case 'PROCESSING':
        return <Clock className="w-16 h-16 text-yellow-500" />;
      default:
        return <AlertCircle className="w-16 h-16 text-gray-500" />;
    }
  };

  const getStatusMessage = () => {
    if (!paymentStatus) return 'Verificando estado del pago...';

    switch (paymentStatus.payment_status) {
      case 'APPROVED':
        return '¡Pago exitoso!';
      case 'DECLINED':
        return 'Pago rechazado';
      case 'ERROR':
        return 'Error en el pago';
      case 'PENDING':
        return 'Pago pendiente';
      case 'PROCESSING':
        return 'Procesando pago...';
      default:
        return 'Estado del pago desconocido';
    }
  };

  const getStatusDescription = () => {
    if (!paymentStatus) return 'Estamos verificando el estado de tu pago. Por favor espera...';

    switch (paymentStatus.payment_status) {
      case 'APPROVED':
        return `Tu pago ha sido procesado exitosamente. Tu pedido #${orderId} está confirmado y será procesado pronto.`;
      case 'DECLINED':
        return 'Tu pago fue rechazado por el banco. Por favor verifica la información de tu tarjeta o intenta con otro método de pago.';
      case 'ERROR':
        return 'Ocurrió un error durante el procesamiento del pago. Por favor intenta nuevamente.';
      case 'PENDING':
        return 'Tu pago está siendo procesado. Recibirás una notificación cuando se complete.';
      case 'PROCESSING':
        return 'Estamos procesando tu pago. Esto puede tomar unos minutos.';
      default:
        return 'No pudimos determinar el estado de tu pago. Por favor contacta al soporte.';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const handleViewOrder = () => {
    navigate(`/orders/${orderId}`);
  };

  const handleTryAgain = () => {
    navigate(`/checkout`);
  };

  const handleGoHome = () => {
    resetCheckout();
    navigate('/');
  };

  const handleGoToOrders = () => {
    navigate('/orders');
  };

  if (loading && !paymentStatus) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full mx-4">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Verificando pago
            </h2>
            <p className="text-gray-600">
              Estamos verificando el estado de tu pago...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full mx-4">
          <div className="text-center">
            <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Error
            </h2>
            <p className="text-gray-600 mb-6">
              {error}
            </p>
            <button
              onClick={handleGoHome}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors"
            >
              Volver al inicio
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto pt-8 pb-16 px-4">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
            <button
              onClick={() => navigate(-1)}
              className="text-white hover:text-blue-200 transition-colors mb-2"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <h1 className="text-xl font-semibold text-white">
              Resultado del Pago
            </h1>
          </div>

          {/* Payment Status */}
          <div className="p-8 text-center">
            <div className="mb-6">
              {getStatusIcon()}
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {getStatusMessage()}
            </h2>

            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              {getStatusDescription()}
            </p>

            {/* Payment Details */}
            {paymentStatus && (
              <div className="bg-gray-50 rounded-lg p-6 mb-6 text-left">
                <h3 className="font-semibold text-gray-900 mb-4 text-center">
                  Detalles del Pago
                </h3>

                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Orden:</span>
                    <span className="font-medium">#{orderId}</span>
                  </div>

                  {paymentStatus.transaction_id && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Transacción:</span>
                      <span className="font-medium">{paymentStatus.transaction_id}</span>
                    </div>
                  )}

                  <div className="flex justify-between">
                    <span className="text-gray-600">Monto:</span>
                    <span className="font-medium">{formatCurrency(paymentStatus.amount)}</span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-gray-600">Estado del pedido:</span>
                    <span className="font-medium capitalize">{paymentStatus.order_status}</span>
                  </div>

                  {paymentStatus.last_updated && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Última actualización:</span>
                      <span className="font-medium">
                        {new Date(paymentStatus.last_updated).toLocaleString('es-CO')}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Real-time updates indicator */}
            {polling && paymentStatus?.payment_status === 'PENDING' && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                <div className="flex items-center justify-center space-x-2">
                  <div className="animate-pulse w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <span className="text-sm text-yellow-800">
                    Actualizando estado en tiempo real...
                  </span>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="space-y-3">
              {paymentStatus?.payment_status === 'APPROVED' && (
                <>
                  <button
                    onClick={handleViewOrder}
                    className="w-full bg-green-600 hover:bg-green-700 text-white py-3 px-4 rounded-md font-medium transition-colors flex items-center justify-center space-x-2"
                  >
                    <ExternalLink className="w-4 h-4" />
                    <span>Ver Detalles del Pedido</span>
                  </button>

                  <button
                    onClick={handleGoToOrders}
                    className="w-full text-green-600 hover:text-green-800 py-2 px-4 font-medium transition-colors"
                  >
                    Ver Mis Pedidos
                  </button>
                </>
              )}

              {(paymentStatus?.payment_status === 'DECLINED' || paymentStatus?.payment_status === 'ERROR') && (
                <>
                  <button
                    onClick={handleTryAgain}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-md font-medium transition-colors"
                  >
                    Intentar Nuevamente
                  </button>

                  <button
                    onClick={handleGoHome}
                    className="w-full text-blue-600 hover:text-blue-800 py-2 px-4 font-medium transition-colors"
                  >
                    Volver al Inicio
                  </button>
                </>
              )}

              {paymentStatus?.payment_status === 'PENDING' && (
                <button
                  onClick={handleGoHome}
                  className="w-full text-blue-600 hover:text-blue-800 py-2 px-4 font-medium transition-colors"
                >
                  Continuar Navegando
                </button>
              )}

              {!paymentStatus?.payment_status && (
                <button
                  onClick={handleGoHome}
                  className="w-full bg-gray-600 hover:bg-gray-700 text-white py-3 px-4 rounded-md font-medium transition-colors"
                >
                  Volver al Inicio
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Support Contact */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-600">
            ¿Tienes problemas con tu pago?{' '}
            <a
              href="/support"
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              Contacta nuestro soporte
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default PaymentResultPage;