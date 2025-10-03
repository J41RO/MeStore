/**
 * Common Components Index
 *
 * Central export file for all common/reusable components.
 * Simplifies imports across the application.
 *
 * Usage:
 * ```tsx
 * import { LoadingSpinner, SkeletonLoader, ProgressBar } from '@/components/common';
 * ```
 */

// Loading Components
export { default as LoadingSpinner, ButtonSpinner, InlineLoader } from './LoadingSpinner';
export {
  default as SkeletonLoader,
  SkeletonTable,
  SkeletonGrid,
  SkeletonStatsCards,
  SkeletonOrderCard,
} from './SkeletonLoader';
export {
  default as ProgressBar,
  CircularProgress,
  StepProgress,
  UploadProgress,
} from './ProgressBar';

// Transition Components
export {
  FadeTransition,
  ScaleTransition,
  SlideTransition,
  CollapseTransition,
  StaggeredList,
  ModalTransition,
  PageTransition,
} from './Transition';

// Button Components
export { Button, IconButton, ButtonGroup } from './Button';
export type { ButtonProps, ButtonVariant, ButtonSize } from './Button';

// Other Common Components
export { default as ErrorBoundary } from './ErrorBoundary';
export { default as Toast } from './Toast';
export { default as ToastContainer } from './ToastContainer';
