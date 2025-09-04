import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

interface ApiResponse {
  success: boolean;
  message: string;
}

const resetPasswordSchema = yup.object({
  newPassword: yup
    .string()
    .required('La nueva contraseña es obligatoria')
    .min(8, 'La contraseña debe tener al menos 8 caracteres')
    .matches(/[A-Z]/, 'Debe contener al menos una mayúscula')
    .matches(/[a-z]/, 'Debe contener al menos una minúscula')
    .matches(/\d/, 'Debe contener al menos un número'),
  confirmPassword: yup
    .string()
    .required('Confirmar contraseña es obligatorio')
    .oneOf([yup.ref('newPassword')], 'Las contraseñas deben coincidir'),
});

type ResetPasswordFormData = yup.InferType<typeof resetPasswordSchema>;

const ResetPassword: React.FC = () => {
  // ✅ TOKEN URL REAL - No más hardcode
  const [token] = useState<string>(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get('token') || '';
  });

  const [loading, setLoading] = useState(false);
  const [validatingToken, setValidatingToken] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error'>(
    'success'
  );
  const [resetSuccess, setResetSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isValid },
  } = useForm<ResetPasswordFormData>({
    resolver: yupResolver(resetPasswordSchema),
    mode: 'onChange',
  });

  const newPassword = watch('newPassword', '');
  const confirmPassword = watch('confirmPassword', '');

  // Validar token al cargar componente
  useEffect(() => {
    if (token) {
      validateToken();
    } else {
      setMessage('Token no encontrado en la URL');
      setMessageType('error');
      setValidatingToken(false);
    }
  }, [token]);

  const validateToken = async () => {
    try {
      const response = await fetch(
        `/api/v1/auth/validate-reset-token?token=${token}`,
        {
          method: 'POST',
        }
      );

      const data: ApiResponse = await response.json();

      if (response.ok) {
        setTokenValid(true);
      } else {
        setMessage(data.message || 'Token inválido o expirado');
        setMessageType('error');
      }
    } catch (error) {
      setMessage('Error validando token');
      setMessageType('error');
    } finally {
      setValidatingToken(false);
    }
  };

  const onSubmit = async (data: ResetPasswordFormData) => {
    setLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/v1/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          new_password: data.newPassword,
          confirm_password: data.confirmPassword,
        }),
      });

      const result: ApiResponse = await response.json();

      if (response.ok) {
        setResetSuccess(true);
        setMessage(result.message);
        setMessageType('success');

        // Simular redirección después de 3 segundos
        setTimeout(() => {
          console.log('Redirecting to login...');
        }, 3000);
      } else {
        setMessage(result.message || 'Error al restablecer contraseña');
        setMessageType('error');
      }
    } catch (error) {
      setMessage('Error de conexión. Intenta nuevamente.');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const getPasswordStrength = () => {
    const checks = [
      newPassword.length >= 8,
      /[A-Z]/.test(newPassword),
      /[a-z]/.test(newPassword),
      /\d/.test(newPassword),
    ];
    return checks.filter(Boolean).length;
  };

  if (validatingToken) {
    return (
      <div className='reset-password-container'>
        <div className='reset-password-card'>
          <div className='loading-spinner'>🔄</div>
          <p>Validando enlace de recuperación...</p>
        </div>
      </div>
    );
  }

  if (!tokenValid) {
    return (
      <div className='reset-password-container'>
        <div className='reset-password-card'>
          <div className='error-icon'>❌</div>
          <h2>Enlace inválido</h2>
          <p className='error-message'>{message}</p>
          <button onClick={() => console.log('Navigate to forgot password')}>
            Solicitar nuevo enlace
          </button>
        </div>
      </div>
    );
  }

  if (resetSuccess) {
    return (
      <div className='reset-password-container'>
        <div className='reset-password-card'>
          <div className='success-icon'>✅</div>
          <h2>Contraseña actualizada</h2>
          <p className='success-message'>{message}</p>
          <p>Serás redirigido al login en unos segundos...</p>
          <button onClick={() => console.log('Navigate to login')}>
            Ir al login
          </button>
        </div>
      </div>
    );
  }

  const strength = getPasswordStrength();
  const strengthText =
    strength === 4
      ? 'Muy fuerte'
      : strength === 3
        ? 'Fuerte'
        : strength === 2
          ? 'Media'
          : 'Débil';

  return (
    <div className='reset-password-container'>
      <div className='reset-password-card'>
        <h2>Nueva contraseña</h2>
        <p>Ingresa tu nueva contraseña. Debe ser segura y fácil de recordar.</p>

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className='form-group'>
            <label htmlFor='newPassword'>Nueva contraseña</label>
            <input
              type='password'
              id='newPassword'
              {...register('newPassword')}
              disabled={loading}
              placeholder='Mínimo 8 caracteres'
            />
            {errors.newPassword && (
              <span className='error-message'>
                {errors.newPassword.message}
              </span>
            )}

            {newPassword && (
              <div className='password-strength'>
                <div className={`strength-bar strength-${strength}`}>
                  <div className='strength-fill'></div>
                </div>
                <p className='strength-text'>Fortaleza: {strengthText}</p>
              </div>
            )}
          </div>

          <div className='form-group'>
            <label htmlFor='confirmPassword'>Confirmar contraseña</label>
            <input
              type='password'
              id='confirmPassword'
              {...register('confirmPassword')}
              disabled={loading}
              placeholder='Repite la contraseña'
            />
            {errors.confirmPassword && (
              <span className='error-message'>
                {errors.confirmPassword.message}
              </span>
            )}

            {confirmPassword && (
              <div
                className={`match-indicator ${newPassword === confirmPassword ? 'match' : 'no-match'}`}
              >
                {newPassword === confirmPassword
                  ? '✅ Las contraseñas coinciden'
                  : '❌ Las contraseñas no coinciden'}
              </div>
            )}
          </div>

          {message && (
            <div className={`message message--${messageType}`}>{message}</div>
          )}

          <button type='submit' disabled={loading || !isValid}>
            {loading ? 'Actualizando...' : 'Actualizar contraseña'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ResetPassword;
