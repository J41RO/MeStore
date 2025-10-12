import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import axios from 'axios';
import {
  ArrowLeft,
  ArrowRight,
  Check,
  AlertCircle,
  Loader2,
  Mail,
  Phone,
  User,
  Lock,
  ShoppingBag,
  Store
} from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================
type UserType = 'BUYER' | 'VENDOR';
type VendorType = 'persona_natural' | 'persona_juridica' | null;

interface LocationState {
  userType: UserType;
  vendorType: VendorType;
}

interface RegistrationData {
  // Step 1: Basic Data
  email: string;
  password: string;
  confirmPassword?: string;
  nombre: string;
  telefono: string;

  // Step 2: Verification data (stored temporarily)
  emailVerified: boolean;
  phoneVerified: boolean;

  // Step 3: Additional Data (based on user type)
  // BUYER fields
  apellido?: string;
  ciudad?: string;
  direccion?: string;

  // VENDOR Natural fields
  cedula?: string;
  departamento?: string;
  direccion_fiscal?: string;
  ciudad_fiscal?: string;
  departamento_fiscal?: string;

  // VENDOR Juridica fields
  razon_social?: string;
  nombre_comercial?: string;
  nit?: string;
  representante_legal?: string;
  cedula_representante?: string;
  email_representante?: string;
  telefono_empresa?: string;
}

interface RegisterResponse {
  success: boolean;
  message: string;
  user_id: string;
  email: string;
  user_type: string;
  account_status: string;
  vendor_status?: string | null;
}

// ============================================================================
// VALIDATION SCHEMAS
// ============================================================================
const step1Schema = yup.object({
  email: yup.string().required('Email requerido').email('Email inválido'),
  password: yup.string().required('Contraseña requerida').min(8, 'Mínimo 8 caracteres'),
  confirmPassword: yup.string().oneOf([yup.ref('password')], 'Las contraseñas no coinciden'),
  nombre: yup.string().required('Nombre requerido'),
  phoneNumber: yup.string().required('Teléfono requerido').matches(/^\d{10}$/, 'Debe tener 10 dígitos')
});

const buyerAdditionalSchema = yup.object({
  apellido: yup.string().required('Apellido requerido'),
  ciudad: yup.string().required('Ciudad requerida'),
  direccion: yup.string().required('Dirección requerida'),
  departamento: yup.string().required('Departamento requerido')
});

const vendorNaturalAdditionalSchema = yup.object({
  apellido: yup.string().required('Apellido requerido'),
  cedula: yup.string().required('Cédula requerida').matches(/^\d{8,10}$/, '8-10 dígitos'),
  direccion: yup.string().required('Dirección requerida'),
  ciudad: yup.string().required('Ciudad requerida'),
  departamento: yup.string().required('Departamento requerido'),
  direccion_fiscal: yup.string().required('Dirección fiscal requerida'),
  ciudad_fiscal: yup.string().required('Ciudad fiscal requerida'),
  departamento_fiscal: yup.string().required('Departamento fiscal requerido')
});

const vendorJuridicaAdditionalSchema = yup.object({
  razon_social: yup.string().required('Razón social requerida'),
  nombre_comercial: yup.string().required('Nombre comercial requerido'),
  nit: yup.string().required('NIT requerido').matches(/^\d{9}-\d$/, 'Formato: 123456789-0'),
  representante_legal: yup.string().required('Representante legal requerido'),
  cedula_representante: yup.string().required('Cédula requerida').matches(/^\d{8,10}$/, '8-10 dígitos'),
  email_representante: yup.string().required('Email requerido').email('Email inválido'),
  telefono_empresa: yup.string().required('Teléfono requerido').matches(/^\+57\d{10}$/, 'Formato: +573001234567'),
  direccion_fiscal: yup.string().required('Dirección fiscal requerida'),
  ciudad_fiscal: yup.string().required('Ciudad fiscal requerida'),
  departamento_fiscal: yup.string().required('Departamento fiscal requerido')
});

