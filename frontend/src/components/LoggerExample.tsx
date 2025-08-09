import React, { useState } from 'react';
import { useLogger } from '../hooks/useLogger';

const LoggerExample: React.FC = () => {
  const [count, setCount] = useState(0);
  const { logInfo, logError, logWarn, logUserAction } =
    useLogger('LoggerExample');

  const handleInfoClick = () => {
    setCount(prev => prev + 1);
    logInfo('Usuario hizo clic en botón de info', { count });
  };

  const handleErrorClick = () => {
    try {
      // Simular error
      throw new Error('Error simulado para testing');
    } catch (error) {
      logError('Error simulado capturado', {
        error: (error as Error).message,
        count,
      });
    }
  };

  const handleWarningClick = () => {
    logWarn('Advertencia de prueba', { count, timestamp: Date.now() });
  };

  const handleUserAction = () => {
    const newCount = count + 1;
    setCount(newCount);
    logUserAction('increment_counter', 'LoggerExample', { newValue: newCount });
  };

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h2>🔍 Logger Example Component</h2>
      <p>Componente de ejemplo para testing del sistema de logging frontend</p>

      <div style={{ marginBottom: '20px' }}>
        <p>
          <strong>Contador:</strong> {count}
        </p>
      </div>

      <div
        style={{
          display: 'flex',
          gap: '10px',
          flexWrap: 'wrap',
          marginBottom: '20px',
        }}
      >
        <button
          onClick={handleInfoClick}
          style={{
            padding: '8px 16px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          📝 Log Info
        </button>

        <button
          onClick={handleErrorClick}
          style={{
            padding: '8px 16px',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          ❌ Log Error
        </button>

        <button
          onClick={handleWarningClick}
          style={{
            padding: '8px 16px',
            backgroundColor: '#ffc107',
            color: 'black',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          ⚠️ Log Warning
        </button>

        <button
          onClick={handleUserAction}
          style={{
            padding: '8px 16px',
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          👤 User Action
        </button>
      </div>

      <div
        style={{
          backgroundColor: '#f8f9fa',
          padding: '15px',
          borderRadius: '4px',
          border: '1px solid #dee2e6',
        }}
      >
        <h4>📋 Funcionalidades del Logger:</h4>
        <ul>
          <li>✅ Log de información general</li>
          <li>✅ Log de errores con stack trace</li>
          <li>✅ Log de advertencias</li>
          <li>✅ Log de acciones de usuario</li>
          <li>✅ Auto-log de mount/unmount de componentes</li>
        </ul>
        <p>
          <em>Abre DevTools Console para ver los logs</em>
        </p>
      </div>
    </div>
  );
};

export default LoggerExample;
