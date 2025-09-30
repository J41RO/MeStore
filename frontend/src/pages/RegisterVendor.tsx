import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { UserType } from '../stores/authStore';
import { GoogleLogin } from '@react-oauth/google';
import { FaFacebook } from 'react-icons/fa';
// import ImageUpload from '../components/ui/ImageUpload/ImageUpload';
import type { ImageFile } from '../components/ui/ImageUpload/ImageUpload.types';

// Schema de validación para datos básicos (Paso 1)
const createBasicDataSchema = (isOAuthUser: boolean) => yup.object({
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
    .test('valid-phone', 'Formato de teléfono inválido', function(value) {
      if (!value) return false;
      // Colombia format: 300 123 4567 (10 digits)
      // US format: 555 123 4567 (10 digits)
      return /^\d{3}\s\d{3}\s\d{4}$/.test(value);
    }),
  password: isOAuthUser
    ? yup.string().optional()
    : yup
        .string()
        .required('Contraseña es requerida')
        .min(8, 'La contraseña debe tener al menos 8 caracteres')
        .matches(
          /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])/,
          'La contraseña debe contener al menos: 1 mayúscula, 1 minúscula, 1 número y 1 carácter especial'
        ),
  confirmPassword: isOAuthUser
    ? yup.string().optional()
    : yup
        .string()
        .required('Confirmar contraseña es requerida')
        .oneOf([yup.ref('password')], 'Las contraseñas deben coincidir'),
});

// Tipo unificado para formulario Paso 3 (compradores y vendedores)
interface Step3FormData {
  // Campos para COMPRADOR
  cedula?: string;
  direccion?: string;
  ciudad?: string;
  departamento?: string;
  
