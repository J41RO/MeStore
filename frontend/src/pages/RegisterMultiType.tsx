import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import axios from 'axios';
import { ArrowLeft, Check, AlertCircle, Loader2 } from 'lucide-react';

// Types
type UserType = 'BUYER' | 'VENDOR';
type VendorType = 'persona_natural' | 'persona_juridica' | null;

interface LocationState {
  userType: UserType;
  vendorType: VendorType;
}

interface RegisterResponse {
  success: boolean;
  message: string;
  user_id: string;
  email: string;
  user_type: string;
  vendor_type: string | null;
  account_status: string;
  vendor_status: string | null;
  requires_approval: boolean;
  next_steps: string[];
}

// Validation Schemas
const buyerSchema = yup.object({
  email: yup.string().required('Email requerido').email('Email inválido'),
  password: yup.string().required('Contraseña requerida').min(8, 'Mínimo 8 caracteres'),
  confirmPassword: yup.string().oneOf([yup.ref('password')], 'Las contraseñas no coinciden'),
  nombre: yup.string().required('Nombre requerido'),
  apellido: yup.string().optional(),
  telefono: yup.string().required('Teléfono requerido').matches(/^\+57\d{10}$/, 'Formato: +573001234567'),
  ciudad: yup.string().required('Ciudad requerida'),
  direccion: yup.string().optional()
});

const vendorNaturalSchema = yup.object({
  email: yup.string().required('Email requerido').email('Email inválido'),
  password: yup.string().required('Contraseña requerida').min(8, 'Mínimo 8 caracteres'),
  confirmPassword: yup.string().oneOf([yup.ref('password')], 'Las contraseñas no coinciden'),
  nombre: yup.string().required('Nombre requerido'),
  apellido: yup.string().required('Apellido requerido'),
  telefono: yup.string().required('Teléfono requerido').matches(/^\+57\d{10}$/, 'Formato: +573001234567'),
  cedula: yup.string().required('Cédula requerida').matches(/^\d{8,10}$/, '8-10 dígitos'),
  direccion: yup.string().required('Dirección requerida'),
  ciudad: yup.string().required('Ciudad requerida'),
  departamento: yup.string().required('Departamento requerido'),
  direccion_fiscal: yup.string().required('Dirección fiscal requerida'),
  ciudad_fiscal: yup.string().required('Ciudad fiscal requerida'),
  departamento_fiscal: yup.string().required('Departamento fiscal requerido')
});

