/**
 * StatusBadge Component
 *
 * Flexible status badge component for displaying various states and statuses
 * with consistent design patterns across the admin interface.
 *
 * Features:
 * - Multiple status variants with predefined color schemes
 * - Size variants for different use cases
 * - Icon support with automatic color matching
 * - Pulse animation for active/loading states
 * - Accessibility compliance with proper aria labels
 * - Hover effects and click handling
 * - Custom color and style overrides
 *
 * @version 1.0.0
 * @author UX Specialist AI
 */

import React, { memo, useMemo } from 'react';
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  Clock,
  Zap,
  Pause,
  Play,
  RefreshCw,
  Eye,
  EyeOff,
  Lock,
  Unlock
} from 'lucide-react';

/**
 * Status variants with semantic meaning
 */
export type StatusVariant =
  | 'success'
  | 'error'
  | 'warning'
  | 'info'
  | 'pending'
  | 'active'
  | 'inactive'
  | 'processing'
  | 'draft'
  | 'published'
  | 'archived'
  | 'approved'
  | 'rejected'
  | 'review'
  | 'locked'
  | 'unlocked'
  | 'visible'
  | 'hidden'
  | 'premium'
  | 'free'
  | 'new'
  | 'updated'
  | 'default';

/**
 * Size variants
 */
export type StatusSize = 'xs' | 'sm' | 'md' | 'lg';

/**
 * StatusBadge component props
 */
export interface StatusBadgeProps {
  /** Status variant */
  variant: StatusVariant;

  /** Badge text content */
  children: React.ReactNode;

  /** Size variant */
  size?: StatusSize;

  /** Custom icon override */
  icon?: React.ComponentType<any>;

  /** Whether to show icon */
  showIcon?: boolean;

  /** Whether to show pulse animation */
  pulse?: boolean;

  /** Whether badge is clickable */
  clickable?: boolean;

  /** Click handler */
  onClick?: () => void;

  /** Custom CSS classes */
  className?: string;

  /** Accessibility label */
  ariaLabel?: string;

  /** Tooltip text */
  title?: string;

  /** Whether badge is outlined */
  outlined?: boolean;

  /** Whether badge is rounded (pill style) */
  rounded?: boolean;

  /** Custom color override */
  customColor?: {
    bg: string;
    text: string;
    border?: string;
  };

  /** Test ID for testing */
  testId?: string;
}

/**
 * StatusBadge Component
 */
