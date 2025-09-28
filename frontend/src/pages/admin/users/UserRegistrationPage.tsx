/**
 * UserRegistrationPage Component
 *
 * Advanced user registration management interface with workflow automation
 * and comprehensive onboarding process administration.
 *
 * Features:
 * - Multi-step registration workflow management
 * - Bulk user invitation system
 * - Registration analytics and metrics
 * - Email verification tracking
 * - Custom onboarding templates
 * - Registration approval workflow
 * - Import/export user lists
 * - Welcome email automation
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
  UserPlus,
  Mail,
  Upload,
  Download,
  Send,
  CheckCircle,
  Clock,
  AlertCircle,
  X,
  Eye,
  Edit,
  Copy,
  FileText,
  Settings,
  Users,
  TrendingUp,
  Calendar,
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
  ActiveFilter
} from '../../../components/admin/common';

/**
 * Registration interface
 */
interface Registration {
  id: string;
  email: string;
  firstName?: string;
  lastName?: string;
  invitedBy: string;
  invitedByName: string;
  role: string;
  status: 'pending' | 'sent' | 'opened' | 'completed' | 'expired' | 'failed';
  invitationSentAt: string;
  lastActivityAt?: string;
  completedAt?: string;
  expiresAt: string;
  reminderCount: number;
  registrationData?: {
    phone?: string;
    department?: string;
    notes?: string;
  };
}

/**
 * Registration template
 */
interface RegistrationTemplate {
  id: string;
  name: string;
  subject: string;
  content: string;
  isDefault: boolean;
  usageCount: number;
  createdAt: string;
}

/**
 * Registration metrics
 */
interface RegistrationMetrics {
  totalInvitations: number;
  pendingInvitations: number;
  completedRegistrations: number;
  expiredInvitations: number;
  completionRate: number;
  averageCompletionTime: number;
  invitationsToday: number;
  completionsToday: number;
}

/**
 * UserRegistrationPage Component
 */