// ============================================================================
// MAIN COMPONENT
// ============================================================================
const RegistrationWizard: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState;

  // ========== STATE ==========
  const [currentStep, setCurrentStep] = useState(1);
  const [registrationData, setRegistrationData] = useState<Partial<RegistrationData>>({
    emailVerified: false,
    phoneVerified: false
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Phone number state
  const [countryCode, setCountryCode] = useState('+57'); // Default Colombia

  // Verification states
  const [emailSent, setEmailSent] = useState(false);
  const [emailSending, setEmailSending] = useState(false);
  const [smsCode, setSmsCode] = useState('');
  const [smsSending, setSmsSending] = useState(false);
  const [smsVerifying, setSmsVerifying] = useState(false);
  const [smsError, setSmsError] = useState('');
  const [otpVerified, setOtpVerified] = useState(false);

  // ========== FORM SETUP ==========
  const getCurrentSchema = () => {
    if (currentStep === 1) return step1Schema;
    if (currentStep === 3) {
      if (state?.userType === 'BUYER') return buyerAdditionalSchema;
      if (state?.vendorType === 'persona_natural') return vendorNaturalAdditionalSchema;
      if (state?.vendorType === 'persona_juridica') return vendorJuridicaAdditionalSchema;
    }
    return yup.object({});
  };

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
    trigger
  } = useForm({
    resolver: yupResolver(getCurrentSchema()),
    mode: 'onChange'
  });

  // Redirect if no user type selected
  useEffect(() => {
    if (!state?.userType) {
      navigate('/user-type-selector');
    }
  }, [state, navigate]);

  // Populate form with saved data when step changes
  useEffect(() => {
    if (registrationData) {
      Object.entries(registrationData).forEach(([key, value]) => {
        if (value !== undefined) {
          setValue(key as any, value);
        }
      });
    }
  }, [currentStep, registrationData, setValue]);

  // NOTE: Email verification is sent automatically by backend in Step 4 (final registration)
  // The /send-verification-email endpoint requires JWT auth, so we can't call it here
  // The /register-multi-type endpoint sends email with background tasks automatically
  // useEffect(() => {
  //   if (currentStep === 2 && registrationData.email && !emailSent) {
  //     console.log('🚀 Auto-sending email verification on Step 2 entry');
  //     sendEmailVerification(registrationData.email);
  //   }
  // }, [currentStep, registrationData.email, emailSent]);

  // ========== STEP 1: BASIC DATA ==========
  const handleStep1Submit = async (data: any) => {
    console.log('📝 Step 1 - Saving basic data to state:', data);

    // Combine country code with phone number
    const fullPhoneNumber = `${countryCode}${data.phoneNumber}`;
    console.log('📱 Full phone number:', fullPhoneNumber);

    // Save data to state (NO DB registration yet)
    setRegistrationData(prev => ({
      ...prev,
      email: data.email,
      password: data.password,
      nombre: data.nombre,
      telefono: fullPhoneNumber
    }));

    // Move to verification step (email will be sent automatically by useEffect)
    setCurrentStep(2);
  };

  // ========== STEP 2: VERIFICATIONS ==========
  const sendEmailVerification = async (email: string) => {
    setEmailSending(true);
    setError(null);

    try {
      console.log('📧 Sending email verification to:', email);
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/v1/auth/send-verification-email`,
        { email }
      );

      if (response.data.success) {
        setEmailSent(true);
        console.log('✅ Email verification sent successfully');
      }
    } catch (err: any) {
      console.error('❌ Error sending email verification:', err);
      setError(err.response?.data?.detail || 'Error al enviar email de verificación');
    } finally {
      setEmailSending(false);
    }
  };

  const sendSMSCode = async () => {
    if (!registrationData.telefono) {
      setSmsError('Teléfono no encontrado');
      return;
    }

    setSmsSending(true);
    setSmsError('');

    try {
      console.log('📱 Sending SMS code to:', registrationData.telefono);

      // ⚡ USAR ENDPOINT PÚBLICO (NO requiere autenticación)
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/v1/auth/send-sms-public`,
        null,  // No body
        {
          params: { phone: registrationData.telefono }  // Query param
        }
      );

      if (response.data.success) {
        console.log('✅ SMS sent successfully via Twilio Verify');
        alert('✅ Código SMS enviado exitosamente a tu teléfono. Revisa tus mensajes.');
      }
    } catch (err: any) {
      console.error('❌ Error sending SMS:', err);
      const errorMessage = err.response?.data?.detail || 'Error al enviar SMS. Por favor intenta de nuevo.';
      setSmsError(errorMessage);
      alert(`❌ ${errorMessage}`);
    } finally {
      setSmsSending(false);
    }
  };

  const verifySMSCode = async () => {
    if (!smsCode || smsCode.length !== 6) {
      setSmsError('Código debe tener 6 dígitos');
      return;
    }

    setSmsVerifying(true);
    setSmsError('');

    try {
      console.log('🔍 Verifying SMS code:', smsCode);
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/v1/auth/verify/phone`,
        {
          phone: registrationData.telefono,
          code: smsCode
        }
      );

      if (response.data.success) {
        console.log('✅ SMS code verified successfully');
        setOtpVerified(true);
        setRegistrationData(prev => ({ ...prev, phoneVerified: true }));

        // Auto-advance after 1.5 seconds
        setTimeout(() => {
          setCurrentStep(3);
        }, 1500);
      }
    } catch (err: any) {
      console.error('❌ Error verifying SMS:', err);
      setSmsError(err.response?.data?.detail || 'Código incorrecto o expirado');
      setOtpVerified(false);
    } finally {
      setSmsVerifying(false);
    }
  };

  // Check if email was verified (would be checked via backend polling or callback)
  const checkEmailVerification = async () => {
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL}/api/v1/auth/check-email-verification/${registrationData.email}`
      );

      if (response.data.verified) {
        setRegistrationData(prev => ({ ...prev, emailVerified: true }));
        return true;
      }
      return false;
    } catch (err) {
      console.error('Error checking email verification:', err);
      return false;
    }
  };

  // ========== STEP 3: ADDITIONAL DATA ==========
  const handleStep3Submit = async (data: any) => {
    console.log('📝 Step 3 - Saving additional data to state:', data);

    // Merge additional data
    setRegistrationData(prev => ({
      ...prev,
      ...data
    }));

    // Move to final registration
    setCurrentStep(4);
  };

  // ========== STEP 4: FINAL REGISTRATION ==========
  const handleFinalRegistration = async () => {
    // Verify both verifications are complete
    if (!registrationData.phoneVerified) {
      setError('Debes verificar tu teléfono antes de continuar');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log('🚀 FINAL REGISTRATION - Data being sent:', registrationData);

      // Remove confirmPassword and verification flags before sending
      const { confirmPassword, emailVerified, phoneVerified, ...submitData } = registrationData;

      // Add user type and vendor type
      const finalData = {
        ...submitData,
        user_type: state.userType,
        vendor_type: state.vendorType
      };

      console.log('📤 Sending final registration to backend:', finalData);

      const response = await axios.post<RegisterResponse>(
        `${import.meta.env.VITE_API_URL}/api/v1/auth/register-multi-type`,
        finalData
      );

      if (response.data.success) {
        console.log('✅ Registration successful:', response.data);
        setSuccess(true);

        // Redirect based on user type
        setTimeout(() => {
          if (state.userType === 'BUYER') {
            navigate('/login', {
              state: {
                message: '¡Registro exitoso! Puedes iniciar sesión ahora.',
                email: response.data.email
              }
            });
          } else {
            navigate('/registration-pending', {
              state: {
                message: 'Tu cuenta de vendedor está pendiente de aprobación.',
                email: response.data.email
              }
            });
          }
        }, 3000);
      }
    } catch (err: any) {
      console.error('❌ Registration error:', err);
      const errorMessage = err.response?.data?.error_message ||
                          err.response?.data?.detail ||
                          'Error en el registro. Por favor intenta de nuevo.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // ========== NAVIGATION ==========
  const canProceedToStep3 = registrationData.phoneVerified && registrationData.emailVerified;

  const getTitleForStep = () => {
    const userTypeText = state?.userType === 'BUYER' ? 'Comprador' : 'Vendedor';
    const vendorTypeText = state?.vendorType === 'persona_natural'
      ? '(Persona Natural)'
      : state?.vendorType === 'persona_juridica'
        ? '(Persona Jurídica)'
        : '';

    switch (currentStep) {
      case 1: return `Registro ${userTypeText} ${vendorTypeText} - Paso 1 de 4`;
      case 2: return `Verificación de Contacto - Paso 2 de 4`;
      case 3: return `Información Adicional - Paso 3 de 4`;
      case 4: return `Confirmar Registro - Paso 4 de 4`;
      default: return 'Registro';
    }
  };

  // ========== SUCCESS SCREEN ==========
  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-6">
            <Check className="w-10 h-10 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            ¡Registro Completado!
          </h2>
          <p className="text-gray-600 mb-6">
            {state?.userType === 'BUYER'
              ? 'Tu cuenta de comprador ha sido activada. Ya puedes iniciar sesión.'
              : 'Tu cuenta de vendedor está pendiente de aprobación por el equipo administrativo.'}
          </p>
          <p className="text-sm text-gray-500">
            Redirigiendo...
          </p>
        </div>
      </div>
    );
  }

  // ========== MAIN RENDER ==========
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => {
              if (currentStep === 1) {
                navigate('/user-type-selector');
              } else {
                setCurrentStep(prev => prev - 1);
              }
            }}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Volver</span>
          </button>

          <div className="flex items-center space-x-3 mb-4">
            {state?.userType === 'BUYER' ? (
              <ShoppingBag className="w-8 h-8 text-blue-600" />
            ) : (
              <Store className="w-8 h-8 text-purple-600" />
            )}
            <h1 className="text-3xl font-bold text-gray-900">
              {getTitleForStep()}
            </h1>
          </div>

          {/* Progress Bar */}
          <div className="flex space-x-2">
            {[1, 2, 3, 4].map((step) => (
              <div
                key={step}
                className={`flex-1 h-2 rounded-full transition-all duration-300 ${
                  step <= currentStep ? 'bg-gradient-to-r from-blue-600 to-purple-600' : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {/* Step Content */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* STEP 1: BASIC DATA */}
          {currentStep === 1 && (
            <form onSubmit={handleSubmit(handleStep1Submit)} className="space-y-6">
              <div className="text-center mb-6">
                <User className="w-12 h-12 text-blue-600 mx-auto mb-3" />
                <h2 className="text-xl font-semibold text-gray-900">
                  Datos Básicos
                </h2>
                <p className="text-gray-600 text-sm mt-2">
                  Completa tu información básica para continuar
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre Completo *
                </label>
                <input
                  {...register('nombre')}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Juan Pérez"
                />
                {errors.nombre && (
                  <p className="mt-1 text-sm text-red-600">{errors.nombre.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email *
                </label>
                <input
                  {...register('email')}
                  type="email"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="juan@example.com"
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Teléfono *
                </label>
                <div className="flex space-x-2">
                  {/* Country Code Selector */}
                  <select
                    value={countryCode}
                    onChange={(e) => setCountryCode(e.target.value)}
                    className="w-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                  >
                    <option value="+57">🇨🇴 +57</option>
                    <option value="+1">🇺🇸 +1</option>
                  </select>

                  {/* Phone Number Input */}
                  <input
                    {...register('phoneNumber')}
                    type="tel"
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder={countryCode === '+57' ? '3001234567' : '5551234567'}
                    maxLength={10}
                  />
                </div>
                {errors.phoneNumber && (
                  <p className="mt-1 text-sm text-red-600">{errors.phoneNumber.message}</p>
                )}
                <p className="mt-1 text-xs text-gray-500">
                  {countryCode === '+57' ? 'Ej: 3001234567 (10 dígitos)' : 'Ej: 5551234567 (10 dígitos)'}
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Contraseña *
                  </label>
                  <input
                    {...register('password')}
                    type="password"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  {errors.password && (
                    <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Confirmar Contraseña *
                  </label>
                  <input
                    {...register('confirmPassword')}
                    type="password"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  {errors.confirmPassword && (
                    <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
                  )}
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center space-x-2"
              >
                <span>Continuar</span>
                <ArrowRight className="w-5 h-5" />
              </button>
            </form>
          )}

          {/* STEP 2: VERIFICATIONS */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <div className="flex items-center justify-center space-x-4 mb-3">
                  <Mail className="w-12 h-12 text-blue-600" />
                  <Phone className="w-12 h-12 text-purple-600" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900">
                  Verificación de Contacto
                </h2>
                <p className="text-gray-600 text-sm mt-2">
                  Verifica tu email y teléfono antes de continuar
                </p>
              </div>

              {/* Email Verification */}
              <div className="p-6 bg-blue-50 rounded-xl border-2 border-blue-200">
                <div className="flex items-start space-x-3">
                  <Mail className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-blue-900 mb-2">
                      Verificación de Email
                    </h3>
                    {emailSent ? (
                      <div className="space-y-2">
                        <p className="text-sm text-blue-800">
                          ✅ Email de verificación enviado a: <strong>{registrationData.email}</strong>
                        </p>
                        <p className="text-sm text-blue-700">
                          Por favor, revisa tu bandeja de entrada y haz click en el enlace de verificación.
                        </p>
                        {registrationData.emailVerified ? (
                          <div className="mt-3 p-3 bg-green-100 rounded-lg">
                            <p className="text-sm font-semibold text-green-800">
                              ✅ Email verificado exitosamente
                            </p>
                          </div>
                        ) : (
                          <button
                            onClick={() => checkEmailVerification()}
                            className="mt-3 text-sm text-blue-600 hover:text-blue-800 font-medium"
                          >
                            ¿Ya verificaste? Haz click aquí para confirmar
                          </button>
                        )}
                      </div>
                    ) : (
                      <button
                        onClick={() => sendEmailVerification(registrationData.email!)}
                        disabled={emailSending}
                        className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                      >
                        {emailSending ? 'Enviando...' : 'Reenviar email'}
                      </button>
                    )}
                  </div>
                  {registrationData.emailVerified && (
                    <Check className="w-6 h-6 text-green-600 flex-shrink-0" />
                  )}
                </div>
              </div>

              {/* SMS Verification */}
              <div className="p-6 bg-purple-50 rounded-xl border-2 border-purple-200">
                <div className="flex items-start space-x-3">
                  <Phone className="w-6 h-6 text-purple-600 flex-shrink-0 mt-1" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-purple-900 mb-2">
                      Verificación de Teléfono
                    </h3>
                    <p className="text-sm text-purple-800 mb-3">
                      Teléfono: <strong>{registrationData.telefono}</strong>
                    </p>

                    {!otpVerified && (
                      <div className="space-y-3">
                        <button
                          onClick={sendSMSCode}
                          disabled={smsSending || otpVerified}
                          className="w-full py-2 px-4 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 disabled:bg-gray-400 transition-colors"
                        >
                          {smsSending ? (
                            <span className="flex items-center justify-center space-x-2">
                              <Loader2 className="w-4 h-4 animate-spin" />
                              <span>Enviando código...</span>
                            </span>
                          ) : (
                            'Enviar código SMS'
                          )}
                        </button>

                        <div>
                          <label className="block text-sm font-medium text-purple-900 mb-2">
                            Código de 6 dígitos
                          </label>
                          <input
                            type="text"
                            value={smsCode}
                            onChange={(e) => setSmsCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                            maxLength={6}
                            className="w-full px-4 py-2 border-2 border-purple-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-center text-2xl tracking-widest"
                            placeholder="000000"
                          />
                        </div>

                        {smsError && (
                          <p className="text-sm text-red-600">{smsError}</p>
                        )}

                        <button
                          onClick={verifySMSCode}
                          disabled={smsCode.length !== 6 || smsVerifying || otpVerified}
                          className="w-full py-2 px-4 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 disabled:bg-gray-400 transition-colors"
                        >
                          {smsVerifying ? (
                            <span className="flex items-center justify-center space-x-2">
                              <Loader2 className="w-4 h-4 animate-spin" />
                              <span>Verificando...</span>
                            </span>
                          ) : (
                            'Verificar código'
                          )}
                        </button>
                      </div>
                    )}

                    {otpVerified && (
                      <div className="mt-3 p-3 bg-green-100 rounded-lg flex items-center justify-between">
                        <p className="text-sm font-semibold text-green-800">
                          ✅ Teléfono verificado exitosamente
                        </p>
                        <Check className="w-6 h-6 text-green-600" />
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Note about email verification */}
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                  <strong>Nota:</strong> Por ahora, puedes continuar solo con la verificación de SMS.
                  La verificación de email se completará más tarde.
                </p>
              </div>

              {/* Continue Button */}
              <button
                onClick={() => {
                  if (registrationData.phoneVerified) {
                    setCurrentStep(3);
                  } else {
                    setError('Debes verificar tu teléfono antes de continuar');
                  }
                }}
                disabled={!registrationData.phoneVerified}
                className={`w-full py-3 px-4 font-semibold rounded-lg shadow-lg transition-all duration-200 flex items-center justify-center space-x-2 ${
                  registrationData.phoneVerified
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 hover:shadow-xl'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                <span>Continuar</span>
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          )}

          {/* STEP 3: ADDITIONAL DATA */}
          {currentStep === 3 && (
            <form onSubmit={handleSubmit(handleStep3Submit)} className="space-y-6">
              <div className="text-center mb-6">
                <User className="w-12 h-12 text-purple-600 mx-auto mb-3" />
                <h2 className="text-xl font-semibold text-gray-900">
                  Información Adicional
                </h2>
                <p className="text-gray-600 text-sm mt-2">
                  {state?.userType === 'BUYER'
                    ? 'Completa tu información para envíos'
                    : 'Completa la información requerida para vendedores'}
                </p>
              </div>

              {/* BUYER Additional Fields */}
              {state?.userType === 'BUYER' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Apellido *
                    </label>
                    <input
                      {...register('apellido')}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Pérez"
                    />
                    {errors.apellido && (
                      <p className="mt-1 text-sm text-red-600">{errors.apellido.message}</p>
                    )}
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Ciudad *
                      </label>
                      <input
                        {...register('ciudad')}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Bogotá"
                      />
                      {errors.ciudad && (
                        <p className="mt-1 text-sm text-red-600">{errors.ciudad.message}</p>
                      )}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Departamento *
                      </label>
                      <input
                        {...register('departamento')}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Cundinamarca"
                      />
                      {errors.departamento && (
                        <p className="mt-1 text-sm text-red-600">{errors.departamento.message}</p>
                      )}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Dirección *
                    </label>
                    <input
                      {...register('direccion')}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Calle 123 #45-67"
                    />
                    {errors.direccion && (
                      <p className="mt-1 text-sm text-red-600">{errors.direccion.message}</p>
                    )}
                    <p className="mt-1 text-sm text-gray-500">
                      Esta dirección se usará para tus envíos
                    </p>
                  </div>
                </>
              )}

              {/* VENDOR Natural Additional Fields */}
              {state?.vendorType === 'persona_natural' && (
                <>
                  <div className="bg-purple-50 p-4 rounded-lg mb-4">
                    <h3 className="font-semibold text-purple-900">Información Personal</h3>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Apellido *</label>
                      <input {...register('apellido')} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                      {errors.apellido && <p className="mt-1 text-sm text-red-600">{errors.apellido.message}</p>}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Cédula *</label>
                      <input {...register('cedula')} placeholder="1234567890" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                      {errors.cedula && <p className="mt-1 text-sm text-red-600">{errors.cedula.message}</p>}
                    </div>
                  </div>

                  <div className="bg-purple-50 p-4 rounded-lg mb-4 mt-6">
                    <h3 className="font-semibold text-purple-900">Dirección Personal</h3>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Dirección *</label>
                    <input {...register('direccion')} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                    {errors.direccion && <p className="mt-1 text-sm text-red-600">{errors.direccion.message}</p>}
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Ciudad *</label>
                      <input {...register('ciudad')} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                      {errors.ciudad && <p className="mt-1 text-sm text-red-600">{errors.ciudad.message}</p>}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Departamento *</label>
                      <input {...register('departamento')} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                      {errors.departamento && <p className="mt-1 text-sm text-red-600">{errors.departamento.message}</p>}
                    </div>
                  </div>

                  <div className="bg-purple-50 p-4 rounded-lg mb-4 mt-6">
                    <h3 className="font-semibold text-purple-900">Dirección Fiscal</h3>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Dirección Fiscal *</label>
                    <input {...register('direccion_fiscal')} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                    {errors.direccion_fiscal && <p className="mt-1 text-sm text-red-600">{errors.direccion_fiscal.message}</p>}
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Ciudad Fiscal *</label>
                      <input {...register('ciudad_fiscal')} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                      {errors.ciudad_fiscal && <p className="mt-1 text-sm text-red-600">{errors.ciudad_fiscal.message}</p>}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Departamento Fiscal *</label>
                      <input {...register('departamento_fiscal')} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                      {errors.departamento_fiscal && <p className="mt-1 text-sm text-red-600">{errors.departamento_fiscal.message}</p>}
                    </div>
                  </div>
                </>
              )}

              {/* VENDOR Juridica Additional Fields */}
              {state?.vendorType === 'persona_juridica' && (
                <>
                  <div className="bg-purple-50 p-4 rounded-lg mb-4">
                    <h3 className="font-semibold text-purple-900">Datos de la Empresa</h3>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Razón Social *</label>
                      <input {...register('razon_social')} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                      {errors.razon_social && <p className="mt-1 text-sm text-red-600">{errors.razon_social.message}</p>}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Nombre Comercial *</label>
                      <input {...register('nombre_comercial')} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                      {errors.nombre_comercial && <p className="mt-1 text-sm text-red-600">{errors.nombre_comercial.message}</p>}
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">NIT * (Formato: 123456789-0)</label>
                      <input {...register('nit')} placeholder="123456789-0" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                      {errors.nit && <p className="mt-1 text-sm text-red-600">{errors.nit.message}</p>}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Teléfono Empresa *</label>
                      <input {...register('telefono_empresa')} placeholder="+573001234567" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                      {errors.telefono_empresa && <p className="mt-1 text-sm text-red-600">{errors.telefono_empresa.message}</p>}
                    </div>
                  </div>

                  <div className="bg-purple-50 p-4 rounded-lg mb-4 mt-6">
                    <h3 className="font-semibold text-purple-900">Representante Legal</h3>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Nombre Completo *</label>
                      <input {...register('representante_legal')} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                      {errors.representante_legal && <p className="mt-1 text-sm text-red-600">{errors.representante_legal.message}</p>}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Cédula *</label>
                      <input {...register('cedula_representante')} placeholder="1234567890" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                      {errors.cedula_representante && <p className="mt-1 text-sm text-red-600">{errors.cedula_representante.message}</p>}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Email Representante *</label>
                    <input {...register('email_representante')} type="email" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                    {errors.email_representante && <p className="mt-1 text-sm text-red-600">{errors.email_representante.message}</p>}
                  </div>

                  <div className="bg-purple-50 p-4 rounded-lg mb-4 mt-6">
                    <h3 className="font-semibold text-purple-900">Dirección Fiscal</h3>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Dirección Fiscal *</label>
                    <input {...register('direccion_fiscal')} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                    {errors.direccion_fiscal && <p className="mt-1 text-sm text-red-600">{errors.direccion_fiscal.message}</p>}
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Ciudad Fiscal *</label>
                      <input {...register('ciudad_fiscal')} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                      {errors.ciudad_fiscal && <p className="mt-1 text-sm text-red-600">{errors.ciudad_fiscal.message}</p>}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Departamento Fiscal *</label>
                      <input {...register('departamento_fiscal')} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                      {errors.departamento_fiscal && <p className="mt-1 text-sm text-red-600">{errors.departamento_fiscal.message}</p>}
                    </div>
                  </div>
                </>
              )}

              <button
                type="submit"
                className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center space-x-2"
              >
                <span>Continuar</span>
                <ArrowRight className="w-5 h-5" />
              </button>
            </form>
          )}

          {/* STEP 4: CONFIRMATION AND FINAL REGISTRATION */}
          {currentStep === 4 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <Check className="w-12 h-12 text-green-600 mx-auto mb-3" />
                <h2 className="text-xl font-semibold text-gray-900">
                  Confirmar Registro
                </h2>
                <p className="text-gray-600 text-sm mt-2">
                  Revisa tu información antes de completar el registro
                </p>
              </div>

              {/* Summary */}
              <div className="space-y-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-3">Datos Básicos</h3>
                  <div className="space-y-2 text-sm">
                    <p><strong>Nombre:</strong> {registrationData.nombre}</p>
                    <p><strong>Email:</strong> {registrationData.email}</p>
                    <p><strong>Teléfono:</strong> {registrationData.telefono}</p>
                  </div>
                </div>

                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <h3 className="font-semibold text-green-900 mb-3">Verificaciones</h3>
                  <div className="space-y-2 text-sm">
                    <p className="flex items-center space-x-2">
                      {registrationData.emailVerified ? (
                        <Check className="w-4 h-4 text-green-600" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-yellow-600" />
                      )}
                      <span>Email: {registrationData.emailVerified ? 'Verificado' : 'Pendiente'}</span>
                    </p>
                    <p className="flex items-center space-x-2">
                      {registrationData.phoneVerified ? (
                        <Check className="w-4 h-4 text-green-600" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-red-600" />
                      )}
                      <span>Teléfono: {registrationData.phoneVerified ? 'Verificado' : 'No verificado'}</span>
                    </p>
                  </div>
                </div>

                <div className="p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-semibold text-blue-900 mb-3">Tipo de Usuario</h3>
                  <p className="text-sm">
                    <strong>{state?.userType === 'BUYER' ? 'Comprador' : 'Vendedor'}</strong>
                    {state?.vendorType && ` - ${state.vendorType === 'persona_natural' ? 'Persona Natural' : 'Persona Jurídica'}`}
                  </p>
                </div>
              </div>

              <button
                onClick={handleFinalRegistration}
                disabled={loading || !registrationData.phoneVerified}
                className={`w-full py-3 px-4 font-semibold rounded-lg shadow-lg transition-all duration-200 flex items-center justify-center space-x-2 ${
                  loading || !registrationData.phoneVerified
                    ? 'bg-gray-400 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-green-600 to-blue-600 text-white hover:from-green-700 hover:to-blue-700 hover:shadow-xl'
                }`}
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Registrando...</span>
                  </>
                ) : (
                  <>
                    <Check className="w-5 h-5" />
                    <span>Completar Registro</span>
                  </>
                )}
              </button>

              {!registrationData.phoneVerified && (
                <p className="text-sm text-red-600 text-center">
                  Debes verificar tu teléfono antes de completar el registro
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RegistrationWizard;
