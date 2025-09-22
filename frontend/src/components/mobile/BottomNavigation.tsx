/**
 * Mobile Bottom Navigation Component
 * Provides touch-friendly navigation for mobile users in the Colombian market
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuthStore, UserType } from '../../stores/authStore';
import {
  HomeIcon,
  ShoppingBagIcon,
  UserIcon,
  Squares2X2Icon,
  ShoppingCartIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import {
  HomeIcon as HomeIconSolid,
  ShoppingBagIcon as ShoppingBagIconSolid,
  UserIcon as UserIconSolid,
  Squares2X2Icon as Squares2X2IconSolid,
  ShoppingCartIcon as ShoppingCartIconSolid,
  MagnifyingGlassIcon as MagnifyingGlassIconSolid
} from '@heroicons/react/24/solid';

interface NavItem {
  path: string;
  label: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  activeIcon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  roles: UserType[];
  badge?: number;
}

interface BottomNavigationProps {
  className?: string;
}

const BottomNavigation: React.FC<BottomNavigationProps> = ({ className = '' }) => {
  const location = useLocation();
  const { user, userType } = useAuthStore();

  // Define navigation items based on user role
  const getNavItems = (): NavItem[] => {
    const baseItems: NavItem[] = [
      {
        path: '/marketplace',
        label: 'Inicio',
        icon: HomeIcon,
        activeIcon: HomeIconSolid,
        roles: [UserType.BUYER, UserType.VENDOR, UserType.ADMIN, UserType.SUPERUSER]
      },
      {
        path: '/marketplace/search',
        label: 'Buscar',
        icon: MagnifyingGlassIcon,
        activeIcon: MagnifyingGlassIconSolid,
        roles: [UserType.BUYER, UserType.VENDOR, UserType.ADMIN, UserType.SUPERUSER]
      },
      {
        path: '/marketplace/cart',
        label: 'Carrito',
        icon: ShoppingCartIcon,
        activeIcon: ShoppingCartIconSolid,
        roles: [UserType.BUYER, UserType.VENDOR, UserType.ADMIN, UserType.SUPERUSER],
        badge: 0 // TODO: Connect to cart store
      }
    ];

    // Add role-specific items
    if (userType === UserType.BUYER) {
      baseItems.push({
        path: '/app/dashboard',
        label: 'Mi Cuenta',
        icon: UserIcon,
        activeIcon: UserIconSolid,
        roles: [UserType.BUYER]
      });
    } else if (userType === UserType.VENDOR || userType === UserType.ADMIN || userType === UserType.SUPERUSER) {
      baseItems.push({
        path: '/app/vendor-dashboard',
        label: 'Dashboard',
        icon: Squares2X2Icon,
        activeIcon: Squares2X2IconSolid,
        roles: [UserType.VENDOR, UserType.ADMIN, UserType.SUPERUSER]
      });
    } else {
      // Not logged in - show account option
      baseItems.push({
        path: '/login',
        label: 'Cuenta',
        icon: UserIcon,
        activeIcon: UserIconSolid,
        roles: [UserType.BUYER, UserType.VENDOR, UserType.ADMIN, UserType.SUPERUSER]
      });
    }

    return baseItems.filter(item =>
      !userType || item.roles.includes(userType)
    );
  };

  const navItems = getNavItems();

  const isActivePath = (path: string): boolean => {
    if (path === '/marketplace' && location.pathname === '/') return true;
    if (path === '/marketplace' && location.pathname === '/marketplace') return true;
    if (path === '/marketplace' && location.pathname === '/marketplace/home') return true;
    return location.pathname.startsWith(path);
  };

  if (!navItems.length) return null;

  return (
    <nav
      className={`fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-40 ${className}`}
      style={{
        paddingBottom: 'env(safe-area-inset-bottom)',
        boxShadow: '0 -2px 10px rgba(0, 0, 0, 0.1)'
      }}
    >
      <div className="flex justify-around items-center h-16 px-2">
        {navItems.map((item) => {
          const isActive = isActivePath(item.path);
          const IconComponent = isActive ? item.activeIcon : item.icon;

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center justify-center flex-1 h-full min-w-0 touch-manipulation relative ${
                isActive
                  ? 'text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 active:text-blue-500'
              }`}
              style={{
                WebkitTapHighlightColor: 'transparent',
                minHeight: '44px', // Touch target minimum size
                minWidth: '44px'
              }}
            >
              {/* Icon container with badge support */}
              <div className="relative flex items-center justify-center w-6 h-6 mb-1">
                <IconComponent
                  className="w-6 h-6 transition-colors duration-150"
                />

                {/* Badge for cart items */}
                {item.badge !== undefined && item.badge > 0 && (
                  <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1">
                    {item.badge > 99 ? '99+' : item.badge}
                  </div>
                )}
              </div>

              {/* Label */}
              <span
                className={`text-xs font-medium leading-tight transition-colors duration-150 ${
                  isActive ? 'text-blue-600' : 'text-gray-500'
                }`}
              >
                {item.label}
              </span>

              {/* Active indicator */}
              {isActive && (
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-8 h-1 bg-blue-600 rounded-full" />
              )}
            </Link>
          );
        })}
      </div>
    </nav>
  );
};

export default BottomNavigation;