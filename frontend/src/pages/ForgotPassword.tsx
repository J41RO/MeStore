import React, { useState } from 'react';
import { Shield, Mail, ArrowLeft, CheckCircle, AlertTriangle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ForgotPassword: React.FC = () => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setStatus('idle');
    setMessage('');

    try {
      const response = await axios.post(`${API_URL}/api/v1/auth/forgot-password`, {
        email
      });

      if (response.data.success) {
        setStatus('success');
        setMessage('Se ha enviado un enlace de recuperación a tu correo electrónico. Por favor revisa tu bandeja de entrada.');
      } else {
        setStatus('error');
        setMessage(response.data.message || 'Error al enviar el enlace de recuperación');
      }
    } catch (error: any) {
      setStatus('error');
      setMessage(error.response?.data?.message || 'Error de conexión. Por favor intenta de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 flex items-center justify-center px-4 relative overflow-hidden">
      {/* Background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-32 -right-32 w-64 h-64 bg-blue-600/20 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-32 -left-32 w-64 h-64 bg-purple-600/20 rounded-full blur-3xl"></div>
        <div className="absolute top-1/3 left-1/2 transform -translate-x-1/2 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl"></div>
      </div>

      <div className="relative z-10 max-w-lg w-full">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-3xl mb-6 shadow-2xl border border-blue-400/20">
            <Mail className="w-12 h-12 text-white" />
          </div>

          <h1 className="text-4xl font-bold text-white mb-3">Recuperar Contraseña</h1>
          <p className="text-blue-200 text-lg">
            Ingresa tu correo electrónico administrativo
          </p>
          <p className="text-slate-400 text-sm mt-2">
            Te enviaremos un enlace para restablecer tu contraseña
          </p>
        </div>

        {/* Form */}
        <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 p-10">
          {status === 'success' ? (
            <div className="text-center py-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Correo Enviado
              </h3>
              <p className="text-gray-600 mb-6">
                {message}
              </p>
              <p className="text-sm text-gray-500 mb-6">
                Si no recibes el correo en los próximos minutos, revisa tu carpeta de spam.
              </p>
              <button
                onClick={() => navigate('/admin-login')}
                className="inline-flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Volver al login</span>
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Email Field */}
              <div className="space-y-2">
                <label className="block text-gray-700 text-sm font-semibold mb-3">
                  <Mail className="inline w-4 h-4 mr-2" />
                  Email Administrativo
                </label>
                <div className="relative">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-5 py-4 bg-gray-50/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 text-gray-800 placeholder-gray-400"
                    placeholder="admin@mestocker.com"
                    required
                  />
                  <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                    <Mail className="w-5 h-5 text-gray-400" />
                  </div>
                </div>
              </div>

              {/* Error Message */}
              {status === 'error' && (
                <div className="flex items-center space-x-3 p-4 bg-red-50 border border-red-200 rounded-xl">
                  <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0" />
                  <p className="text-red-700 text-sm font-medium">{message}</p>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading || !email}
                className={`w-full py-4 px-6 rounded-xl font-semibold text-white transition-all duration-200 ${
                  !isLoading && email
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                    : 'bg-gray-400 cursor-not-allowed'
                }`}
              >
                {isLoading ? (
                  <div className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Enviando enlace...
                  </div>
                ) : (
                  <div className="flex items-center justify-center">
                    <Mail className="w-5 h-5 mr-2" />
                    Enviar Enlace de Recuperación
                  </div>
                )}
              </button>

              {/* Back to login link */}
              <div className="text-center pt-4">
                <button
                  type="button"
                  onClick={() => navigate('/admin-login')}
                  className="inline-flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>Volver al login</span>
                </button>
              </div>
            </form>
          )}

          {/* Security notice */}
          <div className="mt-8 text-center">
            <p className="text-gray-500 text-xs flex items-center justify-center">
              <Shield className="w-4 h-4 mr-1" />
              Proceso seguro y encriptado
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
