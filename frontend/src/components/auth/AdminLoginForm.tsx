import React, { useState } from 'react';
import { Shield, Lock, User, AlertTriangle, CheckCircle, Building2 } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { useNavigate } from 'react-router-dom';

interface AdminLoginFormProps {
  onLoginSuccess?: (data: any) => void;
}

/**
 * AdminLoginForm - Real API Integration
 * Frontend Security AI Implementation
 *
 * Formulario de login administrativo conectado con FastAPI backend
 * Usa endpoint específico /auth/admin-login para verificación de privilegios
 */
const AdminLoginForm: React.FC<AdminLoginFormProps> = ({ onLoginSuccess }) => {
  const [credentials, setCredentials] = useState({
    email: '',
    password: ''
  });
  const { signInAdmin, isLoading, error, clearError } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    try {
      if (!credentials.email.includes('@') || credentials.password.length < 6) {
        throw new Error('Credenciales administrativas inválidas');
      }

      const result = await signInAdmin(credentials.email, credentials.password);

      if (result.success) {
        console.log('Admin login successful:', {
          email: credentials.email,
          timestamp: new Date().toISOString(),
          portal: 'admin-secure'
        });

        if (onLoginSuccess) {
          onLoginSuccess({ email: credentials.email });
        }

        // Navegar al dashboard administrativo
        navigate('/admin-secure-portal/analytics');
      } else {
        // Error manejado por el hook useAuth
        console.error('Admin login failed:', result.error);
      }
    } catch (error) {
      console.error('Error en admin login:', error);
    }
  };

  const handleInputChange = (field: 'email' | 'password') => (e: React.ChangeEvent<HTMLInputElement>) => {
    setCredentials(prev => ({
      ...prev,
      [field]: e.target.value
    }));

    if (error) {
      clearError();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 flex items-center justify-center px-4 relative overflow-hidden">
      {/* Background elements corporativos */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-32 -right-32 w-64 h-64 bg-blue-600/20 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-32 -left-32 w-64 h-64 bg-purple-600/20 rounded-full blur-3xl"></div>
        <div className="absolute top-1/3 left-1/2 transform -translate-x-1/2 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl"></div>
        <div className="absolute top-1/4 right-1/4 w-20 h-20 bg-blue-400/10 rotate-45 rounded-lg"></div>
        <div className="absolute bottom-1/4 left-1/4 w-16 h-16 bg-purple-400/10 rotate-12 rounded-lg"></div>
      </div>

      <div className="relative z-10 max-w-lg w-full">
        {/* Header corporativo */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-28 h-28 bg-gradient-to-br from-blue-500 to-purple-600 rounded-3xl mb-8 shadow-2xl border border-blue-400/20 relative">
            <Shield className="w-14 h-14 text-white" />
            <div className="absolute -top-2 -right-2 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center border-2 border-white">
              <CheckCircle className="w-4 h-4 text-white" />
            </div>
          </div>

          <h1 className="text-4xl font-bold text-white mb-3">Portal Administrativo</h1>
          <p className="text-blue-200 text-lg leading-relaxed mb-2">
            Sistema de gestión empresarial
          </p>
          <p className="text-slate-400 text-sm">
            Acceso restringido para administradores corporativos
          </p>
        </div>

        {/* Formulario de login */}
        <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 p-10">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Field */}
            <div className="space-y-2">
              <label className="block text-gray-700 text-sm font-semibold mb-3">
                <User className="inline w-4 h-4 mr-2" />
                Email Administrativo
              </label>
              <div className="relative">
                <input
                  type="email"
                  value={credentials.email}
                  onChange={handleInputChange('email')}
                  className="w-full px-5 py-4 bg-gray-50/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 text-gray-800 placeholder-gray-400"
                  placeholder="admin@empresa.com"
                  required
                />
                <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                  <User className="w-5 h-5 text-gray-400" />
                </div>
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <label className="block text-gray-700 text-sm font-semibold mb-3">
                <Lock className="inline w-4 h-4 mr-2" />
                Contraseña Segura
              </label>
              <div className="relative">
                <input
                  type="password"
                  value={credentials.password}
                  onChange={handleInputChange('password')}
                  className="w-full px-5 py-4 bg-gray-50/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 text-gray-800 placeholder-gray-400"
                  placeholder="Contraseña administrativa"
                  required
                />
                <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                  <Lock className="w-5 h-5 text-gray-400" />
                </div>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="flex items-center space-x-3 p-4 bg-red-50 border border-red-200 rounded-xl">
                <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0" />
                <p className="text-red-700 text-sm font-medium">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || !credentials.email || !credentials.password}
              className={`w-full py-4 px-6 rounded-xl font-semibold text-white transition-all duration-200 ${
                !isLoading && credentials.email && credentials.password
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
                  Verificando credenciales...
                </div>
              ) : (
                <div className="flex items-center justify-center">
                  <Shield className="w-5 h-5 mr-2" />
                  Acceso Administrativo
                </div>
              )}
            </button>
          </form>

          {/* Security notice */}
          <div className="mt-8 text-center">
            <p className="text-gray-500 text-xs flex items-center justify-center">
              <Building2 className="w-4 h-4 mr-1" />
              Acceso monitorizado y registrado para auditoría
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminLoginForm;