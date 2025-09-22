import React, { useState, useCallback, useEffect } from 'react';
import { useCheckoutStore, CartItem } from '../../stores/checkoutStore';

interface Product {
  id: string;
  name: string;
  price: number;
  image_url?: string;
  sku?: string;
  stock_available?: number;
  vendor_id?: string;
  vendor_name?: string;
}

interface AddToCartButtonProps {
  product: Product;
  quantity?: number;
  variant_attributes?: Record<string, string>;
  className?: string;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  children?: React.ReactNode;
}

const AddToCartButton: React.FC<AddToCartButtonProps> = ({
  product,
  quantity = 1,
  variant_attributes,
  className = '',
  disabled = false,
  size = 'md',
  showIcon = true,
  children
}) => {
  const { addItem } = useCheckoutStore();
  const [isAdding, setIsAdding] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [showAnimation, setShowAnimation] = useState(false);
  const [bounceEffect, setBounceEffect] = useState(false);

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'px-3 py-1.5 text-sm';
      case 'lg':
        return 'px-6 py-3 text-lg';
      default:
        return 'px-4 py-2';
    }
  };

  const handleAddToCart = useCallback(async () => {
    if (disabled || isAdding) return;

    setIsAdding(true);
    setShowAnimation(true);

    try {
      const cartItem: Omit<CartItem, 'id'> = {
        product_id: product.id,
        name: product.name,
        price: product.price,
        quantity,
        image_url: product.image_url,
        sku: product.sku,
        variant_attributes,
        vendor_id: product.vendor_id,
        vendor_name: product.vendor_name,
        stock_available: product.stock_available
      };

      // Add slight delay for better UX
      await new Promise(resolve => setTimeout(resolve, 300));

      addItem(cartItem);

      // Show success feedback with bounce effect
      setShowSuccess(true);
      setBounceEffect(true);

      // Reset success state
      setTimeout(() => {
        setShowSuccess(false);
        setBounceEffect(false);
      }, 2500);

      // Reset animation
      setTimeout(() => setShowAnimation(false), 400);

    } catch (error) {
      console.error('Error adding item to cart:', error);
      setShowAnimation(false);
      // You could add a toast notification here for errors
    } finally {
      setTimeout(() => setIsAdding(false), 200);
    }
  }, [disabled, isAdding, product, quantity, variant_attributes, addItem]);

  const isOutOfStock = product.stock_available !== undefined && product.stock_available <= 0;
  const isDisabled = disabled || isAdding || isOutOfStock;

  const getButtonText = () => {
    if (showSuccess) return 'Agregado';
    if (isAdding) return 'Agregando...';
    if (isOutOfStock) return 'Sin Stock';
    if (children) return children;
    return 'Agregar al Carrito';
  };

  const getButtonClasses = () => {
    let baseClasses = `
      inline-flex items-center justify-center font-medium rounded-lg transition-all duration-300
      ${getSizeClasses()}
      ${className}
      ${showAnimation ? 'scale-95' : 'scale-100'}
      ${bounceEffect ? 'animate-bounce' : ''}
      focus:outline-none focus:ring-4 focus:ring-opacity-50
    `;

    if (showSuccess) {
      baseClasses += ' bg-gradient-to-r from-green-500 to-green-600 text-white shadow-lg transform scale-105 focus:ring-green-300';
    } else if (isDisabled) {
      baseClasses += ' bg-gray-300 text-gray-500 cursor-not-allowed opacity-60';
    } else {
      baseClasses += ' bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white hover:shadow-xl transform hover:scale-105 active:scale-95 focus:ring-blue-300';
    }

    return baseClasses;
  };

  return (
    <button
      onClick={handleAddToCart}
      disabled={isDisabled}
      className={getButtonClasses()}
      title={isOutOfStock ? 'Producto sin stock' : 'Agregar al carrito'}
      aria-label={isOutOfStock ? 'Producto sin stock' : `Agregar ${product.name} al carrito`}
    >
      {showIcon && (
        <span className={`mr-2 transition-transform duration-200 ${
          showSuccess ? 'scale-110' : isAdding ? 'scale-90' : 'scale-100'
        }`}>
          {showSuccess ? (
            <svg className="w-4 h-4 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          ) : isAdding ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : isOutOfStock ? (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg className="w-4 h-4 transition-transform duration-200 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.5 5M7 13l-1.5 5m4.5-5h6m0 0v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m8 0V9a2 2 0 00-2-2H9a2 2 0 00-2-2"
              />
            </svg>
          )}
        </span>
      )}

      <span className={`transition-opacity duration-200 ${
        isAdding ? 'opacity-75' : 'opacity-100'
      }`}>
        {getButtonText()}
      </span>

      {/* Success particles effect */}
      {showSuccess && (
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute inset-0 bg-green-400 opacity-20 rounded-lg animate-ping" />
        </div>
      )}
    </button>
  );
};

export default AddToCartButton;