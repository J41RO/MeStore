import React, { useState, useEffect } from 'react';
import { ShoppingCart, Plus, Minus, Check, AlertCircle } from 'lucide-react';

interface AddToCartButtonProps {
  productId: number;
  price: number;
  stock: number;
  onAddToCart: (quantity: number) => void;
  disabled?: boolean;
}

interface CartItem {
  productId: number;
  quantity: number;
  price: number;
  addedAt: string;
}

const AddToCartButton: React.FC<AddToCartButtonProps> = ({
  productId,
  price,
  stock,
  onAddToCart,
  disabled = false
}) => {
  const [quantity, setQuantity] = useState(1);
  const [isAdding, setIsAdding] = useState(false);
  const [justAdded, setJustAdded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cartItems, setCartItems] = useState<CartItem[]>([]);

  // Load cart from localStorage on component mount
  useEffect(() => {
    loadCartFromStorage();
  }, []);

  const loadCartFromStorage = () => {
    try {
      const cartData = localStorage.getItem('mestore_cart');
      if (cartData) {
        const items = JSON.parse(cartData) as CartItem[];
        setCartItems(items);
      }
    } catch (error) {
      console.error('Error loading cart from localStorage:', error);
      setCartItems([]);
    }
  };

  const saveCartToStorage = (items: CartItem[]) => {
    try {
      localStorage.setItem('mestore_cart', JSON.stringify(items));
      setCartItems(items);
    } catch (error) {
      console.error('Error saving cart to localStorage:', error);
      setError('Error al guardar en el carrito');
    }
  };

  const getCurrentCartQuantity = () => {
    const existingItem = cartItems.find(item => item.productId === productId);
    return existingItem ? existingItem.quantity : 0;
  };


  const handleQuantityChange = (change: number) => {
    const newQuantity = Math.max(1, Math.min(stock, quantity + change));
    
    // Check if total quantity (existing + new) would exceed stock
    const currentInCart = getCurrentCartQuantity();
    const maxNewQuantity = stock - currentInCart;
    
    if (maxNewQuantity <= 0) {
      setError('No hay más stock disponible');
      return;
    }
    
    const finalQuantity = Math.min(newQuantity, maxNewQuantity);
    setQuantity(finalQuantity);
    setError(null);
  };

  const handleAddToCart = async () => {
    if (disabled || stock <= 0) {
      setError('Producto no disponible');
      return;
    }

    const currentInCart = getCurrentCartQuantity();
    const totalQuantity = currentInCart + quantity;

    if (totalQuantity > stock) {
      setError(`Solo hay ${stock} unidades disponibles (${currentInCart} ya en carrito)`);
      return;
    }

    setIsAdding(true);
    setError(null);

    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 500));

      // Update cart in localStorage
      const updatedCartItems = [...cartItems];
      const existingItemIndex = updatedCartItems.findIndex(item => item.productId === productId);

      if (existingItemIndex >= 0) {
        // Update existing item
        const existingItem = updatedCartItems[existingItemIndex];
        if (existingItem) {
          updatedCartItems[existingItemIndex] = {
            ...existingItem,
            quantity: existingItem.quantity + quantity,
            addedAt: new Date().toISOString()
          };
        }
      } else {
        // Add new item
        updatedCartItems.push({
          productId,
          quantity,
          price,
          addedAt: new Date().toISOString()
        });
      }

      saveCartToStorage(updatedCartItems);
      
      // Call parent callback
      onAddToCart(quantity);

      // Show success state
      setJustAdded(true);
      setQuantity(1);
      
      // Reset success state after 2 seconds
      setTimeout(() => {
        setJustAdded(false);
      }, 2000);

    } catch (err) {
      setError('Error al agregar al carrito');
    } finally {
      setIsAdding(false);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price);
  };

  const currentInCart = getCurrentCartQuantity();
  const availableStock = stock - currentInCart;
  const totalPrice = price * quantity;

  // If no stock available
  if (stock <= 0 || disabled) {
    return (
      <div className="space-y-3">
        <div className="text-center py-4 px-6 bg-gray-100 rounded-lg">
          <AlertCircle className="h-6 w-6 text-gray-500 mx-auto mb-2" />
          <p className="text-gray-600 font-medium">Producto agotado</p>
          <p className="text-sm text-gray-500">No hay stock disponible</p>
        </div>
      </div>
    );
  }

  // If all available stock is already in cart
  if (availableStock <= 0) {
    return (
      <div className="space-y-3">
        <div className="text-center py-4 px-6 bg-blue-50 rounded-lg border border-blue-200">
          <Check className="h-6 w-6 text-blue-600 mx-auto mb-2" />
          <p className="text-blue-800 font-medium">Ya en tu carrito</p>
          <p className="text-sm text-blue-600">
            {currentInCart} unidad{currentInCart !== 1 ? 'es' : ''} agregada{currentInCart !== 1 ? 's' : ''}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Quantity Selector */}
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Cantidad:
        </label>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => handleQuantityChange(-1)}
            disabled={quantity <= 1}
            className="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 hover:border-gray-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Minus className="h-4 w-4" />
          </button>
          
          <span className="w-12 text-center font-semibold text-lg">
            {quantity}
          </span>
          
          <button
            onClick={() => handleQuantityChange(1)}
            disabled={quantity >= availableStock}
            className="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 hover:border-gray-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Stock Info */}
      {currentInCart > 0 && (
        <div className="text-sm text-blue-600 text-center">
          Ya tienes {currentInCart} unidad{currentInCart !== 1 ? 'es' : ''} en tu carrito
        </div>
      )}

      <div className="text-sm text-gray-500 text-center">
        {availableStock} unidad{availableStock !== 1 ? 'es' : ''} disponible{availableStock !== 1 ? 's' : ''}
      </div>

      {/* Total Price */}
      <div className="text-center">
        <div className="text-sm text-gray-600">Total:</div>
        <div className="text-2xl font-bold text-blue-600">
          {formatPrice(totalPrice)}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="text-sm text-red-600 text-center bg-red-50 py-2 px-3 rounded-md">
          {error}
        </div>
      )}

      {/* Add to Cart Button */}
      <button
        onClick={handleAddToCart}
        disabled={isAdding || disabled || availableStock <= 0}
        className={`w-full py-3 px-6 rounded-lg font-semibold text-lg transition-all duration-200 flex items-center justify-center space-x-2 ${
          justAdded
            ? 'bg-green-600 text-white'
            : isAdding
            ? 'bg-blue-400 text-white cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700 transform hover:scale-105'
        } ${
          disabled || availableStock <= 0 ? 'opacity-50 cursor-not-allowed' : ''
        }`}
      >
        {isAdding ? (
          <>
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            <span>Agregando...</span>
          </>
        ) : justAdded ? (
          <>
            <Check className="h-5 w-5" />
            <span>¡Agregado al carrito!</span>
          </>
        ) : (
          <>
            <ShoppingCart className="h-5 w-5" />
            <span>Agregar al carrito</span>
          </>
        )}
      </button>

      {/* Buy Now Button (Optional) */}
      <button className="w-full py-2 px-6 rounded-lg font-medium text-blue-600 border border-blue-600 hover:bg-blue-50 transition-colors">
        Comprar ahora
      </button>
    </div>
  );
};

export default AddToCartButton;