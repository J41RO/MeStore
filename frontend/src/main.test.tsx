import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import AppTest from './App.test.tsx';

console.log('🚀 Starting minimal React test...');

try {
  const rootElement = document.getElementById('root');
  if (!rootElement) {
    throw new Error('Root element not found');
  }

  console.log('✅ Root element found');

  const root = createRoot(rootElement);
  console.log('✅ React root created');

  root.render(
    <StrictMode>
      <AppTest />
    </StrictMode>
  );

  console.log('✅ React app rendered successfully');
} catch (error) {
  console.error('❌ Error rendering React app:', error);

  // Fallback: render error message directly to DOM
  const rootElement = document.getElementById('root');
  if (rootElement) {
    rootElement.innerHTML = `
      <div style="padding: 20px; background: #f8d7da; color: #721c24; border-radius: 8px; margin: 20px;">
        <h1>React Rendering Error</h1>
        <p><strong>Error:</strong> ${error.message}</p>
        <p>Check the browser console for more details.</p>
      </div>
    `;
  }
}