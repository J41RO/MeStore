import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';

interface VerificationResponse {
  success: boolean;
  message: string;
  email_verified: boolean;
  phone_verified: boolean;
  account_active: boolean;
}

const EmailVerified = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [verificationData, setVerificationData] = useState<VerificationResponse | null>(null);

  useEffect(() => {
    const verifyEmail = async () => {
      const token = searchParams.get('token');

      if (!token) {
        setError('No se proporcionó un token de verificación');
        setLoading(false);
        return;
      }

      try {
        // Llamar al endpoint de backend para verificar el token
        const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
        const response = await axios.get<VerificationResponse>(
          `${apiUrl}/api/v1/auth/verify-email`,
          {
            params: { token },
            headers: {
              'Content-Type': 'application/json',
            },
          }
        );

        setVerificationData(response.data);
        setLoading(false);

        // Redirigir automáticamente después de 3 segundos
        setTimeout(() => {
          navigate('/dashboard');
        }, 3000);
      } catch (err: any) {
        console.error('Error verificando email:', err);
        setError(
          err.response?.data?.detail ||
            'Error al verificar el email. El token puede ser inválido o haber expirado.'
        );
        setLoading(false);
      }
    };

    verifyEmail();
  }, [searchParams, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="max-w-md w-full text-center p-6">
          <div className="mb-8">
            <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-600"></div>
          </div>
          <h2 className="text-2xl font-semibold text-gray-800 mb-2">
            Verificando tu email...
          </h2>
          <p className="text-gray-600">Por favor espera un momento.</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-pink-100">
        <div className="max-w-md w-full text-center p-6">
          <div className="mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full">
              <svg
                className="w-10 h-10 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </div>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">
              Error en la verificación
            </h2>
            <p className="text-gray-600">{error}</p>
          </div>

          <div className="space-y-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Ir al Dashboard
            </button>

            <button
              onClick={() => navigate('/')}
              className="w-full px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Volver al inicio
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (verificationData?.success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100">
        <div className="max-w-md w-full text-center p-6">
          <div className="mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full">
              <svg
                className="w-12 h-12 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
          </div>

          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-800 mb-4">
              ¡Email Verificado!
            </h2>
            <p className="text-lg text-gray-700 mb-4">
              {verificationData.message}
            </p>

            <div className="bg-white rounded-lg p-4 shadow-sm space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Email:</span>
                <span className="font-semibold text-gray-800">
                  {verificationData.email_verified ? '✅ Verificado' : '❌ Pendiente'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Teléfono:</span>
                <span className="font-semibold text-gray-800">
                  {verificationData.phone_verified ? '✅ Verificado' : '❌ Pendiente'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Cuenta:</span>
                <span className="font-semibold text-gray-800">
                  {verificationData.account_active ? '✅ Activa' : '⏳ Pendiente'}
                </span>
              </div>
            </div>
          </div>

          <p className="text-gray-600 mb-6">
            Serás redirigido al dashboard en 3 segundos...
          </p>

          <button
            onClick={() => navigate('/dashboard')}
            className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg"
          >
            Ir al Dashboard ahora
          </button>
        </div>
      </div>
    );
  }

  return null;
};

export default EmailVerified;
