import React from 'react';
import AdminLoginForm from '../components/auth/AdminLoginForm';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

const AdminLogin: React.FC = () => {
  const { isAuthenticated, user } = useAuthStore();
  const navigate = useNavigate();

  // Si ya está autenticado como admin, redirigir al dashboard
  if (isAuthenticated && (user?.user_type === 'admin' || user?.user_type === 'superuser' || user?.user_type === 'ADMIN' || user?.user_type === 'SUPERUSER')) {
    return <Navigate to="/admin-secure-portal/analytics" replace />;
  }

  // Si está autenticado pero no es admin, mostrar acceso denegado
  if (isAuthenticated && user?.user_type !== 'admin' && user?.user_type !== 'superuser' && user?.user_type !== 'ADMIN' && user?.user_type !== 'SUPERUSER') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-red-900 to-slate-800 flex items-center justify-center">
        <div className="max-w-md w-full bg-white/10 backdrop-blur-lg rounded-xl p-8 border border-red-500/50 text-center">
          <h2 className="text-2xl font-bold text-white mb-4">Acceso Denegado</h2>
          <p className="text-red-200 mb-6">
            Su cuenta no tiene privilegios administrativos para acceder a este portal.
          </p>
          <button
            onClick={() => navigate('/login')}
            className="bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg transition-colors"
          >
            Volver al Login Principal
          </button>
        </div>
      </div>
    );
  }

  return <AdminLoginForm />;
};

export default AdminLogin;
