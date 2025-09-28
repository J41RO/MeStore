/**
 * VendorsPage Component
 *
 * Comprehensive vendor management interface for marketplace administration.
 * Provides complete vendor lifecycle management and performance monitoring.
 *
 * Features:
 * - Advanced vendor directory with filtering and search
 * - Vendor performance metrics and analytics
 * - Vendor status management and lifecycle tracking
 * - Commission and financial overview
 * - Bulk vendor operations
 * - Vendor profile management
 * - Integration with product and order systems
 * - Compliance and document tracking
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
  Store,
  Package,
  DollarSign,
  TrendingUp,
  Users,
  Star,
  Eye,
  Edit,
  Ban,
  CheckCircle,
  X,
  Plus,
  Filter,
  Download,
  Upload,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Activity,
  AlertTriangle,
  Award,
  ShoppingCart
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
  SortConfig,
  PaginationConfig,
  BulkAction
} from '../../../components/admin/common';

/**
 * Vendor interface
 */
interface Vendor {
  id: string;
  businessName: string;
  legalName: string;
  email: string;
  phone: string;
  contactPerson: string;
  status: 'pending' | 'approved' | 'active' | 'suspended' | 'rejected' | 'under_review';
  tier: 'bronze' | 'silver' | 'gold' | 'platinum';
  joinedAt: string;
  lastActivityAt: string;
  address: {
    street: string;
    city: string;
    state: string;
    country: string;
    postalCode: string;
  };
  businessInfo: {
    category: string;
    taxId: string;
    registrationNumber: string;
    website?: string;
    description: string;
  };
  metrics: {
    totalProducts: number;
    activeProducts: number;
    totalOrders: number;
    totalRevenue: number;
    averageRating: number;
    reviewCount: number;
    conversionRate: number;
    responseTime: number; // hours
  };
  compliance: {
    documentsSubmitted: number;
    documentsApproved: number;
    taxDocuments: boolean;
    businessLicense: boolean;
    insuranceCertificate: boolean;
    complianceScore: number;
  };
  financial: {
    commissionRate: number;
    pendingPayouts: number;
    totalEarnings: number;
    lastPayoutDate?: string;
  };
}

/**
 * Vendor metrics interface
 */
interface VendorMetrics {
  totalVendors: number;
  activeVendors: number;
  pendingVendors: number;
  suspendedVendors: number;
  newVendorsThisMonth: number;
  averageRating: number;
  totalRevenue: number;
  averageCommissionRate: number;
  topPerformingVendor: string;
  complianceRate: number;
}

/**
 * VendorsPage Component
 */
