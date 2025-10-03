import React, { useState, useEffect } from 'react';
import { CreditCard, Building2, Loader, AlertCircle, Shield, CheckCircle } from 'lucide-react';

interface PayUCheckoutProps {
  orderId: string;
  amount: number;
  customerEmail: string;
  customerName: string;
  customerPhone: string;
  onSuccess?: (transactionId: string) => void;
  onError?: (error: string) => void;
}

interface PSEBank {
  code: string;
  name: string;
}

// List of Colombian banks for PSE
const PSE_BANKS: PSEBank[] = [
  { code: '1007', name: 'Bancolombia' },
  { code: '1051', name: 'Davivienda' },
  { code: '1001', name: 'Banco de Bogotá' },
  { code: '1023', name: 'Banco de Occidente' },
  { code: '1062', name: 'Banco Falabella' },
  { code: '1012', name: 'Banco GNB Sudameris' },
  { code: '1060', name: 'Banco Pichincha' },
  { code: '1002', name: 'Banco Popular' },
  { code: '1058', name: 'Banco Procredit' },
  { code: '1065', name: 'Banco Santander' },
  { code: '1066', name: 'Banco Cooperativo Coopcentral' },
  { code: '1006', name: 'Banco Corpbanca (Itaú)' },
  { code: '1013', name: 'BBVA Colombia' },
  { code: '1009', name: 'Citibank' },
  { code: '1014', name: 'Itaú' },
  { code: '1019', name: 'Scotiabank Colpatria' },
  { code: '1040', name: 'Banco Agrario' },
  { code: '1052', name: 'Banco AV Villas' },
  { code: '1032', name: 'Banco Caja Social' },
  { code: '1022', name: 'Banco Finandina' },
  { code: '1292', name: 'Confiar' },
  { code: '1283', name: 'CFA Cooperativa Financiera' },
  { code: '1289', name: 'Cotrafa' },
  { code: '1370', name: 'Coltefinanciera' }
];

