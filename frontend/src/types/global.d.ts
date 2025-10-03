/**
 * Global type definitions for the application
 */

import { ToastType } from '../components/common/Toast';

declare global {
  interface Window {
    /**
     * Global toast notification function
     * Available after ToastProvider is mounted
     */
    showToast?: (message: string, type: ToastType, duration?: number) => void;
  }
}

export {};
