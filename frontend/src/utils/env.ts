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
  // En entorno de test, usar valores mock
  if (import.meta && import.meta.env && import.meta.env.MODE === 'test') {
    const testValues: Record<string, string> = {
      VITE_API_BASE_URL: 'http://localhost:8000/api/v1',
      VITE_BUILD_NUMBER: '1',
      MODE: 'test',
    };
    return testValues[key] || defaultValue;
  }

  // En Vite, usar import.meta.env
  if (import.meta && import.meta.env) {
    return (import.meta.env as any)[key] || defaultValue;
  }

  // Fallback a valores por defecto
  return defaultValue;
};

// Variables de entorno específicas con valores seguros
export const ENV = {
  API_BASE_URL: getEnvVar('VITE_API_BASE_URL', 'http://192.168.1.137:8000/api/v1'),
  BUILD_NUMBER: getEnvVar('VITE_BUILD_NUMBER', '1'),
  MODE: getEnvVar('MODE', 'development') as
    | 'development'
    | 'production'
    | 'staging',
};
