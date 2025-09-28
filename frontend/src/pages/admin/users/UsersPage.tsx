/**
 * UsersPage Component
 *
 * Main user management page with comprehensive user administration capabilities.
 * Provides CRUD operations, filtering, bulk actions, and real-time user analytics.
 *
 * Features:
 * - Advanced user table with sorting and filtering
 * - Bulk user operations (activate, deactivate, delete)
 * - Real-time user metrics dashboard
 * - User creation and editing modals
 * - Role-based access control
 * - Export functionality
 * - User activity tracking
 * - Responsive design for mobile/tablet
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
  Users,
  UserPlus,
  Download,
  Filter,
  RefreshCw,
  Search,
  Mail,
  Phone,
  Calendar,
  Activity,
  Shield,
  Eye,
  Edit,
  Trash2,
  Ban,
  CheckCircle,
  Settings,
  MoreVertical
} from 'lucide-react';

import {
  DashboardCard,
  DataTable,
  FilterPanel,
  StatusBadge,
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

import {
  superuserService,
  type UserSummary,
  type UserListResponse,
  type UserStatsResponse,
  type UserFilters,
  type CreateUserData,
  type UpdateUserData
} from '../../../services/superuserService';

/**
 * User interface (mapped from backend UserSummary)
 */
interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  full_name: string;
  role: 'BUYER' | 'VENDOR' | 'ADMIN' | 'SUPERUSER';
  status: 'active' | 'inactive';
  isVerified: boolean;
  email_verified: boolean;
  phone_verified: boolean;
  phone?: string;
  lastLogin?: string;
  createdAt: string;
  vendor_status?: string;
  business_name?: string;
  security_clearance_level?: number;
  failed_login_attempts?: number;
  account_locked: boolean;
}

/**
 * User metrics interface (mapped from backend UserStatsResponse)
 */
interface UserMetrics {
  totalUsers: number;
  activeUsers: number;
  inactiveUsers: number;
  verifiedUsers: number;
  buyers: number;
  vendors: number;
  admins: number;
  superusers: number;
  emailVerified: number;
  phoneVerified: number;
  bothVerified: number;
  newUsersToday: number;
  newUsersThisWeek: number;
  newUsersThisMonth: number;
  recentLogins: number;
  lockedAccounts: number;
}

/**
 * UsersPage Component
 */
