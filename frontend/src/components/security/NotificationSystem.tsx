/**
 * NotificationSystem Component
 * Frontend Security AI Implementation
 *
 * Sistema de notificaciones para mostrar errores, alertas de seguridad
 * y mensajes informativos al usuario
 */

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { X, AlertTriangle, CheckCircle, Info, Shield } from 'lucide-react';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info' | 'security';
  title: string;
  message: string;
  duration?: number;
  persistent?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id'>) => string;
  removeNotification: (id: string) => void;
  clearAll: () => void;
  showSuccess: (title: string, message: string, duration?: number) => string;
  showError: (title: string, message: string, persistent?: boolean) => string;
  showWarning: (title: string, message: string, duration?: number) => string;
  showInfo: (title: string, message: string, duration?: number) => string;
  showSecurityAlert: (title: string, message: string, persistent?: boolean) => string;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotifications = (): NotificationContextType => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};

interface NotificationProviderProps {
  children: React.ReactNode;
  maxNotifications?: number;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({
  children,
  maxNotifications = 5,
}) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  // Add notification
  const addNotification = useCallback((notification: Omit<Notification, 'id'>): string => {
    const id = Math.random().toString(36).substr(2, 9);
    const newNotification: Notification = {
      ...notification,
      id,
      duration: notification.duration ?? (notification.type === 'error' ? 8000 : 5000),
    };

    setNotifications(prev => {
      const updated = [newNotification, ...prev];
      // Keep only the maximum number of notifications
      return updated.slice(0, maxNotifications);
    });

    // Auto-remove non-persistent notifications
    if (!notification.persistent && newNotification.duration) {
      setTimeout(() => {
        removeNotification(id);
      }, newNotification.duration);
    }

    return id;
  }, [maxNotifications]);

  // Remove notification
  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  // Clear all notifications
  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  // Convenience methods
  const showSuccess = useCallback((title: string, message: string, duration?: number) => {
    return addNotification({ type: 'success', title, message, duration });
  }, [addNotification]);

  const showError = useCallback((title: string, message: string, persistent?: boolean) => {
    return addNotification({ type: 'error', title, message, persistent });
  }, [addNotification]);

  const showWarning = useCallback((title: string, message: string, duration?: number) => {
    return addNotification({ type: 'warning', title, message, duration });
  }, [addNotification]);

  const showInfo = useCallback((title: string, message: string, duration?: number) => {
    return addNotification({ type: 'info', title, message, duration });
  }, [addNotification]);

  const showSecurityAlert = useCallback((title: string, message: string, persistent?: boolean) => {
    return addNotification({ type: 'security', title, message, persistent: persistent ?? true });
  }, [addNotification]);

  const contextValue: NotificationContextType = {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showSecurityAlert,
  };

  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
      <NotificationDisplay />
    </NotificationContext.Provider>
  );
};

// Notification display component
const NotificationDisplay: React.FC = () => {
  const { notifications, removeNotification } = useNotifications();

  if (notifications.length === 0) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 z-50 space-y-3">
      {notifications.map((notification) => (
        <NotificationItem
          key={notification.id}
          notification={notification}
          onRemove={() => removeNotification(notification.id)}
        />
      ))}
    </div>
  );
};

// Individual notification item
interface NotificationItemProps {
  notification: Notification;
  onRemove: () => void;
}

const NotificationItem: React.FC<NotificationItemProps> = ({ notification, onRemove }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Trigger animation
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  const handleRemove = () => {
    setIsVisible(false);
    setTimeout(onRemove, 300); // Wait for animation
  };

  const getNotificationStyles = () => {
    const baseStyles = "transform transition-all duration-300 ease-in-out";
    const visibleStyles = isVisible ? "translate-x-0 opacity-100" : "translate-x-full opacity-0";

    const typeStyles = {
      success: "bg-green-50 border-green-200 text-green-800",
      error: "bg-red-50 border-red-200 text-red-800",
      warning: "bg-yellow-50 border-yellow-200 text-yellow-800",
      info: "bg-blue-50 border-blue-200 text-blue-800",
      security: "bg-purple-50 border-purple-200 text-purple-800",
    };

    return `${baseStyles} ${visibleStyles} ${typeStyles[notification.type]} w-96 p-4 rounded-lg border shadow-lg`;
  };

  const getIcon = () => {
    const iconProps = { size: 20, className: "flex-shrink-0" };

    switch (notification.type) {
      case 'success':
        return <CheckCircle {...iconProps} className="text-green-600 flex-shrink-0" />;
      case 'error':
        return <AlertTriangle {...iconProps} className="text-red-600 flex-shrink-0" />;
      case 'warning':
        return <AlertTriangle {...iconProps} className="text-yellow-600 flex-shrink-0" />;
      case 'info':
        return <Info {...iconProps} className="text-blue-600 flex-shrink-0" />;
      case 'security':
        return <Shield {...iconProps} className="text-purple-600 flex-shrink-0" />;
      default:
        return <Info {...iconProps} />;
    }
  };

  return (
    <div className={getNotificationStyles()}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          {getIcon()}
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-sm">{notification.title}</h4>
            <p className="text-sm opacity-90 mt-1">{notification.message}</p>
            {notification.action && (
              <button
                onClick={notification.action.onClick}
                className="mt-2 text-sm font-medium underline hover:no-underline"
              >
                {notification.action.label}
              </button>
            )}
          </div>
        </div>

        <button
          onClick={handleRemove}
          className="ml-3 p-1 rounded-full hover:bg-black/10 transition-colors"
          aria-label="Cerrar notificación"
        >
          <X size={16} />
        </button>
      </div>

      {/* Progress bar for auto-dismiss */}
      {!notification.persistent && notification.duration && (
        <div className="mt-3 w-full bg-black/10 rounded-full h-1 overflow-hidden">
          <div
            className="h-full bg-current opacity-50"
            style={{
              animation: `shrink ${notification.duration}ms linear forwards`,
            }}
          />
        </div>
      )}

      <style jsx>{`
        @keyframes shrink {
          from { width: 100%; }
          to { width: 0%; }
        }
      `}</style>
    </div>
  );
};

export default NotificationProvider;