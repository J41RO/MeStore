import React, { useState } from 'react';

interface ForgotPasswordProps {
  onBackToLogin?: () => void;
}

interface ApiResponse {
  success: boolean;
  message: string;
}

const ForgotPassword: React.FC<ForgotPasswordProps> = ({ onBackToLogin }) => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error'>('success');
  const [emailSent, setEmailSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/v1/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data: ApiResponse = await response.json();

      if (response.ok) {
        setEmailSent(true);
        setMessage(data.message);
        setMessageType('success');
      } else {
        setMessage(data.message || 'Error al solicitar recuperación');
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
      <div className="forgot-password-container">
        <div className="forgot-password-card">
          <div className="success-icon">✅</div>
          <h2>Revisa tu email</h2>
          <p>Se ha enviado un enlace de recuperación a <strong>{email}</strong></p>
          <p className="security-note">
            El enlace expira en 1 hora. Si no ves el email, revisa tu carpeta de spam.
          </p>
          <button type="button" onClick={onBackToLogin}>
            Volver al login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="forgot-password-container">
      <div className="forgot-password-card">
        <h2>Recuperar contraseña</h2>
        <p>Ingresa tu email y te enviaremos un enlace para restablecer tu contraseña.</p>

        <form onSubmit={handleSubmit}>
          <div>
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="tu@email.com"
              disabled={loading}
            />
          </div>

          {message && (
            <div className={`message message--${messageType}`}>
              {message}
            </div>
          )}

          <button type="submit" disabled={loading || !email}>
            {loading ? 'Enviando...' : 'Enviar enlace de recuperación'}
          </button>
        </form>

        <button type="button" onClick={onBackToLogin}>
          ← Volver al login
        </button>
      </div>
    </div>
  );
};

export default ForgotPassword;
