// ~/frontend/src/components/forms/FormField.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Optimized FormField component with enhanced UX and performance
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

import React, { useCallback } from 'react';
import { AlertCircle } from 'lucide-react';
import type { UseFormRegister, FieldValues, Path } from 'react-hook-form';

/**
 * Enhanced FormField Props with strict TypeScript typing
 */
interface FormFieldProps<T extends FieldValues = FieldValues> {
  /** Field label text */
  label: string;
  /** Field name (must match form schema) */
  name: Path<T>;
  /** Input type */
  type?: 'text' | 'email' | 'password' | 'tel' | 'url' | 'search';
  /** React Hook Form register function */
  register: UseFormRegister<T>;
  /** Validation error message */
  error?: string;
  /** Placeholder text */
  placeholder?: string;
  /** Required field indicator */
  required?: boolean;
  /** Help text description */
  helpText?: string;
  /** Optional icon element */
  icon?: React.ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Input autocomplete attribute */
  autoComplete?: string;
  /** Disable field */
  disabled?: boolean;
  /** ARIA describedby for accessibility */
  'aria-describedby'?: string;
}

/**
 * Optimized FormField component with React.memo for performance
 * Supports Colombian market standards and WCAG 2.1 accessibility
 */
const FormField = React.memo(<T extends FieldValues = FieldValues>({
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
  autoComplete,
  disabled = false,
  'aria-describedby': ariaDescribedBy,
}: FormFieldProps<T>) => {
  // Memoized error ID for consistent accessibility
  const errorId = useCallback(() => error ? `${name}-error` : undefined, [name, error]);
  const helpId = useCallback(() => helpText ? `${name}-help` : undefined, [name, helpText]);

  // Computed ARIA attributes
  const ariaDescribedByIds = [ariaDescribedBy, errorId(), helpId()].filter(Boolean).join(' ') || undefined;

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Enhanced label with better accessibility */}
      <label
        htmlFor={name}
        className="block text-sm font-semibold text-slate-200 mb-2 transition-colors duration-200"
      >
        {label}
        {required && (
          <span
            className="text-red-400 ml-1"
            aria-label="required field"
            role="img"
          >
            *
          </span>
        )}
      </label>

      {/* Input container with enhanced styling */}
      <div className="relative">
        {icon && (
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
            <div className="text-slate-400 transition-colors duration-200">{icon}</div>
          </div>
        )}

        <input
          id={name}
          type={type}
          placeholder={placeholder}
          autoComplete={autoComplete}
          disabled={disabled}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={ariaDescribedByIds}
          aria-required={required}
          {...register(name)}
          className={`
            w-full px-4 py-3 rounded-xl border border-slate-300 bg-white text-slate-800
            placeholder-slate-400 font-medium transition-all duration-300 transform
            hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-blue-500
            focus:border-blue-500 shadow-sm hover:shadow-md
            ${icon ? 'pl-12' : ''}
            ${disabled ? 'opacity-50 cursor-not-allowed hover:scale-100' : ''}
            ${error
              ? 'border-red-300 bg-red-50 text-red-900 placeholder-red-400 focus:ring-red-500 focus:border-red-500'
              : 'hover:border-slate-400 hover:bg-slate-50'
            }
          `}
        />
      </div>

      {/* Enhanced error message with better styling */}
      {error && (
        <div
          id={errorId()}
          className="mt-1 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2 flex items-start animate-fade-in"
          role="alert"
          aria-live="polite"
        >
          <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Enhanced help text */}
      {helpText && !error && (
        <p
          id={helpId()}
          className="mt-1 text-xs font-medium"
          style={{ color: '#cbd5e1 !important' }}
        >
          {helpText}
        </p>
      )}
    </div>
  );
});

// Display name for debugging
FormField.displayName = 'FormField';

export type { FormFieldProps };

export default FormField;