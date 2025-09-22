/**
 * PWA Update Notification Component
 * Handles service worker updates for Colombian users
 */

import React, { useState, useEffect } from 'react';
import { RefreshCw, X, Download } from 'lucide-react';

interface PWAUpdateNotificationProps {
  onClose?: () => void;
  className?: string;
}

const PWAUpdateNotification: React.FC<PWAUpdateNotificationProps> = ({
  onClose,
  className = ''
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateAvailable, setUpdateAvailable] = useState(false);

  useEffect(() => {
    // Listen for service worker updates
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data && event.data.type === 'SW_UPDATE_AVAILABLE') {
          setUpdateAvailable(true);
          setIsVisible(true);
        }
      });

      // Check for existing waiting service worker
      navigator.serviceWorker.ready.then(registration => {
        if (registration.waiting) {
          setUpdateAvailable(true);
          setIsVisible(true);
        }
      });
    }
  }, []);

  const handleUpdate = async () => {
    if (!('serviceWorker' in navigator)) return;

    setIsUpdating(true);

    try {
      const registration = await navigator.serviceWorker.ready;

      if (registration.waiting) {
        // Tell the waiting service worker to skip waiting and become active
        registration.waiting.postMessage({ type: 'SKIP_WAITING' });

        // Listen for controlling service worker change
        navigator.serviceWorker.addEventListener('controllerchange', () => {
          // Reload to get the new version
          window.location.reload();
        });
      }
    } catch (error) {
      console.error('Error updating service worker:', error);
      setIsUpdating(false);
    }
  };

  const handleClose = () => {
    setIsVisible(false);
    onClose?.();
  };

  const handleRemindLater = () => {
    setIsVisible(false);
    // Show again in 1 hour
    setTimeout(() => {
      if (updateAvailable) {
        setIsVisible(true);
      }
    }, 60 * 60 * 1000);
  };

  if (!isVisible || !updateAvailable) return null;

  return (
    <div className={`fixed top-4 left-4 right-4 md:left-auto md:max-w-sm z-50 ${className}`}>
      <div className="bg-white rounded-lg shadow-lg border border-green-200 overflow-hidden transform transition-all duration-300 ease-out">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-500 to-blue-500 text-white p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                <RefreshCw className="w-5 h-5 text-green-500" />
              </div>
              <div>
                <h3 className="font-semibold text-sm">
                  Nueva Versión Disponible
                </h3>
                <p className="text-green-100 text-xs">
                  MeStocker tiene nuevas funciones
                </p>
              </div>
            </div>
            <button
              onClick={handleClose}
              className="p-1 rounded-full bg-white bg-opacity-20 hover:bg-opacity-30 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-4">
          <div className="mb-4">
            <h4 className="font-medium text-gray-900 mb-2">
              ¿Qué hay de nuevo?
            </h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                <span>Mejoras en el rendimiento</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                <span>Nuevas funciones offline</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 bg-purple-500 rounded-full"></span>
                <span>Optimizaciones para Colombia</span>
              </li>
            </ul>
          </div>

          {/* Colombian-specific message */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
            <p className="text-sm text-yellow-800">
              <span className="font-medium">🇨🇴 Mejoras para Colombia:</span>
              <br />
              Optimizaciones para redes móviles y nuevos métodos de pago colombianos.
            </p>
          </div>

          {/* Actions */}
          <div className="flex space-x-2">
            <button
              onClick={handleUpdate}
              disabled={isUpdating}
              className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg font-medium text-sm hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
            >
              {isUpdating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Actualizando...</span>
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  <span>Actualizar Ahora</span>
                </>
              )}
            </button>

            <button
              onClick={handleRemindLater}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 text-sm font-medium transition-colors"
            >
              Después
            </button>
          </div>

          {/* Update info */}
          <div className="mt-3 text-xs text-gray-500 text-center">
            La actualización tardará unos segundos
          </div>
        </div>
      </div>
    </div>
  );
};

export default PWAUpdateNotification;