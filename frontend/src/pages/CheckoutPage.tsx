import React, { useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import { useCheckoutStore } from '../stores/checkoutStore';
import CheckoutFlow from '../components/checkout/CheckoutFlow';

const CheckoutPage: React.FC = () => {
  const { isAuthenticated, user, checkAuth } = useAuthStore();
  const { cart_items } = useCheckoutStore();

  useEffect(() => {
    // Verify authentication status on page load
    if (!isAuthenticated) {
      checkAuth();
    }
  }, [isAuthenticated, checkAuth]);

  // If not authenticated, redirect to login
  if (!isAuthenticated) {
    // Show loading while checking auth
    if (!user) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Verificando autenticación...</p>
          </div>
        </div>
      );
    }

    // Redirect to login with return URL
    window.location.href = `/login?redirect=${encodeURIComponent('/checkout')}`;
    return null;
  }

  // If cart is empty, redirect to products page
  if (cart_items.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md mx-auto text-center p-8">
          <div className="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-6">
            <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1}
                d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.5 5M7 13l-1.5 5m4.5-5h6m0 0v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m8 0V9a2 2 0 00-2-2H9a2 2 0 00-2-2"
              />
            </svg>
          </div>

          <h1 className="text-2xl font-bold text-gray-900 mb-4">Tu carrito está vacío</h1>
          <p className="text-gray-600 mb-6">
            Agrega algunos productos a tu carrito antes de proceder al checkout.
          </p>

          <div className="space-y-3">
            <button
              onClick={() => window.location.href = '/products'}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md font-medium transition-colors"
            >
              Explorar Productos
            </button>

            <button
              onClick={() => window.location.href = '/'}
              className="w-full text-gray-600 hover:text-gray-800 font-medium"
            >
              Volver al Inicio
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show the checkout flow
  return <CheckoutFlow />;
};

export default CheckoutPage;