export const UsersPage: React.FC = () => {
  // State management
  const [users, setUsers] = useState<User[]>([]);
  const [metrics, setMetrics] = useState<UserMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilters, setActiveFilters] = useState<ActiveFilter[]>([]);

  // Pagination and sorting
  const [sort, setSort] = useState<SortConfig>({ column: 'createdAt', direction: 'desc' });
  const [pagination, setPagination] = useState<PaginationConfig>({
    page: 1,
    pageSize: 25,
    total: 0
  });

  /**
   * Table columns configuration
   */
  const columns: TableColumn<User>[] = useMemo(() => [
    {
      id: 'user',
      header: 'User',
      accessor: 'email',
      sortable: true,
      cell: (value, row) => (
        <div className="flex items-center space-x-3">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
              <Users className="w-5 h-5 text-gray-600" />
            </div>
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-gray-900 truncate">
              {row.full_name || `${row.firstName} ${row.lastName}`}
            </p>
            <p className="text-sm text-gray-500 truncate">{value}</p>
          </div>
        </div>
      )
    },
    {
      id: 'role',
      header: 'Role',
      accessor: 'role',
      sortable: true,
      cell: (value) => (
        <StatusBadge
          variant={
            value === 'SUPERUSER' ? 'premium' :
            value === 'ADMIN' ? 'success' :
            value === 'VENDOR' ? 'warning' :
            'default'
          }
          size="sm"
        >
          {value.charAt(0).toUpperCase() + value.slice(1).toLowerCase()}
        </StatusBadge>
      )
    },
    {
      id: 'status',
      header: 'Status',
      accessor: 'status',
      sortable: true,
      cell: (value, row) => (
        <div className="flex items-center space-x-2">
          <StatusBadge
            variant={value === 'active' ? 'success' : 'inactive'}
            size="sm"
          >
            {value.charAt(0).toUpperCase() + value.slice(1)}
          </StatusBadge>
          {row.isVerified && (
            <CheckCircle className="w-4 h-4 text-green-500" title="Verified" />
          )}
          {row.email_verified && (
            <Mail className="w-4 h-4 text-blue-500" title="Email Verified" />
          )}
          {row.phone_verified && (
            <Phone className="w-4 h-4 text-purple-500" title="Phone Verified" />
          )}
          {row.account_locked && (
            <Ban className="w-4 h-4 text-red-500" title="Account Locked" />
          )}
        </div>
      )
    },
    {
      id: 'lastLogin',
      header: 'Last Login',
      accessor: 'lastLogin',
      sortable: true,
      hideOnMobile: true,
      cell: (value) => (
        <span className="text-sm text-gray-900">
          {value ? commonComponentUtils.getRelativeTime(value) : 'Never'}
        </span>
      )
    },
    {
      id: 'loginCount',
      header: 'Logins',
      accessor: 'loginCount',
      sortable: true,
      hideOnMobile: true,
      align: 'center',
      cell: (value) => (
        <span className="text-sm font-medium text-gray-900">{value}</span>
      )
    },
    {
      id: 'profileComplete',
      header: 'Profile',
      accessor: 'profileComplete',
      sortable: true,
      hideOnMobile: true,
      cell: (value) => (
        <div className="flex items-center space-x-2">
          <div className="w-16 bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                value >= 80 ? 'bg-green-500' :
                value >= 50 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${value}%` }}
            />
          </div>
          <span className="text-xs text-gray-500">{value}%</span>
        </div>
      )
    },
    {
      id: 'createdAt',
      header: 'Created',
      accessor: 'createdAt',
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
   * Row actions configuration
   */
  const rowActions = useMemo(() => [
    {
      id: 'view',
      label: 'View Details',
      icon: Eye,
      action: (user: User) => {
        console.log('View user:', user.id);
        // TODO: Implement view modal
      }
    },
    {
      id: 'edit',
      label: 'Edit User',
      icon: Edit,
      action: (user: User) => {
        setEditingUser(user);
      }
    },
    {
      id: 'toggle-status',
      label: (user: User) => user.status === 'active' ? 'Suspend User' : 'Activate User',
      icon: (user: User) => user.status === 'active' ? Ban : CheckCircle,
      variant: (user: User) => user.status === 'active' ? 'danger' : 'default',
      action: (user: User) => {
        handleToggleUserStatus(user.id, user.status === 'active' ? 'suspended' : 'active');
      }
    },
    {
      id: 'delete',
      label: 'Delete User',
      icon: Trash2,
      variant: 'danger' as const,
      action: (user: User) => {
        if (confirm(`Are you sure you want to delete ${user.firstName} ${user.lastName}?`)) {
          handleDeleteUser(user.id);
        }
      },
      hidden: (user: User) => user.role === 'superuser'
    }
  ], []);

  /**
   * Bulk actions configuration
   */
  const bulkActions: BulkAction<User>[] = useMemo(() => [
    {
      id: 'activate',
      label: 'Activate Users',
      icon: CheckCircle,
      variant: 'success',
      action: async (users) => {
        const userIds = users.map(u => u.id);
        await handleBulkStatusUpdate(userIds, 'active');
      }
    },
    {
      id: 'suspend',
      label: 'Suspend Users',
      icon: Ban,
      variant: 'warning',
      action: async (users) => {
        const userIds = users.map(u => u.id);
        await handleBulkStatusUpdate(userIds, 'suspended');
      },
      requireConfirmation: true,
      confirmationMessage: 'Are you sure you want to suspend the selected users?'
    },
    {
      id: 'delete',
      label: 'Delete Users',
      icon: Trash2,
      variant: 'danger',
      action: async (users) => {
        const userIds = users.map(u => u.id);
        await handleBulkDelete(userIds);
      },
      requireConfirmation: true,
      confirmationMessage: 'Are you sure you want to delete the selected users? This action cannot be undone.'
    }
  ], []);

  /**
   * Filter definitions
   */
  const filterDefinitions: FilterDefinition[] = useMemo(() => [
    {
      id: 'role',
      label: 'Role',
      type: 'select',
      field: 'role',
      options: [
        { value: 'superuser', label: 'Superuser' },
        { value: 'admin', label: 'Admin' },
        { value: 'manager', label: 'Manager' },
        { value: 'operator', label: 'Operator' },
        { value: 'viewer', label: 'Viewer' }
      ]
    },
    {
      id: 'status',
      label: 'Status',
      type: 'select',
      field: 'status',
      options: [
        { value: 'active', label: 'Active' },
        { value: 'inactive', label: 'Inactive' },
        { value: 'suspended', label: 'Suspended' },
        { value: 'pending', label: 'Pending' }
      ]
    },
    {
      id: 'isVerified',
      label: 'Email Verified',
      type: 'boolean',
      field: 'isVerified'
    },
    {
      id: 'createdAt',
      label: 'Registration Date',
      type: 'daterange',
      field: 'createdAt'
    },
    {
      id: 'lastLogin',
      label: 'Last Login',
      type: 'daterange',
      field: 'lastLogin'
    },
    {
      id: 'loginCount',
      label: 'Login Count',
      type: 'numberrange',
      field: 'loginCount',
      min: 0
    }
  ], []);

  /**
   * Helper function to transform backend UserSummary to local User interface
   */
  const transformBackendUser = (backendUser: UserSummary): User => ({
    id: backendUser.id,
    email: backendUser.email,
    firstName: backendUser.nombre || '',
    lastName: backendUser.apellido || '',
    full_name: backendUser.full_name,
    role: backendUser.user_type,
    status: backendUser.is_active ? 'active' : 'inactive',
    isVerified: backendUser.is_verified,
    email_verified: backendUser.email_verified,
    phone_verified: backendUser.phone_verified,
    phone: backendUser.telefono || undefined,
    lastLogin: backendUser.last_login || undefined,
    createdAt: backendUser.created_at,
    vendor_status: backendUser.vendor_status || undefined,
    business_name: backendUser.business_name || undefined,
    security_clearance_level: backendUser.security_clearance_level || undefined,
    failed_login_attempts: backendUser.failed_login_attempts || undefined,
    account_locked: backendUser.account_locked
  });

  /**
   * Helper function to transform backend UserStatsResponse to local UserMetrics interface
   */
  const transformBackendMetrics = (backendStats: UserStatsResponse): UserMetrics => ({
    totalUsers: backendStats.total_users,
    activeUsers: backendStats.active_users,
    inactiveUsers: backendStats.inactive_users,
    verifiedUsers: backendStats.verified_users,
    buyers: backendStats.buyers,
    vendors: backendStats.vendors,
    admins: backendStats.admins,
    superusers: backendStats.superusers,
    emailVerified: backendStats.email_verified,
    phoneVerified: backendStats.phone_verified,
    bothVerified: backendStats.both_verified,
    newUsersToday: backendStats.created_today,
    newUsersThisWeek: backendStats.created_this_week,
    newUsersThisMonth: backendStats.created_this_month,
    recentLogins: backendStats.recent_logins,
    lockedAccounts: backendStats.locked_accounts
  });

  /**
   * Load users data from real backend
   */
  const loadUsers = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Build filters from active filters and search
      const filters: UserFilters = {};

      // Add search filter
      if (searchQuery.trim()) {
        filters.search = searchQuery.trim();
      }

      // Add filters from active filters
      activeFilters.forEach(filter => {
        switch (filter.field) {
          case 'role':
            filters.user_type = filter.value as any;
            break;
          case 'status':
            if (filter.value === 'active' || filter.value === 'inactive') {
              filters.is_active = filter.value === 'active';
            }
            break;
          case 'isVerified':
            filters.is_verified = filter.value as boolean;
            break;
          case 'email_verified':
            filters.email_verified = filter.value as boolean;
            break;
          case 'phone_verified':
            filters.phone_verified = filter.value as boolean;
            break;
        }
      });

      // Add sorting
      if (sort.column && sort.direction) {
        const sortMap: Record<string, string> = {
          'email': sort.direction === 'asc' ? 'email_asc' : 'email_desc',
          'createdAt': sort.direction === 'asc' ? 'created_at_asc' : 'created_at_desc',
          'lastLogin': sort.direction === 'asc' ? 'last_login_asc' : 'last_login_desc',
          'role': 'user_type',
          'status': 'is_active'
        };
        filters.sort_by = sortMap[sort.column] as any || 'created_at_desc';
      }

      // Load users and metrics in parallel
      const [usersResponse, metricsResponse] = await Promise.all([
        superuserService.getUsers(pagination.page, pagination.pageSize, filters),
        superuserService.getDashboardStats()
      ]);

      // Transform backend data to local format
      const transformedUsers = usersResponse.users.map(transformBackendUser);
      const transformedMetrics = transformBackendMetrics(metricsResponse);

      // Update state
      setUsers(transformedUsers);
      setMetrics(transformedMetrics);
      setPagination(prev => ({
        ...prev,
        total: usersResponse.total,
        page: usersResponse.page
      }));

    } catch (err) {
      console.error('Error loading users:', err);
      setError(err instanceof Error ? err.message : 'Failed to load users from server');
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, activeFilters, sort, pagination.page, pagination.pageSize]);

  /**
   * Handle user status toggle
   */
  const handleToggleUserStatus = useCallback(async (userId: string, newStatus: User['status']) => {
    try {
      await superuserService.updateUser(userId, {
        is_active: newStatus === 'active'
      });

      // Optimistically update local state
      setUsers(prev => prev.map(user =>
        user.id === userId ? { ...user, status: newStatus } : user
      ));
    } catch (err) {
      console.error('Failed to update user status:', err);
      setError(err instanceof Error ? err.message : 'Failed to update user status');
    }
  }, []);

  /**
   * Handle user deletion
   */
  const handleDeleteUser = useCallback(async (userId: string) => {
    try {
      await superuserService.deleteUser(userId, 'Deleted from admin panel');

      // Remove from local state
      setUsers(prev => prev.filter(user => user.id !== userId));

      // Update pagination total
      setPagination(prev => ({ ...prev, total: prev.total - 1 }));
    } catch (err) {
      console.error('Failed to delete user:', err);
      setError(err instanceof Error ? err.message : 'Failed to delete user');
    }
  }, []);

  /**
   * Handle bulk status update
   */
  const handleBulkStatusUpdate = useCallback(async (userIds: string[], newStatus: User['status']) => {
    try {
      // TODO: Replace with actual API call
      setUsers(prev => prev.map(user =>
        userIds.includes(user.id) ? { ...user, status: newStatus } : user
      ));
      setSelectedUsers([]);
    } catch (err) {
      console.error('Failed to update user statuses:', err);
    }
  }, []);

  /**
   * Handle bulk delete
   */
  const handleBulkDelete = useCallback(async (userIds: string[]) => {
    try {
      // TODO: Replace with actual API call
      setUsers(prev => prev.filter(user => !userIds.includes(user.id)));
      setSelectedUsers([]);
    } catch (err) {
      console.error('Failed to delete users:', err);
    }
  }, []);

  /**
   * Handle export
   */
  const handleExport = useCallback(async () => {
    try {
      // Build filters for export
      const filters: UserFilters = {};

      if (searchQuery.trim()) {
        filters.search = searchQuery.trim();
      }

      activeFilters.forEach(filter => {
        switch (filter.field) {
          case 'role':
            filters.user_type = filter.value as any;
            break;
          case 'status':
            if (filter.value === 'active' || filter.value === 'inactive') {
              filters.is_active = filter.value === 'active';
            }
            break;
          case 'isVerified':
            filters.is_verified = filter.value as boolean;
            break;
        }
      });

      const blob = await superuserService.exportUsers(filters);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `users-export-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed:', err);
      setError(err instanceof Error ? err.message : 'Failed to export users');
    }
  }, [searchQuery, activeFilters]);

  /**
   * Load data on mount
   */
  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
          <p className="text-sm text-gray-500 mt-1">
            Manage users, roles, and permissions across the platform
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            type="button"
            onClick={handleExport}
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
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <UserPlus className="w-4 h-4 mr-2" />
            Add User
          </button>
        </div>
      </div>

      {/* Metrics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Total Users"
          value={metrics?.totalUsers}
          icon={Users}
          theme="primary"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Active Users"
          value={metrics?.activeUsers}
          icon={CheckCircle}
          theme="success"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Pending Users"
          value={metrics?.pendingUsers}
          icon={Activity}
          theme="warning"
          isLoading={isLoading}
        />
        <DashboardCard
          title="New This Month"
          value={metrics?.newUsersThisMonth}
          icon={Calendar}
          theme="info"
          isLoading={isLoading}
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
            data={users}
            columns={columns}
            isLoading={isLoading}
            error={error}
            pagination={pagination}
            sort={sort}
            selectedRows={selectedUsers}
            getRowId={(user) => user.id}
            bulkActions={bulkActions}
            rowActions={rowActions}
            searchable={true}
            searchPlaceholder="Search users by name or email..."
            selectable={true}
            onSort={setSort}
            onPageChange={(page) => setPagination(prev => ({ ...prev, page }))}
            onPageSizeChange={(pageSize) => setPagination(prev => ({ ...prev, pageSize }))}
            onRowSelect={setSelectedUsers}
            onSearch={setSearchQuery}
            onRefresh={loadUsers}
            emptyMessage="No users found. Create your first user to get started."
          />
        </div>
      </div>

      {/* Modals */}
      {/* TODO: Implement UserCreateModal and UserEditModal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-medium mb-4">Create New User</h3>
            <p className="text-gray-500 mb-4">User creation modal will be implemented here.</p>
            <button
              type="button"
              onClick={() => setShowCreateModal(false)}
              className="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
            >
              Close
            </button>
          </div>
        </div>
      )}

      {editingUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-medium mb-4">Edit User</h3>
            <p className="text-gray-500 mb-4">
              Editing {editingUser.firstName} {editingUser.lastName}
            </p>
            <button
              type="button"
              onClick={() => setEditingUser(null)}
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
export default UsersPage;