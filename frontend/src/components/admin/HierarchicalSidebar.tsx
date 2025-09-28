import React, { useRef, useEffect, useCallback, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { MenuCategory } from './MenuCategory';
import { MenuItemData } from './MenuItem';
import { useSidebar } from './SidebarProvider';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';

// Definición de la estructura jerárquica del sidebar con iconografía optimizada
const sidebarStructure = [
  {
    id: 'controlCenter',
    title: 'Control Center',
    icon: 'RectangleStackIcon', // Actualizado según especificaciones
    items: [
      {
        id: 'dashboard',
        name: 'Dashboard',
        href: '/admin-secure-portal/dashboard',
        icon: 'RectangleStackIcon' // Dashboard principal
      },
      {
        id: 'kpis',
        name: 'KPIs',
        href: '/admin-secure-portal/kpis',
        icon: 'ChartBarIcon' // KPIs según especificación
      },
      {
        id: 'overview',
        name: 'System Overview',
        href: '/admin-secure-portal/overview',
        icon: 'EyeIcon' // System Overview según especificación
      }
    ]
  },
  {
    id: 'userManagement',
    title: 'User Management',
    icon: 'UsersIcon', // Mantener según especificaciones
    items: [
      {
        id: 'users',
        name: 'Users',
        href: '/admin-secure-portal/users',
        icon: 'UsersIcon' // Users según especificación
      },
      {
        id: 'roles',
        name: 'Roles',
        href: '/admin-secure-portal/roles',
        icon: 'ShieldCheckIcon' // Roles según especificación
      },
      {
        id: 'authentication',
        name: 'Authentication',
        href: '/admin-secure-portal/auth',
        icon: 'KeyIcon' // Authentication según especificación
      }
    ]
  },
  {
    id: 'operations',
    title: 'Operations',
    icon: 'ShoppingBagIcon',
    items: [
      {
        id: 'inventory',
        name: 'Inventory',
        href: '/admin-secure-portal/storage-manager',
        icon: 'CubeIcon' // Actualizado según especificaciones
      },
      {
        id: 'orders',
        name: 'Orders',
        href: '/admin-secure-portal/orders',
        icon: 'ShoppingBagIcon' // Orders según especificación
      },
      {
        id: 'warehouse',
        name: 'Warehouse',
        href: '/admin-secure-portal/warehouse-map',
        icon: 'BuildingStorefrontIcon' // Warehouse según especificación
      },
      {
        id: 'tracking',
        name: 'Tracking',
        href: '/admin-secure-portal/movement-tracker',
        icon: 'TruckIcon' // Tracking según especificación
      }
    ]
  },
  {
    id: 'system',
    title: 'System',
    icon: 'Cog6ToothIcon', // Actualizado según especificaciones
    items: [
      {
        id: 'config',
        name: 'Config',
        href: '/admin-secure-portal/system-config',
        icon: 'Cog6ToothIcon' // Config según especificación
      },
      {
        id: 'reports',
        name: 'Reports',
        href: '/admin-secure-portal/reports',
        icon: 'DocumentTextIcon' // Reports según especificación
      },
      {
        id: 'audit',
        name: 'Audit',
        href: '/admin-secure-portal/auditoria',
        icon: 'ClipboardDocumentListIcon' // Audit según especificación
      },
      {
        id: 'alerts',
        name: 'Alerts',
        href: '/admin-secure-portal/alertas-incidentes',
        icon: 'ExclamationTriangleIcon' // Alerts según especificación
      }
    ]
  }
];

// Props del componente HierarchicalSidebar
export interface HierarchicalSidebarProps {
  onClose?: () => void;
  className?: string;
  'aria-label'?: string;
  id?: string;
}

// Componente HierarchicalSidebar
export const HierarchicalSidebar: React.FC<HierarchicalSidebarProps> = ({
  onClose,
  className = '',
  'aria-label': ariaLabel = 'Admin Navigation',
  id = 'admin-sidebar'
}) => {
  const location = useLocation();
  const {
    toggleCategory,
    isCategoryCollapsed
  } = useSidebar();

  // Accessibility state
  const [announceText, setAnnounceText] = useState('');
  const sidebarRef = useRef<HTMLElement>(null);
  const skipLinkRef = useRef<HTMLAnchorElement>(null);

  // Keyboard navigation hook
  const {
    currentFocus,
    handleKeyDown,
    setFocusToFirst,
    setFocusToLast
  } = useKeyboardNavigation({
    containerRef: sidebarRef,
    onEscape: onClose,
    announceChanges: setAnnounceText
  });

  // Determinar qué item está activo basado en la ruta actual
  const isItemActive = (item: MenuItemData): boolean => {
    return location.pathname === item.href;
  };

  // Manejar click en item (para cerrar sidebar en móvil)
  const handleItemClick = (item: MenuItemData) => {
    if (onClose) {
      onClose();
    }
  };

  // Manejar toggle de categoría
  const handleToggleCategory = useCallback((categoryId: string) => {
    const wasCollapsed = isCategoryCollapsed(categoryId as any);
    toggleCategory(categoryId as any);

    // Anunciar cambio de estado para screen readers
    const categoryData = sidebarStructure.find(cat => cat.id === categoryId);
    const actionText = wasCollapsed ? 'expandida' : 'contraída';
    setAnnounceText(`Categoría ${categoryData?.title} ${actionText}`);
  }, [toggleCategory, isCategoryCollapsed]);

  // Manejar click en skip link
  const handleSkipToContent = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
      mainContent.focus();
      mainContent.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);

  // Focus management para keyboard navigation
  useEffect(() => {
    const handleFocus = (e: FocusEvent) => {
      if (sidebarRef.current?.contains(e.target as Node)) {
        // Usuario está navegando dentro del sidebar
        if (announceText) {
          setTimeout(() => setAnnounceText(''), 1000);
        }
      }
    };

    document.addEventListener('focusin', handleFocus);
    return () => document.removeEventListener('focusin', handleFocus);
  }, [announceText]);

  return (
    <>
      {/* Skip Link para navegación rápida */}
      <a
        ref={skipLinkRef}
        href="#main-content"
        onClick={handleSkipToContent}
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        tabIndex={0}
      >
        Saltar al contenido principal
      </a>

      <nav
        id={id}
        ref={sidebarRef}
        className={`transition-transform ${className}`}
        role="navigation"
        aria-label={ariaLabel}
        onKeyDown={handleKeyDown}
        tabIndex={-1}
      >
        {/* Live region para anuncios de screen reader */}
        <div
          aria-live="polite"
          aria-atomic="true"
          className="sr-only"
          role="status"
        >
          {announceText}
        </div>

        <div className="space-y-2" role="list">
          {sidebarStructure.map((category, index) => {
            const isCollapsed = isCategoryCollapsed(category.id as any);
            const activeItemsCount = category.items.filter(item => item.href === location.pathname).length;

            return (
              <div key={category.id} role="listitem">
                <MenuCategory
                  title={category.title}
                  items={category.items}
                  icon={category.icon}
                  isCollapsed={isCollapsed}
                  onToggleCollapse={() => handleToggleCategory(category.id)}
                  onItemClick={handleItemClick}
                  currentPath={location.pathname}
                  categoryIndex={index}
                  totalCategories={sidebarStructure.length}
                  activeItemsCount={activeItemsCount}
                  aria-label={`Categoría ${category.title}${activeItemsCount > 0 ? `, contiene ${activeItemsCount} elemento activo` : ''}`}
                  id={`category-${category.id}`}
                />
              </div>
            );
          })}
        </div>
      </nav>
    </>
  );
};