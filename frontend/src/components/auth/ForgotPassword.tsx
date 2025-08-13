import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

interface ForgotPasswordProps {
  onBackToLogin?: () => void;
}

interface ApiResponse {
  success: boolean;
  message: string;
}

const forgotPasswordSchema = yup.object({
  email: yup
    .string()
    .required('El email es obligatorio')
    .email('Formato de email inválido'),
});

type ForgotPasswordFormData = yup.InferType<typeof forgotPasswordSchema>;

const ForgotPassword: React.FC<ForgotPasswordProps> = ({ onBackToLogin }) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error'>(
    'success'
  );
  const [emailSent, setEmailSent] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    getValues,
  } = useForm<ForgotPasswordFormData>({
    resolver: yupResolver(forgotPasswordSchema),
    mode: 'onChange',
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/v1/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: data.email }),
      });

      const result: ApiResponse = await response.json();

      if (response.ok) {
        setEmailSent(true);
        setMessage(result.message);
        setMessageType('success');
      } else {
        setMessage(result.message || 'Error al solicitar recuperación');
        setMessageType('error');
      }
    } catch (error) {
      setMessage('Error de conexión. Intenta nuevamente.');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  if (emailSent) {
    return (
      <div className='forgot-password-container'>
        <div className='forgot-password-card'>
          <div className='success-icon'>✅</div>
          <h2>Revisa tu email</h2>
          <p>
            Se ha enviado un enlace de recuperación a <strong>{getValues('email')}</strong>
          </p>
          <p className='security-note'>
            El enlace expira en 1 hora. Si no ves el email, revisa tu carpeta de
            spam.
          </p>
          <button type='button' onClick={onBackToLogin}>
            Volver al login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className='forgot-password-container'>
      <div className='forgot-password-card'>
        <h2>Recuperar contraseña</h2>
        <p>
          Ingresa tu email y te enviaremos un enlace para restablecer tu
          contraseña.
        </p>

        <form onSubmit={handleSubmit(onSubmit)}>
          <div>
            <label htmlFor='email'>Email</label>
            <input
              type='email'
              id='email'
              {...register('email')}
              placeholder='tu@email.com'
              disabled={loading}
            />
            {errors.email && (
              <span className="error-message">{errors.email.message}</span>
            )}
          </div>

          {message && (
            <div className={`message message--${messageType}`}>{message}</div>
          )}

          <button type='submit' disabled={loading || !isValid}>
            {loading ? 'Enviando...' : 'Enviar enlace de recuperación'}
          </button>
        </form>

        <button type='button' onClick={onBackToLogin}>
          ← Volver al login
        </button>
      </div>
    </div>
  );
};

export default ForgotPassword;