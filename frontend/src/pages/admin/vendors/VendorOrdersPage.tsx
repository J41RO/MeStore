/**
 * VendorOrdersPage Component
 *
 * Comprehensive vendor order monitoring and fulfillment management interface.
 * Provides oversight of all vendor orders and fulfillment processes.
 *
 * Features:
 * - Order tracking across all vendors
 * - Fulfillment status monitoring
 * - Shipping and delivery oversight
 * - Performance analytics per vendor
 * - Order dispute management
 * - Bulk order operations
 * - Real-time delivery tracking
 * - Customer satisfaction monitoring
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
  Truck,
  Package,
  Clock,
  CheckCircle,
  AlertTriangle,
  DollarSign,
  MapPin,
  User,
  Store,
  Calendar,
  TrendingUp,
  Filter,
  Download,
  RefreshCw,
  Eye,
  MessageSquare,
  Phone
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
  ActiveFilter
} from '../../../components/admin/common';

/**
 * Vendor order interface
 */
interface VendorOrder {
  id: string;
  orderNumber: string;
  customerId: string;
  customerName: string;
  customerEmail: string;
  vendorId: string;
  vendorName: string;
  status: 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled' | 'returned' | 'disputed';
  orderDate: string;
  expectedDelivery?: string;
  actualDelivery?: string;
  shippingAddress: {
    street: string;
    city: string;
    state: string;
    country: string;
    postalCode: string;
  };
  items: Array<{
    productId: string;
    productName: string;
    quantity: number;
    price: number;
    total: number;
  }>;
  financial: {
    subtotal: number;
    shipping: number;
    tax: number;
    total: number;
    commission: number;
    vendorPayout: number;
  };
  tracking: {
    trackingNumber?: string;
    carrier?: string;
    currentLocation?: string;
    estimatedDelivery?: string;
    deliveryAttempts: number;
  };
  fulfillment: {
    processedAt?: string;
    shippedAt?: string;
    deliveredAt?: string;
    processingTime?: number; // hours
    shippingTime?: number; // hours
  };
  communication: {
    customerMessages: number;
    vendorMessages: number;
    lastContactAt?: string;
    urgentIssues: string[];
  };
}

/**
 * Order metrics interface
 */
interface OrderMetrics {
  totalOrders: number;
  pendingOrders: number;
  shippedOrders: number;
  deliveredOrders: number;
  disputedOrders: number;
  totalRevenue: number;
  averageOrderValue: number;
  fulfillmentRate: number;
  averageProcessingTime: number;
  onTimeDeliveryRate: number;
  ordersToday: number;
  topPerformingVendor: string;
}

/**
 * VendorOrdersPage Component
 */
