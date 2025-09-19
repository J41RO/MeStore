// ~/frontend/src/components/forms/index.ts
// ---------------------------------------------------------------------------------------------
// MESTORE - Optimized Form Components Barrel Export
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

/**
 * Enhanced form components with React 18 optimization, TypeScript strict typing,
 * WCAG 2.1 accessibility compliance, and Colombian market localization
 */

// Base Form Components
export { default as FormField } from './FormField';
export { default as NumberField } from './NumberField';
export { default as SelectField } from './SelectField';
export { default as TextAreaField } from './TextAreaField';

// Type Exports for Enhanced TypeScript Support
export type { FormFieldProps } from './FormField';
export type { NumberFieldProps } from './NumberField';
export type { SelectFieldProps, SelectOption } from './SelectField';
export type { TextAreaFieldProps } from './TextAreaField';

/**
 * Component Feature Summary:
 *
 * FormField:
 * - React.memo optimization for performance
 * - Enhanced TypeScript typing with generics
 * - WCAG 2.1 accessibility compliance
 * - Consistent design system styling
 * - Icon support and validation states
 *
 * NumberField:
 * - Colombian peso (COP) currency formatting
 * - Integer and decimal number support
 * - Unit suffix display (kg, cm, etc.)
 * - Enhanced validation and error handling
 * - Colombian locale number formatting
 *
 * SelectField:
 * - Option grouping support
 * - Multiple selection capability
 * - Enhanced keyboard navigation
 * - Accessibility improvements
 * - Colombian text localization
 *
 * TextAreaField:
 * - Real-time character counting
 * - Auto-resize functionality
 * - Colombian locale formatting
 * - Enhanced accessibility features
 * - Visual character limit indicators
 */

/**
 * Design System Consistency:
 *
 * All components follow the enhanced design system:
 * - Labels: text-slate-200 with font-semibold
 * - Inputs: rounded-xl with enhanced hover effects
 * - Errors: red-50 background with border styling
 * - Focus: ring-2 ring-blue-500 for accessibility
 * - Transitions: smooth 300ms duration
 * - Colombian market optimization
 */

/**
 * Performance Optimizations:
 *
 * - React.memo for component memoization
 * - useCallback for stable function references
 * - useMemo for expensive computations
 * - Optimized re-render prevention
 * - Efficient event handling
 */

/**
 * Accessibility Features:
 *
 * - ARIA labels and descriptions
 * - Screen reader compatibility
 * - High contrast ratio support
 * - Keyboard navigation support
 * - Live regions for dynamic content
 * - Colombian Spanish localization
 */