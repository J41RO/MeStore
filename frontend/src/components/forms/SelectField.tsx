// ~/frontend/src/components/forms/SelectField.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Componente SelectField especializado para selección
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

import React from 'react';
import { AlertCircle, ChevronDown } from 'lucide-react';

interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

interface SelectFieldProps {
  label: string;
  name: string;
  register: any;
  error?: string;
  options: SelectOption[];
  placeholder?: string;
  required?: boolean;
  helpText?: string;
  className?: string;
  onChange?: (event: React.ChangeEvent<HTMLSelectElement>) => void;
}

const SelectField: React.FC<SelectFieldProps> = ({
  label,
  name,
  register,
  error,
  options,
  placeholder = 'Selecciona una opción',
  required,
  helpText,
  className = '',
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
        <select
          id={name}
          {...register(name, { onChange })}
          className={`
            block w-full px-3 py-2 border rounded-md shadow-sm
            focus:outline-none focus:ring-2 focus:ring-offset-2
            transition-colors duration-200
            appearance-none pr-10
            ${error 
              ? 'border-red-300 text-red-900 focus:ring-red-500 focus:border-red-500 bg-red-50' 
              : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500 bg-white hover:border-gray-400 hover:bg-gray-50'
            }
          `}
        >
          <option value="">{placeholder}</option>
          {options.map((option) => (
            <option 
              key={option.value} 
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </option>
          ))}
        </select>
        
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
          <ChevronDown className="w-4 h-4 text-gray-400" />
        </div>
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

export default SelectField;