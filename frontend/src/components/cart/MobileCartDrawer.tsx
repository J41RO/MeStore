import React, { useCallback, useMemo, useEffect } from 'react';
import { useCheckoutStore } from '../../stores/checkoutStore';
import { useAuthStore } from '../../stores/authStore';

interface MobileCartDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

const MobileCartDrawer: React.FC<MobileCartDrawerProps> = ({ isOpen, onClose }) => {
  const {
    cart_items,
    cart_count,
    cart_total,
    updateQuantity,
    removeItem
  } = useCheckoutStore();

  const { isAuthenticated } = useAuthStore();

  // Lock body scroll when drawer is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = 'unset';
      };
    }
  }, [isOpen]);

  const formatCurrency = useCallback((amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount);
  }, []);

  const handleCheckout = useCallback(() => {
    if (!isAuthenticated) {
      window.location.href = `/login?redirect=${encodeURIComponent('/checkout')}`;
    } else {
      window.location.href = '/checkout';
    }
    onClose();
  }, [isAuthenticated, onClose]);

  const handleContinueShopping = useCallback(() => {
    window.location.href = '/products';
    onClose();
  }, [onClose]);

  const subtotal = useMemo(() => {
    return cart_items.reduce((total, item) => total + (item.price * item.quantity), 0);
  }, [cart_items]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 lg:hidden">
      {/* Backdrop with blur effect */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity duration-300"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="fixed bottom-0 left-0 right-0 max-h-[85vh] bg-white rounded-t-2xl shadow-2xl transform transition-transform duration-300 ease-out">
        {/* Handle */}
        <div className="flex justify-center pt-3 pb-2">
          <div className="w-10 h-1 bg-gray-300 rounded-full" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Tu Carrito</h2>
            <p className="text-sm text-gray-500">
              {cart_count} {cart_count === 1 ? 'artículo' : 'artículos'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 -mr-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto max-h-[calc(85vh-180px)]">
          {cart_items.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
              <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.5 5M7 13l-1.5 5m4.5-5h6m0 0v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m8 0V9a2 2 0 00-2-2H9a2 2 0 00-2-2"
                  />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Carrito vacío</h3>
              <p className="text-gray-500 mb-6">Descubre nuestros productos increíbles</p>
              <button
                onClick={handleContinueShopping}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                Explorar Productos
              </button>
            </div>
          ) : (
            <div className="p-4 space-y-4">
              {cart_items.map((item, index) => (
                <div
                  key={item.id}
                  className="flex items-start space-x-3 pb-4 border-b border-gray-100 last:border-b-0"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  {/* Product Image */}
                  <div className="flex-shrink-0">
                    {item.image_url ? (
                      <img
                        src={item.image_url}
                        alt={item.name}
                        className="w-16 h-16 object-cover rounded-lg bg-gray-100"
                        loading="lazy"
                      />
                    ) : (
                      <div className="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg flex items-center justify-center">
                        <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                          />
                        </svg>
                      </div>
                    )}
                  </div>

                  {/* Product Details */}
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium text-gray-900 line-clamp-2 leading-tight">
                      {item.name}
                    </h4>

                    {item.vendor_name && (
                      <p className="text-xs text-gray-500 mt-1">
                        por {item.vendor_name}
                      </p>
                    )}

                    {/* Variant attributes */}
                    {item.variant_attributes && Object.keys(item.variant_attributes).length > 0 && (
                      <div className="mt-1 flex flex-wrap gap-1">
                        {Object.entries(item.variant_attributes).slice(0, 2).map(([key, value]) => (
                          <span
                            key={key}
                            className="inline-block bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full text-xs"
                          >
                            {value}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Quantity and Price */}
                    <div className="flex items-center justify-between mt-3">
                      <div className="flex items-center space-x-1">
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          className="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 active:bg-gray-300 flex items-center justify-center text-sm font-medium transition-colors"
                          disabled={item.quantity <= 1}
                        >
                          −
                        </button>
                        <span className="w-10 text-center text-sm font-medium px-1">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity + 1)}
                          className="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 active:bg-gray-300 flex items-center justify-center text-sm font-medium transition-colors"
                          disabled={item.stock_available && item.quantity >= item.stock_available}
                        >
                          +
                        </button>
                      </div>

                      <div className="text-right">
                        <div className="text-sm font-semibold text-gray-900">
                          {formatCurrency(item.price * item.quantity)}
                        </div>
                        {item.quantity > 1 && (
                          <div className="text-xs text-gray-500">
                            {formatCurrency(item.price)} c/u
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Remove button */}
                    <button
                      onClick={() => removeItem(item.id)}
                      className="text-xs text-red-600 hover:text-red-800 mt-2 font-medium active:text-red-900 transition-colors"
                    >
                      Eliminar
                    </button>

                    {/* Stock warning */}
                    {item.stock_available && item.stock_available <= 3 && (
                      <div className="mt-2 text-xs text-orange-600 bg-orange-50 px-2 py-1 rounded-md">
                        ¡Solo quedan {item.stock_available}!
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {cart_items.length > 0 && (
          <div className="border-t border-gray-100 p-4 bg-gray-50 rounded-t-xl">
            {/* Subtotal */}
            <div className="flex justify-between items-center mb-4">
              <span className="text-base font-medium text-gray-900">Subtotal:</span>
              <span className="text-lg font-bold text-gray-900">
                {formatCurrency(subtotal)}
              </span>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              <button
                onClick={handleCheckout}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white py-4 px-4 rounded-xl font-medium transition-all duration-200 shadow-lg hover:shadow-xl active:scale-[0.98]"
              >
                {isAuthenticated ? 'Proceder al Checkout' : 'Iniciar Sesión y Checkout'}
              </button>

              <button
                onClick={handleContinueShopping}
                className="w-full text-gray-700 hover:text-gray-900 py-3 px-4 rounded-xl font-medium transition-colors bg-white border border-gray-200 hover:bg-gray-50"
              >
                Continuar Comprando
              </button>
            </div>

            {/* Trust badges */}
            <div className="flex items-center justify-center space-x-4 mt-4 pt-3 border-t border-gray-200">
              <div className="flex items-center space-x-1 text-xs text-gray-600">
                <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Pago Seguro</span>
              </div>

              <div className="flex items-center space-x-1 text-xs text-gray-600">
                <svg className="w-3 h-3 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
                </svg>
                <span>Envío Rápido</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MobileCartDrawer;