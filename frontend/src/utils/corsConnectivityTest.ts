import { apiClient } from '../services/apiClient';
import { handleCorsError } from './corsErrorHandler';

export interface ConnectivityTestResult {
  success: boolean;
  message: string;
  details: {
    healthCheck: boolean;
    corsWorking: boolean;
    backendReachable: boolean;
    authEndpointAvailable: boolean;
    responseTime: number;
  };
  errors: string[];
  suggestions: string[];
}

/**
 * Ejecuta una serie de pruebas para verificar la conectividad CORS
 */
export const runCorsConnectivityTest = async (): Promise<ConnectivityTestResult> => {
  const result: ConnectivityTestResult = {
    success: false,
    message: '',
    details: {
      healthCheck: false,
      corsWorking: false,
      backendReachable: false,
      authEndpointAvailable: false,
      responseTime: 0,
    },
    errors: [],
    suggestions: [],
  };

  const startTime = Date.now();

  try {
    console.log('🔍 Iniciando test de conectividad CORS...');

    // Test 1: Health check básico
    try {
      console.log('⚡ Probando health check...');
      const healthResponse = await apiClient.get('/health');
      result.details.healthCheck = healthResponse.status === 200;
      result.details.backendReachable = true;
      console.log('✅ Health check exitoso');
    } catch (error: any) {
      console.log('❌ Health check falló');
      const corsInfo = handleCorsError(error, 'Health Check');
      result.errors.push(`Health check failed: ${corsInfo.userMessage}`);
      result.suggestions.push(...corsInfo.suggestedActions);
    }

    // Test 2: Endpoint de autenticación (sin credenciales)
    try {
      console.log('🔐 Probando endpoint de autenticación...');
      // Intentar acceder al endpoint de login (debería retornar 422 por falta de datos, no CORS error)
      await apiClient.post('/api/auth/login', {});
    } catch (error: any) {
      const status = error.response?.status;
      if (status === 422 || status === 400) {
        // Esperado - el endpoint está disponible pero rechaza datos inválidos
        result.details.authEndpointAvailable = true;
        console.log('✅ Endpoint de autenticación disponible (error 422 esperado)');
      } else if (!error.response) {
        // Error CORS o de red
        const corsInfo = handleCorsError(error, 'Auth Endpoint Test');
        result.errors.push(`Auth endpoint failed: ${corsInfo.userMessage}`);
        result.suggestions.push(...corsInfo.suggestedActions);
        console.log('❌ Error CORS en endpoint de autenticación');
      } else {
        result.details.authEndpointAvailable = true;
        console.log(`✅ Endpoint de autenticación disponible (HTTP ${status})`);
      }
    }

    // Test 3: Verificar headers CORS en una respuesta exitosa
    try {
      console.log('📋 Verificando headers CORS...');
      const response = await apiClient.get('/health');
      const corsHeaders = {
        'access-control-allow-origin': response.headers['access-control-allow-origin'],
        'access-control-allow-credentials': response.headers['access-control-allow-credentials'],
        'access-control-allow-methods': response.headers['access-control-allow-methods'],
        'access-control-allow-headers': response.headers['access-control-allow-headers'],
      };

      console.log('CORS Headers received:', corsHeaders);

      if (corsHeaders['access-control-allow-origin']) {
        result.details.corsWorking = true;
        console.log('✅ Headers CORS encontrados');
      } else {
        result.errors.push('CORS headers not found in response');
        result.suggestions.push('Verificar configuración CORS en el middleware del backend');
        console.log('⚠️ Headers CORS no encontrados');
      }
    } catch (error: any) {
      console.log('❌ Error verificando headers CORS');
    }

    result.details.responseTime = Date.now() - startTime;

    // Determinar resultado general
    if (result.details.healthCheck && result.details.corsWorking) {
      result.success = true;
      result.message = 'Conectividad CORS funcionando correctamente';
      console.log('🎉 Test de conectividad exitoso');
    } else if (result.details.backendReachable) {
      result.message = 'Backend alcanzable pero problemas con CORS';
      result.suggestions.push(
        'Verificar configuración CORS en app/core/config.py',
        'Confirmar que el origen del frontend esté en CORS_ORIGINS'
      );
      console.log('⚠️ Backend alcanzable pero problemas con CORS');
    } else {
      result.message = 'No se puede conectar al backend';
      result.suggestions.push(
        'Verificar que el backend esté ejecutándose en el puerto correcto',
        'Confirmar la URL base de la API en la configuración del frontend',
        'Revisar logs del backend para errores'
      );
      console.log('❌ No se puede conectar al backend');
    }

  } catch (error: any) {
    result.message = 'Error general durante el test de conectividad';
    result.errors.push(error.message || 'Unknown error');
    console.log('💥 Error general durante el test');
  }

  return result;
};

/**
 * Test rápido solo para verificar si el backend está disponible
 */
export const quickConnectivityTest = async (): Promise<boolean> => {
  try {
    const response = await apiClient.get('/health', { timeout: 3000 });
    return response.status === 200;
  } catch {
    return false;
  }
};

/**
 * Muestra un reporte detallado del test de conectividad en la consola
 */
export const logConnectivityReport = (result: ConnectivityTestResult) => {
  console.group('📊 Reporte de Conectividad CORS');

  console.log(`Estado general: ${result.success ? '✅ EXITOSO' : '❌ FALLIDO'}`);
  console.log(`Mensaje: ${result.message}`);
  console.log(`Tiempo de respuesta: ${result.details.responseTime}ms`);

  console.group('📋 Detalles');
  console.log(`Health Check: ${result.details.healthCheck ? '✅' : '❌'}`);
  console.log(`CORS Working: ${result.details.corsWorking ? '✅' : '❌'}`);
  console.log(`Backend Reachable: ${result.details.backendReachable ? '✅' : '❌'}`);
  console.log(`Auth Endpoint: ${result.details.authEndpointAvailable ? '✅' : '❌'}`);
  console.groupEnd();

  if (result.errors.length > 0) {
    console.group('❌ Errores');
    result.errors.forEach(error => console.error(error));
    console.groupEnd();
  }

  if (result.suggestions.length > 0) {
    console.group('💡 Sugerencias');
    result.suggestions.forEach((suggestion, index) => {
      console.warn(`${index + 1}. ${suggestion}`);
    });
    console.groupEnd();
  }

  console.groupEnd();
};