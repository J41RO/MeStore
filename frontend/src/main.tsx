import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { AuthProvider } from './contexts/AuthContext';
import { UserProvider } from './contexts/UserContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { CartProvider } from './contexts/CartContext';
import './index.css';
import 'leaflet/dist/leaflet.css';
import App from './App.tsx';
import { pwaManager } from './utils/pwa';
import { pushNotificationService } from './services/pushNotificationService';
import { offlineService } from './services/offlineService';

// Initialize PWA services
console.log('🇨🇴 Initializing MeStocker PWA for Colombian market');

// Initialize services for Colombian PWA
const initializePWA = async () => {
  try {
    // Log PWA readiness
    if (pwaManager) {
      console.log('✅ PWA Manager initialized');
    }

    if (pushNotificationService) {
      console.log('✅ Push Notification Service ready');
    }

    if (offlineService) {
      console.log('✅ Offline Service initialized');
    }

    // Check if running as PWA
    if (window.matchMedia('(display-mode: standalone)').matches) {
      console.log('🚀 Running as installed PWA');
      document.body.classList.add('pwa-mode');
    }

    // Setup Colombian-specific PWA features
    if ('serviceWorker' in navigator) {
      const registration = await navigator.serviceWorker.ready;
      console.log('🛠️ Service Worker ready for Colombian features');

      // Store Colombian market configuration
      registration.active?.postMessage({
        type: 'INIT_COLOMBIAN_CONFIG',
        config: {
          currency: 'COP',
          locale: 'es-CO',
          timezone: 'America/Bogota',
          city: 'Bucaramanga'
        }
      });
    }

  } catch (error) {
    console.error('❌ Error initializing PWA:', error);
  }
};

// Initialize PWA after DOM is ready
initializePWA();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID || 'your_google_client_id_here'}>
        <AuthProvider>
          <UserProvider>
            <NotificationProvider>
              <CartProvider>
                <App />
              </CartProvider>
            </NotificationProvider>
          </UserProvider>
        </AuthProvider>
      </GoogleOAuthProvider>
    </BrowserRouter>
  </StrictMode>
);