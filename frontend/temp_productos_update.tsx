// Actualización específica para funciones de BulkActions
import { useNotifications } from '../contexts/NotificationContext';

// Dentro del componente, agregar el hook de notificaciones:
const { addNotification } = useNotifications();

// Función para mostrar notificaciones
const showNotification = (message: string, type: 'success' | 'error') => {
  addNotification({
    id: Date.now().toString(),
    message,
    type: type === 'success' ? 'success' : 'error',
    duration: 5000,
  });
};

// Función para manejar completación de operaciones bulk
const handleBulkComplete = () => {
  refreshProducts();
};
