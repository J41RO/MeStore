import React, { useState, useEffect } from 'react';
import { X, CheckCircle, XCircle, AlertCircle, Clock, CreditCard } from 'lucide-react';

export interface PaymentNotification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info' | 'processing';
  title: string;
  message: string;
  orderId?: string;
  transactionId?: string;
  amount?: number;
  autoDismiss?: boolean;
  dismissAfter?: number;
  onAction?: () => void;
  actionLabel?: string;
}

interface PaymentNotificationsProps {
  notifications: PaymentNotification[];
  onDismiss: (id: string) => void;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
}

const PaymentNotifications: React.FC<PaymentNotificationsProps> = ({
  notifications,
  onDismiss,
  position = 'top-right'
}) => {
  const [visibleNotifications, setVisibleNotifications] = useState<PaymentNotification[]>([]);

  useEffect(() => {
    setVisibleNotifications(notifications);

    // Auto-dismiss notifications
    notifications.forEach(notification => {
      if (notification.autoDismiss !== false) {
        const dismissAfter = notification.dismissAfter || 5000;
        setTimeout(() => {
          onDismiss(notification.id);
        }, dismissAfter);
      }
    });
  }, [notifications, onDismiss]);

  const getIcon = (type: PaymentNotification['type']) => {
    const iconClass = "w-5 h-5 flex-shrink-0";

    switch (type) {
      case 'success':
        return <CheckCircle className={`${iconClass} text-green-500`} />;
      case 'error':
        return <XCircle className={`${iconClass} text-red-500`} />;
      case 'warning':
        return <AlertCircle className={`${iconClass} text-yellow-500`} />;
      case 'processing':
        return <Clock className={`${iconClass} text-blue-500 animate-pulse`} />;
      case 'info':
      default:
        return <CreditCard className={`${iconClass} text-blue-500`} />;
    }
  };

  const getBackgroundColor = (type: PaymentNotification['type']) => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'processing':
        return 'bg-blue-50 border-blue-200';
      case 'info':
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getTextColor = (type: PaymentNotification['type']) => {
    switch (type) {
      case 'success':
        return 'text-green-800';
      case 'error':
        return 'text-red-800';
      case 'warning':
        return 'text-yellow-800';
      case 'processing':
        return 'text-blue-800';
      case 'info':
      default:
        return 'text-gray-800';
    }
  };

  const getPositionClasses = () => {
    switch (position) {
      case 'top-left':
        return 'top-4 left-4';
      case 'bottom-right':
        return 'bottom-4 right-4';
      case 'bottom-left':
        return 'bottom-4 left-4';
      case 'top-right':
      default:
        return 'top-4 right-4';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount);
  };

  if (visibleNotifications.length === 0) {
    return null;
  }

  return (
    <div className={`fixed ${getPositionClasses()} z-50 space-y-3 max-w-sm w-full`}>
      {visibleNotifications.map((notification) => (
        <div
          key={notification.id}
          className={`
            ${getBackgroundColor(notification.type)}
            border rounded-lg shadow-lg p-4 transform transition-all duration-300 ease-in-out
            animate-slide-in-right
          `}
        >
          <div className="flex items-start space-x-3">
            {/* Icon */}
            <div className="flex-shrink-0 mt-0.5">
              {getIcon(notification.type)}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <h4 className={`text-sm font-medium ${getTextColor(notification.type)}`}>
                {notification.title}
              </h4>

              <p className={`mt-1 text-sm ${getTextColor(notification.type)} opacity-90`}>
                {notification.message}
              </p>

              {/* Additional details */}
              {(notification.orderId || notification.amount) && (
                <div className="mt-2 space-y-1">
                  {notification.orderId && (
                    <p className={`text-xs ${getTextColor(notification.type)} opacity-75`}>
                      Orden: #{notification.orderId}
                    </p>
                  )}
                  {notification.amount && (
                    <p className={`text-xs ${getTextColor(notification.type)} opacity-75`}>
                      Monto: {formatCurrency(notification.amount)}
                    </p>
                  )}
                  {notification.transactionId && (
                    <p className={`text-xs ${getTextColor(notification.type)} opacity-75`}>
                      ID: {notification.transactionId}
                    </p>
                  )}
                </div>
              )}

              {/* Action button */}
              {notification.onAction && notification.actionLabel && (
                <button
                  onClick={notification.onAction}
                  className={`
                    mt-3 text-xs font-medium px-3 py-1 rounded border transition-colors
                    ${notification.type === 'success'
                      ? 'border-green-300 text-green-700 hover:bg-green-100'
                      : notification.type === 'error'
                      ? 'border-red-300 text-red-700 hover:bg-red-100'
                      : 'border-blue-300 text-blue-700 hover:bg-blue-100'
                    }
                  `}
                >
                  {notification.actionLabel}
                </button>
              )}
            </div>

            {/* Close button */}
            <button
              onClick={() => onDismiss(notification.id)}
              className={`
                flex-shrink-0 rounded-md p-1.5 transition-colors
                ${notification.type === 'success'
                  ? 'text-green-400 hover:bg-green-100'
                  : notification.type === 'error'
                  ? 'text-red-400 hover:bg-red-100'
                  : notification.type === 'warning'
                  ? 'text-yellow-400 hover:bg-yellow-100'
                  : 'text-gray-400 hover:bg-gray-100'
                }
              `}
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

// Hook for managing payment notifications
export const usePaymentNotifications = () => {
  const [notifications, setNotifications] = useState<PaymentNotification[]>([]);

  const addNotification = (notification: Omit<PaymentNotification, 'id'>) => {
    const id = Date.now().toString() + Math.random().toString(36).substr(2, 9);
    const newNotification: PaymentNotification = {
      id,
      ...notification
    };

    setNotifications(prev => [...prev, newNotification]);
    return id;
  };

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const clearAllNotifications = () => {
    setNotifications([]);
  };

  // Predefined notification types for payments
  const notifyPaymentSuccess = (orderId: string, amount: number, transactionId?: string) => {
    return addNotification({
      type: 'success',
      title: '¡Pago exitoso!',
      message: 'Tu pago ha sido procesado correctamente.',
      orderId,
      amount,
      transactionId,
      actionLabel: 'Ver pedido',
      onAction: () => window.location.href = `/orders/${orderId}`
    });
  };

  const notifyPaymentError = (orderId: string, error: string) => {
    return addNotification({
      type: 'error',
      title: 'Error en el pago',
      message: error,
      orderId,
      autoDismiss: false,
      actionLabel: 'Reintentar',
      onAction: () => window.location.href = `/checkout`
    });
  };

  const notifyPaymentProcessing = (orderId: string, amount: number) => {
    return addNotification({
      type: 'processing',
      title: 'Procesando pago...',
      message: 'Tu pago está siendo procesado. Te notificaremos cuando esté listo.',
      orderId,
      amount,
      autoDismiss: false
    });
  };

  const notifyPaymentPending = (orderId: string, amount: number) => {
    return addNotification({
      type: 'warning',
      title: 'Pago pendiente',
      message: 'Tu pago está pendiente de confirmación bancaria.',
      orderId,
      amount,
      dismissAfter: 8000
    });
  };

  return {
    notifications,
    addNotification,
    removeNotification,
    clearAllNotifications,
    notifyPaymentSuccess,
    notifyPaymentError,
    notifyPaymentProcessing,
    notifyPaymentPending
  };
};

export default PaymentNotifications;