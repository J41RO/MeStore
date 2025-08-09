import React, { useState, useEffect } from 'react';

interface ApiResponse {
  success: boolean;
  message: string;
}

const ResetPassword: React.FC = () => {
  // Simular obtención del token desde URL params
  const [token] = useState<string>(() => {
    // En implementación real sería: new URLSearchParams(window.location.search).get('token')
    return 'demo_token_123';
  });

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [validatingToken, setValidatingToken] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error'>(
    'success'
  );
  const [resetSuccess, setResetSuccess] = useState(false);

  // Validar token al cargar componente
  useEffect(() => {
    validateToken();
  }, []);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (newPassword !== confirmPassword) {
      setMessage('Las contraseñas no coinciden');
      setMessageType('error');
      return;
    }

    if (newPassword.length < 8) {
      setMessage('La contraseña debe tener al menos 8 caracteres');
      setMessageType('error');
      return;
    }

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
          new_password: newPassword,
          confirm_password: confirmPassword,
        }),
      });

      const data: ApiResponse = await response.json();

      if (response.ok) {
        setResetSuccess(true);
        setMessage(data.message);
        setMessageType('success');

        // Simular redirección después de 3 segundos
        setTimeout(() => {
          console.log('Redirecting to login...');
        }, 3000);
      } else {
        setMessage(data.message || 'Error al restablecer contraseña');
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

        <form onSubmit={handleSubmit}>
          <div className='form-group'>
            <label htmlFor='newPassword'>Nueva contraseña</label>
            <input
              type='password'
              id='newPassword'
              value={newPassword}
              onChange={e => setNewPassword(e.target.value)}
              required
              disabled={loading}
              placeholder='Mínimo 8 caracteres'
            />

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
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
              required
              disabled={loading}
              placeholder='Repite la contraseña'
            />

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

          <button
            type='submit'
            disabled={
              loading ||
              newPassword !== confirmPassword ||
              newPassword.length < 8
            }
          >
            {loading ? 'Actualizando...' : 'Actualizar contraseña'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ResetPassword;
