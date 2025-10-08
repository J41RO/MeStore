import React, { useState, useEffect } from 'react';
import { Shield, Lock, CheckCircle, AlertTriangle, Eye, EyeOff } from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const PublicResetPassword: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [passwords, setPasswords] = useState({
    newPassword: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error' | 'invalid-token'>('idle');
  const [message, setMessage] = useState('');
  const [passwordStrength, setPasswordStrength] = useState({ score: 0, text: '', color: '' });
  const [countdown, setCountdown] = useState(3);
  const navigate = useNavigate();

  const token = searchParams.get('token');

  useEffect(() => {
    if (!token) {
      setStatus('invalid-token');
      setMessage('Token de recuperación no válido. Por favor solicita un nuevo enlace.');
    }
  }, [token]);

  // Password strength calculator
  useEffect(() => {
    const password = passwords.newPassword;
    if (password.length === 0) {
      setPasswordStrength({ score: 0, text: '', color: '' });
      return;
    }

    let score = 0;
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;

    const strength = [
      { score: 0, text: 'Muy débil', color: 'text-red-600 bg-red-100' },
      { score: 1, text: 'Débil', color: 'text-orange-600 bg-orange-100' },
      { score: 2, text: 'Aceptable', color: 'text-yellow-600 bg-yellow-100' },
      { score: 3, text: 'Buena', color: 'text-blue-600 bg-blue-100' },
      { score: 4, text: 'Fuerte', color: 'text-green-600 bg-green-100' },
      { score: 5, text: 'Muy fuerte', color: 'text-green-700 bg-green-200' }
    ][score];

    setPasswordStrength(strength);
  }, [passwords.newPassword]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (passwords.newPassword !== passwords.confirmPassword) {
      setStatus('error');
      setMessage('Las contraseñas no coinciden');
      return;
    }

    if (passwords.newPassword.length < 8) {
      setStatus('error');
      setMessage('La contraseña debe tener al menos 8 caracteres');
      return;
    }

    if (passwordStrength.score < 2) {
      setStatus('error');
      setMessage('La contraseña es demasiado débil. Usa una combinación de mayúsculas, minúsculas, números y símbolos.');
      return;
    }

    setIsLoading(true);
    setStatus('idle');
    setMessage('');

    try {
      const response = await axios.post(`${API_URL}/api/v1/auth/reset-password`, {
        token,
        new_password: passwords.newPassword
      });

      if (response.data.success) {
        setStatus('success');
        setMessage(response.data.message || 'Tu contraseña ha sido actualizada correctamente.');

        // Countdown timer antes de redireccionar
        let timeLeft = 3;
        setCountdown(timeLeft);

        const countdownInterval = setInterval(() => {
          timeLeft -= 1;
          setCountdown(timeLeft);

          if (timeLeft <= 0) {
            clearInterval(countdownInterval);
            navigate('/login');
          }
        }, 1000);
      } else {
        setStatus('error');
        setMessage(response.data.message || 'Error al restablecer la contraseña');
      }
    } catch (error: any) {
      setStatus('error');
      if (error.response?.status === 400 || error.response?.status === 404) {
        setMessage('Token inválido o expirado. Por favor solicita un nuevo enlace de recuperación.');
      } else {
        setMessage(error.response?.data?.message || 'Error de conexión. Por favor intenta de nuevo.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (status === 'invalid-token') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl p-10 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
            <AlertTriangle className="w-8 h-8 text-red-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-3">
            Token Inválido
          </h3>
          <p className="text-gray-600 mb-6">
            {message}
          </p>
          <button
            onClick={() => navigate('/login/forgot-password')}
            className="w-full py-3 px-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-xl font-semibold transition-all"
          >
            Solicitar Nuevo Enlace
          </button>
        </div>
      </div>
    );
  }

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
            <Lock className="w-12 h-12 text-white" />
          </div>

          <h1 className="text-4xl font-bold text-white mb-3">Nueva Contraseña</h1>
          <p className="text-blue-200 text-lg">
            Crea una contraseña segura para tu cuenta
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
                ¡Contraseña Actualizada!
              </h3>
              <p className="text-gray-600 mb-4">
                {message}
              </p>
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
                <p className="text-blue-800 font-medium mb-2">
                  Redirigiendo al login en:
                </p>
                <div className="text-4xl font-bold text-blue-600">
                  {countdown}
                </div>
              </div>
              <div className="flex items-center justify-center text-sm text-gray-500">
                <svg className="animate-spin h-4 w-4 text-blue-600 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Preparando tu sesión...
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* New Password Field */}
              <div className="space-y-2">
                <label className="block text-gray-700 text-sm font-semibold mb-3">
                  <Lock className="inline w-4 h-4 mr-2" />
                  Nueva Contraseña
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={passwords.newPassword}
                    onChange={(e) => setPasswords(prev => ({ ...prev, newPassword: e.target.value }))}
                    className="w-full px-5 py-4 bg-gray-50/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 text-gray-800 placeholder-gray-400"
                    placeholder="Mínimo 8 caracteres"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>

                {/* Password strength indicator */}
                {passwords.newPassword && (
                  <div className="mt-2">
                    <div className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${passwordStrength.color}`}>
                      Seguridad: {passwordStrength.text}
                    </div>
                  </div>
                )}

                {/* Password requirements */}
                <ul className="mt-3 space-y-1 text-xs text-gray-600">
                  <li className={passwords.newPassword.length >= 8 ? 'text-green-600' : ''}>
                    ✓ Mínimo 8 caracteres
                  </li>
                  <li className={/[A-Z]/.test(passwords.newPassword) ? 'text-green-600' : ''}>
                    ✓ Al menos una letra mayúscula
                  </li>
                  <li className={/[a-z]/.test(passwords.newPassword) ? 'text-green-600' : ''}>
                    ✓ Al menos una letra minúscula
                  </li>
                  <li className={/\d/.test(passwords.newPassword) ? 'text-green-600' : ''}>
                    ✓ Al menos un número
                  </li>
                  <li className={/[^a-zA-Z0-9]/.test(passwords.newPassword) ? 'text-green-600' : ''}>
                    ✓ Al menos un símbolo especial
                  </li>
                </ul>
              </div>

              {/* Confirm Password Field */}
              <div className="space-y-2">
                <label className="block text-gray-700 text-sm font-semibold mb-3">
                  <Lock className="inline w-4 h-4 mr-2" />
                  Confirmar Contraseña
                </label>
                <div className="relative">
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={passwords.confirmPassword}
                    onChange={(e) => setPasswords(prev => ({ ...prev, confirmPassword: e.target.value }))}
                    className="w-full px-5 py-4 bg-gray-50/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 text-gray-800 placeholder-gray-400"
                    placeholder="Repite la contraseña"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>

                {/* Password match indicator */}
                {passwords.confirmPassword && (
                  <div className="mt-2">
                    {passwords.newPassword === passwords.confirmPassword ? (
                      <p className="text-xs text-green-600">✓ Las contraseñas coinciden</p>
                    ) : (
                      <p className="text-xs text-red-600">✗ Las contraseñas no coinciden</p>
                    )}
                  </div>
                )}
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
                disabled={isLoading || !passwords.newPassword || !passwords.confirmPassword || passwords.newPassword !== passwords.confirmPassword}
                className={`w-full py-4 px-6 rounded-xl font-semibold text-white transition-all duration-200 ${
                  !isLoading && passwords.newPassword && passwords.confirmPassword && passwords.newPassword === passwords.confirmPassword
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
                    Actualizando contraseña...
                  </div>
                ) : (
                  <div className="flex items-center justify-center">
                    <Shield className="w-5 h-5 mr-2" />
                    Restablecer Contraseña
                  </div>
                )}
              </button>
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

export default PublicResetPassword;
