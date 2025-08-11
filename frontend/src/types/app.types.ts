// ~/frontend/src/types/app.types.ts
// ---------------------------------------------------------------------------------------------
// MESTOCKER - App Types
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
/**
 * Tipos para el estado global de la aplicación
 * 
 * Define interfaces para:
 * - Estado de UI global
 * - Configuración de app
 * - Estados de loading y errores
 * - Notificaciones y alerts
 */

// Tipos para theme management
export type AppTheme = 'light' | 'dark' | 'auto';
export type Language = 'es' | 'en';
export type Currency = 'USD' | 'MXN' | 'EUR';

// Estado de UI global
export interface UIState {
  // Theme y apariencia
  theme: AppTheme;
  isDarkMode: boolean; // computado basado en theme y preferencias del sistema
  
  // Layout y navegación
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;
  
  // Estados de loading globales
  isAppLoading: boolean;
  isPageTransitioning: boolean;
  
  // Estados de modal y overlay
  activeModal: string | null;
  modalData: any;
  
  // Estados de notificaciones
  notifications: NotificationItem[];
  alerts: AlertItem[];
}

// Configuración global de la app
export interface AppConfig {
  // Configuración regional
  language: Language;
  currency: Currency;
  timezone: string;
  
  // Configuración de features
  features: {
    darkModeEnabled: boolean;
    notificationsEnabled: boolean;
    analyticsEnabled: boolean;
    betaFeaturesEnabled: boolean;
  };
  
  // Configuración de API
  api: {
    baseUrl: string;
    timeout: number;
    retryAttempts: number;
  };
  
  // Configuración de cache
  cache: {
    enabled: boolean;
    ttl: number; // time to live en minutos
  };
}

// Items de notificación
export interface NotificationItem {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  isRead: boolean;
  autoClose?: boolean;
  duration?: number; // en milisegundos
  action?: {
    label: string;
    onClick: () => void;
  };
}

// Items de alert/banner
export interface AlertItem {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  message: string;
  isVisible: boolean;
  isDismissible: boolean;
  persistent?: boolean;
}

// Estado de performance y debug
export interface PerformanceState {
  lastUpdate: string;
  renderCount: number;
  errorCount: number;
  averageResponseTime: number;
}

// Estado completo de la app
export interface AppState extends UIState {
  // Configuración
  config: AppConfig;
  
  // Performance y debug
  performance: PerformanceState;
  
  // Meta información
  version: string;
  buildNumber: string;
  environment: 'development' | 'staging' | 'production';
}

// Tipos para acciones del store
export interface AppActions {
  // Acciones de theme
  setTheme: (theme: AppTheme) => void;
  toggleTheme: () => void;
  
  // Acciones de UI
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  
  // Acciones de loading
  setAppLoading: (loading: boolean) => void;
  setPageTransitioning: (transitioning: boolean) => void;
  
  // Acciones de modal
  openModal: (modalId: string, data?: any) => void;
  closeModal: () => void;
  
  // Acciones de notificaciones
  addNotification: (notification: Omit<NotificationItem, 'id' | 'timestamp' | 'isRead'>) => void;
  removeNotification: (id: string) => void;
  markNotificationAsRead: (id: string) => void;
  clearAllNotifications: () => void;
  
  // Acciones de alerts
  showAlert: (alert: Omit<AlertItem, 'id' | 'isVisible'>) => void;
  hideAlert: (id: string) => void;
  clearAllAlerts: () => void;
  
  // Acciones de configuración
  updateConfig: (config: Partial<AppConfig>) => void;
  updateLanguage: (language: Language) => void;
  updateCurrency: (currency: Currency) => void;
  
  // Acciones de utilidad
  resetAppState: () => void;
  updatePerformanceMetrics: (metrics: Partial<PerformanceState>) => void;
}

// Tipo combinado del store
export interface AppStoreType extends AppState, AppActions {}

// Tipos para selectores
export type AppSelector<T> = (state: AppStoreType) => T;

// Tipos para subscripción a cambios específicos
export interface AppSubscriptionOptions {
  fireImmediately?: boolean;
  equalityFn?: (a: any, b: any) => boolean;
}