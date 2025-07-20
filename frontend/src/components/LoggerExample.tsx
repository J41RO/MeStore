/**
 * Componente de ejemplo para demostrar el sistema de logging
 */

import React, { useState } from 'react';
import { useLogger } from '../hooks/useLogger';

const LoggerExample: React.FC = () => {
  const [count, setCount] = useState(0);
  const { logInfo, logError, logWarn, logUserAction } = useLogger({
    component: 'LoggerExample',
    autoLogMount: true,
    autoLogUnmount: true
  });

  const handleInfoLog = () => {
    logInfo('Usuario hizo clic en botón de info', { count }, 'info_click');
  };

  const handleErrorLog = () => {
    try {
      // Simular error
      throw new Error('Error simulado para testing');
    } catch (error) {
      logError('Error simulado capturado', { error, count }, 'error_simulation');
    }
  };

  const handleWarningLog = () => {
    logWarn('Advertencia de prueba', { count, timestamp: Date.now() }, 'warning_test');
  };

  const handleUserAction = () => {
    setCount(prev => prev + 1);
    logUserAction('increment_counter', { newValue: count + 1 });
  };

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', margin: '20px', borderRadius: '8px' }}>
      <h3>🧪 Demo del Sistema de Logging</h3>
      <p>Contador: {count}</p>
      
      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginTop: '10px' }}>
        <button onClick={handleInfoLog} style={{ padding: '8px 16px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}>
          📝 Log Info
        </button>
        
        <button onClick={handleWarningLog} style={{ padding: '8px 16px', backgroundColor: '#ffc107', color: 'black', border: 'none', borderRadius: '4px' }}>
          ⚠️ Log Warning
        </button>
        
        <button onClick={handleErrorLog} style={{ padding: '8px 16px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px' }}>
          ❌ Log Error
        </button>
        
        <button onClick={handleUserAction} style={{ padding: '8px 16px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px' }}>
          🎯 User Action (+1)
        </button>
      </div>
      
      <div style={{ marginTop: '15px', fontSize: '12px', color: '#666' }}>
        <p>🔍 <strong>Development:</strong> Los logs aparecen en la consola del navegador</p>
        <p>🚀 <strong>Production:</strong> Los logs se envían al backend (/api/v1/logs)</p>
        <p>📱 <strong>Errores globales:</strong> Capturados automáticamente</p>
      </div>
    </div>
  );
};

export default LoggerExample;