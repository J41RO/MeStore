import React, { useEffect } from 'react'
import logger from './utils/logger'
import './App.css'

function App() {
  useEffect(() => {
    // Inicializar logger al cargar la app
    logger.info('App initialized', { 
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href 
    });

    // Ejemplo de logging de eventos
    logger.debug('App useEffect executed');
    
    // Simular algunos logs para demostrar funcionalidad
    setTimeout(() => {
      logger.warn('Example warning log', { component: 'App' });
    }, 2000);

    setTimeout(() => {
      logger.logEvent('app_fully_loaded', { loadTime: '2s' });
    }, 3000);

  }, []);

  const handleTestError = () => {
    // Función para probar captura de errores
    logger.error('Manual error test', { 
      type: 'user_triggered',
      component: 'App' 
    });
    
    // Simular error no manejado (opcional - para testing)
    // throw new Error('Test error for global handler');
  };

  const handleTestLogs = () => {
    logger.debug('Debug message from button');
    logger.info('Info message from button');
    logger.warn('Warning message from button');
    logger.error('Error message from button');
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>MeStore - Frontend Logger System</h1>
        
        <div style={{ margin: '20px' }}>
          <h2>🚀 Sistema de Logging Activo</h2>
          
          <div style={{ margin: '10px' }}>
            <button onClick={handleTestLogs} style={{ margin: '5px', padding: '10px' }}>
              🧪 Test All Log Levels
            </button>
            
            <button onClick={handleTestError} style={{ margin: '5px', padding: '10px' }}>
              ❌ Test Error Logging
            </button>
          </div>
          
          <div style={{ textAlign: 'left', maxWidth: '600px', margin: '20px auto' }}>
            <h3>📋 Características del Logger:</h3>
            <ul>
              <li>✅ Logs enriquecidos en consola (desarrollo)</li>
              <li>✅ Envío remoto opcional (producción)</li>
              <li>✅ Captura automática de errores JS no manejados</li>
              <li>✅ Captura de promesas rechazadas</li>
              <li>✅ Captura de errores de recursos (imágenes, scripts)</li>
              <li>✅ Context del usuario (ID, sesión, URL, timestamp)</li>
              <li>✅ Sistema de filtrado por level (debug/info/warn/error)</li>
              <li>✅ Cola de envío con retry automático</li>
            </ul>
            
            <p><strong>💡 Consola del navegador:</strong> Abre DevTools para ver los logs enriquecidos</p>
            <p><strong>🔧 Configuración:</strong> Variables VITE_LOG_REMOTE y VITE_LOG_ENDPOINT</p>
          </div>
        </div>
      </header>
    </div>
  );
}

export default App
