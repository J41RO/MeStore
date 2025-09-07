import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

// Schema de validación Yup para campos colombianos
const registerSchema = yup.object({
  nombre: yup
    .string()
    .required('Nombre completo es requerido')
    .test(
      'palabras-minimas',
      'Debe tener al menos 2 nombres y solo letras',
      value => {
        const words = value?.trim().split(/\s+/) || [];
        return words.length >= 2 && /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(value || '');
      }
    ),
  email: yup
    .string()
    .required('Correo electrónico es requerido')
    .email('Formato de email inválido'),
  cedula: yup
    .string()
    .required('Cédula es requerida')
    .test(
      'cedula-colombiana',
      'Cédula debe tener entre 8-10 dígitos numéricos',
      value => {
        const numericValue = value?.replace(/\D/g, '') || '';
        return (
          numericValue.length >= 8 &&
          numericValue.length <= 10 &&
          /^\d+$/.test(numericValue)
        );
      }
    ),
  telefono: yup
    .string()
    .required('Teléfono es requerido')
    .matches(/^\d{3}\s\d{3}\s\d{4}$/, 'Formato: 300 123 4567'),
  password: yup
    .string()
    .required('Contraseña es requerida')
    .min(8, 'Mínimo 8 caracteres')
    .matches(
      /(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'Mínimo 8 caracteres con mayúscula, minúscula y número'
    ),
  confirmPassword: yup
    .string()
    .required('Confirmación de contraseña es requerida')
    .oneOf([yup.ref('password')], 'Las contraseñas no coinciden'),
});

interface RegisterFormProps {
  onSuccess?: (data: any) => void;
  onValidationChange?: (isValid: boolean) => void;
  showValidationFeedback?: boolean;
}

interface ApiResponse {
  success: boolean;
  message: string;
  data?: any;
}

const RegisterForm: React.FC<RegisterFormProps> = ({ 
  onSuccess, 
  onValidationChange,
  showValidationFeedback = false 
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isValid, touchedFields },
    reset,
    watch,
  } = useForm({
    resolver: yupResolver(registerSchema),
    mode: 'onChange',
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');
  const [messageType, setMessageType] = useState<'success' | 'error'>('error');

  // Watch all fields for real-time validation feedback
  const watchedFields = watch();

  // Notify parent component about validation changes
  useEffect(() => {
    if (onValidationChange) {
      onValidationChange(isValid);
    }
  }, [isValid, onValidationChange]);

  // Helper function to get field validation status
  const getFieldStatus = (fieldName: string) => {
    const hasError = errors[fieldName as keyof typeof errors];
    const isTouched = touchedFields[fieldName as keyof typeof touchedFields];
    const hasValue = watchedFields[fieldName as keyof typeof watchedFields];
    
    if (!isTouched && !hasValue) return 'default';
    if (hasError) return 'error';
    if (isTouched && !hasError && hasValue) return 'success';
    return 'default';
  };

  // Helper function to render validation icon
  const renderValidationIcon = (fieldName: string) => {
    if (!showValidationFeedback) return null;
    
    const status = getFieldStatus(fieldName);
    
    if (status === 'success') {
      return (
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
          <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
      );
    }
    
    if (status === 'error') {
      return (
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
          <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
      );
    }
    
    return null;
  };

  // Helper function to get input border color
  const getInputBorderClass = (fieldName: string) => {
    if (!showValidationFeedback) {
      return errors[fieldName as keyof typeof errors] ? 'border-red-300 focus:border-red-500' : 'border-gray-300 focus:border-blue-500';
    }
    
    const status = getFieldStatus(fieldName);
    
    switch (status) {
      case 'success':
        return 'border-green-300 focus:border-green-500';
      case 'error':
        return 'border-red-300 focus:border-red-500';
      default:
        return 'border-gray-300 focus:border-blue-500';
    }
  };

  const onSubmit = async (data: any) => {
    setLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/v1/vendedores/registro', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        const result = await response.json();
        setMessage('¡Registro exitoso! Redirigiendo...');
        setMessageType('success');
        reset();
        
        if (onSuccess) {
          setTimeout(() => onSuccess(data), 1500);
        }
      } else {
        const errorData = await response.json();
        setMessage(errorData.message || 'Error en registro');
        setMessageType('error');
      }
    } catch (error) {
      setMessage('Error de conexión');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Nombre Completo */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Nombre Completo *
        </label>
        <div className="relative">
          <input
            {...register('nombre')}
            type="text"
            placeholder="Juan Carlos Pérez"
            className={`w-full px-4 py-3 rounded-lg border ${getInputBorderClass('nombre')} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white font-medium`}
          />
          {renderValidationIcon('nombre')}
        </div>
        {errors.nombre && (
          <p className="mt-1 text-sm text-red-600">{errors.nombre.message}</p>
        )}
      </div>

      {/* Email */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Correo Electrónico *
        </label>
        <div className="relative">
          <input
            {...register('email')}
            type="email"
            placeholder="juan@correo.com"
            className={`w-full px-4 py-3 rounded-lg border ${getInputBorderClass('email')} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white font-medium`}
          />
          {renderValidationIcon('email')}
        </div>
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
        )}
      </div>

      {/* Cédula */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Cédula de Ciudadanía *
        </label>
        <div className="relative">
          <input
            {...register('cedula')}
            type="text"
            placeholder="12345678"
            onInput={(e) => {
              const target = e.target as HTMLInputElement;
              target.value = target.value.replace(/\D/g, '');
            }}
            onKeyPress={(e) => {
              // Prevenir caracteres no numéricos
              if (!/[0-9]/.test(e.key) && !['Backspace', 'Delete', 'Tab', 'Enter'].includes(e.key)) {
                e.preventDefault();
              }
            }}
            maxLength={10}
            className={`w-full px-4 py-3 rounded-lg border ${getInputBorderClass('cedula')} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white font-medium`}
          />
          {renderValidationIcon('cedula')}
        </div>
        {errors.cedula && (
          <p className="mt-1 text-sm text-red-600">{errors.cedula.message}</p>
        )}
      </div>

      {/* Teléfono */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Teléfono Móvil *
        </label>
        <div className="relative flex">
          {/* Selector de país (preparado para futuro) */}
          <div className="flex items-center bg-gray-50 border border-r-0 border-gray-300 rounded-l-lg px-3 py-3">
            <span className="text-sm font-medium text-gray-700 mr-2">🇨🇴</span>
            <span className="text-sm text-gray-600">+57</span>
            <svg className="w-4 h-4 ml-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
          <input
            {...register('telefono')}
            type="tel"
            placeholder="300 123 4567"
            onInput={(e) => {
              const target = e.target as HTMLInputElement;
              let value = target.value.replace(/\D/g, '');
              // Formatear automáticamente: 300 123 4567
              if (value.length >= 6) {
                value = value.replace(/(\d{3})(\d{3})(\d{0,4})/, '$1 $2 $3');
              } else if (value.length >= 3) {
                value = value.replace(/(\d{3})(\d{0,3})/, '$1 $2');
              }
              target.value = value.trim();
            }}
            maxLength={12}
            className={`flex-1 px-4 py-3 rounded-r-lg border ${getInputBorderClass('telefono')} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white font-medium`}
          />
          {renderValidationIcon('telefono')}
        </div>
        {errors.telefono && (
          <p className="mt-1 text-sm text-red-600">{errors.telefono.message}</p>
        )}
      </div>

      {/* Password */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Contraseña *
        </label>
        <div className="relative">
          <input
            {...register('password')}
            type="password"
            placeholder="Mínimo 8 caracteres, mayúscula, minúscula y número"
            className={`w-full px-4 py-3 rounded-lg border ${getInputBorderClass('password')} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white font-medium`}
          />
          {renderValidationIcon('password')}
        </div>
        {errors.password && (
          <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
        )}
      </div>

      {/* Confirmar Password */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Confirmar Contraseña *
        </label>
        <div className="relative">
          <input
            {...register('confirmPassword')}
            type="password"
            placeholder="Repetir la contraseña"
            className={`w-full px-4 py-3 rounded-lg border ${getInputBorderClass('confirmPassword')} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white font-medium`}
          />
          {renderValidationIcon('confirmPassword')}
        </div>
        {errors.confirmPassword && (
          <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
        )}
      </div>

      {/* Mensaje de estado */}
      {message && (
        <div className={`p-4 rounded-lg text-sm text-center ${
          messageType === 'success' 
            ? 'bg-green-100 text-green-800 border border-green-200' 
            : 'bg-red-100 text-red-800 border border-red-200'
        }`}>
          {message}
        </div>
      )}

      {/* Botón de registro */}
      <button
        type="submit"
        disabled={loading || !isValid}
        className={`w-full py-3 px-4 rounded-lg font-medium text-white transition-all duration-200 ${
          !loading && isValid
            ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
            : 'bg-gray-400 cursor-not-allowed'
        }`}
      >
        {loading ? (
          <div className="flex items-center justify-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Registrando...
          </div>
        ) : (
          'Crear Cuenta'
        )}
      </button>
    </form>
  );
};

export default RegisterForm;