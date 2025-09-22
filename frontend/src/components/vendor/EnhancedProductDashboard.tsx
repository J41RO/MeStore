/**
 * Enhanced Product Management Dashboard with Drag & Drop UX
 * Colombian Market Optimized Design System
 * TDD-Compliant Implementation with 60fps Performance
 */

import React, { useState, useCallback, useMemo, useRef, useEffect } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
  DragStartEvent,
  DragOverlay,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  rectSortingStrategy,
} from '@dnd-kit/sortable';
import {
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { motion, AnimatePresence } from 'framer-motion';
import {
  GripVertical,
  Edit,
  ImageUp,
  Star,
  Package,
  CheckCircle,
  X,
  Eye,
  ShoppingCart,
  AlertTriangle,
  Check,
  Trash2,
  Search,
  Filter,
  Grid3X3,
  List,
  Plus,
  RefreshCw,
  SlidersHorizontal,
  ArrowUpDown,
  DollarSign,
  TrendingUp,
  Loader2,
} from 'lucide-react';

// Import Colombian design system and accessibility utilities
import { useAccessibleDragDrop } from '../../hooks/useAccessibleDragDrop';
import { screenReader, focusManagement, touchAccessibility, aria, reducedMotion } from '../../utils/accessibility';

// Import Colombian design system
import {
  getProductCategoryStyle,
  formatColombianCurrency,
  formatColombianDate,
  SPACING,
  ANIMATIONS,
  ACCESSIBILITY
} from '../../utils/colombianDesignSystem';

// Types
interface Product {
  id: string;
  vendor_id: string;
  sku: string;
  name: string;
  description: string;
  price: number;
  stock: number;
  category_id: string;
  category_name: string;
  precio_venta: number;
  precio_costo?: number;
  comision_mestocker?: number;
  peso?: number;
  is_active: boolean;
  is_featured: boolean;
  is_digital: boolean;
  images: string[];
  main_image_url?: string;
  sales_count: number;
  view_count: number;
  rating: number;
  review_count: number;
  created_at: string;
  updated_at: string;
}

interface ProductFilters {
  search: string;
  is_active?: boolean;
  is_featured?: boolean;
  in_stock?: boolean;
  category_id: string;
  price_range?: { min: number; max: number };
}

interface ProductSort {
  field: keyof Product;
  direction: 'asc' | 'desc';
}

type ViewMode = 'grid' | 'list';
type BulkAction = 'activate' | 'deactivate' | 'feature' | 'unfeature' | 'delete' | 'edit';

// Mock data optimized for Colombian market
const MOCK_PRODUCTS: Product[] = [
  {
    id: '1',
    vendor_id: 'vendor-1',
    sku: 'TECH-001',
    name: 'Smartphone Samsung Galaxy A54',
    description: 'Smartphone con cámara de 50MP, 128GB almacenamiento y pantalla AMOLED de 6.4"',
    price: 899000,
    stock: 25,
    category_id: 'electronics',
    category_name: 'Electrónicos',
    precio_venta: 899000,
    precio_costo: 650000,
    comision_mestocker: 44950,
    peso: 202,
    is_active: true,
    is_featured: true,
    is_digital: false,
    images: [],
    main_image_url: '/api/placeholder/300/300',
    sales_count: 45,
    view_count: 320,
    rating: 4.5,
    review_count: 12,
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-20T15:30:00Z'
  },
  {
    id: '2',
    vendor_id: 'vendor-1',
    sku: 'FASH-002',
    name: 'Camiseta Polo Lacoste Original',
    description: 'Camiseta polo 100% algodón, disponible en múltiples colores',
    price: 189000,
    stock: 8,
    category_id: 'clothing',
    category_name: 'Ropa',
    precio_venta: 189000,
    precio_costo: 120000,
    comision_mestocker: 9450,
    peso: 180,
    is_active: true,
    is_featured: false,
    is_digital: false,
    images: [],
    main_image_url: '/api/placeholder/300/300',
    sales_count: 23,
    view_count: 156,
    rating: 4.8,
    review_count: 8,
    created_at: '2024-01-10T08:00:00Z',
    updated_at: '2024-01-18T12:15:00Z'
  },
  {
    id: '3',
    vendor_id: 'vendor-1',
    sku: 'HOME-003',
    name: 'Cafetera Oster 12 Tazas',
    description: 'Cafetera automática programable con jarra de vidrio y filtro permanente',
    price: 245000,
    stock: 0,
    category_id: 'home',
    category_name: 'Hogar',
    precio_venta: 245000,
    precio_costo: 180000,
    comision_mestocker: 12250,
    peso: 2200,
    is_active: false,
    is_featured: false,
    is_digital: false,
    images: [],
    main_image_url: '/api/placeholder/300/300',
    sales_count: 12,
    view_count: 89,
    rating: 4.2,
    review_count: 5,
    created_at: '2024-01-05T14:00:00Z',
    updated_at: '2024-01-22T09:45:00Z'
  }
];

// Enhanced Product Card with Drag & Drop
const SortableProductCard: React.FC<{ product: Product; isSelected: boolean; onSelect: (id: string, selected: boolean) => void }> = ({
  product,
  isSelected,
  onSelect
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: product.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    zIndex: isDragging ? 1000 : 1,
  };

  const categoryStyle = getProductCategoryStyle(product.category_id);

  const StockIndicator = () => {
    if (product.stock === 0) {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
          <AlertTriangle className="w-3 h-3 mr-1" />
          Agotado
        </span>
      );
    }
    if (product.stock <= 5) {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          <AlertTriangle className="w-3 h-3 mr-1" />
          Stock bajo ({product.stock})
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
        <Check className="w-3 h-3 mr-1" />
        En stock ({product.stock})
      </span>
    );
  };

  return (
    <div ref={setNodeRef} style={style} data-testid={`draggable-${product.id}`}>
      <motion.div
        layout
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.2 }}
        className={`
          relative bg-white rounded-lg border-2 transition-all duration-200 hover:shadow-lg group
          ${isSelected ? `border-primary-500 shadow-mestocker ${categoryStyle.bg}` : `${categoryStyle.border} hover:border-neutral-300`}
          ${!product.is_active ? 'opacity-60' : ''}
          ${isDragging ? 'opacity-50 rotate-1 scale-105' : ''}
          ${ACCESSIBILITY.motion.reduce}
        `}
        data-testid={`product-card-${product.id}`}
      >
        {/* Drag Handle */}
        <div
          {...attributes}
          {...listeners}
          className="absolute top-2 left-2 z-20 p-2 opacity-0 group-hover:opacity-100 transition-opacity cursor-grab active:cursor-grabbing bg-white/90 backdrop-blur-sm rounded-full shadow-sm hover:bg-white"
          style={{ minWidth: '44px', minHeight: '44px' }}
          aria-label={`Arrastra producto ${product.name} para reordenar`}
          title="Arrastra para reordenar"
        >
          <GripVertical className="w-4 h-4 text-neutral-600" />
        </div>

        {/* Selection Checkbox - Touch Friendly */}
        <div className="absolute top-3 right-3 z-10">
          <label className="flex items-center justify-center w-11 h-11 cursor-pointer">
            <input
              type="checkbox"
              checked={isSelected}
              onChange={(e) => onSelect(product.id, e.target.checked)}
              className="w-5 h-5 text-primary-600 bg-white border-neutral-300 rounded focus:ring-primary-500 focus:ring-2"
              aria-label={`Seleccionar producto ${product.name}`}
            />
          </label>
        </div>

        {/* Status Badges */}
        <div className="absolute top-14 right-3 z-10 flex flex-col gap-1">
          {product.is_featured && (
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="inline-flex items-center p-1.5 rounded-full bg-accent-100 text-accent-600 shadow-sm"
            >
              <Star className="w-3 h-3" fill="currentColor" />
            </motion.span>
          )}
          {!product.is_active && (
            <span className="px-2 py-1 text-xs font-medium bg-neutral-100 text-neutral-600 rounded-full">
              Inactivo
            </span>
          )}
        </div>

        {/* Product Image */}
        <div className="aspect-square bg-neutral-100 rounded-t-lg overflow-hidden">
          {product.main_image_url ? (
            <img
              src={product.main_image_url}
              alt={product.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Package className="w-12 h-12 text-neutral-400" />
            </div>
          )}
        </div>

        {/* Product Content */}
        <div className="p-4">
          {/* Title and SKU */}
          <div className="mb-2">
            <h3 className="font-semibold text-neutral-900 line-clamp-2 text-sm mb-1">
              {product.name}
            </h3>
            <p className="text-xs text-neutral-500 font-mono">SKU: {product.sku}</p>
          </div>

          {/* Category with Color Coding */}
          <div className="mb-3">
            <span className={`inline-block px-2 py-1 text-xs font-medium rounded ${categoryStyle.bg} ${categoryStyle.text}`}>
              {product.category_name}
            </span>
          </div>

          {/* Pricing */}
          <div className="mb-3">
            <div className="flex items-center justify-between">
              <span className="text-lg font-bold text-neutral-900">
                {formatColombianCurrency(product.precio_venta)}
              </span>
              <span className="text-sm text-neutral-500">
                Costo: {formatColombianCurrency(product.precio_costo || 0)}
              </span>
            </div>
            <div className="text-xs text-secondary-600 mt-1">
              Comisión: {formatColombianCurrency(product.comision_mestocker || 0)}
            </div>
          </div>

          {/* Stock Indicator */}
          <div className="mb-3">
            <StockIndicator />
          </div>

          {/* Metrics */}
          <div className="flex items-center justify-between text-xs text-neutral-500 mb-4">
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1">
                <ShoppingCart className="w-3 h-3" />
                {product.sales_count}
              </span>
              <span className="flex items-center gap-1">
                <Eye className="w-3 h-3" />
                {product.view_count}
              </span>
              <span className="flex items-center gap-1">
                <Star className="w-3 h-3" fill="currentColor" />
                {product.rating.toFixed(1)}
              </span>
            </div>
          </div>

          {/* Actions - Touch Friendly */}
          <div className="flex items-center gap-2">
            <button
              className="flex-1 px-3 py-2 text-sm font-medium text-primary-700 bg-primary-50 rounded-md hover:bg-primary-100 transition-colors"
              style={{ minHeight: '44px' }}
            >
              <Edit className="w-4 h-4 inline mr-2" />
              Editar
            </button>
            <button
              className="p-2 text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100 rounded-md transition-colors"
              style={{ minWidth: '44px', minHeight: '44px' }}
              title="Subir imágenes"
            >
              <ImageUp className="w-4 h-4" />
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

// Main Dashboard Component
interface EnhancedProductDashboardProps {
  className?: string;
  vendorId?: string;
}

export const EnhancedProductDashboard: React.FC<EnhancedProductDashboardProps> = ({
  className = '',
  vendorId
}) => {
  // State
  const [products, setProducts] = useState<Product[]>(MOCK_PRODUCTS);
  const mainRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const [announcements, setAnnouncements] = useState<string[]>([]);
  const [selectedProducts, setSelectedProducts] = useState<Set<string>>(new Set());
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [activeId, setActiveId] = useState<string | null>(null);

  // Accessibility announcements
  const announceChange = useCallback((message: string) => {
    screenReader.announce(message, 'polite');
    setAnnouncements(prev => [...prev.slice(-4), message]);
  }, []);

  // Filters
  const [filters, setFilters] = useState<ProductFilters>({
    search: '',
    is_active: undefined,
    is_featured: undefined,
    in_stock: undefined,
    category_id: '',
    price_range: undefined
  });

  // Sorting
  const [sort, setSort] = useState<ProductSort>({
    field: 'updated_at',
    direction: 'desc'
  });

  // Filtered and sorted products (moved before use in accessibleDragDrop)
  const filteredProducts = useMemo(() => {
    let filtered = [...products];

    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(product =>
        product.name.toLowerCase().includes(searchLower) ||
        product.sku.toLowerCase().includes(searchLower) ||
        product.description.toLowerCase().includes(searchLower)
      );
    }

    if (filters.is_active !== undefined) {
      filtered = filtered.filter(product => product.is_active === filters.is_active);
    }

    if (filters.is_featured !== undefined) {
      filtered = filtered.filter(product => product.is_featured === filters.is_featured);
    }

    if (filters.in_stock !== undefined) {
      filtered = filtered.filter(product =>
        filters.in_stock ? product.stock > 0 : product.stock === 0
      );
    }

    // Sort products
    filtered.sort((a, b) => {
      const aValue = a[sort.field];
      const bValue = b[sort.field];

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sort.direction === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }

      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sort.direction === 'asc'
          ? aValue - bValue
          : bValue - aValue;
      }

      return 0;
    });

    return filtered;
  }, [products, filters, sort]);

  // Accessible drag & drop
  const accessibleDragDrop = useAccessibleDragDrop({
    items: filteredProducts,
    getId: (product) => product.id,
    onReorder: (reorderedProducts) => {
      setProducts(reorderedProducts);
      announceChange(`Productos reordenados. ${reorderedProducts.length} productos en la lista.`);
    },
    announceMove: (product, from, to) =>
      `${product.name} movido desde posición ${from + 1} a posición ${to + 1}`,
    announceStart: (product) =>
      `Iniciando arrastre de ${product.name}`,
    announceEnd: (product) =>
      `Finalizando arrastre de ${product.name}`
  });

  // Drag & Drop sensors with accessibility enhancements
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Stats
  const stats = useMemo(() => {
    const totalProducts = products.length;
    const activeProducts = products.filter(p => p.is_active).length;
    const lowStockProducts = products.filter(p => p.stock > 0 && p.stock <= 5).length;
    const outOfStockProducts = products.filter(p => p.stock === 0).length;
    const totalValue = products.reduce((sum, p) => sum + (p.price * p.stock), 0);
    const totalSales = products.reduce((sum, p) => sum + p.sales_count, 0);

    return {
      totalProducts,
      activeProducts,
      lowStockProducts,
      outOfStockProducts,
      totalValue,
      totalSales
    };
  }, [products]);

  // Focus management
  useEffect(() => {
    if (mainRef.current) {
      mainRef.current.focus();
      announceChange('Dashboard de productos cargado. Use Tab para navegar entre controles.');
    }
  }, [announceChange]);

  // Handlers
  const handleDragStart = useCallback((event: DragStartEvent) => {
    setActiveId(event.active.id as string);
    accessibleDragDrop.handleDragStart(
      filteredProducts.findIndex(p => p.id === event.active.id)
    );
  }, [accessibleDragDrop, filteredProducts]);

  const handleDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);
    accessibleDragDrop.handleDragEnd();

    if (over && active.id !== over.id) {
      const oldIndex = filteredProducts.findIndex((item) => item.id === active.id);
      const newIndex = filteredProducts.findIndex((item) => item.id === over.id);

      setProducts((prevProducts) => {
        const reordered = arrayMove(prevProducts, oldIndex, newIndex);
        accessibleDragDrop.handleDrop(oldIndex, newIndex);
        return reordered;
      });
    }
  }, [accessibleDragDrop, filteredProducts]);

  const handleProductSelect = useCallback((productId: string, selected: boolean) => {
    const newSelected = new Set(selectedProducts);
    if (selected) {
      newSelected.add(productId);
    } else {
      newSelected.delete(productId);
    }
    setSelectedProducts(newSelected);
  }, [selectedProducts]);

  const handleSelectAll = useCallback((selected: boolean) => {
    if (selected) {
      setSelectedProducts(new Set(filteredProducts.map(p => p.id)));
    } else {
      setSelectedProducts(new Set());
    }
  }, [filteredProducts]);

  const handleBulkAction = useCallback(async (action: BulkAction) => {
    setIsLoading(true);
    announceChange(`Aplicando acción ${action} a ${selectedProducts.size} productos...`);

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));

    setProducts(prevProducts =>
      prevProducts.map(product => {
        if (selectedProducts.has(product.id)) {
          switch (action) {
            case 'activate':
              return { ...product, is_active: true };
            case 'deactivate':
              return { ...product, is_active: false };
            case 'feature':
              return { ...product, is_featured: true };
            case 'unfeature':
              return { ...product, is_featured: false };
            case 'delete':
              return null;
            default:
              return product;
          }
        }
        return product;
      }).filter(Boolean) as Product[]
    );

    setSelectedProducts(new Set());
    setIsLoading(false);
    announceChange(`Acción ${action} completada exitosamente.`);
  }, [selectedProducts, announceChange]);

  return (
    <div
      ref={mainRef}
      className={`min-h-screen bg-neutral-50 ${className}`}
      data-testid="enhanced-product-dashboard"
      tabIndex={-1}
    >
      {/* Live region for announcements */}
      <div
        className="sr-only"
        aria-live="polite"
        aria-atomic="false"
        id="dashboard-announcements"
      >
        {announcements.map((announcement, index) => (
          <div key={index}>{announcement}</div>
        ))}
      </div>

      {/* Skip link */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-primary-600 text-white px-4 py-2 rounded z-50"
      >
        Saltar al contenido principal
      </a>
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <Package className="h-8 w-8 text-primary-600 mr-3" aria-hidden="true" />
              <div>
                <h1
                  id="main-heading"
                  className="text-xl font-bold text-neutral-900"
                >
                  Gestión Avanzada de Productos
                </h1>
                <p
                  id="main-description"
                  className="text-sm text-neutral-500"
                >
                  Dashboard con funciones de arrastrar y soltar accesibles por teclado
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3" role="toolbar" aria-label="Acciones principales">
              <button
                onClick={() => {
                  setIsLoading(true);
                  announceChange('Actualizando lista de productos...');
                }}
                disabled={isLoading}
                className="flex items-center px-3 py-2 text-sm font-medium text-neutral-700 bg-white border border-neutral-300 rounded-md hover:bg-neutral-50 disabled:opacity-50 transition-colors focus:ring-2 focus:ring-primary-500"
                style={{ minHeight: '44px' }}
                aria-describedby="refresh-help"
              >
                <RefreshCw
                  className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`}
                  aria-hidden="true"
                />
                {isLoading ? 'Actualizando...' : 'Actualizar'}
              </button>
              <div id="refresh-help" className="sr-only">
                Actualiza la lista de productos con los datos más recientes
              </div>

              <button
                className="flex items-center px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 transition-colors focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
                style={{ minHeight: '44px' }}
                aria-describedby="new-product-help"
              >
                <Plus className="w-4 h-4 mr-2" aria-hidden="true" />
                Nuevo Producto
              </button>
              <div id="new-product-help" className="sr-only">
                Abre el formulario para crear un nuevo producto
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main id="main-content" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Stats Dashboard */}
        <section
          className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6"
          aria-labelledby="stats-heading"
        >
          <h2 id="stats-heading" className="sr-only">Estadísticas de productos</h2>
          <article className="bg-white p-4 rounded-lg shadow-sm border border-neutral-200">
            <div className="flex items-center">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Package className="h-5 w-5 text-primary-600" aria-hidden="true" />
              </div>
              <div className="ml-3 min-w-0 flex-1">
                <h3 className="text-sm font-medium text-neutral-500">Total Productos</h3>
                <p className="text-lg font-bold text-neutral-900" aria-describedby="total-products-desc">
                  {stats.totalProducts}
                </p>
                <p id="total-products-desc" className="text-xs text-secondary-600">
                  {stats.activeProducts} productos activos
                </p>
              </div>
            </div>
          </article>

          <div className="bg-white p-4 rounded-lg shadow-sm border border-neutral-200">
            <div className="flex items-center">
              <div className="p-2 bg-secondary-100 rounded-lg">
                <DollarSign className="h-5 w-5 text-secondary-600" />
              </div>
              <div className="ml-3 min-w-0 flex-1">
                <p className="text-sm font-medium text-neutral-500">Valor Inventario</p>
                <p className="text-lg font-bold text-neutral-900">{formatColombianCurrency(stats.totalValue)}</p>
                <p className="text-xs text-secondary-600">{stats.totalSales} ventas</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow-sm border border-neutral-200">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
              </div>
              <div className="ml-3 min-w-0 flex-1">
                <p className="text-sm font-medium text-neutral-500">Stock Bajo</p>
                <p className="text-lg font-bold text-neutral-900">{stats.lowStockProducts}</p>
                <p className="text-xs text-red-600">{stats.outOfStockProducts} agotados</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow-sm border border-neutral-200">
            <div className="flex items-center">
              <div className="p-2 bg-accent-100 rounded-lg">
                <TrendingUp className="h-5 w-5 text-accent-600" />
              </div>
              <div className="ml-3 min-w-0 flex-1">
                <p className="text-sm font-medium text-neutral-500">Rendimiento</p>
                <p className="text-lg font-bold text-neutral-900">+15%</p>
                <p className="text-xs text-neutral-500">vs mes anterior</p>
              </div>
            </div>
          </div>
        </section>

        {/* Controls */}
        <section className="bg-white rounded-lg shadow-sm border border-neutral-200 mb-6">
          <div className="p-4 border-b border-neutral-200">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              {/* Search */}
              <div className="flex-1 max-w-md">
                <label htmlFor="product-search" className="sr-only">
                  Buscar productos por nombre, SKU o descripción
                </label>
                <div className="relative">
                  <Search
                    className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-neutral-400"
                    aria-hidden="true"
                  />
                  <input
                    ref={searchInputRef}
                    id="product-search"
                    type="text"
                    placeholder="Buscar productos, SKU o descripción..."
                    value={filters.search}
                    onChange={(e) => {
                      setFilters(prev => ({ ...prev, search: e.target.value }));
                      if (e.target.value) {
                        announceChange(`Buscando: ${e.target.value}`);
                      }
                    }}
                    className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    style={{ minHeight: '44px' }}
                    aria-describedby="search-help"
                  />
                </div>
                <div id="search-help" className="sr-only">
                  Escribe para filtrar la lista de productos en tiempo real
                </div>
              </div>

              {/* View Controls */}
              <div className="flex items-center gap-3">
                <fieldset className="flex items-center bg-neutral-100 rounded-md p-1">
                  <legend className="sr-only">Modo de vista de productos</legend>
                  <button
                    onClick={() => {
                      setViewMode('grid');
                      announceChange('Vista cambiada a cuadrícula');
                    }}
                    className={`p-2 rounded ${viewMode === 'grid' ? 'bg-white shadow-sm text-primary-600' : 'text-neutral-500 hover:text-neutral-700'}`}
                    style={{ minWidth: '44px', minHeight: '44px' }}
                    aria-pressed={viewMode === 'grid'}
                    aria-label="Vista en cuadrícula"
                  >
                    <Grid3X3 className="w-4 h-4" aria-hidden="true" />
                  </button>
                  <button
                    onClick={() => {
                      setViewMode('list');
                      announceChange('Vista cambiada a lista');
                    }}
                    className={`p-2 rounded ${viewMode === 'list' ? 'bg-white shadow-sm text-primary-600' : 'text-neutral-500 hover:text-neutral-700'}`}
                    style={{ minWidth: '44px', minHeight: '44px' }}
                    aria-pressed={viewMode === 'list'}
                    aria-label="Vista en lista"
                  >
                    <List className="w-4 h-4" aria-hidden="true" />
                  </button>
                </fieldset>

                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={`flex items-center px-3 py-2 text-sm font-medium rounded-md border transition-colors ${
                    showFilters
                      ? 'bg-primary-50 text-primary-700 border-primary-200'
                      : 'bg-white text-neutral-700 border-neutral-300 hover:bg-neutral-50'
                  }`}
                  style={{ minHeight: '44px' }}
                >
                  <SlidersHorizontal className="w-4 h-4 mr-2" />
                  Filtros
                </button>

                <label htmlFor="sort-select" className="sr-only">
                  Ordenar productos por
                </label>
                <select
                  id="sort-select"
                  value={`${sort.field}-${sort.direction}`}
                  onChange={(e) => {
                    const [field, direction] = e.target.value.split('-') as [keyof Product, 'asc' | 'desc'];
                    setSort({ field, direction });
                    const sortText = {
                      'updated_at-desc': 'más recientes',
                      'name-asc': 'nombre A-Z',
                      'price-asc': 'precio menor',
                      'price-desc': 'precio mayor',
                      'sales_count-desc': 'más vendidos'
                    }[e.target.value] || 'fecha';
                    announceChange(`Productos ordenados por ${sortText}`);
                  }}
                  className="appearance-none bg-white border border-neutral-300 rounded-md px-3 py-2 pr-8 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  style={{ minHeight: '44px' }}
                  aria-describedby="sort-help"
                >
                  <option value="updated_at-desc">Más recientes</option>
                  <option value="name-asc">Nombre A-Z</option>
                  <option value="price-asc">Precio menor</option>
                  <option value="price-desc">Precio mayor</option>
                  <option value="sales_count-desc">Más vendidos</option>
                </select>
                <div id="sort-help" className="sr-only">
                  Cambia el criterio de ordenamiento de la lista de productos
                </div>
              </div>
            </div>
          </div>

          {/* Bulk Actions */}
          {selectedProducts.size > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="p-4 bg-primary-50 border-b border-primary-200"
              data-testid="bulk-actions-toolbar"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-primary-700">
                  {selectedProducts.size} producto{selectedProducts.size !== 1 ? 's' : ''} seleccionado{selectedProducts.size !== 1 ? 's' : ''}
                </span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleBulkAction('activate')}
                    className="px-3 py-1 text-sm font-medium text-secondary-700 bg-secondary-100 rounded hover:bg-secondary-200 transition-colors"
                    style={{ minHeight: '44px' }}
                  >
                    Activar
                  </button>
                  <button
                    onClick={() => handleBulkAction('feature')}
                    className="px-3 py-1 text-sm font-medium text-accent-700 bg-accent-100 rounded hover:bg-accent-200 transition-colors"
                    style={{ minHeight: '44px' }}
                  >
                    Destacar
                  </button>
                  <button
                    onClick={() => handleBulkAction('delete')}
                    className="px-3 py-1 text-sm font-medium text-red-700 bg-red-100 rounded hover:bg-red-200 transition-colors"
                    style={{ minHeight: '44px' }}
                  >
                    Eliminar
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </section>

        {/* Products Grid with Drag & Drop */}
        <section className="bg-white rounded-lg shadow-sm border border-neutral-200">
          <div className="p-4 border-b border-neutral-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-neutral-900">
                Productos ({filteredProducts.length})
              </h3>

              <div className="flex items-center" style={{ minHeight: '44px' }}>
                <input
                  id="select-all"
                  type="checkbox"
                  checked={selectedProducts.size === filteredProducts.length && filteredProducts.length > 0}
                  onChange={(e) => {
                    handleSelectAll(e.target.checked);
                    announceChange(
                      e.target.checked
                        ? `${filteredProducts.length} productos seleccionados`
                        : 'Selección eliminada de todos los productos'
                    );
                  }}
                  className="w-5 h-5 text-primary-600 bg-white border-neutral-300 rounded focus:ring-primary-500 focus:ring-2 mr-3"
                  aria-describedby="select-all-help"
                />
                <label htmlFor="select-all" className="text-sm text-neutral-600 cursor-pointer">
                  Seleccionar todos ({filteredProducts.length})
                </label>
                <div id="select-all-help" className="sr-only">
                  Selecciona o deselecciona todos los productos visibles en la lista actual
                </div>
              </div>
            </div>

            {filteredProducts.length > 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-2 text-xs text-neutral-500 flex items-center gap-2"
              >
                <GripVertical className="w-3 h-3" />
                Arrastra los productos para reordenar tu catálogo
              </motion.div>
            )}
          </div>

          {/* Drag & Drop Instructions */}
          <accessibleDragDrop.Instructions />

          {/* Products Content */}
          <div
            className="p-4"
            data-testid="products-grid"
            {...accessibleDragDrop.containerProps}
          >
            {isLoading ? (
              <div className="p-12 text-center">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"
                />
                <p className="text-neutral-500 mt-2">Cargando productos...</p>
              </div>
            ) : filteredProducts.length === 0 ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-12 text-center"
              >
                <Package className="h-12 w-12 text-neutral-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-neutral-900 mb-2">
                  No se encontraron productos
                </h3>
                <p className="text-neutral-500 mb-4">
                  Comienza agregando tu primer producto al catálogo
                </p>
              </motion.div>
            ) : (
              <DndContext
                sensors={sensors}
                collisionDetection={closestCenter}
                onDragStart={handleDragStart}
                onDragEnd={handleDragEnd}
                accessibility={{
                  announcements: {
                    onDragStart: ({ active }) => {
                      const product = filteredProducts.find(p => p.id === active.id);
                      return `Arrastrando ${product?.name}. Use las teclas de flecha para mover.`;
                    },
                    onDragOver: ({ active, over }) => {
                      if (over) {
                        const activeProduct = filteredProducts.find(p => p.id === active.id);
                        const overProduct = filteredProducts.find(p => p.id === over.id);
                        return `${activeProduct?.name} encima de ${overProduct?.name}`;
                      }
                      return '';
                    },
                    onDragEnd: ({ active, over }) => {
                      const product = filteredProducts.find(p => p.id === active.id);
                      if (over && active.id !== over.id) {
                        return `${product?.name} movido exitosamente`;
                      }
                      return `${product?.name} regresado a su posición original`;
                    },
                  }
                }}
              >
                <SortableContext
                  items={filteredProducts.map(p => p.id)}
                  strategy={rectSortingStrategy}
                >
                  <motion.div
                    layout
                    className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
                    role="grid"
                    aria-label={`Cuadrícula de productos con ${filteredProducts.length} elementos`}
                  >
                    <AnimatePresence>
                      {filteredProducts.map((product, index) => (
                        <div
                          key={product.id}
                          role="gridcell"
                          {...accessibleDragDrop.getItemProps(product, index)}
                        >
                          <SortableProductCard
                            product={product}
                            isSelected={selectedProducts.has(product.id)}
                            onSelect={handleProductSelect}
                          />
                        </div>
                      ))}
                    </AnimatePresence>
                  </motion.div>
                </SortableContext>

                <DragOverlay>
                  {activeId ? (
                    <div className="opacity-80">
                      <SortableProductCard
                        product={filteredProducts.find(p => p.id === activeId)!}
                        isSelected={false}
                        onSelect={() => {}}
                      />
                    </div>
                  ) : null}
                </DragOverlay>
              </DndContext>
            )}
          </div>
        </section>
      </main>
    </div>
  );
};

export default EnhancedProductDashboard;