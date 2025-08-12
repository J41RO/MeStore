import React from 'react';
import { ButtonProps } from './Button.types';

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  fullWidth = false,
  disabled = false,
  icon,
  children,
  className,
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded sm:rounded-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95 active:transform touch-target';
  
  const variantClasses = {
    primary: 'btn-primary focus:ring-primary-500 active:bg-primary-700',
    secondary: 'btn-secondary focus:ring-secondary-500 active:bg-secondary-700',
    outline: 'btn-outline-primary focus:ring-primary-500',
    ghost: 'btn-ghost focus:ring-primary-500',
    danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500 active:bg-red-800',
  };

  const sizeClasses = {
    sm: 'px-2 sm:px-3 py-1 sm:py-1.5 text-xs sm:text-sm gap-1 sm:gap-1.5',
    md: 'px-3 sm:px-4 py-1.5 sm:py-2 text-sm sm:text-base gap-1.5 sm:gap-2',
    lg: 'px-4 sm:px-6 py-2 sm:py-3 text-base sm:text-lg gap-2 sm:gap-2.5',
  };

  const widthClasses = fullWidth ? 'w-full' : '';

  const combinedClasses = [
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    widthClasses,
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      className={combinedClasses}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" className="opacity-25" />
          <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" className="opacity-75" />
        </svg>
      )}
      {!loading && icon && icon}
      {children}
    </button>
  );
};

export default Button;