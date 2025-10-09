import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { Product } from '../types';

// Cart Item extends Product with quantity
export interface CartItem extends Product {
  quantity: number;
}

// Cart Context Interface
interface CartContextType {
  items: CartItem[];
  itemCount: number;
  totalAmount: number;
  isOpen: boolean;

  // Actions
  addItem: (product: Product, quantity?: number) => void;
  removeItem: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
  openCart: () => void;
  closeCart: () => void;
  toggleCart: () => void;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

// Hook personalizado para usar el carrito
export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within CartProvider');
  }
  return context;
};

interface CartProviderProps {
  children: ReactNode;
}

// Provider del carrito
export const CartProvider: React.FC<CartProviderProps> = ({ children }) => {
  const [items, setItems] = useState<CartItem[]>([]);
  const [isOpen, setIsOpen] = useState(false);

  // Load cart from localStorage on mount
  useEffect(() => {
    const savedCart = localStorage.getItem('mestore_cart');
    if (savedCart) {
      try {
        const parsedCart = JSON.parse(savedCart);
        setItems(parsedCart);
      } catch (error) {
        console.error('Error loading cart from localStorage:', error);
      }
    }
  }, []);

  // Save cart to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('mestore_cart', JSON.stringify(items));
  }, [items]);

  // Calculate derived values
  const itemCount = items.reduce((total, item) => total + item.quantity, 0);
  const totalAmount = items.reduce((total, item) => total + (item.precio_venta * item.quantity), 0);

  // Add item to cart
  const addItem = (product: Product, quantity: number = 1) => {
    setItems(currentItems => {
      // Check if product already exists in cart
      const existingItemIndex = currentItems.findIndex(item => item.id === product.id);

      if (existingItemIndex > -1) {
        // Update quantity of existing item
        const updatedItems = [...currentItems];
        const newQuantity = updatedItems[existingItemIndex].quantity + quantity;

        // Don't exceed stock
        if (newQuantity > product.stock) {
          console.warn(`Cannot add more items. Stock limit: ${product.stock}`);
          updatedItems[existingItemIndex].quantity = product.stock;
        } else {
          updatedItems[existingItemIndex].quantity = newQuantity;
        }

        return updatedItems;
      } else {
        // Add new item to cart
        const newItem: CartItem = {
          ...product,
          quantity: Math.min(quantity, product.stock)
        };
        return [...currentItems, newItem];
      }
    });

    // Open cart drawer when item is added
    setIsOpen(true);

    // Show notification (could be replaced with toast notification)
    console.log(`Added ${quantity}x ${product.name} to cart`);
  };

  // Remove item from cart
  const removeItem = (productId: string) => {
    setItems(currentItems => currentItems.filter(item => item.id !== productId));
  };

  // Update quantity of item in cart
  const updateQuantity = (productId: string, quantity: number) => {
    if (quantity < 1) {
      removeItem(productId);
      return;
    }

    setItems(currentItems => {
      const itemIndex = currentItems.findIndex(item => item.id === productId);

      if (itemIndex === -1) return currentItems;

      const updatedItems = [...currentItems];
      const item = updatedItems[itemIndex];

      // Don't exceed stock
      if (quantity > item.stock) {
        console.warn(`Cannot set quantity to ${quantity}. Stock limit: ${item.stock}`);
        updatedItems[itemIndex].quantity = item.stock;
      } else {
        updatedItems[itemIndex].quantity = quantity;
      }

      return updatedItems;
    });
  };

  // Clear all items from cart
  const clearCart = () => {
    setItems([]);
    localStorage.removeItem('mestore_cart');
  };

  // Drawer controls
  const openCart = () => setIsOpen(true);
  const closeCart = () => setIsOpen(false);
  const toggleCart = () => setIsOpen(prev => !prev);

  const value: CartContextType = {
    items,
    itemCount,
    totalAmount,
    isOpen,
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
    openCart,
    closeCart,
    toggleCart
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};

export default CartContext;
