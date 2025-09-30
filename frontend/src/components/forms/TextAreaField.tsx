// ~/frontend/src/components/forms/TextAreaField.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Optimized TextAreaField with enhanced character counting and accessibility
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

import React, { useCallback, useMemo } from 'react';
import { AlertCircle } from 'lucide-react';
import type { UseFormRegister, UseFormWatch, FieldValues, Path } from 'react-hook-form';

/**
 * Enhanced TextAreaField Props with accessibility and character counting
 */
interface TextAreaFieldProps<T extends FieldValues = FieldValues> {
  /** Field label text */
  label: string;
  /** Field name (must match form schema) */
  name: Path<T>;
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
  /** Number of visible text lines */
  rows?: number;
  /** Maximum character length */
  maxLength?: number;
  /** Minimum character length */
  minLength?: number;
  /** Additional CSS classes */
  className?: string;
  /** Disable field */
  disabled?: boolean;
  /** Show character count indicator */
  showCharCount?: boolean;
  /** React Hook Form watch function for real-time character counting */
  watch?: UseFormWatch<T>;
  /** Auto-resize based on content */
  autoResize?: boolean;
  /** ARIA describedby for accessibility */
  'aria-describedby'?: string;
}

/**
 * Optimized TextAreaField component with enhanced character counting and accessibility
 * Supports Colombian content standards and real-time character feedback
 */
const TextAreaField = React.memo(<T extends FieldValues = FieldValues>({
  label,
  name,
  register,
  error,
  placeholder,
  required,
  helpText,
  rows = 4,
  maxLength,
  minLength,
  className = '',
  disabled = false,
  showCharCount = false,
  watch,
  autoResize = false,
  'aria-describedby': ariaDescribedBy,
}: TextAreaFieldProps<T>) => {
  // Memoized accessibility IDs
  const errorId = useCallback(() => error ? `${name}-error` : undefined, [name, error]);
  const helpId = useCallback(() => helpText ? `${name}-help` : undefined, [name, helpText]);
  const charCountId = useCallback(() => showCharCount ? `${name}-char-count` : undefined, [name, showCharCount]);

  // Get current value for character counting
  const currentValue = watch ? watch(name) : '';
  const currentLength = useMemo(() => String(currentValue || '').length, [currentValue]);

  // Character count status
  const charCountStatus = useMemo(() => {
    if (!maxLength) return 'normal';
    if (currentLength > maxLength) return 'over';
    if (currentLength > maxLength * 0.8) return 'warning';
    return 'normal';
  }, [currentLength, maxLength]);

  // Character count styling
  const charCountStyles = useMemo(() => {
    switch (charCountStatus) {
      case 'over':
        return 'text-red-700 bg-red-100 border-red-200';
      case 'warning':
        return 'text-amber-700 bg-amber-100 border-amber-200';
      default:
        return 'text-slate-500 bg-slate-100 border-slate-200';
    }
  }, [charCountStatus]);

  // Computed ARIA attributes
  const ariaDescribedByIds = [ariaDescribedBy, errorId(), helpId(), charCountId()].filter(Boolean).join(' ') || undefined;

  // Enhanced placeholder with Colombian context
  const enhancedPlaceholder = useMemo(() => {
    if (placeholder) return placeholder;
    return 'Ingrese su texto aquí...';
  }, [placeholder]);

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Enhanced header with label and character count */}
      <div className="flex justify-between items-center">
        <label
          htmlFor={name}
          className="block text-sm font-semibold text-slate-200 transition-colors duration-200"
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

        {/* Real-time character counter */}
        {showCharCount && maxLength && (
          <div
            id={charCountId()}
            className={`text-sm font-bold px-3 py-1 rounded-lg border transition-all duration-200 ${charCountStyles}`}
            aria-live="polite"
            aria-label={`Caracteres: ${currentLength} de ${maxLength}`}
          >
            <span className="tabular-nums">
              {currentLength.toLocaleString('es-CO')}
            </span>
            <span className="text-xs mx-1">/</span>
            <span className="tabular-nums">
              {maxLength.toLocaleString('es-CO')}
            </span>
          </div>
        )}
      </div>

      {/* TextArea container with enhanced styling */}
      <div className="relative">
        <textarea
          id={name}
          rows={autoResize ? undefined : rows}
          maxLength={maxLength}
          minLength={minLength}
          placeholder={enhancedPlaceholder}
          disabled={disabled}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={ariaDescribedByIds}
          aria-required={required}
          {...register(name)}
          className={`
            w-full px-4 py-3 rounded-xl border border-slate-300 bg-white text-slate-800
            placeholder-slate-400 font-medium transition-all duration-300 transform
            hover:scale-[1.01] focus:outline-none focus:ring-2 focus:ring-blue-500
            focus:border-blue-500 shadow-sm hover:shadow-md resize-vertical
            ${autoResize ? 'resize-none' : 'min-h-[100px]'}
            ${disabled ? 'opacity-50 cursor-not-allowed hover:scale-100' : ''}
            ${error
              ? 'border-red-300 bg-red-50 text-red-900 placeholder-red-400 focus:ring-red-500 focus:border-red-500'
              : 'hover:border-slate-400 hover:bg-slate-50'
            }
          `}
          style={autoResize ? { minHeight: `${rows * 1.5}rem` } : undefined}
        />

        {/* Character count overlay for better UX */}
        {showCharCount && !maxLength && (
          <div className="absolute bottom-2 right-2 text-xs text-slate-400 bg-white/80 backdrop-blur-sm px-2 py-1 rounded-md border border-slate-200">
            {currentLength.toLocaleString('es-CO')} caracteres
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
        <div
          id={helpId()}
          className="mt-1 text-xs font-medium"
        >
          <p style={{ color: '#cbd5e1 !important' }}>{helpText}</p>

          {/* Additional context for Colombian users */}
          <div className="mt-1 space-y-1">
            {minLength && (
              <p style={{ color: '#cbd5e1 !important' }}>
                Mínimo: {minLength.toLocaleString('es-CO')} caracteres
              </p>
            )}
            {maxLength && (
              <p style={{ color: '#cbd5e1 !important' }}>
                Máximo: {maxLength.toLocaleString('es-CO')} caracteres
              </p>
            )}
            {autoResize && (
              <p style={{ color: '#cbd5e1 !important' }}>
                El campo se ajusta automáticamente al contenido
              </p>
            )}
          </div>
        </div>
      )}

      {/* Accessibility improvements */}
      {showCharCount && charCountStatus === 'over' && (
        <div
          className="sr-only"
          aria-live="assertive"
          role="status"
        >
          Has excedido el límite de caracteres. Texto actual: {currentLength}, máximo permitido: {maxLength}
        </div>
      )}
    </div>
  );
});

// Display name for debugging
TextAreaField.displayName = 'TextAreaField';

export type { TextAreaFieldProps };
export default TextAreaField;