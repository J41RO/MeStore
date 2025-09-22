/**
 * PWA Install Prompt Component
 * Colombian-optimized install experience for MeStocker
 */

import React, { useState, useEffect } from 'react';
import { X, Download, Smartphone, Wifi, ShoppingCart, User } from 'lucide-react';
import { usePWAInstall } from '../../utils/pwa';

interface PWAInstallPromptProps {
  onClose?: () => void;
  className?: string;
}

const PWAInstallPrompt: React.FC<PWAInstallPromptProps> = ({
  onClose,
  className = ''
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [isInstalling, setIsInstalling] = useState(false);
  const { isInstallable, isInstalled, install } = usePWAInstall();

  useEffect(() => {
    // Show prompt if installable and not already installed
    if (isInstallable && !isInstalled) {
      // Delay to allow page to load
      const timer = setTimeout(() => {
        setIsVisible(true);
      }, 3000);

      return () => clearTimeout(timer);
    }
  }, [isInstallable, isInstalled]);

  useEffect(() => {
    // Auto-advance through benefits
    if (isVisible && currentStep < benefits.length - 1) {
      const timer = setTimeout(() => {
        setCurrentStep(prev => prev + 1);
      }, 4000);

      return () => clearTimeout(timer);
    }
  }, [isVisible, currentStep]);

  const handleInstall = async () => {
    setIsInstalling(true);
    try {
      const success = await install();
      if (success) {
        setIsVisible(false);
        onClose?.();
      }
    } catch (error) {
      console.error('Installation failed:', error);
    } finally {
      setIsInstalling(false);
    }
  };

  const handleClose = () => {
    setIsVisible(false);
    onClose?.();
  };

  const benefits = [
    {
      icon: <Smartphone className="w-8 h-8 text-blue-500" />,
      title: 'Acceso Rápido',
      description: 'Abre MeStocker desde tu pantalla de inicio como una app nativa'
    },
    {
      icon: <Wifi className="w-8 h-8 text-green-500" />,
      title: 'Funciona Sin Internet',
      description: 'Consulta productos y gestiona tu inventario incluso sin conexión'
    },
    {
      icon: <ShoppingCart className="w-8 h-8 text-purple-500" />,
      title: 'Compras Más Rápidas',
      description: 'Carrito y checkout optimizados para móviles colombianos'
    },
    {
      icon: <User className="w-8 h-8 text-orange-500" />,
      title: 'Panel de Vendedor',
      description: 'Gestiona tu negocio desde cualquier lugar en Bucaramanga'
    }
  ];

  if (!isVisible || isInstalled) return null;

  return (
    <div className={`fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end md:items-center justify-center p-4 ${className}`}>
      <div className="bg-white rounded-t-3xl md:rounded-3xl max-w-md w-full max-h-[80vh] overflow-hidden transform transition-all duration-300 ease-out">
        {/* Header */}
        <div className="relative bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
          <button
            onClick={handleClose}
            className="absolute top-4 right-4 p-2 rounded-full bg-white bg-opacity-20 hover:bg-opacity-30 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          <div className="text-center">
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-4">
              <img
                src="/pwa-192x192.png"
                alt="MeStocker"
                className="w-12 h-12 rounded-full"
              />
            </div>
            <h2 className="text-xl font-bold mb-2">
              ¡Instala MeStocker!
            </h2>
            <p className="text-blue-100 text-sm">
              La app de marketplace más rápida de Bucaramanga
            </p>
          </div>
        </div>

        {/* Benefits Carousel */}
        <div className="p-6">
          <div className="relative overflow-hidden h-32 mb-6">
            {benefits.map((benefit, index) => (
              <div
                key={index}
                className={`absolute inset-0 flex items-center transition-all duration-500 ${
                  index === currentStep
                    ? 'opacity-100 transform translate-x-0'
                    : index < currentStep
                    ? 'opacity-0 transform -translate-x-full'
                    : 'opacity-0 transform translate-x-full'
                }`}
              >
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    {benefit.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">
                      {benefit.title}
                    </h3>
                    <p className="text-gray-600 text-sm">
                      {benefit.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Progress Indicators */}
          <div className="flex justify-center space-x-2 mb-6">
            {benefits.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentStep(index)}
                className={`w-2 h-2 rounded-full transition-all ${
                  index === currentStep
                    ? 'bg-blue-500 w-8'
                    : 'bg-gray-300'
                }`}
              />
            ))}
          </div>

          {/* Colombian-specific features */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <h4 className="font-semibold text-yellow-800 mb-2 flex items-center">
              🇨🇴 Diseñado para Colombia
            </h4>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• Pagos con PSE, Nequi y Daviplata</li>
              <li>• Optimizado para redes 3G/4G</li>
              <li>• Soporte en español colombiano</li>
              <li>• Entregas en Bucaramanga y área metropolitana</li>
            </ul>
          </div>

          {/* Install Button */}
          <button
            onClick={handleInstall}
            disabled={isInstalling}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-xl font-semibold text-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center space-x-2"
          >
            {isInstalling ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Instalando...</span>
              </>
            ) : (
              <>
                <Download className="w-5 h-5" />
                <span>Instalar App Gratis</span>
              </>
            )}
          </button>

          {/* Secondary Actions */}
          <div className="flex justify-between items-center mt-4 text-sm">
            <button
              onClick={handleClose}
              className="text-gray-500 hover:text-gray-700 py-2 px-4"
            >
              Recordar después
            </button>
            <span className="text-gray-400">
              Sin anuncios • Gratuito
            </span>
          </div>
        </div>

        {/* Installation Instructions (for browsers that don't support automatic install) */}
        <div className="bg-gray-50 p-4 text-xs text-gray-600">
          <details>
            <summary className="cursor-pointer font-medium mb-2">
              ¿No puedes instalar? Instrucciones manuales
            </summary>
            <div className="space-y-2">
              <div>
                <strong>Chrome/Edge:</strong> Menú → "Instalar MeStocker"
              </div>
              <div>
                <strong>Safari (iOS):</strong> Compartir → "Agregar a pantalla de inicio"
              </div>
              <div>
                <strong>Firefox:</strong> Menú → "Instalar"
              </div>
            </div>
          </details>
        </div>
      </div>
    </div>
  );
};

export default PWAInstallPrompt;