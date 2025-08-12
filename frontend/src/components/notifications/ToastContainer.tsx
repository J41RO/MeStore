import * as React from 'react';
import { useNotifications } from '../../contexts/NotificationContext';
import { Toast } from './Toast';

interface ToastContainerProps {
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
  maxToasts?: number;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ 
  position = 'top-right',
  maxToasts = 5
}) => {
  const { notifications, removeNotification } = useNotifications();

  // Filtrar solo notificaciones activas y limitar cantidad
  const activeNotifications = notifications
    .slice(0, maxToasts);

  if (activeNotifications.length === 0) {
    return null;
  }

  return (
    <div className="fixed z-50 pointer-events-none">
      <div className="space-y-2">
        {activeNotifications.map((notification, index) => (
          <div
            key={notification.id}
            className="pointer-events-auto"
            style={{
              animationDelay: `${index * 100}ms`,
              transform: `translateY(${index * 4}px)`,
              zIndex: 50 - index
            }}
          >
            <Toast
              notification={notification}
              onRemove={removeNotification}
              position={position}
            />
          </div>
        ))}
      </div>
    </div>
  );
};