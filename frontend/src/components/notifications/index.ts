// Exportaciones unificadas del sistema de notificaciones
export { Toast } from './Toast';
export { ToastContainer } from './ToastContainer';

// Re-exportar desde contexts para conveniencia
export { NotificationProvider, useNotifications } from '../../contexts/NotificationContext';

// Tipos útiles para componentes que usen notificaciones
export type { NotificationItem, AlertItem } from '../../types/app.types';