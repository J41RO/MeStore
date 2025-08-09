import React from 'react';
import { InputProps } from './Input.types';

const Input: React.FC<InputProps> = ({
  size = 'md',
  state = 'default',
  label,
  error,
  helper,
  icon,
  fullWidth = true,
  className,
  id,
  ...props
}) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

  const baseClasses = 'input-mestocker transition-all duration-200';
  
  const sizeClasses = {
    sm: 'px-2.5 py-1.5 text-sm',
    md: 'px-3 py-2 text-base',
    lg: 'px-4 py-3 text-lg',
  };

  const stateClasses = {
    default: 'border-neutral-300 focus:border-primary-500 focus:ring-primary-500',
    error: 'border-red-500 focus:border-red-500 focus:ring-red-500',
    success: 'border-green-500 focus:border-green-500 focus:ring-green-500',
  };

  const widthClasses = fullWidth ? 'w-full' : '';

  const combinedClasses = [
    baseClasses,
    sizeClasses[size],
    stateClasses[error ? 'error' : state],
    widthClasses,
    icon ? 'pl-10' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label htmlFor={inputId} className="block text-sm font-medium text-neutral-700 mb-1">
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <div className="h-4 w-4 text-neutral-400">
              {icon}
            </div>
          </div>
        )}
        <input
          id={inputId}
          className={combinedClasses}
          {...props}
        />
      </div>
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
      {helper && !error && (
        <p className="mt-1 text-sm text-neutral-500">{helper}</p>
      )}
    </div>
  );
};

export default Input;
