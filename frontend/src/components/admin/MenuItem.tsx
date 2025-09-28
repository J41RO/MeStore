import React, { memo, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
// Optimized icon imports with tree shaking
import {
  ChartBarIcon,
  UserIcon,
  PresentationChartLineIcon,
  EyeIcon,
  Cog6ToothIcon, // Reemplaza CogIcon
  DocumentTextIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  HomeIcon,
  UsersIcon,
  ShoppingBagIcon,
  TruckIcon,
  ClipboardDocumentListIcon,
  MapIcon,
  ClipboardDocumentCheckIcon,
  DocumentChartBarIcon,
  InboxStackIcon,
  WrenchScrewdriverIcon,
  BellAlertIcon,
  MagnifyingGlassIcon,
  // Nuevos iconos integrados
  RectangleStackIcon,
  CubeIcon,
  BuildingStorefrontIcon,
  KeyIcon
} from '@heroicons/react/24/outline';

// Mapping optimizado de iconos con tree shaking y performance
const iconMap: Record<string, React.ComponentType<React.ComponentProps<'svg'>>> = {
  ChartBarIcon,
  UserIcon,
  PresentationChartLineIcon,
  EyeIcon,
  Cog6ToothIcon,
  DocumentTextIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  HomeIcon,
  UsersIcon,
  ShoppingBagIcon,
  TruckIcon,
  ClipboardDocumentListIcon,
  MapIcon,
  ClipboardDocumentCheckIcon,
  DocumentChartBarIcon,
  InboxStackIcon,
  WrenchScrewdriverIcon,
  BellAlertIcon,
  MagnifyingGlassIcon,
  // Nuevos iconos integrados
  RectangleStackIcon,
  CubeIcon,
  BuildingStorefrontIcon,
  KeyIcon,
  // Backward compatibility
  CogIcon: Cog6ToothIcon
};

// Interfaz para un item de menú
export interface MenuItemData {
  id: string;
  name: string;
  href: string;
  icon?: string;
}

// Props del componente MenuItem con performance optimizations
export interface MenuItemProps {
  item: MenuItemData;
  isActive: boolean;
  onClick?: (item: MenuItemData) => void;
  onItemClick?: (item: MenuItemData) => void;
  itemIndex?: number;
  totalItems?: number;
  categoryTitle?: string;
}

// Componente MenuItem optimizado con React.memo y useMemo
export const MenuItem: React.FC<MenuItemProps> = memo(({
  item,
  isActive,
  onClick,
  onItemClick,
  itemIndex = 0,
  totalItems = 1,
  categoryTitle = ''
}) => {
  const navigate = useNavigate();

  // Memoizar el icono para evitar re-renders innecesarios
  const IconComponent = useMemo(() => {
    return item.icon ? iconMap[item.icon] : null;
  }, [item.icon]);

  // Memoizar handlers para mejor performance
  const handleClick = useCallback(() => {
    // Navegar a la ruta
    navigate(item.href);

    // Llamar callbacks opcionales
    if (onClick) {
      onClick(item);
    }

    if (onItemClick) {
      onItemClick(item);
    }
  }, [navigate, item.href, onClick, onItemClick, item]);

  // Manejar navegación por teclado con useCallback
  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    const { key, shiftKey, ctrlKey, metaKey } = event;

    // Solo manejar keys sin modificadores (excepto Shift para accessibility)
    if (ctrlKey || metaKey) return;

    switch (key) {
      case 'Enter':
      case ' ':
        event.preventDefault();
        handleClick();
        break;

      default:
        // Permitir navegación normal con arrow keys (manejada por el contenedor)
        break;
    }
  }, [handleClick]);

  // Crear aria-label comprensivo
  const menuItemAriaLabel = useMemo(() => {
    const positionText = `Elemento ${itemIndex + 1} de ${totalItems}`;
    const categoryText = categoryTitle ? ` en categoría ${categoryTitle}` : '';
    const stateText = isActive ? ', página actual' : '';

    return `${item.name}${categoryText}. ${positionText}${stateText}. Navegar a ${item.name}`;
  }, [item.name, itemIndex, totalItems, categoryTitle, isActive]);

  // Memoizar clases CSS para evitar cálculos repetidos con mejores focus indicators
  const buttonClasses = useMemo(() => {
    const baseClasses = 'w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 flex items-center';
    const focusClasses = 'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-white';
    const touchClasses = 'min-h-[44px] min-w-[44px]'; // WCAG 2.1 AA touch target size

    if (isActive) {
      return `${baseClasses} ${focusClasses} ${touchClasses} bg-red-100 text-red-900 border-l-4 border-red-500 font-semibold`;
    }

    return `${baseClasses} ${focusClasses} ${touchClasses} text-gray-700 hover:bg-red-50 hover:text-red-700 focus:bg-blue-50`;
  }, [isActive]);

  return (
    <button
      type="button"
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      data-href={item.href}
      tabIndex={0}
      role="menuitem"
      aria-label={menuItemAriaLabel}
      aria-current={isActive ? 'page' : undefined}
      aria-describedby={`${item.id}-description`}
      className={buttonClasses}
      style={{
        // Optimización GPU para animaciones suaves
        willChange: 'transform, background-color',
        transform: 'translateZ(0)' // Hardware acceleration
      }}
      data-item-index={itemIndex}
      id={`menu-item-${item.id}`}
    >
      {/* Descripción oculta para screen readers */}
      <span id={`${item.id}-description`} className="sr-only">
        {isActive ? 'Página actual' : 'Presiona Enter para navegar'}
      </span>
      {/* Icono optimizado */}
      {IconComponent ? (
        <IconComponent
          className="w-5 h-5 mr-3 transition-transform duration-150"
          data-testid={`menu-item-icon-${item.icon}`}
          style={{
            // Evitar layout shifts con iconos
            minWidth: '1.25rem',
            minHeight: '1.25rem'
          }}
        />
      ) : (
        <div
          className="w-5 h-5 mr-3 bg-gray-300 rounded flex-shrink-0"
          data-testid="menu-item-icon-fallback"
          style={{
            minWidth: '1.25rem',
            minHeight: '1.25rem'
          }}
        />
      )}

      {/* Nombre del item con indicador visual para página actual */}
      <span className="truncate flex-1">
        {item.name}
        {isActive && (
          <span className="sr-only"> (página actual)</span>
        )}
      </span>

      {/* Indicador visual de página actual */}
      {isActive && (
        <span
          className="ml-2 w-2 h-2 bg-red-500 rounded-full flex-shrink-0"
          aria-hidden="true"
          title="Página actual"
        />
      )}
    </button>
  );
});

// Configurar display name para debugging
MenuItem.displayName = 'MenuItem';