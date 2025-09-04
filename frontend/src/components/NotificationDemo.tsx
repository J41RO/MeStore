import * as React from 'react';
import { useNotifications } from '../contexts/NotificationContext';

export const NotificationDemo: React.FC = () => {
  const { showNotification } = useNotifications();

  const handleTestNotification = () => {
    showNotification({
      type: 'success',
      title: 'Test Success',
      message: 'Esta es una notificación de prueba exitosa',
    });
  };

  const handleErrorNotification = () => {
    showNotification({
      type: 'error',
      title: 'Test Error',
      message: 'Esta es una notificación de error de prueba',
    });
  };

  const handleWarningNotification = () => {
    showNotification({
      type: 'warning',
      title: 'Test Warning',
      message: 'Esta es una notificación de advertencia de prueba',
    });
  };

  const handleInfoNotification = () => {
    showNotification({
      type: 'info',
      title: 'Test Info',
      message: 'Esta es una notificación informativa de prueba',
    });
  };

  return (
    <div className='p-4 space-y-4'>
      <h2 className='text-xl font-bold'>Demo de Notificaciones</h2>

      <div className='flex gap-2 flex-wrap'>
        <button
          onClick={handleTestNotification}
          className='px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600'
        >
          Success Toast
        </button>

        <button
          onClick={handleErrorNotification}
          className='px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600'
        >
          Error Toast
        </button>

        <button
          onClick={handleWarningNotification}
          className='px-4 py-2 bg-yellow-500 text-black rounded hover:bg-yellow-600'
        >
          Warning Toast
        </button>

        <button
          onClick={handleInfoNotification}
          className='px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600'
        >
          Info Toast
        </button>
      </div>
    </div>
  );
};
