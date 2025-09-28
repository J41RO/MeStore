import React, { memo, useCallback, useMemo } from 'react';
import { ChevronRightIcon } from '@heroicons/react/24/outline';
// Optimized icon imports for tree shaking
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
  // Nuevos iconos según especificaciones
  RectangleStackIcon, // Dashboard principal
  CubeIcon, // Inventory
  BuildingStorefrontIcon, // Warehouse
  KeyIcon // Authentication
} from '@heroicons/react/24/outline';
import { MenuItem, MenuItemData } from './MenuItem';

// Mapping optimizado de iconos con tree shaking para categorías
const categoryIconMap: Record<string, React.ComponentType<React.ComponentProps<'svg'>>> = {
  HomeIcon,
  UsersIcon,
  ShoppingBagIcon,
  Cog6ToothIcon, // Actualizado
  ChartBarIcon,
  UserIcon,
  PresentationChartLineIcon,
  EyeIcon,
  DocumentTextIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
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

// Props del componente MenuCategory con performance optimizations
export interface MenuCategoryProps {
  title: string;
  items: MenuItemData[];
  icon: string;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  onItemClick?: (item: MenuItemData) => void;
  currentPath?: string;
  categoryIndex?: number;
  totalCategories?: number;
  activeItemsCount?: number;
  'aria-label'?: string;
  id?: string;
}

// Componente MenuCategory optimizado con React.memo
export const MenuCategory: React.FC<MenuCategoryProps> = memo(({
  title,
  items,
  icon,
  isCollapsed,
  onToggleCollapse,
  onItemClick,
  currentPath,
  categoryIndex = 0,
  totalCategories = 1,
  activeItemsCount = 0,
  'aria-label': ariaLabel,
  id
}) => {
  // Memoizar el icono de la categoría para evitar recreaciones
  const CategoryIcon = useMemo(() => {
    return categoryIconMap[icon] || HomeIcon;
  }, [icon]);

  // Memoizar ID único para los items
  const itemsId = useMemo(() => {
    return `menu-items-${title.toLowerCase().replace(/\s+/g, '-')}`;
  }, [title]);

  // Crear aria-label comprensivo
  const categoryAriaLabel = useMemo(() => {
    if (ariaLabel) return ariaLabel;

    const positionText = `Categoría ${categoryIndex + 1} de ${totalCategories}`;
    const stateText = isCollapsed ? 'contraída' : 'expandida';
    const itemsText = `${items.length} elemento${items.length !== 1 ? 's' : ''}`;
    const activeText = activeItemsCount > 0 ? `, ${activeItemsCount} activo${activeItemsCount !== 1 ? 's' : ''}` : '';

    return `${title}. ${positionText}, ${stateText}, contiene ${itemsText}${activeText}`;
  }, [ariaLabel, title, categoryIndex, totalCategories, isCollapsed, items.length, activeItemsCount]);

  // Manejar click en el header con useCallback
  const handleHeaderClick = useCallback(() => {
    onToggleCollapse();
  }, [onToggleCollapse]);

  // Manejar navegación por teclado en el header con useCallback
  const handleHeaderKeyDown = useCallback((event: React.KeyboardEvent) => {
    const { key, shiftKey } = event;

    switch (key) {
      case 'Enter':
      case ' ':
        event.preventDefault();
        onToggleCollapse();
        break;

      case 'ArrowRight':
        if (isCollapsed) {
          event.preventDefault();
          onToggleCollapse();
        }
        break;

      case 'ArrowLeft':
        if (!isCollapsed) {
          event.preventDefault();
          onToggleCollapse();
        }
        break;

      default:
        // Permitir navegación normal con otros keys
        break;
    }
  }, [onToggleCollapse, isCollapsed]);

  // Manejar click en item con useCallback
  const handleItemClick = useCallback((item: MenuItemData) => {
    if (onItemClick) {
      onItemClick(item);
    }
  }, [onItemClick]);

  // Memoizar clases CSS para mejor performance
  const headerClasses = useMemo(() => {
    return "w-full flex items-center justify-between px-3 py-3 text-left hover:bg-gray-50 transition-colors duration-200 rounded-md border-b border-gray-200";
  }, []);

  // Memoizar clases del chevron
  const chevronClasses = useMemo(() => {
    return `w-4 h-4 text-gray-400 transition-transform duration-200 ${
      isCollapsed ? '' : 'rotate-90'
    }`;
  }, [isCollapsed]);

  return (
    <div
      className="mb-6"
      data-testid="menu-category-container"
      style={{
        // Optimización GPU para animaciones suaves
        willChange: isCollapsed ? 'auto' : 'height',
        transform: 'translateZ(0)' // Hardware acceleration
      }}
    >
      {/* Header de la categoría optimizado */}
      <button
        type="button"
        onClick={handleHeaderClick}
        onKeyDown={handleHeaderKeyDown}
        aria-expanded={!isCollapsed}
        aria-controls={itemsId}
        aria-label={categoryAriaLabel}
        aria-describedby={`${id}-description`}
        tabIndex={0}
        role="button"
        className={`${headerClasses} focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:bg-blue-50`}
        style={{
          // Performance optimizations
          willChange: 'background-color',
          transform: 'translateZ(0)'
        }}
        data-category-index={categoryIndex}
        id={id}
      >
        {/* Descripción oculta para screen readers */}
        <span id={`${id}-description`} className="sr-only">
          {isCollapsed ? 'Presiona Enter o Space para expandir' : 'Presiona Enter o Space para contraer'}
        </span>
        <div className="flex items-center">
          <CategoryIcon
            className="w-5 h-5 mr-3 text-gray-500 transition-transform duration-150"
            data-testid={`category-icon-${icon}`}
            style={{
              // Evitar layout shifts
              minWidth: '1.25rem',
              minHeight: '1.25rem'
            }}
          />
          <span className="font-semibold text-gray-900">{title}</span>
        </div>

        <ChevronRightIcon
          className={chevronClasses}
          data-testid="chevron-icon"
          style={{
            // GPU acceleration para rotación suave
            willChange: 'transform',
            minWidth: '1rem',
            minHeight: '1rem'
          }}
        />
      </button>

      {/* Items de la categoría con lazy rendering */}
      {!isCollapsed && (
        <div
          id={itemsId}
          data-testid="menu-items-container"
          className="mt-2 space-y-1 transition-all duration-300"
          role="list"
          aria-label={`Elementos de ${title}`}
          style={{
            // Optimización para animaciones de altura
            willChange: 'height, opacity',
            transform: 'translateZ(0)'
          }}
        >
          {items.map((item, itemIndex) => (
            <div key={item.id} role="listitem">
              <MenuItem
                item={item}
                isActive={currentPath === item.href}
                onClick={handleItemClick}
                onItemClick={onItemClick}
                itemIndex={itemIndex}
                totalItems={items.length}
                categoryTitle={title}
              />
            </div>
          ))}
        </div>
      )}

      {/* Región live para anuncios de cambios de estado */}
      <div
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
        role="status"
      >
        {!isCollapsed && activeItemsCount > 0 && (
          `Categoría ${title} expandida, ${activeItemsCount} elemento${activeItemsCount !== 1 ? 's' : ''} activo${activeItemsCount !== 1 ? 's' : ''}`
        )}
      </div>
    </div>
  );
});

// Configurar display name para debugging
MenuCategory.displayName = 'MenuCategory';