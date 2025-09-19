import React, { useState, useEffect } from 'react';
import {
  runCorsConnectivityTest,
  logConnectivityReport,
  ConnectivityTestResult,
  quickConnectivityTest
} from '../../utils/corsConnectivityTest';
import {
  runAuthCorsTest,
  logAuthCorsReport,
  AuthCorsTestResult,
  quickAuthTest
} from '../../utils/authCorsTest';

interface CorsDebugPanelProps {
  showInProduction?: boolean;
  autoTest?: boolean;
}

export const CorsDebugPanel: React.FC<CorsDebugPanelProps> = ({
  showInProduction = false,
  autoTest = true
}) => {
  const [testResult, setTestResult] = useState<ConnectivityTestResult | null>(null);
  const [authTestResult, setAuthTestResult] = useState<AuthCorsTestResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const [quickStatus, setQuickStatus] = useState<boolean | null>(null);
  const [quickAuthStatus, setQuickAuthStatus] = useState<boolean | null>(null);

  const isDevelopment = import.meta.env.MODE === 'development';
  const shouldShow = isDevelopment || showInProduction;

  useEffect(() => {
    if (autoTest && shouldShow) {
      runQuickTest();
    }
  }, [autoTest, shouldShow]);

  const runQuickTest = async () => {
    const result = await quickConnectivityTest();
    setQuickStatus(result);

    const authResult = await quickAuthTest();
    setQuickAuthStatus(authResult);
  };

  const runFullTest = async () => {
    setIsRunning(true);
    try {
      console.log('🔍 Ejecutando test completo CORS...');
      const result = await runCorsConnectivityTest();
      setTestResult(result);
      logConnectivityReport(result);

      console.log('🔐 Ejecutando test de autenticación...');
      const authResult = await runAuthCorsTest();
      setAuthTestResult(authResult);
      logAuthCorsReport(authResult);
    } catch (error) {
      console.error('Error running CORS test:', error);
    } finally {
      setIsRunning(false);
    }
  };

  if (!shouldShow) {
    return null;
  }

  const getStatusIcon = (status: boolean) => status ? '✅' : '❌';
  const getQuickStatusColor = () => {
    if (quickStatus === null) return 'text-gray-500';
    return quickStatus ? 'text-green-600' : 'text-red-600';
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Toggle Button */}
      <button
        onClick={() => setIsVisible(!isVisible)}
        className={`mb-2 px-3 py-2 rounded-lg shadow-lg font-medium text-sm transition-all duration-200 ${
          quickStatus === null
            ? 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            : quickStatus
              ? 'bg-green-100 text-green-700 hover:bg-green-200'
              : 'bg-red-100 text-red-700 hover:bg-red-200'
        }`}
      >
        <span className={getQuickStatusColor()}>
          {quickStatus === null ? '🔍' : getStatusIcon(quickStatus)} API
        </span>
      </button>

      {/* Debug Panel */}
      {isVisible && (
        <div className="bg-white border border-gray-200 rounded-lg shadow-xl p-4 w-80 max-h-96 overflow-y-auto">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-800">CORS Debug Panel</h3>
            <button
              onClick={() => setIsVisible(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          {/* Quick Status */}
          <div className="mb-4 p-2 bg-gray-50 rounded space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>API General:</span>
              <span className={getQuickStatusColor()}>
                {quickStatus === null ? 'Probando...' : quickStatus ? 'Conectado' : 'Desconectado'}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>Autenticación:</span>
              <span className={quickAuthStatus === null ? 'text-gray-500' : quickAuthStatus ? 'text-green-600' : 'text-red-600'}>
                {quickAuthStatus === null ? 'Probando...' : quickAuthStatus ? 'Disponible' : 'No disponible'}
              </span>
            </div>
            <button
              onClick={runQuickTest}
              className="mt-1 text-xs text-blue-600 hover:text-blue-800"
            >
              Actualizar
            </button>
          </div>

          {/* Full Test */}
          <div className="space-y-3">
            <button
              onClick={runFullTest}
              disabled={isRunning}
              className="w-full px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-blue-300 text-sm"
            >
              {isRunning ? 'Ejecutando test...' : 'Test completo CORS'}
            </button>

            {/* Test Results */}
            {testResult && (
              <div className="space-y-2 text-sm">
                <div className="font-medium text-gray-800 flex items-center">
                  {getStatusIcon(testResult.success)}
                  <span className="ml-2">{testResult.message}</span>
                </div>

                <div className="text-xs text-gray-600">
                  Tiempo: {testResult.details.responseTime}ms
                </div>

                {/* Details */}
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span>Health Check:</span>
                    <span>{getStatusIcon(testResult.details.healthCheck)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>CORS Headers:</span>
                    <span>{getStatusIcon(testResult.details.corsWorking)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Backend:</span>
                    <span>{getStatusIcon(testResult.details.backendReachable)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Auth Endpoint:</span>
                    <span>{getStatusIcon(testResult.details.authEndpointAvailable)}</span>
                  </div>
                </div>

                {/* Errors */}
                {testResult.errors.length > 0 && (
                  <div className="mt-3 p-2 bg-red-50 rounded text-xs">
                    <div className="font-medium text-red-700 mb-1">Errores:</div>
                    {testResult.errors.map((error, index) => (
                      <div key={index} className="text-red-600">{error}</div>
                    ))}
                  </div>
                )}

                {/* Suggestions */}
                {testResult.suggestions.length > 0 && (
                  <div className="mt-3 p-2 bg-yellow-50 rounded text-xs">
                    <div className="font-medium text-yellow-700 mb-1">Sugerencias:</div>
                    {testResult.suggestions.slice(0, 3).map((suggestion, index) => (
                      <div key={index} className="text-yellow-600">
                        {index + 1}. {suggestion}
                      </div>
                    ))}
                    {testResult.suggestions.length > 3 && (
                      <div className="text-yellow-500 mt-1">
                        +{testResult.suggestions.length - 3} más en consola
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Auth Test Results */}
            {authTestResult && (
              <div className="space-y-2 text-sm border-t pt-3">
                <div className="font-medium text-gray-800 flex items-center">
                  {getStatusIcon(authTestResult.success)}
                  <span className="ml-2">Autenticación: {authTestResult.message}</span>
                </div>

                {/* Auth Test Details */}
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span>Login:</span>
                    <span>{getStatusIcon(authTestResult.tests.loginEndpoint)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Refresh:</span>
                    <span>{getStatusIcon(authTestResult.tests.refreshEndpoint)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Logout:</span>
                    <span>{getStatusIcon(authTestResult.tests.logoutEndpoint)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Preflight:</span>
                    <span>{getStatusIcon(authTestResult.tests.preflightRequest)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Credentials:</span>
                    <span>{getStatusIcon(authTestResult.tests.credentialsSupport)}</span>
                  </div>
                </div>

                {/* Auth Errors */}
                {authTestResult.errors.length > 0 && (
                  <div className="mt-2 p-2 bg-red-50 rounded text-xs">
                    <div className="font-medium text-red-700 mb-1">Errores Auth:</div>
                    {authTestResult.errors.slice(0, 2).map((error, index) => (
                      <div key={index} className="text-red-600">{error}</div>
                    ))}
                    {authTestResult.errors.length > 2 && (
                      <div className="text-red-500 mt-1">
                        +{authTestResult.errors.length - 2} más en consola
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Development Info */}
            {isDevelopment && (
              <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-500">
                <div>Entorno: {import.meta.env.MODE}</div>
                <div>API URL: {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}</div>
                <div>Consola: F12 para más detalles</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CorsDebugPanel;