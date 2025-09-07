import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import RegisterForm from '../components/auth/RegisterForm';

const RegisterVendor: React.FC = () => {
  const navigate = useNavigate();
  const [isFormComplete, setIsFormComplete] = useState(false);

  const handleRegistrationSuccess = (data: any) => {
    // Redirigir a verificación OTP
    navigate('/verify-otp', { state: { telefono: data.telefono } });
  };

  const handleFormValidation = (isValid: boolean) => {
    setIsFormComplete(isValid);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Layout dividido: Grid responsivo */}
      <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2">
        
        {/* LADO IZQUIERDO: Formulario (50%) */}
        <div className="flex items-center justify-center p-6 lg:p-12">
          <div className="w-full max-w-md space-y-8">
            {/* Header del formulario */}
            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                Únete a MeStocker
              </h2>
              <p className="text-gray-600">
                Registra tu empresa y comienza a vender
              </p>
            </div>

            {/* Formulario con validaciones avanzadas */}
            <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
              <RegisterForm 
                onSuccess={handleRegistrationSuccess}
                onValidationChange={handleFormValidation}
                showValidationFeedback={true}
              />
              
              {/* Link a login */}
              <div className="text-center mt-6 pt-6 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => navigate('/login')}
                  className="text-blue-600 hover:text-blue-800 font-medium transition-colors"
                >
                  ¿Ya tienes cuenta? Inicia sesión
                </button>
              </div>
            </div>

            {/* Indicador de progreso visual */}
            <div className="flex items-center justify-center space-x-2">
              <div className={`w-3 h-3 rounded-full transition-colors ${isFormComplete ? 'bg-green-500' : 'bg-gray-300'}`}></div>
              <span className="text-sm text-gray-600">
                {isFormComplete ? 'Formulario completo' : 'Completa todos los campos'}
              </span>
            </div>
          </div>
        </div>

        {/* LADO DERECHO: Visual 3D con branding MeStocker (50%) */}
        <div className="hidden lg:flex items-center justify-center bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 relative overflow-hidden">
          {/* Elementos de fondo 3D */}
          <div className="absolute inset-0">
            {/* Círculos flotantes con efecto 3D */}
            <div className="absolute top-20 left-20 w-32 h-32 bg-white/10 rounded-full blur-xl animate-pulse"></div>
            <div className="absolute bottom-32 right-16 w-24 h-24 bg-white/15 rounded-full blur-lg animate-pulse delay-300"></div>
            <div className="absolute top-1/2 left-16 w-16 h-16 bg-white/20 rounded-full blur-md animate-pulse delay-700"></div>
            
            {/* Grid pattern */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:50px_50px]"></div>
          </div>

          {/* Contenido principal 3D */}
          <div className="relative z-10 text-center text-white p-12 max-w-lg">
            {/* Logo/Brand principal */}
            <div className="mb-8">
              <div className="mx-auto w-24 h-24 bg-white/20 backdrop-blur rounded-3xl flex items-center justify-center mb-6 shadow-2xl transform rotate-3 hover:rotate-0 transition-transform duration-500">
                <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <h1 className="text-4xl font-bold mb-2">MeStocker</h1>
              <p className="text-xl text-blue-100">Tu almacén digital</p>
            </div>

            {/* Elementos visuales 3D de almacenamiento */}
            <div className="space-y-6">
              {/* Cajas 3D flotantes */}
              <div className="flex justify-center space-x-4 mb-8">
                <div className="w-16 h-16 bg-gradient-to-br from-white/30 to-white/10 rounded-lg transform rotate-12 shadow-2xl backdrop-blur border border-white/20 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                  </svg>
                </div>
                <div className="w-16 h-16 bg-gradient-to-br from-white/25 to-white/5 rounded-lg transform -rotate-6 shadow-xl backdrop-blur border border-white/20 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="w-16 h-16 bg-gradient-to-br from-white/35 to-white/15 rounded-lg transform rotate-3 shadow-2xl backdrop-blur border border-white/20 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
              </div>

              {/* Beneficios con iconos */}
              <div className="space-y-4 text-left">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-white/90">Gestión inteligente de inventario</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <span className="text-white/90">Ventas automatizadas 24/7</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                  <span className="text-white/90">Pagos seguros garantizados</span>
                </div>
              </div>

              {/* Call to action visual */}
              <div className="mt-8 p-4 bg-white/10 backdrop-blur rounded-xl border border-white/20">
                <p className="text-white/90 text-sm">
                  Únete a más de <span className="font-bold text-white">2,000+</span> empresas que confían en MeStocker
                </p>
              </div>
            </div>
          </div>

          {/* Efecto de partículas flotantes */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute top-10 left-10 w-2 h-2 bg-white/30 rounded-full animate-ping"></div>
            <div className="absolute top-1/3 right-20 w-1 h-1 bg-white/40 rounded-full animate-ping delay-1000"></div>
            <div className="absolute bottom-20 left-1/3 w-1.5 h-1.5 bg-white/35 rounded-full animate-ping delay-500"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterVendor;