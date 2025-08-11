// ~/frontend/src/hooks/useApp.ts
// ---------------------------------------------------------------------------------------------
// MESTOCKER - useApp Hook
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
/**
 * Hook simplificado para manejo del estado global de la app
 * 
 * Proporciona interfaz limpia para componentes que necesitan estado global
 */

import { useAppStore } from '../stores/appStore';

/**
 * Hook simplificado para manejo del estado global de la app
 */
export const useApp = () => {
  // Selectores primitivos directos (no objetos)
  const theme = useAppStore(state => state.theme);
  const isDarkMode = useAppStore(state => state.isDarkMode);
  const sidebarOpen = useAppStore(state => state.sidebarOpen);
  const sidebarCollapsed = useAppStore(state => state.sidebarCollapsed);
  const isAppLoading = useAppStore(state => state.isAppLoading);
  const isPageTransitioning = useAppStore(state => state.isPageTransitioning);
  const activeModal = useAppStore(state => state.activeModal);
  const modalData = useAppStore(state => state.modalData);
  const notifications = useAppStore(state => state.notifications);
  const alerts = useAppStore(state => state.alerts);
  const language = useAppStore(state => state.config.language);
  const currency = useAppStore(state => state.config.currency);
  
  // Acciones del store
  const {
    setTheme,
    toggleTheme,
    setSidebarOpen,
    toggleSidebar,
    setSidebarCollapsed,
    setAppLoading,
    setPageTransitioning,
    openModal,
    closeModal,
    addNotification,
    removeNotification,
    markNotificationAsRead,
    clearAllNotifications,
    showAlert,
    hideAlert,
    clearAllAlerts,
    updateLanguage,
    updateCurrency,
    resetAppState
  } = useAppStore();
  
  // Métodos de conveniencia para notificaciones
  const showSuccessNotification = (title: string, message: string) => {
    addNotification({
      type: 'success',
      title,
      message,
      autoClose: true,
      duration: 5000
    });
  };
  
  const showErrorNotification = (title: string, message: string) => {
    addNotification({
      type: 'error',
      title,
      message,
      autoClose: true,
      duration: 8000
    });
  };
  
  const showInfoNotification = (title: string, message: string) => {
    addNotification({
      type: 'info',
      title,
      message,
      autoClose: true,
      duration: 6000
    });
  };
  
  const showWarningNotification = (title: string, message: string) => {
    addNotification({
      type: 'warning',
      title,
      message,
      autoClose: true,
      duration: 7000
    });
  };
  
  // Métodos de conveniencia para alerts
  const showSuccessAlert = (message: string, persistent = false) => {
    showAlert({
      type: 'success',
      message,
      isDismissible: true,
      persistent
    });
  };
  
  const showErrorAlert = (message: string, persistent = true) => {
    showAlert({
      type: 'error',
      message,
      isDismissible: true,
      persistent
    });
  };
  
  // Métodos de tema
  const enableDarkMode = () => setTheme('dark');
  const enableLightMode = () => setTheme('light');
  const enableAutoMode = () => setTheme('auto');
  
  // Métodos de sidebar
  const openSidebar = () => setSidebarOpen(true);
  const closeSidebar = () => setSidebarOpen(false);
  const expandSidebar = () => setSidebarCollapsed(false);
  const collapseSidebar = () => setSidebarCollapsed(true);
  
  // Métodos de loading
  const showAppLoading = () => setAppLoading(true);
  const hideAppLoading = () => setAppLoading(false);
  const showPageTransition = () => setPageTransitioning(true);
  const hidePageTransition = () => setPageTransitioning(false);
  
  // Métodos de modal
  const openConfirmModal = (data: any) => openModal('confirm', data);
  const openSettingsModal = () => openModal('settings');
  const openProfileModal = () => openModal('profile');
  
  // Estados computados (calculados una vez por render)
  const unreadNotifications = notifications.filter(n => !n.isRead);
  const notificationCount = unreadNotifications.length;
  const visibleAlerts = alerts.filter(a => a.isVisible);
  const hasUnreadNotifications = notificationCount > 0;
  const hasVisibleAlerts = visibleAlerts.length > 0;
  const isSidebarVisible = sidebarOpen && !sidebarCollapsed;
  
  return {
    // Estado básico
    theme,
    isDarkMode,
    language,
    currency,
    
    // Estados de UI
    sidebar: {
      isOpen: sidebarOpen,
      isCollapsed: sidebarCollapsed,
      isVisible: isSidebarVisible
    },
    
    loading: {
      isAppLoading: isAppLoading,
      isPageTransitioning: isPageTransitioning
    },
    
    modal: {
      activeModal: activeModal,
      modalData: modalData,
      isOpen: activeModal !== null
    },
    
    notifications: {
      unread: unreadNotifications,
      count: notificationCount,
      hasUnread: hasUnreadNotifications
    },
    
    alerts: {
      visible: visibleAlerts,
      hasVisible: hasVisibleAlerts
    },
    
    // Métodos de theme
    setTheme,
    toggleTheme,
    enableDarkMode,
    enableLightMode,
    enableAutoMode,
    
    // Métodos de sidebar
    setSidebarOpen,
    toggleSidebar,
    setSidebarCollapsed,
    openSidebar,
    closeSidebar,
    expandSidebar,
    collapseSidebar,
    
    // Métodos de loading
    setAppLoading,
    setPageTransitioning,
    showAppLoading,
    hideAppLoading,
    showPageTransition,
    hidePageTransition,
    
    // Métodos de modal
    openModal,
    closeModal,
    openConfirmModal,
    openSettingsModal,
    openProfileModal,
    
    // Métodos de notificaciones
    addNotification,
    removeNotification,
    markNotificationAsRead,
    clearAllNotifications,
    showSuccessNotification,
    showErrorNotification,
    showInfoNotification,
    showWarningNotification,
    
    // Métodos de alerts
    showAlert,
    hideAlert,
    clearAllAlerts,
    showSuccessAlert,
    showErrorAlert,
    
    // Métodos de configuración
    updateLanguage,
    updateCurrency,
    
    // Métodos de utilidad
    resetAppState
  };
};

export type UseAppReturn = ReturnType<typeof useApp>;
