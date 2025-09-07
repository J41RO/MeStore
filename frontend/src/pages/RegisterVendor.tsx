import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useAuthStore, UserType } from '../stores/authStore';
import { GoogleLogin } from '@react-oauth/google';
import { FaFacebook, FaGoogle } from 'react-icons/fa';

// Schema de validación para datos básicos (Paso 1)
const basicDataSchema = yup.object({
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
  telefono: yup
    .string()
    .required('Teléfono es requerido')
    .matches(/^\d{3}\s\d{3}\s\d{4}$/, 'Formato: 300 123 4567'),
});

// Schema de validación para COMPRADOR (Paso 3)
const compradorSchema = yup.object({
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
  direccion: yup
    .string()
    .required('Dirección es requerida')
    .min(10, 'Dirección debe tener al menos 10 caracteres'),
  ciudad: yup
    .string()
    .required('Ciudad es requerida')
    .min(3, 'Ciudad debe tener al menos 3 caracteres'),
  departamento: yup
    .string()
    .required('Departamento es requerido'),
});

// Schema de validación para VENDEDOR (Paso 3)
const vendedorSchema = yup.object({
  tipo_vendedor: yup
    .string()
    .required('Tipo de vendedor es requerido')
    .oneOf(['persona_juridica', 'persona_natural'], 'Selecciona un tipo válido'),
  nombre_empresa: yup
    .string()
    .when('tipo_vendedor', {
      is: 'persona_juridica',
      then: (schema) => schema.required('Nombre de empresa es requerido').min(3, 'Mínimo 3 caracteres'),
      otherwise: (schema) => schema.notRequired(),
    }),
  nit: yup
    .string()
    .when('tipo_vendedor', {
      is: 'persona_juridica',
      then: (schema) => schema.required('NIT es requerido').matches(/^\d{9}-\d$/, 'Formato: 123456789-0'),
      otherwise: (schema) => schema.notRequired(),
    }),
  direccion_fiscal: yup
    .string()
    .required('Dirección fiscal es requerida')
    .min(10, 'Dirección debe tener al menos 10 caracteres'),
  ciudad_fiscal: yup
    .string()
    .required('Ciudad fiscal es requerida'),
  departamento_fiscal: yup
    .string()
    .required('Departamento fiscal es requerido'),
});

