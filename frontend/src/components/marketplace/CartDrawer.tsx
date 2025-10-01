/**
 * CartDrawer Component - Sliding Cart Panel
 * MeStore Marketplace - Colombian E-commerce
 *
 * Features:
 * - Sliding animation from right
 * - Cart item management
 * - Colombian pricing (IVA 19%)
 * - Shipping calculation
 * - Mobile responsive
 * - Accessibility support
 */

import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Plus,
  Minus,
  Trash2,
  ShoppingCart,
  ArrowRight,
  Package,
  Truck,
} from 'lucide-react';
import {
  useCartStore,
  formatCOP,
  hasFreeShipping,
  amountNeededForFreeShipping,
} from '../../store/cartStore';

// ========================================
// COMPONENT
// ========================================

const CartDrawer: React.FC = () => {
  const navigate = useNavigate();

  // Cart store
  const {
    cart_items: items, // Use cart_items from unified store, alias as items
    isDrawerOpen,
    closeDrawer,
    removeItem,
    updateQuantity,
    clearCart,
    getSubtotal,
    getIVA,
    getShipping,
    getTotal,
    getTotalItems,
  } = useCartStore();

  // Lock body scroll when drawer is open
  useEffect(() => {
    if (isDrawerOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isDrawerOpen]);

  // Calculations
  const subtotal = getSubtotal();
  const iva = getIVA();
  const shipping = getShipping();
  const total = getTotal();
  const totalItems = getTotalItems();
  const freeShipping = hasFreeShipping(subtotal);
  const amountForFreeShipping = amountNeededForFreeShipping(subtotal);

  // Handlers
  const handleCheckout = () => {
    closeDrawer();
    navigate('/checkout');
  };

  const handleContinueShopping = () => {
    closeDrawer();
  };

  const handleIncreaseQuantity = (itemId: string, currentQuantity: number) => {
    updateQuantity(itemId, currentQuantity + 1);
  };

  const handleDecreaseQuantity = (itemId: string, currentQuantity: number) => {
    if (currentQuantity > 1) {
      updateQuantity(itemId, currentQuantity - 1);
    }
  };

  const handleRemoveItem = (itemId: string) => {
    removeItem(itemId);
  };

  const handleClearCart = () => {
    if (window.confirm('¿Estás seguro de vaciar el carrito?')) {
      clearCart();
    }
  };

  // Empty state
  const EmptyCart = () => (
    <div className="flex flex-col items-center justify-center h-full py-20 px-6">
      <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-6">
        <ShoppingCart className="w-12 h-12 text-gray-400" />
      </div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">
        Tu carrito está vacío
      </h3>
      <p className="text-gray-500 text-center mb-8">
        Agrega productos al carrito para comenzar tu compra
      </p>
      <button
        onClick={handleContinueShopping}
        className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
      >
        Explorar Productos
      </button>
    </div>
  );

  return (
    <>
      {/* Backdrop Overlay */}
      <AnimatePresence>
        {isDrawerOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            onClick={closeDrawer}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            aria-hidden="true"
          />
        )}
      </AnimatePresence>

      {/* Drawer Panel */}
      <AnimatePresence>
        {isDrawerOpen && (
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 h-full w-full sm:w-[480px] bg-white shadow-2xl z-50 flex flex-col"
            role="dialog"
            aria-labelledby="cart-drawer-title"
            aria-modal="true"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <ShoppingCart className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h2 id="cart-drawer-title" className="text-lg font-bold text-gray-900">
                    Mi Carrito
                  </h2>
                  <p className="text-sm text-gray-500">
                    {totalItems} {totalItems === 1 ? 'artículo' : 'artículos'}
                  </p>
                </div>
              </div>
              <button
                onClick={closeDrawer}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                aria-label="Cerrar carrito"
              >
                <X className="w-6 h-6 text-gray-600" />
              </button>
            </div>

            {/* Content */}
            {items.length === 0 ? (
              <EmptyCart />
            ) : (
              <>
                {/* Free Shipping Progress */}
                {!freeShipping && amountForFreeShipping > 0 && (
                  <div className="p-4 bg-blue-50 border-b border-blue-100">
                    <div className="flex items-start space-x-3">
                      <Truck className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-blue-900">
                          ¡Estás cerca del envío gratis!
                        </p>
                        <p className="text-xs text-blue-700 mt-1">
                          Agrega {formatCOP(amountForFreeShipping)} más para envío gratis
                        </p>
                        <div className="w-full bg-blue-200 rounded-full h-2 mt-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{
                              width: `${Math.min((subtotal / 200000) * 100, 100)}%`,
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Cart Items */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {items.map((item) => (
                    <motion.div
                      key={item.id}
                      layout
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, x: -100 }}
                      className="flex space-x-4 bg-gray-50 p-3 rounded-lg border border-gray-200"
                    >
                      {/* Product Image */}
                      <div className="w-20 h-20 bg-white rounded-lg overflow-hidden flex-shrink-0 border border-gray-200">
                        {item.image_url ? (
                          <img
                            src={item.image_url}
                            alt={item.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <Package className="w-8 h-8 text-gray-400" />
                          </div>
                        )}
                      </div>

                      {/* Product Info */}
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-semibold text-gray-900 truncate">
                          {item.name}
                        </h3>
                        <p className="text-xs text-gray-500 mt-1">SKU: {item.sku}</p>

                        {/* Price */}
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-sm font-bold text-blue-600">
                            {formatCOP(item.price)}
                          </span>

                          {/* Quantity Controls */}
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() =>
                                handleDecreaseQuantity(item.id, item.quantity)
                              }
                              disabled={item.quantity <= 1}
                              className="w-7 h-7 flex items-center justify-center rounded-full border border-gray-300 hover:border-gray-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                              aria-label="Disminuir cantidad"
                            >
                              <Minus className="w-3 h-3" />
                            </button>

                            <span className="w-8 text-center text-sm font-semibold">
                              {item.quantity}
                            </span>

                            <button
                              onClick={() =>
                                handleIncreaseQuantity(item.id, item.quantity)
                              }
                              disabled={
                                item.max_stock ? item.quantity >= item.max_stock : false
                              }
                              className="w-7 h-7 flex items-center justify-center rounded-full border border-gray-300 hover:border-gray-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                              aria-label="Aumentar cantidad"
                            >
                              <Plus className="w-3 h-3" />
                            </button>
                          </div>
                        </div>

                        {/* Subtotal & Remove */}
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-xs text-gray-600">
                            Subtotal: {formatCOP(item.price * item.quantity)}
                          </span>

                          <button
                            onClick={() => handleRemoveItem(item.id)}
                            className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
                            aria-label="Eliminar producto"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>

                {/* Footer - Summary & Actions */}
                <div className="border-t border-gray-200 bg-white p-4 space-y-4">
                  {/* Price Breakdown */}
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between text-gray-600">
                      <span>Subtotal:</span>
                      <span>{formatCOP(subtotal)}</span>
                    </div>
                    <div className="flex justify-between text-gray-600">
                      <span>IVA (19%):</span>
                      <span>{formatCOP(iva)}</span>
                    </div>
                    <div className="flex justify-between text-gray-600">
                      <div className="flex items-center space-x-1">
                        <Truck className="w-4 h-4" />
                        <span>Envío:</span>
                      </div>
                      <span className={freeShipping ? 'text-green-600 font-semibold' : ''}>
                        {freeShipping ? '¡GRATIS!' : formatCOP(shipping)}
                      </span>
                    </div>

                    <div className="h-px bg-gray-200 my-2" />

                    <div className="flex justify-between text-lg font-bold text-gray-900">
                      <span>Total:</span>
                      <span className="text-blue-600">{formatCOP(total)}</span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="space-y-2">
                    <button
                      onClick={handleCheckout}
                      className="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-all duration-200 flex items-center justify-center space-x-2 transform hover:scale-105"
                    >
                      <span>Ir al Checkout</span>
                      <ArrowRight className="w-5 h-5" />
                    </button>

                    <button
                      onClick={handleContinueShopping}
                      className="w-full py-2 text-blue-600 font-medium rounded-lg border border-blue-600 hover:bg-blue-50 transition-colors"
                    >
                      Seguir Comprando
                    </button>

                    <button
                      onClick={handleClearCart}
                      className="w-full py-2 text-red-600 text-sm hover:bg-red-50 rounded-lg transition-colors"
                    >
                      Vaciar Carrito
                    </button>
                  </div>
                </div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default CartDrawer;
