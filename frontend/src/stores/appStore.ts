// ~/frontend/src/stores/appStore.ts
// ---------------------------------------------------------------------------------------------
// MESTOCKER - App Store
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
/**
 * AppStore - Estado global de la aplicación con Zustand
 * 
 * Maneja:
 * - Theme y apariencia (dark/light/auto)
 * - Estado de UI (sidebar, modals, loading)
 * - Notificaciones y alerts
 * - Configuración global de la app
 */

import { create } from 'zustand';
import { persist, devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { 
  AppStoreType, 
  AppTheme, 
  Language, 
  Currency, 
  NotificationItem, 
  AlertItem,
  AppConfig,
  PerformanceState
} from '../types/app.types';

// Configuración por defecto
const defaultConfig: AppConfig = {
  language: 'es',
  currency: 'USD',
  timezone: 'America/Mexico_City',
  
  features: {
    darkModeEnabled: true,
    notificationsEnabled: true,
    analyticsEnabled: false,
    betaFeaturesEnabled: false
  },
  
  api: {
    baseUrl: process.env.VITE_API_BASE_URL || 'http://192.168.1.137:8000',
    timeout: 30000,
    retryAttempts: 3
  },
  
  cache: {
    enabled: true,
    ttl: 5 // 5 minutos
  }
};

// Estado inicial de performance
const initialPerformance: PerformanceState = {
  lastUpdate: new Date().toISOString(),
  renderCount: 0,
  errorCount: 0,
  averageResponseTime: 0
};

// Función para detectar dark mode del sistema
const getSystemDarkMode = (): boolean => {
  if (typeof window !== 'undefined') {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  return false;
};

// Función para calcular isDarkMode basado en theme
const calculateIsDarkMode = (theme: AppTheme): boolean => {
  switch (theme) {
    case 'dark':
      return true;
    case 'light':
      return false;
    case 'auto':
      return getSystemDarkMode();
    default:
      return false;
  }
};

// Crear el store de app
export const useAppStore = create<AppStoreType>()(
  devtools(
    persist(
      immer((set, get) => ({
        // Estado inicial de UI
        theme: 'auto' as AppTheme,
        isDarkMode: calculateIsDarkMode('auto'),
        sidebarOpen: true,
        sidebarCollapsed: false,
        isAppLoading: false,
        isPageTransitioning: false,
        activeModal: null,
        modalData: null,
        notifications: [],
        alerts: [],
        
        // Configuración inicial
        config: defaultConfig,
        
        // Performance inicial
        performance: initialPerformance,
        
        // Meta información
        version: '1.0.0',
        buildNumber: process.env.VITE_BUILD_NUMBER || '1',
        environment: (process.env.NODE_ENV as any) || 'development',
        
        // ACCIONES DE THEME
        setTheme: (theme: AppTheme) => {
          set((state) => {
            state.theme = theme;
            state.isDarkMode = calculateIsDarkMode(theme);
            
            // Aplicar theme al DOM
            if (typeof window !== 'undefined') {
              const root = window.document.documentElement;
              if (state.isDarkMode) {
                root.classList.add('dark');
              } else {
                root.classList.remove('dark');
              }
            }
          });
        },
        
        toggleTheme: () => {
          const currentTheme = get().theme;
          const newTheme: AppTheme = currentTheme === 'light' ? 'dark' : 'light';
          get().setTheme(newTheme);
        },
        
        // ACCIONES DE UI
        setSidebarOpen: (open: boolean) => {
          set((state) => {
            state.sidebarOpen = open;
          });
        },
        
        toggleSidebar: () => {
          set((state) => {
            state.sidebarOpen = !state.sidebarOpen;
          });
        },
        
        setSidebarCollapsed: (collapsed: boolean) => {
          set((state) => {
            state.sidebarCollapsed = collapsed;
          });
        },
        
        // ACCIONES DE LOADING
        setAppLoading: (loading: boolean) => {
          set((state) => {
            state.isAppLoading = loading;
          });
        },
        
        setPageTransitioning: (transitioning: boolean) => {
          set((state) => {
            state.isPageTransitioning = transitioning;
          });
        },
        
        // ACCIONES DE MODAL
        openModal: (modalId: string, data?: any) => {
          set((state) => {
            state.activeModal = modalId;
            state.modalData = data || null;
          });
        },
        
        closeModal: () => {
          set((state) => {
            state.activeModal = null;
            state.modalData = null;
          });
        },
        
        // ACCIONES DE NOTIFICACIONES
        addNotification: (notification) => {
          set((state) => {
            const newNotification: NotificationItem = {
              ...notification,
              id: `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
              timestamp: new Date().toISOString(),
              isRead: false
            };
            
            state.notifications.unshift(newNotification);
            
            // Limitar a máximo 50 notificaciones
            if (state.notifications.length > 50) {
              state.notifications = state.notifications.slice(0, 50);
            }
            
            // Auto-remover notificaciones con autoClose
            if (newNotification.autoClose && newNotification.duration) {
              setTimeout(() => {
                get().removeNotification(newNotification.id);
              }, newNotification.duration);
            }
          });
        },
        
        removeNotification: (id: string) => {
          set((state) => {
            state.notifications = state.notifications.filter(n => n.id !== id);
          });
        },
        
        markNotificationAsRead: (id: string) => {
          set((state) => {
            const notification = state.notifications.find(n => n.id === id);
            if (notification) {
              notification.isRead = true;
            }
          });
        },
        
        clearAllNotifications: () => {
          set((state) => {
            state.notifications = [];
          });
        },
        
        // ACCIONES DE ALERTS
        showAlert: (alert) => {
          set((state) => {
            const newAlert: AlertItem = {
              ...alert,
              id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
              isVisible: true
            };
            
            state.alerts.push(newAlert);
          });
        },
        
        hideAlert: (id: string) => {
          set((state) => {
            const alert = state.alerts.find(a => a.id === id);
            if (alert) {
              alert.isVisible = false;
            }
          });
        },
        
        clearAllAlerts: () => {
          set((state) => {
            state.alerts = [];
          });
        },
        
        // ACCIONES DE CONFIGURACIÓN
        updateConfig: (configUpdate) => {
          set((state) => {
            state.config = { ...state.config, ...configUpdate };
          });
        },
        
        updateLanguage: (language: Language) => {
          set((state) => {
            state.config.language = language;
          });
        },
        
        updateCurrency: (currency: Currency) => {
          set((state) => {
            state.config.currency = currency;
          });
        },
        
        // ACCIONES DE UTILIDAD
        resetAppState: () => {
          set((state) => {
            // Reset solo UI state, mantener configuración
            state.sidebarOpen = true;
            state.sidebarCollapsed = false;
            state.isAppLoading = false;
            state.isPageTransitioning = false;
            state.activeModal = null;
            state.modalData = null;
            state.notifications = [];
            state.alerts = [];
          });
        },
        
        updatePerformanceMetrics: (metrics) => {
          set((state) => {
            state.performance = { ...state.performance, ...metrics };
            state.performance.lastUpdate = new Date().toISOString();
          });
        }
      })),
      {
        name: 'mestore-app-state',
        // Persistir solo configuración y theme, no UI state temporal
        partialize: (state) => ({
          theme: state.theme,
          config: state.config,
          sidebarCollapsed: state.sidebarCollapsed
        })
      }
    ),
    {
      name: 'AppStore'
    }
  )
);

// Selectores útiles
export const appSelectors = {
  // Selectores de theme
  theme: (state: AppStoreType) => state.theme,
  isDarkMode: (state: AppStoreType) => state.isDarkMode,
  
  // Selectores de UI
  sidebarState: (state: AppStoreType) => ({
    isOpen: state.sidebarOpen,
    isCollapsed: state.sidebarCollapsed
  }),
  
  loadingState: (state: AppStoreType) => ({
    isAppLoading: state.isAppLoading,
    isPageTransitioning: state.isPageTransitioning
  }),
  
  modalState: (state: AppStoreType) => ({
    activeModal: state.activeModal,
    modalData: state.modalData
  }),
  
  // Selectores de notificaciones
  unreadNotifications: (state: AppStoreType) => state.notifications.filter(n => !n.isRead),
  notificationCount: (state: AppStoreType) => state.notifications.filter(n => !n.isRead).length,
  visibleAlerts: (state: AppStoreType) => state.alerts.filter(a => a.isVisible),
  
  // Selectores de configuración
  language: (state: AppStoreType) => state.config.language,
  currency: (state: AppStoreType) => state.config.currency,
  apiConfig: (state: AppStoreType) => state.config.api
};