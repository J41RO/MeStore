/**
 * VendorProductsPage Component
 *
 * Comprehensive vendor product catalog management interface.
 * Provides oversight and control over all vendor products in the marketplace.
 *
 * Features:
 * - Product catalog overview across all vendors
 * - Product approval and quality control
 * - Inventory monitoring and alerts
 * - Pricing oversight and recommendations
 * - Product performance analytics
 * - Category management and optimization
 * - Bulk product operations
 * - Compliance and policy enforcement
 *
 * @version 1.0.0
 * @author UX Specialist AI
 */

import React, {
  useState,
  useCallback,
  useMemo,
  useEffect
} from 'react';
import {
  Package,
  Store,
  DollarSign,
  TrendingUp,
  Eye,
  Edit,
  Ban,
  CheckCircle,
  AlertTriangle,
  Star,
  ShoppingCart,
  BarChart3,
  Filter,
  Download,
  Search,
  Grid,
  List,
  Calendar,
  Tag,
  Image
} from 'lucide-react';

import {
  DashboardCard,
  DataTable,
  StatusBadge,
  FilterPanel,
  commonComponentUtils
} from '../../../components/admin/common';

import type {
  TableColumn,
  FilterDefinition,
  ActiveFilter,
  BulkAction
} from '../../../components/admin/common';

/**
 * Vendor product interface
 */
interface VendorProduct {
  id: string;
  name: string;
  sku: string;
  vendorId: string;
  vendorName: string;
  category: string;
  subcategory: string;
  price: number;
  originalPrice?: number;
  currency: string;
  stock: number;
  status: 'active' | 'inactive' | 'pending_approval' | 'rejected' | 'out_of_stock' | 'discontinued';
  createdAt: string;
  updatedAt: string;
  lastSoldAt?: string;
  images: string[];
  description: string;
  specifications: Record<string, string>;
  metrics: {
    views: number;
    sales: number;
    revenue: number;
    rating: number;
    reviewCount: number;
    conversionRate: number;
    returnRate: number;
  };
  compliance: {
    approved: boolean;
    qualityScore: number;
    policyViolations: string[];
    lastReviewedAt?: string;
  };
}

/**
 * Product metrics interface
 */
interface ProductMetrics {
  totalProducts: number;
  activeProducts: number;
  pendingProducts: number;
  outOfStockProducts: number;
  totalRevenue: number;
  averagePrice: number;
  topSellingProduct: string;
  averageRating: number;
  totalSales: number;
  newProductsToday: number;
}

/**
 * VendorProductsPage Component
 */