export const VendorsPage: React.FC = () => {
  // State management
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [metrics, setMetrics] = useState<VendorMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedVendors, setSelectedVendors] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [activeFilters, setActiveFilters] = useState<ActiveFilter[]>([]);
  const [showVendorModal, setShowVendorModal] = useState(false);
  const [editingVendor, setEditingVendor] = useState<Vendor | null>(null);
  const [selectedVendor, setSelectedVendor] = useState<Vendor | null>(null);

  // Pagination and sorting
  const [sort, setSort] = useState<SortConfig>({ column: 'lastActivityAt', direction: 'desc' });
  const [pagination, setPagination] = useState<PaginationConfig>({
    page: 1,
    pageSize: 25,
    total: 0
  });

  /**
   * Vendor table columns
   */
  const columns: TableColumn<Vendor>[] = useMemo(() => [
    {
      id: 'vendor',
      header: 'Vendor',
      accessor: 'businessName',
      sortable: true,
      cell: (value, row) => (
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
            <Store className="w-5 h-5 text-purple-600" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center space-x-2">
              <p className="text-sm font-medium text-gray-900 truncate">{value}</p>
              {row.tier && (
                <StatusBadge
                  variant={
                    row.tier === 'platinum' ? 'premium' :
                    row.tier === 'gold' ? 'warning' :
                    row.tier === 'silver' ? 'info' : 'default'
                  }
                  size="xs"
                >
                  {row.tier.charAt(0).toUpperCase() + row.tier.slice(1)}
                </StatusBadge>
              )}
            </div>
            <div className="flex items-center space-x-4 text-xs text-gray-500">
              <span>{row.contactPerson}</span>
              <span className="flex items-center">
                <MapPin className="w-3 h-3 mr-1" />
                {row.address.city}, {row.address.country}
              </span>
            </div>
          </div>
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
            value === 'approved' ? 'info' :
            value === 'pending' || value === 'under_review' ? 'warning' :
            value === 'suspended' || value === 'rejected' ? 'error' : 'default'
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
      cell: (value, row) => (
        <div className="space-y-1">
          <div className="flex items-center space-x-1">
            <Star className="w-4 h-4 text-yellow-400 fill-current" />
            <span className="text-sm font-medium text-gray-900">
              {value.averageRating.toFixed(1)}
            </span>
            <span className="text-xs text-gray-500">({value.reviewCount})</span>
          </div>
          <div className="text-xs text-gray-500">
            {value.totalProducts} products • {value.totalOrders} orders
          </div>
          <div className="text-xs font-medium text-green-600">
            {commonComponentUtils.formatCurrency(value.totalRevenue)}
          </div>
        </div>
      )
    },
    {
      id: 'category',
      header: 'Category',
      accessor: 'businessInfo.category',
      sortable: true,
      hideOnMobile: true,
      cell: (value) => (
        <span className="text-sm text-gray-900">{value}</span>
      )
    },
    {
      id: 'compliance',
      header: 'Compliance',
      accessor: 'compliance',
      hideOnMobile: true,
      cell: (value) => (
        <div className="flex items-center space-x-2">
          <div className="w-16 bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                value.complianceScore >= 80 ? 'bg-green-500' :
                value.complianceScore >= 60 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${value.complianceScore}%` }}
            />
          </div>
          <span className="text-xs text-gray-500">{value.complianceScore}%</span>
        </div>
      )
    },
    {
      id: 'commission',
      header: 'Commission',
      accessor: 'financial.commissionRate',
      sortable: true,
      hideOnMobile: true,
      align: 'center',
      cell: (value) => (
        <span className="text-sm font-medium text-gray-900">{value}%</span>
      )
    },
    {
      id: 'joinedAt',
      header: 'Joined',
      accessor: 'joinedAt',
      sortable: true,
      hideOnMobile: true,
      cell: (value) => (
        <span className="text-sm text-gray-900">
          {commonComponentUtils.formatDate(value, 'short')}
        </span>
      )
    }
  ], []);

  /**
   * Row actions
   */
  const rowActions = useMemo(() => [
    {
      id: 'view',
      label: 'View Profile',
      icon: Eye,
      action: (vendor: Vendor) => {
        setSelectedVendor(vendor);
      }
    },
    {
      id: 'edit',
      label: 'Edit Vendor',
      icon: Edit,
      action: (vendor: Vendor) => {
        setEditingVendor(vendor);
      }
    },
    {
      id: 'approve',
      label: 'Approve Vendor',
      icon: CheckCircle,
      variant: 'success' as const,
      action: (vendor: Vendor) => {
        handleStatusChange(vendor.id, 'approved');
      },
      hidden: (vendor: Vendor) => !['pending', 'under_review'].includes(vendor.status)
    },
    {
      id: 'activate',
      label: 'Activate Vendor',
      icon: CheckCircle,
      variant: 'success' as const,
      action: (vendor: Vendor) => {
        handleStatusChange(vendor.id, 'active');
      },
      hidden: (vendor: Vendor) => vendor.status !== 'approved'
    },
    {
      id: 'suspend',
      label: 'Suspend Vendor',
      icon: Ban,
      variant: 'warning' as const,
      action: (vendor: Vendor) => {
        if (confirm(`Suspend ${vendor.businessName}?`)) {
          handleStatusChange(vendor.id, 'suspended');
        }
      },
      hidden: (vendor: Vendor) => !['active', 'approved'].includes(vendor.status)
    },
    {
      id: 'reject',
      label: 'Reject Application',
      icon: X,
      variant: 'danger' as const,
      action: (vendor: Vendor) => {
        if (confirm(`Reject ${vendor.businessName} application?`)) {
          handleStatusChange(vendor.id, 'rejected');
        }
      },
      hidden: (vendor: Vendor) => !['pending', 'under_review'].includes(vendor.status)
    }
  ], []);

  /**
   * Bulk actions
   */
  const bulkActions: BulkAction<Vendor>[] = useMemo(() => [
    {
      id: 'approve',
      label: 'Approve Vendors',
      icon: CheckCircle,
      variant: 'success',
      action: async (vendors) => {
        const vendorIds = vendors
          .filter(v => ['pending', 'under_review'].includes(v.status))
          .map(v => v.id);
        await handleBulkStatusChange(vendorIds, 'approved');
      }
    },
    {
      id: 'activate',
      label: 'Activate Vendors',
      icon: Activity,
      variant: 'success',
      action: async (vendors) => {
        const vendorIds = vendors
          .filter(v => v.status === 'approved')
          .map(v => v.id);
        await handleBulkStatusChange(vendorIds, 'active');
      }
    },
    {
      id: 'suspend',
      label: 'Suspend Vendors',
      icon: Ban,
      variant: 'warning',
      action: async (vendors) => {
        const vendorIds = vendors
          .filter(v => ['active', 'approved'].includes(v.status))
          .map(v => v.id);
        await handleBulkStatusChange(vendorIds, 'suspended');
      },
      requireConfirmation: true,
      confirmationMessage: 'Are you sure you want to suspend the selected vendors?'
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
        { value: 'pending', label: 'Pending' },
        { value: 'approved', label: 'Approved' },
        { value: 'active', label: 'Active' },
        { value: 'suspended', label: 'Suspended' },
        { value: 'rejected', label: 'Rejected' },
        { value: 'under_review', label: 'Under Review' }
      ]
    },
    {
      id: 'tier',
      label: 'Vendor Tier',
      type: 'select',
      field: 'tier',
      options: [
        { value: 'bronze', label: 'Bronze' },
        { value: 'silver', label: 'Silver' },
        { value: 'gold', label: 'Gold' },
        { value: 'platinum', label: 'Platinum' }
      ]
    },
    {
      id: 'category',
      label: 'Business Category',
      type: 'select',
      field: 'businessInfo.category',
      options: [
        { value: 'Electronics', label: 'Electronics' },
        { value: 'Fashion', label: 'Fashion' },
        { value: 'Home & Garden', label: 'Home & Garden' },
        { value: 'Sports', label: 'Sports' },
        { value: 'Books', label: 'Books' }
      ]
    },
    {
      id: 'country',
      label: 'Country',
      type: 'text',
      field: 'address.country'
    },
    {
      id: 'revenue',
      label: 'Total Revenue',
      type: 'numberrange',
      field: 'metrics.totalRevenue',
      min: 0
    },
    {
      id: 'rating',
      label: 'Average Rating',
      type: 'numberrange',
      field: 'metrics.averageRating',
      min: 0,
      max: 5,
      step: 0.1
    },
    {
      id: 'joinedAt',
      label: 'Join Date',
      type: 'daterange',
      field: 'joinedAt'
    }
  ], []);

  /**
   * Load vendors data
   */
  const loadVendors = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // TODO: Replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Mock data
      const mockVendors: Vendor[] = [
        {
          id: '1',
          businessName: 'TechStore Colombia',
          legalName: 'TechStore Colombia SAS',
          email: 'contact@techstore.co',
          phone: '+57 300 123 4567',
          contactPerson: 'Carlos Rodriguez',
          status: 'active',
          tier: 'gold',
          joinedAt: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString(),
          lastActivityAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          address: {
            street: 'Calle 100 #15-20',
            city: 'Bogotá',
            state: 'Cundinamarca',
            country: 'Colombia',
            postalCode: '110111'
          },
          businessInfo: {
            category: 'Electronics',
            taxId: '900123456-1',
            registrationNumber: 'CC-900123456',
            website: 'https://techstore.co',
            description: 'Leading electronics retailer in Colombia'
          },
          metrics: {
            totalProducts: 450,
            activeProducts: 420,
            totalOrders: 1250,
            totalRevenue: 125000000,
            averageRating: 4.7,
            reviewCount: 850,
            conversionRate: 3.2,
            responseTime: 2.5
          },
          compliance: {
            documentsSubmitted: 5,
            documentsApproved: 5,
            taxDocuments: true,
            businessLicense: true,
            insuranceCertificate: true,
            complianceScore: 100
          },
          financial: {
            commissionRate: 8.5,
            pendingPayouts: 2500000,
            totalEarnings: 10625000,
            lastPayoutDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
          }
        },
        {
          id: '2',
          businessName: 'Fashion Trends',
          legalName: 'Fashion Trends Ltda',
          email: 'info@fashiontrends.com',
          phone: '+57 301 234 5678',
          contactPerson: 'Maria Gonzalez',
          status: 'pending',
          tier: 'bronze',
          joinedAt: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
          lastActivityAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          address: {
            street: 'Av. El Dorado #68-90',
            city: 'Medellín',
            state: 'Antioquia',
            country: 'Colombia',
            postalCode: '050010'
          },
          businessInfo: {
            category: 'Fashion',
            taxId: '800234567-2',
            registrationNumber: 'CC-800234567',
            website: 'https://fashiontrends.com',
            description: 'Trendy fashion retailer for young adults'
          },
          metrics: {
            totalProducts: 0,
            activeProducts: 0,
            totalOrders: 0,
            totalRevenue: 0,
            averageRating: 0,
            reviewCount: 0,
            conversionRate: 0,
            responseTime: 0
          },
          compliance: {
            documentsSubmitted: 3,
            documentsApproved: 1,
            taxDocuments: true,
            businessLicense: false,
            insuranceCertificate: false,
            complianceScore: 60
          },
          financial: {
            commissionRate: 12.0,
            pendingPayouts: 0,
            totalEarnings: 0
          }
        },
        {
          id: '3',
          businessName: 'Home & Garden Plus',
          legalName: 'Home & Garden Plus SA',
          email: 'ventas@homegardenplus.co',
          phone: '+57 312 345 6789',
          contactPerson: 'Ana Martinez',
          status: 'active',
          tier: 'silver',
          joinedAt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(),
          lastActivityAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
          address: {
            street: 'Carrera 15 #85-40',
            city: 'Cali',
            state: 'Valle del Cauca',
            country: 'Colombia',
            postalCode: '760044'
          },
          businessInfo: {
            category: 'Home & Garden',
            taxId: '700345678-3',
            registrationNumber: 'CC-700345678',
            description: 'Home improvement and garden supplies'
          },
          metrics: {
            totalProducts: 280,
            activeProducts: 265,
            totalOrders: 680,
            totalRevenue: 45000000,
            averageRating: 4.3,
            reviewCount: 420,
            conversionRate: 2.8,
            responseTime: 4.2
          },
          compliance: {
            documentsSubmitted: 4,
            documentsApproved: 4,
            taxDocuments: true,
            businessLicense: true,
            insuranceCertificate: true,
            complianceScore: 95
          },
          financial: {
            commissionRate: 10.0,
            pendingPayouts: 850000,
            totalEarnings: 4500000,
            lastPayoutDate: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString()
          }
        }
      ];

      const mockMetrics: VendorMetrics = {
        totalVendors: mockVendors.length,
        activeVendors: mockVendors.filter(v => v.status === 'active').length,
        pendingVendors: mockVendors.filter(v => v.status === 'pending').length,
        suspendedVendors: mockVendors.filter(v => v.status === 'suspended').length,
        newVendorsThisMonth: 5,
        averageRating: 4.5,
        totalRevenue: mockVendors.reduce((sum, v) => sum + v.metrics.totalRevenue, 0),
        averageCommissionRate: 10.2,
        topPerformingVendor: 'TechStore Colombia',
        complianceRate: 85
      };

      setVendors(mockVendors);
      setMetrics(mockMetrics);
      setPagination(prev => ({ ...prev, total: mockVendors.length }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load vendors');
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Handle vendor status change
   */
  const handleStatusChange = useCallback(async (vendorId: string, newStatus: Vendor['status']) => {
    try {
      // TODO: Replace with actual API call
      setVendors(prev => prev.map(vendor =>
        vendor.id === vendorId ? { ...vendor, status: newStatus } : vendor
      ));
    } catch (err) {
      console.error('Failed to update vendor status:', err);
    }
  }, []);

  /**
   * Handle bulk status change
   */
  const handleBulkStatusChange = useCallback(async (vendorIds: string[], newStatus: Vendor['status']) => {
    try {
      // TODO: Replace with actual API call
      setVendors(prev => prev.map(vendor =>
        vendorIds.includes(vendor.id) ? { ...vendor, status: newStatus } : vendor
      ));
      setSelectedVendors([]);
    } catch (err) {
      console.error('Failed to update vendor statuses:', err);
    }
  }, []);

  /**
   * Load data on mount
   */
  useEffect(() => {
    loadVendors();
  }, [loadVendors]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Vendor Directory</h1>
          <p className="text-sm text-gray-500 mt-1">
            Manage vendor accounts, performance, and marketplace relationships
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            type="button"
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>

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
            onClick={() => setShowVendorModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Vendor
          </button>
        </div>
      </div>

      {/* Metrics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Total Vendors"
          value={metrics?.totalVendors}
          icon={Store}
          theme="primary"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Active Vendors"
          value={metrics?.activeVendors}
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
          title="Avg. Rating"
          value={metrics?.averageRating ? `${metrics.averageRating.toFixed(1)} ⭐` : undefined}
          icon={Star}
          theme="info"
          isLoading={isLoading}
          formatValue={(val) => String(val)}
        />
      </div>

      {/* Main Content Area */}
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
            data={vendors}
            columns={columns}
            isLoading={isLoading}
            error={error}
            pagination={pagination}
            sort={sort}
            selectedRows={selectedVendors}
            getRowId={(vendor) => vendor.id}
            bulkActions={bulkActions}
            rowActions={rowActions}
            searchable={true}
            searchPlaceholder="Search vendors by name, email, or category..."
            selectable={true}
            onSort={setSort}
            onPageChange={(page) => setPagination(prev => ({ ...prev, page }))}
            onPageSizeChange={(pageSize) => setPagination(prev => ({ ...prev, pageSize }))}
            onRowSelect={setSelectedVendors}
            onRefresh={loadVendors}
            emptyMessage="No vendors found. Add your first vendor to get started."
          />
        </div>
      </div>

      {/* Modals */}
      {/* Vendor Detail Modal */}
      {selectedVendor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium">{selectedVendor.businessName}</h3>
                  <p className="text-sm text-gray-500">{selectedVendor.legalName}</p>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedVendor(null)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            <div className="p-6 overflow-auto max-h-[calc(90vh-140px)]">
              <p className="text-gray-500">Vendor profile details will be implemented here.</p>
            </div>
          </div>
        </div>
      )}

      {/* Add/Edit Vendor Modal */}
      {(showVendorModal || editingVendor) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-medium mb-4">
              {editingVendor ? 'Edit Vendor' : 'Add New Vendor'}
            </h3>
            <p className="text-gray-500 mb-4">
              {editingVendor ? 'Vendor editing' : 'Vendor creation'} form will be implemented here.
            </p>
            <button
              type="button"
              onClick={() => {
                setShowVendorModal(false);
                setEditingVendor(null);
              }}
              className="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Default export
 */
export default VendorsPage;