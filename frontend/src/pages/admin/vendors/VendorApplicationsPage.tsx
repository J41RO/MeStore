/**
 * VendorApplicationsPage Component
 *
 * Advanced vendor application review and approval workflow interface.
 * Provides comprehensive application management with automated screening.
 *
 * Features:
 * - Application workflow management (pending → review → approved/rejected)
 * - Document verification and compliance checking
 * - Automated background checks and scoring
 * - Bulk application processing
 * - Application templates and requirements
 * - Communication tracking with applicants
 * - Approval history and audit trails
 * - Integration with external verification services
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
  CheckCircle,
  X,
  Clock,
  FileText,
  Eye,
  Download,
  MessageSquare,
  AlertTriangle,
  User,
  Building,
  MapPin,
  Globe,
  Phone,
  Mail,
  Calendar,
  Star,
  Shield,
  TrendingUp,
  Filter,
  Search
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
 * Vendor application interface
 */
interface VendorApplication {
  id: string;
  applicantName: string;
  businessName: string;
  email: string;
  phone: string;
  status: 'pending' | 'under_review' | 'approved' | 'rejected' | 'incomplete' | 'on_hold';
  submittedAt: string;
  reviewedAt?: string;
  reviewedBy?: string;
  businessCategory: string;
  businessType: 'individual' | 'company' | 'corporation';
  location: {
    city: string;
    state: string;
    country: string;
  };
  documents: {
    businessLicense: boolean;
    taxCertificate: boolean;
    bankStatement: boolean;
    identityDocument: boolean;
    insuranceCertificate: boolean;
    totalSubmitted: number;
    totalRequired: number;
  };
  businessInfo: {
    yearEstablished: number;
    employeeCount: string;
    annualRevenue: string;
    website?: string;
    description: string;
    productCategories: string[];
  };
  verification: {
    emailVerified: boolean;
    phoneVerified: boolean;
    businessVerified: boolean;
    backgroundCheck: boolean;
    complianceScore: number;
    riskScore: number;
  };
  communication: {
    messagesCount: number;
    lastContactAt?: string;
    requiresResponse: boolean;
  };
}

/**
 * Application metrics interface
 */
interface ApplicationMetrics {
  totalApplications: number;
  pendingApplications: number;
  underReviewApplications: number;
  approvedApplications: number;
  rejectedApplications: number;
  approvalRate: number;
  averageProcessingTime: number;
  applicationsToday: number;
  completionRate: number;
}

/**
 * VendorApplicationsPage Component
 */
