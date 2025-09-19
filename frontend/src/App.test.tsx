import React from 'react';
import TestComponent from './TestComponent';
import './App.css';

function AppTest() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <TestComponent />

      <div style={{ marginTop: '20px', padding: '20px', backgroundColor: 'white', borderRadius: '8px' }}>
        <h2 style={{ color: '#333', marginBottom: '15px' }}>Additional Tests</h2>

        <div style={{ marginBottom: '10px' }}>
          <strong>CSS Test:</strong> If this text has proper styling, CSS is working.
        </div>

        <div className="bg-blue-100 text-blue-700 p-3 rounded">
          Tailwind CSS Test: If this box has blue background, Tailwind is working.
        </div>

        <div style={{ marginTop: '15px' }}>
          <button
            style={{
              backgroundColor: '#007bff',
              color: 'white',
              padding: '10px 20px',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
            onClick={() => alert('JavaScript is working!')}
          >
            Click to Test JavaScript
          </button>
        </div>
      </div>
    </div>
  );
}

export default AppTest;