/**
 * Mobile Checkout Component
 * Optimized checkout flow for Colombian market with mobile payments
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useGesture } from '@use-gesture/react';
import {
  CreditCardIcon,
  BuildingLibraryIcon,
  DevicePhoneMobileIcon,
  LockClosedIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowLeftIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

interface CheckoutFormData {
  // Personal info
  email: string;
  nombre: string;
  telefono: string;

  // Address
  direccion: string;
  ciudad: string;
  departamento: string;
  codigoPostal: string;

  // Payment
  paymentMethod: 'pse' | 'credit_card' | 'nequi' | 'daviplata';

  // PSE specific
  banco?: string;
  tipoPersona?: 'NATURAL' | 'JURIDICA';
  tipoDocumento?: 'CC' | 'CE' | 'NIT';
  numeroDocumento?: string;

  // Credit card specific
  numeroTarjeta?: string;
  fechaVencimiento?: string;
  cvv?: string;
  nombreTarjeta?: string;
}

interface MobileCheckoutProps {
  cartItems: any[];
  total: number;
  onComplete: (data: CheckoutFormData) => Promise<void>;
  className?: string;
}

const MobileCheckout: React.FC<MobileCheckoutProps> = ({
  cartItems,
  total,
  onComplete,
  className = ''
}) => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [isProcessing, setIsProcessing] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors: formErrors, isValid }
  } = useForm<CheckoutFormData>({
    mode: 'onChange',
    defaultValues: {
      departamento: 'Santander',
      ciudad: 'Bucaramanga',
      paymentMethod: 'pse'
    }
  });

  const paymentMethod = watch('paymentMethod');

  // Gesture handling for step navigation
  const bind = useGesture({
    onDrag: ({ movement: [mx], direction: [xDir], distance, cancel }) => {
      if (distance > 50) {
        if (xDir > 0 && currentStep > 1) {
          setCurrentStep(currentStep - 1);
          cancel();
        } else if (xDir < 0 && currentStep < 3) {
          setCurrentStep(currentStep + 1);
          cancel();
        }
      }
    }
  });

  const steps = [
    { id: 1, title: 'Información Personal', icon: '👤' },
    { id: 2, title: 'Dirección de Envío', icon: '📍' },
    { id: 3, title: 'Método de Pago', icon: '💳' }
  ];

  const paymentMethods = [
    {
      id: 'pse',
      name: 'PSE',
      description: 'Pago seguro con tu banco',
      icon: BuildingLibraryIcon,
      color: 'bg-blue-50 border-blue-200 text-blue-700',
      popular: true
    },
    {
      id: 'credit_card',
      name: 'Tarjeta de Crédito',
      description: 'Visa, Mastercard, American Express',
      icon: CreditCardIcon,
      color: 'bg-green-50 border-green-200 text-green-700'
    },
    {
      id: 'nequi',
      name: 'Nequi',
      description: 'Pago con Nequi desde tu celular',
      icon: DevicePhoneMobileIcon,
      color: 'bg-purple-50 border-purple-200 text-purple-700'
    },
    {
      id: 'daviplata',
      name: 'DaviPlata',
      description: 'Pago con DaviPlata',
      icon: DevicePhoneMobileIcon,
      color: 'bg-orange-50 border-orange-200 text-orange-700'
    }
  ];

  const colombianBanks = [
    'Bancolombia',
    'Banco de Bogotá',
    'Banco Popular',
    'BBVA Colombia',
    'Banco Caja Social',
    'Banco AV Villas',
    'Banco Agrario',
    'Citibank',
    'Banco GNB Sudameris',
    'Banco Falabella'
  ];

  const handleStepNavigation = (step: number) => {
    if (step >= 1 && step <= 3) {
      setCurrentStep(step);
    }
  };

  const validateStep = (step: number): boolean => {
    const data = watch();

    switch (step) {
      case 1:
        return !!(data.email && data.nombre && data.telefono);
      case 2:
        return !!(data.direccion && data.ciudad && data.departamento);
      case 3:
        if (data.paymentMethod === 'pse') {
          return !!(data.banco && data.tipoPersona && data.tipoDocumento && data.numeroDocumento);
        } else if (data.paymentMethod === 'credit_card') {
          return !!(data.numeroTarjeta && data.fechaVencimiento && data.cvv && data.nombreTarjeta);
        }
        return true;
      default:
        return false;
    }
  };

  const onSubmit = async (data: CheckoutFormData) => {
    setIsProcessing(true);
    setErrors([]);

    try {
      await onComplete(data);
    } catch (error: any) {
      setErrors([error.message || 'Error procesando el pago']);
    } finally {
      setIsProcessing(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">
              Información Personal
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Correo Electrónico
                </label>
                <input
                  {...register('email', {
                    required: 'El correo es obligatorio',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: 'Correo inválido'
                    }
                  })}
                  type="email"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                  placeholder="tu@correo.com"
                />
                {formErrors.email && (
                  <p className="text-red-500 text-sm mt-1">{formErrors.email.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre Completo
                </label>
                <input
                  {...register('nombre', { required: 'El nombre es obligatorio' })}
                  type="text"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                  placeholder="Tu nombre completo"
                />
                {formErrors.nombre && (
                  <p className="text-red-500 text-sm mt-1">{formErrors.nombre.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Teléfono
                </label>
                <input
                  {...register('telefono', {
                    required: 'El teléfono es obligatorio',
                    pattern: {
                      value: /^3\d{9}$/,
                      message: 'Formato: 3XXXXXXXXX'
                    }
                  })}
                  type="tel"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                  placeholder="3001234567"
                />
                {formErrors.telefono && (
                  <p className="text-red-500 text-sm mt-1">{formErrors.telefono.message}</p>
                )}
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">
              Dirección de Envío
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dirección Completa
                </label>
                <input
                  {...register('direccion', { required: 'La dirección es obligatoria' })}
                  type="text"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                  placeholder="Calle 123 #45-67, Apartamento 8B"
                />
                {formErrors.direccion && (
                  <p className="text-red-500 text-sm mt-1">{formErrors.direccion.message}</p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ciudad
                  </label>
                  <select
                    {...register('ciudad', { required: 'La ciudad es obligatoria' })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                  >
                    <option value="Bucaramanga">Bucaramanga</option>
                    <option value="Floridablanca">Floridablanca</option>
                    <option value="Girón">Girón</option>
                    <option value="Piedecuesta">Piedecuesta</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Departamento
                  </label>
                  <select
                    {...register('departamento')}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                  >
                    <option value="Santander">Santander</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Código Postal (Opcional)
                </label>
                <input
                  {...register('codigoPostal')}
                  type="text"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                  placeholder="680001"
                />
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">
              Método de Pago
            </h3>

            {/* Payment Method Selection */}
            <div className="space-y-3">
              {paymentMethods.map((method) => (
                <div
                  key={method.id}
                  className={`relative border-2 rounded-lg p-4 cursor-pointer transition-all ${
                    paymentMethod === method.id
                      ? method.color
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setValue('paymentMethod', method.id as any)}
                >
                  {method.popular && (
                    <div className="absolute -top-2 -right-2 bg-blue-600 text-white text-xs px-2 py-1 rounded-full">
                      Popular
                    </div>
                  )}

                  <div className="flex items-center">
                    <input
                      type="radio"
                      {...register('paymentMethod')}
                      value={method.id}
                      className="sr-only"
                    />
                    <method.icon className="w-6 h-6 mr-3 flex-shrink-0" />
                    <div className="flex-1">
                      <div className="font-medium">{method.name}</div>
                      <div className="text-sm opacity-75">{method.description}</div>
                    </div>
                    {paymentMethod === method.id && (
                      <CheckCircleIcon className="w-6 h-6 text-current" />
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* PSE Form */}
            {paymentMethod === 'pse' && (
              <div className="space-y-4 mt-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Banco
                  </label>
                  <select
                    {...register('banco', { required: 'Selecciona tu banco' })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                  >
                    <option value="">Selecciona tu banco</option>
                    {colombianBanks.map((bank) => (
                      <option key={bank} value={bank}>{bank}</option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tipo de Persona
                    </label>
                    <select
                      {...register('tipoPersona')}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                    >
                      <option value="NATURAL">Natural</option>
                      <option value="JURIDICA">Jurídica</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tipo de Documento
                    </label>
                    <select
                      {...register('tipoDocumento')}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                    >
                      <option value="CC">Cédula</option>
                      <option value="CE">Cédula Extranjería</option>
                      <option value="NIT">NIT</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Número de Documento
                  </label>
                  <input
                    {...register('numeroDocumento', { required: 'El documento es obligatorio' })}
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                    placeholder="12345678"
                  />
                </div>
              </div>
            )}

            {/* Credit Card Form */}
            {paymentMethod === 'credit_card' && (
              <div className="space-y-4 mt-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Número de Tarjeta
                  </label>
                  <input
                    {...register('numeroTarjeta', {
                      required: 'El número de tarjeta es obligatorio',
                      pattern: {
                        value: /^\d{16}$/,
                        message: 'Debe tener 16 dígitos'
                      }
                    })}
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                    placeholder="1234 5678 9012 3456"
                    maxLength={16}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Fecha de Vencimiento
                    </label>
                    <input
                      {...register('fechaVencimiento', { required: 'La fecha es obligatoria' })}
                      type="text"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                      placeholder="MM/YY"
                      maxLength={5}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      CVV
                    </label>
                    <input
                      {...register('cvv', {
                        required: 'El CVV es obligatorio',
                        pattern: {
                          value: /^\d{3,4}$/,
                          message: '3 o 4 dígitos'
                        }
                      })}
                      type="text"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                      placeholder="123"
                      maxLength={4}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre en la Tarjeta
                  </label>
                  <input
                    {...register('nombreTarjeta', { required: 'El nombre es obligatorio' })}
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                    placeholder="JUAN PEREZ"
                  />
                </div>
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className={`min-h-screen bg-gray-50 ${className}`} {...bind()}>
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-4">
        <div className="flex items-center">
          <button
            onClick={() => navigate(-1)}
            className="mr-4 p-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeftIcon className="w-6 h-6" />
          </button>
          <h1 className="text-lg font-semibold text-gray-900">Checkout</h1>
        </div>

        {/* Step Indicator */}
        <div className="flex items-center justify-center mt-4">
          {steps.map((step, index) => (
            <React.Fragment key={step.id}>
              <div
                className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                  currentStep >= step.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}
              >
                {step.icon}
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`w-12 h-1 mx-2 ${
                    currentStep > step.id ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                />
              )}
            </React.Fragment>
          ))}
        </div>

        <div className="text-center mt-2">
          <span className="text-sm text-gray-600">
            Paso {currentStep} de {steps.length}: {steps[currentStep - 1]?.title}
          </span>
        </div>
      </div>

      {/* Content */}
      <form onSubmit={handleSubmit(onSubmit)} className="flex-1">
        <div className="p-4">
          {errors.length > 0 && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex">
                <ExclamationTriangleIcon className="w-5 h-5 text-red-400 mr-2" />
                <div className="text-sm text-red-700">
                  {errors.map((error, index) => (
                    <p key={index}>{error}</p>
                  ))}
                </div>
              </div>
            </div>
          )}

          {renderStepContent()}
        </div>

        {/* Order Summary (Fixed at bottom) */}
        <div className="bg-white border-t border-gray-200 p-4 sticky bottom-0">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm text-gray-600">
              Total ({cartItems.length} {cartItems.length === 1 ? 'artículo' : 'artículos'})
            </span>
            <span className="text-lg font-bold text-gray-900">
              ${total.toLocaleString('es-CO')} COP
            </span>
          </div>

          <div className="flex space-x-3">
            {currentStep > 1 && (
              <button
                type="button"
                onClick={() => setCurrentStep(currentStep - 1)}
                className="flex-1 py-3 px-4 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50"
              >
                Anterior
              </button>
            )}

            {currentStep < 3 ? (
              <button
                type="button"
                onClick={() => setCurrentStep(currentStep + 1)}
                disabled={!validateStep(currentStep)}
                className="flex-1 py-3 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center"
              >
                Continuar
                <ArrowRightIcon className="w-4 h-4 ml-2" />
              </button>
            ) : (
              <button
                type="submit"
                disabled={!validateStep(3) || isProcessing}
                className="flex-1 py-3 px-4 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isProcessing ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                ) : (
                  <LockClosedIcon className="w-4 h-4 mr-2" />
                )}
                {isProcessing ? 'Procesando...' : 'Pagar Seguro'}
              </button>
            )}
          </div>

          <div className="text-xs text-gray-500 text-center mt-2">
            <LockClosedIcon className="w-4 h-4 inline mr-1" />
            Tu información está protegida con SSL
          </div>
        </div>
      </form>
    </div>
  );
};

export default MobileCheckout;