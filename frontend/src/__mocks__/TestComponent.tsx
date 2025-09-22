import React from 'react';

const TestComponent: React.FC = () => {
  // Use process.env instead of import.meta in tests
  const env = {
    MODE: process.env.NODE_ENV || 'test',
    VITE_API_BASE_URL: 'http://localhost:8000',
  };

  return (
    <div style={{
      padding: '20px',
      backgroundColor: '#f0f0f0',
      border: '2px solid #007bff',
      borderRadius: '8px',
      textAlign: 'center',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1 style={{ color: '#007bff', marginBottom: '10px' }}>
        🎉 React is Working!
      </h1>
      <p style={{ color: '#333', marginBottom: '15px' }}>
        If you can see this, React is rendering correctly.
      </p>
      <div style={{
        backgroundColor: '#d4edda',
        padding: '10px',
        borderRadius: '4px',
        border: '1px solid #c3e6cb',
        color: '#155724'
      }}>
        ✅ Components are loading successfully
      </div>
      <div style={{ marginTop: '15px' }}>
        <strong>Debug Info:</strong>
        <ul style={{ textAlign: 'left', margin: '10px 0' }}>
          <li>Environment: {env.MODE}</li>
          <li>API URL: {env.VITE_API_BASE_URL}</li>
          <li>Timestamp: {new Date().toISOString()}</li>
        </ul>
      </div>
    </div>
  );
};

export default TestComponent;