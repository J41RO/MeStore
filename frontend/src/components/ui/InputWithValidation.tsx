import React, { forwardRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ValidationResult } from '../../hooks/useRealTimeValidation';

interface InputWithValidationProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  validationResult?: ValidationResult;
  isValidating?: boolean;
  tooltip?: string;
  tooltipTestId?: string;
  suggestionTestId?: string;
}

export const InputWithValidation = forwardRef<HTMLInputElement, InputWithValidationProps>(
  ({
    error,
    validationResult,
    isValidating,
    tooltip,
    tooltipTestId,
    suggestionTestId,
    className = '',
    onFocus,
    onBlur,
    ...props
  }, ref) => {
    const [showTooltip, setShowTooltip] = useState(false);

    const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
      setShowTooltip(true);
      onFocus?.(e);
    };

    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      setShowTooltip(false);
      onBlur?.(e);
    };

    // Determine border color based on validation state
    const getBorderColor = () => {
      if (error) return 'border-red-300 focus:border-red-500';
      if (validationResult?.isValid === false) return 'border-red-300 focus:border-red-500';
      if (validationResult?.isValid === true) return 'border-green-300 focus:border-green-500';
      return 'border-gray-300 focus:border-blue-500';
    };

    // Get validation icon
    const getValidationIcon = () => {
      if (isValidating) {
        return (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <svg className="animate-spin w-5 h-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        );
      }

      if (validationResult?.isValid === true) {
        return (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2" data-testid={`${props['data-testid']?.replace('-input', '')}-success`}>
            <motion.svg
              className="w-5 h-5 text-green-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.2 }}
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </motion.svg>
          </div>
        );
      }

      if (validationResult?.isValid === false || error) {
        return (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2" data-testid={`${props['data-testid']?.replace('-input', '')}-error`}>
            <motion.svg
              className="w-5 h-5 text-red-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.2 }}
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </motion.svg>
          </div>
        );
      }

      return null;
    };

    return (
      <div className="relative">
        {/* Input Field */}
        <div className="relative">
          <input
            ref={ref}
            className={`w-full px-4 py-3 rounded-lg border ${getBorderColor()} focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 text-gray-900 placeholder-gray-400 bg-white font-medium pr-12 ${className}`}
            onFocus={handleFocus}
            onBlur={handleBlur}
            {...props}
          />
          {getValidationIcon()}
        </div>

        {/* Tooltip */}
        <AnimatePresence>
          {showTooltip && tooltip && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="absolute top-full left-0 mt-2 p-3 bg-gray-900 text-white text-sm rounded-lg shadow-lg z-10 max-w-xs"
              data-testid={tooltipTestId}
            >
              <div className="relative">
                {tooltip}
                <div className="absolute -top-1 left-4 w-2 h-2 bg-gray-900 transform rotate-45"></div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error Message */}
        <AnimatePresence>
          {error && (
            <motion.p
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -5 }}
              transition={{ duration: 0.2 }}
              className="mt-1 text-sm text-red-600"
            >
              {error}
            </motion.p>
          )}
        </AnimatePresence>

        {/* Validation Message */}
        <AnimatePresence>
          {validationResult?.message && !error && (
            <motion.p
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -5 }}
              transition={{ duration: 0.2 }}
              className={`mt-1 text-sm ${
                validationResult.isValid ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {validationResult.message}
            </motion.p>
          )}
        </AnimatePresence>

        {/* Suggestions */}
        <AnimatePresence>
          {validationResult?.suggestions && validationResult.suggestions.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -5 }}
              transition={{ duration: 0.2 }}
              className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded text-xs text-blue-700"
              data-testid={suggestionTestId}
            >
              <div className="font-medium mb-1">💡 Sugerencia:</div>
              <ul className="space-y-1">
                {validationResult.suggestions.map((suggestion, index) => (
                  <li key={index}>• {suggestion}</li>
                ))}
              </ul>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  }
);

InputWithValidation.displayName = 'InputWithValidation';