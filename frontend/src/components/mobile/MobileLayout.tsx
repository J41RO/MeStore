/**
 * Mobile Layout Component
 * Provides mobile-optimized layout with bottom navigation and PWA features
 */

import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import MobileHeader from './MobileHeader';
import BottomNavigation from './BottomNavigation';
import MobileSidebar from './MobileSidebar';
import PWAInstallPrompt from '../pwa/PWAInstallPrompt';
import PWAUpdateNotification from '../pwa/PWAUpdateNotification';
import { usePWAOffline, usePWAInstall } from '../../utils/pwa';
import { useOfflineService } from '../../services/offlineService';

interface MobileLayoutProps {
  children?: React.ReactNode;
  showBottomNav?: boolean;
  showHeader?: boolean;
  headerProps?: {
    title?: string;
    showBack?: boolean;
    showSearch?: boolean;
    showNotifications?: boolean;
  };
  className?: string;
}

const MobileLayout: React.FC<MobileLayoutProps> = ({
  children,
  showBottomNav = true,
  showHeader = true,
  headerProps = {},
  className = ''
}) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);
  const [offlineStats, setOfflineStats] = useState<any>(null);

  const { isOffline, onOffline, onOnline } = usePWAOffline();
  const { isInstallable, isInstalled } = usePWAInstall();
  const { getOfflineStats, syncOfflineData } = useOfflineService();

  // Close sidebar when clicking outside or navigating
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsSidebarOpen(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  // Handle network status changes and PWA features
  useEffect(() => {
    onOffline(() => {
      console.log('Mobile layout: Switched to offline mode');
      loadOfflineStats();
    });

    onOnline(() => {
      console.log('Mobile layout: Back online');
      syncOfflineData();
      loadOfflineStats();
    });
  }, [onOffline, onOnline]);

  // Load offline statistics
  const loadOfflineStats = async () => {
    try {
      const stats = await getOfflineStats();
      setOfflineStats(stats);
    } catch (error) {
      console.error('Error loading offline stats:', error);
    }
  };

  // Check for install prompt eligibility
  useEffect(() => {
    if (isInstallable && !isInstalled) {
      // Show install prompt after user interaction
      const timer = setTimeout(() => {
        setShowInstallPrompt(true);
      }, 10000); // Show after 10 seconds

      return () => clearTimeout(timer);
    }
  }, [isInstallable, isInstalled]);

  // Load offline stats on mount
  useEffect(() => {
    loadOfflineStats();
  }, []);

  const handleMenuClick = () => {
    setIsSidebarOpen(true);
  };

  const handleSidebarClose = () => {
    setIsSidebarOpen(false);
  };

  return (
    <div className={`min-h-screen bg-gray-50 ${className}`}>
      {/* Mobile Header */}
      {showHeader && (
        <MobileHeader
          {...headerProps}
          onMenuClick={handleMenuClick}
          className="fixed top-0 left-0 right-0 z-50"
        />
      )}

      {/* Mobile Sidebar */}
      <MobileSidebar
        isOpen={isSidebarOpen}
        onClose={handleSidebarClose}
      />

      {/* Overlay for sidebar */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={handleSidebarClose}
        />
      )}

      {/* Main Content */}
      <main
        className={`${showHeader ? 'pt-14' : ''} ${showBottomNav ? 'pb-16' : ''}`}
        style={{
          minHeight: showHeader ? 'calc(100vh - 3.5rem)' : '100vh',
          paddingTop: showHeader ? 'calc(3.5rem + env(safe-area-inset-top))' : 'env(safe-area-inset-top)',
          paddingBottom: showBottomNav ? 'calc(4rem + env(safe-area-inset-bottom))' : 'env(safe-area-inset-bottom)'
        }}
      >
        {/* Enhanced offline indicator bar with stats */}
        {isOffline && (
          <div className="bg-yellow-100 border-b border-yellow-200 px-4 py-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-yellow-800">
                  📱 Modo Offline
                </span>
                {offlineStats && offlineStats.pendingSync > 0 && (
                  <span className="bg-yellow-200 text-yellow-800 px-2 py-1 rounded-full text-xs">
                    {offlineStats.pendingSync} pendientes
                  </span>
                )}
              </div>
              {offlineStats && (
                <div className="text-xs text-yellow-700">
                  Carrito: {offlineStats.cartItems} | Productos: {offlineStats.cachedProducts}
                </div>
              )}
            </div>
            <div className="text-xs text-yellow-700 mt-1">
              Funciones disponibles: Ver productos, gestionar carrito, crear pedidos
            </div>
          </div>
        )}

        {/* PWA Install Banner for Colombian users */}
        {!isInstalled && isInstallable && !showInstallPrompt && (
          <div className="bg-blue-50 border-b border-blue-200 px-4 py-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-blue-800">
                  📲 Instala MeStocker
                </span>
                <span className="text-xs text-blue-600">
                  Acceso más rápido desde tu inicio
                </span>
              </div>
              <button
                onClick={() => setShowInstallPrompt(true)}
                className="bg-blue-600 text-white px-3 py-1 rounded text-xs font-medium hover:bg-blue-700 transition-colors"
              >
                Instalar
              </button>
            </div>
          </div>
        )}

        {/* Content */}
        <div className="h-full">
          {children || <Outlet />}
        </div>
      </main>

      {/* Bottom Navigation */}
      {showBottomNav && <BottomNavigation />}

      {/* PWA Components */}
      <PWAInstallPrompt
        onClose={() => setShowInstallPrompt(false)}
      />

      <PWAUpdateNotification />

      {/* Touch feedback styles */}
      <style jsx>{`
        * {
          -webkit-tap-highlight-color: transparent;
        }

        button, a, [role="button"] {
          touch-action: manipulation;
        }

        /* Smooth scrolling for mobile */
        * {
          -webkit-overflow-scrolling: touch;
        }

        /* Disable zoom on input focus */
        input[type="text"],
        input[type="email"],
        input[type="password"],
        input[type="number"],
        input[type="tel"],
        textarea,
        select {
          font-size: 16px;
        }

        /* Safe area support */
        @supports (padding: max(0px)) {
          .safe-area-inset-top {
            padding-top: max(1rem, env(safe-area-inset-top));
          }

          .safe-area-inset-bottom {
            padding-bottom: max(1rem, env(safe-area-inset-bottom));
          }
        }
      `}</style>
    </div>
  );
};

export default MobileLayout;