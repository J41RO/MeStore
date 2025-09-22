import React, { useEffect } from 'react';
import { useCheckoutStore } from '../stores/checkoutStore';
import { useAuthStore } from '../stores/authStore';
import AddToCartButton from '../components/cart/AddToCartButton';
import CartIcon from '../components/cart/CartIcon';

const CheckoutDemo: React.FC = () => {
  const { cart_items, cart_count, clearCart } = useCheckoutStore();
  const { isAuthenticated, user, login } = useAuthStore();

  // Sample products for demo
  const sampleProducts = [
    {
      id: 'prod-1',
      name: 'MacBook Pro 14" M3',
      price: 8500000,
      image_url: 'https://via.placeholder.com/200x200/007ACC/FFFFFF?text=MacBook',
      sku: 'MBP-14-M3',
      stock_available: 5,
      vendor_id: 'vendor-1',
      vendor_name: 'Apple Store Colombia'
    },
    {
      id: 'prod-2',
      name: 'iPhone 15 Pro 128GB',
      price: 5200000,
      image_url: 'https://via.placeholder.com/200x200/FF6B6B/FFFFFF?text=iPhone',
      sku: 'IPH-15-PRO-128',
      stock_available: 10,
      vendor_id: 'vendor-1',
      vendor_name: 'Apple Store Colombia'
    },
    {
      id: 'prod-3',
      name: 'Samsung Galaxy S24 Ultra',
      price: 4800000,
      image_url: 'https://via.placeholder.com/200x200/4ECDC4/FFFFFF?text=Galaxy',
      sku: 'SAM-S24-ULTRA',
      stock_available: 8,
      vendor_id: 'vendor-2',
      vendor_name: 'Samsung Store'
    },
    {
      id: 'prod-4',
      name: 'Sony WH-1000XM5',
      price: 1200000,
      image_url: 'https://via.placeholder.com/200x200/45B7D1/FFFFFF?text=Sony',
      sku: 'SONY-WH1000XM5',
      stock_available: 15,
      vendor_id: 'vendor-3',
      vendor_name: 'TechSound'
    }
  ];

  const handleTestLogin = async () => {
    const success = await login('buyer@test.com', 'test123');
    if (success) {
      console.log('✅ Login exitoso como buyer');
    } else {
      console.log('❌ Error en login');
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">MeStore - Checkout Demo</h1>
              <p className="text-gray-600">Prueba el flujo completo de checkout</p>
            </div>

            <div className="flex items-center space-x-4">
              {/* Cart Icon */}
              <CartIcon />

              {/* User Info */}
              {isAuthenticated && user ? (
                <div className="text-sm">
                  <span className="text-gray-600">Hola, </span>
                  <span className="font-medium text-gray-900">{user.name || user.email}</span>
                </div>
              ) : (
                <button
                  onClick={handleTestLogin}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Iniciar Sesión (Demo)
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Demo Instructions */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <h2 className="text-lg font-semibold text-blue-900 mb-3">
            🚀 Demo del Flujo de Checkout
          </h2>
          <div className="text-sm text-blue-800 space-y-2">
            <p><strong>1.</strong> Inicia sesión con el botón de demo (credenciales: buyer@test.com)</p>
            <p><strong>2.</strong> Agrega productos al carrito usando los botones "Agregar al Carrito"</p>
            <p><strong>3.</strong> Haz clic en el ícono del carrito para ver el resumen</p>
            <p><strong>4.</strong> Procede al checkout para probar el flujo completo:</p>
            <ul className="ml-6 space-y-1">
              <li>• Paso 1: Revisar carrito y productos</li>
              <li>• Paso 2: Información de envío y direcciones</li>
              <li>• Paso 3: Método de pago (PSE, Tarjeta, etc.)</li>
              <li>• Paso 4: Confirmación y finalización</li>
            </ul>
          </div>
        </div>

        {/* Cart Summary */}
        {cart_count > 0 && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-green-900">
                  Tienes {cart_count} producto{cart_count === 1 ? '' : 's'} en tu carrito
                </h3>
                <p className="text-green-700 text-sm">Total: {formatCurrency(cart_items.reduce((total, item) => total + (item.price * item.quantity), 0))}</p>
              </div>
              <div className="space-x-3">
                <button
                  onClick={clearCart}
                  className="text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  Limpiar Carrito
                </button>
                <button
                  onClick={() => window.location.href = '/checkout'}
                  className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Ir al Checkout →
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Products Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {sampleProducts.map((product) => (
            <div key={product.id} className="bg-white rounded-lg shadow-sm border overflow-hidden">
              <div className="aspect-square bg-gray-100 p-4">
                <img
                  src={product.image_url}
                  alt={product.name}
                  className="w-full h-full object-cover rounded-md"
                />
              </div>

              <div className="p-4">
                <h3 className="font-semibold text-gray-900 text-lg mb-1">{product.name}</h3>
                <p className="text-sm text-gray-600 mb-2">Por: {product.vendor_name}</p>
                <p className="text-xs text-gray-500 mb-3">SKU: {product.sku}</p>

                <div className="flex items-center justify-between mb-4">
                  <div className="text-2xl font-bold text-gray-900">
                    {formatCurrency(product.price)}
                  </div>
                  <div className="text-sm text-gray-500">
                    Stock: {product.stock_available}
                  </div>
                </div>

                <AddToCartButton
                  product={product}
                  quantity={1}
                  className="w-full"
                  size="md"
                />
              </div>
            </div>
          ))}
        </div>

        {/* Feature Highlights */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.5 5M7 13l-1.5 5m4.5-5h6m0 0v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m8 0V9a2 2 0 00-2-2H9a2 2 0 00-2-2" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Carrito Inteligente</h3>
            <p className="text-gray-600 text-sm">
              Gestión de productos con variantes, stock en tiempo real y persistencia de sesión.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Envío Inteligente</h3>
            <p className="text-gray-600 text-sm">
              Gestión de direcciones múltiples, cálculo automático de costos y seguimiento en tiempo real.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Pagos Seguros</h3>
            <p className="text-gray-600 text-sm">
              Integración con PSE, tarjetas de crédito, y múltiples métodos de pago con seguridad bancaria.
            </p>
          </div>
        </div>

        {/* Technical Details */}
        <div className="mt-12 bg-gray-800 rounded-lg p-8 text-white">
          <h2 className="text-xl font-bold mb-4">🔧 Detalles Técnicos</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
            <div>
              <h3 className="font-semibold mb-2">Frontend Stack:</h3>
              <ul className="space-y-1 text-gray-300">
                <li>• React 18 + TypeScript</li>
                <li>• Zustand para estado global</li>
                <li>• Tailwind CSS para estilos</li>
                <li>• React Router para navegación</li>
                <li>• Vite para desarrollo y build</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Características:</h3>
              <ul className="space-y-1 text-gray-300">
                <li>• Checkout multi-paso responsive</li>
                <li>• Integración con Payment Systems AI</li>
                <li>• Gestión de direcciones persistente</li>
                <li>• Validación en tiempo real</li>
                <li>• Manejo de errores robusto</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CheckoutDemo;