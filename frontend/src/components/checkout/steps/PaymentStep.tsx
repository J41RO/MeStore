import React, { useState, useEffect } from 'react';
import { useCheckoutStore, PaymentInfo } from '../../../stores/checkoutStore';
import PSEForm from '../../payments/PSEForm';
import CreditCardForm from '../../payments/CreditCardForm';

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
  const {
    cart_items,
    shipping_address,
    shipping_cost,
    payment_info,
    setPaymentInfo,
    getTotalWithShipping,
    goToNextStep,
    goToPreviousStep,
    canProceedToNextStep,
    setError,
    clearErrors,
    setProcessing,
    is_processing
  } = useCheckoutStore();

  const [selectedMethod, setSelectedMethod] = useState<'pse' | 'credit_card' | 'bank_transfer' | 'cash_on_delivery'>('pse');
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethods | null>(null);
  const [loadingMethods, setLoadingMethods] = useState(true);

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
      console.error('Error loading payment methods:', error);
      setError(error instanceof Error ? error.message : 'Error cargando métodos de pago');
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
    try {
      setProcessing(true);
      clearErrors();

      const paymentInfo: PaymentInfo = {
        method: 'credit_card',
        card_number: cardData.number,
        card_holder_name: cardData.cardHolder,
        expiry_month: cardData.expMonth,
        expiry_year: cardData.expYear,
        cvv: cardData.cvc,
        email: cardData.email,
        total_amount: getTotalWithShipping()
      };

      setPaymentInfo(paymentInfo);

      // If validation passes, continue to next step
      if (canProceedToNextStep()) {
        goToNextStep();
      }
    } catch (error) {
      console.error('Error processing credit card data:', error);
      setError('Error procesando información de tarjeta');
    } finally {
      setProcessing(false);
    }
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

        {selectedMethod === 'credit_card' && (
          <div className="border-t pt-6">
            <CreditCardForm
              onSubmit={handleCreditCardSubmit}
              loading={is_processing}
              total={getTotalWithShipping()}
              publicKey={paymentMethods?.wompi_public_key || ''}
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