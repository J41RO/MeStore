import React, { useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCheckoutStore } from '../stores/checkoutStore';
import { useAuthStore } from '../stores/authStore';
import CartIcon from '../components/cart/CartIcon';

const CartPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    cart_items,
    cart_count,
    cart_total,
    updateQuantity,
    removeItem,
    clearCart,
    setCurrentStep
  } = useCheckoutStore();

  const { isAuthenticated } = useAuthStore();

  const formatCurrency = useMemo(() => {
    return (amount: number) => {
      return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0
      }).format(amount);
    };
  }, []);

  useEffect(() => {
    // Set checkout step to cart when visiting this page
    setCurrentStep('cart');
  }, [setCurrentStep]);

  const handleContinueShopping = () => {
    navigate('/marketplace');
  };

  const handleCheckout = () => {
    if (!isAuthenticated) {
      navigate('/login?redirect=/checkout');
    } else {
      navigate('/checkout');
    }
  };

  const subtotal = useMemo(() => {
    return cart_items.reduce((total, item) => total + (item.price * item.quantity), 0);
  }, [cart_items]);

  const estimatedShipping = 15000; // Default shipping cost
  const estimatedTax = subtotal * 0.19; // 19% tax
  const estimatedTotal = subtotal + estimatedShipping + estimatedTax;

  if (cart_items.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="py-4 flex items-center justify-between">
              <h1 className="text-2xl font-bold text-gray-900">Carrito de Compras</h1>
              <CartIcon variant="default" />
            </div>
          </div>
        </div>

        {/* Empty Cart */}
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.5 5M7 13l-1.5 5m4.5-5h6m0 0v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m8 0V9a2 2 0 00-2-2H9a2 2 0 00-2-2"
                />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Tu carrito está vacío</h2>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              Parece que aún no has agregado ningún producto a tu carrito.
              ¡Explora nuestro catálogo y encuentra productos increíbles!
            </p>
            <button
              onClick={handleContinueShopping}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-medium transition-all duration-200 hover:shadow-lg transform hover:scale-105"
            >
              Explorar Productos
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-4 flex items-center justify-between">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900">Carrito de Compras</h1>
              <p className="text-sm text-gray-600 mt-1">
                {cart_count} {cart_count === 1 ? 'artículo' : 'artículos'} en tu carrito
              </p>
            </div>
            <CartIcon variant="default" />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="lg:grid lg:grid-cols-12 lg:gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-8">
            <div className="bg-white rounded-lg shadow-sm border">
              {/* Header */}
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">Productos</h2>
                  <button
                    onClick={clearCart}
                    className="text-red-600 hover:text-red-800 text-sm font-medium transition-colors"
                  >
                    Limpiar Carrito
                  </button>
                </div>
              </div>

              {/* Items List */}
              <div className="divide-y divide-gray-200">
                {cart_items.map((item) => (
                  <div key={item.id} className="p-6">
                    <div className="flex items-start space-x-4">
                      {/* Product Image */}
                      <div className="flex-shrink-0">
                        {item.image_url ? (
                          <img
                            src={item.image_url}
                            alt={item.name}
                            className="w-20 h-20 lg:w-24 lg:h-24 object-cover rounded-lg bg-gray-100"
                          />
                        ) : (
                          <div className="w-20 h-20 lg:w-24 lg:h-24 bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg flex items-center justify-center">
                            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                        <div className="lg:flex lg:items-start lg:justify-between">
                          <div className="flex-1">
                            <h3 className="text-lg font-medium text-gray-900 mb-1">
                              {item.name}
                            </h3>

                            {item.sku && (
                              <p className="text-sm text-gray-500 mb-1">SKU: {item.sku}</p>
                            )}

                            {item.vendor_name && (
                              <p className="text-sm text-gray-600 mb-2">
                                Vendido por: <span className="font-medium">{item.vendor_name}</span>
                              </p>
                            )}

                            {/* Variant attributes */}
                            {item.variant_attributes && Object.keys(item.variant_attributes).length > 0 && (
                              <div className="mb-3 space-y-1">
                                {Object.entries(item.variant_attributes).map(([key, value]) => (
                                  <span
                                    key={key}
                                    className="inline-block bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs mr-2"
                                  >
                                    {key}: {value}
                                  </span>
                                ))}
                              </div>
                            )}

                            {/* Stock warning */}
                            {item.stock_available && item.stock_available <= 5 && (
                              <div className="mb-3 text-sm text-orange-600 bg-orange-50 px-3 py-1 rounded-md inline-block">
                                ¡Solo quedan {item.stock_available}!
                              </div>
                            )}
                          </div>

                          {/* Price and Controls */}
                          <div className="mt-4 lg:mt-0 lg:ml-6 lg:text-right">
                            <div className="text-lg font-semibold text-gray-900 mb-3">
                              {formatCurrency(item.price * item.quantity)}
                            </div>
                            <div className="text-sm text-gray-500 mb-4">
                              {formatCurrency(item.price)} por unidad
                            </div>

                            {/* Quantity Controls */}
                            <div className="flex items-center justify-center lg:justify-end space-x-3 mb-3">
                              <button
                                onClick={() => updateQuantity(item.id, item.quantity - 1)}
                                className="w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center text-gray-600 hover:text-gray-800 transition-colors"
                                disabled={item.quantity <= 1}
                              >
                                −
                              </button>
                              <span className="w-12 text-center font-medium text-gray-900">
                                {item.quantity}
                              </span>
                              <button
                                onClick={() => updateQuantity(item.id, item.quantity + 1)}
                                className="w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center text-gray-600 hover:text-gray-800 transition-colors"
                                disabled={item.stock_available && item.quantity >= item.stock_available}
                              >
                                +
                              </button>
                            </div>

                            {/* Remove Button */}
                            <button
                              onClick={() => removeItem(item.id)}
                              className="text-red-600 hover:text-red-800 text-sm font-medium transition-colors"
                            >
                              Eliminar
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Continue Shopping */}
            <div className="mt-6">
              <button
                onClick={handleContinueShopping}
                className="text-blue-600 hover:text-blue-800 font-medium transition-colors flex items-center"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Continuar Comprando
              </button>
            </div>
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-4 mt-8 lg:mt-0">
            <div className="bg-white rounded-lg shadow-sm border p-6 sticky top-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Resumen del Pedido</h2>

              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Subtotal ({cart_count} artículos)</span>
                  <span className="font-medium">{formatCurrency(subtotal)}</span>
                </div>

                <div className="flex justify-between">
                  <span className="text-gray-600">Envío estimado</span>
                  <span className="font-medium">{formatCurrency(estimatedShipping)}</span>
                </div>

                <div className="flex justify-between">
                  <span className="text-gray-600">Impuestos estimados</span>
                  <span className="font-medium">{formatCurrency(estimatedTax)}</span>
                </div>

                <div className="border-t border-gray-200 pt-3">
                  <div className="flex justify-between text-lg font-semibold">
                    <span>Total estimado</span>
                    <span>{formatCurrency(estimatedTotal)}</span>
                  </div>
                </div>
              </div>

              <button
                onClick={handleCheckout}
                className="w-full mt-6 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white py-3 px-4 rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95"
              >
                {isAuthenticated ? 'Proceder al Checkout' : 'Iniciar Sesión y Checkout'}
              </button>

              {/* Trust badges */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center justify-center space-x-4 text-sm text-gray-600">
                  <div className="flex items-center space-x-1">
                    <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>Pago Seguro</span>
                  </div>

                  <div className="flex items-center space-x-1">
                    <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
                    </svg>
                    <span>Envío Rápido</span>
                  </div>
                </div>

                <p className="text-xs text-gray-500 mt-2 text-center">
                  Los impuestos y gastos de envío se calcularán al finalizar la compra
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartPage;