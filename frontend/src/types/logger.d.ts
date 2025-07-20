/**
 * Tipos para el sistema de logging frontend
 */

declare global {
  interface Window {
    __MESTORE_LOGGER__?: {
      debug: (message: string, data?: any) => void;
      info: (message: string, data?: any) => void;
      warn: (message: string, data?: any) => void;
      error: (message: string, data?: any) => void;
    };
  }
}

export {};