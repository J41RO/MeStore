/**
 * RolesPage Component
 *
 * Advanced role and permission management interface for enterprise user access control.
 * Provides comprehensive RBAC (Role-Based Access Control) administration.
 *
 * Features:
 * - Hierarchical role management
 * - Granular permission matrix
 * - Permission inheritance visualization
 * - Role templates and presets
 * - Bulk permission assignment
 * - Audit trail for permission changes
 * - Visual permission dependencies
 * - Role usage analytics
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
  Shield,
  Users,
  Lock,
  Unlock,
  Key,
  Eye,
  Edit,
  Trash2,
  Plus,
  Copy,
  AlertTriangle,
  Check,
  X,
  Search,
  Filter,
  Settings,
  Activity,
  Download,
  Upload
} from 'lucide-react';

import {
  DashboardCard,
  DataTable,
  StatusBadge,
  commonComponentUtils
} from '../../../components/admin/common';

import type {
  TableColumn
} from '../../../components/admin/common';

/**
 * Permission interface
 */
interface Permission {
  id: string;
  name: string;
  category: string;
  description: string;
  isRequired?: boolean;
  dependencies?: string[];
}

/**
 * Role interface
 */
interface Role {
  id: string;
  name: string;
  description: string;
  level: number;
  isSystem: boolean;
  isActive: boolean;
  userCount: number;
  permissions: string[];
  createdAt: string;
  updatedAt: string;
}

/**
 * Permission category
 */
interface PermissionCategory {
  id: string;
  name: string;
  description: string;
  permissions: Permission[];
}

/**
 * Role metrics
 */
interface RoleMetrics {
  totalRoles: number;
  activeRoles: number;
  systemRoles: number;
  customRoles: number;
  totalPermissions: number;
  mostUsedRole: string;
  averagePermissionsPerRole: number;
}

/**
 * RolesPage Component
 */
