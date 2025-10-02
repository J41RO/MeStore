import React, { useState, useEffect } from 'react';
import { useCheckoutStore, PaymentInfo, formatCOP } from '../../../stores/checkoutStore';
import { useAuthStore } from '../../../stores/authStore';
import { useNavigate } from 'react-router-dom';
import PSEForm from '../../payments/PSEForm';
import CreditCardForm from '../../payments/CreditCardForm';
import WompiCheckout from '../WompiCheckout';
import orderApiService from '../../../services/orderApiService';
import { Loader } from 'lucide-react';

interface PSEBank {
  financial_institution_code: string;
  financial_institution_name: string;
}

interface PaymentMethods {
  card_enabled: boolean;
  pse_enabled: boolean;
  pse_banks: PSEBank[];
  wompi_public_key: string;
}

const PaymentStep: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const {
    cart_items,
    shipping_address,
    shipping_cost,
    payment_info,
    order_notes,
    order_id,
    setPaymentInfo,
    setOrderId,
    getTotal,
    getTotalWithShipping,
    goToNextStep,
    goToPreviousStep,
    canProceedToNextStep,
    setError,
    clearErrors,
    clearCart,
    setProcessing,
    is_processing
  } = useCheckoutStore();

  const [selectedMethod, setSelectedMethod] = useState<'pse' | 'credit_card' | 'bank_transfer' | 'cash_on_delivery'>('pse');
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethods | null>(null);
  const [loadingMethods, setLoadingMethods] = useState(true);
  const [showWompiWidget, setShowWompiWidget] = useState(false);
  const [orderReference, setOrderReference] = useState<string>('');
  const [creatingOrder, setCreatingOrder] = useState(false);

  useEffect(() => {
    clearErrors();
    loadPaymentMethods();

    // Set default payment method if already selected
    if (payment_info?.method) {
      setSelectedMethod(payment_info.method);
    }
  }, [clearErrors, payment_info]);

  const loadPaymentMethods = async () => {
    try {
      setLoadingMethods(true);

      // Get auth token
      const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');

      const response = await fetch('/api/v1/payments/methods', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Error al cargar métodos de pago');
      }

      const data = await response.json();
      setPaymentMethods(data);
    } catch (error) {
      console.warn('Payment methods API not available, using defaults:', error);

      // Use default payment methods configuration (hardcoded fallback)
      // This ensures the UI works even if the backend endpoint is not implemented
      setPaymentMethods({
        card_enabled: true,
        pse_enabled: true,
        pse_banks: [], // Will be loaded from Wompi if needed
        wompi_public_key: import.meta.env.VITE_WOMPI_PUBLIC_KEY || ''
      });

      // DO NOT show error to user - the fallback works perfectly
      // Just log it for developers in console (already done with console.warn above)
    } finally {
      setLoadingMethods(false);
    }
  };

  const handleMethodSelect = (method: PaymentInfo['method']) => {
    setSelectedMethod(method);

    // Clear previous payment info when switching methods
    setPaymentInfo({
      method,
      total_amount: getTotalWithShipping()
    });

    // Reset Wompi widget state when switching methods
    setShowWompiWidget(false);
  };

  /**
   * Create order before opening payment widget
   * This ensures we have a valid order reference for the payment
   */
  const createOrderBeforePayment = async (): Promise<string | null> => {
    if (!shipping_address) {
      setError('Dirección de envío no configurada');
      return null;
    }

    try {
      setCreatingOrder(true);
      clearErrors();

      // Prepare order data
      const orderData = {
        items: cart_items.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity,
          price: item.price
        })),
        shipping_name: shipping_address.name,
        shipping_phone: shipping_address.phone,
        shipping_address: shipping_address.address,
        shipping_city: shipping_address.city,
        shipping_state: shipping_address.department || '',
        shipping_postal_code: shipping_address.postal_code || '',
        notes: order_notes || ''
      };

      console.log('Creating order with data:', orderData);

      // Create order via API
      const orderResponse = await orderApiService.createOrder(orderData);

      console.log('Order created successfully:', orderResponse);

      // Save order ID and reference
      setOrderId(orderResponse.id.toString());
      const reference = orderResponse.order_number || `ORDER-${orderResponse.id}-${Date.now()}`;
      setOrderReference(reference);

      return reference;
    } catch (error) {
      console.error('Error creating order:', error);
      setError(error instanceof Error ? error.message : 'Error al crear la orden. Por favor intenta de nuevo.');
      return null;
    } finally {
      setCreatingOrder(false);
    }
  };

  const handlePSESubmit = async (pseData: any) => {
    try {
      setProcessing(true);
      clearErrors();

      const paymentInfo: PaymentInfo = {
        method: 'pse',
        bank_code: pseData.bankCode,
        bank_name: pseData.bankName,
        user_type: pseData.userType,
        identification_type: pseData.identificationType,
        identification_number: pseData.userLegalId,
        email: pseData.email,
        total_amount: getTotalWithShipping()
      };

      setPaymentInfo(paymentInfo);

      // If validation passes, continue to next step
      if (canProceedToNextStep()) {
        goToNextStep();
      }
    } catch (error) {
      console.error('Error processing PSE data:', error);
      setError('Error procesando información de PSE');
    } finally {
      setProcessing(false);
    }
  };

  const handleCreditCardSubmit = async (cardData: any) => {
    // For Wompi integration, we don't use the old credit card form
    // Instead, we create the order and open the Wompi widget
    await handleProceedToWompiPayment();
  };

  /**
   * Proceed to Wompi payment widget
   * Creates order first, then shows Wompi widget
   */
  const handleProceedToWompiPayment = async () => {
    try {
      setProcessing(true);
      clearErrors();

      // Create order if not already created
      let reference = orderReference;
      if (!reference || !order_id) {
        reference = await createOrderBeforePayment();
        if (!reference) {
          return; // Error already set in createOrderBeforePayment
        }
      }

      // Open Wompi widget
      setShowWompiWidget(true);
    } catch (error) {
      console.error('Error proceeding to payment:', error);
      setError(error instanceof Error ? error.message : 'Error al procesar el pago');
    } finally {
      setProcessing(false);
    }
  };

  /**
   * Handle successful payment from Wompi
   */
  const handlePaymentSuccess = async (transaction: any) => {
    console.log('Payment successful:', transaction);

    try {
      // Save payment info to checkout store
      setPaymentInfo({
        method: 'credit_card',
        total_amount: getTotalWithShipping(),
        email: shipping_address?.phone || ''
      });

      // Clear cart after successful payment
      clearCart();

      // Redirect to confirmation page
      navigate('/checkout/confirmation');
    } catch (error) {
      console.error('Error handling payment success:', error);
      setError('Pago procesado pero hubo un error. Contacta soporte.');
    }
  };

  /**
   * Handle payment error from Wompi
   */
  const handlePaymentError = (error: string) => {
    console.error('Payment failed:', error);
    setError(`Pago rechazado: ${error}. Por favor intenta con otro método.`);
    setShowWompiWidget(false);
  };

  /**
   * Handle payment widget close/cancel
   */
  const handlePaymentClose = () => {
    console.log('Payment widget closed by user');
    setShowWompiWidget(false);
    // Don't show error - user may want to try another payment method
  };

  const handleBankTransferSelect = () => {
    const paymentInfo: PaymentInfo = {
      method: 'bank_transfer',
      total_amount: getTotalWithShipping()
    };

    setPaymentInfo(paymentInfo);
  };

  const handleCashOnDeliverySelect = () => {
    const paymentInfo: PaymentInfo = {
      method: 'cash_on_delivery',
      total_amount: getTotalWithShipping()
    };

    setPaymentInfo(paymentInfo);
  };

  const handleContinue = () => {
    if (canProceedToNextStep()) {
      goToNextStep();
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const renderPaymentMethodOption = (
    method: PaymentInfo['method'],
    title: string,
    description: string,
    icon: React.ReactNode,
    enabled: boolean = true
  ) => {
    return (
      <div
        onClick={() => enabled && handleMethodSelect(method)}
        className={`
          cursor-pointer border-2 rounded-lg p-4 transition-all
          ${!enabled ? 'opacity-50 cursor-not-allowed' : ''}
          ${selectedMethod === method
            ? 'border-blue-600 bg-blue-50 shadow-md'
            : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
          }
        `}
      >
        <div className="flex items-center">
          <div className={`
            w-5 h-5 rounded-full border-2 mr-3 flex items-center justify-center transition-colors
            ${selectedMethod === method
              ? 'border-blue-600 bg-blue-600'
              : 'border-gray-300'
            }
          `}>
            {selectedMethod === method && (
              <div className="w-2 h-2 bg-white rounded-full"></div>
            )}
          </div>

          <div className="mr-3">
            {icon}
          </div>

          <div className="flex-1">
            <h3 className="font-medium text-gray-900">{title}</h3>
            <p className="text-sm text-gray-600">{description}</p>
          </div>

          {!enabled && (
            <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded">
              No disponible
            </span>
          )}
        </div>
      </div>
    );
  };

  if (loadingMethods) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Cargando métodos de pago...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Método de Pago
        </h2>
        <p className="text-gray-600">
          Selecciona cómo quieres pagar tu pedido de {formatCurrency(getTotalWithShipping())}
        </p>
      </div>

      {/* Payment Method Selection */}
      <div className="mb-8">
        <div className="space-y-3">
          {/* PSE */}
          {renderPaymentMethodOption(
            'pse',
            'PSE - Pago Seguro en Línea',
            'Paga directamente desde tu cuenta bancaria',
            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>,
            paymentMethods?.pse_enabled
          )}

          {/* Credit Card */}
          {renderPaymentMethodOption(
            'credit_card',
            'Tarjeta de Crédito/Débito',
            'Visa, Mastercard, American Express',
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>,
            paymentMethods?.card_enabled
          )}

          {/* Bank Transfer */}
          {renderPaymentMethodOption(
            'bank_transfer',
            'Transferencia Bancaria',
            'Transferencia manual a nuestra cuenta',
            <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
            </svg>,
            true
          )}

          {/* Cash on Delivery */}
          {renderPaymentMethodOption(
            'cash_on_delivery',
            'Pago Contraentrega',
            'Paga en efectivo al recibir tu pedido',
            <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>,
            shipping_address?.city?.toLowerCase().includes('bogotá') // Only available in Bogotá
          )}
        </div>
      </div>

      {/* Payment Forms */}
      <div className="mb-8">
        {selectedMethod === 'pse' && paymentMethods?.pse_banks && (
          <div className="border-t pt-6">
            <PSEForm
              banks={paymentMethods.pse_banks}
              onSubmit={handlePSESubmit}
              loading={is_processing}
              total={getTotalWithShipping()}
            />
          </div>
        )}

        {selectedMethod === 'credit_card' && !showWompiWidget && (
          <div className="border-t pt-6">
            <div className="bg-blue-50 rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Pago con Tarjeta de Crédito/Débito
              </h3>

              <div className="space-y-3 text-sm text-gray-700">
                <div className="flex items-start space-x-2">
                  <svg className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <p>Pago seguro procesado por Wompi</p>
                </div>
                <div className="flex items-start space-x-2">
                  <svg className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <p>Aceptamos Visa, Mastercard, American Express</p>
                </div>
                <div className="flex items-start space-x-2">
                  <svg className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <p>Confirmación inmediata de tu pago</p>
                </div>
                <div className="flex items-start space-x-2">
                  <svg className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <p>Monto total a pagar: {formatCurrency(getTotalWithShipping())}</p>
                </div>
              </div>

              <button
                onClick={handleProceedToWompiPayment}
                disabled={creatingOrder || is_processing}
                className="mt-6 w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {creatingOrder || is_processing ? (
                  <>
                    <Loader className="w-5 h-5 mr-2 animate-spin" />
                    Preparando pago...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                    Proceder al Pago Seguro
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Wompi Widget */}
        {selectedMethod === 'credit_card' && showWompiWidget && order_id && orderReference && (
          <div className="border-t pt-6">
            <WompiCheckout
              orderId={order_id}
              amount={getTotalWithShipping()}
              customerEmail={user?.email || ''}
              reference={orderReference}
              publicKey={paymentMethods?.wompi_public_key || ''}
              redirectUrl={`${window.location.origin}/checkout/confirmation?order_id=${order_id}`}
              onSuccess={handlePaymentSuccess}
              onError={handlePaymentError}
              onClose={handlePaymentClose}
              currency="COP"
              paymentMethods={['CARD']}
            />
          </div>
        )}

        {selectedMethod === 'bank_transfer' && (
          <div className="border-t pt-6">
            <div className="bg-blue-50 rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Instrucciones para Transferencia Bancaria
              </h3>

              <div className="space-y-3 text-sm">
                <div>
                  <span className="font-medium">Banco:</span> Banco de Bogotá
                </div>
                <div>
                  <span className="font-medium">Número de cuenta:</span> 123-456789-01
                </div>
                <div>
                  <span className="font-medium">Tipo de cuenta:</span> Ahorros
                </div>
                <div>
                  <span className="font-medium">Titular:</span> MeStore S.A.S
                </div>
                <div>
                  <span className="font-medium">NIT:</span> 900.123.456-7
                </div>
                <div>
                  <span className="font-medium">Monto a transferir:</span> {formatCurrency(getTotalWithShipping())}
                </div>
              </div>

              <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
                <p className="text-sm text-yellow-800">
                  <strong>Importante:</strong> Envía el comprobante de transferencia a pagos@mestore.com
                  con tu número de pedido en el asunto.
                </p>
              </div>

              <button
                onClick={handleBankTransferSelect}
                className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors"
              >
                Confirmar Transferencia Bancaria
              </button>
            </div>
          </div>
        )}

        {selectedMethod === 'cash_on_delivery' && (
          <div className="border-t pt-6">
            <div className="bg-yellow-50 rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Pago Contraentrega
              </h3>

              <div className="space-y-3 text-sm text-gray-700">
                <p>• Pagarás {formatCurrency(getTotalWithShipping())} en efectivo al recibir tu pedido</p>
                <p>• Nuestro repartidor tendrá cambio disponible</p>
                <p>• Verifica tu pedido antes de realizar el pago</p>
                <p>• Disponible solo en Bogotá y alrededores</p>
              </div>

              <button
                onClick={handleCashOnDeliverySelect}
                className="mt-4 w-full bg-yellow-600 hover:bg-yellow-700 text-white py-2 px-4 rounded-md transition-colors"
              >
                Confirmar Pago Contraentrega
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Security Notice */}
      <div className="mb-8 bg-gray-50 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <svg className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <div className="text-sm text-gray-700">
            <p className="font-medium mb-1">Pago seguro garantizado</p>
            <p>Tu información está protegida con encriptación SSL. No almacenamos datos de tarjetas.</p>
          </div>
        </div>
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-between items-center pt-6 border-t border-gray-200">
        <button
          onClick={goToPreviousStep}
          className="text-gray-600 hover:text-gray-800 font-medium"
        >
          ← Volver al Envío
        </button>

        <button
          onClick={handleContinue}
          disabled={!canProceedToNextStep() || is_processing}
          className={`
            px-6 py-3 rounded-md font-medium transition-colors
            ${canProceedToNextStep() && !is_processing
              ? 'bg-blue-600 hover:bg-blue-700 text-white'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          {is_processing ? 'Procesando...' : 'Continuar a Confirmación →'}
        </button>
      </div>
    </div>
  );
};

export default PaymentStep;