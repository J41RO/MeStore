import React, { useCallback, useMemo } from 'react';
import { useCheckoutStore } from '../../stores/checkoutStore';
import { useAuthStore } from '../../stores/authStore';

interface CartSidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const CartSidebar: React.FC<CartSidebarProps> = ({ isOpen, onClose }) => {
  const {
    cart_items,
    cart_count,
    cart_total,
    updateQuantity,
    removeItem
  } = useCheckoutStore();

  const { isAuthenticated } = useAuthStore();

  const formatCurrency = useCallback((amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount);
  }, []);

  const handleCheckout = useCallback(() => {
    if (!isAuthenticated) {
      // Redirect to login with checkout return URL
      window.location.href = `/login?redirect=${encodeURIComponent('/checkout')}`;
    } else {
      // Go to checkout page
      window.location.href = '/checkout';
    }
    onClose();
  }, [isAuthenticated, onClose]);

  const handleContinueShopping = useCallback(() => {
    window.location.href = '/marketplace';
    onClose();
  }, [onClose]);

  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />

      {/* Sidebar */}
      <div className="fixed right-0 top-0 h-full w-full max-w-md bg-white shadow-xl z-50 flex flex-col transform transition-transform duration-300 ease-in-out">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">
            Carrito ({cart_count} {cart_count === 1 ? 'artículo' : 'artículos'})
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded-md hover:bg-gray-100 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {cart_items.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full p-8 text-center">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1}
                    d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.5 5M7 13l-1.5 5m4.5-5h6m0 0v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m8 0V9a2 2 0 00-2-2H9a2 2 0 00-2-2"
                  />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Tu carrito está vacío</h3>
              <p className="text-gray-500 mb-4">Agrega productos para comenzar tu compra</p>
              <button
                onClick={handleContinueShopping}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors"
              >
                Explorar Productos
              </button>
            </div>
          ) : (
            <div className="p-4 space-y-4">
              {cart_items.map((item) => (
                <div key={item.id} className="flex items-start space-x-3 pb-4 border-b border-gray-100 last:border-b-0">
                  {/* Product Image */}
                  <div className="flex-shrink-0">
                    {item.image_url ? (
                      <img
                        src={item.image_url}
                        alt={item.name}
                        className="w-16 h-16 object-cover rounded-md bg-gray-100"
                      />
                    ) : (
                      <div className="w-16 h-16 bg-gray-100 rounded-md flex items-center justify-center">
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
                    <h4 className="text-sm font-medium text-gray-900 truncate">{item.name}</h4>

                    {item.vendor_name && (
                      <p className="text-xs text-gray-500 mt-1">Por: {item.vendor_name}</p>
                    )}

                    {/* Variant attributes */}
                    {item.variant_attributes && Object.keys(item.variant_attributes).length > 0 && (
                      <div className="mt-1">
                        {Object.entries(item.variant_attributes).map(([key, value]) => (
                          <span
                            key={key}
                            className="inline-block bg-gray-100 text-gray-600 px-2 py-0.5 rounded text-xs mr-1"
                          >
                            {key}: {value}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Price and Quantity */}
                    <div className="flex items-center justify-between mt-2">
                      <div className="flex items-center space-x-1">
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          className="w-6 h-6 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center text-sm"
                          disabled={item.quantity <= 1}
                        >
                          -
                        </button>
                        <span className="w-8 text-center text-sm font-medium">{item.quantity}</span>
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity + 1)}
                          className="w-6 h-6 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center text-sm"
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
                      className="text-xs text-red-600 hover:text-red-800 mt-1"
                    >
                      Eliminar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {cart_items.length > 0 && (
          <div className="border-t p-4 space-y-4">
            {/* Total */}
            <div className="flex justify-between items-center text-lg font-semibold">
              <span>Total:</span>
              <span>{formatCurrency(cart_total)}</span>
            </div>

            {/* Action Buttons */}
            <div className="space-y-2">
              <button
                onClick={handleCheckout}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-md font-medium transition-colors"
              >
                {isAuthenticated ? 'Proceder al Checkout' : 'Iniciar Sesión y Checkout'}
              </button>

              <button
                onClick={handleContinueShopping}
                className="w-full text-gray-600 hover:text-gray-800 py-2 px-4 rounded-md font-medium transition-colors"
              >
                Continuar Comprando
              </button>
            </div>

            {/* Security notice */}
            <div className="flex items-center justify-center space-x-1 text-xs text-gray-500">
              <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>Compra 100% segura</span>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default CartSidebar;