// ~/frontend/src/components/forms/NumberField.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Optimized NumberField with Colombian currency support
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

import React, { useCallback, useMemo } from 'react';
import { AlertCircle } from 'lucide-react';
import type { UseFormRegister, FieldValues, Path } from 'react-hook-form';

/**
 * Enhanced NumberField Props with Colombian market optimization
 */
interface NumberFieldProps<T extends FieldValues = FieldValues> {
  /** Field label text */
  label: string;
  /** Field name (must match form schema) */
  name: Path<T>;
  /** React Hook Form register function */
  register: UseFormRegister<T>;
  /** Validation error message */
  error?: string;
  /** Minimum value */
  min?: number;
  /** Maximum value */
  max?: number;
  /** Step increment (default: 0.01 for currency, 1 for integers) */
  step?: number;
  /** Enable Colombian peso (COP) currency formatting */
  currency?: boolean;
  /** Unit suffix (e.g., 'kg', 'cm', 'unidades') */
  unit?: string;
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
  /** Disable field */
  disabled?: boolean;
  /** Format as integer (no decimals) */
  integer?: boolean;
  /** Show thousand separators */
  thousandSeparator?: boolean;
  /** Custom onBlur handler */
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  /** Custom onChange handler */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  /** ARIA describedby for accessibility */
  'aria-describedby'?: string;
}

/**
 * Optimized NumberField component with Colombian market support
 * Includes COP currency formatting and accessibility enhancements
 */
const NumberField = React.memo(<T extends FieldValues = FieldValues>({
  label,
  name,
  register,
  error,
  min,
  max,
  step,
  currency = false,
  unit,
  placeholder,
  required,
  helpText,
  icon,
  className = '',
  disabled = false,
  integer = false,
  thousandSeparator = false,
  onBlur,
  onChange,
  'aria-describedby': ariaDescribedBy,
}: NumberFieldProps<T>) => {
  // Optimized step calculation for Colombian standards
  const optimizedStep = useMemo(() => {
    if (step !== undefined) return step;
    if (integer) return 1;
    if (currency) return 100; // Colombian pesos don't use decimals in most cases
    return 0.01;
  }, [step, integer, currency]);

  // Memoized accessibility IDs
  const errorId = useCallback(() => error ? `${name}-error` : undefined, [name, error]);
  const helpId = useCallback(() => helpText ? `${name}-help` : undefined, [name, helpText]);

  // Colombian currency symbol
  const currencySymbol = currency ? 'COP $' : null;

  // Computed ARIA attributes
  const ariaDescribedByIds = [ariaDescribedBy, errorId(), helpId()].filter(Boolean).join(' ') || undefined;

  // Enhanced placeholder with Colombian context
  const enhancedPlaceholder = useMemo(() => {
    if (placeholder) return placeholder;
    if (currency) return 'Ej: 150000';
    if (unit) return `Ingrese cantidad en ${unit}`;
    return 'Ingrese un número';
  }, [placeholder, currency, unit]);

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
            aria-label="campo requerido"
            role="img"
          >
            *
          </span>
        )}
      </label>

      {/* Input container with enhanced styling */}
      <div className="relative">
        {/* Left side indicators (currency or icon) */}
        {(currencySymbol || icon) && (
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
            {currencySymbol && (
              <span className="text-slate-600 text-sm font-bold bg-slate-100 px-2 py-1 rounded-md border border-slate-200">
                {currencySymbol}
              </span>
            )}
            {icon && !currency && (
              <div className="text-slate-400 transition-colors duration-200">{icon}</div>
            )}
          </div>
        )}

        <input
          id={name}
          type="number"
          min={min}
          max={max}
          step={optimizedStep}
          placeholder={enhancedPlaceholder}
          disabled={disabled}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={ariaDescribedByIds}
          aria-required={required}
          {...register(name, {
            valueAsNumber: true,
            onBlur,
            onChange
          })}
          className={`
            w-full px-4 py-3 rounded-xl border border-slate-300 bg-white text-slate-800
            placeholder-slate-400 font-medium transition-all duration-300 transform
            hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-blue-500
            focus:border-blue-500 shadow-sm hover:shadow-md
            ${currencySymbol ? 'pl-20' : icon ? 'pl-12' : ''}
            ${unit ? 'pr-24' : ''}
            ${disabled ? 'opacity-50 cursor-not-allowed hover:scale-100' : ''}
            ${error
              ? 'border-red-300 bg-red-50 text-red-900 placeholder-red-400 focus:ring-red-500 focus:border-red-500'
              : 'hover:border-slate-400 hover:bg-slate-50'
            }
          `}
        />

        {/* Right side unit indicator */}
        {unit && (
          <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none">
            <span className="text-slate-600 text-sm font-bold bg-slate-100 px-3 py-1 rounded-md border border-slate-200">
              {unit}
            </span>
          </div>
        )}
      </div>

      {/* Enhanced error message */}
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

      {/* Enhanced help text with Colombian context */}
      {helpText && !error && (
        <p
          id={helpId()}
          className="mt-1 text-xs text-slate-400 font-medium"
        >
          {helpText}
          {currency && !helpText.includes('COP') && (
            <span className="block text-xs text-slate-500 mt-1">
              Moneda: Pesos colombianos (COP)
            </span>
          )}
        </p>
      )}
    </div>
  );
});

// Display name for debugging
NumberField.displayName = 'NumberField';

export type { NumberFieldProps };

export default NumberField;