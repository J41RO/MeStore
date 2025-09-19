// frontend/src/components/vendor/VendorMobileNavigation.tsx
// PRODUCTION_READY: Navegación móvil optimizada para vendedores colombianos
// Diseñada para pantallas pequeñas con gestos touch-friendly

import React, { useState } from 'react';
import {
  Package,
  BarChart3,
  ShoppingCart,
  Settings,
  Menu,
  X,
  Home,
  DollarSign,
  Users,
  HelpCircle,
  Bell,
  Search,
  Plus
} from 'lucide-react';

interface NavigationItem {
  id: string;
  name: string;
  icon: React.ElementType;
  badge?: number;
  href: string;
}

const NAVIGATION_ITEMS: NavigationItem[] = [
  {
    id: 'dashboard',
    name: 'Inicio',
    icon: Home,
    href: '/vendor/dashboard'
  },
  {
    id: 'products',
    name: 'Productos',
    icon: Package,
    href: '/vendor/products'
  },
  {
    id: 'orders',
    name: 'Órdenes',
    icon: ShoppingCart,
    badge: 5,
    href: '/vendor/orders'
  },
  {
    id: 'analytics',
    name: 'Analytics',
    icon: BarChart3,
    href: '/vendor/analytics'
  },
  {
    id: 'earnings',
    name: 'Ganancias',
    icon: DollarSign,
    href: '/vendor/earnings'
  }
];

const QUICK_ACTIONS = [
  {
    id: 'add-product',
    name: 'Nuevo Producto',
    icon: Plus,
    color: 'bg-primary-600',
    action: 'add-product'
  },
  {
    id: 'search',
    name: 'Buscar',
    icon: Search,
    color: 'bg-secondary-600',
    action: 'search'
  },
  {
    id: 'notifications',
    name: 'Notificaciones',
    icon: Bell,
    color: 'bg-accent-600',
    badge: 3,
    action: 'notifications'
  }
];

interface VendorMobileNavigationProps {
  currentRoute: string;
  onNavigate: (route: string) => void;
  onAction: (action: string) => void;
  className?: string;
}

