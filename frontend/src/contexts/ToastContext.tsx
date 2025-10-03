/**
 * Toast Context
 * Provides global toast notification system throughout the application
 */

import React, { createContext, useContext, useState, useCallback } from 'react';
import ToastContainer from '../components/common/ToastContainer';
import { ToastType } from '../components/common/Toast';
import { errorHandler, AppError } from '../utils/errorHandler';

export interface ToastMessage {
  id: string;
  message: string;
  type: ToastType;
  duration?: number;
}

interface ToastContextType {
  showToast: (message: string, type: ToastType, duration?: number) => void;
  showSuccess: (message: string, duration?: number) => void;
  showError: (message: string | AppError, duration?: number) => void;
  showWarning: (message: string, duration?: number) => void;
  showInfo: (message: string, duration?: number) => void;
  removeToast: (id: string) => void;
  clearAllToasts: () => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = (): ToastContextType => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

interface ToastProviderProps {
  children: React.ReactNode;
  maxToasts?: number;
  defaultDuration?: number;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
}

export const ToastProvider: React.FC<ToastProviderProps> = ({
  children,
  maxToasts = 5,
  defaultDuration = 5000,
  position = 'top-right'
}) => {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  // Generate unique ID for toast
  const generateId = (): string => {
    return `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  };

  // Add toast to stack
  const showToast = useCallback(
    (message: string, type: ToastType, duration: number = defaultDuration) => {
      const id = generateId();
      const newToast: ToastMessage = { id, message, type, duration };

      setToasts((prevToasts) => {
        // Limit number of toasts
        const updatedToasts = [...prevToasts, newToast];
        if (updatedToasts.length > maxToasts) {
          return updatedToasts.slice(-maxToasts);
        }
        return updatedToasts;
      });

      return id;
    },
    [maxToasts, defaultDuration]
  );

  // Show success toast
  const showSuccess = useCallback(
    (message: string, duration?: number) => {
      return showToast(message, 'success', duration);
    },
    [showToast]
  );

  // Show error toast
  const showError = useCallback(
    (messageOrError: string | AppError, duration?: number) => {
      let message: string;

      if (typeof messageOrError === 'string') {
        message = messageOrError;
      } else {
        // Handle AppError object
        message = errorHandler.getUserMessage(messageOrError);

        // Log error for debugging
        errorHandler.logError(messageOrError);
      }

      return showToast(message, 'error', duration);
    },
    [showToast]
  );

  // Show warning toast
  const showWarning = useCallback(
    (message: string, duration?: number) => {
      return showToast(message, 'warning', duration);
    },
    [showToast]
  );

  // Show info toast
  const showInfo = useCallback(
    (message: string, duration?: number) => {
      return showToast(message, 'info', duration);
    },
    [showToast]
  );

  // Remove specific toast
  const removeToast = useCallback((id: string) => {
    setToasts((prevToasts) => prevToasts.filter((toast) => toast.id !== id));
  }, []);

  // Clear all toasts
  const clearAllToasts = useCallback(() => {
    setToasts([]);
  }, []);

  const value: ToastContextType = {
    showToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    removeToast,
    clearAllToasts
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastContainer
        toasts={toasts}
        onClose={removeToast}
        position={position}
      />
    </ToastContext.Provider>
  );
};

/**
 * Hook to show API errors with toast notifications
 * Automatically handles different error types and shows appropriate messages
 */
export const useApiErrorToast = () => {
  const { showError } = useToast();

  return useCallback(
    (error: any, context?: string) => {
      const appError = errorHandler.handleApiError(error);

      // Show error toast
      showError(appError);

      // Handle auto-logout if needed
      if (errorHandler.shouldLogout(appError)) {
        // Clear auth tokens
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');

        // Redirect to login after a short delay
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
      }

      return appError;
    },
    [showError]
  );
};

export default ToastContext;
