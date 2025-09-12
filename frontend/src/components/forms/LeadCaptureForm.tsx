import React, { useState } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';

interface LeadCaptureFormData {
  email: string;
  source?: string;
}

interface LeadCaptureFormProps {
  className?: string;
  compact?: boolean;
  placeholder?: string;
  source?: string;
  onSuccess?: (data: LeadCaptureFormData) => void;
}

const LeadCaptureForm: React.FC<LeadCaptureFormProps> = ({
  className = '',
  compact = false,
  placeholder = 'tu@empresa.com',
  source = 'landing',
  onSuccess
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm<LeadCaptureFormData>();

  const onSubmit: SubmitHandler<LeadCaptureFormData> = async (data) => {
    setIsSubmitting(true);
    setSubmitStatus('idle');
    setErrorMessage('');

    try {
      // Import leadService dynamically
      const { leadService } = await import('../../services/leadService');
      
      await leadService.createQuickLead(data.email, source);
      
      setSubmitStatus('success');
      reset();
      onSuccess?.(data);
      
      // Auto-hide success message after 3 seconds
      setTimeout(() => {
        setSubmitStatus('idle');
      }, 3000);
      
      // Track successful quick capture
      leadService.trackFormSubmission('quick_capture', true);
      
    } catch (error) {
      const { leadService } = await import('../../services/leadService');
      const errorMessage = leadService.formatErrorMessage(error);
      setErrorMessage(errorMessage);
      setSubmitStatus('error');
      
      // Track form error
      leadService.trackFormError('quick_capture', errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitStatus === 'success') {
    return (
      <div className={`${compact ? 'p-4' : 'p-6'} bg-green-50 border border-green-200 rounded-lg ${className}`}>
        <div className="flex items-center justify-center">
          <div className="text-green-500 mr-3">✅</div>
          <div className="text-center">
            <h4 className="font-semibold text-green-800">¡Listo!</h4>
            <p className="text-green-700 text-sm">
              Te notificaremos cuando esté disponible
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <form onSubmit={handleSubmit(onSubmit)} className={compact ? 'space-y-3' : 'space-y-4'}>
        <div className={compact ? 'flex gap-2' : 'space-y-2'}>
          <div className="flex-1">
            <input
              {...register('email', {
                required: 'Email requerido',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Email inválido'
                }
              })}
              type="email"
              className={`w-full px-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                compact ? 'py-2 text-sm' : 'py-3'
              } ${errors.email ? 'border-red-300' : ''}`}
              placeholder={placeholder}
            />
            {errors.email && !compact && (
              <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className={`bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none ${
              compact ? 'px-4 py-2 text-sm' : 'px-6 py-3'
            }`}
          >
            {isSubmitting ? (
              <span className="flex items-center">
                <svg className="animate-spin h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {compact ? '...' : 'Enviando...'}
              </span>
            ) : (
              compact ? 'Notificar' : 'Reservar Lugar'
            )}
          </button>
        </div>

        {errors.email && compact && (
          <p className="text-red-500 text-xs">{errors.email.message}</p>
        )}

        {errorMessage && (
          <div className={`bg-red-50 border border-red-200 rounded text-red-700 text-xs ${compact ? 'p-2' : 'p-3'}`}>
            {errorMessage}
          </div>
        )}

        {!compact && (
          <p className="text-xs text-gray-500 text-center">
            Sin spam. Solo te notificaremos cuando MeStocker esté listo.
          </p>
        )}
      </form>
    </div>
  );
};

export default LeadCaptureForm;