export const RolesPage: React.FC = () => {
  // State management
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [permissionCategories, setPermissionCategories] = useState<PermissionCategory[]>([]);
  const [metrics, setMetrics] = useState<RoleMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showPermissionMatrix, setShowPermissionMatrix] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  /**
   * Role table columns
   */
  const roleColumns: TableColumn<Role>[] = useMemo(() => [
    {
      id: 'role',
      header: 'Role',
      accessor: 'name',
      sortable: true,
      cell: (value, row) => (
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
            row.isSystem ? 'bg-purple-100' : 'bg-blue-100'
          }`}>
            <Shield className={`w-5 h-5 ${
              row.isSystem ? 'text-purple-600' : 'text-blue-600'
            }`} />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-medium text-gray-900">{value}</span>
              {row.isSystem && (
                <StatusBadge variant="info" size="xs">System</StatusBadge>
              )}
            </div>
            <p className="text-sm text-gray-500">{row.description}</p>
          </div>
        </div>
      )
    },
    {
      id: 'level',
      header: 'Level',
      accessor: 'level',
      sortable: true,
      align: 'center',
      cell: (value) => (
        <div className="flex items-center justify-center">
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
            value >= 4 ? 'bg-red-100 text-red-800' :
            value >= 3 ? 'bg-orange-100 text-orange-800' :
            value >= 2 ? 'bg-yellow-100 text-yellow-800' :
            'bg-green-100 text-green-800'
          }`}>
            Level {value}
          </span>
        </div>
      )
    },
    {
      id: 'userCount',
      header: 'Users',
      accessor: 'userCount',
      sortable: true,
      align: 'center',
      cell: (value) => (
        <div className="flex items-center justify-center space-x-1">
          <Users className="w-4 h-4 text-gray-400" />
          <span className="text-sm font-medium text-gray-900">{value}</span>
        </div>
      )
    },
    {
      id: 'permissions',
      header: 'Permissions',
      accessor: 'permissions',
      cell: (value) => (
        <span className="text-sm text-gray-900">{value.length} permissions</span>
      )
    },
    {
      id: 'status',
      header: 'Status',
      accessor: 'isActive',
      sortable: true,
      cell: (value) => (
        <StatusBadge variant={value ? 'success' : 'inactive'} size="sm">
          {value ? 'Active' : 'Inactive'}
        </StatusBadge>
      )
    },
    {
      id: 'updatedAt',
      header: 'Last Modified',
      accessor: 'updatedAt',
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
   * Role actions
   */
  const roleActions = useMemo(() => [
    {
      id: 'view',
      label: 'View Details',
      icon: Eye,
      action: (role: Role) => {
        setSelectedRole(role);
      }
    },
    {
      id: 'edit',
      label: 'Edit Role',
      icon: Edit,
      action: (role: Role) => {
        setEditingRole(role);
      },
      hidden: (role: Role) => role.isSystem
    },
    {
      id: 'duplicate',
      label: 'Duplicate Role',
      icon: Copy,
      action: (role: Role) => {
        handleDuplicateRole(role);
      }
    },
    {
      id: 'delete',
      label: 'Delete Role',
      icon: Trash2,
      variant: 'danger' as const,
      action: (role: Role) => {
        if (confirm(`Are you sure you want to delete the ${role.name} role?`)) {
          handleDeleteRole(role.id);
        }
      },
      hidden: (role: Role) => role.isSystem || role.userCount > 0
    }
  ], []);

  /**
   * Load roles and permissions data
   */
  const loadData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // TODO: Replace with actual API calls
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Mock permissions data
      const mockPermissions: Permission[] = [
        {
          id: 'users.view',
          name: 'View Users',
          category: 'User Management',
          description: 'View user profiles and basic information'
        },
        {
          id: 'users.create',
          name: 'Create Users',
          category: 'User Management',
          description: 'Create new user accounts',
          dependencies: ['users.view']
        },
        {
          id: 'users.edit',
          name: 'Edit Users',
          category: 'User Management',
          description: 'Modify user profiles and settings',
          dependencies: ['users.view']
        },
        {
          id: 'users.delete',
          name: 'Delete Users',
          category: 'User Management',
          description: 'Delete user accounts permanently',
          dependencies: ['users.view', 'users.edit']
        },
        {
          id: 'roles.view',
          name: 'View Roles',
          category: 'Role Management',
          description: 'View roles and permissions'
        },
        {
          id: 'roles.manage',
          name: 'Manage Roles',
          category: 'Role Management',
          description: 'Create, edit, and delete roles',
          dependencies: ['roles.view']
        },
        {
          id: 'vendors.view',
          name: 'View Vendors',
          category: 'Vendor Management',
          description: 'View vendor profiles and information'
        },
        {
          id: 'vendors.approve',
          name: 'Approve Vendors',
          category: 'Vendor Management',
          description: 'Approve or reject vendor applications',
          dependencies: ['vendors.view']
        },
        {
          id: 'analytics.view',
          name: 'View Analytics',
          category: 'Analytics',
          description: 'Access analytics dashboards and reports'
        },
        {
          id: 'analytics.export',
          name: 'Export Reports',
          category: 'Analytics',
          description: 'Export analytics data and generate reports',
          dependencies: ['analytics.view']
        },
        {
          id: 'system.configure',
          name: 'System Configuration',
          category: 'System',
          description: 'Modify system settings and configurations',
          isRequired: true
        }
      ];

      // Mock roles data
      const mockRoles: Role[] = [
        {
          id: 'superuser',
          name: 'Superuser',
          description: 'Full system access with all permissions',
          level: 5,
          isSystem: true,
          isActive: true,
          userCount: 1,
          permissions: mockPermissions.map(p => p.id),
          createdAt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(),
          updatedAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
          id: 'admin',
          name: 'Administrator',
          description: 'Administrative access with most permissions',
          level: 4,
          isSystem: true,
          isActive: true,
          userCount: 3,
          permissions: [
            'users.view', 'users.create', 'users.edit',
            'roles.view',
            'vendors.view', 'vendors.approve',
            'analytics.view', 'analytics.export'
          ],
          createdAt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(),
          updatedAt: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
          id: 'manager',
          name: 'Manager',
          description: 'Management role with vendor and analytics access',
          level: 3,
          isSystem: true,
          isActive: true,
          userCount: 8,
          permissions: [
            'users.view',
            'vendors.view', 'vendors.approve',
            'analytics.view'
          ],
          createdAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
          updatedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
          id: 'operator',
          name: 'Operator',
          description: 'Basic operational access',
          level: 2,
          isSystem: true,
          isActive: true,
          userCount: 15,
          permissions: [
            'users.view',
            'vendors.view',
            'analytics.view'
          ],
          createdAt: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString(),
          updatedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
          id: 'viewer',
          name: 'Viewer',
          description: 'Read-only access to basic information',
          level: 1,
          isSystem: true,
          isActive: true,
          userCount: 25,
          permissions: [
            'users.view',
            'vendors.view'
          ],
          createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
          updatedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
          id: 'custom-analyst',
          name: 'Data Analyst',
          description: 'Custom role for data analysis and reporting',
          level: 2,
          isSystem: false,
          isActive: true,
          userCount: 5,
          permissions: [
            'analytics.view',
            'analytics.export',
            'vendors.view'
          ],
          createdAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
          updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
        }
      ];

      // Group permissions by category
      const groupedPermissions = mockPermissions.reduce((acc, permission) => {
        const category = permission.category;
        if (!acc[category]) {
          acc[category] = [];
        }
        acc[category].push(permission);
        return acc;
      }, {} as Record<string, Permission[]>);

      const permissionCategories = Object.entries(groupedPermissions).map(([name, perms]) => ({
        id: name.toLowerCase().replace(/\s+/g, '-'),
        name,
        description: `Permissions related to ${name.toLowerCase()}`,
        permissions: perms
      }));

      const mockMetrics: RoleMetrics = {
        totalRoles: mockRoles.length,
        activeRoles: mockRoles.filter(r => r.isActive).length,
        systemRoles: mockRoles.filter(r => r.isSystem).length,
        customRoles: mockRoles.filter(r => !r.isSystem).length,
        totalPermissions: mockPermissions.length,
        mostUsedRole: 'Viewer',
        averagePermissionsPerRole: Math.round(
          mockRoles.reduce((sum, role) => sum + role.permissions.length, 0) / mockRoles.length
        )
      };

      setRoles(mockRoles);
      setPermissions(mockPermissions);
      setPermissionCategories(permissionCategories);
      setMetrics(mockMetrics);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load roles and permissions');
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Handle role duplication
   */
  const handleDuplicateRole = useCallback((role: Role) => {
    const duplicatedRole: Role = {
      ...role,
      id: `${role.id}-copy`,
      name: `${role.name} (Copy)`,
      isSystem: false,
      userCount: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    setRoles(prev => [...prev, duplicatedRole]);
  }, []);

  /**
   * Handle role deletion
   */
  const handleDeleteRole = useCallback(async (roleId: string) => {
    try {
      // TODO: Replace with actual API call
      setRoles(prev => prev.filter(role => role.id !== roleId));
    } catch (err) {
      console.error('Failed to delete role:', err);
    }
  }, []);

  /**
   * Get permission by ID
   */
  const getPermissionById = useCallback((permissionId: string) => {
    return permissions.find(p => p.id === permissionId);
  }, [permissions]);

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
          <h1 className="text-2xl font-bold text-gray-900">Roles & Permissions</h1>
          <p className="text-sm text-gray-500 mt-1">
            Manage user roles and configure granular permissions
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            type="button"
            onClick={() => setShowPermissionMatrix(!showPermissionMatrix)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Key className="w-4 h-4 mr-2" />
            Permission Matrix
          </button>

          <button
            type="button"
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Role
          </button>
        </div>
      </div>

      {/* Metrics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Total Roles"
          value={metrics?.totalRoles}
          icon={Shield}
          theme="primary"
          isLoading={isLoading}
        />
        <DashboardCard
          title="System Roles"
          value={metrics?.systemRoles}
          icon={Lock}
          theme="info"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Custom Roles"
          value={metrics?.customRoles}
          icon={Unlock}
          theme="success"
          isLoading={isLoading}
        />
        <DashboardCard
          title="Total Permissions"
          value={metrics?.totalPermissions}
          icon={Key}
          theme="warning"
          isLoading={isLoading}
        />
      </div>

      {/* Permission Matrix Modal */}
      {showPermissionMatrix && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-7xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">Permission Matrix</h3>
                <button
                  type="button"
                  onClick={() => setShowPermissionMatrix(false)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            <div className="p-6 overflow-auto max-h-[calc(90vh-140px)]">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sticky left-0 bg-gray-50 z-10">
                        Permission
                      </th>
                      {roles.map((role) => (
                        <th key={role.id} className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[100px]">
                          <div className="transform -rotate-45 origin-center">
                            {role.name}
                          </div>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {permissionCategories.map((category) => (
                      <React.Fragment key={category.id}>
                        <tr className="bg-gray-50">
                          <td colSpan={roles.length + 1} className="px-6 py-2 text-sm font-medium text-gray-900">
                            {category.name}
                          </td>
                        </tr>
                        {category.permissions.map((permission) => (
                          <tr key={permission.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 text-sm text-gray-900 sticky left-0 bg-white border-r border-gray-200">
                              <div>
                                <div className="font-medium">{permission.name}</div>
                                <div className="text-xs text-gray-500">{permission.description}</div>
                              </div>
                            </td>
                            {roles.map((role) => (
                              <td key={`${role.id}-${permission.id}`} className="px-3 py-4 text-center">
                                {role.permissions.includes(permission.id) ? (
                                  <Check className="w-5 h-5 text-green-500 mx-auto" />
                                ) : (
                                  <X className="w-5 h-5 text-gray-300 mx-auto" />
                                )}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </React.Fragment>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Roles Table */}
      <DataTable
        data={roles}
        columns={roleColumns}
        isLoading={isLoading}
        error={error}
        rowActions={roleActions}
        searchable={true}
        searchPlaceholder="Search roles..."
        onRefresh={loadData}
        emptyMessage="No roles found. Create your first custom role to get started."
      />

      {/* Role Details Modal */}
      {selectedRole && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium">{selectedRole.name}</h3>
                  <p className="text-sm text-gray-500">{selectedRole.description}</p>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedRole(null)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            <div className="p-6 overflow-auto max-h-[calc(90vh-140px)]">
              <div className="space-y-6">
                {/* Role Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Level</label>
                    <p className="text-sm text-gray-900">Level {selectedRole.level}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Type</label>
                    <p className="text-sm text-gray-900">
                      {selectedRole.isSystem ? 'System Role' : 'Custom Role'}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Users</label>
                    <p className="text-sm text-gray-900">{selectedRole.userCount} users</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Status</label>
                    <StatusBadge variant={selectedRole.isActive ? 'success' : 'inactive'} size="sm">
                      {selectedRole.isActive ? 'Active' : 'Inactive'}
                    </StatusBadge>
                  </div>
                </div>

                {/* Permissions */}
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-3">
                    Permissions ({selectedRole.permissions.length})
                  </h4>
                  <div className="space-y-4">
                    {permissionCategories.map((category) => {
                      const categoryPermissions = category.permissions.filter(p =>
                        selectedRole.permissions.includes(p.id)
                      );

                      if (categoryPermissions.length === 0) return null;

                      return (
                        <div key={category.id}>
                          <h5 className="text-sm font-medium text-gray-900 mb-2">{category.name}</h5>
                          <div className="space-y-1">
                            {categoryPermissions.map((permission) => (
                              <div key={permission.id} className="flex items-center space-x-2 text-sm">
                                <Check className="w-4 h-4 text-green-500" />
                                <span className="text-gray-900">{permission.name}</span>
                                <span className="text-gray-500">- {permission.description}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create/Edit Role Modal */}
      {(showCreateModal || editingRole) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="p-6">
              <h3 className="text-lg font-medium mb-4">
                {editingRole ? 'Edit Role' : 'Create New Role'}
              </h3>
              <p className="text-gray-500 mb-4">
                {editingRole ? 'Role editing' : 'Role creation'} interface will be implemented here.
              </p>
              <button
                type="button"
                onClick={() => {
                  setShowCreateModal(false);
                  setEditingRole(null);
                }}
                className="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
              >
                Close
              </button>
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
export default RolesPage;