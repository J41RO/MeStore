import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

// Schema de validación Yup para campos colombianos
const registerSchema = yup.object({
  nombre: yup
    .string()
    .required('Nombre completo es requerido')
    .test('palabras-minimas', 'Debe tener al menos 2 nombres y solo letras', (value) => {
      const words = value.trim().split(/\s+/);
      return words.length >= 2 && /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(value);
    }),
  email: yup
    .string()
    .required('Correo electrónico es requerido')
    .email('Formato de email inválido'),
  cedula: yup
    .string()
    .required('Cédula es requerida')
    .test('cedula-colombiana', 'Cédula debe tener entre 8-10 dígitos numéricos', (value) => {
      const numericValue = value.replace(/\D/g, '');
      return numericValue.length >= 8 && numericValue.length <= 10 && /^\d+$/.test(numericValue);
    }),
  telefono: yup
    .string()
    .required('Teléfono es requerido')
    .matches(/^\+57\s?\d{3}\s?\d{3}\s?\d{4}$/, 'Formato: +57 300 123 4567'),
  password: yup
    .string()
    .required('Contraseña es requerida')
    .min(8, 'Mínimo 8 caracteres')
    .matches(/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, 'Mínimo 8 caracteres con mayúscula, minúscula y número'),
  confirmPassword: yup
    .string()
    .required('Confirmación de contraseña es requerida')
    .oneOf([yup.ref('password')], 'Las contraseñas no coinciden')
});

/**
 * Componente RegisterForm para usuarios colombianos
 *
 * Características:
 * - Campos específicos para Colombia: cédula, teléfono +57
 * - Validación en tiempo real de todos los campos con react-hook-form + yup
 * - Integración con API /api/v1/auth/register
 * - Manejo de estados loading/success/error
 * - Callback opcional onRegisterSuccess
 */

interface RegisterFormProps {
  onRegisterSuccess?: () => void;
}

interface ApiResponse {
  success: boolean;
  message: string;
  data?: any;
}

const RegisterForm: React.FC<RegisterFormProps> = ({ onRegisterSuccess }) => {
  // React Hook Form setup - MIGRACIÓN COMPLETA
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    reset
  } = useForm({
    resolver: yupResolver(registerSchema),
    mode: 'onChange' // Validación en tiempo real
  });

  // Estados de control (conservados)
  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');
  const [messageType, setMessageType] = useState<'success' | 'error'>('error');

  // Implementación del handleSubmit con API integration
  const onSubmit = async (data: any) => {
    setLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const result: ApiResponse = await response.json();

      if (result.success) {
        setMessage('¡Registro exitoso! Bienvenido/a a MeStore');
        setMessageType('success');
        
        // Limpiar formulario usando react-hook-form
        reset();
        
        // Llamar callback si existe
        if (onRegisterSuccess) {
          setTimeout(() => onRegisterSuccess(), 2000);
        }
      } else {
        setMessage(result.message || 'Error en el registro');
        setMessageType('error');
      }
    } catch (error) {
      setMessage('Error de conexión. Intente nuevamente');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto', padding: '20px' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '30px', color: '#333' }}>
        Registro - Usuario Colombiano
      </h2>

      <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* Nombre Completo */}
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Nombre Completo *
          </label>
          <input
            {...register('nombre')}
            type="text"
            placeholder="ejemplo: Juan Carlos Pérez"
            style={{
              width: '100%',
              padding: '10px',
              border: `1px solid ${errors.nombre ? 'red' : '#ddd'}`,
              borderRadius: '4px',
              fontSize: '16px'
            }}
          />
          {errors.nombre && (
            <div style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
              {errors.nombre.message}
            </div>
          )}
        </div>

        {/* Email */}
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Correo Electrónico *
          </label>
          <input
            {...register('email')}
            type="email"
            placeholder="ejemplo: juan@correo.com"
            style={{
              width: '100%',
              padding: '10px',
              border: `1px solid ${errors.email ? 'red' : '#ddd'}`,
              borderRadius: '4px',
              fontSize: '16px'
            }}
          />
          {errors.email && (
            <div style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
              {errors.email.message}
            </div>
          )}
        </div>

        {/* Cédula */}
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Cédula de Ciudadanía *
          </label>
          <input
            {...register('cedula')}
            type="text"
            placeholder="ejemplo: 12345678"
            style={{
              width: '100%',
              padding: '10px',
              border: `1px solid ${errors.cedula ? 'red' : '#ddd'}`,
              borderRadius: '4px',
              fontSize: '16px'
            }}
          />
          {errors.cedula && (
            <div style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
              {errors.cedula.message}
            </div>
          )}
        </div>

        {/* Teléfono */}
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Teléfono Móvil *
          </label>
          <input
            {...register('telefono')}
            type="tel"
            placeholder="ejemplo: +57 300 123 4567"
            style={{
              width: '100%',
              padding: '10px',
              border: `1px solid ${errors.telefono ? 'red' : '#ddd'}`,
              borderRadius: '4px',
              fontSize: '16px'
            }}
          />
          {errors.telefono && (
            <div style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
              {errors.telefono.message}
            </div>
          )}
        </div>

        {/* Password */}
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Contraseña *
          </label>
          <input
            {...register('password')}
            type="password"
            placeholder="Mínimo 8 caracteres, mayúscula, minúscula y número"
            style={{
              width: '100%',
              padding: '10px',
              border: `1px solid ${errors.password ? 'red' : '#ddd'}`,
              borderRadius: '4px',
              fontSize: '16px'
            }}
          />
          {errors.password && (
            <div style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
              {errors.password.message}
            </div>
          )}
        </div>

        {/* Confirmar Password */}
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Confirmar Contraseña *
          </label>
          <input
            {...register('confirmPassword')}
            type="password"
            placeholder="Repetir la contraseña"
            style={{
              width: '100%',
              padding: '10px',
              border: `1px solid ${errors.confirmPassword ? 'red' : '#ddd'}`,
              borderRadius: '4px',
              fontSize: '16px'
            }}
          />
          {errors.confirmPassword && (
            <div style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
              {errors.confirmPassword.message}
            </div>
          )}
        </div>

        {/* Mensaje de estado */}
        {message && (
          <div style={{
            color: messageType === 'success' ? 'green' : 'red',
            fontSize: '14px',
            textAlign: 'center',
            padding: '10px',
            backgroundColor: messageType === 'success' ? '#f0f8f0' : '#fef0f0',
            borderRadius: '4px'
          }}>
            {message}
          </div>
        )}

        {/* Botón de registro */}
        <button
          type="submit"
          disabled={loading || !isValid}
          style={{
            padding: '12px',
            backgroundColor: !loading && isValid ? '#007bff' : '#ccc',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: !loading && isValid ? 'pointer' : 'not-allowed'
          }}
        >
          {loading ? 'Registrando...' : 'Registrarse'}
        </button>
      </form>
    </div>
  );
};

export default RegisterForm;