const RegisterVendor: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<1 | 2 | 3>(1);
  const [basicFormData, setBasicFormData] = useState<any>(null);
  const [selectedRole, setSelectedRole] = useState<UserType | null>(null);
  const [specificData, setSpecificData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [oauthLoading, setOauthLoading] = useState<'google' | 'facebook' | null>(null);

  // Form para Paso 1 - Datos básicos
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    watch,
    setValue,
  } = useForm({
    resolver: yupResolver(basicDataSchema),
    mode: 'onChange',
  });

  // Form para Paso 3 - Datos específicos
  const {
    register: registerStep3,
    handleSubmit: handleSubmitStep3,
    formState: { errors: errorsStep3, isValid: isValidStep3 },
    watch: watchStep3,
    setValue: setValueStep3,
  } = useForm({
    resolver: yupResolver(selectedRole === UserType.COMPRADOR ? compradorSchema : vendedorSchema),
    mode: 'onChange',
  });

  const watchedFields = watch();
  const watchedFieldsStep3 = watchStep3();

  // Funciones OAuth
  const handleGoogleSuccess = async (credentialResponse: any) => {
    setOauthLoading('google');
    try {
      // TODO: Integración real con Google OAuth
      console.log('Google OAuth Success:', credentialResponse);
      
      // Simulación de datos del usuario desde Google
      const mockUserData = {
        nombre: 'Usuario Google',
        email: 'usuario@gmail.com',
        telefono: '', // El usuario deberá completar este campo
      };
      
      // Pre-llenar formulario con datos de Google
      setValue('nombre', mockUserData.nombre);
      setValue('email', mockUserData.email);
      
      // Mostrar mensaje de éxito
      alert('Datos de Google cargados. Por favor completa el número de teléfono.');
      
    } catch (error) {
      console.error('Error en autenticación con Google:', error);
      alert('Error al conectar con Google. Intenta nuevamente.');
    } finally {
      setOauthLoading(null);
    }
  };

  const handleGoogleError = () => {
    console.error('Error en Google OAuth');
    alert('Error al conectar con Google. Intenta nuevamente.');
    setOauthLoading(null);
  };

  const handleFacebookLogin = async () => {
    setOauthLoading('facebook');
    try {
      // TODO: Integración real con Facebook SDK
      console.log('Facebook OAuth Initiated');
      
      // Simulación de datos del usuario desde Facebook
      const mockUserData = {
        nombre: 'Usuario Facebook',
        email: 'usuario@facebook.com',
        telefono: '', // El usuario deberá completar este campo
      };
      
      // Pre-llenar formulario con datos de Facebook
      setValue('nombre', mockUserData.nombre);
      setValue('email', mockUserData.email);
      
      // Mostrar mensaje de éxito
      alert('Datos de Facebook cargados. Por favor completa el número de teléfono.');
      
    } catch (error) {
      console.error('Error en autenticación con Facebook:', error);
      alert('Error al conectar con Facebook. Intenta nuevamente.');
    } finally {
      setOauthLoading(null);
    }
  };

  // Funciones de navegación entre pasos
  const nextStep = () => {
    if (currentStep === 1 && isValid) {
      setCurrentStep(2);
    } else if (currentStep === 2 && selectedRole) {
      setCurrentStep(3);
    }
  };

  const prevStep = () => {
    if (currentStep === 2) {
      setCurrentStep(1);
    } else if (currentStep === 3) {
      setCurrentStep(2);
    }
  };

  // Manejar datos del Paso 1
  const handleBasicDataSubmit = (data: any) => {
    setBasicFormData(data);
    nextStep();
  };

  // Manejar selección de rol
  const handleRoleSelect = (role: UserType) => {
    setSelectedRole(role);
  };

  // Continuar al paso 3 después de seleccionar rol
  const handleRoleSubmit = () => {
    if (selectedRole) {
      nextStep();
    }
  };

  // Manejar datos del Paso 3
  const handleSpecificDataSubmit = (data: any) => {
    setSpecificData(data);
    handleFinalSubmit(data);
  };

  // Envío final
  const handleFinalSubmit = async (step3Data?: any) => {
    if (!basicFormData || !selectedRole) return;

    setLoading(true);
    try {
      const finalData = {
        ...basicFormData,
        ...specificData,
        ...step3Data,
        user_type: selectedRole,
        password: 'temp123', // En producción, agregar campo de password
        confirmPassword: 'temp123'
      };

      const response = await fetch('/api/v1/vendedores/registro', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(finalData),
      });

      if (response.ok) {
        navigate('/verify-otp', { state: { telefono: basicFormData.telefono } });
      } else {
        console.error('Error en registro');
      }
    } catch (error) {
      console.error('Error de conexión:', error);
    } finally {
      setLoading(false);
    }
  };

  // Helper function para renderizar iconos de validación
  const renderValidationIcon = (fieldName: string, formErrors?: any, formFields?: any) => {
    const errors = formErrors || errorsStep3;
    const fields = formFields || watchedFieldsStep3;

    const hasError = errors[fieldName as keyof typeof errors];
    const hasValue = fields[fieldName as keyof typeof fields];

    if (hasValue && !hasError) {
      return (
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
          <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
      );
    }

    if (hasError) {
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

  // Helper function para clases de input
  const getInputBorderClass = (fieldName: string, formErrors?: any, formFields?: any) => {
    const errors = formErrors || errorsStep3;
    const fields = formFields || watchedFieldsStep3;

    const hasError = errors[fieldName as keyof typeof errors];
    const hasValue = fields[fieldName as keyof typeof fields];

    if (hasValue && !hasError) return 'border-green-300 focus:border-green-500';
    if (hasError) return 'border-red-300 focus:border-red-500';
    return 'border-gray-300 focus:border-blue-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Layout dividido: Grid responsivo */}
      <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2">

        {/* LADO IZQUIERDO: Formulario (50%) */}
        <div className="flex items-center justify-center p-6 lg:p-12">
          <div className="w-full max-w-md space-y-8">

            {/* Indicador de progreso */}
            <div className="flex justify-center mb-6">
              <div className="flex items-center space-x-4">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${currentStep >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
                  1
                </div>
                <div className="w-6 border-t-2 border-gray-300"></div>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${currentStep >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
                  2
                </div>
                <div className="w-6 border-t-2 border-gray-300"></div>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${currentStep >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
                  3
                </div>
              </div>
            </div>

            {/* Header del formulario */}
            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                Únete a MeStocker
              </h2>
              <p className="text-gray-600">
                {currentStep === 1 && 'Completa tus datos personales'}
                {currentStep === 2 && 'Selecciona cómo quieres usar MeStocker'}
                {currentStep === 3 && selectedRole === UserType.COMPRADOR && 'Información para entregas'}
                {currentStep === 3 && selectedRole === UserType.VENDEDOR && 'Información comercial'}
              </p>
            </div>

            {/* Contenido por pasos */}
            <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">

              {/* PASO 1: Datos básicos */}
              {currentStep === 1 && (
                <div className="space-y-6">
                  <div className="text-center mb-6">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Información Básica</h3>
                    <p className="text-gray-600 text-sm">Paso 1 de 3</p>
                  </div>

                  {/* Botones OAuth */}
                  <div className="space-y-4 mb-6">
                    <div className="text-center">
                      <p className="text-sm text-gray-600 mb-4">Regístrate rápidamente con:</p>
                    </div>
                    
                    {/* Botón Google */}
                    <div className="w-full">
                      <GoogleLogin
                        onSuccess={handleGoogleSuccess}
                        onError={handleGoogleError}
                        useOneTap={false}
                        auto_select={false}
                        width="100%"
                        text="signup_with"
                        theme="outline"
                        size="large"
                        logo_alignment="left"
                      />
                    </div>

                    {/* Botón Facebook Custom */}
                    <button
                      onClick={handleFacebookLogin}
                      disabled={oauthLoading === 'facebook'}
                      className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg bg-[#1877F2] text-white font-medium hover:bg-[#166FE5] transition-colors duration-200 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {oauthLoading === 'facebook' ? (
                        <div className="flex items-center">
                          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Conectando...
                        </div>
                      ) : (
                        <div className="flex items-center">
                          <FaFacebook className="w-5 h-5 mr-3" />
                          Registrarse con Facebook
                        </div>
                      )}
                    </button>

                    {/* Separador */}
                    <div className="relative my-6">
                      <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-gray-300"></div>
                      </div>
                      <div className="relative flex justify-center text-sm">
                        <span className="px-4 bg-white text-gray-500 font-medium">o continúa con email</span>
                      </div>
                    </div>
                  </div>

                  {/* Formulario tradicional */}
                  <form onSubmit={handleSubmit(handleBasicDataSubmit)} className="space-y-6">
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
                          className={`w-full px-4 py-3 rounded-lg border ${getInputBorderClass('nombre', errors, watchedFields)} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white font-medium`}
                        />
                        {renderValidationIcon('nombre', errors, watchedFields)}
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
                          className={`w-full px-4 py-3 rounded-lg border ${getInputBorderClass('email', errors, watchedFields)} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white font-medium`}
                        />
                        {renderValidationIcon('email', errors, watchedFields)}
                      </div>
                      {errors.email && (
                        <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                      )}
                    </div>

                    {/* Teléfono */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Teléfono Móvil *
                      </label>
                      <div className="relative flex">
                        <div className="flex items-center bg-gray-50 border border-r-0 border-gray-300 rounded-l-lg px-3 py-3">
                          <span className="text-sm font-medium text-gray-700 mr-2">🇨🇴</span>
                          <span className="text-sm text-gray-600">+57</span>
                        </div>
                        <input
                          {...register('telefono')}
                          type="tel"
                          placeholder="300 123 4567"
                          onInput={(e) => {
                            const target = e.target as HTMLInputElement;
                            let value = target.value.replace(/\D/g, '');
                            if (value.length >= 6) {
                              value = value.replace(/(\d{3})(\d{3})(\d{0,4})/, '$1 $2 $3');
                            } else if (value.length >= 3) {
                              value = value.replace(/(\d{3})(\d{0,3})/, '$1 $2');
                            }
                            target.value = value.trim();
                          }}
                          maxLength={12}
                          className={`flex-1 px-4 py-3 rounded-r-lg border ${getInputBorderClass('telefono', errors, watchedFields)} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white font-medium`}
                        />
                        {renderValidationIcon('telefono', errors, watchedFields)}
                      </div>
                      {errors.telefono && (
                        <p className="mt-1 text-sm text-red-600">{errors.telefono.message}</p>
                      )}
                    </div>

                    {/* Botón continuar */}
                    <button
                      type="submit"
                      disabled={!isValid}
                      className={`w-full py-3 px-4 rounded-lg font-medium text-white transition-all duration-200 ${
                        isValid
                          ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                          : 'bg-gray-400 cursor-not-allowed'
                      }`}
                    >
                      Continuar al Paso 2
                    </button>
                  </form>
                </div>
              )}

              {/* PASO 2: Selección de rol */}
              {currentStep === 2 && (
                <div className="space-y-6">
                  <div className="text-center mb-6">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Selecciona tu Rol</h3>
                    <p className="text-gray-600 text-sm">Paso 2 de 3</p>
                  </div>

                  {/* Cards de selección */}
                  <div className="space-y-4">
                    {/* Card Vendedor */}
                    <div
                      onClick={() => handleRoleSelect(UserType.VENDEDOR)}
                      className={`p-6 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                        selectedRole === UserType.VENDEDOR
                          ? 'border-blue-500 bg-blue-50 shadow-lg transform scale-105'
                          : 'border-gray-200 hover:border-blue-300 hover:shadow-md'
                      }`}
                    >
                      <div className="flex items-center space-x-4">
                        <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                          selectedRole === UserType.VENDEDOR ? 'bg-blue-100' : 'bg-gray-100'
                        }`}>
                          <svg className={`w-6 h-6 ${
                            selectedRole === UserType.VENDEDOR ? 'text-blue-600' : 'text-gray-600'
                          }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                          </svg>
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900">SOY VENDEDOR</h4>
                          <p className="text-sm text-gray-600">Quiero vender mis productos</p>
                        </div>
                        {selectedRole === UserType.VENDEDOR && (
                          <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Card Comprador */}
                    <div
                      onClick={() => handleRoleSelect(UserType.COMPRADOR)}
                      className={`p-6 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                        selectedRole === UserType.COMPRADOR
                          ? 'border-green-500 bg-green-50 shadow-lg transform scale-105'
                          : 'border-gray-200 hover:border-green-300 hover:shadow-md'
                      }`}
                    >
                      <div className="flex items-center space-x-4">
                        <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                          selectedRole === UserType.COMPRADOR ? 'bg-green-100' : 'bg-gray-100'
                        }`}>
                          <svg className={`w-6 h-6 ${
                            selectedRole === UserType.COMPRADOR ? 'text-green-600' : 'text-gray-600'
                          }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                          </svg>
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900">SOY COMPRADOR</h4>
                          <p className="text-sm text-gray-600">Quiero comprar productos</p>
                        </div>
                        {selectedRole === UserType.COMPRADOR && (
                          <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Botones de navegación */}
                  <div className="flex space-x-4">
                    <button
                      onClick={prevStep}
                      className="flex-1 py-3 px-4 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      Atrás
                    </button>
                    <button
                      onClick={handleRoleSubmit}
                      disabled={!selectedRole}
                      className={`flex-1 py-3 px-4 rounded-lg font-medium text-white transition-all duration-200 ${
                        selectedRole
                          ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                          : 'bg-gray-400 cursor-not-allowed'
                      }`}
                    >
                      Continuar al Paso 3
                    </button>
                  </div>
                </div>
              )}

              {/* PASO 3: Datos específicos según rol */}
              {currentStep === 3 && (
                <form onSubmit={handleSubmitStep3(handleSpecificDataSubmit)} className="space-y-6">
                  <div className="text-center mb-6">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      {selectedRole === UserType.COMPRADOR ? 'Información para Entregas' : 'Información Comercial'}
                    </h3>
                    <p className="text-gray-600 text-sm">Paso 3 de 3</p>
                  </div>

                  {/* FORMULARIO PARA COMPRADORES */}
                  {selectedRole === UserType.COMPRADOR && (
                    <>
                      {/* Cédula */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Cédula de Ciudadanía *
                        </label>
                        <div className="relative">
                          <input
                            {...registerStep3('cedula')}
                            type="text"
                            placeholder="12345678"
                            onInput={(e) => {
                              const target = e.target as HTMLInputElement;
                              target.value = target.value.replace(/\D/g, '');
                            }}
                            maxLength={10}
                            className={`w-full px-4 py-3 rounded-lg border ${getInputBorderClass('cedula')} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white font-medium`}
                          />
                          {renderValidationIcon('cedula')}
                        </div>
                        {errorsStep3.cedula && (
                          <p className="mt-1 text-sm text-red-600">{errorsStep3.cedula.message}</p>
                        )}
                      </div>

                      {/* Dirección */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Dirección de Entrega *
                        </label>
                        <div className="relative">
                          <input
                            {...registerStep3('direccion')}
                            type="text"
                            placeholder="Calle 123 #45-67, Barrio Centro"
                            className={`w-full px-4 py-3 rounded-lg border ${getInputBorderClass('direccion')} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white font-medium`}
                          />
                          {renderValidationIcon('direccion')}
                        </div>
                        {errorsStep3.direccion && (
                          <p className="mt-1 text-sm text-red-600">{errorsStep3.direccion.message}</p>
                        )}
                      </div>

                      {/* Ciudad y Departamento */}
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Ciudad *
                          </label>
                          <div className="relative">
                            <input
                              {...registerStep3('ciudad')}
                              type="text"
                              placeholder="Bucaramanga"
                              className={`w-full px-4 py-3 rounded-lg border ${getInputBorderClass('ciudad')} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white font-medium`}
                            />
                            {renderValidationIcon('ciudad')}
                          </div>
                          {errorsStep3.ciudad && (
                            <p className="mt-1 text-sm text-red-600">{errorsStep3.ciudad.message}</p>
                          )}
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Departamento *
                          </label>
                          <div className="relative">
                            <select
                              {...registerStep3('departamento')}
                              className={`w-full px-4 py-3 rounded-lg border ${getInputBorderClass('departamento')} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 bg-white font-medium`}
                            >
                              <option value="">Seleccionar</option>
                              <option value="santander">Santander</option>
                              <option value="cundinamarca">Cundinamarca</option>
                              <option value="antioquia">Antioquia</option>
                              <option value="valle">Valle del Cauca</option>
                              <option value="atlantico">Atlántico</option>
                            </select>
                          </div>
                          {errorsStep3.departamento && (
                            <p className="mt-1 text-sm text-red-600">{errorsStep3.departamento.message}</p>
                          )}
                        </div>
                      </div>
                    </>
                  )}

                  {/* FORMULARIO PARA VENDEDORES */}
                  {selectedRole === UserType.VENDEDOR && (
                    <>
                      {/* Tipo de Vendedor */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-3">
                          Tipo de Vendedor *
                        </label>
                        <div className="grid grid-cols-2 gap-4">
                          <div
                            onClick={() => setValueStep3('tipo_vendedor', 'persona_juridica')}
                            className={`p-6 rounded-lg border-2 cursor-pointer transition-all ${
                              watchedFieldsStep3.tipo_vendedor === 'persona_juridica'
                                ? 'border-blue-500 bg-blue-50 shadow-lg transform scale-105'
                                : 'border-gray-300 hover:border-blue-300 hover:shadow-md bg-white'
                            }`}
                          >
                            <div className="text-center">
                              <div className={`w-12 h-12 mx-auto mb-3 rounded-full flex items-center justify-center ${
                                watchedFieldsStep3.tipo_vendedor === 'persona_juridica' ? 'bg-blue-100' : 'bg-gray-100'
                              }`}>
                                <svg className={`w-6 h-6 ${
                                  watchedFieldsStep3.tipo_vendedor === 'persona_juridica' ? 'text-blue-600' : 'text-gray-600'
                                }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                                </svg>
                              </div>
                              <h4 className="font-bold text-black text-base mb-1">Persona Jurídica</h4>
                              <p className="text-sm text-gray-700 font-medium">Tengo empresa constituida</p>
                              {watchedFieldsStep3.tipo_vendedor === 'persona_juridica' && (
                                <div className="mt-3 w-6 h-6 mx-auto bg-blue-500 rounded-full flex items-center justify-center">
                                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                  </svg>
                                </div>
                              )}
                            </div>
                          </div>
                          <div
                            onClick={() => setValueStep3('tipo_vendedor', 'persona_natural')}
                            className={`p-6 rounded-lg border-2 cursor-pointer transition-all ${
                              watchedFieldsStep3.tipo_vendedor === 'persona_natural'
                                ? 'border-green-500 bg-green-50 shadow-lg transform scale-105'
                                : 'border-gray-300 hover:border-green-300 hover:shadow-md bg-white'
                            }`}
                          >
                            <div className="text-center">
                              <div className={`w-12 h-12 mx-auto mb-3 rounded-full flex items-center justify-center ${
                                watchedFieldsStep3.tipo_vendedor === 'persona_natural' ? 'bg-green-100' : 'bg-gray-100'
                              }`}>
                                <svg className={`w-6 h-6 ${
                                  watchedFieldsStep3.tipo_vendedor === 'persona_natural' ? 'text-green-600' : 'text-gray-600'
                                }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                </svg>
                              </div>
                              <h4 className="font-bold text-black text-base mb-1">Persona Natural</h4>
                              <p className="text-sm text-gray-700 font-medium">Vendo como persona natural</p>
                              {watchedFieldsStep3.tipo_vendedor === 'persona_natural' && (
                                <div className="mt-3 w-6 h-6 mx-auto bg-green-500 rounded-full flex items-center justify-center">
                                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                  </svg>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                        {errorsStep3.tipo_vendedor && (
                          <p className="mt-1 text-sm text-red-600">{errorsStep3.tipo_vendedor.message}</p>
                        )}
                      </div>

                      {/* Campos para Persona Jurídica */}
                      {watchedFieldsStep3.tipo_vendedor === 'persona_juridica' && (
                        <>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Nombre de la Empresa *
                            </label>
                            <div className="relative">
                              <input
                                {...registerStep3('nombre_empresa')}
                                type="text"
                                placeholder="Mi Empresa S.A.S"
                                className={`w-full px-4 py-3 rounded-lg border ${getInputBorderClass('nombre_empresa')} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white font-medium`}
                              />
                              {renderValidationIcon('nombre_empresa')}
                            </div>
                            {errorsStep3.nombre_empresa && (
                              <p className="mt-1 text-sm text-red-600">{errorsStep3.nombre_empresa.message}</p>
                            )}
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              NIT *
                            </label>
                            <div className="relative">
                              <input
                                {...registerStep3('nit')}
                                type="text"
                                placeholder="123456789-0"
                                onInput={(e) => {
                                  const target = e.target as HTMLInputElement;
                                  let value = target.value.replace(/[^\d-]/g, '');
                                  if (value.length === 9 && !value.includes('-')) {
                                    value = value + '-';
                                  }
                                  target.value = value;
                                }}
                                maxLength={11}
                                className={`w-full px-4 py-3 rounded-lg border ${getInputBorderClass('nit')} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white font-medium`}
                              />
                              {renderValidationIcon('nit')}
                            </div>
                            {errorsStep3.nit && (
                              <p className="mt-1 text-sm text-red-600">{errorsStep3.nit.message}</p>
                            )}
                          </div>
                        </>
                      )}

                      {/* Dirección Fiscal */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Dirección Fiscal *
                        </label>
                        <div className="relative">
                          <input
                            {...registerStep3('direccion_fiscal')}
                            type="text"
                            placeholder="Carrera 27 #123-45, Centro"
                            className={`w-full px-4 py-3 rounded-lg border ${getInputBorderClass('direccion_fiscal')} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white font-medium`}
                          />
                          {renderValidationIcon('direccion_fiscal')}
                        </div>
                        {errorsStep3.direccion_fiscal && (
                          <p className="mt-1 text-sm text-red-600">{errorsStep3.direccion_fiscal.message}</p>
                        )}
                      </div>

                      {/* Ciudad y Departamento Fiscal */}
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Ciudad Fiscal *
                          </label>
                          <div className="relative">
                            <input
                              {...registerStep3('ciudad_fiscal')}
                              type="text"
                              placeholder="Bucaramanga"
                              className={`w-full px-4 py-3 rounded-lg border ${getInputBorderClass('ciudad_fiscal')} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white font-medium`}
                            />
                            {renderValidationIcon('ciudad_fiscal')}
                          </div>
                          {errorsStep3.ciudad_fiscal && (
                            <p className="mt-1 text-sm text-red-600">{errorsStep3.ciudad_fiscal.message}</p>
                          )}
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Departamento Fiscal *
                          </label>
                          <div className="relative">
                            <select
                              {...registerStep3('departamento_fiscal')}
                              className={`w-full px-4 py-3 rounded-lg border ${getInputBorderClass('departamento_fiscal')} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 bg-white font-medium`}
                            >
                              <option value="">Seleccionar</option>
                              <option value="santander">Santander</option>
                              <option value="cundinamarca">Cundinamarca</option>
                              <option value="antioquia">Antioquia</option>
                              <option value="valle">Valle del Cauca</option>
                              <option value="atlantico">Atlántico</option>
                            </select>
                          </div>
                          {errorsStep3.departamento_fiscal && (
                            <p className="mt-1 text-sm text-red-600">{errorsStep3.departamento_fiscal.message}</p>
                          )}
                        </div>
                      </div>
                    </>
                  )}

                  {/* Botones de navegación */}
                  <div className="flex space-x-4">
                    <button
                      type="button"
                      onClick={prevStep}
                      className="flex-1 py-3 px-4 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      Atrás
                    </button>
                    <button
                      type="submit"
                      disabled={!isValidStep3 || loading}
                      className={`flex-1 py-3 px-4 rounded-lg font-medium text-white transition-all duration-200 ${
                        isValidStep3 && !loading
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
                  </div>
                </form>
              )}

              {/* Link a login */}
              <div className="text-center mt-6 pt-6 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => navigate('/login')}
                  className="text-blue-600 hover:text-blue-800 font-medium transition-colors"
                >
                  ¿Ya tienes cuenta? Inicia sesión
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* LADO DERECHO: Visual 3D con branding MeStocker (50%) - MANTIENE DISEÑO ORIGINAL */}
        <div className="hidden lg:flex items-center justify-center bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 relative overflow-hidden">
          {/* Elementos de fondo 3D */}
          <div className="absolute inset-0">
            <div className="absolute top-20 left-20 w-32 h-32 bg-white/10 rounded-full blur-xl animate-pulse"></div>
            <div className="absolute bottom-32 right-16 w-24 h-24 bg-white/15 rounded-full blur-lg animate-pulse delay-300"></div>
            <div className="absolute top-1/2 left-16 w-16 h-16 bg-white/20 rounded-full blur-md animate-pulse delay-700"></div>
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:50px_50px]"></div>
          </div>

          {/* Contenido principal 3D */}
          <div className="relative z-10 text-center text-white p-12 max-w-lg">
            <div className="mb-8">
              <div className="mx-auto w-24 h-24 bg-white/20 backdrop-blur rounded-3xl flex items-center justify-center mb-6 shadow-2xl transform rotate-3 hover:rotate-0 transition-transform duration-500">
                <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <h1 className="text-4xl font-bold mb-2">MeStocker</h1>
              <p className="text-xl text-blue-100">Tu almacén digital</p>
            </div>

            <div className="space-y-6">
              <div className="flex justify-center space-x-4 mb-8">
                <div className="w-16 h-16 bg-gradient-to-br from-white/30 to-white/10 rounded-lg transform rotate-12 shadow-2xl backdrop-blur border border-white/20 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                  </svg>
                </div>
                <div className="w-16 h-16 bg-gradient-to-br from-white/25 to-white/5 rounded-lg transform -rotate-6 shadow-xl backdrop-blur border border-white/20 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="w-16 h-16 bg-gradient-to-br from-white/35 to-white/15 rounded-lg transform rotate-3 shadow-2xl backdrop-blur border border-white/20 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
              </div>

              <div className="space-y-4 text-left">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-white/90">Gestión inteligente de inventario</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <span className="text-white/90">Ventas automatizadas 24/7</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                  <span className="text-white/90">Pagos seguros garantizados</span>
                </div>
              </div>

              <div className="mt-8 p-4 bg-white/10 backdrop-blur rounded-xl border border-white/20">
                <p className="text-white/90 text-sm">
                  Únete a más de <span className="font-bold text-white">2,000+</span> empresas que confían en MeStocker
                </p>
              </div>
            </div>
          </div>

          {/* Efecto de partículas flotantes */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute top-10 left-10 w-2 h-2 bg-white/30 rounded-full animate-ping"></div>
            <div className="absolute top-1/3 right-20 w-1 h-1 bg-white/40 rounded-full animate-ping delay-1000"></div>
            <div className="absolute bottom-20 left-1/3 w-1.5 h-1.5 bg-white/35 rounded-full animate-ping delay-500"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterVendor;