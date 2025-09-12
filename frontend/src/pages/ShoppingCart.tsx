import React, { useState, useEffect } from 'react';
import { ShoppingCart as CartIcon, ArrowLeft, Trash2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import MarketplaceLayout from '../components/marketplace/MarketplaceLayout';
import CartItemList from '../components/marketplace/CartItemList';
import CartSummary from '../components/marketplace/CartSummary';

interface CartItem {
  productId: number;
  quantity: number;
  price: number;
  addedAt: string;
}

const ShoppingCart: React.FC = () => {
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Cargar items del localStorage al montar el componente
  useEffect(() => {
    loadCartItems();
  }, []);

  const loadCartItems = () => {
    try {
      setLoading(true);
      setError(null);
      
      const cartData = localStorage.getItem('mestore_cart');
      if (cartData) {
        const items = JSON.parse(cartData) as CartItem[];
        setCartItems(items);
      } else {
        setCartItems([]);
      }
    } catch (err) {
      console.error('Error loading cart from localStorage:', err);
      setError('Error al cargar el carrito. Por favor, recarga la página.');
      setCartItems([]);
    } finally {
      setLoading(false);
    }
  };

  const updateCartQuantity = (productId: number, newQuantity: number) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
      return;
    }

    try {
      const updatedItems = cartItems.map(item =>
        item.productId === productId
          ? { ...item, quantity: newQuantity }
          : item
      );

      setCartItems(updatedItems);
      localStorage.setItem('mestore_cart', JSON.stringify(updatedItems));
    } catch (err) {
      console.error('Error updating cart quantity:', err);
      setError('Error al actualizar la cantidad.');
    }
  };

  const removeFromCart = (productId: number) => {
    try {
      const updatedItems = cartItems.filter(item => item.productId !== productId);
      setCartItems(updatedItems);
      localStorage.setItem('mestore_cart', JSON.stringify(updatedItems));
    } catch (err) {
      console.error('Error removing item from cart:', err);
      setError('Error al eliminar el producto.');
    }
  };

  const clearCart = () => {
    try {
      setCartItems([]);
      localStorage.removeItem('mestore_cart');
    } catch (err) {
      console.error('Error clearing cart:', err);
      setError('Error al vaciar el carrito.');
    }
  };

  const calculateSubtotal = (): number => {
    return cartItems.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  const calculateTax = (subtotal: number): number => {
    return subtotal * 0.19; // IVA 19%
  };

  const calculateTotal = (): number => {
    const subtotal = calculateSubtotal();
    const tax = calculateTax(subtotal);
    return subtotal + tax;
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price);
  };

  const getTotalItems = (): number => {
    return cartItems.reduce((total, item) => total + item.quantity, 0);
  };

  const handleProceedToCheckout = () => {
    // TODO: Implementar navegación al checkout
    alert('Funcionalidad de checkout en desarrollo. Total: ' + formatPrice(calculateTotal()));
  };

  if (loading) {
    return (
      <MarketplaceLayout>
        <div className="min-h-screen bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="animate-pulse">
              <div className="h-8 bg-gray-200 rounded w-48 mb-6"></div>
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </MarketplaceLayout>
    );
  }

  return (
    <MarketplaceLayout>
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header del carrito */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-4">
              <Link 
                to="/marketplace" 
                className="flex items-center text-blue-600 hover:text-blue-700 transition-colors"
              >
                <ArrowLeft className="h-5 w-5 mr-2" />
                <span>Continuar comprando</span>
              </Link>
            </div>
            
            <div className="flex items-center space-x-4">
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <CartIcon className="h-8 w-8 mr-3 text-blue-600" />
                Mi Carrito
                {cartItems.length > 0 && (
                  <span className="ml-2 text-lg font-medium text-gray-500">
                    ({getTotalItems()} {getTotalItems() === 1 ? 'producto' : 'productos'})
                  </span>
                )}
              </h1>
              
              {cartItems.length > 0 && (
                <button
                  onClick={clearCart}
                  className="flex items-center px-4 py-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Vaciar carrito
                </button>
              )}
            </div>
          </div>

          {/* Mensaje de error */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600">{error}</p>
              <button
                onClick={() => setError(null)}
                className="mt-2 text-sm text-red-500 hover:text-red-700 underline"
              >
                Cerrar
              </button>
            </div>
          )}

          {/* Carrito vacío */}
          {cartItems.length === 0 ? (
            <div className="text-center py-16">
              <CartIcon className="h-24 w-24 mx-auto text-gray-300 mb-6" />
              <h2 className="text-2xl font-medium text-gray-600 mb-4">
                Tu carrito está vacío
              </h2>
              <p className="text-gray-500 mb-8 max-w-md mx-auto">
                Explora nuestro marketplace y encuentra productos increíbles para agregar a tu carrito.
              </p>
              <Link
                to="/marketplace"
                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                <CartIcon className="h-5 w-5 mr-2" />
                Explorar productos
              </Link>
            </div>
          ) : (
            /* Contenido del carrito con componentes integrados */
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Lista de productos */}
              <div className="lg:col-span-2">
                <CartItemList
                  items={cartItems}
                  onUpdateQuantity={updateCartQuantity}
                  onRemoveItem={removeFromCart}
                  onClearCart={clearCart}
                  loading={false}
                />
              </div>

              {/* Resumen del carrito */}
              <div className="lg:col-span-1">
                <CartSummary
                  items={cartItems}
                  onProceedToCheckout={handleProceedToCheckout}
                  loading={false}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </MarketplaceLayout>
  );
};

export default ShoppingCart;