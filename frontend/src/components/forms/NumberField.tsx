// ~/frontend/src/components/forms/NumberField.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Componente NumberField especializado para números
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

import React from 'react';
import { AlertCircle } from 'lucide-react';

interface NumberFieldProps {
  label: string;
  name: string;
  register: any;
  error?: string;
  min?: number;
  max?: number;
  step?: number;
  currency?: boolean;
  unit?: string;
  placeholder?: string;
  required?: boolean;
  helpText?: string;
  icon?: React.ReactNode;
  className?: string;
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const NumberField: React.FC<NumberFieldProps> = ({
  label,
  name,
  register,
  error,
  min,
  max,
  step = 0.01,
  currency,
  unit,
  placeholder,
  required,
  helpText,
  icon,
  className = '',
  onBlur,
  onChange,
}) => {
  return (
    <div className={`space-y-1 ${className}`}>
      <label 
        htmlFor={name}
        className={`block text-sm font-medium ${
          error ? 'text-red-700' : 'text-gray-700'
        }`}
      >
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      
      <div className="relative">
        {(currency || icon) && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            {currency && <span className="text-gray-500 sm:text-sm font-medium">$</span>}
            {icon && <div className="text-gray-400">{icon}</div>}
          </div>
        )}
        
        <input
          id={name}
          type="number"
          min={min}
          max={max}
          step={step}
          placeholder={placeholder}
          {...register(name, { 
            valueAsNumber: true,
            onBlur,
            onChange 
          })}
          className={`
            block w-full px-3 py-2 border rounded-md shadow-sm
            focus:outline-none focus:ring-2 focus:ring-offset-2
            transition-colors duration-200
            ${currency || icon ? 'pl-8' : ''}
            ${unit ? 'pr-16' : ''}
            ${error 
              ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500 bg-red-50' 
              : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500 bg-white hover:border-gray-400 hover:bg-gray-50'
            }
          `}
        />
        
        {unit && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <span className="text-gray-500 sm:text-sm font-medium">{unit}</span>
          </div>
        )}
      </div>
      
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

export default NumberField;