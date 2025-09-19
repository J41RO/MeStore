// frontend/src/components/vendor/VendorAccessibility.tsx
// PRODUCTION_READY: Componentes de accesibilidad para vendedores
// Cumple con WCAG 2.1 AA y optimizado para lectores de pantalla

import React, { useEffect, useRef, useState } from 'react';
import {
  AlertCircle,
  CheckCircle,
  Info,
  X,
  ChevronDown,
  ChevronUp,
  HelpCircle
} from 'lucide-react';

// Tipos para accesibilidad
export interface AccessibilityProps {
  'aria-label'?: string;
  'aria-labelledby'?: string;
  'aria-describedby'?: string;
  'aria-expanded'?: boolean;
  'aria-hidden'?: boolean;
  role?: string;
  tabIndex?: number;
}

// Hook para gestión de foco
export const useFocusManagement = () => {
  const focusableElements = useRef<HTMLElement[]>([]);

  const trapFocus = (container: HTMLElement) => {
    const focusableSelectors = [
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      'a[href]',
      '[tabindex]:not([tabindex="-1"])'
    ].join(', ');

    focusableElements.current = Array.from(
      container.querySelectorAll(focusableSelectors)
    ) as HTMLElement[];

    const firstElement = focusableElements.current[0];
    const lastElement = focusableElements.current[focusableElements.current.length - 1];

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    container.addEventListener('keydown', handleTabKey);
    firstElement?.focus();

    return () => {
      container.removeEventListener('keydown', handleTabKey);
    };
  };

  return { trapFocus };
};

// Componente de anuncio para lectores de pantalla
interface ScreenReaderAnnouncementProps {
  message: string;
  priority: 'polite' | 'assertive';
  onComplete?: () => void;
}

export const ScreenReaderAnnouncement: React.FC<ScreenReaderAnnouncementProps> = ({
  message,
  priority,
  onComplete
}) => {
  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => {
        onComplete?.();
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [message, onComplete]);

  if (!message) return null;

  return (
    <div
      aria-live={priority}
      aria-atomic="true"
      className="sr-only"
    >
      {message}
    </div>
  );
};

// Componente de saltar navegación
export const SkipNavigation: React.FC = () => {
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-primary-600 text-white px-4 py-2 rounded-md z-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
    >
      Saltar al contenido principal
    </a>
  );
};

// Componente de breadcrumb accesible
interface AccessibleBreadcrumbProps {
  items: Array<{
    label: string;
    href?: string;
    current?: boolean;
  }>;
  className?: string;
}