export const PayUCheckout: React.FC<PayUCheckoutProps> = ({
  orderId,
  amount,
  customerEmail,
  customerName,
  customerPhone,
  onSuccess,
  onError
}) => {
  const [paymentMethod, setPaymentMethod] = useState<'CREDIT_CARD' | 'PSE'>('CREDIT_CARD');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Credit card state
  const [cardNumber, setCardNumber] = useState('');
  const [cardHolder, setCardHolder] = useState(customerName);
  const [expiryDate, setExpiryDate] = useState('');
  const [cvv, setCvv] = useState('');
  const [installments, setInstallments] = useState(1);

  // PSE state
  const [pseBank, setPseBank] = useState('');
  const [pseUserType, setPseUserType] = useState<'N' | 'J'>('N');
  const [pseIdType, setPseIdType] = useState('CC');
  const [pseIdNumber, setPseIdNumber] = useState('');

  useEffect(() => {
    setCardHolder(customerName);
  }, [customerName]);

  // Format card number with spaces
  const handleCardNumberChange = (value: string) => {
    const cleaned = value.replace(/\s/g, '');
    const formatted = cleaned.replace(/(\d{4})/g, '$1 ').trim();
    setCardNumber(formatted.substring(0, 19)); // Max 16 digits + 3 spaces
  };

  // Format expiry date as MM/YY
  const handleExpiryDateChange = (value: string) => {
    const cleaned = value.replace(/\D/g, '');
    if (cleaned.length >= 2) {
      setExpiryDate(`${cleaned.substring(0, 2)}/${cleaned.substring(2, 4)}`);
    } else {
      setExpiryDate(cleaned);
    }
  };

  // Validate credit card form
  const validateCreditCard = (): boolean => {
    if (cardNumber.replace(/\s/g, '').length !== 16) {
      setError('Número de tarjeta debe tener 16 dígitos');
      return false;
    }
    if (!cardHolder.trim()) {
      setError('Nombre del titular es requerido');
      return false;
    }
    if (!/^\d{2}\/\d{2}$/.test(expiryDate)) {
      setError('Fecha de vencimiento inválida (MM/YY)');
      return false;
    }
    if (cvv.length < 3 || cvv.length > 4) {
      setError('CVV debe tener 3 o 4 dígitos');
      return false;
    }
    return true;
  };

  // Validate PSE form
  const validatePSE = (): boolean => {
    if (!pseBank) {
      setError('Selecciona tu banco');
      return false;
    }
    if (!pseIdNumber.trim()) {
      setError('Número de identificación es requerido');
      return false;
    }
    return true;
  };

  const handlePayment = async () => {
    setIsProcessing(true);
    setError(null);

    try {
      // Validate form based on payment method
      if (paymentMethod === 'CREDIT_CARD') {
        if (!validateCreditCard()) {
          setIsProcessing(false);
          return;
        }
      } else if (paymentMethod === 'PSE') {
        if (!validatePSE()) {
          setIsProcessing(false);
          return;
        }
      }

      const paymentData: any = {
        order_id: orderId,
        amount,
        currency: 'COP',
        payment_method: paymentMethod,
        payer_email: customerEmail,
        payer_full_name: customerName,
        payer_phone: customerPhone,
        response_url: `${window.location.origin}/payment-result`
      };

      if (paymentMethod === 'CREDIT_CARD') {
        // Convert expiry date from MM/YY to MM/YYYY
        const [month, year] = expiryDate.split('/');
        const fullYear = `20${year}`;

        paymentData.card_number = cardNumber.replace(/\s/g, '');
        paymentData.card_holder_name = cardHolder;
        paymentData.card_expiration_date = `${month}/${fullYear}`;
        paymentData.card_security_code = cvv;
        paymentData.installments = installments;
      } else if (paymentMethod === 'PSE') {
        paymentData.pse_bank_code = pseBank;
        paymentData.pse_user_type = pseUserType;
        paymentData.pse_identification_type = pseIdType;
        paymentData.pse_identification_number = pseIdNumber;
      }

      // Get auth token
      const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');

      const response = await fetch('http://192.168.1.137:8000/api/v1/payments/process/payu', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(paymentData)
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || result.message || 'Error al procesar el pago');
      }

      if (result.payment_url) {
        // For PSE, redirect to bank portal
        window.location.href = result.payment_url;
      } else if (result.success) {
        onSuccess?.(result.transaction_id);
      } else {
        throw new Error(result.message || 'Pago rechazado');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error al procesar el pago';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-6">
        <Shield className="text-green-600 mr-2" size={24} />
        <h3 className="text-lg font-semibold">Pago Seguro con PayU</h3>
      </div>

      {/* Method selector */}
      <div className="mb-6 grid grid-cols-2 gap-4">
        <button
          onClick={() => setPaymentMethod('CREDIT_CARD')}
          className={`p-4 rounded-lg border-2 transition-all ${
            paymentMethod === 'CREDIT_CARD'
              ? 'border-blue-500 bg-blue-50 shadow-md'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <CreditCard className="mx-auto mb-2 text-blue-600" size={32} />
          <div className="font-medium">Tarjeta</div>
          <div className="text-xs text-gray-600">Crédito/Débito</div>
        </button>
        <button
          onClick={() => setPaymentMethod('PSE')}
          className={`p-4 rounded-lg border-2 transition-all ${
            paymentMethod === 'PSE'
              ? 'border-blue-500 bg-blue-50 shadow-md'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <Building2 className="mx-auto mb-2 text-green-600" size={32} />
          <div className="font-medium">PSE</div>
          <div className="text-xs text-gray-600">Pago en Línea</div>
        </button>
      </div>

      {/* Credit card form */}
      {paymentMethod === 'CREDIT_CARD' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Número de Tarjeta
            </label>
            <input
              type="text"
              placeholder="1234 5678 9012 3456"
              value={cardNumber}
              onChange={(e) => handleCardNumberChange(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              maxLength={19}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nombre del Titular
            </label>
            <input
              type="text"
              placeholder="Nombre como aparece en la tarjeta"
              value={cardHolder}
              onChange={(e) => setCardHolder(e.target.value.toUpperCase())}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha de Vencimiento
              </label>
              <input
                type="text"
                placeholder="MM/YY"
                value={expiryDate}
                onChange={(e) => handleExpiryDateChange(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                maxLength={5}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                CVV
              </label>
              <input
                type="text"
                placeholder="123"
                value={cvv}
                onChange={(e) => setCvv(e.target.value.replace(/\D/g, '').substring(0, 4))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                maxLength={4}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Cuotas
            </label>
            <select
              value={installments}
              onChange={(e) => setInstallments(Number(e.target.value))}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value={1}>1 cuota (Sin intereses)</option>
              <option value={3}>3 cuotas</option>
              <option value={6}>6 cuotas</option>
              <option value={12}>12 cuotas</option>
              <option value={24}>24 cuotas</option>
              <option value={36}>36 cuotas</option>
            </select>
          </div>

          <div className="bg-blue-50 p-3 rounded-lg flex items-start">
            <CheckCircle className="text-blue-600 mr-2 mt-0.5 flex-shrink-0" size={18} />
            <div className="text-sm text-blue-800">
              <strong>Seguro:</strong> Tus datos están protegidos con encriptación SSL.
            </div>
          </div>
        </div>
      )}

      {/* PSE form */}
      {paymentMethod === 'PSE' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Banco
            </label>
            <select
              value={pseBank}
              onChange={(e) => setPseBank(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Seleccionar banco</option>
              {PSE_BANKS.map((bank) => (
                <option key={bank.code} value={bank.code}>
                  {bank.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Persona
            </label>
            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setPseUserType('N')}
                className={`p-3 rounded-lg border-2 transition-all ${
                  pseUserType === 'N'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                Natural
              </button>
              <button
                type="button"
                onClick={() => setPseUserType('J')}
                className={`p-3 rounded-lg border-2 transition-all ${
                  pseUserType === 'J'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                Jurídica
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Identificación
            </label>
            <select
              value={pseIdType}
              onChange={(e) => setPseIdType(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="CC">Cédula de Ciudadanía</option>
              <option value="CE">Cédula de Extranjería</option>
              <option value="TI">Tarjeta de Identidad</option>
              <option value="NIT">NIT</option>
              <option value="PP">Pasaporte</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Número de Identificación
            </label>
            <input
              type="text"
              placeholder="Ingresa tu número de identificación"
              value={pseIdNumber}
              onChange={(e) => setPseIdNumber(e.target.value.replace(/\D/g, ''))}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="bg-green-50 p-3 rounded-lg flex items-start">
            <CheckCircle className="text-green-600 mr-2 mt-0.5 flex-shrink-0" size={18} />
            <div className="text-sm text-green-800">
              Serás redirigido al portal de tu banco para completar el pago de forma segura.
            </div>
          </div>
        </div>
      )}

      {/* Error display */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
          <AlertCircle className="text-red-600 mr-2 mt-0.5 flex-shrink-0" size={20} />
          <span className="text-red-700 text-sm">{error}</span>
        </div>
      )}

      {/* Submit button */}
      <button
        onClick={handlePayment}
        disabled={isProcessing}
        className="w-full mt-6 bg-blue-600 text-white p-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center font-semibold"
      >
        {isProcessing ? (
          <>
            <Loader className="animate-spin mr-2" size={20} />
            Procesando pago...
          </>
        ) : (
          <>
            <Shield className="mr-2" size={20} />
            Pagar ${amount.toLocaleString('es-CO')} COP
          </>
        )}
      </button>

      {/* Payment brands */}
      <div className="mt-4 text-center text-xs text-gray-500">
        Aceptamos Visa, Mastercard, American Express, Diners
      </div>
    </div>
  );
};

export default PayUCheckout;
