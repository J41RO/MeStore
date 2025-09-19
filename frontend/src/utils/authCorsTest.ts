import { apiClient } from '../services/apiClient';
import { handleCorsError } from './corsErrorHandler';

export interface AuthCorsTestResult {
  success: boolean;
  message: string;
  tests: {
    loginEndpoint: boolean;
    refreshEndpoint: boolean;
    logoutEndpoint: boolean;
    preflightRequest: boolean;
    credentialsSupport: boolean;
  };
  errors: string[];
  suggestions: string[];
}

/**
 * Test específico para verificar que los endpoints de autenticación funcionan con CORS
 */
export const runAuthCorsTest = async (): Promise<AuthCorsTestResult> => {
  const result: AuthCorsTestResult = {
    success: false,
    message: '',
    tests: {
      loginEndpoint: false,
      refreshEndpoint: false,
      logoutEndpoint: false,
      preflightRequest: false,
      credentialsSupport: false,
    },
    errors: [],
    suggestions: [],
  };

  console.log('🔐 Iniciando test CORS para autenticación...');

  try {
    // Test 1: Login endpoint availability
    console.log('📝 Probando endpoint de login...');
    try {
      await apiClient.post('/api/auth/login', {
        email: 'test@example.com',
        password: 'testpassword'
      });
    } catch (error: any) {
      const status = error.response?.status;
      if (status === 422 || status === 400 || status === 401) {
        // Estos códigos indican que el endpoint está disponible
        result.tests.loginEndpoint = true;
        console.log('✅ Endpoint de login disponible');
      } else if (!error.response) {
        const corsInfo = handleCorsError(error, 'Login Endpoint');
        result.errors.push(`Login endpoint CORS error: ${corsInfo.userMessage}`);
        result.suggestions.push(...corsInfo.suggestedActions);
      } else {
        result.errors.push(`Login endpoint unexpected error: ${status}`);
      }
    }

    // Test 2: Refresh endpoint availability
    console.log('🔄 Probando endpoint de refresh...');
    try {
      await apiClient.post('/api/auth/refresh', {
        refresh_token: 'invalid_token'
      });
    } catch (error: any) {
      const status = error.response?.status;
      if (status === 422 || status === 400 || status === 401) {
        result.tests.refreshEndpoint = true;
        console.log('✅ Endpoint de refresh disponible');
      } else if (!error.response) {
        const corsInfo = handleCorsError(error, 'Refresh Endpoint');
        result.errors.push(`Refresh endpoint CORS error: ${corsInfo.userMessage}`);
        result.suggestions.push(...corsInfo.suggestedActions);
      } else {
        result.errors.push(`Refresh endpoint unexpected error: ${status}`);
      }
    }

    // Test 3: Logout endpoint availability
    console.log('🚪 Probando endpoint de logout...');
    try {
      await apiClient.post('/api/auth/logout');
    } catch (error: any) {
      const status = error.response?.status;
      if (status === 401 || status === 422) {
        // 401 es esperado sin token válido
        result.tests.logoutEndpoint = true;
        console.log('✅ Endpoint de logout disponible');
      } else if (!error.response) {
        const corsInfo = handleCorsError(error, 'Logout Endpoint');
        result.errors.push(`Logout endpoint CORS error: ${corsInfo.userMessage}`);
        result.suggestions.push(...corsInfo.suggestedActions);
      } else {
        result.errors.push(`Logout endpoint unexpected error: ${status}`);
      }
    }

    // Test 4: Preflight request (OPTIONS)
    console.log('✈️ Probando preflight request...');
    try {
      // Simular un preflight request manualmente
      const preflightResponse = await fetch(
        `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/auth/login`,
        {
          method: 'OPTIONS',
          headers: {
            'Origin': window.location.origin,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization',
          },
        }
      );

      if (preflightResponse.ok || preflightResponse.status === 204) {
        result.tests.preflightRequest = true;
        console.log('✅ Preflight request exitoso');

        // Verificar headers CORS en la respuesta
        const corsOrigin = preflightResponse.headers.get('Access-Control-Allow-Origin');
        const corsCredentials = preflightResponse.headers.get('Access-Control-Allow-Credentials');

        if (corsCredentials === 'true') {
          result.tests.credentialsSupport = true;
          console.log('✅ Soporte para credenciales habilitado');
        } else {
          result.suggestions.push('Verificar que CORS_ALLOW_CREDENTIALS esté habilitado en el backend');
        }

        console.log('CORS Headers en preflight:', {
          origin: corsOrigin,
          credentials: corsCredentials,
          methods: preflightResponse.headers.get('Access-Control-Allow-Methods'),
          headers: preflightResponse.headers.get('Access-Control-Allow-Headers'),
        });
      } else {
        result.errors.push(`Preflight request failed: ${preflightResponse.status}`);
      }
    } catch (error: any) {
      const corsInfo = handleCorsError(error, 'Preflight Request');
      result.errors.push(`Preflight request error: ${corsInfo.userMessage}`);
      result.suggestions.push(...corsInfo.suggestedActions);
    }

    // Determinar resultado general
    const passedTests = Object.values(result.tests).filter(Boolean).length;
    const totalTests = Object.keys(result.tests).length;

    if (passedTests === totalTests) {
      result.success = true;
      result.message = 'Todos los tests de autenticación CORS pasaron exitosamente';
    } else if (passedTests >= 3) {
      result.success = true;
      result.message = `${passedTests}/${totalTests} tests pasaron - Funcionalidad básica disponible`;
    } else {
      result.message = `${passedTests}/${totalTests} tests pasaron - Problemas significativos con CORS`;
      result.suggestions.push(
        'Verificar configuración CORS en el backend',
        'Confirmar que el frontend esté en CORS_ORIGINS',
        'Revisar que CORS_ALLOW_CREDENTIALS esté habilitado'
      );
    }

    console.log(`🎯 Test completado: ${passedTests}/${totalTests} tests pasaron`);

  } catch (error: any) {
    result.message = 'Error general durante el test de autenticación CORS';
    result.errors.push(error.message || 'Unknown error');
    console.error('💥 Error general durante el test', error);
  }

  return result;
};

