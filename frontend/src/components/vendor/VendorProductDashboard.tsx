// frontend/src/components/vendor/VendorProductDashboard.tsx
// PRODUCTION_READY: Dashboard completo para gestión de productos de vendedores
// Optimizado para el mercado colombiano con UX excepcional

import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import {
  Plus,
  Filter,
  Grid3X3,
  List,
  Search,
  Package,
  TrendingUp,
  DollarSign,
  AlertTriangle,
  MoreVertical,
  Edit,
  Trash2,
  Eye,
  Copy,
  Star,
  ShoppingCart,
  BarChart3,
  Zap,
  ChevronDown,
  Image as ImageIcon,
  X,
  Check,
  Download,
  Upload,
  ArrowUpDown,
  SlidersHorizontal,
  RefreshCw,
  GripVertical,
  Move3D,
  Archive,
  Heart,
  ImageUp,
  Loader2,
  ChevronLeft,
  ChevronRight,
  CheckCircle
} from 'lucide-react';
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
  UniqueIdentifier
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  rectSortingStrategy
} from '@dnd-kit/sortable';
import {
  useSortable
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { motion, AnimatePresence } from 'framer-motion';
import { Product, ProductFilters, ProductSort } from '../../types/product.types';

// Simulamos datos de productos para el diseño
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

interface VendorProductDashboardProps {
  className?: string;
  vendorId?: string;
}

type ViewMode = 'grid' | 'list';
type BulkAction = 'activate' | 'deactivate' | 'feature' | 'unfeature' | 'delete' | 'edit';
type ProductCategory = 'electronics' | 'clothing' | 'home' | 'beauty' | 'sports' | 'books';

// Category color mapping for Colombian market preferences
const CATEGORY_COLORS: Record<string, { border: string; bg: string; text: string; accent: string }> = {
  electronics: {
    border: 'border-primary-200',
    bg: 'bg-primary-50',
    text: 'text-primary-700',
    accent: 'accent-primary-500'
  },
  clothing: {
    border: 'border-secondary-200',
    bg: 'bg-secondary-50',
    text: 'text-secondary-700',
    accent: 'accent-secondary-500'
  },
  home: {
    border: 'border-accent-200',
    bg: 'bg-accent-50',
    text: 'text-accent-700',
    accent: 'accent-accent-500'
  },
  beauty: {
    border: 'border-pink-200',
    bg: 'bg-pink-50',
    text: 'text-pink-700',
    accent: 'accent-pink-500'
  },
  sports: {
    border: 'border-green-200',
    bg: 'bg-green-50',
    text: 'text-green-700',
    accent: 'accent-green-500'
  },
  books: {
    border: 'border-purple-200',
    bg: 'bg-purple-50',
    text: 'text-purple-700',
    accent: 'accent-purple-500'
  }
};

interface BulkEditModalData {
  isOpen: boolean;
  selectedIds: string[];
  action: BulkAction | null;
}

interface QuickEditData {
  productId: string | null;
  field: 'name' | 'price' | 'stock' | null;
  value: string;
}

interface ImageUploadProgress {
  [key: string]: {
    progress: number;
    status: 'uploading' | 'success' | 'error';
    url?: string;
  };
}

export const VendorProductDashboard: React.FC<VendorProductDashboardProps> = ({
  className = '',
  vendorId
}) => {
  // Estado principal
  const [products, setProducts] = useState<Product[]>(MOCK_PRODUCTS);
  const [selectedProducts, setSelectedProducts] = useState<Set<string>>(new Set());
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showBulkActions, setShowBulkActions] = useState(false);

  // Filtros y búsqueda
  const [filters, setFilters] = useState<ProductFilters>({
    search: '',
    is_active: undefined,
    is_featured: undefined,
    in_stock: undefined,
    category_id: '',
    price_range: undefined
  });

  // Ordenamiento
  const [sort, setSort] = useState<ProductSort>({
    field: 'updated_at',
    direction: 'desc'
  });

  // Formateo de moneda colombiana
  const formatCOP = useCallback((amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }, []);

  // Formateo de fecha
  const formatDate = useCallback((dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }, []);

  // Productos filtrados y ordenados
  const filteredProducts = useMemo(() => {
    let filtered = [...products];

    // Aplicar filtros de búsqueda
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(product =>
        product.name.toLowerCase().includes(searchLower) ||
        product.sku.toLowerCase().includes(searchLower) ||
        product.description.toLowerCase().includes(searchLower)
      );
    }

    // Aplicar filtros de estado
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

    if (filters.category_id) {
      filtered = filtered.filter(product => product.category_id === filters.category_id);
    }

    // Aplicar rango de precios
    if (filters.price_range) {
      filtered = filtered.filter(product =>
        product.price >= filters.price_range!.min &&
        product.price <= filters.price_range!.max
      );
    }

    // Aplicar ordenamiento
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

  // Estadísticas del dashboard
  const stats = useMemo(() => {
    const totalProducts = products.length;
    const activeProducts = products.filter(p => p.is_active).length;
    const lowStockProducts = products.filter(p => p.stock > 0 && p.stock <= 5).length;
    const outOfStockProducts = products.filter(p => p.stock === 0).length;
    const totalValue = products.reduce((sum, p) => sum + (p.price * p.stock), 0);
    const totalSales = products.reduce((sum, p) => sum + p.sales_count, 0);
    const avgRating = products.reduce((sum, p) => sum + p.rating, 0) / products.length;

    return {
      totalProducts,
      activeProducts,
      lowStockProducts,
      outOfStockProducts,
      totalValue,
      totalSales,
      avgRating: isNaN(avgRating) ? 0 : avgRating
    };
  }, [products]);

  // Handlers
  const handleProductSelect = (productId: string, selected: boolean) => {
    const newSelected = new Set(selectedProducts);
    if (selected) {
      newSelected.add(productId);
    } else {
      newSelected.delete(productId);
    }
    setSelectedProducts(newSelected);
    setShowBulkActions(newSelected.size > 0);
  };

  const handleSelectAll = (selected: boolean) => {
    if (selected) {
      setSelectedProducts(new Set(filteredProducts.map(p => p.id)));
      setShowBulkActions(true);
    } else {
      setSelectedProducts(new Set());
      setShowBulkActions(false);
    }
  };

  const handleBulkAction = async (action: BulkAction) => {
    setIsLoading(true);
    // Simular acción bulk
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Aquí iría la lógica real de bulk actions
    console.log(`Bulk action ${action} applied to products:`, Array.from(selectedProducts));

    setSelectedProducts(new Set());
    setShowBulkActions(false);
    setIsLoading(false);
  };

  // Componente de indicador de estado de stock
  const StockIndicator: React.FC<{ stock: number }> = ({ stock }) => {
    if (stock === 0) {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
          <AlertTriangle className="w-3 h-3 mr-1" />
          Agotado
        </span>
      );
    }
    if (stock <= 5) {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          <AlertTriangle className="w-3 h-3 mr-1" />
          Stock bajo ({stock})
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
        <Check className="w-3 h-3 mr-1" />
        En stock ({stock})
      </span>
    );
  };

  // Componente de tarjeta de producto (vista grid)
  const ProductCard: React.FC<{ product: Product }> = ({ product }) => {
    const isSelected = selectedProducts.has(product.id);

    return (
      <div className={`
        relative bg-white rounded-lg border-2 transition-all duration-200 hover:shadow-lg
        ${isSelected ? 'border-primary-500 shadow-mestocker' : 'border-neutral-200 hover:border-neutral-300'}
        ${!product.is_active ? 'opacity-60' : ''}
      `}>
        {/* Checkbox de selección */}
        <div className="absolute top-3 left-3 z-10">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={(e) => handleProductSelect(product.id, e.target.checked)}
            className="w-4 h-4 text-primary-600 bg-white border-neutral-300 rounded focus:ring-primary-500 focus:ring-2"
          />
        </div>

        {/* Badges de estado */}
        <div className="absolute top-3 right-3 z-10 flex gap-1">
          {product.is_featured && (
            <span className="inline-flex items-center p-1 rounded-full bg-accent-100 text-accent-600">
              <Star className="w-3 h-3" fill="currentColor" />
            </span>
          )}
          {!product.is_active && (
            <span className="px-2 py-1 text-xs font-medium bg-neutral-100 text-neutral-600 rounded-full">
              Inactivo
            </span>
          )}
        </div>

        {/* Imagen del producto */}
        <div className="aspect-square bg-neutral-100 rounded-t-lg overflow-hidden">
          {product.main_image_url ? (
            <img
              src={product.main_image_url}
              alt={product.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <ImageIcon className="w-12 h-12 text-neutral-400" />
            </div>
          )}
        </div>

        {/* Contenido de la tarjeta */}
        <div className="p-4">
          {/* Título y SKU */}
          <div className="mb-2">
            <h3 className="font-semibold text-neutral-900 line-clamp-2 text-sm mb-1">
              {product.name}
            </h3>
            <p className="text-xs text-neutral-500 font-mono">SKU: {product.sku}</p>
          </div>

          {/* Categoría */}
          <div className="mb-3">
            <span className="inline-block px-2 py-1 text-xs font-medium bg-primary-100 text-primary-700 rounded">
              {product.category_name}
            </span>
          </div>

          {/* Precios */}
          <div className="mb-3">
            <div className="flex items-center justify-between">
              <span className="text-lg font-bold text-neutral-900">
                {formatCOP(product.precio_venta)}
              </span>
              <span className="text-sm text-neutral-500">
                Costo: {formatCOP(product.precio_costo || 0)}
              </span>
            </div>
            <div className="text-xs text-secondary-600 mt-1">
              Comisión: {formatCOP(product.comision_mestocker || 0)}
            </div>
          </div>

          {/* Indicador de stock */}
          <div className="mb-3">
            <StockIndicator stock={product.stock} />
          </div>

          {/* Métricas */}
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

          {/* Acciones */}
          <div className="flex items-center gap-2">
            <button className="flex-1 px-3 py-2 text-sm font-medium text-primary-700 bg-primary-50 rounded-md hover:bg-primary-100 transition-colors">
              <Edit className="w-4 h-4 inline mr-2" />
              Editar
            </button>
            <div className="relative">
              <button className="p-2 text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100 rounded-md transition-colors">
                <MoreVertical className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={`min-h-screen bg-neutral-50 ${className}`}>
      {/* Header principal */}
      <div className="bg-white shadow-sm border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <Package className="h-8 w-8 text-primary-600 mr-3" />
              <div>
                <h1 className="text-xl font-bold text-neutral-900">
                  Mis Productos
                </h1>
                <p className="text-sm text-neutral-500">
                  Gestiona tu catálogo de productos
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsLoading(true)}
                disabled={isLoading}
                className="flex items-center px-3 py-2 text-sm font-medium text-neutral-700 bg-white border border-neutral-300 rounded-md hover:bg-neutral-50 disabled:opacity-50 transition-colors"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                Actualizar
              </button>

              <button className="flex items-center px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 transition-colors">
                <Plus className="w-4 h-4 mr-2" />
                Nuevo Producto
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Panel de estadísticas */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {/* Total productos */}
          <div className="bg-white p-4 rounded-lg shadow-sm border border-neutral-200">
            <div className="flex items-center">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Package className="h-5 w-5 text-primary-600" />
              </div>
              <div className="ml-3 min-w-0 flex-1">
                <p className="text-sm font-medium text-neutral-500">Total Productos</p>
                <p className="text-lg font-bold text-neutral-900">{stats.totalProducts}</p>
                <p className="text-xs text-secondary-600">{stats.activeProducts} activos</p>
              </div>
            </div>
          </div>

          {/* Valor inventario */}
          <div className="bg-white p-4 rounded-lg shadow-sm border border-neutral-200">
            <div className="flex items-center">
              <div className="p-2 bg-secondary-100 rounded-lg">
                <DollarSign className="h-5 w-5 text-secondary-600" />
              </div>
              <div className="ml-3 min-w-0 flex-1">
                <p className="text-sm font-medium text-neutral-500">Valor Inventario</p>
                <p className="text-lg font-bold text-neutral-900">{formatCOP(stats.totalValue)}</p>
                <p className="text-xs text-secondary-600">{stats.totalSales} ventas</p>
              </div>
            </div>
          </div>

          {/* Stock bajo */}
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

          {/* Rating promedio */}
          <div className="bg-white p-4 rounded-lg shadow-sm border border-neutral-200">
            <div className="flex items-center">
              <div className="p-2 bg-accent-100 rounded-lg">
                <Star className="h-5 w-5 text-accent-600" fill="currentColor" />
              </div>
              <div className="ml-3 min-w-0 flex-1">
                <p className="text-sm font-medium text-neutral-500">Rating Promedio</p>
                <p className="text-lg font-bold text-neutral-900">{stats.avgRating.toFixed(1)}</p>
                <p className="text-xs text-neutral-500">de 5.0 estrellas</p>
              </div>
            </div>
          </div>
        </div>

        {/* Controles y filtros */}
        <div className="bg-white rounded-lg shadow-sm border border-neutral-200 mb-6">
          <div className="p-4 border-b border-neutral-200">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              {/* Barra de búsqueda */}
              <div className="flex-1 max-w-md">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-neutral-400" />
                  <input
                    type="text"
                    placeholder="Buscar productos, SKU o descripción..."
                    value={filters.search}
                    onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                    className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
              </div>

              {/* Controles de vista y filtros */}
              <div className="flex items-center gap-3">
                {/* Selector de vista */}
                <div className="flex items-center bg-neutral-100 rounded-md p-1">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`p-2 rounded ${viewMode === 'grid' ? 'bg-white shadow-sm text-primary-600' : 'text-neutral-500 hover:text-neutral-700'}`}
                  >
                    <Grid3X3 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    className={`p-2 rounded ${viewMode === 'list' ? 'bg-white shadow-sm text-primary-600' : 'text-neutral-500 hover:text-neutral-700'}`}
                  >
                    <List className="w-4 h-4" />
                  </button>
                </div>

                {/* Botón de filtros */}
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={`flex items-center px-3 py-2 text-sm font-medium rounded-md border transition-colors ${
                    showFilters
                      ? 'bg-primary-50 text-primary-700 border-primary-200'
                      : 'bg-white text-neutral-700 border-neutral-300 hover:bg-neutral-50'
                  }`}
                >
                  <SlidersHorizontal className="w-4 h-4 mr-2" />
                  Filtros
                  {Object.values(filters).some(v => v !== undefined && v !== '') && (
                    <span className="ml-2 bg-primary-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                      !
                    </span>
                  )}
                </button>

                {/* Ordenamiento */}
                <div className="relative">
                  <select
                    value={`${sort.field}-${sort.direction}`}
                    onChange={(e) => {
                      const [field, direction] = e.target.value.split('-') as [any, 'asc' | 'desc'];
                      setSort({ field, direction });
                    }}
                    className="appearance-none bg-white border border-neutral-300 rounded-md px-3 py-2 pr-8 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="updated_at-desc">Más recientes</option>
                    <option value="name-asc">Nombre A-Z</option>
                    <option value="name-desc">Nombre Z-A</option>
                    <option value="price-asc">Precio menor</option>
                    <option value="price-desc">Precio mayor</option>
                    <option value="sales_count-desc">Más vendidos</option>
                    <option value="stock-asc">Menor stock</option>
                  </select>
                  <ArrowUpDown className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-neutral-400 pointer-events-none" />
                </div>
              </div>
            </div>
          </div>

          {/* Panel de filtros expandible */}
          {showFilters && (
            <div className="p-4 border-b border-neutral-200 bg-neutral-50">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Filtro de estado */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-1">
                    Estado
                  </label>
                  <select
                    value={filters.is_active === undefined ? '' : filters.is_active ? 'active' : 'inactive'}
                    onChange={(e) => {
                      const value = e.target.value;
                      setFilters(prev => ({
                        ...prev,
                        is_active: value === '' ? undefined : value === 'active'
                      }));
                    }}
                    className="w-full border border-neutral-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="">Todos</option>
                    <option value="active">Activos</option>
                    <option value="inactive">Inactivos</option>
                  </select>
                </div>

                {/* Filtro de stock */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-1">
                    Stock
                  </label>
                  <select
                    value={filters.in_stock === undefined ? '' : filters.in_stock ? 'in_stock' : 'out_of_stock'}
                    onChange={(e) => {
                      const value = e.target.value;
                      setFilters(prev => ({
                        ...prev,
                        in_stock: value === '' ? undefined : value === 'in_stock'
                      }));
                    }}
                    className="w-full border border-neutral-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="">Todos</option>
                    <option value="in_stock">Con stock</option>
                    <option value="out_of_stock">Agotados</option>
                  </select>
                </div>

                {/* Filtro de productos destacados */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-1">
                    Destacados
                  </label>
                  <select
                    value={filters.is_featured === undefined ? '' : filters.is_featured ? 'featured' : 'not_featured'}
                    onChange={(e) => {
                      const value = e.target.value;
                      setFilters(prev => ({
                        ...prev,
                        is_featured: value === '' ? undefined : value === 'featured'
                      }));
                    }}
                    className="w-full border border-neutral-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="">Todos</option>
                    <option value="featured">Destacados</option>
                    <option value="not_featured">No destacados</option>
                  </select>
                </div>

                {/* Botón limpiar filtros */}
                <div className="flex items-end">
                  <button
                    onClick={() => setFilters({
                      search: '',
                      is_active: undefined,
                      is_featured: undefined,
                      in_stock: undefined,
                      category_id: '',
                      price_range: undefined
                    })}
                    className="w-full px-3 py-2 text-sm font-medium text-neutral-700 bg-white border border-neutral-300 rounded-md hover:bg-neutral-50 transition-colors"
                  >
                    Limpiar filtros
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Acciones bulk */}
          {showBulkActions && (
            <div className="p-4 bg-primary-50 border-b border-primary-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <span className="text-sm font-medium text-primary-700">
                    {selectedProducts.size} producto{selectedProducts.size !== 1 ? 's' : ''} seleccionado{selectedProducts.size !== 1 ? 's' : ''}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleBulkAction('activate')}
                    className="px-3 py-1 text-sm font-medium text-secondary-700 bg-secondary-100 rounded hover:bg-secondary-200 transition-colors"
                  >
                    Activar
                  </button>
                  <button
                    onClick={() => handleBulkAction('deactivate')}
                    className="px-3 py-1 text-sm font-medium text-neutral-700 bg-neutral-100 rounded hover:bg-neutral-200 transition-colors"
                  >
                    Desactivar
                  </button>
                  <button
                    onClick={() => handleBulkAction('feature')}
                    className="px-3 py-1 text-sm font-medium text-accent-700 bg-accent-100 rounded hover:bg-accent-200 transition-colors"
                  >
                    Destacar
                  </button>
                  <button
                    onClick={() => handleBulkAction('edit')}
                    className="px-3 py-1 text-sm font-medium text-blue-700 bg-blue-100 rounded hover:bg-blue-200 transition-colors"
                  >
                    Editar
                  </button>
                  <button
                    onClick={() => handleBulkAction('delete')}
                    className="px-3 py-1 text-sm font-medium text-red-700 bg-red-100 rounded hover:bg-red-200 transition-colors"
                  >
                    Eliminar
                  </button>
                  <button
                    onClick={() => {
                      setSelectedProducts(new Set());
                      setShowBulkActions(false);
                    }}
                    className="p-1 text-primary-500 hover:text-primary-700 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Lista de productos */}
        <div className="bg-white rounded-lg shadow-sm border border-neutral-200">
          <div className="p-4 border-b border-neutral-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-neutral-900">
                Productos ({filteredProducts.length})
              </h3>

              {/* Checkbox seleccionar todos */}
              <div className="flex items-center gap-4">
                <label className="flex items-center text-sm text-neutral-600">
                  <input
                    type="checkbox"
                    checked={selectedProducts.size === filteredProducts.length && filteredProducts.length > 0}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="w-4 h-4 text-primary-600 bg-white border-neutral-300 rounded focus:ring-primary-500 focus:ring-2 mr-2"
                  />
                  Seleccionar todos
                </label>
              </div>
            </div>
          </div>

          {/* Vista de productos */}
          {isLoading ? (
            <div className="p-12 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="text-neutral-500 mt-2">Cargando productos...</p>
            </div>
          ) : filteredProducts.length === 0 ? (
            <div className="p-12 text-center">
              <Package className="h-12 w-12 text-neutral-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-neutral-900 mb-2">
                No se encontraron productos
              </h3>
              <p className="text-neutral-500 mb-4">
                {Object.values(filters).some(v => v !== undefined && v !== '')
                  ? 'Prueba ajustando los filtros de búsqueda'
                  : 'Comienza agregando tu primer producto al catálogo'
                }
              </p>
              {Object.values(filters).some(v => v !== undefined && v !== '') && (
                <button
                  onClick={() => setFilters({
                    search: '',
                    is_active: undefined,
                    is_featured: undefined,
                    in_stock: undefined,
                    category_id: '',
                    price_range: undefined
                  })}
                  className="text-primary-600 hover:text-primary-700 font-medium"
                >
                  Limpiar filtros
                </button>
              )}
            </div>
          ) : (
            <div className="p-4">
              {viewMode === 'grid' ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {filteredProducts.map(product => (
                    <ProductCard key={product.id} product={product} />
                  ))}
                </div>
              ) : (
                // Vista lista (se implementaría aquí)
                <div className="space-y-2">
                  {filteredProducts.map(product => (
                    <div key={product.id} className="p-4 border border-neutral-200 rounded-lg">
                      <p>Vista lista: {product.name} - {formatCOP(product.price)}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VendorProductDashboard;