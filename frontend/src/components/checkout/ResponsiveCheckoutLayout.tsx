import React, { useState, useEffect } from 'react';
import { useCheckoutStore } from '../../stores/checkoutStore';
import { useAuthStore } from '../../stores/authStore';
import CheckoutFlow from './CheckoutFlow';
import CheckoutProgress from './CheckoutProgress';
import CheckoutSummary from './CheckoutSummary';

interface ResponsiveCheckoutLayoutProps {
  children?: React.ReactNode;
}

const ResponsiveCheckoutLayout: React.FC<ResponsiveCheckoutLayoutProps> = ({ children }) => {
  const {
    current_step,
    cart_items,
    is_processing,
    error,
    setError,
    clearErrors,
    resetCheckout
  } = useCheckoutStore();

  const { isAuthenticated, user } = useAuthStore();
  const [isMobile, setIsMobile] = useState(false);
  const [showSummary, setShowSummary] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    clearErrors();
    if (!isAuthenticated) {
      window.location.href = '/login?redirect=/checkout';
      return;
    }
    if (cart_items.length === 0 && current_step !== 'confirmation') {
      window.location.href = '/cart';
      return;
    }
  }, [isAuthenticated, cart_items.length, current_step, clearErrors]);

  const getStepTitle = () => {
    switch (current_step) {
      case 'cart':
        return 'Carrito de Compras';
      case 'shipping':
        return 'Información de Envío';
      case 'payment':
        return 'Método de Pago';
      case 'confirmation':
        return 'Confirmación de Pedido';
      default:
        return 'Checkout';
    }
  };

  const getSummaryPosition = () => {
    if (isMobile) {
      return showSummary ? 'fixed' : 'hidden';
    }
    return 'sticky';
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Verificando autenticación...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile Header */}
      {isMobile && (
        <div className="lg:hidden bg-white shadow-sm border-b sticky top-0 z-40">
          <div className="px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <h1 className="text-lg font-semibold text-gray-900 truncate">
                  {getStepTitle()}
                </h1>
                {user && (
                  <p className="text-sm text-gray-600 truncate">
                    {user.name || user.email}
                  </p>
                )}
              </div>

              <button
                onClick={() => setShowSummary(true)}
                className="ml-4 bg-blue-600 text-white px-3 py-2 rounded-lg text-sm font-medium shadow-lg hover:bg-blue-700 active:scale-95 transition-all duration-200"
              >
                Ver Resumen
              </button>
            </div>

            {/* Mobile Progress */}
            <div className="mt-3">
              <CheckoutProgress variant="mobile" showLabels={false} />
            </div>
          </div>
        </div>
      )}

      {/* Desktop Header */}
      {!isMobile && (
        <div className="hidden lg:block bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="py-6">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">{getStepTitle()}</h1>
                  {user && (
                    <p className="text-sm text-gray-600 mt-1">
                      Comprando como: <span className="font-medium">{user.name || user.email}</span>
                    </p>
                  )}
                </div>

                <CheckoutProgress variant="default" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 relative z-30">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm text-red-700">{error}</p>
              </div>
              <div className="ml-auto pl-3">
                <button
                  onClick={() => setError(null)}
                  className="inline-flex text-red-400 hover:text-red-600 transition-colors"
                >
                  <span className="sr-only">Cerrar</span>
                  <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 lg:py-8">
        <div className={`${isMobile ? 'space-y-6' : 'lg:grid lg:grid-cols-12 lg:gap-8'}`}>
          {/* Main checkout content */}
          <div className={`${isMobile ? 'mb-20' : 'lg:col-span-8'}`}>
            <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
              {is_processing && (
                <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center z-20 rounded-lg backdrop-blur-sm">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-sm text-gray-600 font-medium">Procesando...</p>
                  </div>
                </div>
              )}

              <div className="relative">
                {children || <CheckoutFlow />}
              </div>
            </div>
          </div>

          {/* Order summary */}
          <div className={`${isMobile ? 'hidden' : 'lg:col-span-4'}`}>
            <div className="sticky top-8">
              <CheckoutSummary />
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Summary Overlay */}
      {isMobile && showSummary && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setShowSummary(false)}
          />
          <div className="fixed bottom-0 left-0 right-0 max-h-[80vh] bg-white rounded-t-2xl shadow-2xl overflow-hidden">
            <div className="flex justify-center pt-3 pb-2">
              <div className="w-10 h-1 bg-gray-300 rounded-full" />
            </div>
            <div className="px-4 pb-4 overflow-y-auto max-h-[calc(80vh-60px)]">
              <CheckoutSummary />
            </div>
            <div className="border-t border-gray-200 p-4 bg-gray-50">
              <button
                onClick={() => setShowSummary(false)}
                className="w-full bg-gray-800 text-white py-3 px-4 rounded-xl font-medium transition-colors hover:bg-gray-900"
              >
                Continuar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Mobile Bottom Navigation */}
      {isMobile && cart_items.length > 0 && current_step !== 'confirmation' && (
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 lg:hidden z-30">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setShowSummary(true)}
              className="text-blue-600 hover:text-blue-800 font-medium transition-colors"
            >
              Ver Resumen
            </button>

            <div className="text-right">
              <div className="text-sm text-gray-600">Total</div>
              <div className="text-lg font-bold text-gray-900">
                {new Intl.NumberFormat('es-CO', {
                  style: 'currency',
                  currency: 'COP',
                  minimumFractionDigits: 0
                }).format(cart_items.reduce((total, item) => total + (item.price * item.quantity), 0))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Development tools - Only show in development */}
      {import.meta.env.DEV && (
        <div className="fixed bottom-4 left-4 z-50 bg-gray-900 text-white p-3 rounded-lg text-xs max-w-48">
          <div className="space-y-1">
            <p><strong>Step:</strong> {current_step}</p>
            <p><strong>Items:</strong> {cart_items.length}</p>
            <p><strong>Mobile:</strong> {isMobile ? 'Yes' : 'No'}</p>
            <button
              onClick={resetCheckout}
              className="mt-2 bg-red-600 hover:bg-red-700 px-2 py-1 rounded text-xs w-full transition-colors"
            >
              Reset Checkout
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResponsiveCheckoutLayout;