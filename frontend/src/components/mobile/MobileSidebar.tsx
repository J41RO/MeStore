/**
 * Mobile Sidebar Component
 * Slide-out navigation menu for mobile users with Colombian market features
 */

import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore, UserType } from '../../stores/authStore';
import { usePWAInstall } from '../../utils/pwa';
import {
  XMarkIcon,
  HomeIcon,
  ShoppingBagIcon,
  UserIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  ArrowLeftOnRectangleIcon,
  Squares2X2Icon,
  ChatBubbleLeftIcon,
  QuestionMarkCircleIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  HeartIcon,
  ClockIcon,
  DocumentTextIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

interface MobileSidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

interface MenuItem {
  path: string;
  label: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  roles?: UserType[];
  action?: () => void;
  external?: boolean;
  divider?: boolean;
}

const MobileSidebar: React.FC<MobileSidebarProps> = ({ isOpen, onClose }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, userType, isAuthenticated, logout } = useAuthStore();
  const { isInstallable, install, isInstalled } = usePWAInstall();

  const handleLogout = async () => {
    logout();
    onClose();
    navigate('/');
  };

  const handleInstall = async () => {
    const success = await install();
    if (success) {
      onClose();
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'MeStocker - Fulfillment Inteligente',
          text: 'Descubre la mejor plataforma de fulfillment en Bucaramanga',
          url: window.location.origin
        });
      } catch (error) {
        console.log('Error sharing:', error);
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.origin);
      // TODO: Show toast notification
    }
    onClose();
  };

  const getMenuItems = (): MenuItem[] => {
    const items: MenuItem[] = [];

    // Main navigation
    items.push(
      {
        path: '/marketplace',
        label: 'Inicio',
        icon: HomeIcon
      },
      {
        path: '/marketplace/search',
        label: 'Buscar Productos',
        icon: ShoppingBagIcon
      }
    );

    if (isAuthenticated) {
      // Authenticated user items
      if (userType === UserType.BUYER) {
        items.push(
          {
            path: '/app/dashboard',
            label: 'Mi Cuenta',
            icon: UserIcon
          },
          {
            path: '/app/mis-compras',
            label: 'Mis Compras',
            icon: ClockIcon
          },
          {
            path: '/marketplace/favorites', // TODO: Implement favorites
            label: 'Favoritos',
            icon: HeartIcon
          }
        );
      } else if (userType === UserType.VENDOR || userType === UserType.ADMIN || userType === UserType.SUPERUSER) {
        items.push(
          {
            path: '/app/vendor-dashboard',
            label: 'Dashboard Vendedor',
            icon: Squares2X2Icon
          },
          {
            path: '/app/productos',
            label: 'Mis Productos',
            icon: ShoppingBagIcon
          },
          {
            path: '/app/ordenes',
            label: 'Mis Órdenes',
            icon: ClockIcon
          },
          {
            path: '/app/reportes',
            label: 'Reportes',
            icon: DocumentTextIcon
          }
        );
      }

      // Common authenticated items
      items.push(
        { divider: true, path: '', label: '', icon: HomeIcon },
        {
          path: '/app/configuracion', // TODO: Implement settings
          label: 'Configuración',
          icon: Cog6ToothIcon
        }
      );
    } else {
      // Not authenticated
      items.push(
        {
          path: '/login',
          label: 'Iniciar Sesión',
          icon: ArrowRightOnRectangleIcon
        },
        {
          path: '/register',
          label: 'Registrarse',
          icon: UserIcon
        }
      );
    }

    // App actions
    items.push(
      { divider: true, path: '', label: '', icon: HomeIcon }
    );

    // PWA Install
    if (isInstallable && !isInstalled) {
      items.push({
        path: '',
        label: 'Instalar App',
        icon: ArrowDownTrayIcon,
        action: handleInstall
      });
    }

    // Share
    items.push({
      path: '',
      label: 'Compartir App',
      icon: ShareIcon,
      action: handleShare
    });

    // Support and info
    items.push(
      {
        path: '/ayuda', // TODO: Implement help
        label: 'Ayuda y Soporte',
        icon: QuestionMarkCircleIcon
      },
      {
        path: '/terminos', // TODO: Implement terms
        label: 'Términos y Condiciones',
        icon: ShieldCheckIcon
      }
    );

    // Colombian market specific
    items.push({
      path: 'https://wa.me/573001234567', // Colombian WhatsApp
      label: 'Soporte WhatsApp',
      icon: ChatBubbleLeftIcon,
      external: true
    });

    // Logout
    if (isAuthenticated) {
      items.push(
        { divider: true, path: '', label: '', icon: HomeIcon },
        {
          path: '',
          label: 'Cerrar Sesión',
          icon: ArrowLeftOnRectangleIcon,
          action: handleLogout
        }
      );
    }

    return items;
  };

  const menuItems = getMenuItems();

  return (
    <>
      {/* Sidebar */}
      <div
        className={`fixed top-0 left-0 h-full w-80 max-w-[80vw] bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{
          paddingTop: 'env(safe-area-inset-top)',
          paddingBottom: 'env(safe-area-inset-bottom)'
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center mr-3">
              <span className="text-white font-bold text-lg">M</span>
            </div>
            <div>
              <h2 className="font-bold text-gray-900">MeStocker</h2>
              {isAuthenticated && user && (
                <p className="text-sm text-gray-500 truncate">
                  {user.nombre || user.email}
                </p>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 touch-manipulation"
            style={{
              minHeight: '44px',
              minWidth: '44px'
            }}
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        {/* Menu Items */}
        <div className="flex-1 overflow-y-auto">
          <nav className="p-2">
            {menuItems.map((item, index) => {
              if (item.divider) {
                return (
                  <div
                    key={index}
                    className="h-px bg-gray-200 my-2"
                  />
                );
              }

              const isActive = location.pathname === item.path ||
                (item.path !== '/' && location.pathname.startsWith(item.path));

              if (item.action) {
                return (
                  <button
                    key={index}
                    onClick={item.action}
                    className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors touch-manipulation ${
                      isActive
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-50 active:bg-gray-100'
                    }`}
                    style={{
                      minHeight: '44px'
                    }}
                  >
                    <item.icon className="w-6 h-6 mr-3 flex-shrink-0" />
                    <span className="font-medium">{item.label}</span>
                  </button>
                );
              }

              if (item.external) {
                return (
                  <a
                    key={index}
                    href={item.path}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={onClose}
                    className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-50 active:bg-gray-100 rounded-lg transition-colors touch-manipulation"
                    style={{
                      minHeight: '44px'
                    }}
                  >
                    <item.icon className="w-6 h-6 mr-3 flex-shrink-0" />
                    <span className="font-medium">{item.label}</span>
                  </a>
                );
              }

              return (
                <Link
                  key={index}
                  to={item.path}
                  onClick={onClose}
                  className={`flex items-center px-4 py-3 rounded-lg transition-colors touch-manipulation ${
                    isActive
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-700 hover:bg-gray-50 active:bg-gray-100'
                  }`}
                  style={{
                    minHeight: '44px'
                  }}
                >
                  <item.icon className="w-6 h-6 mr-3 flex-shrink-0" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 text-center">
            <p>MeStocker v1.0</p>
            <p>Bucaramanga, Colombia 🇨🇴</p>
          </div>
        </div>
      </div>
    </>
  );
};

export default MobileSidebar;