export const VendorMobileNavigation: React.FC<VendorMobileNavigationProps> = ({
  currentRoute,
  onNavigate,
  onAction,
  className = ''
}) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <>
      {/* Header móvil fijo */}
      <div className={`lg:hidden fixed top-0 left-0 right-0 z-50 bg-white border-b border-neutral-200 ${className}`}>
        <div className="flex items-center justify-between px-4 h-16">
          {/* Logo y título */}
          <div className="flex items-center">
            <button
              onClick={() => setIsMenuOpen(true)}
              className="p-2 -ml-2 text-neutral-600 hover:text-neutral-900 transition-colors"
              aria-label="Abrir menú"
            >
              <Menu className="w-6 h-6" />
            </button>
            <div className="ml-2">
              <h1 className="text-lg font-bold text-neutral-900">MeStore</h1>
              <p className="text-xs text-neutral-500">Panel Vendedor</p>
            </div>
          </div>

          {/* Acciones rápidas */}
          <div className="flex items-center gap-2">
            {QUICK_ACTIONS.map(action => (
              <button
                key={action.id}
                onClick={() => onAction(action.action)}
                className={`relative p-2 text-white rounded-lg hover:opacity-90 transition-opacity ${action.color}`}
                aria-label={action.name}
              >
                <action.icon className="w-5 h-5" />
                {action.badge && action.badge > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {action.badge > 9 ? '9+' : action.badge}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Navegación inferior móvil */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-neutral-200">
        <div className="grid grid-cols-5 h-16">
          {NAVIGATION_ITEMS.map(item => {
            const isActive = currentRoute === item.href;

            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.href)}
                className={`
                  relative flex flex-col items-center justify-center gap-1 transition-colors
                  ${isActive
                    ? 'text-primary-600 bg-primary-50'
                    : 'text-neutral-500 hover:text-neutral-700 hover:bg-neutral-50'
                  }
                `}
                aria-label={item.name}
              >
                <div className="relative">
                  <item.icon className="w-5 h-5" />
                  {item.badge && item.badge > 0 && (
                    <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                      {item.badge > 9 ? '9+' : item.badge}
                    </span>
                  )}
                </div>
                <span className="text-xs font-medium truncate">{item.name}</span>

                {/* Indicador activo */}
                {isActive && (
                  <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-8 h-1 bg-primary-600 rounded-b-full" />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Menú lateral móvil */}
      {isMenuOpen && (
        <>
          {/* Overlay */}
          <div
            className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-50"
            onClick={() => setIsMenuOpen(false)}
          />

          {/* Panel del menú */}
          <div className="lg:hidden fixed top-0 left-0 bottom-0 w-80 max-w-[85vw] bg-white z-50 transform transition-transform duration-300">
            {/* Header del menú */}
            <div className="flex items-center justify-between p-4 border-b border-neutral-200">
              <div className="flex items-center">
                <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                  <Package className="w-5 h-5 text-primary-600" />
                </div>
                <div className="ml-3">
                  <h2 className="font-semibold text-neutral-900">Mi Tienda</h2>
                  <p className="text-sm text-neutral-500">Vendedor Premium</p>
                </div>
              </div>
              <button
                onClick={() => setIsMenuOpen(false)}
                className="p-2 text-neutral-500 hover:text-neutral-700 transition-colors"
                aria-label="Cerrar menú"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Navegación principal */}
            <div className="py-4">
              <nav className="space-y-1">
                {NAVIGATION_ITEMS.map(item => {
                  const isActive = currentRoute === item.href;

                  return (
                    <button
                      key={item.id}
                      onClick={() => {
                        onNavigate(item.href);
                        setIsMenuOpen(false);
                      }}
                      className={`
                        w-full flex items-center gap-3 px-4 py-3 text-left transition-colors
                        ${isActive
                          ? 'text-primary-700 bg-primary-50 border-r-2 border-primary-600'
                          : 'text-neutral-700 hover:text-neutral-900 hover:bg-neutral-50'
                        }
                      `}
                    >
                      <item.icon className="w-5 h-5" />
                      <span className="font-medium">{item.name}</span>
                      {item.badge && item.badge > 0 && (
                        <span className="ml-auto bg-red-500 text-white text-xs rounded-full px-2 py-1 min-w-[20px] text-center">
                          {item.badge > 9 ? '9+' : item.badge}
                        </span>
                      )}
                    </button>
                  );
                })}
              </nav>
            </div>

            {/* Sección de configuración */}
            <div className="border-t border-neutral-200 py-4">
              <div className="px-4 mb-3">
                <h3 className="text-sm font-medium text-neutral-500 uppercase tracking-wider">
                  Configuración
                </h3>
              </div>
              <nav className="space-y-1">
                <button
                  onClick={() => {
                    onNavigate('/vendor/settings');
                    setIsMenuOpen(false);
                  }}
                  className="w-full flex items-center gap-3 px-4 py-3 text-left text-neutral-700 hover:text-neutral-900 hover:bg-neutral-50 transition-colors"
                >
                  <Settings className="w-5 h-5" />
                  <span className="font-medium">Configuración</span>
                </button>
                <button
                  onClick={() => {
                    onNavigate('/vendor/help');
                    setIsMenuOpen(false);
                  }}
                  className="w-full flex items-center gap-3 px-4 py-3 text-left text-neutral-700 hover:text-neutral-900 hover:bg-neutral-50 transition-colors"
                >
                  <HelpCircle className="w-5 h-5" />
                  <span className="font-medium">Ayuda y Soporte</span>
                </button>
              </nav>
            </div>

            {/* Información de contacto de soporte */}
            <div className="absolute bottom-4 left-4 right-4">
              <div className="bg-neutral-50 rounded-lg p-3">
                <p className="text-sm font-medium text-neutral-900 mb-1">
                  ¿Necesitas ayuda?
                </p>
                <p className="text-xs text-neutral-600 mb-2">
                  Nuestro equipo está disponible 24/7
                </p>
                <button
                  onClick={() => onAction('contact-support')}
                  className="text-xs font-medium text-primary-600 hover:text-primary-700"
                >
                  Contactar Soporte →
                </button>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Espaciador para el contenido */}
      <div className="lg:hidden h-16" /> {/* Header height */}
      <div className="lg:hidden h-16" /> {/* Bottom nav height */}
    </>
  );
};

export default VendorMobileNavigation;