  // Campos para VENDEDOR
  tipo_vendedor?: 'persona_juridica' | 'persona_natural';
  nombre_empresa?: string;
  nit?: string;
  direccion_fiscal?: string;
  ciudad_fiscal?: string;
  departamento_fiscal?: string;
}

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
  const [currentStep, setCurrentStep] = useState<1 | 2 | 3 | 4>(1);
  const [basicFormData, setBasicFormData] = useState<any>(null);
  const [selectedRole, setSelectedRole] = useState<UserType | null>(null);
  const [specificData, setSpecificData] = useState<any>(null);
  const [documentsData, setDocumentsData] = useState<{[key: string]: ImageFile[]}>({});
  const [otpVerified, setOtpVerified] = useState(false);
  const [loading, setLoading] = useState(false);
  const [oauthLoading, setOauthLoading] = useState<'google' | 'facebook' | null>(null);
  const [registrationError, setRegistrationError] = useState<string>('');
  const [isOAuthUser, setIsOAuthUser] = useState(false);

  // Country code selector state
  const [selectedCountry, setSelectedCountry] = useState({
    code: 'CO',
    prefix: '+57',
    flag: '🇨🇴',
    name: 'Colombia'
  });

  // Available countries for phone registration
  const availableCountries = [
    { code: 'CO', prefix: '+57', flag: '🇨🇴', name: 'Colombia' },
    { code: 'US', prefix: '+1', flag: '🇺🇸', name: 'Estados Unidos' },
  ];

  const [isCountryDropdownOpen, setIsCountryDropdownOpen] = useState(false);

  // OTP code state
  const [otpCode, setOtpCode] = useState(['', '', '', '', '', '']);
  const [otpError, setOtpError] = useState('');
  const [smsSent, setSmsSent] = useState(false);
  const [smsLoading, setSmsLoading] = useState(false);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (isCountryDropdownOpen && !target.closest('.country-selector')) {
        setIsCountryDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isCountryDropdownOpen]);

  // No enviar SMS automáticamente por ahora - requiere estar registrado primero
  // useEffect(() => {
  //   if (currentStep === 3 && !smsSent && !smsLoading && basicFormData?.telefono) {
  //     sendSMSVerification();
  //   }
  // }, [currentStep, smsSent, smsLoading, basicFormData?.telefono]);

  // Form para Paso 1 - Datos básicos
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    watch,
    setValue,
  } = useForm({
    resolver: yupResolver(createBasicDataSchema(isOAuthUser)),
    mode: 'onChange',
  });

  // Form para Paso 3 - Datos específicos
  const {
    register: registerStep3,
    handleSubmit: handleSubmitStep3,
    formState: { errors: errorsStep3, isValid: isValidStep3 },
    watch: watchStep3,
    setValue: setValueStep3,
  } = useForm<Step3FormData>({
    resolver: yupResolver(
      yup.lazy(() => selectedRole === UserType.BUYER ? compradorSchema : vendedorSchema) as any
    ),
    mode: 'onChange',
  });

  const watchedFields = watch();
  const watchedFieldsStep3 = watchStep3();

  // Funciones de navegación entre pasos
  const nextStep = () => {
    if (currentStep === 1 && isValid) {
      setCurrentStep(2);
    } else if (currentStep === 2) {
      setCurrentStep(3);
    } else if (currentStep === 3 && otpVerified) {
      setCurrentStep(4);
    }
  };

  const prevStep = () => {
    if (currentStep === 2) {
      setCurrentStep(1);
    } else if (currentStep === 3) {
      setCurrentStep(2);
    } else if (currentStep === 4) {
      setCurrentStep(3);
    }
  };

  // Funciones OAuth
  const handleGoogleSuccess = async (credentialResponse: any) => {
    setOauthLoading('google');
    try {
      console.log('Google OAuth Success:', credentialResponse);

      // Llamar a nuestro backend para verificar el token de Google
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/google/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id_token: credentialResponse.credential,
          user_type: 'VENDOR' // Siempre registro como vendor en esta página
        }),
      });

      const data = await response.json();

      if (data.success && data.user) {
        // Pre-llenar formulario con datos reales de Google
        const fullName = `${data.user.nombre || ''} ${data.user.apellido || ''}`.trim();
        setValue('nombre', fullName);
        setValue('email', data.user.email);

        // Marcar como usuario OAuth
        setIsOAuthUser(true);

        // Mostrar mensaje de éxito
        alert(`¡Bienvenido ${fullName}! Datos de Google cargados. Por favor completa el número de teléfono para continuar con el registro.`);

      } else {
        throw new Error(data.message || 'Error en la respuesta del servidor');
      }

    } catch (error) {
      console.error('Error en autenticación con Google:', error);
      alert('Error al conectar con Google. Intenta nuevamente.');
    } finally {
      setOauthLoading(null);
    }
  };

  const handleGoogleError = (error: any) => {
    console.error('Error en Google OAuth:', error);
    console.error('Error details:', JSON.stringify(error, null, 2));

    // Información adicional para debugging
    console.log('Current URL:', window.location.href);
    console.log('Client ID from env:', import.meta.env.VITE_GOOGLE_CLIENT_ID);

    // Análisis específico de errores comunes
    let errorMessage = 'Error desconocido';

    if (error?.error === 'popup_blocked') {
      errorMessage = 'El popup fue bloqueado por el navegador. Permite popups y reintenta.';
    } else if (error?.error === 'access_denied') {
      errorMessage = 'Acceso denegado por el usuario.';
    } else if (typeof error === 'string' && error.includes('400')) {
      errorMessage = `Error 400: URL no autorizada en Google Cloud Console.

🚨 SOLUCIÓN REQUERIDA:
1. Ve a https://console.cloud.google.com/apis/credentials
2. Busca el proyecto con Client ID: ${import.meta.env.VITE_GOOGLE_CLIENT_ID}
3. En "Orígenes de JavaScript autorizados", agrega:
   - http://192.168.1.137:5173
4. En "URIs de redirección autorizados", agrega:
   - http://192.168.1.137:5173
5. Guarda los cambios y espera unos minutos.

ALTERNATIVA INMEDIATA: Usa localhost:5173 en lugar de 192.168.1.137:5173`;
    } else if (error?.error) {
      errorMessage = `Error de Google OAuth: ${error.error}`;
    } else {
      errorMessage = `Error al conectar con Google: ${error?.error || 'Error desconocido'}. Revisa la consola para más detalles.`;
    }

    console.error('🚨 DIAGNÓSTICO DEL ERROR:', errorMessage);
    alert(errorMessage);
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

  // Manejar datos del Paso 1
  const handleBasicDataSubmit = (data: any) => {
    setRegistrationError(''); // Clear any previous registration errors
    setBasicFormData(data);
    nextStep();
  };

  // Manejar upload de documentos (Paso 2)
  const handleDocumentUpload = (documentType: string, files: ImageFile[]) => {
    setDocumentsData(prev => ({
      ...prev,
      [documentType]: files
    }));
  };

  // Función para enviar SMS real al backend - AHORA CON AUTENTICACIÓN
  const sendSMSVerification = async () => {
    if (!basicFormData?.telefono) {
      setOtpError('No se encontró número de teléfono');
      return;
    }

    const token = localStorage.getItem('temp_access_token');
    if (!token) {
      setOtpError('Error: No hay token de autenticación. Reinicia el proceso.');
      return;
    }

    setSmsLoading(true);
    setOtpError('');

    try {
      const fullPhoneNumber = `${selectedCountry.prefix}${basicFormData.telefono.replace(/\s/g, '')}`;

      const response = await fetch('http://192.168.1.137:8000/api/v1/auth/send-verification-sms', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          phone_number: fullPhoneNumber,
          otp_type: 'SMS'
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ SMS enviado exitosamente:', result);
        setSmsSent(true);
        setOtpError('');
      } else {
        const errorData = await response.json();
        console.error('❌ Error enviando SMS:', errorData);
        setOtpError('Error enviando SMS. Intenta nuevamente.');
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      setOtpError('Error de conexión. Verifica tu internet.');
    } finally {
      setSmsLoading(false);
    }
  };

  // Continuar al paso 3 después de subir documentos - AHORA REGISTRA PRIMERO
  const handleDocumentsSubmit = async () => {
    if (!basicFormData) return;

    setLoading(true);
    try {
      // Crear el usuario primero para poder enviar SMS
      const registrationData = {
        email: basicFormData.email,
        password: basicFormData.password,
        nombre: basicFormData.nombre,
        telefono: `${selectedCountry.prefix}${basicFormData.telefono.replace(/\s/g, '')}`,
        user_type: 'VENDOR'
      };

      console.log('🚀 Registrando usuario para SMS verification:', registrationData);

      const response = await fetch('http://192.168.1.137:8000/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registrationData),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Usuario registrado para SMS:', result);

        // Guardar token para usar en SMS
        if (result.access_token) {
          localStorage.setItem('temp_access_token', result.access_token);
        }

        // Avanzar al paso 3 donde ahora sí podremos enviar SMS
        nextStep();
      } else if (response.status === 400) {
        // Si el usuario ya existe, intentar login en su lugar
        console.log('⚠️ Usuario ya existe, intentando login...');
        try {
          const loginResponse = await fetch('http://192.168.1.137:8000/api/v1/auth/login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              email: basicFormData.email,
              password: basicFormData.password
            }),
          });

          if (loginResponse.ok) {
            const loginResult = await loginResponse.json();
            console.log('✅ Login exitoso para usuario existente:', loginResult);

            // Guardar token para usar en SMS
            if (loginResult.access_token) {
              localStorage.setItem('temp_access_token', loginResult.access_token);
            }

            // Avanzar al paso 3 donde ahora sí podremos enviar SMS
            nextStep();
          } else {
            const loginErrorData = await loginResponse.json();
            console.error('❌ Error en login fallback:', loginErrorData);
            setRegistrationError(`El email ${basicFormData.email} ya existe pero la contraseña no coincide. Opciones:\n1. Verifica tu contraseña actual\n2. Usa un email diferente (ej: ${basicFormData.email.replace('@', '.test@')})\n3. Contacta soporte si olvidaste tu contraseña`);
          }
        } catch (loginError) {
          console.error('Error en login fallback:', loginError);
          setRegistrationError('Usuario ya registrado. Verifica tu contraseña o usa otra email.');
        }
      } else {
        const errorData = await response.json();
        console.error('❌ Error en pre-registro:', errorData);
        setRegistrationError('Error en el registro. Intenta nuevamente.');
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      setRegistrationError('Error de conexión. Verifica tu internet.');
    } finally {
      setLoading(false);
    }
  };

  // Handle OTP digit input
  const handleOtpInput = (index: number, value: string) => {
    if (value.length > 1) return; // Only allow single digit

    const newOtpCode = [...otpCode];
    newOtpCode[index] = value;
    setOtpCode(newOtpCode);
    setOtpError(''); // Clear error when user types

    // Auto-focus next input
    if (value && index < 5) {
      const nextInput = document.querySelector(`input[data-otp-index="${index + 1}"]`) as HTMLInputElement;
      if (nextInput) nextInput.focus();
    }
  };

  // Handle backspace in OTP input
  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !otpCode[index] && index > 0) {
      const prevInput = document.querySelector(`input[data-otp-index="${index - 1}"]`) as HTMLInputElement;
      if (prevInput) prevInput.focus();
    }
  };

  // Manejar verificación OTP (Paso 3) - Updated with validation
  const handleOTPVerification = () => {
    const enteredCode = otpCode.join('');
    const validCode = '123456'; // Bypass code for testing

    if (enteredCode.length !== 6) {
      setOtpError('Por favor ingresa el código completo de 6 dígitos');
      return;
    }

    if (enteredCode === validCode) {
      // Valid code - show success feedback
      setOtpError('');
      setOtpVerified(true);
      setTimeout(() => {
        nextStep();
      }, 1500);
    } else {
      // Invalid code - show error
      setOtpError('Código incorrecto. Usa 123456 para testing.');
      // Clear the inputs for retry
      setOtpCode(['', '', '', '', '', '']);
      const firstInput = document.querySelector(`input[data-otp-index="0"]`) as HTMLInputElement;
      if (firstInput) firstInput.focus();
    }
  };

  // Manejar selección de rol (Paso 4 - reorganizado)
  const handleRoleSelect = (role: UserType) => {
    // Exclusive selection like radio buttons - always set the selected role
    console.log('🎯 Role selection:', role);
    console.log('📊 Current selectedRole:', selectedRole);
    setRegistrationError(''); // Clear any errors when changing role
    setSelectedRole(role);
  };

  // Manejar datos del Paso 4 (específicos según rol)
  const handleSpecificDataSubmit = (data: any) => {
    setSpecificData(data);
    handleFinalSubmit(data);
  };

  // Envío final - AHORA ACTUALIZA EL USUARIO EXISTENTE
  const handleFinalSubmit = async (step3Data?: any) => {
    if (!basicFormData || !selectedRole) return;

    const token = localStorage.getItem('temp_access_token');
    if (!token) {
      setRegistrationError('Error: Usuario no registrado. Reinicia el proceso.');
      return;
    }

    setLoading(true);
    try {
      // Actualizar el user_type y datos específicos del usuario existente
      const updateData = {
        user_type: selectedRole?.toUpperCase(),
        ...specificData,
        ...step3Data
      };

      console.log('🚀 Actualizando usuario con rol:', updateData);

      // Por ahora simulamos éxito ya que el usuario ya está registrado
      console.log('✅ Usuario actualizado exitosamente con rol:', selectedRole);

      // Limpiar token temporal
      localStorage.removeItem('temp_access_token');

      setRegistrationError('');
      navigate('/login', {
        state: {
          email: basicFormData.email,
          message: 'Registro completado exitosamente. Por favor inicia sesión.'
        }
      });

      /* TODO: Implementar endpoint para actualizar usuario existente
      const response = await fetch('http://192.168.1.137:8000/api/v1/auth/update-profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(updateData),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Usuario actualizado:', result);
        setRegistrationError('');
        navigate('/login', { state: { email: basicFormData.email, message: 'Registro completado exitosamente.' } });
      } else {
        const errorData = await response.json();
        console.error('❌ Error actualizando usuario:', errorData);
        setRegistrationError('Error actualizando perfil. Inténtalo nuevamente.');
      }
      */

    } catch (error) {
      console.error('Error de conexión:', error);
      setRegistrationError('Error de conexión. Verifica tu internet e inténtalo nuevamente.');
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
              <div className="flex items-center space-x-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${currentStep >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
                  1
                </div>
                <div className="w-4 border-t-2 border-gray-300"></div>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${currentStep >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
                  2
                </div>
                <div className="w-4 border-t-2 border-gray-300"></div>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${currentStep >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
                  3
                </div>
                <div className="w-4 border-t-2 border-gray-300"></div>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${currentStep >= 4 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
                  4
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
                {currentStep === 2 && 'Sube los documentos requeridos'}
                {currentStep === 3 && 'Verifica tu número de teléfono'}
                {currentStep === 4 && selectedRole === UserType.BUYER && 'Información para entregas'}
                {currentStep === 4 && selectedRole === UserType.VENDOR && 'Información comercial'}
                {currentStep === 4 && !selectedRole && 'Selecciona cómo quieres usar MeStocker'}
              </p>
            </div>

            {/* Contenido por pasos */}
            <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">

              {/* PASO 1: Datos básicos */}
              {currentStep === 1 && (
                <div className="space-y-6">
                  <div className="text-center mb-6">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Información Básica</h3>
                    <p className="text-gray-600 text-sm">Paso 1 de 4</p>
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
                        <div className="relative country-selector">
                          <button
                            type="button"
                            onClick={() => setIsCountryDropdownOpen(!isCountryDropdownOpen)}
                            className="flex items-center bg-gray-50 border border-r-0 border-gray-300 rounded-l-lg px-3 py-3 hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                          >
                            <span className="text-sm font-medium text-gray-700 mr-1">{selectedCountry.flag}</span>
                            <span className="text-sm text-gray-600 mr-1">{selectedCountry.prefix}</span>
                            <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                          </button>

                          {isCountryDropdownOpen && (
                            <div className="absolute top-full left-0 z-10 mt-1 bg-white border border-gray-200 rounded-md shadow-lg min-w-48">
                              {availableCountries.map((country) => (
                                <button
                                  key={country.code}
                                  type="button"
                                  onClick={() => {
                                    setSelectedCountry(country);
                                    setIsCountryDropdownOpen(false);
                                    // Update placeholder based on country
                                    const phoneInput = document.querySelector('input[name="telefono"]') as HTMLInputElement;
                                    if (phoneInput) {
                                      phoneInput.placeholder = country.code === 'US' ? '555 123 4567' : '300 123 4567';
                                      phoneInput.value = ''; // Clear current input
                                    }
                                  }}
                                  className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center transition-colors"
                                >
                                  <span className="mr-2">{country.flag}</span>
                                  <span className="mr-2 text-sm font-medium">{country.prefix}</span>
                                  <span className="text-sm text-gray-600">{country.name}</span>
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                        <input
                          {...register('telefono')}
                          type="tel"
                          placeholder={selectedCountry.code === 'US' ? '555 123 4567' : '300 123 4567'}
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

                    {/* Contraseña - Solo mostrar si no es usuario OAuth */}
                    {!isOAuthUser && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Contraseña *
                        </label>
                        <div className="relative">
                          <input
                            {...register('password')}
                            type="password"
                            placeholder="Mínimo 8 caracteres"
                            className={`w-full px-4 py-3 rounded-lg border ${getInputBorderClass('password', errors, watchedFields)} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white font-medium`}
                          />
                          {renderValidationIcon('password', errors, watchedFields)}
                        </div>
                        {errors.password && (
                          <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
                        )}
                      </div>
                    )}

                    {/* Confirmar Contraseña - Solo mostrar si no es usuario OAuth */}
                    {!isOAuthUser && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Confirmar Contraseña *
                        </label>
                        <div className="relative">
                          <input
                            {...register('confirmPassword')}
                            type="password"
                            placeholder="Repite tu contraseña"
                            className={`w-full px-4 py-3 rounded-lg border ${getInputBorderClass('confirmPassword', errors, watchedFields)} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white font-medium`}
                          />
                          {renderValidationIcon('confirmPassword', errors, watchedFields)}
                        </div>
                        {errors.confirmPassword && (
                          <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
                        )}
                      </div>
                    )}

                    {/* Mensaje informativo para usuarios OAuth */}
                    {isOAuthUser && (
                      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                        <div className="flex items-center">
                          <svg className="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                          </svg>
                          <p className="text-sm text-green-800">
                            ¡Perfecto! Te has autenticado con Google. No necesitas crear una contraseña.
                          </p>
                        </div>
                      </div>
                    )}

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

              {/* PASO 2: Upload de documentos */}
              {currentStep === 2 && (
                <div className="space-y-6">
                  <div className="text-center mb-6">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Documentos Requeridos</h3>
                    <p className="text-gray-600 text-sm">Paso 2 de 4</p>
                  </div>

                  {/* Upload de documentos simplificado para evitar errores */}
                  <div className="space-y-6">
                    <div className="p-6 border-2 border-dashed border-blue-300 rounded-lg text-center">
                      <div className="mb-4">
                        <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                          <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      </div>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">Subir Documentos</h3>
                      <p className="text-gray-600 mb-4">
                        Por favor sube los siguientes documentos requeridos:
                      </p>
                      
                      <div className="space-y-3 text-sm text-gray-600">
                        <div className="flex items-center justify-center space-x-2">
                          <span>📄</span>
                          <span>Cédula de Ciudadanía (ambos lados)</span>
                        </div>
                        <div className="flex items-center justify-center space-x-2">
                          <span>📋</span>
                          <span>RUT (solo personas jurídicas)</span>
                        </div>
                        <div className="flex items-center justify-center space-x-2">
                          <span>🏦</span>
                          <span>Certificado Bancario (solo vendedores)</span>
                        </div>
                      </div>
                      
                      <div className="mt-6">
                        <input
                          type="file"
                          multiple
                          accept="image/*,.pdf"
                          onChange={(e) => {
                            const files = Array.from(e.target.files || []);
                            if (files.length > 0) {
                              const imageFiles: ImageFile[] = files.map((file, index) => ({
                                file,
                                preview: URL.createObjectURL(file),
                                id: `${Date.now()}-${index}`
                              }));
                              handleDocumentUpload('mixed', imageFiles);
                            }
                          }}
                          className="hidden"
                          id="document-upload"
                        />
                        <label
                          htmlFor="document-upload"
                          className="cursor-pointer inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                        >
                          Seleccionar Archivos
                        </label>
                      </div>
                      
                      {Object.keys(documentsData).length > 0 && (
                        <div className="mt-4 p-3 bg-green-50 rounded-lg">
                          <p className="text-green-800 text-sm">
                            ✅ {Object.keys(documentsData).length} documento(s) subido(s)
                          </p>
                        </div>
                      )}
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
                      onClick={handleDocumentsSubmit}
                      className="flex-1 py-3 px-4 rounded-lg font-medium text-white transition-all duration-200 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                    >
                      Continuar al Paso 3
                    </button>
                  </div>
                </div>
              )}

              {/* PASO 3: Verificación OTP */}
              {currentStep === 3 && (
                <div className="space-y-6">
                  <div className="text-center mb-6">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Verificación de Teléfono</h3>
                    <p className="text-gray-600 text-sm">Paso 3 de 4</p>
                  </div>

                  <div className="max-w-md mx-auto text-center">
                    <div className="mb-6">
                      <div className={`mx-auto w-16 h-16 rounded-full flex items-center justify-center mb-4 ${
                        smsLoading ? 'bg-yellow-100' : smsSent ? 'bg-green-100' : 'bg-blue-100'
                      }`}>
                        {smsLoading ? (
                          <svg className="animate-spin w-8 h-8 text-yellow-600" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                        ) : smsSent ? (
                          <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        ) : (
                          <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                          </svg>
                        )}
                      </div>
                      <p className="text-gray-600 mb-4">
                        {smsLoading ? 'Enviando código de verificación...' :
                         smsSent ? '✅ Código de verificación enviado a tu teléfono' :
                         'Haz clic en el botón para recibir tu código de verificación'}
                      </p>
                      <p className="font-semibold text-gray-900 mb-4">
                        {basicFormData?.telefono ? `${selectedCountry.prefix} ${basicFormData.telefono}` : `${selectedCountry.prefix} XXX XXX XXXX`}
                      </p>

                      {/* Botón para enviar SMS manualmente */}
                      {!smsSent && (
                        <div className="mb-6">
                          <button
                            onClick={sendSMSVerification}
                            disabled={smsLoading}
                            className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
                              smsLoading
                                ? 'bg-gray-400 cursor-not-allowed text-white'
                                : 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                            }`}
                          >
                            {smsLoading ? 'Enviando...' : '📱 Enviar Código SMS'}
                          </button>
                        </div>
                      )}
                    </div>

                    {/* Simulación de campos OTP */}
                    <div className="flex justify-center space-x-3 mb-6">
                      {[0, 1, 2, 3, 4, 5].map((index) => (
                        <input
                          key={index}
                          data-otp-index={index}
                          type="text"
                          inputMode="numeric"
                          maxLength={1}
                          value={otpCode[index]}
                          onChange={(e) => handleOtpInput(index, e.target.value.replace(/\D/g, ''))}
                          onKeyDown={(e) => handleOtpKeyDown(index, e)}
                          className="w-12 h-12 text-center text-xl font-bold border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                          placeholder="0"
                        />
                      ))}
                    </div>

                    {/* Error message */}
                    {otpError && (
                      <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                        <p className="text-red-600 text-sm text-center">{otpError}</p>
                      </div>
                    )}

                    {/* Testing hint */}
                    <div className="mb-6 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-blue-600 text-sm text-center">
                        💡 <strong>Testing:</strong> Usa el código <code className="bg-blue-100 px-2 py-1 rounded">123456</code> para probar
                      </p>
                    </div>

                    <p className="text-sm text-gray-500 mb-6">
                      ¿No recibiste el código?{' '}
                      <button
                        onClick={() => {
                          setSmsSent(false);
                          setOtpCode(['', '', '', '', '', '']);
                          setOtpError('');
                          sendSMSVerification();
                        }}
                        disabled={smsLoading}
                        className={`font-medium ${
                          smsLoading
                            ? 'text-gray-400 cursor-not-allowed'
                            : 'text-blue-600 hover:text-blue-800'
                        }`}
                      >
                        {smsLoading ? 'Enviando...' : 'Reenviar'}
                      </button>
                    </p>
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
                      onClick={handleOTPVerification}
                      className="flex-1 py-3 px-4 rounded-lg font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200"
                    >
                      {otpVerified ? (
                        <div className="flex items-center justify-center">
                          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          Verificado
                        </div>
                      ) : (
                        'Verificar Código'
                      )}
                    </button>
                  </div>
                </div>
              )}

              {/* PASO 4: Selección de rol y datos específicos */}
              {currentStep === 4 && (
                <div className="space-y-6">
                  <div className="text-center mb-6">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">{!selectedRole ? 'Selecciona tu Rol' : 'Datos Específicos'}</h3>
                    <p className="text-gray-600 text-sm">Paso 4 de 4</p>
                  </div>

                  {/* Selección de rol */}
                  <div className="space-y-4">
                    {/* Card Vendedor */}
                    <div
                      onClick={() => handleRoleSelect(UserType.VENDOR)}
                      className={`p-6 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                        selectedRole === UserType.VENDOR
                          ? 'border-blue-500 bg-blue-50 shadow-lg transform scale-105'
                          : 'border-gray-200 hover:border-blue-300 hover:shadow-md hover:bg-blue-50'
                      }`}
                    >
                      <div className="flex items-center space-x-4">
                        <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                          selectedRole === UserType.VENDOR ? 'bg-blue-100' : 'bg-gray-100'
                        }`}>
                          <svg className={`w-6 h-6 ${
                            selectedRole === UserType.VENDOR ? 'text-blue-600' : 'text-gray-600'
                          }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                          </svg>
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900">SOY VENDEDOR</h4>
                          <p className="text-sm text-gray-600">Quiero vender mis productos</p>
                        </div>
                        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                          selectedRole === UserType.VENDOR
                            ? 'border-blue-500 bg-blue-500'
                            : 'border-gray-300'
                        }`}>
                          {selectedRole === UserType.VENDOR && (
                            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Card Comprador */}
                    <div
                      onClick={() => handleRoleSelect(UserType.BUYER)}
                      className={`p-6 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                        selectedRole === UserType.BUYER
                          ? 'border-green-500 bg-green-50 shadow-lg transform scale-105'
                          : 'border-gray-200 hover:border-green-300 hover:shadow-md hover:bg-green-50'
                      }`}
                    >
                      <div className="flex items-center space-x-4">
                        <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                          selectedRole === UserType.BUYER ? 'bg-green-100' : 'bg-gray-100'
                        }`}>
                          <svg className={`w-6 h-6 ${
                            selectedRole === UserType.BUYER ? 'text-green-600' : 'text-gray-600'
                          }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                          </svg>
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900">SOY COMPRADOR</h4>
                          <p className="text-sm text-gray-600">Quiero comprar productos</p>
                        </div>
                        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                          selectedRole === UserType.BUYER
                            ? 'border-green-500 bg-green-500'
                            : 'border-gray-300'
                        }`}>
                          {selectedRole === UserType.BUYER && (
                            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Selection confirmation - only show when a role is selected */}
                    {selectedRole && (
                      <div className="mt-6">
                        <div className={`p-4 rounded-lg mb-4 ${
                          selectedRole === UserType.VENDOR ? 'bg-blue-50 border border-blue-200' : 'bg-green-50 border border-green-200'
                        }`}>
                          <div className="flex items-center space-x-3">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                              selectedRole === UserType.VENDOR ? 'bg-blue-500' : 'bg-green-500'
                            }`}>
                              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            </div>
                            <div>
                              <h5 className={`font-semibold ${
                                selectedRole === UserType.VENDOR ? 'text-blue-900' : 'text-green-900'
                              }`}>
                                {selectedRole === UserType.VENDOR ? 'Vendedor seleccionado' : 'Comprador seleccionado'}
                              </h5>
                              <p className={`text-sm ${
                                selectedRole === UserType.VENDOR ? 'text-blue-700' : 'text-green-700'
                              }`}>
                                {selectedRole === UserType.VENDOR ? 'Podrás gestionar tu inventario y ventas' : 'Podrás realizar compras y seguir tus pedidos'}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Datos específicos según el rol seleccionado */}
                  {selectedRole && (
                    <form onSubmit={handleSubmitStep3(handleSpecificDataSubmit)} className="space-y-6">
                      {/* Error de registro */}
                      {registrationError && (
                        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                          <div className="flex items-center">
                            <svg className="w-5 h-5 text-red-600 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <p className="text-red-600 text-sm">{registrationError}</p>
                          </div>
                        </div>
                      )}

                      {/* Los formularios específicos irán aquí */}
                      {selectedRole === UserType.BUYER && (
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

                      {selectedRole === UserType.VENDOR && (
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
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Más campos de vendedor... */}
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

                      {/* Botón de envío para datos específicos */}
                      <div className="flex space-x-4">
                        <button
                          type="button"
                          onClick={() => setSelectedRole(null)}
                          className="flex-1 py-3 px-4 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                        >
                          Cambiar Rol
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

                  {/* Botones de navegación para selección de rol */}
                  {!selectedRole && (
                  <div className="flex space-x-4">
                    <button
                      onClick={prevStep}
                      className="flex-1 py-3 px-4 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      Atrás
                    </button>
                    <div className="flex-1 flex items-center justify-center text-gray-500 text-sm">
                      ↑ Selecciona un rol para continuar
                    </div>
                  </div>
                  )}
                </div>
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