export const AccessibleBreadcrumb: React.FC<AccessibleBreadcrumbProps> = ({
  items,
  className = ''
}) => {
  return (
    <nav aria-label="Breadcrumb" className={className}>
      <ol className="flex items-center space-x-2 text-sm text-neutral-600">
        {items.map((item, index) => (
          <li key={index} className="flex items-center">
            {index > 0 && (
              <span className="mx-2 text-neutral-400" aria-hidden="true">
                /
              </span>
            )}
            {item.href && !item.current ? (
              <a
                href={item.href}
                className="hover:text-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-1 rounded"
              >
                {item.label}
              </a>
            ) : (
              <span
                className={item.current ? 'text-neutral-900 font-medium' : ''}
                aria-current={item.current ? 'page' : undefined}
              >
                {item.label}
              </span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
};

// Componente de tooltip accesible
interface AccessibleTooltipProps {
  content: string;
  children: React.ReactNode;
  placement?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
}

export const AccessibleTooltip: React.FC<AccessibleTooltipProps> = ({
  content,
  children,
  placement = 'top',
  className = ''
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const tooltipId = `tooltip-${Math.random().toString(36).substr(2, 9)}`;

  const placementClasses = {
    top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 transform -translate-y-1/2 ml-2'
  };

  return (
    <div className={`relative inline-block ${className}`}>
      <div
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        onFocus={() => setIsVisible(true)}
        onBlur={() => setIsVisible(false)}
        aria-describedby={tooltipId}
      >
        {children}
      </div>
      {isVisible && (
        <div
          id={tooltipId}
          role="tooltip"
          className={`absolute z-50 px-2 py-1 text-sm text-white bg-neutral-900 rounded shadow-lg ${placementClasses[placement]}`}
        >
          {content}
          <div
            className={`absolute w-2 h-2 bg-neutral-900 transform rotate-45 ${
              placement === 'top' ? 'top-full left-1/2 -translate-x-1/2 -mt-1' :
              placement === 'bottom' ? 'bottom-full left-1/2 -translate-x-1/2 -mb-1' :
              placement === 'left' ? 'left-full top-1/2 -translate-y-1/2 -ml-1' :
              'right-full top-1/2 -translate-y-1/2 -mr-1'
            }`}
          />
        </div>
      )}
    </div>
  );
};

// Componente de modal accesible
interface AccessibleModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

export const AccessibleModal: React.FC<AccessibleModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  className = ''
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const { trapFocus } = useFocusManagement();
  const titleId = `modal-title-${Math.random().toString(36).substr(2, 9)}`;

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
  };

  useEffect(() => {
    if (isOpen && modalRef.current) {
      const cleanup = trapFocus(modalRef.current);
      document.body.style.overflow = 'hidden';

      return () => {
        cleanup();
        document.body.style.overflow = '';
      };
    }
  }, [isOpen, trapFocus]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto"
      aria-labelledby={titleId}
      aria-modal="true"
      role="dialog"
    >
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Overlay */}
        <div
          className="fixed inset-0 transition-opacity bg-black bg-opacity-50"
          aria-hidden="true"
          onClick={onClose}
        />

        {/* Modal content */}
        <div
          ref={modalRef}
          className={`
            inline-block w-full ${sizeClasses[size]} p-6 my-8 text-left align-middle
            transition-all transform bg-white shadow-xl rounded-lg ${className}
          `}
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <h2
              id={titleId}
              className="text-lg font-semibold text-neutral-900"
            >
              {title}
            </h2>
            <button
              onClick={onClose}
              className="p-2 text-neutral-400 hover:text-neutral-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 rounded"
              aria-label="Cerrar modal"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div>{children}</div>
        </div>
      </div>
    </div>
  );
};

// Componente de notificación accesible
interface AccessibleNotificationProps {
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  isVisible: boolean;
  onClose: () => void;
  autoClose?: boolean;
  autoCloseDelay?: number;
}

export const AccessibleNotification: React.FC<AccessibleNotificationProps> = ({
  type,
  title,
  message,
  isVisible,
  onClose,
  autoClose = true,
  autoCloseDelay = 5000
}) => {
  useEffect(() => {
    if (isVisible && autoClose) {
      const timer = setTimeout(() => {
        onClose();
      }, autoCloseDelay);

      return () => clearTimeout(timer);
    }
  }, [isVisible, autoClose, autoCloseDelay, onClose]);

  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertCircle,
    info: Info
  };

  const colors = {
    success: 'bg-secondary-50 border-secondary-200 text-secondary-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-primary-50 border-primary-200 text-primary-800'
  };

  const iconColors = {
    success: 'text-secondary-600',
    error: 'text-red-600',
    warning: 'text-yellow-600',
    info: 'text-primary-600'
  };

  const Icon = icons[type];

  if (!isVisible) return null;

  return (
    <div
      role="alert"
      aria-live="assertive"
      className={`
        fixed top-4 right-4 z-50 max-w-sm p-4 border rounded-lg shadow-lg
        transform transition-all duration-300 ${colors[type]}
      `}
    >
      <div className="flex items-start gap-3">
        <Icon className={`w-5 h-5 mt-0.5 ${iconColors[type]}`} />
        <div className="flex-1 min-w-0">
          <h4 className="font-medium">{title}</h4>
          <p className="text-sm mt-1">{message}</p>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-white hover:bg-opacity-20 rounded focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-current"
          aria-label="Cerrar notificación"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

// Componente de accordion accesible
interface AccordionItem {
  id: string;
  title: string;
  content: React.ReactNode;
}

interface AccessibleAccordionProps {
  items: AccordionItem[];
  allowMultiple?: boolean;
  className?: string;
}

export const AccessibleAccordion: React.FC<AccessibleAccordionProps> = ({
  items,
  allowMultiple = false,
  className = ''
}) => {
  const [openItems, setOpenItems] = useState<Set<string>>(new Set());

  const toggleItem = (itemId: string) => {
    setOpenItems(prev => {
      const newSet = new Set(prev);

      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        if (!allowMultiple) {
          newSet.clear();
        }
        newSet.add(itemId);
      }

      return newSet;
    });
  };

  return (
    <div className={`space-y-2 ${className}`}>
      {items.map((item) => {
        const isOpen = openItems.has(item.id);
        const headingId = `accordion-heading-${item.id}`;
        const panelId = `accordion-panel-${item.id}`;

        return (
          <div key={item.id} className="border border-neutral-200 rounded-lg">
            <h3 id={headingId}>
              <button
                onClick={() => toggleItem(item.id)}
                aria-expanded={isOpen}
                aria-controls={panelId}
                className="w-full px-4 py-3 text-left font-medium text-neutral-900 hover:bg-neutral-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-inset rounded-lg transition-colors"
              >
                <div className="flex items-center justify-between">
                  <span>{item.title}</span>
                  {isOpen ? (
                    <ChevronUp className="w-5 h-5 text-neutral-500" aria-hidden="true" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-neutral-500" aria-hidden="true" />
                  )}
                </div>
              </button>
            </h3>
            <div
              id={panelId}
              role="region"
              aria-labelledby={headingId}
              className={`
                transition-all duration-200 overflow-hidden
                ${isOpen ? 'max-h-screen opacity-100' : 'max-h-0 opacity-0'}
              `}
            >
              <div className="px-4 pb-3">
                {item.content}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

// Hook para anuncios de estado
export const useStatusAnnouncements = () => {
  const [announcement, setAnnouncement] = useState<{
    message: string;
    priority: 'polite' | 'assertive';
  } | null>(null);

  const announce = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    setAnnouncement({ message, priority });
  };

  const clear = () => {
    setAnnouncement(null);
  };

  return {
    announcement,
    announce,
    clear
  };
};

export default {
  ScreenReaderAnnouncement,
  SkipNavigation,
  AccessibleBreadcrumb,
  AccessibleTooltip,
  AccessibleModal,
  AccessibleNotification,
  AccessibleAccordion,
  useFocusManagement,
  useStatusAnnouncements
};