export const VendorProductsPage: React.FC = () => {
  // State management
  const [products, setProducts] = useState<VendorProduct[]>([]);
  const [metrics, setMetrics] = useState<ProductMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedProducts, setSelectedProducts] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [activeFilters, setActiveFilters] = useState<ActiveFilter[]>([]);
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table');

  /**
   * Product table columns
   */
  const columns: TableColumn<VendorProduct>[] = useMemo(() => [
    {
      id: 'product',
      header: 'Product',
      accessor: 'name',
      sortable: true,
      cell: (value, row) => (
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gray-200 rounded-lg flex items-center justify-center">
            {row.images.length > 0 ? (
              <img src={row.images[0]} alt={value} className="w-10 h-10 object-cover rounded-lg" />
            ) : (
              <Package className="w-5 h-5 text-gray-400" />
            )}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">{value}</p>
            <p className="text-sm text-gray-500 truncate">SKU: {row.sku}</p>
            <p className="text-xs text-gray-400">{row.vendorName}</p>
          </div>
        </div>
      )
    },
    {
      id: 'category',
      header: 'Category',
      accessor: 'category',
      sortable: true,
      cell: (value, row) => (
        <div className="space-y-1">
          <span className="text-sm text-gray-900">{value}</span>
          <div className="text-xs text-gray-500">{row.subcategory}</div>
        </div>
      )
    },
    {
      id: 'price',
      header: 'Price',
      accessor: 'price',
      sortable: true,
      align: 'right',
      cell: (value, row) => (
        <div className="text-right">
          <div className="text-sm font-medium text-gray-900">
            {commonComponentUtils.formatCurrency(value)}
          </div>
          {row.originalPrice && row.originalPrice > value && (
            <div className="text-xs text-gray-500 line-through">
              {commonComponentUtils.formatCurrency(row.originalPrice)}
            </div>
          )}
        </div>
      )
    },
    {
      id: 'stock',
      header: 'Stock',
      accessor: 'stock',
      sortable: true,
      align: 'center',
      cell: (value) => (
        <div className="text-center">
          <span className={`text-sm font-medium ${
            value <= 0 ? 'text-red-600' :
            value <= 10 ? 'text-orange-600' : 'text-gray-900'
          }`}>
            {value}
          </span>
        </div>
      )
    },
    {
      id: 'status',
      header: 'Status',
      accessor: 'status',
      sortable: true,
      cell: (value) => (
        <StatusBadge
          variant={
            value === 'active' ? 'success' :
            value === 'pending_approval' ? 'warning' :
            value === 'rejected' ? 'error' :
            value === 'out_of_stock' ? 'inactive' :
            value === 'discontinued' ? 'error' : 'default'
          }
          size="sm"
        >
          {value.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
        </StatusBadge>
      )
    },
    {
      id: 'performance',
      header: 'Performance',
      accessor: 'metrics',
      hideOnMobile: true,
      cell: (value) => (
        <div className="space-y-1">
          <div className="flex items-center space-x-1">
            <Star className="w-3 h-3 text-yellow-400 fill-current" />
            <span className="text-sm text-gray-900">{value.rating.toFixed(1)}</span>
            <span className="text-xs text-gray-500">({value.reviewCount})</span>
          </div>
          <div className="text-xs text-gray-500">
            {value.sales} sales • {value.views} views
          </div>
          <div className="text-xs font-medium text-green-600">
            {commonComponentUtils.formatCurrency(value.revenue)}
          </div>
        </div>
      )
    },
    {
      id: 'compliance',
      header: 'Quality',
      accessor: 'compliance',
      hideOnMobile: true,
      cell: (value) => (
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${value.approved ? 'bg-green-500' : 'bg-yellow-500'}`} />
          <span className="text-sm text-gray-900">{value.qualityScore}%</span>
          {value.policyViolations.length > 0 && (
            <AlertTriangle className="w-4 h-4 text-orange-500" title="Policy violations" />
          )}
        </div>
      )
    }
  ], []);

  /**
   * Row actions
   */
  const rowActions = useMemo(() => [
    {
      id: 'view',
      label: 'View Product',
      icon: Eye,
      action: (product: VendorProduct) => {
        console.log('View product:', product.id);
      }
    },
    {
      id: 'approve',
      label: 'Approve Product',
      icon: CheckCircle,
      variant: 'success' as const,
      action: (product: VendorProduct) => {
        handleStatusChange(product.id, 'active');
      },
      hidden: (product: VendorProduct) => product.status !== 'pending_approval'
    },
    {
      id: 'reject',
      label: 'Reject Product',
      icon: Ban,
      variant: 'danger' as const,
      action: (product: VendorProduct) => {
        if (confirm(`Reject ${product.name}?`)) {
          handleStatusChange(product.id, 'rejected');
        }
      },
      hidden: (product: VendorProduct) => !['pending_approval', 'active'].includes(product.status)
    }
  ], []);

  /**
   * Bulk actions
   */
  const bulkActions: BulkAction<VendorProduct>[] = useMemo(() => [
    {
      id: 'approve',
      label: 'Approve Products',
      icon: CheckCircle,
      variant: 'success',
      action: async (products) => {
        const productIds = products
          .filter(p => p.status === 'pending_approval')
          .map(p => p.id);
        await handleBulkStatusChange(productIds, 'active');
      }
    },
    {
      id: 'deactivate',
      label: 'Deactivate Products',
      icon: Ban,
      variant: 'warning',
      action: async (products) => {
        const productIds = products
          .filter(p => p.status === 'active')
          .map(p => p.id);
        await handleBulkStatusChange(productIds, 'inactive');
      }
    }
  ], []);

  /**
   * Filter definitions
   */
  const filterDefinitions: FilterDefinition[] = useMemo(() => [
    {
      id: 'status',
      label: 'Status',
      type: 'select',
      field: 'status',
      options: [
        { value: 'active', label: 'Active' },
        { value: 'inactive', label: 'Inactive' },
        { value: 'pending_approval', label: 'Pending Approval' },
        { value: 'rejected', label: 'Rejected' },
        { value: 'out_of_stock', label: 'Out of Stock' },
        { value: 'discontinued', label: 'Discontinued' }
      ]
    },
    {
      id: 'category',
      label: 'Category',
      type: 'select',
      field: 'category',
      options: [
        { value: 'Electronics', label: 'Electronics' },
        { value: 'Fashion', label: 'Fashion' },
        { value: 'Home & Garden', label: 'Home & Garden' },
        { value: 'Sports', label: 'Sports' },
        { value: 'Books', label: 'Books' }
      ]
    },
    {
      id: 'vendor',
      label: 'Vendor',
      type: 'text',
      field: 'vendorName'
    },
    {
      id: 'price',
      label: 'Price Range',
      type: 'numberrange',
      field: 'price',
      min: 0
    },
    {
      id: 'stock',
      label: 'Stock Level',
      type: 'numberrange',
      field: 'stock',
      min: 0
    },
    {
      id: 'rating',
      label: 'Rating',
      type: 'numberrange',
      field: 'metrics.rating',
      min: 0,
      max: 5,
      step: 0.1
    }
  ], []);

  /**
   * Load data
   */
  const loadData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // TODO: Replace with actual API calls
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Mock data
      const mockProducts: VendorProduct[] = [
        {
          id: '1',
          name: 'Samsung Galaxy A54 128GB',
          sku: 'TECH-SAMSUNG-A54-128',
          vendorId: 'vendor1',
          vendorName: 'TechStore Colombia',
          category: 'Electronics',
          subcategory: 'Smartphones',
          price: 899000,
          originalPrice: 999000,
          currency: 'COP',
          stock: 25,
          status: 'active',
          createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
          updatedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          lastSoldAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
          images: ['/images/samsung-a54.jpg'],
          description: 'Latest Samsung Galaxy A54 with excellent camera and battery life',
          specifications: {
            'Storage': '128GB',
            'RAM': '6GB',
            'Camera': '50MP + 12MP + 5MP',
            'Battery': '5000mAh'
          },
          metrics: {
            views: 1250,
            sales: 45,
            revenue: 40455000,
            rating: 4.6,
            reviewCount: 32,
            conversionRate: 3.6,
            returnRate: 1.2
          },
          compliance: {
            approved: true,
            qualityScore: 95,
            policyViolations: [],
            lastReviewedAt: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString()
          }
        },
        {
          id: '2',
          name: 'Wireless Bluetooth Headphones',
          sku: 'TECH-AUDIO-WBH-001',
          vendorId: 'vendor1',
          vendorName: 'TechStore Colombia',
          category: 'Electronics',
          subcategory: 'Audio',
          price: 129000,
          currency: 'COP',
          stock: 0,
          status: 'out_of_stock',
          createdAt: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString(),
          updatedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
          lastSoldAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          images: ['/images/bluetooth-headphones.jpg'],
          description: 'High-quality wireless headphones with noise cancellation',
          specifications: {
            'Battery Life': '30 hours',
            'Connectivity': 'Bluetooth 5.0',
            'Noise Cancellation': 'Active',
            'Weight': '250g'
          },
          metrics: {
            views: 850,
            sales: 78,
            revenue: 10062000,
            rating: 4.4,
            reviewCount: 56,
            conversionRate: 9.2,
            returnRate: 2.1
          },
          compliance: {
            approved: true,
            qualityScore: 88,
            policyViolations: [],
            lastReviewedAt: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString()
          }
        },
        {
          id: '3',
          name: 'Designer Summer Dress',
          sku: 'FASH-DRESS-SUM-001',
          vendorId: 'vendor2',
          vendorName: 'Fashion Trends',
          category: 'Fashion',
          subcategory: 'Dresses',
          price: 89000,
          currency: 'COP',
          stock: 15,
          status: 'pending_approval',
          createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
          updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
          images: ['/images/summer-dress.jpg'],
          description: 'Elegant summer dress perfect for casual and formal occasions',
          specifications: {
            'Material': '100% Cotton',
            'Sizes': 'S, M, L, XL',
            'Care': 'Machine washable',
            'Origin': 'Colombia'
          },
          metrics: {
            views: 45,
            sales: 0,
            revenue: 0,
            rating: 0,
            reviewCount: 0,
            conversionRate: 0,
            returnRate: 0
          },
          compliance: {
            approved: false,
            qualityScore: 75,
            policyViolations: ['Missing size chart'],
            lastReviewedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
          }
        }
      ];

      const mockMetrics: ProductMetrics = {
        totalProducts: mockProducts.length,
        activeProducts: mockProducts.filter(p => p.status === 'active').length,
        pendingProducts: mockProducts.filter(p => p.status === 'pending_approval').length,
        outOfStockProducts: mockProducts.filter(p => p.status === 'out_of_stock').length,
        totalRevenue: mockProducts.reduce((sum, p) => sum + p.metrics.revenue, 0),
        averagePrice: mockProducts.reduce((sum, p) => sum + p.price, 0) / mockProducts.length,
        topSellingProduct: 'Wireless Bluetooth Headphones',
        averageRating: 4.5,
        totalSales: mockProducts.reduce((sum, p) => sum + p.metrics.sales, 0),
        newProductsToday: 2
      };

      setProducts(mockProducts);
      setMetrics(mockMetrics);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load product data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Handle status change
   */
  const handleStatusChange = useCallback(async (productId: string, newStatus: VendorProduct['status']) => {
    try {
      // TODO: Replace with actual API call
      setProducts(prev => prev.map(product =>
        product.id === productId ? { ...product, status: newStatus } : product
      ));
    } catch (err) {
      console.error('Failed to update product status:', err);
    }
  }, []);

  /**
   * Handle bulk status change
   */
  const handleBulkStatusChange = useCallback(async (productIds: string[], newStatus: VendorProduct['status']) => {
    try {
      // TODO: Replace with actual API call
      setProducts(prev => prev.map(product =>
        productIds.includes(product.id) ? { ...product, status: newStatus } : product
      ));
      setSelectedProducts([]);
    } catch (err) {
      console.error('Failed to update product statuses:', err);
    }
  }, []);

  /**
   * Load data on mount
   */
  useEffect(() => {
    loadData();
  }, [loadData]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Product Catalog</h1>
          <p className="text-sm text-gray-500 mt-1">
            Manage vendor products and inventory oversight
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {/* View Toggle */}
          <div className="flex items-center bg-gray-100 rounded-lg p-1">
            <button
              type="button"
              onClick={() => setViewMode('table')}
              className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                viewMode === 'table'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <List className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={() => setViewMode('grid')}
              className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                viewMode === 'grid'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Grid className="w-4 h-4" />
            </button>
          </div>

          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </button>

          <button
            type="button"
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Metrics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Total Products"
          value={metrics?.totalProducts}
          icon={Package}
          theme="primary"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Active Products"
          value={metrics?.activeProducts}
          icon={CheckCircle}
          theme="success"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Total Revenue"
          value={metrics ? commonComponentUtils.formatCurrency(metrics.totalRevenue) : undefined}
          icon={DollarSign}
          theme="warning"
          isLoading={isLoading}
          formatValue={(val) => String(val)}
        />
        <DashboardCard
          title="Total Sales"
          value={metrics?.totalSales}
          icon={ShoppingCart}
          theme="info"
          isLoading={isLoading}
        />
      </div>

      {/* Main Content */}
      <div className="flex gap-6">
        {/* Filter Panel */}
        {showFilters && (
          <div className="w-80">
            <FilterPanel
              filterDefinitions={filterDefinitions}
              activeFilters={activeFilters}
              isOpen={showFilters}
              onFiltersChange={setActiveFilters}
              onClose={() => setShowFilters(false)}
            />
          </div>
        )}

        {/* Data Table */}
        <div className="flex-1">
          <DataTable
            data={products}
            columns={columns}
            isLoading={isLoading}
            error={error}
            selectedRows={selectedProducts}
            getRowId={(product) => product.id}
            bulkActions={bulkActions}
            rowActions={rowActions}
            searchable={true}
            searchPlaceholder="Search products by name, SKU, or vendor..."
            selectable={true}
            onRowSelect={setSelectedProducts}
            onRefresh={loadData}
            emptyMessage="No products found."
          />
        </div>
      </div>
    </div>
  );
};

/**
 * Default export
 */
export default VendorProductsPage;