export const StatusBadge: React.FC<StatusBadgeProps> = memo(({
  variant,
  children,
  size = 'sm',
  icon,
  showIcon = true,
  pulse = false,
  clickable = false,
  onClick,
  className = '',
  ariaLabel,
  title,
  outlined = false,
  rounded = true,
  customColor,
  testId = 'status-badge'
}) => {
  /**
   * Get variant styles
   */
  const variantStyles = useMemo(() => {
    const styles: Record<StatusVariant, {
      bg: string;
      text: string;
      border: string;
      icon?: React.ComponentType<any>;
      pulse?: boolean;
    }> = {
      success: {
        bg: 'bg-green-100',
        text: 'text-green-800',
        border: 'border-green-200',
        icon: CheckCircle
      },
      error: {
        bg: 'bg-red-100',
        text: 'text-red-800',
        border: 'border-red-200',
        icon: XCircle
      },
      warning: {
        bg: 'bg-yellow-100',
        text: 'text-yellow-800',
        border: 'border-yellow-200',
        icon: AlertCircle
      },
      info: {
        bg: 'bg-blue-100',
        text: 'text-blue-800',
        border: 'border-blue-200',
        icon: AlertCircle
      },
      pending: {
        bg: 'bg-orange-100',
        text: 'text-orange-800',
        border: 'border-orange-200',
        icon: Clock,
        pulse: true
      },
      active: {
        bg: 'bg-green-100',
        text: 'text-green-800',
        border: 'border-green-200',
        icon: Play,
        pulse: true
      },
      inactive: {
        bg: 'bg-gray-100',
        text: 'text-gray-800',
        border: 'border-gray-200',
        icon: Pause
      },
      processing: {
        bg: 'bg-blue-100',
        text: 'text-blue-800',
        border: 'border-blue-200',
        icon: RefreshCw,
        pulse: true
      },
      draft: {
        bg: 'bg-gray-100',
        text: 'text-gray-800',
        border: 'border-gray-200'
      },
      published: {
        bg: 'bg-green-100',
        text: 'text-green-800',
        border: 'border-green-200',
        icon: CheckCircle
      },
      archived: {
        bg: 'bg-gray-100',
        text: 'text-gray-600',
        border: 'border-gray-200'
      },
      approved: {
        bg: 'bg-green-100',
        text: 'text-green-800',
        border: 'border-green-200',
        icon: CheckCircle
      },
      rejected: {
        bg: 'bg-red-100',
        text: 'text-red-800',
        border: 'border-red-200',
        icon: XCircle
      },
      review: {
        bg: 'bg-yellow-100',
        text: 'text-yellow-800',
        border: 'border-yellow-200',
        icon: Eye
      },
      locked: {
        bg: 'bg-red-100',
        text: 'text-red-800',
        border: 'border-red-200',
        icon: Lock
      },
      unlocked: {
        bg: 'bg-green-100',
        text: 'text-green-800',
        border: 'border-green-200',
        icon: Unlock
      },
      visible: {
        bg: 'bg-green-100',
        text: 'text-green-800',
        border: 'border-green-200',
        icon: Eye
      },
      hidden: {
        bg: 'bg-gray-100',
        text: 'text-gray-800',
        border: 'border-gray-200',
        icon: EyeOff
      },
      premium: {
        bg: 'bg-purple-100',
        text: 'text-purple-800',
        border: 'border-purple-200',
        icon: Zap
      },
      free: {
        bg: 'bg-gray-100',
        text: 'text-gray-800',
        border: 'border-gray-200'
      },
      new: {
        bg: 'bg-blue-100',
        text: 'text-blue-800',
        border: 'border-blue-200',
        pulse: true
      },
      updated: {
        bg: 'bg-indigo-100',
        text: 'text-indigo-800',
        border: 'border-indigo-200'
      },
      default: {
        bg: 'bg-gray-100',
        text: 'text-gray-800',
        border: 'border-gray-200'
      }
    };

    return styles[variant] || styles.default;
  }, [variant]);

  /**
   * Get size styles
   */
  const sizeStyles = useMemo(() => {
    const styles: Record<StatusSize, {
      text: string;
      padding: string;
      iconSize: string;
      gap: string;
    }> = {
      xs: {
        text: 'text-xs',
        padding: 'px-2 py-0.5',
        iconSize: 'w-3 h-3',
        gap: 'gap-1'
      },
      sm: {
        text: 'text-xs',
        padding: 'px-2.5 py-0.5',
        iconSize: 'w-3 h-3',
        gap: 'gap-1'
      },
      md: {
        text: 'text-sm',
        padding: 'px-3 py-1',
        iconSize: 'w-4 h-4',
        gap: 'gap-1.5'
      },
      lg: {
        text: 'text-base',
        padding: 'px-4 py-1.5',
        iconSize: 'w-5 h-5',
        gap: 'gap-2'
      }
    };

    return styles[size];
  }, [size]);

  /**
   * Get icon component
   */
  const IconComponent = useMemo(() => {
    return icon || variantStyles.icon;
  }, [icon, variantStyles.icon]);

  /**
   * Should show pulse animation
   */
  const shouldPulse = useMemo(() => {
    return pulse || variantStyles.pulse;
  }, [pulse, variantStyles.pulse]);

  /**
   * Badge classes
   */
  const badgeClasses = useMemo(() => {
    const baseClasses = [
      'inline-flex items-center font-medium transition-all duration-200',
      sizeStyles.text,
      sizeStyles.padding,
      sizeStyles.gap
    ];

    // Color classes
    if (customColor) {
      baseClasses.push(customColor.bg, customColor.text);
      if (outlined && customColor.border) {
        baseClasses.push('border', customColor.border);
      }
    } else {
      if (outlined) {
        baseClasses.push('border', 'bg-white', variantStyles.text, variantStyles.border);
      } else {
        baseClasses.push(variantStyles.bg, variantStyles.text);
      }
    }

    // Shape classes
    if (rounded) {
      baseClasses.push('rounded-full');
    } else {
      baseClasses.push('rounded-md');
    }

    // Interactive classes
    if (clickable || onClick) {
      baseClasses.push(
        'cursor-pointer',
        'hover:scale-105',
        'focus:outline-none',
        'focus:ring-2',
        'focus:ring-offset-2',
        'focus:ring-blue-500'
      );
    }

    // Animation classes
    if (shouldPulse) {
      baseClasses.push('animate-pulse');
    }

    // Custom classes
    if (className) {
      baseClasses.push(className);
    }

    return baseClasses.join(' ');
  }, [
    sizeStyles,
    customColor,
    outlined,
    variantStyles,
    rounded,
    clickable,
    onClick,
    shouldPulse,
    className
  ]);

  /**
   * Handle click
   */
  const handleClick = (event: React.MouseEvent) => {
    if (onClick) {
      event.preventDefault();
      event.stopPropagation();
      onClick();
    }
  };

  /**
   * Handle keyboard navigation
   */
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if ((event.key === 'Enter' || event.key === ' ') && onClick) {
      event.preventDefault();
      event.stopPropagation();
      onClick();
    }
  };

  return (
    <span
      className={badgeClasses}
      onClick={clickable ? handleClick : undefined}
      onKeyDown={clickable ? handleKeyDown : undefined}
      role={clickable ? 'button' : undefined}
      tabIndex={clickable ? 0 : undefined}
      aria-label={ariaLabel}
      title={title}
      data-testid={testId}
    >
      {/* Icon */}
      {showIcon && IconComponent && (
        <IconComponent
          className={`${sizeStyles.iconSize} ${shouldPulse && variant === 'processing' ? 'animate-spin' : ''}`}
          aria-hidden="true"
        />
      )}

      {/* Content */}
      <span>{children}</span>
    </span>
  );
});

