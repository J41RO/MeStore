import React, { useState, useEffect } from 'react';
import { CreditCard, Building2, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import CreditCardForm from './CreditCardForm';
import PSEForm from './PSEForm';
import { useAuthStore } from '../../stores/authStore';

interface PaymentMethodsProps {
  order: {
    id: number;
    order_number: string;
    total_amount: number;
  };
  shippingData: {
    name: string;
    phone: string;
    email: string;
    address: string;
    city: string;
    state: string;
  };
  onSuccess: (transactionData: any) => void;
  onError: (error: string) => void;
  loading: boolean;
  setLoading: (loading: boolean) => void;
}

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

const PaymentMethods: React.FC<PaymentMethodsProps> = ({
  order,
  shippingData,
  onSuccess,
  onError,
  loading,
  setLoading
}) => {
  const { user } = useAuthStore();
  const [selectedMethod, setSelectedMethod] = useState<'card' | 'pse'>('card');
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethods | null>(null);
  const [loadingMethods, setLoadingMethods] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPaymentMethods();
  }, []);

  const loadPaymentMethods = async () => {
    try {
      setLoadingMethods(true);
      const response = await fetch('/api/v1/payments/methods', {
        headers: {
          'Authorization': `Bearer ${user?.token || localStorage.getItem('auth_token')}`,
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
      setError(error instanceof Error ? error.message : 'Error desconocido');
    } finally {
      setLoadingMethods(false);
    }
  };

  const handleCardPayment = async (cardData: any) => {
    try {
      setLoading(true);
      setError(null);

      const paymentRequest = {
        order_id: order.id,
        card_number: cardData.number,
        exp_month: cardData.expMonth,
        exp_year: cardData.expYear,
        cvc: cardData.cvc,
        card_holder: cardData.cardHolder,
        installments: cardData.installments || 1,
        customer_phone: shippingData.phone,
        redirect_url: `${window.location.origin}/orders/${order.id}/payment-result`
      };

      const response = await fetch('/api/v1/payments/card', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user?.token || localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(paymentRequest)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error procesando el pago');
      }

      const result = await response.json();
      
      if (result.checkout_url) {
        // Redirect to Wompi checkout
        window.location.href = result.checkout_url;
      } else {
        onSuccess(result);
      }
    } catch (error) {
      console.error('Error processing card payment:', error);
      onError(error instanceof Error ? error.message : 'Error procesando el pago');
    } finally {
      setLoading(false);
    }
  };

  const handlePSEPayment = async (pseData: any) => {
    try {
      setLoading(true);
      setError(null);

      const paymentRequest = {
        order_id: order.id,
        user_type: pseData.userType,
        user_legal_id: pseData.userLegalId,
        bank_code: pseData.bankCode,
        redirect_url: `${window.location.origin}/orders/${order.id}/payment-result`
      };

      const response = await fetch('/api/v1/payments/pse', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user?.token || localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(paymentRequest)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error procesando el pago PSE');
      }

      const result = await response.json();
      
      if (result.checkout_url) {
        // Redirect to PSE bank interface
        window.location.href = result.checkout_url;
      } else {
        onSuccess(result);
      }
    } catch (error) {
      console.error('Error processing PSE payment:', error);
      onError(error instanceof Error ? error.message : 'Error procesando el pago PSE');
    } finally {
      setLoading(false);
    }
  };

  if (loadingMethods) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Loader className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Cargando métodos de pago...</p>
        </div>
      </div>
    );
  }

  if (error && !paymentMethods) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center">
          <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
          <div>
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
        <button
          onClick={loadPaymentMethods}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
        >
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Método de pago</h2>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Payment Method Selection */}
      <div className="mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Credit Card Option */}
          {paymentMethods?.card_enabled && (
            <div
              onClick={() => setSelectedMethod('card')}
              className={`cursor-pointer border-2 rounded-lg p-4 transition-colors ${
                selectedMethod === 'card'
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center">
                <div className={`w-5 h-5 rounded-full border-2 mr-3 flex items-center justify-center ${
                  selectedMethod === 'card'
                    ? 'border-blue-600 bg-blue-600'
                    : 'border-gray-300'
                }`}>
                  {selectedMethod === 'card' && <div className="w-2 h-2 bg-white rounded-full" />}
                </div>
                <CreditCard className="w-6 h-6 text-gray-700 mr-3" />
                <div>
                  <h3 className="font-medium text-gray-900">Tarjeta de crédito/débito</h3>
                  <p className="text-sm text-gray-600">Visa, Mastercard, American Express</p>
                </div>
              </div>
            </div>
          )}

          {/* PSE Option */}
          {paymentMethods?.pse_enabled && (
            <div
              onClick={() => setSelectedMethod('pse')}
              className={`cursor-pointer border-2 rounded-lg p-4 transition-colors ${
                selectedMethod === 'pse'
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center">
                <div className={`w-5 h-5 rounded-full border-2 mr-3 flex items-center justify-center ${
                  selectedMethod === 'pse'
                    ? 'border-blue-600 bg-blue-600'
                    : 'border-gray-300'
                }`}>
                  {selectedMethod === 'pse' && <div className="w-2 h-2 bg-white rounded-full" />}
                </div>
                <Building2 className="w-6 h-6 text-gray-700 mr-3" />
                <div>
                  <h3 className="font-medium text-gray-900">PSE</h3>
                  <p className="text-sm text-gray-600">Pago Seguro en Línea</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Payment Forms */}
      <div className="border-t pt-8">
        {selectedMethod === 'card' && (
          <CreditCardForm
            onSubmit={handleCardPayment}
            loading={loading}
            total={order.total_amount}
            publicKey={paymentMethods?.wompi_public_key || ''}
          />
        )}

        {selectedMethod === 'pse' && paymentMethods?.pse_banks && (
          <PSEForm
            banks={paymentMethods.pse_banks}
            onSubmit={handlePSEPayment}
            loading={loading}
            total={order.total_amount}
          />
        )}
      </div>

      {/* Security Notice */}
      <div className="mt-8 bg-gray-50 rounded-lg p-4">
        <div className="flex items-start">
          <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-gray-700">
            <p className="font-medium mb-1">Pago seguro garantizado</p>
            <p>
              Tu información de pago está protegida con encriptación de nivel bancario.
              No almacenamos información de tarjetas de crédito.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PaymentMethods;