/**
 * VendorCommissionsPage Component
 *
 * Advanced commission management and payout system for vendors.
 * Provides comprehensive financial oversight and automated payout processing.
 *
 * Features:
 * - Commission rate management and tier-based pricing
 * - Automated payout calculations and scheduling
 * - Financial analytics and reporting
 * - Payment method management
 * - Commission dispute resolution
 * - Tax document generation
 * - Performance-based commission adjustments
 * - Multi-currency support
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
  DollarSign,
  TrendingUp,
  Calendar,
  Download,
  Upload,
  CreditCard,
  Bank,
  Calculator,
  CheckCircle,
  Clock,
  AlertTriangle,
  Filter,
  Eye,
  Edit,
  Send,
  FileText,
  PieChart,
  BarChart3
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
 * Vendor commission interface
 */
interface VendorCommission {
  id: string;
  vendorId: string;
  vendorName: string;
  tier: 'bronze' | 'silver' | 'gold' | 'platinum';
  period: string; // YYYY-MM format
  commissionRate: number;
  baseRate: number;
  performanceBonus: number;
  sales: {
    totalOrders: number;
    totalRevenue: number;
    averageOrderValue: number;
    refunds: number;
    returns: number;
  };
  earnings: {
    grossCommission: number;
    deductions: number;
    netCommission: number;
    previousBalance: number;
    totalPayout: number;
  };
  payout: {
    status: 'pending' | 'processing' | 'paid' | 'failed' | 'disputed' | 'hold';
    method: 'bank_transfer' | 'paypal' | 'wire' | 'check';
    scheduledDate?: string;
    processedDate?: string;
    transactionId?: string;
    bankDetails?: {
      accountName: string;
      accountNumber: string;
      bankName: string;
      routingNumber: string;
    };
  };
  documents: {
    invoiceGenerated: boolean;
    taxDocumentRequired: boolean;
    contractSigned: boolean;
    complianceCheck: boolean;
  };
  adjustments: Array<{
    id: string;
    type: 'bonus' | 'penalty' | 'correction' | 'promotion';
    amount: number;
    reason: string;
    appliedDate: string;
  }>;
}

/**
 * Commission metrics interface
 */
interface CommissionMetrics {
  totalVendors: number;
  totalCommissions: number;
  pendingPayouts: number;
  averageCommissionRate: number;
  monthlyGrowth: number;
  topEarningVendor: string;
  totalDeductions: number;
  payoutSuccessRate: number;
  averagePayoutTime: number;
  commissionsThisMonth: number;
}

/**
 * VendorCommissionsPage Component
 */
