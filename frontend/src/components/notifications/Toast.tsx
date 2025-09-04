import * as React from 'react';
import { useEffect, useState } from 'react';
import { NotificationItem } from '../../types/app.types';

interface ToastProps {
  notification: NotificationItem;
  onRemove: (id: string) => void;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
}

export const Toast: React.FC<ToastProps> = ({
  notification,
  onRemove,
  position = 'top-right',
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    // Animación de entrada
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    // Auto-remove después de 5 segundos para success/info
    if (notification.type === 'success' || notification.type === 'info') {
      const timer = setTimeout(() => handleRemove(), 5000);
      return () => clearTimeout(timer);
    }
    // Retorno explícito para satisfacer TypeScript
    return () => {};
  }, [notification.type]);

  const handleRemove = () => {
    setIsExiting(true);
    setTimeout(() => onRemove(notification.id), 300);
  };

  const getToastStyles = () => {
    const baseStyles =
      'fixed z-50 p-4 rounded-lg shadow-lg transition-all duration-300 ease-in-out max-w-sm';
    const positionStyles = {
      'top-right': 'top-4 right-4',
      'top-left': 'top-4 left-4',
      'bottom-right': 'bottom-4 right-4',
      'bottom-left': 'bottom-4 left-4',
    };

    const typeStyles = {
      success: 'bg-green-500 text-white',
      error: 'bg-red-500 text-white',
      warning: 'bg-yellow-500 text-black',
      info: 'bg-blue-500 text-white',
    };

    const visibilityStyles = isExiting
      ? 'opacity-0 translate-x-full scale-95'
      : isVisible
        ? 'opacity-100 translate-x-0 scale-100'
        : 'opacity-0 translate-x-full scale-95';

    return `${baseStyles} ${positionStyles[position]} ${typeStyles[notification.type]} ${visibilityStyles}`;
  };

  return (
    <div className={getToastStyles()}>
      <div className='flex items-start justify-between'>
        <div className='flex-1'>
          <h4 className='font-semibold text-sm'>{notification.title}</h4>
          <p className='text-sm mt-1 opacity-90'>{notification.message}</p>
        </div>
        <button
          onClick={handleRemove}
          className='ml-3 text-white hover:text-gray-200 focus:outline-none'
          aria-label='Cerrar notificación'
        >
          <svg className='w-4 h-4' fill='currentColor' viewBox='0 0 20 20'>
            <path
              fillRule='evenodd'
              d='M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z'
              clipRule='evenodd'
            />
          </svg>
        </button>
      </div>
    </div>
  );
};
