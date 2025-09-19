// ~/frontend/src/components/forms/SelectField.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Optimized SelectField with enhanced accessibility
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

import React, { useCallback, useMemo } from 'react';
import { AlertCircle, ChevronDown } from 'lucide-react';
import type { UseFormRegister, FieldValues, Path } from 'react-hook-form';

/**
 * Enhanced SelectOption interface
 */
interface SelectOption {
  /** Option value */
  value: string;
  /** Display label */
  label: string;
  /** Disable this option */
  disabled?: boolean;
  /** Optional group for categorization */
  group?: string;
}

/**
 * Enhanced SelectField Props with accessibility features
 */
interface SelectFieldProps<T extends FieldValues = FieldValues> {
  /** Field label text */
  label: string;
  /** Field name (must match form schema) */
  name: Path<T>;
  /** React Hook Form register function */
  register: UseFormRegister<T>;
  /** Validation error message */
  error?: string;
  /** Select options array */
  options: SelectOption[];
  /** Placeholder text */
  placeholder?: string;
  /** Required field indicator */
  required?: boolean;
  /** Help text description */
  helpText?: string;
  /** Additional CSS classes */
  className?: string;
  /** Disable field */
  disabled?: boolean;
  /** Multiple selection support */
  multiple?: boolean;
  /** Custom onChange handler */
  onChange?: (event: React.ChangeEvent<HTMLSelectElement>) => void;
  /** ARIA describedby for accessibility */
  'aria-describedby'?: string;
}

/**
 * Optimized SelectField component with enhanced accessibility and performance
 * Supports option grouping and keyboard navigation
 */
const SelectField = React.memo(<T extends FieldValues = FieldValues>({
  label,
  name,
  register,
  error,
  options,
  placeholder = 'Selecciona una opción',
  required,
  helpText,
  className = '',
  disabled = false,
  multiple = false,
  onChange,
  'aria-describedby': ariaDescribedBy,
}: SelectFieldProps<T>) => {
  // Memoized accessibility IDs
  const errorId = useCallback(() => error ? `${name}-error` : undefined, [name, error]);
  const helpId = useCallback(() => helpText ? `${name}-help` : undefined, [name, helpText]);

  // Computed ARIA attributes
  const ariaDescribedByIds = [ariaDescribedBy, errorId(), helpId()].filter(Boolean).join(' ') || undefined;

  // Group options by group property for better organization
  const groupedOptions = useMemo(() => {
    const groups: Record<string, SelectOption[]> = {};
    const ungrouped: SelectOption[] = [];

    options.forEach(option => {
      if (option.group) {
        if (!groups[option.group]) {
          groups[option.group] = [];
        }
        groups[option.group].push(option);
      } else {
        ungrouped.push(option);
      }
    });

    return { groups, ungrouped };
  }, [options]);

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

      {/* Select container with enhanced styling */}
      <div className="relative">
        <select
          id={name}
          multiple={multiple}
          disabled={disabled}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={ariaDescribedByIds}
          aria-required={required}
          {...register(name, { onChange })}
          className={`
            w-full px-4 py-3 rounded-xl border border-slate-300 bg-white text-slate-800
            font-medium transition-all duration-300 transform hover:scale-[1.02]
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
            shadow-sm hover:shadow-md appearance-none cursor-pointer
            ${multiple ? 'min-h-[120px]' : 'pr-12'}
            ${disabled ? 'opacity-50 cursor-not-allowed hover:scale-100' : ''}
            ${error
              ? 'border-red-300 bg-red-50 text-red-900 focus:ring-red-500 focus:border-red-500'
              : 'hover:border-slate-400 hover:bg-slate-50'
            }
          `}
        >
          {/* Placeholder option */}
          {!multiple && (
            <option value="" disabled={required}>
              {placeholder}
            </option>
          )}

          {/* Render ungrouped options first */}
          {groupedOptions.ungrouped.map((option) => (
            <option
              key={option.value}
              value={option.value}
              disabled={option.disabled}
              className={option.disabled ? 'text-slate-400' : 'text-slate-800'}
            >
              {option.label}
            </option>
          ))}

          {/* Render grouped options */}
          {Object.entries(groupedOptions.groups).map(([groupName, groupOptions]) => (
            <optgroup key={groupName} label={groupName}>
              {groupOptions.map((option) => (
                <option
                  key={option.value}
                  value={option.value}
                  disabled={option.disabled}
                  className={option.disabled ? 'text-slate-400' : 'text-slate-800'}
                >
                  {option.label}
                </option>
              ))}
            </optgroup>
          ))}
        </select>

        {/* Dropdown indicator (only for single select) */}
        {!multiple && (
          <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none">
            <ChevronDown className={`w-5 h-5 transition-colors duration-200 ${
              disabled ? 'text-slate-300' : 'text-slate-500'
            }`} />
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

      {/* Enhanced help text */}
      {helpText && !error && (
        <p
          id={helpId()}
          className="mt-1 text-xs text-slate-400 font-medium"
        >
          {helpText}
          {multiple && (
            <span className="block text-xs text-slate-500 mt-1">
              Mantén presionado Ctrl (o Cmd en Mac) para seleccionar múltiples opciones
            </span>
          )}
        </p>
      )}
    </div>
  );
});

// Display name for debugging
SelectField.displayName = 'SelectField';

export type { SelectFieldProps, SelectOption };
export default SelectField;