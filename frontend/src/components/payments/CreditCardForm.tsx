import React, { useState } from 'react';
import { CreditCard, Lock, AlertCircle } from 'lucide-react';

interface CreditCardFormProps {
  onSubmit: (cardData: CardData) => void;
  loading: boolean;
  total: number;
  publicKey?: string;
}

interface CardData {
  number: string;
  expMonth: string;
  expYear: string;
  cvc: string;
  cardHolder: string;
  installments: number;
}

const CreditCardForm: React.FC<CreditCardFormProps> = ({
  onSubmit,
  loading,
  total
}) => {
  const [formData, setFormData] = useState<CardData>({
    number: '',
    expMonth: '',
    expYear: '',
    cvc: '',
    cardHolder: '',
    installments: 1
  });

  const [errors, setErrors] = useState<Partial<CardData>>({});
  const [cardType, setCardType] = useState<string>('');

  const detectCardType = (number: string): string => {
    const cleaned = number.replace(/\s/g, '');
    
    if (/^4/.test(cleaned)) return 'visa';
    if (/^5[1-5]/.test(cleaned) || /^2[2-7]/.test(cleaned)) return 'mastercard';
    if (/^3[47]/.test(cleaned)) return 'amex';
    if (/^6/.test(cleaned)) return 'discover';
    
    return '';
  };

  const formatCardNumber = (value: string): string => {
    const cleaned = value.replace(/\D/g, '');
    const groups = cleaned.match(/.{1,4}/g);
    return groups ? groups.join(' ') : cleaned;
  };

  const validateCardNumber = (number: string): boolean => {
    const cleaned = number.replace(/\s/g, '');
    
    // Luhn algorithm
    let sum = 0;
    let alternate = false;
    
    for (let i = cleaned.length - 1; i >= 0; i--) {
      let n = parseInt(cleaned.charAt(i), 10);
      
      if (alternate) {
        n *= 2;
        if (n > 9) n = (n % 10) + 1;
      }
      
      sum += n;
      alternate = !alternate;
    }
    
    return sum % 10 === 0 && cleaned.length >= 13 && cleaned.length <= 19;
  };

  const handleInputChange = (field: keyof CardData, value: string) => {
    let processedValue = value;
    
    if (field === 'number') {
      processedValue = formatCardNumber(value);
      const type = detectCardType(value);
      setCardType(type);
    }
    
    if (field === 'cardHolder') {
      processedValue = value.toUpperCase();
    }
    
    if (field === 'expMonth' || field === 'expYear') {
      processedValue = value.replace(/\D/g, '');
    }
    
    if (field === 'cvc') {
      processedValue = value.replace(/\D/g, '').substring(0, 4);
    }

    setFormData(prev => ({
      ...prev,
      [field]: processedValue
    }));

    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<CardData> = {};

    // Card number validation
    if (!formData.number) {
      newErrors.number = 'Número de tarjeta es requerido';
    } else if (!validateCardNumber(formData.number)) {
      newErrors.number = 'Número de tarjeta inválido';
    }

    // Expiration month
    if (!formData.expMonth) {
      newErrors.expMonth = 'Mes es requerido';
    } else {
      const month = parseInt(formData.expMonth);
      if (month < 1 || month > 12) {
        newErrors.expMonth = 'Mes inválido';
      }
    }

    // Expiration year
    if (!formData.expYear) {
      newErrors.expYear = 'Año es requerido';
    } else {
      const currentYear = new Date().getFullYear();
      const year = parseInt(formData.expYear);
      if (year < currentYear || year > currentYear + 20) {
        newErrors.expYear = 'Año inválido';
      }
    }

    // CVC
    if (!formData.cvc) {
      newErrors.cvc = 'CVC es requerido';
    } else if (formData.cvc.length < 3) {
      newErrors.cvc = 'CVC debe tener al menos 3 dígitos';
    }

    // Cardholder name
    if (!formData.cardHolder.trim()) {
      newErrors.cardHolder = 'Nombre del titular es requerido';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    // Clean card number for submission
    const cleanedData = {
      ...formData,
      number: formData.number.replace(/\s/g, '')
    };

    onSubmit(cleanedData);
  };

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 21 }, (_, i) => currentYear + i);

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900 flex items-center">
        <CreditCard className="w-5 h-5 mr-2" />
        Información de la tarjeta
      </h3>

      {/* Card Number */}
      <div>
        <label htmlFor="cardNumber" className="block text-sm font-medium text-gray-700 mb-2">
          Número de tarjeta
        </label>
        <div className="relative">
          <input
            id="cardNumber"
            type="text"
            value={formData.number}
            onChange={(e) => handleInputChange('number', e.target.value)}
            placeholder="1234 5678 9012 3456"
            className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              errors.number ? 'border-red-500' : 'border-gray-300'
            }`}
            maxLength={19}
          />
          {cardType && (
            <div className="absolute right-3 top-3">
              <img
                src={`/images/cards/${cardType}.svg`}
                alt={cardType}
                className="w-8 h-5"
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                }}
              />
            </div>
          )}
        </div>
        {errors.number && (
          <p className="mt-1 text-sm text-red-600 flex items-center">
            <AlertCircle className="w-4 h-4 mr-1" />
            {errors.number}
          </p>
        )}
      </div>

      {/* Expiration and CVC */}
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label htmlFor="expMonth" className="block text-sm font-medium text-gray-700 mb-2">
            Mes
          </label>
          <select
            id="expMonth"
            value={formData.expMonth}
            onChange={(e) => handleInputChange('expMonth', e.target.value)}
            className={`w-full px-3 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              errors.expMonth ? 'border-red-500' : 'border-gray-300'
            }`}
          >
            <option value="">MM</option>
            {Array.from({ length: 12 }, (_, i) => i + 1).map(month => (
              <option key={month} value={month.toString().padStart(2, '0')}>
                {month.toString().padStart(2, '0')}
              </option>
            ))}
          </select>
          {errors.expMonth && (
            <p className="mt-1 text-xs text-red-600">{errors.expMonth}</p>
          )}
        </div>

        <div>
          <label htmlFor="expYear" className="block text-sm font-medium text-gray-700 mb-2">
            Año
          </label>
          <select
            id="expYear"
            value={formData.expYear}
            onChange={(e) => handleInputChange('expYear', e.target.value)}
            className={`w-full px-3 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              errors.expYear ? 'border-red-500' : 'border-gray-300'
            }`}
          >
            <option value="">YYYY</option>
            {years.map(year => (
              <option key={year} value={year.toString()}>
                {year}
              </option>
            ))}
          </select>
          {errors.expYear && (
            <p className="mt-1 text-xs text-red-600">{errors.expYear}</p>
          )}
        </div>

        <div>
          <label htmlFor="cvc" className="block text-sm font-medium text-gray-700 mb-2">
            CVC
          </label>
          <input
            id="cvc"
            type="text"
            value={formData.cvc}
            onChange={(e) => handleInputChange('cvc', e.target.value)}
            placeholder="123"
            className={`w-full px-3 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              errors.cvc ? 'border-red-500' : 'border-gray-300'
            }`}
            maxLength={4}
          />
          {errors.cvc && (
            <p className="mt-1 text-xs text-red-600">{errors.cvc}</p>
          )}
        </div>
      </div>

      {/* Cardholder Name */}
      <div>
        <label htmlFor="cardHolder" className="block text-sm font-medium text-gray-700 mb-2">
          Nombre del titular (como aparece en la tarjeta)
        </label>
        <input
          id="cardHolder"
          type="text"
          value={formData.cardHolder}
          onChange={(e) => handleInputChange('cardHolder', e.target.value)}
          placeholder="JUAN CARLOS MARTINEZ"
          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
            errors.cardHolder ? 'border-red-500' : 'border-gray-300'
          }`}
        />
        {errors.cardHolder && (
          <p className="mt-1 text-sm text-red-600 flex items-center">
            <AlertCircle className="w-4 h-4 mr-1" />
            {errors.cardHolder}
          </p>
        )}
      </div>

      {/* Installments */}
      <div>
        <label htmlFor="installments" className="block text-sm font-medium text-gray-700 mb-2">
          Número de cuotas
        </label>
        <select
          id="installments"
          value={formData.installments}
          onChange={(e) => setFormData(prev => ({ ...prev, installments: parseInt(e.target.value) }))}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value={1}>1 cuota - ${total.toLocaleString()}</option>
          <option value={3}>3 cuotas - ${(total / 3).toLocaleString()} c/u</option>
          <option value={6}>6 cuotas - ${(total / 6).toLocaleString()} c/u</option>
          <option value={12}>12 cuotas - ${(total / 12).toLocaleString()} c/u</option>
        </select>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
      >
        {loading ? (
          <>
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
            Procesando...
          </>
        ) : (
          <>
            <Lock className="w-5 h-5 mr-2" />
            Pagar ${total.toLocaleString()}
          </>
        )}
      </button>

      {/* Security Notice */}
      <div className="text-xs text-gray-500 text-center">
        <Lock className="w-4 h-4 inline mr-1" />
        Tu información está protegida con encriptación SSL de 256 bits
      </div>
    </form>
  );
};

export default CreditCardForm;