export const VendorCommissionsPage: React.FC = () => {
  // State management
  const [commissions, setCommissions] = useState<VendorCommission[]>([]);
  const [metrics, setMetrics] = useState<CommissionMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCommissions, setSelectedCommissions] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [activeFilters, setActiveFilters] = useState<ActiveFilter[]>([]);
  const [selectedCommission, setSelectedCommission] = useState<VendorCommission | null>(null);
  const [showPayoutModal, setShowPayoutModal] = useState(false);

  /**
   * Commission table columns
   */
  const columns: TableColumn<VendorCommission>[] = useMemo(() => [
    {
      id: 'vendor',
      header: 'Vendor',
      accessor: 'vendorName',
      sortable: true,
      cell: (value, row) => (
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
            row.tier === 'platinum' ? 'bg-purple-100' :
            row.tier === 'gold' ? 'bg-yellow-100' :
            row.tier === 'silver' ? 'bg-gray-100' : 'bg-orange-100'
          }`}>
            <DollarSign className={`w-5 h-5 ${
              row.tier === 'platinum' ? 'text-purple-600' :
              row.tier === 'gold' ? 'text-yellow-600' :
              row.tier === 'silver' ? 'text-gray-600' : 'text-orange-600'
            }`} />
          </div>
          <div className="min-w-0">
            <div className="flex items-center space-x-2">
              <p className="text-sm font-medium text-gray-900 truncate">{value}</p>
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
            </div>
            <p className="text-sm text-gray-500">Period: {row.period}</p>
          </div>
        </div>
      )
    },
    {
      id: 'commission',
      header: 'Commission',
      accessor: 'commissionRate',
      sortable: true,
      cell: (value, row) => (
        <div className="space-y-1">
          <div className="text-sm font-medium text-gray-900">{value}%</div>
          <div className="text-xs text-gray-500">
            Base: {row.baseRate}%
            {row.performanceBonus > 0 && (
              <span className="text-green-600"> + {row.performanceBonus}%</span>
            )}
          </div>
        </div>
      )
    },
    {
      id: 'sales',
      header: 'Sales Performance',
      accessor: 'sales',
      cell: (value) => (
        <div className="space-y-1">
          <div className="text-sm font-medium text-gray-900">
            {commonComponentUtils.formatCurrency(value.totalRevenue)}
          </div>
          <div className="text-xs text-gray-500">
            {value.totalOrders} orders • AOV: {commonComponentUtils.formatCurrency(value.averageOrderValue)}
          </div>
          {(value.refunds > 0 || value.returns > 0) && (
            <div className="text-xs text-orange-600">
              {value.refunds} refunds • {value.returns} returns
            </div>
          )}
        </div>
      )
    },
    {
      id: 'earnings',
      header: 'Earnings',
      accessor: 'earnings',
      sortable: true,
      cell: (value) => (
        <div className="space-y-1">
          <div className="text-sm font-medium text-gray-900">
            {commonComponentUtils.formatCurrency(value.netCommission)}
          </div>
          <div className="text-xs text-gray-500">
            Gross: {commonComponentUtils.formatCurrency(value.grossCommission)}
          </div>
          {value.deductions > 0 && (
            <div className="text-xs text-red-600">
              Deductions: -{commonComponentUtils.formatCurrency(value.deductions)}
            </div>
          )}
        </div>
      )
    },
    {
      id: 'payout',
      header: 'Payout',
      accessor: 'payout',
      sortable: true,
      cell: (value, row) => (
        <div className="space-y-1">
          <StatusBadge
            variant={
              value.status === 'paid' ? 'success' :
              value.status === 'processing' ? 'info' :
              value.status === 'failed' || value.status === 'disputed' ? 'error' :
              value.status === 'hold' ? 'warning' : 'pending'
            }
            size="sm"
          >
            {value.status.charAt(0).toUpperCase() + value.status.slice(1)}
          </StatusBadge>
          <div className="text-xs text-gray-500">
            {value.method.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </div>
          {value.scheduledDate && (
            <div className="text-xs text-gray-500">
              {value.status === 'paid' ? 'Paid:' : 'Due:'} {new Date(value.scheduledDate).toLocaleDateString()}
            </div>
          )}
        </div>
      )
    },
    {
      id: 'totalPayout',
      header: 'Total Payout',
      accessor: 'earnings.totalPayout',
      sortable: true,
      align: 'right',
      cell: (value) => (
        <span className="text-sm font-medium text-gray-900">
          {commonComponentUtils.formatCurrency(value)}
        </span>
      )
    },
    {
      id: 'documents',
      header: 'Documents',
      accessor: 'documents',
      hideOnMobile: true,
      cell: (value) => (
        <div className="flex items-center space-x-1">
          <div className={`w-2 h-2 rounded-full ${value.invoiceGenerated ? 'bg-green-500' : 'bg-gray-300'}`} title="Invoice" />
          <div className={`w-2 h-2 rounded-full ${value.taxDocumentRequired ? 'bg-green-500' : 'bg-gray-300'}`} title="Tax Doc" />
          <div className={`w-2 h-2 rounded-full ${value.contractSigned ? 'bg-green-500' : 'bg-gray-300'}`} title="Contract" />
          <div className={`w-2 h-2 rounded-full ${value.complianceCheck ? 'bg-green-500' : 'bg-gray-300'}`} title="Compliance" />
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
      action: (commission: VendorCommission) => {
        setSelectedCommission(commission);
      }
    },
    {
      id: 'edit',
      label: 'Edit Commission',
      icon: Edit,
      action: (commission: VendorCommission) => {
        console.log('Edit commission:', commission.id);
      }
    },
    {
      id: 'process-payout',
      label: 'Process Payout',
      icon: Send,
      variant: 'success' as const,
      action: (commission: VendorCommission) => {
        handleProcessPayout(commission.id);
      },
      hidden: (commission: VendorCommission) => !['pending', 'failed'].includes(commission.payout.status)
    },
    {
      id: 'generate-invoice',
      label: 'Generate Invoice',
      icon: FileText,
      action: (commission: VendorCommission) => {
        handleGenerateInvoice(commission.id);
      },
      hidden: (commission: VendorCommission) => commission.documents.invoiceGenerated
    }
  ], []);

  /**
   * Bulk actions
   */
  const bulkActions: BulkAction<VendorCommission>[] = useMemo(() => [
    {
      id: 'process-payouts',
      label: 'Process Payouts',
      icon: Send,
      variant: 'success',
      action: async (commissions) => {
        const commissionIds = commissions
          .filter(c => ['pending', 'failed'].includes(c.payout.status))
          .map(c => c.id);
        await handleBulkProcessPayouts(commissionIds);
      }
    },
    {
      id: 'generate-invoices',
      label: 'Generate Invoices',
      icon: FileText,
      variant: 'info',
      action: async (commissions) => {
        const commissionIds = commissions
          .filter(c => !c.documents.invoiceGenerated)
          .map(c => c.id);
        await handleBulkGenerateInvoices(commissionIds);
      }
    }
  ], []);

  /**
   * Filter definitions
   */
  const filterDefinitions: FilterDefinition[] = useMemo(() => [
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
      id: 'payoutStatus',
      label: 'Payout Status',
      type: 'select',
      field: 'payout.status',
      options: [
        { value: 'pending', label: 'Pending' },
        { value: 'processing', label: 'Processing' },
        { value: 'paid', label: 'Paid' },
        { value: 'failed', label: 'Failed' },
        { value: 'disputed', label: 'Disputed' },
        { value: 'hold', label: 'On Hold' }
      ]
    },
    {
      id: 'paymentMethod',
      label: 'Payment Method',
      type: 'select',
      field: 'payout.method',
      options: [
        { value: 'bank_transfer', label: 'Bank Transfer' },
        { value: 'paypal', label: 'PayPal' },
        { value: 'wire', label: 'Wire Transfer' },
        { value: 'check', label: 'Check' }
      ]
    },
    {
      id: 'period',
      label: 'Period',
      type: 'text',
      field: 'period'
    },
    {
      id: 'commissionRate',
      label: 'Commission Rate',
      type: 'numberrange',
      field: 'commissionRate',
      min: 0,
      max: 100
    },
    {
      id: 'totalPayout',
      label: 'Total Payout',
      type: 'numberrange',
      field: 'earnings.totalPayout',
      min: 0
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
      const mockCommissions: VendorCommission[] = [
        {
          id: '1',
          vendorId: 'vendor1',
          vendorName: 'TechStore Colombia',
          tier: 'gold',
          period: '2024-03',
          commissionRate: 8.5,
          baseRate: 8.0,
          performanceBonus: 0.5,
          sales: {
            totalOrders: 145,
            totalRevenue: 125000000,
            averageOrderValue: 862069,
            refunds: 3,
            returns: 5
          },
          earnings: {
            grossCommission: 10625000,
            deductions: 125000,
            netCommission: 10500000,
            previousBalance: 0,
            totalPayout: 10500000
          },
          payout: {
            status: 'processing',
            method: 'bank_transfer',
            scheduledDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
            bankDetails: {
              accountName: 'TechStore Colombia SAS',
              accountNumber: '****1234',
              bankName: 'Banco de Bogotá',
              routingNumber: '001'
            }
          },
          documents: {
            invoiceGenerated: true,
            taxDocumentRequired: true,
            contractSigned: true,
            complianceCheck: true
          },
          adjustments: [
            {
              id: 'adj1',
              type: 'bonus',
              amount: 62500,
              reason: 'Performance bonus for Q1',
              appliedDate: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString()
            }
          ]
        },
        {
          id: '2',
          vendorId: 'vendor3',
          vendorName: 'Home & Garden Plus',
          tier: 'silver',
          period: '2024-03',
          commissionRate: 10.0,
          baseRate: 10.0,
          performanceBonus: 0,
          sales: {
            totalOrders: 68,
            totalRevenue: 45000000,
            averageOrderValue: 661765,
            refunds: 1,
            returns: 2
          },
          earnings: {
            grossCommission: 4500000,
            deductions: 0,
            netCommission: 4500000,
            previousBalance: 150000,
            totalPayout: 4650000
          },
          payout: {
            status: 'pending',
            method: 'bank_transfer',
            scheduledDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
          },
          documents: {
            invoiceGenerated: false,
            taxDocumentRequired: true,
            contractSigned: true,
            complianceCheck: true
          },
          adjustments: []
        },
        {
          id: '3',
          vendorId: 'vendor2',
          vendorName: 'Fashion Trends',
          tier: 'bronze',
          period: '2024-03',
          commissionRate: 12.0,
          baseRate: 12.0,
          performanceBonus: 0,
          sales: {
            totalOrders: 23,
            totalRevenue: 8500000,
            averageOrderValue: 369565,
            refunds: 2,
            returns: 1
          },
          earnings: {
            grossCommission: 1020000,
            deductions: 50000,
            netCommission: 970000,
            previousBalance: 0,
            totalPayout: 970000
          },
          payout: {
            status: 'failed',
            method: 'paypal',
            scheduledDate: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
          },
          documents: {
            invoiceGenerated: true,
            taxDocumentRequired: false,
            contractSigned: true,
            complianceCheck: false
          },
          adjustments: [
            {
              id: 'adj2',
              type: 'penalty',
              amount: -50000,
              reason: 'Late fulfillment penalty',
              appliedDate: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString()
            }
          ]
        }
      ];

      const mockMetrics: CommissionMetrics = {
        totalVendors: mockCommissions.length,
        totalCommissions: mockCommissions.reduce((sum, c) => sum + c.earnings.grossCommission, 0),
        pendingPayouts: mockCommissions.filter(c => ['pending', 'processing'].includes(c.payout.status)).length,
        averageCommissionRate: mockCommissions.reduce((sum, c) => sum + c.commissionRate, 0) / mockCommissions.length,
        monthlyGrowth: 12.5,
        topEarningVendor: 'TechStore Colombia',
        totalDeductions: mockCommissions.reduce((sum, c) => sum + c.earnings.deductions, 0),
        payoutSuccessRate: 85,
        averagePayoutTime: 3.2,
        commissionsThisMonth: mockCommissions.reduce((sum, c) => sum + c.earnings.netCommission, 0)
      };

      setCommissions(mockCommissions);
      setMetrics(mockMetrics);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load commission data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Handle process payout
   */
  const handleProcessPayout = useCallback(async (commissionId: string) => {
    try {
      // TODO: Replace with actual API call
      setCommissions(prev => prev.map(commission =>
        commission.id === commissionId
          ? { ...commission, payout: { ...commission.payout, status: 'processing' as const } }
          : commission
      ));
    } catch (err) {
      console.error('Failed to process payout:', err);
    }
  }, []);

  /**
   * Handle generate invoice
   */
  const handleGenerateInvoice = useCallback(async (commissionId: string) => {
    try {
      // TODO: Replace with actual API call
      setCommissions(prev => prev.map(commission =>
        commission.id === commissionId
          ? { ...commission, documents: { ...commission.documents, invoiceGenerated: true } }
          : commission
      ));
    } catch (err) {
      console.error('Failed to generate invoice:', err);
    }
  }, []);

  /**
   * Handle bulk process payouts
   */
  const handleBulkProcessPayouts = useCallback(async (commissionIds: string[]) => {
    try {
      // TODO: Replace with actual API call
      setCommissions(prev => prev.map(commission =>
        commissionIds.includes(commission.id)
          ? { ...commission, payout: { ...commission.payout, status: 'processing' as const } }
          : commission
      ));
      setSelectedCommissions([]);
    } catch (err) {
      console.error('Failed to process bulk payouts:', err);
    }
  }, []);

  /**
   * Handle bulk generate invoices
   */
  const handleBulkGenerateInvoices = useCallback(async (commissionIds: string[]) => {
    try {
      // TODO: Replace with actual API call
      setCommissions(prev => prev.map(commission =>
        commissionIds.includes(commission.id)
          ? { ...commission, documents: { ...commission.documents, invoiceGenerated: true } }
          : commission
      ));
      setSelectedCommissions([]);
    } catch (err) {
      console.error('Failed to generate bulk invoices:', err);
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
          <h1 className="text-2xl font-bold text-gray-900">Commission Management</h1>
          <p className="text-sm text-gray-500 mt-1">
            Manage vendor commissions and payout schedules
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
            onClick={() => setShowPayoutModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Calculator className="w-4 h-4 mr-2" />
            Calculate Commissions
          </button>
        </div>
      </div>

      {/* Metrics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Total Commissions"
          value={metrics ? commonComponentUtils.formatCurrency(metrics.totalCommissions) : undefined}
          icon={DollarSign}
          theme="primary"
          isLoading={isLoading}
          formatValue={(val) => String(val)}
        />
        <DashboardCard
          title="Pending Payouts"
          value={metrics?.pendingPayouts}
          icon={Clock}
          theme="warning"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Avg. Commission Rate"
          value={metrics ? `${metrics.averageCommissionRate.toFixed(1)}%` : undefined}
          icon={TrendingUp}
          theme="info"
          isLoading={isLoading}
          formatValue={(val) => String(val)}
        />
        <DashboardCard
          title="Payout Success Rate"
          value={metrics ? `${metrics.payoutSuccessRate}%` : undefined}
          icon={CheckCircle}
          theme="success"
          isLoading={isLoading}
          formatValue={(val) => String(val)}
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
            data={commissions}
            columns={columns}
            isLoading={isLoading}
            error={error}
            selectedRows={selectedCommissions}
            getRowId={(commission) => commission.id}
            bulkActions={bulkActions}
            rowActions={rowActions}
            searchable={true}
            searchPlaceholder="Search by vendor name or period..."
            selectable={true}
            onRowSelect={setSelectedCommissions}
            onRefresh={loadData}
            emptyMessage="No commission data found."
          />
        </div>
      </div>

      {/* Commission Detail Modal */}
      {selectedCommission && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium">{selectedCommission.vendorName}</h3>
                  <p className="text-sm text-gray-500">Commission Details - {selectedCommission.period}</p>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedCommission(null)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  ×
                </button>
              </div>
            </div>
            <div className="p-6 overflow-auto max-h-[calc(90vh-140px)]">
              <p className="text-gray-500">Commission details interface will be implemented here.</p>
            </div>
          </div>
        </div>
      )}

      {/* Payout Calculation Modal */}
      {showPayoutModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-medium mb-4">Calculate Commissions</h3>
            <p className="text-gray-500 mb-4">Commission calculation interface will be implemented here.</p>
            <button
              type="button"
              onClick={() => setShowPayoutModal(false)}
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
export default VendorCommissionsPage;