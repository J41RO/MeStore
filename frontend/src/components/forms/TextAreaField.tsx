// ~/frontend/src/components/forms/TextAreaField.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Componente TextAreaField especializado para texto largo
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

import React from 'react';
import { AlertCircle } from 'lucide-react';

interface TextAreaFieldProps {
  label: string;
  name: string;
  register: any;
  error?: string;
  placeholder?: string;
  required?: boolean;
  helpText?: string;
  rows?: number;
  maxLength?: number;
  className?: string;
  showCharCount?: boolean;
  watch?: (name: string) => string;
}

const TextAreaField: React.FC<TextAreaFieldProps> = ({
  label,
  name,
  register,
  error,
  placeholder,
  required,
  helpText,
  rows = 4,
  maxLength,
  className = '',
  showCharCount,
  watch,
}) => {
  const currentValue = watch ? watch(name) : '';
  const currentLength = currentValue?.length || 0;

  return (
    <div className={`space-y-1 ${className}`}>
      <div className="flex justify-between items-center">
        <label 
          htmlFor={name}
          className={`block text-sm font-medium ${
            error ? 'text-red-700' : 'text-gray-700'
          }`}
        >
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
        
        {showCharCount && maxLength && (
          <span className={`text-xs ${
            currentLength > maxLength ? 'text-red-500' : 'text-gray-500'
          }`}>
            {currentLength}/{maxLength}
          </span>
        )}
      </div>
      
      <textarea
        id={name}
        rows={rows}
        maxLength={maxLength}
        placeholder={placeholder}
        {...register(name)}
        className={`
          block w-full px-3 py-2 border rounded-md shadow-sm
          focus:outline-none focus:ring-2 focus:ring-offset-2
          transition-colors duration-200 resize-vertical
          ${error 
            ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500 bg-red-50' 
            : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500 bg-white hover:border-gray-400 hover:bg-gray-50'
          }
        `}
      />
      
      {error && (
        <p className="text-sm text-red-600 flex items-center animate-fade-in">
          <AlertCircle className="w-4 h-4 mr-1 flex-shrink-0" />
          {error}
        </p>
      )}
      
      {helpText && !error && (
        <p className="text-sm text-gray-500">{helpText}</p>
      )}
    </div>
  );
};

export default TextAreaField;