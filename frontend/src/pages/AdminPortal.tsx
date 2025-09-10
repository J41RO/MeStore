import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

const AdminPortal: React.FC = () => {
  const { isAuthenticated, user } = useAuthStore();

  // Si ya está autenticado como admin, redirigir al dashboard
  if (isAuthenticated && (user?.user_type === 'ADMIN' || user?.user_type === 'SUPERUSER')) {
    return <Navigate to="/admin-secure-portal/dashboard" replace />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 flex items-center justify-center p-4">
      {/* Background corporativo con partículas */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-600/30 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-600/30 rounded-full blur-3xl"></div>
      </div>

      <div className="relative z-10 w-full max-w-6xl mx-auto grid lg:grid-cols-2 gap-8 items-center">
        {/* Panel Izquierdo - Branding Corporativo */}
        <div className="text-center lg:text-left">
          <div className="mb-8">
            <h1 className="text-5xl lg:text-6xl font-bold mb-4">
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-blue-300 bg-clip-text text-transparent">
                Portal
              </span>
              <br />
              <span className="text-white">Administrativo</span>
            </h1>
            <p className="text-xl text-slate-300 mb-6">
              Acceso exclusivo para administradores y superusuarios del sistema MeStocker
            </p>
          </div>

          {/* Características corporativas */}
          <div className="space-y-4 mb-8">
            <div className="flex items-center justify-center lg:justify-start space-x-3">
              <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span className="text-slate-300">Gestión completa del marketplace</span>
            </div>
            <div className="flex items-center justify-center lg:justify-start space-x-3">
              <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <span className="text-slate-300">Panel de control avanzado</span>
            </div>
            <div className="flex items-center justify-center lg:justify-start space-x-3">
              <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <span className="text-slate-300">Acceso seguro y auditado</span>
            </div>
          </div>
        </div>

        {/* Panel Derecho - Card de Acceso */}
        <div className="flex justify-center lg:justify-end">
          <div className="w-full max-w-md bg-white/5 backdrop-blur-xl rounded-2xl p-8 border border-white/10 shadow-2xl">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl mx-auto mb-4 flex items-center justify-center">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Portal Corporativo</h2>
              <p className="text-slate-400">Credenciales administrativas requeridas</p>
            </div>

            <div className="space-y-4">
              <button
                onClick={() => window.location.href = '/admin-login'}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-300 transform hover:scale-105 hover:shadow-lg"
              >
                Acceder al Sistema
              </button>

              <div className="text-center">
                <span className="text-slate-400 text-sm">¿No tienes acceso administrativo?</span>
              </div>

              <button
                onClick={() => window.location.href = '/login'}
                className="w-full border border-slate-600 hover:border-slate-500 text-slate-300 hover:text-white font-medium py-3 px-6 rounded-xl transition-all duration-300"
              >
                Ir al Portal Público
              </button>
            </div>

            {/* Información de seguridad */}
            <div className="mt-8 p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg">
              <div className="flex items-start space-x-3">
                <svg className="w-5 h-5 text-orange-300 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                <div>
                  <p className="text-white text-base font-semibold">Acceso Restringido</p>
                  <p className="text-white text-sm mt-2 leading-relaxed opacity-90">
                    Este portal está destinado exclusivamente para personal autorizado. 
                    Todos los accesos son monitoreados y auditados.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer corporativo */}
      <div className="absolute bottom-4 left-4 right-4 text-center">
        <p className="text-slate-500 text-sm">
          © 2024 MeStocker. Portal Administrativo Seguro.
        </p>
      </div>
    </div>
  );
};

export default AdminPortal;