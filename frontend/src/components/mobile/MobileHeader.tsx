/**
 * Mobile Header Component
 * Optimized header for mobile PWA experience with Colombian market features
 */

import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';
import { usePWAInstall, usePWAOffline } from '../../utils/pwa';
import {
  Bars3Icon,
  MagnifyingGlassIcon,
  BellIcon,
  UserIcon,
  ArrowLeftIcon,
  WifiIcon,
  SignalSlashIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline';

interface MobileHeaderProps {
  title?: string;
  showBack?: boolean;
  showSearch?: boolean;
  showNotifications?: boolean;
  showInstallPrompt?: boolean;
  className?: string;
  onMenuClick?: () => void;
  onSearchClick?: () => void;
}

const MobileHeader: React.FC<MobileHeaderProps> = ({
  title,
  showBack = false,
  showSearch = true,
  showNotifications = true,
  showInstallPrompt = true,
  className = '',
  onMenuClick,
  onSearchClick
}) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuthStore();
  const { isInstallable, install } = usePWAInstall();
  const { isOffline } = usePWAOffline();

  const [showInstallBanner, setShowInstallBanner] = useState(
    isInstallable && showInstallPrompt
  );

  const handleBack = () => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate('/');
    }
  };

  const handleSearch = () => {
    if (onSearchClick) {
      onSearchClick();
    } else {
      navigate('/marketplace/search');
    }
  };

  const handleInstall = async () => {
    const success = await install();
    if (success) {
      setShowInstallBanner(false);
    }
  };

  const getPageTitle = (): string => {
    if (title) return title;

    // Auto-generate title based on route
    const path = location.pathname;
    if (path === '/' || path === '/marketplace' || path === '/marketplace/home') {
      return 'MeStocker';
    }
    if (path.includes('/marketplace/search')) return 'Buscar Productos';
    if (path.includes('/marketplace/cart')) return 'Mi Carrito';
    if (path.includes('/marketplace/category')) return 'Categoría';
    if (path.includes('/marketplace/product')) return 'Producto';
    if (path.includes('/checkout')) return 'Checkout';
    if (path.includes('/dashboard')) return 'Mi Cuenta';
    if (path.includes('/vendor-dashboard')) return 'Dashboard';
    if (path.includes('/login')) return 'Iniciar Sesión';
    if (path.includes('/register')) return 'Registrarse';

    return 'MeStocker';
  };

  return (
    <div className={`bg-white border-b border-gray-200 ${className}`}>
      {/* Install Banner */}
      {showInstallBanner && isInstallable && (
        <div className="bg-blue-50 border-b border-blue-200 px-4 py-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <ArrowDownTrayIcon className="w-4 h-4 text-blue-600 mr-2" />
              <span className="text-sm text-blue-800">
                ¡Instala MeStocker para mejor experiencia!
              </span>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={handleInstall}
                className="text-xs bg-blue-600 text-white px-3 py-1 rounded font-medium"
              >
                Instalar
              </button>
              <button
                onClick={() => setShowInstallBanner(false)}
                className="text-xs text-blue-600 hover:text-blue-800"
              >
                ✕
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Offline Banner */}
      {isOffline && (
        <div className="bg-yellow-50 border-b border-yellow-200 px-4 py-2">
          <div className="flex items-center">
            <SignalSlashIcon className="w-4 h-4 text-yellow-600 mr-2" />
            <span className="text-sm text-yellow-800">
              Sin conexión - Usando modo offline
            </span>
          </div>
        </div>
      )}

      {/* Main Header */}
      <header
        className="h-14 px-4 flex items-center justify-between"
        style={{
          paddingTop: 'env(safe-area-inset-top)'
        }}
      >
        {/* Left Section */}
        <div className="flex items-center flex-1 min-w-0">
          {showBack ? (
            <button
              onClick={handleBack}
              className="mr-3 p-2 -ml-2 text-gray-600 hover:text-gray-900 touch-manipulation"
              style={{
                minHeight: '44px',
                minWidth: '44px'
              }}
            >
              <ArrowLeftIcon className="w-6 h-6" />
            </button>
          ) : (
            <button
              onClick={onMenuClick}
              className="mr-3 p-2 -ml-2 text-gray-600 hover:text-gray-900 touch-manipulation md:hidden"
              style={{
                minHeight: '44px',
                minWidth: '44px'
              }}
            >
              <Bars3Icon className="w-6 h-6" />
            </button>
          )}

          {/* Title/Logo */}
          <div className="flex items-center min-w-0 flex-1">
            <Link
              to="/"
              className="text-lg font-bold text-gray-900 truncate"
            >
              {getPageTitle()}
            </Link>
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center space-x-1">
          {/* Connection Status */}
          {!isOffline && (
            <div className="p-2 text-green-600">
              <WifiIcon className="w-5 h-5" />
            </div>
          )}

          {/* Search Button */}
          {showSearch && (
            <button
              onClick={handleSearch}
              className="p-2 text-gray-600 hover:text-gray-900 touch-manipulation"
              style={{
                minHeight: '44px',
                minWidth: '44px'
              }}
            >
              <MagnifyingGlassIcon className="w-6 h-6" />
            </button>
          )}

          {/* Notifications */}
          {showNotifications && isAuthenticated && (
            <button
              className="p-2 text-gray-600 hover:text-gray-900 relative touch-manipulation"
              style={{
                minHeight: '44px',
                minWidth: '44px'
              }}
            >
              <BellIcon className="w-6 h-6" />
              {/* Notification badge */}
              <div className="absolute top-1 right-1 w-3 h-3 bg-red-500 rounded-full border-2 border-white"></div>
            </button>
          )}

          {/* User Avatar/Login */}
          <Link
            to={isAuthenticated ? '/app/dashboard' : '/login'}
            className="p-2 text-gray-600 hover:text-gray-900 touch-manipulation"
            style={{
              minHeight: '44px',
              minWidth: '44px'
            }}
          >
            {user?.avatar_url ? (
              <img
                src={user.avatar_url}
                alt={user.nombre}
                className="w-6 h-6 rounded-full"
              />
            ) : (
              <UserIcon className="w-6 h-6" />
            )}
          </Link>
        </div>
      </header>
    </div>
  );
};

export default MobileHeader;