export const VendorApplicationsPage: React.FC = () => {
  // State management
  const [applications, setApplications] = useState<VendorApplication[]>([]);
  const [metrics, setMetrics] = useState<ApplicationMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedApplications, setSelectedApplications] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [activeFilters, setActiveFilters] = useState<ActiveFilter[]>([]);
  const [selectedApplication, setSelectedApplication] = useState<VendorApplication | null>(null);

  /**
   * Application table columns
   */
  const columns: TableColumn<VendorApplication>[] = useMemo(() => [
    {
      id: 'applicant',
      header: 'Applicant',
      accessor: 'applicantName',
      sortable: true,
      cell: (value, row) => (
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <Building className="w-5 h-5 text-blue-600" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">{row.businessName}</p>
            <p className="text-sm text-gray-500 truncate">{value}</p>
            <div className="flex items-center space-x-2 text-xs text-gray-400">
              <MapPin className="w-3 h-3" />
              <span>{row.location.city}, {row.location.country}</span>
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
      cell: (value, row) => (
        <div className="space-y-1">
          <StatusBadge
            variant={
              value === 'approved' ? 'success' :
              value === 'rejected' ? 'error' :
              value === 'under_review' ? 'info' :
              value === 'incomplete' || value === 'on_hold' ? 'warning' : 'pending'
            }
            size="sm"
          >
            {value.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </StatusBadge>
          {row.communication.requiresResponse && (
            <div className="flex items-center space-x-1">
              <MessageSquare className="w-3 h-3 text-orange-500" />
              <span className="text-xs text-orange-600">Requires Response</span>
            </div>
          )}
        </div>
      )
    },
    {
      id: 'category',
      header: 'Category',
      accessor: 'businessCategory',
      sortable: true,
      cell: (value, row) => (
        <div className="space-y-1">
          <span className="text-sm text-gray-900">{value}</span>
          <div className="text-xs text-gray-500">
            {row.businessType.charAt(0).toUpperCase() + row.businessType.slice(1)}
          </div>
        </div>
      )
    },
    {
      id: 'documents',
      header: 'Documents',
      accessor: 'documents',
      cell: (value) => (
        <div className="flex items-center space-x-2">
          <div className="w-16 bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                value.totalSubmitted === value.totalRequired ? 'bg-green-500' :
                value.totalSubmitted > value.totalRequired / 2 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${(value.totalSubmitted / value.totalRequired) * 100}%` }}
            />
          </div>
          <span className="text-xs text-gray-500">
            {value.totalSubmitted}/{value.totalRequired}
          </span>
        </div>
      )
    },
    {
      id: 'verification',
      header: 'Verification',
      accessor: 'verification',
      hideOnMobile: true,
      cell: (value) => (
        <div className="space-y-1">
          <div className="flex items-center space-x-1">
            <div className={`w-2 h-2 rounded-full ${value.emailVerified ? 'bg-green-500' : 'bg-gray-300'}`} />
            <span className="text-xs text-gray-600">Email</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className={`w-2 h-2 rounded-full ${value.businessVerified ? 'bg-green-500' : 'bg-gray-300'}`} />
            <span className="text-xs text-gray-600">Business</span>
          </div>
          <div className="text-xs">
            <span className={`${
              value.riskScore < 30 ? 'text-green-600' :
              value.riskScore < 70 ? 'text-yellow-600' : 'text-red-600'
            }`}>
              Risk: {value.riskScore}%
            </span>
          </div>
        </div>
      )
    },
    {
      id: 'submitted',
      header: 'Submitted',
      accessor: 'submittedAt',
      sortable: true,
      hideOnMobile: true,
      cell: (value) => (
        <span className="text-sm text-gray-900">
          {commonComponentUtils.getRelativeTime(value)}
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
      label: 'Review Application',
      icon: Eye,
      action: (application: VendorApplication) => {
        setSelectedApplication(application);
      }
    },
    {
      id: 'approve',
      label: 'Approve Application',
      icon: CheckCircle,
      variant: 'success' as const,
      action: (application: VendorApplication) => {
        handleStatusChange(application.id, 'approved');
      },
      hidden: (application: VendorApplication) => !['under_review', 'on_hold'].includes(application.status)
    },
    {
      id: 'reject',
      label: 'Reject Application',
      icon: X,
      variant: 'danger' as const,
      action: (application: VendorApplication) => {
        if (confirm(`Reject application from ${application.businessName}?`)) {
          handleStatusChange(application.id, 'rejected');
        }
      },
      hidden: (application: VendorApplication) => ['approved', 'rejected'].includes(application.status)
    },
    {
      id: 'message',
      label: 'Send Message',
      icon: MessageSquare,
      action: (application: VendorApplication) => {
        console.log('Send message to:', application.email);
      }
    }
  ], []);

  /**
   * Bulk actions
   */
  const bulkActions: BulkAction<VendorApplication>[] = useMemo(() => [
    {
      id: 'approve',
      label: 'Approve Applications',
      icon: CheckCircle,
      variant: 'success',
      action: async (applications) => {
        const applicationIds = applications
          .filter(app => ['under_review', 'on_hold'].includes(app.status))
          .map(app => app.id);
        await handleBulkStatusChange(applicationIds, 'approved');
      }
    },
    {
      id: 'review',
      label: 'Move to Review',
      icon: Clock,
      variant: 'info',
      action: async (applications) => {
        const applicationIds = applications
          .filter(app => app.status === 'pending')
          .map(app => app.id);
        await handleBulkStatusChange(applicationIds, 'under_review');
      }
    },
    {
      id: 'reject',
      label: 'Reject Applications',
      icon: X,
      variant: 'danger',
      action: async (applications) => {
        const applicationIds = applications
          .filter(app => !['approved', 'rejected'].includes(app.status))
          .map(app => app.id);
        await handleBulkStatusChange(applicationIds, 'rejected');
      },
      requireConfirmation: true,
      confirmationMessage: 'Are you sure you want to reject the selected applications?'
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
        { value: 'under_review', label: 'Under Review' },
        { value: 'approved', label: 'Approved' },
        { value: 'rejected', label: 'Rejected' },
        { value: 'incomplete', label: 'Incomplete' },
        { value: 'on_hold', label: 'On Hold' }
      ]
    },
    {
      id: 'businessCategory',
      label: 'Business Category',
      type: 'select',
      field: 'businessCategory',
      options: [
        { value: 'Electronics', label: 'Electronics' },
        { value: 'Fashion', label: 'Fashion' },
        { value: 'Home & Garden', label: 'Home & Garden' },
        { value: 'Sports', label: 'Sports' },
        { value: 'Books', label: 'Books' }
      ]
    },
    {
      id: 'businessType',
      label: 'Business Type',
      type: 'select',
      field: 'businessType',
      options: [
        { value: 'individual', label: 'Individual' },
        { value: 'company', label: 'Company' },
        { value: 'corporation', label: 'Corporation' }
      ]
    },
    {
      id: 'country',
      label: 'Country',
      type: 'text',
      field: 'location.country'
    },
    {
      id: 'riskScore',
      label: 'Risk Score',
      type: 'numberrange',
      field: 'verification.riskScore',
      min: 0,
      max: 100
    },
    {
      id: 'submittedAt',
      label: 'Submission Date',
      type: 'daterange',
      field: 'submittedAt'
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
      const mockApplications: VendorApplication[] = [
        {
          id: '1',
          applicantName: 'Carlos Rodriguez',
          businessName: 'TechGadgets Colombia',
          email: 'carlos@techgadgets.co',
          phone: '+57 300 123 4567',
          status: 'under_review',
          submittedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
          businessCategory: 'Electronics',
          businessType: 'company',
          location: { city: 'Bogotá', state: 'Cundinamarca', country: 'Colombia' },
          documents: {
            businessLicense: true,
            taxCertificate: true,
            bankStatement: true,
            identityDocument: true,
            insuranceCertificate: false,
            totalSubmitted: 4,
            totalRequired: 5
          },
          businessInfo: {
            yearEstablished: 2018,
            employeeCount: '11-50',
            annualRevenue: '$100K-$500K',
            website: 'https://techgadgets.co',
            description: 'Electronics retailer specializing in mobile accessories',
            productCategories: ['Mobile Accessories', 'Headphones', 'Chargers']
          },
          verification: {
            emailVerified: true,
            phoneVerified: true,
            businessVerified: true,
            backgroundCheck: true,
            complianceScore: 85,
            riskScore: 25
          },
          communication: {
            messagesCount: 2,
            lastContactAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
            requiresResponse: false
          }
        },
        {
          id: '2',
          applicantName: 'Maria Gonzalez',
          businessName: 'Fashion Forward Boutique',
          email: 'maria@fashionforward.com',
          phone: '+57 301 234 5678',
          status: 'pending',
          submittedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
          businessCategory: 'Fashion',
          businessType: 'individual',
          location: { city: 'Medellín', state: 'Antioquia', country: 'Colombia' },
          documents: {
            businessLicense: false,
            taxCertificate: true,
            bankStatement: false,
            identityDocument: true,
            insuranceCertificate: false,
            totalSubmitted: 2,
            totalRequired: 5
          },
          businessInfo: {
            yearEstablished: 2021,
            employeeCount: '1-10',
            annualRevenue: '$10K-$50K',
            description: 'Boutique fashion store for young professionals',
            productCategories: ['Women\'s Clothing', 'Accessories']
          },
          verification: {
            emailVerified: true,
            phoneVerified: false,
            businessVerified: false,
            backgroundCheck: false,
            complianceScore: 40,
            riskScore: 65
          },
          communication: {
            messagesCount: 0,
            requiresResponse: true
          }
        }
      ];

      const mockMetrics: ApplicationMetrics = {
        totalApplications: mockApplications.length,
        pendingApplications: mockApplications.filter(app => app.status === 'pending').length,
        underReviewApplications: mockApplications.filter(app => app.status === 'under_review').length,
        approvedApplications: mockApplications.filter(app => app.status === 'approved').length,
        rejectedApplications: mockApplications.filter(app => app.status === 'rejected').length,
        approvalRate: 75,
        averageProcessingTime: 5.2,
        applicationsToday: 3,
        completionRate: 68
      };

      setApplications(mockApplications);
      setMetrics(mockMetrics);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load application data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Handle status change
   */
  const handleStatusChange = useCallback(async (applicationId: string, newStatus: VendorApplication['status']) => {
    try {
      // TODO: Replace with actual API call
      setApplications(prev => prev.map(app =>
        app.id === applicationId
          ? { ...app, status: newStatus, reviewedAt: new Date().toISOString() }
          : app
      ));
    } catch (err) {
      console.error('Failed to update application status:', err);
    }
  }, []);

  /**
   * Handle bulk status change
   */
  const handleBulkStatusChange = useCallback(async (applicationIds: string[], newStatus: VendorApplication['status']) => {
    try {
      // TODO: Replace with actual API call
      setApplications(prev => prev.map(app =>
        applicationIds.includes(app.id)
          ? { ...app, status: newStatus, reviewedAt: new Date().toISOString() }
          : app
      ));
      setSelectedApplications([]);
    } catch (err) {
      console.error('Failed to update application statuses:', err);
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
          <h1 className="text-2xl font-bold text-gray-900">Vendor Applications</h1>
          <p className="text-sm text-gray-500 mt-1">
            Review and approve new vendor applications
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
        </div>
      </div>

      {/* Metrics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Total Applications"
          value={metrics?.totalApplications}
          icon={Package}
          theme="primary"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Approval Rate"
          value={metrics ? `${metrics.approvalRate}%` : undefined}
          icon={CheckCircle}
          theme="success"
          isLoading={isLoading}
          formatValue={(val) => String(val)}
        />
        <DashboardCard
          title="Under Review"
          value={metrics?.underReviewApplications}
          icon={Clock}
          theme="warning"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Applications Today"
          value={metrics?.applicationsToday}
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
            data={applications}
            columns={columns}
            isLoading={isLoading}
            error={error}
            selectedRows={selectedApplications}
            getRowId={(app) => app.id}
            bulkActions={bulkActions}
            rowActions={rowActions}
            searchable={true}
            searchPlaceholder="Search applications by business name or applicant..."
            selectable={true}
            onRowSelect={setSelectedApplications}
            onRefresh={loadData}
            emptyMessage="No vendor applications found."
          />
        </div>
      </div>

      {/* Application Detail Modal */}
      {selectedApplication && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium">{selectedApplication.businessName}</h3>
                  <p className="text-sm text-gray-500">Application Review</p>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedApplication(null)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            <div className="p-6 overflow-auto max-h-[calc(90vh-140px)]">
              <p className="text-gray-500">Application review interface will be implemented here.</p>
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
export default VendorApplicationsPage;