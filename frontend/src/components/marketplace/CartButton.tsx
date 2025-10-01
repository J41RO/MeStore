/**
 * CartButton Component - Shopping Cart Button with Badge
 * MeStore Marketplace - Colombian E-commerce
 *
 * Features:
 * - Animated badge counter
 * - Opens CartDrawer on click
 * - Responsive design
 * - Accessibility support
 */

import React from 'react';
import { ShoppingCart } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useCartStore } from '../../store/cartStore';

// ========================================
// COMPONENT
// ========================================

const CartButton: React.FC = () => {
  const { getTotalItems, toggleDrawer } = useCartStore();
  const totalItems = getTotalItems();

  return (
    <button
      onClick={toggleDrawer}
      className="relative p-2 text-gray-600 hover:text-blue-600 transition-colors group"
      aria-label={`Carrito de compras, ${totalItems} ${
        totalItems === 1 ? 'artículo' : 'artículos'
      }`}
    >
      {/* Shopping Cart Icon */}
      <ShoppingCart className="w-6 h-6 transform group-hover:scale-110 transition-transform duration-200" />

      {/* Badge Counter */}
      <AnimatePresence mode="wait">
        {totalItems > 0 && (
          <motion.span
            key={totalItems}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            transition={{ type: 'spring', stiffness: 500, damping: 30 }}
            className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center shadow-lg ring-2 ring-white"
          >
            {totalItems > 99 ? '99+' : totalItems}
          </motion.span>
        )}
      </AnimatePresence>

      {/* Pulse animation when items are added */}
      {totalItems > 0 && (
        <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full animate-ping opacity-75" />
      )}
    </button>
  );
};

export default CartButton;
