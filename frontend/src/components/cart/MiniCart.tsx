import React, { useEffect } from 'react';
import { X, ShoppingCart, Plus, Minus, Trash2, ArrowRight, Package } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useCartStore, formatCOP, hasFreeShipping, amountNeededForFreeShipping } from '../../store/cartStore';

/**
 * MiniCart Component - Slide-in Sidebar
 *
 * Displays cart items in a sidebar drawer with:
 * - List of cart items with quantity controls
 * - Order summary (Subtotal, IVA, Shipping, Total)
 * - Quick actions to view full cart or checkout
 *
 * Features:
 * - Colombian IVA calculation (19%)
 * - Free shipping indicator ($200,000 COP threshold)
 * - Stock validation
 * - Smooth animations
 * - Click outside to close
 * - ESC key to close
 */
const MiniCart: React.FC = () => {
  const navigate = useNavigate();

  // Cart store state
  const {
    cart_items,
    isDrawerOpen,
    closeDrawer,
    removeItem,
    updateQuantity,
    getSubtotal,
    getIVA,
    getShipping,
    getTotal,
    getTotalItems,
  } = useCartStore();

  const subtotal = getSubtotal();
  const iva = getIVA();
  const shipping = getShipping();
  const total = getTotal();
  const totalItems = getTotalItems();
  const freeShippingQualifies = hasFreeShipping(subtotal);
  const amountForFreeShipping = amountNeededForFreeShipping(subtotal);

  // Close drawer with ESC key
  useEffect(() => {
    const handleEscKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isDrawerOpen) {
        closeDrawer();
      }
    };

    document.addEventListener('keydown', handleEscKey);
    return () => document.removeEventListener('keydown', handleEscKey);
  }, [isDrawerOpen, closeDrawer]);

  // Prevent body scroll when drawer is open
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

  const handleQuantityChange = (itemId: string, currentQuantity: number, change: number) => {
    const newQuantity = currentQuantity + change;
    if (newQuantity <= 0) {
      removeItem(itemId);
    } else {
      updateQuantity(itemId, newQuantity);
    }
  };

  const handleViewCart = () => {
    closeDrawer();
    navigate('/cart');
  };

  const handleCheckout = () => {
    closeDrawer();
    navigate('/checkout');
  };

  if (!isDrawerOpen) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 transition-opacity duration-300"
        onClick={closeDrawer}
        aria-hidden="true"
      />

      {/* Drawer */}
      <div className="fixed right-0 top-0 bottom-0 w-full sm:w-[450px] bg-white shadow-2xl z-50 flex flex-col animate-slide-in-right">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50">
          <div className="flex items-center gap-2">
            <ShoppingCart className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-bold text-gray-900">
              Mi Carrito
            </h2>
            {totalItems > 0 && (
              <span className="ml-2 px-2.5 py-0.5 bg-blue-600 text-white text-sm font-semibold rounded-full">
                {totalItems}
              </span>
            )}
          </div>
          <button
            onClick={closeDrawer}
            className="p-2 hover:bg-white/50 rounded-full transition-colors"
            aria-label="Cerrar carrito"
          >
            <X className="w-6 h-6 text-gray-600" />
          </button>
        </div>

        {/* Free Shipping Progress */}
        {!freeShippingQualifies && subtotal > 0 && (
          <div className="px-6 py-3 bg-blue-50 border-b border-blue-100">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-blue-800 font-medium">
                Envío GRATIS desde {formatCOP(200000)}
              </span>
              <span className="text-blue-600 font-semibold">
                Faltan {formatCOP(amountForFreeShipping)}
              </span>
            </div>
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${Math.min((subtotal / 200000) * 100, 100)}%` }}
              />
            </div>
          </div>
        )}

        {freeShippingQualifies && (
          <div className="px-6 py-3 bg-green-50 border-b border-green-100 flex items-center gap-2">
            <Package className="w-5 h-5 text-green-600" />
            <span className="text-green-800 font-medium text-sm">
              ¡Felicitaciones! Tienes envío GRATIS
            </span>
          </div>
        )}

        {/* Cart Items */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {cart_items.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center py-12">
              <ShoppingCart className="w-20 h-20 text-gray-300 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Tu carrito está vacío
              </h3>
              <p className="text-gray-600 mb-6">
                Agrega productos para comenzar tu compra
              </p>
              <button
                onClick={() => {
                  closeDrawer();
                  navigate('/marketplace');
                }}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all duration-200 transform hover:scale-105"
              >
                Explorar Productos
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {cart_items.map((item) => (
                <div
                  key={item.id}
                  className="flex gap-4 pb-4 border-b border-gray-200 last:border-0"
                >
                  {/* Product Image */}
                  <div className="flex-shrink-0 w-20 h-20 bg-gray-100 rounded-lg overflow-hidden">
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
                    <h3 className="text-sm font-semibold text-gray-900 truncate mb-1">
                      {item.name}
                    </h3>
                    {item.sku && (
                      <p className="text-xs text-gray-500 mb-2">SKU: {item.sku}</p>
                    )}

                    <div className="flex items-center justify-between">
                      {/* Quantity Controls */}
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleQuantityChange(item.id, item.quantity, -1)}
                          className="w-7 h-7 flex items-center justify-center rounded-full border border-gray-300 hover:border-gray-400 hover:bg-gray-50 transition-colors"
                          aria-label="Disminuir cantidad"
                        >
                          <Minus className="w-3.5 h-3.5 text-gray-600" />
                        </button>

                        <span className="w-8 text-center font-semibold text-gray-900">
                          {item.quantity}
                        </span>

                        <button
                          onClick={() => handleQuantityChange(item.id, item.quantity, 1)}
                          disabled={item.quantity >= (item.max_stock || item.stock_available || 999)}
                          className="w-7 h-7 flex items-center justify-center rounded-full border border-gray-300 hover:border-gray-400 hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          aria-label="Aumentar cantidad"
                        >
                          <Plus className="w-3.5 h-3.5 text-gray-600" />
                        </button>
                      </div>

                      {/* Remove Button */}
                      <button
                        onClick={() => removeItem(item.id)}
                        className="p-1.5 text-red-600 hover:bg-red-50 rounded transition-colors"
                        aria-label="Eliminar producto"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    {/* Price */}
                    <div className="mt-2 flex items-center justify-between">
                      <span className="text-xs text-gray-600">
                        {formatCOP(item.price)} c/u
                      </span>
                      <span className="text-sm font-bold text-blue-600">
                        {formatCOP(item.price * item.quantity)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Summary Footer */}
        {cart_items.length > 0 && (
          <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
            {/* Summary Lines */}
            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Subtotal:</span>
                <span className="font-semibold text-gray-900">{formatCOP(subtotal)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">IVA (19%):</span>
                <span className="font-semibold text-gray-900">{formatCOP(iva)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Envío:</span>
                <span className={`font-semibold ${shipping === 0 ? 'text-green-600' : 'text-gray-900'}`}>
                  {shipping === 0 ? 'GRATIS' : formatCOP(shipping)}
                </span>
              </div>
              <div className="flex justify-between text-base pt-2 border-t border-gray-300">
                <span className="font-bold text-gray-900">Total:</span>
                <span className="font-bold text-blue-600 text-lg">{formatCOP(total)}</span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="space-y-2">
              <button
                onClick={handleCheckout}
                className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold rounded-lg hover:shadow-lg transition-all duration-200 transform hover:scale-105 flex items-center justify-center gap-2"
              >
                <span>Ir al Checkout</span>
                <ArrowRight className="w-5 h-5" />
              </button>

              <button
                onClick={handleViewCart}
                className="w-full py-2.5 bg-white text-blue-600 font-semibold rounded-lg border-2 border-blue-600 hover:bg-blue-50 transition-colors"
              >
                Ver Carrito Completo
              </button>
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes slide-in-right {
          from {
            transform: translateX(100%);
          }
          to {
            transform: translateX(0);
          }
        }

        .animate-slide-in-right {
          animation: slide-in-right 0.3s ease-out;
        }
      `}</style>
    </>
  );
};

export default MiniCart;
