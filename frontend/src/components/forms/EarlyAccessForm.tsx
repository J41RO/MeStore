import React, { useState, useEffect } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import MathCaptcha from '../security/MathCaptcha';
import { trackFormStart, trackFormSubmit, trackFormError, trackEvent } from '../../services/analytics';

interface EarlyAccessFormData {
  email: string;
  nombre: string;
  tipo_negocio: 'vendedor' | 'comprador' | 'ambos';
  telefono?: string;
  empresa?: string;
}

interface EarlyAccessFormProps {
  className?: string;
  onSuccess?: (data: EarlyAccessFormData) => void;
}

const EarlyAccessForm: React.FC<EarlyAccessFormProps> = ({ className = '', onSuccess }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [captchaValid, setCaptchaValid] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm<EarlyAccessFormData>();

  // Track form start when user first interacts
  useEffect(() => {
    const formElement = document.querySelector('form[data-form="early_access"]');
    if (formElement) {
      const handleFirstInteraction = () => {
        trackFormStart('early_access', {
          source: 'landing_page',
          form_type: 'lead_generation'
        });
        formElement.removeEventListener('focusin', handleFirstInteraction);
        formElement.removeEventListener('click', handleFirstInteraction);
      };

      formElement.addEventListener('focusin', handleFirstInteraction);
      formElement.addEventListener('click', handleFirstInteraction);

      return () => {
        formElement.removeEventListener('focusin', handleFirstInteraction);
        formElement.removeEventListener('click', handleFirstInteraction);
      };
    }
    return undefined;
  }, []);

  const onSubmit: SubmitHandler<EarlyAccessFormData> = async (data) => {
    if (!captchaValid) {
      setErrorMessage('Por favor, completa la verificación de seguridad');
      return;
    }

    setIsSubmitting(true);
    setSubmitStatus('idle');
    setErrorMessage('');

    try {
      // Import leadService dynamically to avoid import issues
      const { leadService } = await import('../../services/leadService');
      
      // Track form submission attempt
      leadService.trackFormSubmission('early_access', false);
      
      await leadService.createLead({
        ...data,
        source: 'early_access_form'
      });

      setSubmitStatus('success');
      reset();
      setCaptchaValid(false);
      onSuccess?.(data);
      
      // Track successful submission
      leadService.trackFormSubmission('early_access', true);
      
      // Enhanced analytics tracking
      trackFormSubmit('early_access', true, {
        business_type: data.tipo_negocio,
        has_phone: !!data.telefono,
        has_company: !!data.empresa,
        source: 'landing_page',
        value: 1 // Lead value
      });
      
      // Track lead generation conversion
      trackEvent('generate_lead', {
        lead_type: data.tipo_negocio,
        lead_source: 'early_access_form',
        value: 1,
        currency: 'COP',
        category: 'conversion'
      });
      
    } catch (error) {
      const { leadService } = await import('../../services/leadService');
      const errorMessage = leadService.formatErrorMessage(error);
      setErrorMessage(errorMessage);
      setSubmitStatus('error');
      
      // Track form error
      leadService.trackFormError('early_access', errorMessage);
      
      // Enhanced analytics error tracking
      trackFormError('early_access', errorMessage, {
        error_type: 'submission_error',
        source: 'landing_page'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCaptchaValidation = (isValid: boolean) => {
    setCaptchaValid(isValid);
    if (!isValid) {
      setErrorMessage('');
    }
  };

  return (
    <div className={`bg-white rounded-2xl shadow-2xl p-8 border border-gray-100 mx-auto max-w-md w-full ${className}`}>
      <div className="mb-6 text-center">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">
          Únete al Early Access
        </h3>
        <p className="text-gray-600">
          Sé de los primeros en acceder a MeStocker. Sin compromisos, solo ventajas.
        </p>
      </div>

      {submitStatus === 'success' && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center justify-center">
            <div className="text-green-500 mr-3">✅</div>
            <div className="text-center">
              <h4 className="font-semibold text-green-800">¡Registro Exitoso!</h4>
              <p className="text-green-700 text-sm">
                Te contactaremos pronto con acceso prioritario y beneficios exclusivos.
              </p>
            </div>
          </div>
        </div>
      )}

      <form 
        onSubmit={handleSubmit(onSubmit)} 
        className="space-y-6 flex flex-col items-center"
        data-form="early_access"
      >
        {/* Email */}
        <div className="w-full">
          <label htmlFor="email" className="block text-sm font-semibold text-gray-700 mb-2 text-center">
            Email Corporativo *
          </label>
          <input
            {...register('email', {
              required: 'Email es requerido',
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: 'Email inválido'
              }
            })}
            type="email"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            placeholder="tu@empresa.com"
          />
          {errors.email && (
            <p className="text-red-500 text-sm mt-1 text-center">{errors.email.message}</p>
          )}
        </div>

        {/* Nombre */}
        <div className="w-full">
          <label htmlFor="nombre" className="block text-sm font-semibold text-gray-700 mb-2 text-center">
            Nombre Completo *
          </label>
          <input
            {...register('nombre', {
              required: 'Nombre es requerido',
              minLength: {
                value: 2,
                message: 'Nombre debe tener al menos 2 caracteres'
              }
            })}
            type="text"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            placeholder="Juan Pérez"
          />
          {errors.nombre && (
            <p className="text-red-500 text-sm mt-1 text-center">{errors.nombre.message}</p>
          )}
        </div>

        {/* Tipo de Negocio */}
        <div className="w-full">
          <label className="block text-sm font-semibold text-gray-700 mb-3 text-center">
            Tipo de Negocio *
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              { value: 'vendedor', label: 'Vendedor', icon: '🏪', desc: 'Vendo productos' },
              { value: 'comprador', label: 'Comprador', icon: '🛒', desc: 'Compro productos' },
              { value: 'ambos', label: 'Ambos', icon: '🔄', desc: 'Compro y vendo' }
            ].map((option) => (
              <label key={option.value} className="relative">
                <input
                  {...register('tipo_negocio', { required: 'Selecciona un tipo de negocio' })}
                  type="radio"
                  value={option.value}
                  className="sr-only peer"
                />
                <div className="cursor-pointer p-4 border-2 border-gray-200 rounded-lg peer-checked:border-blue-500 peer-checked:bg-blue-50 hover:border-gray-300 transition-all">
                  <div className="text-center">
                    <div className="text-2xl mb-2">{option.icon}</div>
                    <div className="font-semibold text-gray-900">{option.label}</div>
                    <div className="text-xs text-gray-500">{option.desc}</div>
                  </div>
                </div>
              </label>
            ))}
          </div>
          {errors.tipo_negocio && (
            <p className="text-red-500 text-sm mt-1 text-center">{errors.tipo_negocio.message}</p>
          )}
        </div>

        {/* Teléfono (Opcional) */}
        <div className="w-full">
          <label htmlFor="telefono" className="block text-sm font-semibold text-gray-700 mb-2 text-center">
            WhatsApp (Opcional)
          </label>
          <input
            {...register('telefono', {
              pattern: {
                value: /^[+]?[0-9\s-()]{7,15}$/,
                message: 'Número de teléfono inválido'
              }
            })}
            type="tel"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            placeholder="+57 300 123 4567"
          />
          {errors.telefono && (
            <p className="text-red-500 text-sm mt-1 text-center">{errors.telefono.message}</p>
          )}
        </div>

        {/* Empresa (Opcional) */}
        <div className="w-full">
          <label htmlFor="empresa" className="block text-sm font-semibold text-gray-700 mb-2 text-center">
            Empresa (Opcional)
          </label>
          <input
            {...register('empresa')}
            type="text"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            placeholder="Mi Empresa S.A.S"
          />
        </div>

        {/* Captcha */}
        <MathCaptcha onValidationChange={handleCaptchaValidation} />

        {/* Error Message */}
        {errorMessage && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg w-full">
            <div className="flex items-center justify-center">
              <div className="text-red-500 mr-3">⚠️</div>
              <p className="text-red-700 text-sm text-center">{errorMessage}</p>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSubmitting || !captchaValid}
          className={`w-full py-4 px-6 rounded-lg font-bold text-lg transition-all duration-300 mx-auto block ${
            isSubmitting || !captchaValid
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 transform hover:scale-105 shadow-lg hover:shadow-xl'
          }`}
        >
          {isSubmitting ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Procesando...
            </span>
          ) : (
            'Reservar Mi Lugar'
          )}
        </button>

        <div className="text-center w-full">
          <p className="text-xs text-gray-500">
            Al registrarte, aceptas recibir información sobre MeStocker. 
            <br />
            <span className="font-semibold">100% libre de spam.</span>
          </p>
        </div>
      </form>
    </div>
  );
};

export default EarlyAccessForm;