const vendorJuridicaSchema = yup.object({
  email: yup.string().required('Email requerido').email('Email inválido'),
  password: yup.string().required('Contraseña requerida').min(8, 'Mínimo 8 caracteres'),
  confirmPassword: yup.string().oneOf([yup.ref('password')], 'Las contraseñas no coinciden'),
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

const RegisterMultiType: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState;

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [nextSteps, setNextSteps] = useState<string[]>([]);

  // Determine schema based on user type
  const getValidationSchema = () => {
    if (state?.userType === 'BUYER') return buyerSchema;
    if (state?.vendorType === 'persona_natural') return vendorNaturalSchema;
    if (state?.vendorType === 'persona_juridica') return vendorJuridicaSchema;
    return buyerSchema;
  };

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch
  } = useForm({
    resolver: yupResolver(getValidationSchema())
  });

  // Redirect if no user type selected
  useEffect(() => {
    if (!state?.userType) {
      navigate('/user-type-selector');
    }
  }, [state, navigate]);

  const onSubmit = async (data: any) => {
    setLoading(true);
    setError(null);

    try {
      // Remove confirmPassword before sending
      const { confirmPassword, ...submitData } = data;

      // Extract phone number based on user type (telefono for buyer/natural, telefono_empresa for juridica)
      const telefono = data.telefono || data.telefono_empresa;

      const response = await axios.post<RegisterResponse>(
        `${import.meta.env.VITE_API_URL}/api/v1/auth/register-multi-type`,
        submitData,
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        setSuccess(true);
        setNextSteps(response.data.next_steps);

        // Redirect to SMS verification after 3 seconds
        setTimeout(() => {
          navigate('/verify-sms', {
            state: {
              email: response.data.email,
              userId: response.data.user_id,
              userType: response.data.user_type,
              telefono: telefono  // ✅ PASS PHONE NUMBER FOR VERIFICATION
            }
          });
        }, 3000);
      }
    } catch (err: any) {
      console.error('Registration error:', err);
      const errorMessage = err.response?.data?.error_message ||
                          err.response?.data?.detail ||
                          'Error en el registro. Por favor intenta de nuevo.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getTitleText = () => {
    if (state?.userType === 'BUYER') return 'Registro de Comprador';
    if (state?.vendorType === 'persona_natural') return 'Registro Vendedor - Persona Natural';
    if (state?.vendorType === 'persona_juridica') return 'Registro Vendedor - Persona Jurídica';
    return 'Registro';
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-6">
            <Check className="w-10 h-10 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            ¡Registro Exitoso!
          </h2>
          <p className="text-gray-600 mb-6">
            Tu cuenta ha sido creada. Por favor completa los siguientes pasos:
          </p>
          <div className="text-left space-y-3 mb-6">
            {nextSteps.map((step, index) => (
              <div key={index} className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-semibold text-sm">
                  {index + 1}
                </div>
                <p className="text-sm text-gray-700">{step}</p>
              </div>
            ))}
          </div>
          <p className="text-sm text-gray-500">
            Redirigiendo a verificación...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/user-type-selector')}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Volver</span>
          </button>
          <h1 className="text-3xl font-bold text-gray-900">
            {getTitleText()}
          </h1>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
          {/* BUYER Fields */}
          {state?.userType === 'BUYER' && (
            <>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre *
                  </label>
                  <input
                    {...register('nombre')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Juan"
                  />
                  {errors.nombre && (
                    <p className="mt-1 text-sm text-red-600">{errors.nombre.message}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Apellido
                  </label>
                  <input
                    {...register('apellido')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Pérez"
                  />
                </div>
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
                  Teléfono * (Formato: +573001234567)
                </label>
                <input
                  {...register('telefono')}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="+573001234567"
                />
                {errors.telefono && (
                  <p className="mt-1 text-sm text-red-600">{errors.telefono.message}</p>
                )}
              </div>

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
                  Dirección
                </label>
                <input
                  {...register('direccion')}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Calle 123 #45-67"
                />
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
            </>
          )}

          {/* VENDOR NATURAL Fields */}
          {state?.vendorType === 'persona_natural' && (
            <>
              <div className="bg-purple-50 p-4 rounded-lg mb-6">
                <h3 className="font-semibold text-purple-900 mb-2">Datos Personales</h3>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Nombre *</label>
                  <input {...register('nombre')} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                  {errors.nombre && <p className="mt-1 text-sm text-red-600">{errors.nombre.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Apellido *</label>
                  <input {...register('apellido')} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                  {errors.apellido && <p className="mt-1 text-sm text-red-600">{errors.apellido.message}</p>}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
                <input {...register('email')} type="email" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>}
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Teléfono *</label>
                  <input {...register('telefono')} placeholder="+573001234567" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                  {errors.telefono && <p className="mt-1 text-sm text-red-600">{errors.telefono.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Cédula *</label>
                  <input {...register('cedula')} placeholder="1234567890" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                  {errors.cedula && <p className="mt-1 text-sm text-red-600">{errors.cedula.message}</p>}
                </div>
              </div>

              <div className="bg-purple-50 p-4 rounded-lg mb-6 mt-6">
                <h3 className="font-semibold text-purple-900 mb-2">Dirección Personal</h3>
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

              <div className="bg-purple-50 p-4 rounded-lg mb-6 mt-6">
                <h3 className="font-semibold text-purple-900 mb-2">Dirección Fiscal</h3>
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

              <div className="grid md:grid-cols-2 gap-4 mt-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Contraseña *</label>
                  <input {...register('password')} type="password" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                  {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Confirmar Contraseña *</label>
                  <input {...register('confirmPassword')} type="password" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                  {errors.confirmPassword && <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>}
                </div>
              </div>
            </>
          )}

          {/* VENDOR JURIDICA Fields */}
          {state?.vendorType === 'persona_juridica' && (
            <>
              <div className="bg-purple-50 p-4 rounded-lg mb-6">
                <h3 className="font-semibold text-purple-900 mb-2">Datos de la Empresa</h3>
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
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email Empresa *</label>
                  <input {...register('email')} type="email" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                  {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Teléfono Empresa *</label>
                <input {...register('telefono_empresa')} placeholder="+573001234567" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                {errors.telefono_empresa && <p className="mt-1 text-sm text-red-600">{errors.telefono_empresa.message}</p>}
              </div>

              <div className="bg-purple-50 p-4 rounded-lg mb-6 mt-6">
                <h3 className="font-semibold text-purple-900 mb-2">Representante Legal</h3>
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

              <div className="bg-purple-50 p-4 rounded-lg mb-6 mt-6">
                <h3 className="font-semibold text-purple-900 mb-2">Dirección Fiscal</h3>
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

              <div className="grid md:grid-cols-2 gap-4 mt-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Contraseña *</label>
                  <input {...register('password')} type="password" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                  {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Confirmar Contraseña *</label>
                  <input {...register('confirmPassword')} type="password" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                  {errors.confirmPassword && <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>}
                </div>
              </div>
            </>
          )}

          {/* Submit Button */}
          <div className="pt-6">
            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 px-4 rounded-lg font-semibold text-white transition-all duration-200 ${
                loading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl'
              }`}
            >
              {loading ? (
                <span className="flex items-center justify-center space-x-2">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Registrando...</span>
                </span>
              ) : (
                'Crear Cuenta'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RegisterMultiType;
