// ~/frontend/src/utils/env.ts
// ---------------------------------------------------------------------------------------------
// MESTOCKER - Environment Variables Helper
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------

/**
 * Helper para manejo seguro de variables de entorno
 * Compatible con Jest y Vite
 */

// Función para obtener variables de entorno de forma segura
export const getEnvVar = (key: string, defaultValue: string = ''): string => {
  // Check if running in Jest test environment
  if (typeof global !== 'undefined' && global.importMetaMock) {
    const testValues = global.importMetaMock.env;
    return testValues[key] || defaultValue;
  }

  // Check for Node.js test environment (Jest)
  if (typeof process !== 'undefined' && process.env.NODE_ENV === 'test') {
    const testValues: Record<string, string> = {
      VITE_API_BASE_URL: 'http://localhost:8000',
      VITE_BUILD_NUMBER: '1',
      MODE: 'test',
    };
    return testValues[key] || defaultValue;
  }

  // In browser environment, try to access Vite environment variables
  try {
    // Use window object for environment variables in browser
    if (typeof window !== 'undefined') {
      const env = (window as any).__VITE_ENV__ || {};
      return env[key] || defaultValue;
    }
  } catch (error) {
    // Fallback if window access fails
  }

  // Fallback a valores por defecto
  return defaultValue;
};

// Variables de entorno específicas con valores seguros
export const ENV = {
  API_BASE_URL: getEnvVar('VITE_API_BASE_URL', 'http://192.168.1.137:8000'),
  BUILD_NUMBER: getEnvVar('VITE_BUILD_NUMBER', '1'),
  MODE: getEnvVar('MODE', 'development') as
    | 'development'
    | 'production'
    | 'staging',
};
