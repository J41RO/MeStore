import React, { useState } from 'react';

/**
 * ConstructionBanner - Professional "Under Construction" banner for MeStore
 *
 * Features:
 * - Dismissible by user (localStorage to remember preference)
 * - Expandable details section
 * - Clear messaging about available vs upcoming features
 * - Professional yellow/orange gradient design
 * - Mobile responsive
 *
 * Usage: Place at top of App.jsx or main layout component
 */
export const ConstructionBanner = () => {
  // Check if user previously dismissed the banner (persists across sessions)
  const [isOpen, setIsOpen] = useState(() => {
    const dismissed = localStorage.getItem('constructionBannerDismissed');
    return dismissed !== 'true';
  });

  const [showDetails, setShowDetails] = useState(false);

  const handleDismiss = () => {
    setIsOpen(false);
    localStorage.setItem('constructionBannerDismissed', 'true');
  };

  if (!isOpen) return null;

  return (
    <div
      className="bg-gradient-to-r from-yellow-50 to-orange-50 border-b-2 border-yellow-300 shadow-sm"
      style={{ marginTop: '64px' }}
      role="alert"
      aria-live="polite"
    >
      <div className="max-w-7xl mx-auto px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          {/* Icon + Message */}
          <div className="flex items-center space-x-3 flex-1">
            <span className="text-2xl flex-shrink-0" aria-hidden="true">🚧</span>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-bold text-gray-900 leading-tight">
                Sitio en Construcción - Funcionalidad Limitada
              </p>
              <p className="text-xs text-gray-600 mt-1 leading-tight">
                Puedes registrarte ahora. Te notificaremos cuando estemos 100% operativos.
                {' '}
                <button
                  onClick={() => setShowDetails(!showDetails)}
                  className="text-blue-600 hover:text-blue-800 hover:underline font-medium inline-flex items-center focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 rounded"
                  aria-expanded={showDetails}
                  aria-controls="construction-details"
                >
                  {showDetails ? (
                    <>Ver menos <span aria-hidden="true" className="ml-1">▲</span></>
                  ) : (
                    <>Ver más <span aria-hidden="true" className="ml-1">▼</span></>
                  )}
                </button>
              </p>
            </div>
          </div>

          {/* Close button */}
          <button
            onClick={handleDismiss}
            className="text-gray-500 hover:text-gray-700 ml-4 flex-shrink-0 p-1 rounded hover:bg-yellow-100 focus:outline-none focus:ring-2 focus:ring-yellow-500"
            aria-label="Cerrar aviso de construcción"
            title="Cerrar aviso"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Expandable details */}
        {showDetails && (
          <div
            id="construction-details"
            className="mt-4 pt-3 border-t border-yellow-200 animate-fadeIn"
          >
            <div className="grid sm:grid-cols-2 gap-4 text-sm">
              <div className="bg-white/50 rounded-lg p-3 border border-green-200">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <span className="text-green-600 mr-2">✅</span>
                  Disponible ahora:
                </h4>
                <ul className="space-y-1 text-gray-700">
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2 mt-0.5">•</span>
                    <span>Registro de usuarios y vendedores</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2 mt-0.5">•</span>
                    <span>Explorar catálogo de productos</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2 mt-0.5">•</span>
                    <span>Ver detalles de productos</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2 mt-0.5">•</span>
                    <span>Portal administrativo</span>
                  </li>
                </ul>
              </div>

              <div className="bg-white/50 rounded-lg p-3 border border-orange-200">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <span className="text-orange-600 mr-2">⏳</span>
                  Próximamente:
                </h4>
                <ul className="space-y-1 text-gray-700">
                  <li className="flex items-start">
                    <span className="text-orange-500 mr-2 mt-0.5">•</span>
                    <span>Sistema de compras completo</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-orange-500 mr-2 mt-0.5">•</span>
                    <span>Pasarelas de pago integradas (Wompi, PayU)</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-orange-500 mr-2 mt-0.5">•</span>
                    <span>Seguimiento de pedidos en tiempo real</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-orange-500 mr-2 mt-0.5">•</span>
                    <span>Sistema de mensajería con vendedores</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Beta notice */}
            <div className="mt-3 text-center">
              <p className="text-xs text-gray-600 italic">
                🎯 <strong>Beta Pública:</strong> Estamos refinando la experiencia.
                Tu feedback es invaluable - contáctanos si encuentras problemas.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Add fadeIn animation styles */}
      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default ConstructionBanner;
