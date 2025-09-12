// ~/frontend/src/components/forms/FormField.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Componente FormField con validación visual
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

import React from 'react';
import { AlertCircle } from 'lucide-react';

interface FormFieldProps {
  label: string;
  name: string;
  type?: string;
  register: any;
  error?: string;
  placeholder?: string;
  required?: boolean;
  helpText?: string;
  icon?: React.ReactNode;
  className?: string;
}

const FormField: React.FC<FormFieldProps> = ({
  label,
  name,
  type = 'text',
  register,
  error,
  placeholder,
  required,
  helpText,
  icon,
  className = '',
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
        {icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <div className="text-gray-400">{icon}</div>
          </div>
        )}
        
        <input
          id={name}
          type={type}
          placeholder={placeholder}
          {...register(name)}
          className={`
            block w-full px-3 py-2 border rounded-md shadow-sm 
            focus:outline-none focus:ring-2 focus:ring-offset-2
            transition-colors duration-200
            ${icon ? 'pl-10' : ''}
            ${error 
              ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500' 
              : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500 hover:border-gray-400'
            }
            ${error ? 'bg-red-50' : 'bg-white hover:bg-gray-50'}
          `}
        />
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

export default FormField;