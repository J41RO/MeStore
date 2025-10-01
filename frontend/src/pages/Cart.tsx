import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShoppingCart, Plus, Minus, Trash2, ArrowRight, Package, ArrowLeft, X } from 'lucide-react';
import { useCartStore, formatCOP, hasFreeShipping, amountNeededForFreeShipping } from '../store/cartStore';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';

/**
 * Cart Page - Full Shopping Cart Experience
 *
 * Complete cart management page with:
 * - Detailed cart items table
 * - Quantity controls and item removal
 * - Colombian pricing (IVA, Shipping, Total)
 * - Free shipping progress indicator
 * - Order summary sidebar
 * - CTA buttons to continue shopping or checkout
 *
 * Features:
 * - Responsive design (table on desktop, cards on mobile)
 * - Stock validation
 * - Empty state with call-to-action
 * - Real-time calculations
 */
const Cart: React.FC = () => {
  const navigate = useNavigate();

  // Cart store
  const {
    cart_items,
    removeItem,
    updateQuantity,
    clearCart,
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

  const handleQuantityChange = (itemId: string, currentQuantity: number, change: number) => {
    const newQuantity = currentQuantity + change;
    if (newQuantity <= 0) {
      removeItem(itemId);
    } else {
      updateQuantity(itemId, newQuantity);
    }
  };

  const handleClearCart = () => {
    if (window.confirm('¿Estás seguro de que deseas vaciar tu carrito?')) {
      clearCart();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      {/* Page Content */}
      <main className="flex-1 pt-20 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                  <ShoppingCart className="w-8 h-8 text-blue-600" />
                  Carrito de Compras
                </h1>
                {totalItems > 0 && (
                  <p className="text-gray-600 mt-2">
                    {totalItems} {totalItems === 1 ? 'artículo' : 'artículos'} en tu carrito
                  </p>
                )}
              </div>

              {cart_items.length > 0 && (
                <button
                  onClick={handleClearCart}
                  className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors flex items-center gap-2"
                >
                  <X className="w-4 h-4" />
                  Vaciar Carrito
                </button>
              )}
            </div>

            {/* Back to Shopping */}
            <Link
              to="/marketplace"
              className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
            >
              <ArrowLeft className="w-4 h-4" />
              Continuar Comprando
            </Link>
          </div>

          {/* Free Shipping Progress */}
          {!freeShippingQualifies && subtotal > 0 && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-blue-800 font-medium">
                  🚚 Envío GRATIS desde {formatCOP(200000)}
                </span>
                <span className="text-blue-600 font-semibold">
                  Faltan {formatCOP(amountForFreeShipping)}
                </span>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-3">
                <div
                  className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min((subtotal / 200000) * 100, 100)}%` }}
                />
              </div>
            </div>
          )}

          {freeShippingQualifies && subtotal > 0 && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
              <Package className="w-6 h-6 text-green-600" />
              <span className="text-green-800 font-semibold">
                ¡Felicitaciones! Tienes envío GRATIS en este pedido
              </span>
            </div>
          )}

          {/* Empty Cart State */}
          {cart_items.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-12 text-center">
              <ShoppingCart className="w-24 h-24 text-gray-300 mx-auto mb-6" />
              <h2 className="text-2xl font-bold text-gray-900 mb-3">
                Tu carrito está vacío
              </h2>
              <p className="text-gray-600 mb-8 max-w-md mx-auto">
                Explora nuestro marketplace y encuentra productos increíbles de vendedores de confianza
              </p>
              <Link
                to="/marketplace"
                className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold rounded-lg hover:shadow-lg transition-all duration-200 transform hover:scale-105"
              >
                <ShoppingCart className="w-5 h-5" />
                Explorar Productos
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Cart Items - Left Side (2/3) */}
              <div className="lg:col-span-2">
                <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                  {/* Desktop Table View */}
                  <div className="hidden md:block overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                          <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                            Producto
                          </th>
                          <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                            Precio
                          </th>
                          <th className="px-6 py-4 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">
                            Cantidad
                          </th>
                          <th className="px-6 py-4 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                            Subtotal
                          </th>
                          <th className="px-6 py-4 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">
                            Acción
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {cart_items.map((item) => (
                          <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                            {/* Product Info */}
                            <td className="px-6 py-4">
                              <div className="flex items-center gap-4">
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
                                <div className="min-w-0 flex-1">
                                  <h3 className="text-sm font-semibold text-gray-900 mb-1">
                                    {item.name}
                                  </h3>
                                  {item.sku && (
                                    <p className="text-xs text-gray-500">SKU: {item.sku}</p>
                                  )}
                                  {item.vendor_name && (
                                    <p className="text-xs text-gray-500">Por: {item.vendor_name}</p>
                                  )}
                                </div>
                              </div>
                            </td>

                            {/* Price */}
                            <td className="px-6 py-4">
                              <span className="text-sm font-semibold text-gray-900">
                                {formatCOP(item.price)}
                              </span>
                            </td>

                            {/* Quantity Controls */}
                            <td className="px-6 py-4">
                              <div className="flex items-center justify-center gap-2">
                                <button
                                  onClick={() => handleQuantityChange(item.id, item.quantity, -1)}
                                  className="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 hover:border-gray-400 hover:bg-gray-50 transition-colors"
                                  aria-label="Disminuir cantidad"
                                >
                                  <Minus className="w-4 h-4 text-gray-600" />
                                </button>

                                <span className="w-12 text-center font-semibold text-gray-900">
                                  {item.quantity}
                                </span>

                                <button
                                  onClick={() => handleQuantityChange(item.id, item.quantity, 1)}
                                  disabled={item.quantity >= (item.max_stock || item.stock_available || 999)}
                                  className="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 hover:border-gray-400 hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                  aria-label="Aumentar cantidad"
                                >
                                  <Plus className="w-4 h-4 text-gray-600" />
                                </button>
                              </div>
                              {item.stock_available && item.stock_available < 10 && (
                                <p className="text-xs text-orange-600 text-center mt-1">
                                  Solo {item.stock_available} disponibles
                                </p>
                              )}
                            </td>

                            {/* Subtotal */}
                            <td className="px-6 py-4 text-right">
                              <span className="text-sm font-bold text-blue-600">
                                {formatCOP(item.price * item.quantity)}
                              </span>
                            </td>

                            {/* Remove Button */}
                            <td className="px-6 py-4 text-center">
                              <button
                                onClick={() => removeItem(item.id)}
                                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                aria-label="Eliminar producto"
                              >
                                <Trash2 className="w-5 h-5" />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Mobile Card View */}
                  <div className="md:hidden divide-y divide-gray-200">
                    {cart_items.map((item) => (
                      <div key={item.id} className="p-4">
                        <div className="flex gap-4">
                          {/* Image */}
                          <div className="flex-shrink-0 w-24 h-24 bg-gray-100 rounded-lg overflow-hidden">
                            {item.image_url ? (
                              <img
                                src={item.image_url}
                                alt={item.name}
                                className="w-full h-full object-cover"
                              />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center">
                                <Package className="w-10 h-10 text-gray-400" />
                              </div>
                            )}
                          </div>

                          {/* Info */}
                          <div className="flex-1 min-w-0">
                            <h3 className="text-sm font-semibold text-gray-900 mb-1">
                              {item.name}
                            </h3>
                            {item.sku && (
                              <p className="text-xs text-gray-500 mb-1">SKU: {item.sku}</p>
                            )}
                            <p className="text-sm font-bold text-blue-600 mb-2">
                              {formatCOP(item.price)}
                            </p>

                            {/* Quantity Controls */}
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() => handleQuantityChange(item.id, item.quantity, -1)}
                                  className="w-7 h-7 flex items-center justify-center rounded-full border border-gray-300 hover:border-gray-400"
                                >
                                  <Minus className="w-3.5 h-3.5" />
                                </button>
                                <span className="w-8 text-center font-semibold">{item.quantity}</span>
                                <button
                                  onClick={() => handleQuantityChange(item.id, item.quantity, 1)}
                                  disabled={item.quantity >= (item.max_stock || item.stock_available || 999)}
                                  className="w-7 h-7 flex items-center justify-center rounded-full border border-gray-300 hover:border-gray-400 disabled:opacity-50"
                                >
                                  <Plus className="w-3.5 h-3.5" />
                                </button>
                              </div>

                              <button
                                onClick={() => removeItem(item.id)}
                                className="p-2 text-red-600 hover:bg-red-50 rounded"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>

                            <div className="mt-2 text-right">
                              <span className="text-sm font-bold text-gray-900">
                                Subtotal: {formatCOP(item.price * item.quantity)}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Order Summary - Right Side (1/3) */}
              <div className="lg:col-span-1">
                <div className="bg-white rounded-xl shadow-sm p-6 sticky top-24">
                  <h2 className="text-xl font-bold text-gray-900 mb-6">Resumen del Pedido</h2>

                  {/* Summary Lines */}
                  <div className="space-y-3 mb-6">
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
                    <div className="border-t border-gray-300 pt-3 flex justify-between">
                      <span className="text-lg font-bold text-gray-900">Total:</span>
                      <span className="text-xl font-bold text-blue-600">{formatCOP(total)}</span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="space-y-3">
                    <button
                      onClick={() => navigate('/checkout')}
                      className="w-full py-3.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold rounded-lg hover:shadow-lg transition-all duration-200 transform hover:scale-105 flex items-center justify-center gap-2"
                    >
                      <span>Proceder al Checkout</span>
                      <ArrowRight className="w-5 h-5" />
                    </button>

                    <Link
                      to="/marketplace"
                      className="block w-full py-3 text-center bg-white text-blue-600 font-semibold rounded-lg border-2 border-blue-600 hover:bg-blue-50 transition-colors"
                    >
                      Continuar Comprando
                    </Link>
                  </div>

                  {/* Trust Badges */}
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <div className="space-y-3 text-sm text-gray-600">
                      <div className="flex items-center gap-2">
                        <span className="text-green-600">✓</span>
                        <span>Pago seguro</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-green-600">✓</span>
                        <span>Envío confiable</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-green-600">✓</span>
                        <span>Soporte 24/7</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default Cart;
