/**
 * Enhanced Button Component with Animations
 *
 * Professional button component with smooth animations and transitions.
 * Supports multiple variants, sizes, and states.
 */

import React, { ButtonHTMLAttributes, ReactNode } from 'react';
import { ButtonSpinner } from './LoadingSpinner';

export type ButtonVariant = 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'ghost' | 'link';
export type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** Button visual style */
  variant?: ButtonVariant;
  /** Button size */
  size?: ButtonSize;
  /** Loading state - shows spinner and disables button */
  loading?: boolean;
  /** Full width button */
  fullWidth?: boolean;
  /** Icon to show before text */
  iconBefore?: ReactNode;
  /** Icon to show after text */
  iconAfter?: ReactNode;
  /** Disable button */
  disabled?: boolean;
  /** Children content */
  children?: ReactNode;
}

/**
 * Get variant-specific classes
 */
const getVariantClasses = (variant: ButtonVariant, disabled?: boolean): string => {
  if (disabled) {
    return 'bg-gray-300 text-gray-500 cursor-not-allowed';
  }

  switch (variant) {
    case 'primary':
      return `bg-blue-600 text-white
        hover:bg-blue-700 active:bg-blue-800
        focus:ring-4 focus:ring-blue-200`;

    case 'secondary':
      return `bg-gray-200 text-gray-900
        hover:bg-gray-300 active:bg-gray-400
        focus:ring-4 focus:ring-gray-200`;

    case 'success':
      return `bg-green-600 text-white
        hover:bg-green-700 active:bg-green-800
        focus:ring-4 focus:ring-green-200`;

    case 'danger':
      return `bg-red-600 text-white
        hover:bg-red-700 active:bg-red-800
        focus:ring-4 focus:ring-red-200`;

    case 'warning':
      return `bg-orange-600 text-white
        hover:bg-orange-700 active:bg-orange-800
        focus:ring-4 focus:ring-orange-200`;

    case 'ghost':
      return `bg-transparent text-gray-700 border border-gray-300
        hover:bg-gray-50 active:bg-gray-100
        focus:ring-4 focus:ring-gray-200`;

    case 'link':
      return `bg-transparent text-blue-600 underline
        hover:text-blue-700 active:text-blue-800
        focus:ring-4 focus:ring-blue-200`;

    default:
      return '';
  }
};

/**
 * Get size-specific classes
 */
const getSizeClasses = (size: ButtonSize): string => {
  switch (size) {
    case 'xs':
      return 'px-2 py-1 text-xs';
    case 'sm':
      return 'px-3 py-1.5 text-sm';
    case 'md':
      return 'px-4 py-2 text-base';
    case 'lg':
      return 'px-6 py-3 text-lg';
    case 'xl':
      return 'px-8 py-4 text-xl';
    default:
      return 'px-4 py-2 text-base';
  }
};

/**
 * Enhanced Button Component
 */
export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  fullWidth = false,
  iconBefore,
  iconAfter,
  disabled = false,
  className = '',
  children,
  ...props
}) => {
  const isDisabled = disabled || loading;

  const baseClasses = `
    inline-flex items-center justify-center gap-2
    font-medium rounded-lg
    transition-all duration-200 ease-out
    transform active:scale-95
    focus:outline-none
    ${fullWidth ? 'w-full' : ''}
  `;

  const variantClasses = getVariantClasses(variant, isDisabled);
  const sizeClasses = getSizeClasses(size);

  // Add pulse animation when loading
  const loadingClasses = loading ? 'animate-pulse' : '';

  return (
    <button
      className={`
        ${baseClasses}
        ${variantClasses}
        ${sizeClasses}
        ${loadingClasses}
        ${className}
      `}
      disabled={isDisabled}
      {...props}
    >
      {/* Icon Before */}
      {iconBefore && !loading && (
        <span className="transition-transform duration-200 group-hover:scale-110">
          {iconBefore}
        </span>
      )}

      {/* Loading Spinner */}
      {loading && <ButtonSpinner color={variant === 'primary' || variant === 'danger' ? 'white' : 'primary'} />}

      {/* Button Text */}
      {children && <span>{children}</span>}

      {/* Icon After */}
      {iconAfter && !loading && (
        <span className="transition-transform duration-200 group-hover:scale-110">
          {iconAfter}
        </span>
      )}
    </button>
  );
};

/**
 * Icon Button - circular button for icons
 */
interface IconButtonProps extends Omit<ButtonProps, 'iconBefore' | 'iconAfter'> {
  icon: ReactNode;
}

export const IconButton: React.FC<IconButtonProps> = ({
  icon,
  variant = 'ghost',
  size = 'md',
  className = '',
  ...props
}) => {
  const sizeMap: Record<ButtonSize, string> = {
    xs: 'w-6 h-6 p-1',
    sm: 'w-8 h-8 p-1.5',
    md: 'w-10 h-10 p-2',
    lg: 'w-12 h-12 p-3',
    xl: 'w-14 h-14 p-3.5',
  };

  return (
    <Button
      variant={variant}
      className={`!p-0 rounded-full ${sizeMap[size]} ${className}`}
      {...props}
    >
      {icon}
    </Button>
  );
};

/**
 * Button Group - group related buttons
 */
interface ButtonGroupProps {
  children: ReactNode;
  className?: string;
  orientation?: 'horizontal' | 'vertical';
}

export const ButtonGroup: React.FC<ButtonGroupProps> = ({
  children,
  className = '',
  orientation = 'horizontal',
}) => {
  return (
    <div
      className={`
        inline-flex
        ${orientation === 'horizontal' ? 'flex-row' : 'flex-col'}
        ${className}
      `}
      role="group"
    >
      {children}
    </div>
  );
};

export default Button;