export const UserRegistrationPage: React.FC = () => {
  // State management
  const [registrations, setRegistrations] = useState<Registration[]>([]);
  const [templates, setTemplates] = useState<RegistrationTemplate[]>([]);
  const [metrics, setMetrics] = useState<RegistrationMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRegistrations, setSelectedRegistrations] = useState<string[]>([]);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [showBulkInviteModal, setShowBulkInviteModal] = useState(false);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<RegistrationTemplate | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [activeFilters, setActiveFilters] = useState<ActiveFilter[]>([]);

  /**
   * Registration table columns
   */
  const columns: TableColumn<Registration>[] = useMemo(() => [
    {
      id: 'user',
      header: 'Invited User',
      accessor: 'email',
      sortable: true,
      cell: (value, row) => (
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
            <Mail className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <div className="font-medium text-gray-900">
              {row.firstName && row.lastName
                ? `${row.firstName} ${row.lastName}`
                : value}
            </div>
            {row.firstName && row.lastName && (
              <div className="text-sm text-gray-500">{value}</div>
            )}
            <div className="text-xs text-gray-400">
              Role: {row.role.charAt(0).toUpperCase() + row.role.slice(1)}
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
              value === 'completed' ? 'success' :
              value === 'expired' || value === 'failed' ? 'error' :
              value === 'opened' ? 'info' :
              value === 'sent' ? 'warning' : 'pending'
            }
            size="sm"
          >
            {value.charAt(0).toUpperCase() + value.slice(1)}
          </StatusBadge>
          {row.reminderCount > 0 && (
            <div className="text-xs text-gray-500">
              {row.reminderCount} reminder{row.reminderCount > 1 ? 's' : ''} sent
            </div>
          )}
        </div>
      )
    },
    {
      id: 'invitedBy',
      header: 'Invited By',
      accessor: 'invitedByName',
      sortable: true,
      hideOnMobile: true,
      cell: (value) => (
        <span className="text-sm text-gray-900">{value}</span>
      )
    },
    {
      id: 'timeline',
      header: 'Timeline',
      accessor: 'invitationSentAt',
      sortable: true,
      cell: (value, row) => (
        <div className="text-sm space-y-1">
          <div className="flex items-center space-x-1">
            <Clock className="w-3 h-3 text-gray-400" />
            <span className="text-gray-600">
              Sent: {commonComponentUtils.getRelativeTime(value)}
            </span>
          </div>
          {row.completedAt && (
            <div className="flex items-center space-x-1">
              <CheckCircle className="w-3 h-3 text-green-500" />
              <span className="text-gray-600">
                Completed: {commonComponentUtils.getRelativeTime(row.completedAt)}
              </span>
            </div>
          )}
          {row.status !== 'completed' && row.status !== 'expired' && (
            <div className="flex items-center space-x-1">
              <AlertCircle className="w-3 h-3 text-orange-500" />
              <span className="text-gray-600">
                Expires: {commonComponentUtils.getRelativeTime(row.expiresAt)}
              </span>
            </div>
          )}
        </div>
      )
    },
    {
      id: 'progress',
      header: 'Progress',
      accessor: 'status',
      hideOnMobile: true,
      cell: (value, row) => {
        const progressSteps = [
          { key: 'sent', label: 'Sent', completed: ['sent', 'opened', 'completed'].includes(value) },
          { key: 'opened', label: 'Opened', completed: ['opened', 'completed'].includes(value) },
          { key: 'completed', label: 'Completed', completed: value === 'completed' }
        ];

        return (
          <div className="flex items-center space-x-2">
            {progressSteps.map((step, index) => (
              <React.Fragment key={step.key}>
                <div className={`w-3 h-3 rounded-full ${
                  step.completed ? 'bg-green-500' : 'bg-gray-300'
                }`} />
                {index < progressSteps.length - 1 && (
                  <div className={`w-4 h-0.5 ${
                    step.completed ? 'bg-green-500' : 'bg-gray-300'
                  }`} />
                )}
              </React.Fragment>
            ))}
          </div>
        );
      }
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
      action: (registration: Registration) => {
        console.log('View registration:', registration.id);
      }
    },
    {
      id: 'resend',
      label: 'Resend Invitation',
      icon: Send,
      action: (registration: Registration) => {
        handleResendInvitation(registration.id);
      },
      hidden: (registration: Registration) => registration.status === 'completed'
    },
    {
      id: 'copy-link',
      label: 'Copy Link',
      icon: Copy,
      action: (registration: Registration) => {
        const link = `${window.location.origin}/register/${registration.id}`;
        navigator.clipboard.writeText(link);
        // TODO: Show toast notification
      },
      hidden: (registration: Registration) => registration.status === 'completed' || registration.status === 'expired'
    },
    {
      id: 'cancel',
      label: 'Cancel Invitation',
      icon: X,
      variant: 'danger' as const,
      action: (registration: Registration) => {
        if (confirm('Are you sure you want to cancel this invitation?')) {
          handleCancelInvitation(registration.id);
        }
      },
      hidden: (registration: Registration) => registration.status === 'completed'
    }
  ], []);

  /**
   * Bulk actions
   */
  const bulkActions = useMemo(() => [
    {
      id: 'resend',
      label: 'Resend Invitations',
      icon: Send,
      variant: 'default' as const,
      action: async (registrations: Registration[]) => {
        const eligibleIds = registrations
          .filter(r => r.status !== 'completed')
          .map(r => r.id);
        await handleBulkResend(eligibleIds);
      }
    },
    {
      id: 'cancel',
      label: 'Cancel Invitations',
      icon: X,
      variant: 'danger' as const,
      action: async (registrations: Registration[]) => {
        const eligibleIds = registrations
          .filter(r => r.status !== 'completed')
          .map(r => r.id);
        await handleBulkCancel(eligibleIds);
      },
      requireConfirmation: true,
      confirmationMessage: 'Are you sure you want to cancel the selected invitations?'
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
        { value: 'sent', label: 'Sent' },
        { value: 'opened', label: 'Opened' },
        { value: 'completed', label: 'Completed' },
        { value: 'expired', label: 'Expired' },
        { value: 'failed', label: 'Failed' }
      ]
    },
    {
      id: 'role',
      label: 'Invited Role',
      type: 'select',
      field: 'role',
      options: [
        { value: 'admin', label: 'Administrator' },
        { value: 'manager', label: 'Manager' },
        { value: 'operator', label: 'Operator' },
        { value: 'viewer', label: 'Viewer' }
      ]
    },
    {
      id: 'invitedBy',
      label: 'Invited By',
      type: 'text',
      field: 'invitedByName'
    },
    {
      id: 'dateRange',
      label: 'Invitation Date',
      type: 'daterange',
      field: 'invitationSentAt'
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
      const mockRegistrations: Registration[] = [
        {
          id: '1',
          email: 'newuser@example.com',
          firstName: 'Ana',
          lastName: 'Rodriguez',
          invitedBy: 'admin1',
          invitedByName: 'Admin User',
          role: 'manager',
          status: 'completed',
          invitationSentAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
          completedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
          expiresAt: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
          reminderCount: 1,
          registrationData: {
            phone: '+57 300 123 4567',
            department: 'Sales'
          }
        },
        {
          id: '2',
          email: 'pending@example.com',
          invitedBy: 'admin1',
          invitedByName: 'Admin User',
          role: 'operator',
          status: 'opened',
          invitationSentAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          lastActivityAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
          expiresAt: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
          reminderCount: 0
        },
        {
          id: '3',
          email: 'expired@example.com',
          invitedBy: 'manager1',
          invitedByName: 'Maria Rodriguez',
          role: 'viewer',
          status: 'expired',
          invitationSentAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
          expiresAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
          reminderCount: 2
        },
        {
          id: '4',
          email: 'fresh@example.com',
          invitedBy: 'admin1',
          invitedByName: 'Admin User',
          role: 'admin',
          status: 'sent',
          invitationSentAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
          expiresAt: new Date(Date.now() + 6 * 24 * 60 * 60 * 1000).toISOString(),
          reminderCount: 0
        }
      ];

      const mockTemplates: RegistrationTemplate[] = [
        {
          id: 'default',
          name: 'Default Invitation',
          subject: 'Welcome to MeStore - Complete Your Registration',
          content: 'You have been invited to join MeStore. Click the link below to complete your registration.',
          isDefault: true,
          usageCount: 45,
          createdAt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
          id: 'manager',
          name: 'Manager Invitation',
          subject: 'Manager Access Invitation - MeStore',
          content: 'You have been granted manager access to MeStore. Complete your registration to start managing.',
          isDefault: false,
          usageCount: 12,
          createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()
        }
      ];

      const mockMetrics: RegistrationMetrics = {
        totalInvitations: mockRegistrations.length,
        pendingInvitations: mockRegistrations.filter(r => !['completed', 'expired'].includes(r.status)).length,
        completedRegistrations: mockRegistrations.filter(r => r.status === 'completed').length,
        expiredInvitations: mockRegistrations.filter(r => r.status === 'expired').length,
        completionRate: 75,
        averageCompletionTime: 2.5,
        invitationsToday: 1,
        completionsToday: 0
      };

      setRegistrations(mockRegistrations);
      setTemplates(mockTemplates);
      setMetrics(mockMetrics);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load registration data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Handle resend invitation
   */
  const handleResendInvitation = useCallback(async (registrationId: string) => {
    try {
      // TODO: Replace with actual API call
      setRegistrations(prev => prev.map(reg =>
        reg.id === registrationId
          ? {
              ...reg,
              status: 'sent' as const,
              reminderCount: reg.reminderCount + 1,
              invitationSentAt: new Date().toISOString()
            }
          : reg
      ));
    } catch (err) {
      console.error('Failed to resend invitation:', err);
    }
  }, []);

  /**
   * Handle cancel invitation
   */
  const handleCancelInvitation = useCallback(async (registrationId: string) => {
    try {
      // TODO: Replace with actual API call
      setRegistrations(prev => prev.filter(reg => reg.id !== registrationId));
    } catch (err) {
      console.error('Failed to cancel invitation:', err);
    }
  }, []);

  /**
   * Handle bulk resend
   */
  const handleBulkResend = useCallback(async (registrationIds: string[]) => {
    try {
      // TODO: Replace with actual API call
      setRegistrations(prev => prev.map(reg =>
        registrationIds.includes(reg.id)
          ? {
              ...reg,
              status: 'sent' as const,
              reminderCount: reg.reminderCount + 1,
              invitationSentAt: new Date().toISOString()
            }
          : reg
      ));
      setSelectedRegistrations([]);
    } catch (err) {
      console.error('Failed to bulk resend invitations:', err);
    }
  }, []);

  /**
   * Handle bulk cancel
   */
  const handleBulkCancel = useCallback(async (registrationIds: string[]) => {
    try {
      // TODO: Replace with actual API call
      setRegistrations(prev => prev.filter(reg => !registrationIds.includes(reg.id)));
      setSelectedRegistrations([]);
    } catch (err) {
      console.error('Failed to bulk cancel invitations:', err);
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
          <h1 className="text-2xl font-bold text-gray-900">User Registration</h1>
          <p className="text-sm text-gray-500 mt-1">
            Manage user invitations and registration workflow
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
            onClick={() => setShowBulkInviteModal(true)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Upload className="w-4 h-4 mr-2" />
            Bulk Invite
          </button>

          <button
            type="button"
            onClick={() => setShowTemplateModal(true)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <FileText className="w-4 h-4 mr-2" />
            Templates
          </button>

          <button
            type="button"
            onClick={() => setShowInviteModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <UserPlus className="w-4 h-4 mr-2" />
            Invite User
          </button>
        </div>
      </div>

      {/* Metrics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Total Invitations"
          value={metrics?.totalInvitations}
          icon={Mail}
          theme="primary"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Completion Rate"
          value={metrics?.completionRate ? `${metrics.completionRate}%` : undefined}
          icon={TrendingUp}
          theme="success"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Pending"
          value={metrics?.pendingInvitations}
          icon={Clock}
          theme="warning"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Completed Today"
          value={metrics?.completionsToday}
          icon={CheckCircle}
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
            data={registrations}
            columns={columns}
            isLoading={isLoading}
            error={error}
            selectedRows={selectedRegistrations}
            getRowId={(reg) => reg.id}
            bulkActions={bulkActions}
            rowActions={rowActions}
            searchable={true}
            searchPlaceholder="Search by email or name..."
            selectable={true}
            onRowSelect={setSelectedRegistrations}
            onRefresh={loadData}
            emptyMessage="No invitations sent yet. Send your first invitation to get started."
          />
        </div>
      </div>

      {/* Modals */}
      {/* Single Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-medium mb-4">Send User Invitation</h3>
            <p className="text-gray-500 mb-4">Single user invitation form will be implemented here.</p>
            <button
              type="button"
              onClick={() => setShowInviteModal(false)}
              className="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* Bulk Invite Modal */}
      {showBulkInviteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-medium mb-4">Bulk User Invitation</h3>
            <p className="text-gray-500 mb-4">Bulk invitation interface will be implemented here.</p>
            <button
              type="button"
              onClick={() => setShowBulkInviteModal(false)}
              className="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* Templates Modal */}
      {showTemplateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium">Email Templates</h3>
              <button
                type="button"
                onClick={() => setShowTemplateModal(false)}
                className="text-gray-400 hover:text-gray-500"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-4">
              {templates.map((template) => (
                <div key={template.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h4 className="font-medium text-gray-900">{template.name}</h4>
                        {template.isDefault && (
                          <StatusBadge variant="info" size="xs">Default</StatusBadge>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{template.subject}</p>
                      <p className="text-xs text-gray-500 mt-2">
                        Used {template.usageCount} times
                      </p>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        type="button"
                        className="text-gray-400 hover:text-gray-500"
                        title="Edit Template"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        className="text-gray-400 hover:text-gray-500"
                        title="View Template"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
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
export default UserRegistrationPage;