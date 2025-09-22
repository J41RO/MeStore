import React, { useState, useEffect, useCallback } from 'react';
import { useCheckoutStore } from '../../stores/checkoutStore';
import CartSidebar from './CartSidebar';
import MobileCartDrawer from './MobileCartDrawer';

interface CartIconProps {
  variant?: 'default' | 'mobile';
  className?: string;
}

const CartIcon: React.FC<CartIconProps> = ({ variant = 'default', className = '' }) => {
  const { cart_count, cart_total } = useCheckoutStore();
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Detect mobile device
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Animate when cart count changes
  useEffect(() => {
    if (cart_count > 0) {
      setIsAnimating(true);
      const timer = setTimeout(() => setIsAnimating(false), 400);
      return () => clearTimeout(timer);
    }
  }, [cart_count]);

  const formatCurrency = useCallback((amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount);
  }, []);

  const handleCartClick = useCallback(() => {
    if (cart_count > 0) {
      setIsCartOpen(true);
    }
  }, [cart_count]);

  const handleCloseCart = useCallback(() => {
    setIsCartOpen(false);
  }, []);

  return (
    <>
      <button
        onClick={handleCartClick}
        className={`
          relative p-2 rounded-lg transition-all duration-200 group
          ${cart_count > 0
            ? 'text-gray-700 hover:text-gray-900 hover:bg-gray-100 hover:scale-105'
            : 'text-gray-400 cursor-not-allowed'
          }
          ${isAnimating ? 'animate-pulse' : ''}
          ${className}
        `}
        disabled={cart_count === 0}
        title={cart_count > 0 ? `${cart_count} artículos - ${formatCurrency(cart_total)}` : 'Carrito vacío'}
        aria-label={`Carrito de compras (${cart_count} artículos)`}
      >
        {/* Cart Icon */}
        <svg
          className={`w-6 h-6 transition-transform duration-200 ${
            cart_count > 0 ? 'group-hover:scale-110' : ''
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={cart_count > 0 ? 2.5 : 2}
            d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.5 5M7 13l-1.5 5m4.5-5h6m0 0v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m8 0V9a2 2 0 00-2-2H9a2 2 0 00-2-2"
          />
        </svg>

        {/* Cart Count Badge */}
        {cart_count > 0 && (
          <span className={`
            absolute -top-1 -right-1 bg-gradient-to-r from-red-500 to-red-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold
            transform transition-all duration-300 shadow-lg
            ${isAnimating ? 'scale-125 animate-bounce' : 'scale-100'}
            ${cart_count > 0 ? 'group-hover:scale-110' : ''}
          `}>
            {cart_count > 99 ? '99+' : cart_count}
          </span>
        )}

        {/* Pulse ring animation for new items */}
        {isAnimating && (
          <span className="absolute -inset-1 rounded-full bg-blue-400 opacity-30 animate-ping" />
        )}
      </button>

      {/* Cart Sidebar/Drawer - Conditional based on device */}
      {variant === 'mobile' || isMobile ? (
        <MobileCartDrawer
          isOpen={isCartOpen}
          onClose={handleCloseCart}
        />
      ) : (
        <CartSidebar
          isOpen={isCartOpen}
          onClose={handleCloseCart}
        />
      )}
    </>
  );
};

export default CartIcon;