/**
 * Display name for debugging
 */
StatusBadge.displayName = 'StatusBadge';

/**
 * Predefined status badge components for common use cases
 */

/**
 * Success status badge
 */
export const SuccessBadge: React.FC<Omit<StatusBadgeProps, 'variant'>> = (props) => (
  <StatusBadge variant="success" {...props} />
);

/**
 * Error status badge
 */
export const ErrorBadge: React.FC<Omit<StatusBadgeProps, 'variant'>> = (props) => (
  <StatusBadge variant="error" {...props} />
);

/**
 * Warning status badge
 */
export const WarningBadge: React.FC<Omit<StatusBadgeProps, 'variant'>> = (props) => (
  <StatusBadge variant="warning" {...props} />
);

/**
 * Info status badge
 */
export const InfoBadge: React.FC<Omit<StatusBadgeProps, 'variant'>> = (props) => (
  <StatusBadge variant="info" {...props} />
);

/**
 * Pending status badge
 */
export const PendingBadge: React.FC<Omit<StatusBadgeProps, 'variant'>> = (props) => (
  <StatusBadge variant="pending" {...props} />
);

/**
 * Active status badge
 */
export const ActiveBadge: React.FC<Omit<StatusBadgeProps, 'variant'>> = (props) => (
  <StatusBadge variant="active" {...props} />
);

/**
 * Inactive status badge
 */
export const InactiveBadge: React.FC<Omit<StatusBadgeProps, 'variant'>> = (props) => (
  <StatusBadge variant="inactive" {...props} />
);

/**
 * Processing status badge
 */
export const ProcessingBadge: React.FC<Omit<StatusBadgeProps, 'variant'>> = (props) => (
  <StatusBadge variant="processing" {...props} />
);

/**
 * Default export
 */
export default StatusBadge;