import React, { useState } from 'react';
import { Building2, User, AlertCircle, Lock } from 'lucide-react';

interface PSEFormProps {
  banks: Array<{
    financial_institution_code: string;
    financial_institution_name: string;
  }>;
  onSubmit: (pseData: PSEData) => void;
  loading: boolean;
  total: number;
}

interface PSEData {
  bankCode: string;
  bankName: string;
  userType: string;
  identificationType: string;
  userLegalId: string;
  email: string;
}

const PSEForm: React.FC<PSEFormProps> = ({
  banks,
  onSubmit,
  loading,
  total
}) => {
  const [formData, setFormData] = useState<PSEData>({
    bankCode: '',
    bankName: '',
    userType: '0', // 0 = natural person, 1 = juridical person
    identificationType: 'CC',
    userLegalId: '',
    email: ''
  });

  const [errors, setErrors] = useState<Partial<PSEData>>({});

  const handleInputChange = (field: keyof PSEData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
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
    const newErrors: Partial<PSEData> = {};

    // Bank selection
    if (!formData.bankCode) {
      newErrors.bankCode = 'Selecciona tu banco';
    }

    // User legal ID
    if (!formData.userLegalId.trim()) {
      newErrors.userLegalId = 'Número de documento es requerido';
    } else {
      const cleanedId = formData.userLegalId.replace(/\D/g, '');
      if (formData.userType === '0' && (cleanedId.length < 6 || cleanedId.length > 12)) {
        newErrors.userLegalId = 'Número de cédula debe tener entre 6 y 12 dígitos';
      } else if (formData.userType === '1' && (cleanedId.length < 9 || cleanedId.length > 12)) {
        newErrors.userLegalId = 'NIT debe tener entre 9 y 12 dígitos';
      }
    }

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = 'Correo electrónico es requerido';
    } else {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        newErrors.email = 'Correo electrónico inválido';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    onSubmit(formData);
  };

  const formatLegalId = (value: string, userType: string): string => {
    // Remove all non-numeric characters
    const cleaned = value.replace(/\D/g, '');
    
    if (userType === '0') {
      // Natural person - format cedula with dots
      return cleaned.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    } else {
      // Juridical person - format NIT
      if (cleaned.length > 3) {
        return cleaned.replace(/(\d{1,3})(?=(\d{3})+(?!\d))/g, '$1.');
      }
      return cleaned;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900 flex items-center">
        <Building2 className="w-5 h-5 mr-2" />
        Pago Seguro en Línea (PSE)
      </h3>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <Building2 className="h-5 w-5 text-blue-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">
              ¿Qué es PSE?
            </h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                PSE te permite pagar directamente desde tu cuenta bancaria de forma segura.
                Serás redirigido al sitio web de tu banco para autorizar la transacción.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* User Type Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Tipo de persona
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            onClick={() => handleInputChange('userType', '0')}
            className={`cursor-pointer border-2 rounded-lg p-4 transition-colors ${
              formData.userType === '0'
                ? 'border-blue-600 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center">
              <div className={`w-5 h-5 rounded-full border-2 mr-3 flex items-center justify-center ${
                formData.userType === '0'
                  ? 'border-blue-600 bg-blue-600'
                  : 'border-gray-300'
              }`}>
                {formData.userType === '0' && <div className="w-2 h-2 bg-white rounded-full" />}
              </div>
              <User className="w-5 h-5 text-gray-700 mr-2" />
              <div>
                <h3 className="font-medium text-gray-900">Persona Natural</h3>
                <p className="text-sm text-gray-600">Con cédula de ciudadanía</p>
              </div>
            </div>
          </div>

          <div
            onClick={() => handleInputChange('userType', '1')}
            className={`cursor-pointer border-2 rounded-lg p-4 transition-colors ${
              formData.userType === '1'
                ? 'border-blue-600 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center">
              <div className={`w-5 h-5 rounded-full border-2 mr-3 flex items-center justify-center ${
                formData.userType === '1'
                  ? 'border-blue-600 bg-blue-600'
                  : 'border-gray-300'
              }`}>
                {formData.userType === '1' && <div className="w-2 h-2 bg-white rounded-full" />}
              </div>
              <Building2 className="w-5 h-5 text-gray-700 mr-2" />
              <div>
                <h3 className="font-medium text-gray-900">Persona Jurídica</h3>
                <p className="text-sm text-gray-600">Con NIT</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Legal ID Input */}
      <div>
        <label htmlFor="userLegalId" className="block text-sm font-medium text-gray-700 mb-2">
          {formData.userType === '0' ? 'Número de cédula' : 'NIT'}
        </label>
        <input
          id="userLegalId"
          type="text"
          value={formData.userLegalId}
          onChange={(e) => {
            const formatted = formatLegalId(e.target.value, formData.userType);
            handleInputChange('userLegalId', formatted);
          }}
          placeholder={formData.userType === '0' ? '12.345.678' : '900.123.456-1'}
          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
            errors.userLegalId ? 'border-red-500' : 'border-gray-300'
          }`}
        />
        {errors.userLegalId && (
          <p className="mt-1 text-sm text-red-600 flex items-center">
            <AlertCircle className="w-4 h-4 mr-1" />
            {errors.userLegalId}
          </p>
        )}
      </div>

      {/* Email Input */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
          Correo electrónico
        </label>
        <input
          id="email"
          type="email"
          value={formData.email}
          onChange={(e) => handleInputChange('email', e.target.value)}
          placeholder="tu@email.com"
          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
            errors.email ? 'border-red-500' : 'border-gray-300'
          }`}
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600 flex items-center">
            <AlertCircle className="w-4 h-4 mr-1" />
            {errors.email}
          </p>
        )}
      </div>

      {/* Bank Selection */}
      <div>
        <label htmlFor="bankCode" className="block text-sm font-medium text-gray-700 mb-2">
          Selecciona tu banco
        </label>
        <select
          id="bankCode"
          value={formData.bankCode}
          onChange={(e) => {
            const selectedBank = banks.find(bank => bank.financial_institution_code === e.target.value);
            setFormData(prev => ({
              ...prev,
              bankCode: e.target.value,
              bankName: selectedBank?.financial_institution_name || ''
            }));
            // Clear error when user starts typing
            if (errors.bankCode) {
              setErrors(prev => ({
                ...prev,
                bankCode: undefined
              }));
            }
          }}
          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
            errors.bankCode ? 'border-red-500' : 'border-gray-300'
          }`}
        >
          <option value="">Selecciona tu banco</option>
          {banks.map(bank => (
            <option key={bank.financial_institution_code} value={bank.financial_institution_code}>
              {bank.financial_institution_name}
            </option>
          ))}
        </select>
        {errors.bankCode && (
          <p className="mt-1 text-sm text-red-600 flex items-center">
            <AlertCircle className="w-4 h-4 mr-1" />
            {errors.bankCode}
          </p>
        )}
      </div>

      {/* Important Information */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h4 className="text-sm font-medium text-yellow-800 mb-2">Información importante:</h4>
        <ul className="text-sm text-yellow-700 space-y-1">
          <li>• Asegúrate de tener activado el servicio de PSE en tu banco</li>
          <li>• Ten a la mano tu clave de internet banking</li>
          <li>• El proceso puede tomar algunos minutos</li>
          <li>• No cierres la ventana durante el proceso</li>
        </ul>
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
            Continuar con PSE - ${total.toLocaleString()}
          </>
        )}
      </button>

      {/* Security Notice */}
      <div className="text-xs text-gray-500 text-center">
        <Lock className="w-4 h-4 inline mr-1" />
        Serás redirigido al sitio seguro de tu banco para completar el pago
      </div>
    </form>
  );
};

export default PSEForm;