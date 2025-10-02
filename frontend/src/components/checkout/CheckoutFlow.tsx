import React, { useEffect, useMemo, lazy, Suspense } from 'react';
import { useCheckoutStore } from '../../stores/checkoutStore';
import { useAuthStore } from '../../stores/authStore';
import { DevOnly } from '../DevOnly';

// Lazy load step components for better performance
const CartStep = lazy(() => import('./steps/CartStep'));
const ShippingStep = lazy(() => import('./steps/ShippingStep'));
const PaymentStep = lazy(() => import('./steps/PaymentStep'));
const ConfirmationStep = lazy(() => import('./steps/ConfirmationStep'));
const CheckoutProgress = lazy(() => import('./CheckoutProgress'));
const CheckoutSummary = lazy(() => import('./CheckoutSummary'));

// Step loading component
const StepLoader = React.memo(() => (
  <div className="p-8 flex items-center justify-center">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
  </div>
));

const CheckoutFlow = React.memo(() => {
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

  useEffect(() => {
    // Clear any previous errors when component mounts
    clearErrors();

    // If user is not authenticated, redirect to login
    if (!isAuthenticated) {
      // This should be handled by route protection, but as a fallback
      window.location.href = '/login?redirect=/checkout';
      return;
    }

    // If cart is empty and we're not on confirmation step, redirect to cart
    if (cart_items.length === 0 && current_step !== 'confirmation') {
      window.location.href = '/cart';
      return;
    }
  }, [isAuthenticated, cart_items.length, current_step, clearErrors]);

  // Memoize step rendering for performance
  const currentStepComponent = useMemo(() => {
    switch (current_step) {
      case 'cart':
        return <CartStep />;
      case 'shipping':
        return <ShippingStep />;
      case 'payment':
        return <PaymentStep />;
      case 'confirmation':
        return <ConfirmationStep />;
      default:
        return <CartStep />;
    }
  }, [current_step]);

  // Memoize step title calculation
  const stepTitle = useMemo(() => {
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
  }, [current_step]);

  // Loading state
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Verificando autenticación...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{stepTitle}</h1>
                {user && (
                  <p className="text-sm text-gray-600">
                    Comprando como: {user.name || user.email}
                  </p>
                )}
              </div>

              {/* Progress indicator */}
              <Suspense fallback={<StepLoader />}>
                <CheckoutProgress />
              </Suspense>
            </div>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-red-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
              <div className="ml-auto pl-3">
                <button
                  onClick={() => setError(null)}
                  className="inline-flex text-red-400 hover:text-red-600"
                >
                  <span className="sr-only">Cerrar</span>
                  <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path
                      fillRule="evenodd"
                      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="lg:grid lg:grid-cols-12 lg:gap-8">
          {/* Main checkout content */}
          <div className="lg:col-span-8">
            <div className="bg-white rounded-lg shadow-sm border">
              {is_processing && (
                <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-10 rounded-lg">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-2 text-sm text-gray-600">Procesando...</p>
                  </div>
                </div>
              )}

              <div className="relative">
                <Suspense fallback={<StepLoader />}>
                  {currentStepComponent}
                </Suspense>
              </div>
            </div>
          </div>

          {/* Order summary sidebar */}
          <div className="lg:col-span-4 mt-8 lg:mt-0">
            <Suspense fallback={<StepLoader />}>
              <CheckoutSummary />
            </Suspense>
          </div>
        </div>
      </div>

      {/* Development tools - Only show in development */}
      <DevOnly>
        <div className="fixed bottom-4 right-4 z-50">
          <div className="bg-gray-900 text-white p-3 rounded-lg text-xs">
            <p>Step: {current_step}</p>
            <p>Items: {cart_items.length}</p>
            <button
              onClick={resetCheckout}
              className="mt-2 bg-red-600 hover:bg-red-700 px-2 py-1 rounded text-xs"
            >
              Reset Checkout
            </button>
          </div>
        </div>
      </DevOnly>
    </div>
  );
});

CheckoutFlow.displayName = 'CheckoutFlow';

export default CheckoutFlow;