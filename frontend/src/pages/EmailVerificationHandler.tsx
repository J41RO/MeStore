import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { Check, X, Loader2, Mail } from 'lucide-react';

type VerificationStatus = 'loading' | 'success' | 'error' | 'expired';

interface VerificationResponse {
  success: boolean;
  message: string;
  user_id?: string;
  email?: string;
}

const EmailVerificationHandler: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<VerificationStatus>('loading');
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');

  useEffect(() => {
    const token = searchParams.get('token');

    if (!token) {
      setStatus('error');
      setMessage('Token de verificación no encontrado');
      return;
    }

    verifyEmail(token);
  }, [searchParams]);

  const verifyEmail = async (token: string) => {
    try {
      const response = await axios.post<VerificationResponse>(
        `${import.meta.env.VITE_API_URL}/api/v1/auth/verify-email`,
        { token },
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        setStatus('success');
        setMessage(response.data.message || '¡Email verificado exitosamente!');
        setEmail(response.data.email || '');

        // Redirect to SMS verification after 3 seconds
        setTimeout(() => {
          navigate('/verify-sms', {
            state: {
              email: response.data.email,
              userId: response.data.user_id
            }
          });
        }, 3000);
      } else {
        setStatus('error');
        setMessage(response.data.message || 'Error al verificar el email');
      }
    } catch (error: any) {
      console.error('Email verification error:', error);

      if (error.response?.status === 400) {
        const errorMessage = error.response.data?.error_message || error.response.data?.detail;

        if (errorMessage?.includes('expirado') || errorMessage?.includes('expired')) {
          setStatus('expired');
          setMessage('El token de verificación ha expirado. Por favor solicita un nuevo enlace.');
        } else if (errorMessage?.includes('inválido') || errorMessage?.includes('invalid')) {
          setStatus('error');
          setMessage('El token de verificación es inválido.');
        } else {
          setStatus('error');
          setMessage(errorMessage || 'Error al verificar el email');
        }
      } else {
        setStatus('error');
        setMessage('Error de conexión. Por favor intenta de nuevo más tarde.');
      }
    }
  };

  const handleResendEmail = async () => {
    // TODO: Implement resend email logic
    setMessage('Funcionalidad de reenvío en desarrollo');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        {/* Loading State */}
        {status === 'loading' && (
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-6">
              <Loader2 className="w-10 h-10 text-blue-600 animate-spin" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Verificando Email
            </h2>
            <p className="text-gray-600">
              Por favor espera mientras verificamos tu dirección de correo electrónico...
            </p>
          </div>
        )}

        {/* Success State */}
        {status === 'success' && (
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-6">
              <Check className="w-10 h-10 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              ¡Email Verificado!
            </h2>
            <p className="text-gray-600 mb-4">
              {message}
            </p>
            {email && (
              <p className="text-sm text-gray-500 mb-6">
                Email: <span className="font-semibold">{email}</span>
              </p>
            )}
            <div className="space-y-3">
              <div className="flex items-center justify-center space-x-2 text-sm text-gray-600">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Redirigiendo a verificación SMS...</span>
              </div>
            </div>
          </div>
        )}

        {/* Error State */}
        {status === 'error' && (
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-6">
              <X className="w-10 h-10 text-red-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Error de Verificación
            </h2>
            <p className="text-gray-600 mb-6">
              {message}
            </p>
            <div className="space-y-3">
              <button
                onClick={() => navigate('/register')}
                className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Volver al Registro
              </button>
              <button
                onClick={() => navigate('/login')}
                className="w-full px-4 py-3 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
              >
                Ir a Iniciar Sesión
              </button>
            </div>
          </div>
        )}

        {/* Expired State */}
        {status === 'expired' && (
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mb-6">
              <Mail className="w-10 h-10 text-yellow-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Token Expirado
            </h2>
            <p className="text-gray-600 mb-6">
              {message}
            </p>
            <div className="space-y-3">
              <button
                onClick={handleResendEmail}
                className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Reenviar Email de Verificación
              </button>
              <button
                onClick={() => navigate('/login')}
                className="w-full px-4 py-3 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
              >
                Ir a Iniciar Sesión
              </button>
            </div>
          </div>
        )}

        {/* Help Text */}
        <div className="mt-8 pt-6 border-t border-gray-200 text-center">
          <p className="text-sm text-gray-600">
            ¿Necesitas ayuda?{' '}
            <a
              href="mailto:soporte@mestocker.com"
              className="text-blue-600 hover:underline font-semibold"
            >
              Contáctanos
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default EmailVerificationHandler;