/**
 * Test simple para verificar si los endpoints básicos de auth están disponibles
 */
export const quickAuthTest = async (): Promise<boolean> => {
  try {
    // Intentar hacer login con datos inválidos - debería retornar 422, no error CORS
    await apiClient.post('/api/auth/login', { email: '', password: '' });
    return true;
  } catch (error: any) {
    // 422 (validation error) significa que el endpoint está disponible
    if (error.response?.status === 422) {
      return true;
    }
    // Cualquier otro error con response también indica disponibilidad
    if (error.response) {
      return true;
    }
    // Error sin response indica problema CORS o de red
    return false;
  }
};

/**
 * Muestra un reporte detallado del test de autenticación CORS
 */
export const logAuthCorsReport = (result: AuthCorsTestResult) => {
  console.group('🔐 Reporte de Autenticación CORS');

  console.log(`Estado: ${result.success ? '✅ EXITOSO' : '❌ FALLIDO'}`);
  console.log(`Mensaje: ${result.message}`);

  console.group('📋 Tests Individuales');
  console.log(`Login Endpoint: ${result.tests.loginEndpoint ? '✅' : '❌'}`);
  console.log(`Refresh Endpoint: ${result.tests.refreshEndpoint ? '✅' : '❌'}`);
  console.log(`Logout Endpoint: ${result.tests.logoutEndpoint ? '✅' : '❌'}`);
  console.log(`Preflight Request: ${result.tests.preflightRequest ? '✅' : '❌'}`);
  console.log(`Credentials Support: ${result.tests.credentialsSupport ? '✅' : '❌'}`);
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