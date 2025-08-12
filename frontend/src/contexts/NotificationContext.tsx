import * as React from 'react';
import { createContext, useContext, ReactNode } from 'react';
import { useAppStore } from '../stores/appStore';
import { NotificationItem, AlertItem } from '../types/app.types';

interface NotificationContextType {
  // Estado
  notifications: NotificationItem[];
  alerts: AlertItem[];
  unreadCount: number;
  
  // Métodos simplificados
  showNotification: (notification: Omit<NotificationItem, 'id' | 'timestamp' | 'isRead'>) => void;
  showAlert: (alert: Omit<AlertItem, 'id' | 'isVisible'>) => void;
  removeNotification: (id: string) => void;
  hideAlert: (id: string) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const {
    notifications,
    alerts,
    addNotification,
    showAlert,
    removeNotification,
    hideAlert
  } = useAppStore();
  
  const unreadCount = notifications.filter(n => !n.isRead).length;

  const contextValue: NotificationContextType = {
    notifications,
    alerts,
    unreadCount,
    showNotification: addNotification,
    showAlert,
    removeNotification,
    hideAlert
  };

  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = (): NotificationContextType => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};