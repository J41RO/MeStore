import React, { useState } from 'react';
import { Shield, Lock, User, AlertTriangle, CheckCircle, Building2 } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import { useNavigate } from 'react-router-dom';
import { UserType } from '../../stores/authStore';

interface AdminLoginFormProps {
  onLoginSuccess?: (data: any) => void;
}

const AdminLoginForm: React.FC<AdminLoginFormProps> = ({ onLoginSuccess }) => {
  const [credentials, setCredentials] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (!credentials.email.includes('@') || credentials.password.length < 6) {
        throw new Error('Credenciales administrativas inválidas');
      }

      const response = await fetch('/api/v1/auth/admin-login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: credentials.email,
          password: credentials.password
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error de autenticación administrativa');
      }

      const result = await response.json();
      
      login(result.access_token, {
        id: result.user_id || 'admin-temp-id',
        name: credentials.email?.split('@')[0] || 'Admin Usuario',
        email: credentials.email,
        user_type: UserType.SUPERUSER
      });

      console.log('Admin login successful:', {
        email: credentials.email,
        timestamp: new Date().toISOString(),
        portal: 'admin-secure'
      });

      onLoginSuccess?.(result);
      navigate('/admin-secure-portal/dashboard');

    } catch (err: any) {
      setError(err.message || 'Error de autenticación administrativa');
      console.warn('Admin login failed:', {
        email: credentials.email,
        error: err.message,
        timestamp: new Date().toISOString()
      });
    } finally {
      setLoading(false);
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
        {/* Header corporativo mejorado */}
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

        {/* Card principal mejorado */}
        <div className="bg-white/8 backdrop-blur-xl rounded-3xl p-10 border border-white/15 shadow-2xl ring-1 ring-white/5">
          
          {/* Security badge mejorado */}
          <div className="flex items-center justify-center mb-10">
            <div className="inline-flex items-center space-x-3 px-6 py-3 bg-blue-500/15 rounded-full border border-blue-400/25 backdrop-blur-sm">
              <Shield className="w-5 h-5 text-green-400" />
              <span className="text-sm font-medium text-blue-200">Conexión Segura</span>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-8">
            <div>
              <label className="block text-sm font-semibold text-slate-200 mb-4 flex items-center space-x-2">
                <User className="w-4 h-4 text-blue-300" />
                <span>Email Corporativo</span>
              </label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-blue-300" />
                <input
                  type="email"
                  value={credentials.email}
                  onChange={(e) => setCredentials({...credentials, email: e.target.value})}
                  className="w-full pl-12 pr-4 py-4 bg-white/8 border border-white/25 rounded-xl text-white placeholder-blue-200/70 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-400 transition-all duration-300 backdrop-blur-sm"
                  placeholder="administrador@mestocker.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-200 mb-4 flex items-center space-x-2">
                <Lock className="w-4 h-4 text-blue-300" />
                <span>Contraseña Administrativa</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-blue-300" />
                <input
                  type="password"
                  value={credentials.password}
                  onChange={(e) => setCredentials({...credentials, password: e.target.value})}
                  className="w-full pl-12 pr-4 py-4 bg-white/8 border border-white/25 rounded-xl text-white placeholder-blue-200/70 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-400 transition-all duration-300 backdrop-blur-sm"
                  placeholder="••••••••••••"
                  required
                />
              </div>
            </div>

            {error && (
              <div className="flex items-center space-x-3 text-red-300 bg-red-900/20 p-4 rounded-xl border border-red-500/25 backdrop-blur-sm">
                <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                <span className="text-sm font-medium">{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-blue-800 disabled:to-purple-800 text-white font-semibold py-5 px-8 rounded-xl transition-all duration-300 transform hover:scale-[1.02] hover:shadow-xl disabled:cursor-not-allowed shadow-lg"
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-3">
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Verificando Credenciales...</span>
                </div>
              ) : (
                <div className="flex items-center justify-center space-x-2">
                  <Building2 className="w-5 h-5" />
                  <span>Acceso Administrativo</span>
                </div>
              )}
            </button>
          </form>

          {/* Security notice corregido y mejorado */}
          <div className="mt-10 p-6 bg-amber-500/8 border border-amber-500/20 rounded-2xl backdrop-blur-sm">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-amber-500/20 rounded-xl flex items-center justify-center">
                  <Shield className="w-5 h-5 text-amber-400" />
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="text-white font-semibold text-lg mb-3">Acceso Restringido</h4>
                <p className="text-slate-300 text-sm leading-relaxed">
                  Portal exclusivo para personal ejecutivo y administrativo autorizado. 
                  Todas las sesiones son monitoreadas y registradas conforme a políticas 
                  de seguridad corporativa establecidas.
                </p>
                <div className="mt-3 flex items-center space-x-2 text-xs text-slate-400">
                  <div className="w-1.5 h-1.5 bg-green-400 rounded-full"></div>
                  <span>Sistema de auditoría activo</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer corporativo mejorado */}
        <div className="text-center mt-10 space-y-6">
          <button
            onClick={() => window.location.href = '/'}
            className="inline-flex items-center space-x-2 text-blue-300 hover:text-blue-200 transition-colors group"
          >
            <svg className="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span>Volver al portal público</span>
          </button>
          
          <div className="flex items-center justify-center space-x-3 text-xs text-slate-500">
            <Building2 className="w-4 h-4" />
            <span>© 2024 MeStocker Enterprise</span>
            <span>•</span>
            <span>Portal Administrativo Seguro</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminLoginForm;