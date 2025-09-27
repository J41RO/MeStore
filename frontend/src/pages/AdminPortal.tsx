import React from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

const AdminPortal: React.FC = () => {
  const { isAuthenticated, user } = useAuthStore();
  const navigate = useNavigate();

  // Si ya está autenticado como admin, redirigir al dashboard
  if (isAuthenticated && (user?.user_type === 'ADMIN' || user?.user_type === 'SUPERUSER')) {
    return <Navigate to="/admin-secure-portal/dashboard" replace />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background corporativo con partículas mejorado */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-blue-600/30 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-600/30 rounded-full blur-3xl"></div>
        <div className="absolute top-1/4 left-1/4 w-32 h-32 bg-blue-500/10 rotate-45 rounded-lg"></div>
        <div className="absolute bottom-1/4 right-1/4 w-24 h-24 bg-purple-500/10 rotate-12 rounded-lg"></div>
      </div>

      <div className="relative z-10 w-full max-w-7xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
        {/* Panel Izquierdo - Branding Corporativo */}
        <div className="text-center lg:text-left space-y-8">
          <div className="space-y-6">
            <div className="inline-flex items-center px-4 py-2 bg-blue-800/50 rounded-full border border-blue-700/50">
              <span className="text-sm font-medium text-blue-200">MeStocker Enterprise</span>
            </div>
            
            <h1 className="text-5xl lg:text-7xl font-bold leading-tight">
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-blue-300 bg-clip-text text-transparent">
                Portal
              </span>
              <br />
              <span className="text-white">Administrativo</span>
            </h1>
            
            <p className="text-xl text-slate-300 leading-relaxed max-w-2xl">
              Centro de comando empresarial para la gestión integral del ecosistema MeStocker. 
              Acceso exclusivo para personal autorizado con credenciales corporativas.
            </p>
          </div>

          {/* Características corporativas */}
          <div className="space-y-6">
            <div className="flex items-center justify-center lg:justify-start space-x-4">
              <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center border border-blue-400/30">
                <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="text-left">
                <h3 className="text-white font-semibold">Gestión Completa del Marketplace</h3>
                <p className="text-slate-300 text-sm">Control total sobre productos, usuarios y transacciones</p>
              </div>
            </div>
            
            <div className="flex items-center justify-center lg:justify-start space-x-4">
              <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center border border-purple-400/30">
                <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="text-left">
                <h3 className="text-white font-semibold">Analytics y Reportes Avanzados</h3>
                <p className="text-slate-300 text-sm">Dashboard ejecutivo con métricas en tiempo real</p>
              </div>
            </div>
            
            <div className="flex items-center justify-center lg:justify-start space-x-4">
              <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center border border-blue-400/30">
                <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div className="text-left">
                <h3 className="text-white font-semibold">Seguridad Empresarial</h3>
                <p className="text-slate-300 text-sm">Autenticación avanzada y auditoría completa</p>
              </div>
            </div>
          </div>
        </div>

        {/* Panel Derecho - Card de Acceso */}
        <div className="flex justify-center lg:justify-end">
          <div className="w-full max-w-lg bg-white/5 backdrop-blur-xl rounded-3xl p-10 border border-white/10 shadow-2xl ring-1 ring-white/5">
            <div className="text-center mb-10">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl mx-auto mb-6 flex items-center justify-center shadow-lg">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h2 className="text-3xl font-bold text-white mb-3">Centro de Comando</h2>
              <p className="text-slate-400 text-lg">Autenticación corporativa requerida</p>
            </div>

            <div className="space-y-6">
              <button
                onClick={() => navigate('/admin-login')}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-5 px-8 rounded-2xl transition-all duration-300 transform hover:scale-105 hover:shadow-xl"
              >
                <span className="text-lg">Acceder al Sistema</span>
              </button>

              <div className="text-center py-4">
                <span className="text-slate-400">¿Necesitas acceso público?</span>
              </div>

                <button
                  onClick={() => navigate('/login')}
                  className="w-full border border-white/20 hover:border-white/30 bg-white/5 hover:bg-white/10 backdrop-blur-sm text-slate-300 hover:text-white font-medium py-4 px-8 rounded-2xl transition-all duration-300"
                >
                  Portal Público
                </button>
            </div>

            {/* Información de seguridad */}
            <div className="mt-10 p-6 bg-amber-500/10 border border-amber-500/20 rounded-2xl">
              <div className="flex items-start space-x-4">
                <svg className="w-5 h-5 text-amber-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                <div>
                  <p className="text-slate-300 text-sm leading-relaxed">
                    Portal exclusivo para personal ejecutivo y administrativo autorizado. 
                    Todas las sesiones son monitoreadas y registradas conforme a políticas corporativas.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer corporativo */}
      <div className="absolute bottom-6 left-6 right-6 text-center">
        <p className="text-slate-500">
          © 2024 MeStocker. Portal Administrativo Seguro.
        </p>
      </div>
    </div>
  );
};

export default AdminPortal;