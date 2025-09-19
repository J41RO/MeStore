import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useAuthStore } from '../../stores/authStore';
import { UserType } from '../../types';
import type { RegisterFormProps } from '../../types';

// Schema de validación actualizado para integración con backend
const registerSchema = yup.object({
  nombre: yup
    .string()
    .required('Nombre completo es requerido')
    .min(2, 'Mínimo 2 caracteres')
    .matches(/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/, 'Solo se permiten letras y espacios'),
  email: yup
    .string()
    .required('Correo electrónico es requerido')
    .email('Formato de email inválido'),
  password: yup
    .string()
    .required('Contraseña es requerida')
    .min(6, 'Mínimo 6 caracteres')
    .matches(
      /^(?=.*[a-zA-Z])(?=.*\d)/,
      'Debe contener al menos una letra y un número'
    ),
  confirmPassword: yup
    .string()
    .required('Confirmación de contraseña es requerida')
    .oneOf([yup.ref('password')], 'Las contraseñas no coinciden'),
  // Campos opcionales para información adicional
  apellido: yup.string().optional(),
  telefono: yup
    .string()
    .optional()
    .matches(/^\d{3}\s\d{3}\s\d{4}$/, 'Formato: 300 123 4567'),
  cedula: yup
    .string()
    .optional()
    .test(
      'cedula-colombiana',
      'Cédula debe tener entre 8-10 dígitos numéricos',
      value => {
        if (!value) return true; // Campo opcional
        const numericValue = value.replace(/\D/g, '');
        return (
          numericValue.length >= 8 &&
          numericValue.length <= 10 &&
          /^\d+$/.test(numericValue)
        );
      }
    ),
});

// Interface ya definida en types, removemos la duplicada

const RegisterForm: React.FC<RegisterFormProps> = ({
  onRegisterSuccess,
  onRegisterError,
  onValidationChange,
  showValidationFeedback = false,
  userType = UserType.VENDOR // Default para vendors
}) => {
  // Zustand auth store
  const { register: registerUser, isLoading, error: authError, clearError } = useAuthStore();

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

  // Clear auth errors when user starts typing
  useEffect(() => {
    if (authError && Object.keys(watchedFields).some(key => watchedFields[key])) {
      clearError();
    }
  }, [watchedFields, authError, clearError]);

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
    setMessage('');

    try {
      // Preparar datos para el backend con tipo de usuario
      const registerData = {
        email: data.email.trim(),
        password: data.password,
        nombre: data.nombre.trim(),
        user_type: userType,
        // Campos opcionales
        ...(data.apellido && { apellido: data.apellido.trim() }),
        ...(data.telefono && { telefono: data.telefono }),
        ...(data.cedula && { cedula: data.cedula }),
      };

      // Usar el store de Zustand para registro
      const success = await registerUser(registerData.email, registerData.password);

      if (success) {
        setMessage('¡Registro exitoso! Bienvenido a MeStore');
        setMessageType('success');
        reset();

        if (onRegisterSuccess) {
          setTimeout(() => onRegisterSuccess({ email: registerData.email }), 1500);
        }
      } else {
        setMessage(authError || 'Error en el registro');
        setMessageType('error');

        if (onRegisterError) {
          onRegisterError({
            message: authError || 'Error en el registro',
            status: 400
          });
        }
      }
    } catch (error) {
      console.error('Error en onSubmit:', error);
      const errorMessage = 'Error inesperado durante el registro';
      setMessage(errorMessage);
      setMessageType('error');

      if (onRegisterError) {
        onRegisterError({
          message: errorMessage,
          status: 500
        });
      }
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

      {/* Error Message from Auth Store */}
      {authError && (
        <div className="p-4 rounded-lg bg-red-100 border border-red-200">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-sm text-red-800">{authError}</p>
          </div>
        </div>
      )}

      {/* Local Message */}
      {message && !authError && (
        <div className={`p-4 rounded-lg text-sm text-center ${
          messageType === 'success'
            ? 'bg-green-100 text-green-800 border border-green-200'
            : 'bg-red-100 text-red-800 border border-red-200'
        }`}>
          {message}
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading || !isValid}
        className={`w-full py-3 px-4 rounded-lg font-medium text-white transition-all duration-200 ${
          !isLoading && isValid
            ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
            : 'bg-gray-400 cursor-not-allowed'
        }`}
      >
        {isLoading ? (
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