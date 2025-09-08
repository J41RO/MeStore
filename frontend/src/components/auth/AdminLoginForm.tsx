import React, { useState } from 'react';
import { Shield, Lock, User, AlertTriangle } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import { useNavigate } from 'react-router-dom';

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
      // Validación específica para admin
      if (!credentials.email.includes('@') || credentials.password.length < 6) {
        throw new Error('Credenciales administrativas inválidas');
      }

      // Llamar al endpoint admin-login directamente
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
      
      // Verificar que el usuario es admin
      if (result.user?.user_type !== 'ADMIN' && result.user?.user_type !== 'SUPERUSER') {
        throw new Error('Acceso denegado: Se requieren privilegios administrativos');
      }

      // Establecer estado de autenticación
      login(result.access_token, result.user);

      // Log de acceso exitoso
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="mx-auto w-16 h-16 bg-red-600 rounded-full flex items-center justify-center mb-4">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Portal Administrativo</h1>
          <p className="text-blue-200">Acceso restringido para administradores</p>
        </div>

        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 border border-white/20">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-white mb-2">
                Email Administrativo
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-blue-300" />
                <input
                  type="email"
                  value={credentials.email}
                  onChange={(e) => setCredentials({...credentials, email: e.target.value})}
                  className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/30 rounded-lg text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-red-500"
                  placeholder="admin@mestore.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-white mb-2">
                Contraseña Administrativa
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-blue-300" />
                <input
                  type="password"
                  value={credentials.password}
                  onChange={(e) => setCredentials({...credentials, password: e.target.value})}
                  className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/30 rounded-lg text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-red-500"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {error && (
              <div className="flex items-center space-x-2 text-red-300 bg-red-900/30 p-3 rounded-lg border border-red-500/50">
                <AlertTriangle className="w-5 h-5" />
                <span className="text-sm">{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-red-600 hover:bg-red-700 disabled:bg-red-800 text-white font-semibold py-3 px-4 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              {loading ? 'Verificando...' : 'Acceso Administrativo'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-xs text-blue-200">
              Acceso monitoreado y registrado para auditoría
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminLoginForm;
