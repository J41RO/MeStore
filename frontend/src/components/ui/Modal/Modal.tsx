import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { ModalProps } from './Modal.types';

const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  size = 'md',
  closeOnOverlayClick = true,
  closeOnEscape = true,
  children,
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  const sizeClasses = {
    sm: 'w-full sm:w-96 md:max-w-md',
    md: 'w-full sm:w-96 md:w-[32rem] lg:max-w-lg',
    lg: 'w-full sm:w-96 md:w-[32rem] lg:w-[40rem] xl:max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-4',
  };

  // Handle escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (closeOnEscape && event.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Store previous focus
      previousFocusRef.current = document.activeElement as HTMLElement;
      // Focus modal
      modalRef.current?.focus();
      // Prevent body scroll
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      // Restore body scroll
      document.body.style.overflow = 'unset';
      // Restore previous focus
      if (previousFocusRef.current) {
        previousFocusRef.current.focus();
      }
    };
  }, [isOpen, closeOnEscape, onClose]);

  const handleOverlayClick = (event: React.MouseEvent) => {
    if (closeOnOverlayClick && event.target === event.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  const modalContent = (
    <div
      className='fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 md:p-8'
      onClick={handleOverlayClick}
    >
      {/* Backdrop */}
      <div className='absolute inset-0 bg-black bg-opacity-50 transition-opacity' />

      {/* Modal */}
      <div
        ref={modalRef}
        className={`relative bg-white rounded sm:rounded-lg shadow-mestocker-xl w-full ${sizeClasses[size]} max-h-[90vh] overflow-hidden`}
        tabIndex={-1}
        role='dialog'
        aria-modal='true'
        aria-labelledby={title ? 'modal-title' : undefined}
      >
        {/* Header */}
        {title && (
          <div className='flex items-center justify-between p-4 sm:p-6 border-b border-neutral-200'>
            <h2
              id='modal-title'
              className='text-base sm:text-lg font-semibold text-neutral-900'
            >
              {title}
            </h2>
            <button
              onClick={onClose}
              className='p-1 rounded-md hover:bg-neutral-100 focus:outline-none focus:ring-2 focus:ring-primary-500'
              aria-label='Cerrar modal'
            >
              <svg
                className='w-5 h-5'
                fill='none'
                stroke='currentColor'
                viewBox='0 0 24 24'
              >
                <path
                  strokeLinecap='round'
                  strokeLinejoin='round'
                  strokeWidth={2}
                  d='M6 18L18 6M6 6l12 12'
                />
              </svg>
            </button>
          </div>
        )}

        {/* Content */}
        <div className='overflow-y-auto max-h-[calc(90vh-8rem)]'>
          {children}
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};

export default Modal;