export const VendorOrdersPage: React.FC = () => {
  // State management
  const [orders, setOrders] = useState<VendorOrder[]>([]);
  const [metrics, setMetrics] = useState<OrderMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedOrders, setSelectedOrders] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [activeFilters, setActiveFilters] = useState<ActiveFilter[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<VendorOrder | null>(null);

  /**
   * Order table columns
   */
  const columns: TableColumn<VendorOrder>[] = useMemo(() => [
    {
      id: 'order',
      header: 'Order',
      accessor: 'orderNumber',
      sortable: true,
      cell: (value, row) => (
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <Package className="w-5 h-5 text-blue-600" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-gray-900">{value}</p>
            <p className="text-sm text-gray-500">{row.customerName}</p>
            <p className="text-xs text-gray-400">
              {row.items.length} item{row.items.length > 1 ? 's' : ''}
            </p>
          </div>
        </div>
      )
    },
    {
      id: 'vendor',
      header: 'Vendor',
      accessor: 'vendorName',
      sortable: true,
      cell: (value) => (
        <div className="flex items-center space-x-2">
          <Store className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-900">{value}</span>
        </div>
      )
    },
    {
      id: 'status',
      header: 'Status',
      accessor: 'status',
      sortable: true,
      cell: (value, row) => (
        <div className="space-y-1">
          <StatusBadge
            variant={
              value === 'delivered' ? 'success' :
              value === 'shipped' ? 'info' :
              value === 'processing' || value === 'confirmed' ? 'warning' :
              value === 'cancelled' || value === 'returned' || value === 'disputed' ? 'error' : 'pending'
            }
            size="sm"
          >
            {value.charAt(0).toUpperCase() + value.slice(1)}
          </StatusBadge>
          {row.tracking.trackingNumber && (
            <div className="text-xs text-gray-500">
              {row.tracking.carrier}: {row.tracking.trackingNumber.slice(-6)}
            </div>
          )}
        </div>
      )
    },
    {
      id: 'total',
      header: 'Total',
      accessor: 'financial.total',
      sortable: true,
      align: 'right',
      cell: (value) => (
        <span className="text-sm font-medium text-gray-900">
          {commonComponentUtils.formatCurrency(value)}
        </span>
      )
    },
    {
      id: 'shipping',
      header: 'Shipping',
      accessor: 'shippingAddress',
      hideOnMobile: true,
      cell: (value, row) => (
        <div className="space-y-1">
          <div className="flex items-center space-x-1">
            <MapPin className="w-3 h-3 text-gray-400" />
            <span className="text-sm text-gray-900">{value.city}</span>
          </div>
          {row.expectedDelivery && (
            <div className="text-xs text-gray-500">
              ETA: {new Date(row.expectedDelivery).toLocaleDateString()}
            </div>
          )}
        </div>
      )
    },
    {
      id: 'timeline',
      header: 'Timeline',
      accessor: 'orderDate',
      sortable: true,
      hideOnMobile: true,
      cell: (value, row) => (
        <div className="space-y-1">
          <div className="text-sm text-gray-900">
            Ordered: {commonComponentUtils.getRelativeTime(value)}
          </div>
          {row.fulfillment.shippedAt && (
            <div className="text-xs text-gray-500">
              Shipped: {commonComponentUtils.getRelativeTime(row.fulfillment.shippedAt)}
            </div>
          )}
          {row.fulfillment.deliveredAt && (
            <div className="text-xs text-green-600">
              Delivered: {commonComponentUtils.getRelativeTime(row.fulfillment.deliveredAt)}
            </div>
          )}
        </div>
      )
    },
    {
      id: 'issues',
      header: 'Issues',
      accessor: 'communication',
      hideOnMobile: true,
      cell: (value) => (
        <div className="flex items-center space-x-2">
          {value.urgentIssues.length > 0 && (
            <div className="flex items-center space-x-1">
              <AlertTriangle className="w-4 h-4 text-red-500" />
              <span className="text-xs text-red-600">{value.urgentIssues.length}</span>
            </div>
          )}
          {value.customerMessages > 0 && (
            <div className="flex items-center space-x-1">
              <MessageSquare className="w-4 h-4 text-blue-500" />
              <span className="text-xs text-blue-600">{value.customerMessages}</span>
            </div>
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
      label: 'View Details',
      icon: Eye,
      action: (order: VendorOrder) => {
        setSelectedOrder(order);
      }
    },
    {
      id: 'contact',
      label: 'Contact Customer',
      icon: Phone,
      action: (order: VendorOrder) => {
        console.log('Contact customer:', order.customerEmail);
      }
    },
    {
      id: 'track',
      label: 'Track Package',
      icon: Truck,
      action: (order: VendorOrder) => {
        if (order.tracking.trackingNumber) {
          console.log('Track package:', order.tracking.trackingNumber);
        }
      },
      hidden: (order: VendorOrder) => !order.tracking.trackingNumber
    }
  ], []);

  /**
   * Filter definitions
   */
  const filterDefinitions: FilterDefinition[] = useMemo(() => [
    {
      id: 'status',
      label: 'Order Status',
      type: 'select',
      field: 'status',
      options: [
        { value: 'pending', label: 'Pending' },
        { value: 'confirmed', label: 'Confirmed' },
        { value: 'processing', label: 'Processing' },
        { value: 'shipped', label: 'Shipped' },
        { value: 'delivered', label: 'Delivered' },
        { value: 'cancelled', label: 'Cancelled' },
        { value: 'returned', label: 'Returned' },
        { value: 'disputed', label: 'Disputed' }
      ]
    },
    {
      id: 'vendor',
      label: 'Vendor',
      type: 'text',
      field: 'vendorName'
    },
    {
      id: 'customer',
      label: 'Customer',
      type: 'text',
      field: 'customerName'
    },
    {
      id: 'total',
      label: 'Order Total',
      type: 'numberrange',
      field: 'financial.total',
      min: 0
    },
    {
      id: 'city',
      label: 'Delivery City',
      type: 'text',
      field: 'shippingAddress.city'
    },
    {
      id: 'orderDate',
      label: 'Order Date',
      type: 'daterange',
      field: 'orderDate'
    },
    {
      id: 'hasIssues',
      label: 'Has Issues',
      type: 'boolean',
      field: 'communication.urgentIssues'
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
      const mockOrders: VendorOrder[] = [
        {
          id: '1',
          orderNumber: 'ORD-2024-001234',
          customerId: 'cust1',
          customerName: 'Ana Rodriguez',
          customerEmail: 'ana.rodriguez@email.com',
          vendorId: 'vendor1',
          vendorName: 'TechStore Colombia',
          status: 'shipped',
          orderDate: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          expectedDelivery: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toISOString(),
          shippingAddress: {
            street: 'Calle 85 #15-20 Apt 501',
            city: 'Bogotá',
            state: 'Cundinamarca',
            country: 'Colombia',
            postalCode: '110221'
          },
          items: [
            {
              productId: 'prod1',
              productName: 'Samsung Galaxy A54 128GB',
              quantity: 1,
              price: 899000,
              total: 899000
            }
          ],
          financial: {
            subtotal: 899000,
            shipping: 25000,
            tax: 133860,
            total: 1057860,
            commission: 76450,
            vendorPayout: 981410
          },
          tracking: {
            trackingNumber: 'TRK123456789',
            carrier: 'Servientrega',
            currentLocation: 'Centro de distribución Bogotá',
            deliveryAttempts: 0
          },
          fulfillment: {
            processedAt: new Date(Date.now() - 36 * 60 * 60 * 1000).toISOString(),
            shippedAt: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
            processingTime: 24,
            shippingTime: 12
          },
          communication: {
            customerMessages: 0,
            vendorMessages: 1,
            urgentIssues: []
          }
        },
        {
          id: '2',
          orderNumber: 'ORD-2024-001235',
          customerId: 'cust2',
          customerName: 'Carlos Gomez',
          customerEmail: 'carlos.gomez@email.com',
          vendorId: 'vendor2',
          vendorName: 'Home & Garden Plus',
          status: 'disputed',
          orderDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          expectedDelivery: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          actualDelivery: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
          shippingAddress: {
            street: 'Carrera 45 #78-90',
            city: 'Medellín',
            state: 'Antioquia',
            country: 'Colombia',
            postalCode: '050021'
          },
          items: [
            {
              productId: 'prod2',
              productName: 'Garden Tool Set',
              quantity: 1,
              price: 145000,
              total: 145000
            },
            {
              productId: 'prod3',
              productName: 'Plant Fertilizer 2kg',
              quantity: 2,
              price: 35000,
              total: 70000
            }
          ],
          financial: {
            subtotal: 215000,
            shipping: 15000,
            tax: 34200,
            total: 264200,
            commission: 21500,
            vendorPayout: 242700
          },
          tracking: {
            trackingNumber: 'TRK987654321',
            carrier: 'Coordinadora',
            currentLocation: 'Entregado',
            deliveryAttempts: 2
          },
          fulfillment: {
            processedAt: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(),
            shippedAt: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
            deliveredAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
            processingTime: 48,
            shippingTime: 72
          },
          communication: {
            customerMessages: 3,
            vendorMessages: 2,
            lastContactAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
            urgentIssues: ['Damaged items', 'Refund requested']
          }
        }
      ];

      const mockMetrics: OrderMetrics = {
        totalOrders: mockOrders.length,
        pendingOrders: mockOrders.filter(o => ['pending', 'confirmed'].includes(o.status)).length,
        shippedOrders: mockOrders.filter(o => o.status === 'shipped').length,
        deliveredOrders: mockOrders.filter(o => o.status === 'delivered').length,
        disputedOrders: mockOrders.filter(o => o.status === 'disputed').length,
        totalRevenue: mockOrders.reduce((sum, o) => sum + o.financial.total, 0),
        averageOrderValue: mockOrders.reduce((sum, o) => sum + o.financial.total, 0) / mockOrders.length,
        fulfillmentRate: 85,
        averageProcessingTime: 36,
        onTimeDeliveryRate: 92,
        ordersToday: 5,
        topPerformingVendor: 'TechStore Colombia'
      };

      setOrders(mockOrders);
      setMetrics(mockMetrics);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load order data');
    } finally {
      setIsLoading(false);
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
          <h1 className="text-2xl font-bold text-gray-900">Vendor Orders</h1>
          <p className="text-sm text-gray-500 mt-1">
            Monitor and manage vendor order fulfillment
          </p>
        </div>

        <div className="flex items-center space-x-3">
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

          <button
            type="button"
            onClick={loadData}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      {/* Metrics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Total Orders"
          value={metrics?.totalOrders}
          icon={Package}
          theme="primary"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Fulfillment Rate"
          value={metrics ? `${metrics.fulfillmentRate}%` : undefined}
          icon={CheckCircle}
          theme="success"
          isLoading={isLoading}
          formatValue={(val) => String(val)}
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
          title="Orders Today"
          value={metrics?.ordersToday}
          icon={Calendar}
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
            data={orders}
            columns={columns}
            isLoading={isLoading}
            error={error}
            selectedRows={selectedOrders}
            getRowId={(order) => order.id}
            rowActions={rowActions}
            searchable={true}
            searchPlaceholder="Search orders by number, customer, or vendor..."
            selectable={false}
            onRowSelect={setSelectedOrders}
            onRefresh={loadData}
            emptyMessage="No orders found."
          />
        </div>
      </div>

      {/* Order Detail Modal */}
      {selectedOrder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium">{selectedOrder.orderNumber}</h3>
                  <p className="text-sm text-gray-500">Order Details</p>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedOrder(null)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  ×
                </button>
              </div>
            </div>
            <div className="p-6 overflow-auto max-h-[calc(90vh-140px)]">
              <p className="text-gray-500">Order details interface will be implemented here.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Default export
 */
export default VendorOrdersPage;