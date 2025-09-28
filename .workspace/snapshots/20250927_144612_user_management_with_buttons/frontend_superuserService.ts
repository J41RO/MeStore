import axios from 'axios';

// Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? 'http://192.168.1.137:8000' : 'http://192.168.1.137:8000');

const superuserApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor to add auth token
superuserApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
superuserApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/admin-login';
    }
    return Promise.reject(error);
  }
);

// Types matching backend schemas
export interface UserSummary {
  id: string;
  email: string;
  nombre: string | null;
  apellido: string | null;
  full_name: string;
  user_type: 'BUYER' | 'VENDOR' | 'ADMIN' | 'SUPERUSER';
  is_active: boolean;
  is_verified: boolean;
  email_verified: boolean;
  phone_verified: boolean;
  created_at: string;
  last_login: string | null;
  vendor_status: string | null;
  business_name: string | null;
  security_clearance_level: number | null;
  department_id: string | null;
  failed_login_attempts: number | null;
  account_locked: boolean;
}

export interface UserDetailedInfo {
  id: string;
  email: string;
  nombre: string | null;
  apellido: string | null;
  full_name: string;
  user_type: 'BUYER' | 'VENDOR' | 'ADMIN' | 'SUPERUSER';
  is_active: boolean;
  is_verified: boolean;
  email_verified: boolean;
  phone_verified: boolean;
  last_login: string | null;
  cedula: string | null;
  telefono: string | null;
  ciudad: string | null;
  empresa: string | null;
  direccion: string | null;
  vendor_status: string | null;
  business_name: string | null;
  business_description: string | null;
  website_url: string | null;
  security_clearance_level: number | null;
  department_id: string | null;
  employee_id: string | null;
  performance_score: number | null;
  failed_login_attempts: number;
  account_locked_until: string | null;
  force_password_change: boolean;
  bank_name: string | null;
  account_holder_name: string | null;
  account_number: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserListResponse {
  users: UserSummary[];
  total: number;
  page: number;
  size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
  filters_applied: Record<string, any>;
  summary_stats: Record<string, any>;
}

export interface UserStatsResponse {
  total_users: number;
  active_users: number;
  inactive_users: number;
  verified_users: number;
  buyers: number;
  vendors: number;
  admins: number;
  superusers: number;
  email_verified: number;
  phone_verified: number;
  both_verified: number;
  created_today: number;
  created_this_week: number;
  created_this_month: number;
  vendor_stats: Record<string, number>;
  recent_logins: number;
  locked_accounts: number;
  calculated_at: string;
  period: string;
}

export interface UserFilters {
  search?: string;
  email?: string;
  user_type?: 'BUYER' | 'VENDOR' | 'ADMIN' | 'SUPERUSER';
  status?: 'all' | 'active' | 'inactive' | 'verified' | 'unverified' | 'email_verified' | 'phone_verified';
  is_active?: boolean;
  is_verified?: boolean;
  email_verified?: boolean;
  phone_verified?: boolean;
  created_after?: string;
  created_before?: string;
  last_login_after?: string;
  last_login_before?: string;
  security_clearance_min?: number;
  security_clearance_max?: number;
  department_id?: string;
  sort_by?: 'created_at_desc' | 'created_at_asc' | 'email_asc' | 'email_desc' | 'last_login_desc' | 'last_login_asc' | 'user_type' | 'is_active';
}

export interface CreateUserData {
  email: string;
  password: string;
  nombre: string;
  apellido: string;
  user_type: 'BUYER' | 'VENDOR' | 'ADMIN' | 'SUPERUSER';
  cedula?: string;
  telefono?: string;
  ciudad?: string;
  empresa?: string;
  direccion?: string;
  is_active?: boolean;
  is_verified?: boolean;
  security_clearance_level?: number;
  created_by_admin?: boolean;
  notes?: string;
}

export interface UpdateUserData {
  nombre?: string;
  apellido?: string;
  user_type?: 'BUYER' | 'VENDOR' | 'ADMIN' | 'SUPERUSER';
  cedula?: string;
  telefono?: string;
  ciudad?: string;
  empresa?: string;
  direccion?: string;
  is_active?: boolean;
  is_verified?: boolean;
  email_verified?: boolean;
  phone_verified?: boolean;
  security_clearance_level?: number;
  department_id?: string;
  employee_id?: string;
  performance_score?: number;
  force_password_change?: boolean;
  failed_login_attempts?: number;
  admin_notes?: string;
}

export interface BulkUserActionRequest {
  user_ids: string[];
  action: 'activate' | 'deactivate' | 'verify_email' | 'unverify_email' | 'reset_failed_attempts' | 'force_password_change' | 'update_clearance';
  reason?: string;
  parameters?: Record<string, any>;
}

export interface BulkUserActionResponse {
  success: boolean;
  action: string;
  total_requested: number;
  successful: number;
  failed: number;
  successful_users: string[];
  failed_users: Array<{ id: string; reason: string }>;
  warnings: string[];
  processed_at: string;
  processed_by: string;
}

// Legacy types for compatibility
export interface User extends UserSummary {}
export interface UsersResponse extends UserListResponse {}
export interface SuperuserDashboardStats extends UserStatsResponse {
  usersByType: {
    BUYER: number;
    VENDOR: number;
    ADMIN: number;
    SUPERUSER: number;
  };
  recentActivity: {
    date: string;
    newUsers: number;
    activeUsers: number;
  }[];
}

// Superuser Service
export class SuperuserService {
  // Dashboard Statistics
  async getDashboardStats(): Promise<SuperuserDashboardStats> {
    try {
      // Get real statistics from backend
      const response = await superuserApi.get('/api/v1/superuser-admin/users/stats');
      const stats: UserStatsResponse = response.data;

      // Transform to legacy format for compatibility
      const usersByType = {
        BUYER: stats.buyers,
        VENDOR: stats.vendors,
        ADMIN: stats.admins,
        SUPERUSER: stats.superusers,
      };

      // Mock recent activity for now (backend doesn't provide this yet)
      const recentActivity = Array.from({ length: 7 }, (_, i) => ({
        date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        newUsers: Math.floor(Math.random() * 5) + 1,
        activeUsers: Math.floor(Math.random() * 20) + 10,
      })).reverse();

      return {
        ...stats,
        totalUsers: stats.total_users,
        activeUsers: stats.active_users,
        verifiedUsers: stats.verified_users,
        usersByType,
        recentActivity,
      };
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      // Return mock data as fallback
      return {
        total_users: 0,
        active_users: 0,
        inactive_users: 0,
        verified_users: 0,
        buyers: 0,
        vendors: 0,
        admins: 0,
        superusers: 0,
        email_verified: 0,
        phone_verified: 0,
        both_verified: 0,
        created_today: 0,
        created_this_week: 0,
        created_this_month: 0,
        vendor_stats: {},
        recent_logins: 0,
        locked_accounts: 0,
        calculated_at: new Date().toISOString(),
        period: 'all_time',
        totalUsers: 0,
        activeUsers: 0,
        verifiedUsers: 0,
        usersByType: { BUYER: 0, VENDOR: 0, ADMIN: 0, SUPERUSER: 0 },
        recentActivity: [],
      };
    }
  }

  // User Management
  async getUsers(page: number = 1, size: number = 10, filters?: UserFilters): Promise<UserListResponse> {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        size: size.toString(),
      });

      // Add filters to params
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null && value !== '') {
            params.append(key, value.toString());
          }
        });
      }

      const response = await superuserApi.get(`/api/v1/superuser-admin/users?${params}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching users:', error);
      throw error;
    }
  }

  async getUserById(userId: string): Promise<UserDetailedInfo> {
    try {
      const response = await superuserApi.get(`/api/v1/superuser-admin/users/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching user:', error);
      throw error;
    }
  }

  async createUser(userData: CreateUserData): Promise<UserDetailedInfo> {
    try {
      const response = await superuserApi.post('/api/v1/superuser-admin/users', userData);
      return response.data;
    } catch (error) {
      console.error('Error creating user:', error);
      throw error;
    }
  }

  async updateUser(userId: string, userData: UpdateUserData): Promise<UserDetailedInfo> {
    try {
      const response = await superuserApi.put(`/api/v1/superuser-admin/users/${userId}`, userData);
      return response.data;
    } catch (error) {
      console.error('Error updating user:', error);
      throw error;
    }
  }

  async deleteUser(userId: string, reason?: string): Promise<{ success: boolean; message: string }> {
    try {
      const params = reason ? `?reason=${encodeURIComponent(reason)}` : '';
      await superuserApi.delete(`/api/v1/superuser-admin/users/${userId}${params}`);
      return { success: true, message: 'User deleted successfully' };
    } catch (error) {
      console.error('Error deleting user:', error);
      throw error;
    }
  }

  async toggleUserStatus(userId: string): Promise<UserDetailedInfo> {
    try {
      // Get current user to toggle status
      const user = await this.getUserById(userId);
      const updatedData: UpdateUserData = {
        is_active: !user.is_active
      };
      return await this.updateUser(userId, updatedData);
    } catch (error) {
      console.error('Error toggling user status:', error);
      throw error;
    }
  }

  // Admin Operations
  async resetUserPassword(userId: string): Promise<{ success: boolean }> {
    try {
      // Force password change on next login
      await this.updateUser(userId, { force_password_change: true });
      return { success: true };
    } catch (error) {
      console.error('Error forcing password reset:', error);
      throw error;
    }
  }

  async resendVerificationEmail(userId: string): Promise<{ success: boolean }> {
    try {
      // Mark email as unverified to force re-verification
      await this.updateUser(userId, { email_verified: false });
      return { success: true };
    } catch (error) {
      console.error('Error resending verification:', error);
      throw error;
    }
  }

  async getUserAuditLog(userId: string): Promise<any[]> {
    try {
      // Use dependencies endpoint as audit alternative
      const response = await superuserApi.get(`/api/v1/superuser-admin/users/${userId}/dependencies`);
      return [response.data] || [];
    } catch (error) {
      console.error('Error fetching user info:', error);
      return [];
    }
  }

  // Bulk Operations
  async bulkUpdateUsers(userIds: string[], action: string, parameters?: Record<string, any>): Promise<BulkUserActionResponse> {
    try {
      const request: BulkUserActionRequest = {
        user_ids: userIds,
        action: action as any,
        reason: 'Bulk operation from admin panel',
        parameters: parameters || {}
      };

      const response = await superuserApi.post('/api/v1/superuser-admin/users/bulk-action', request);
      return response.data;
    } catch (error) {
      console.error('Error bulk updating users:', error);
      throw error;
    }
  }

  async exportUsers(filters?: UserFilters): Promise<Blob> {
    try {
      // Get all users and create CSV export
      const users = await this.getUsers(1, 1000, filters);
      const csvContent = this.convertToCSV(users.users);
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      return blob;
    } catch (error) {
      console.error('Error exporting users:', error);
      throw error;
    }
  }

  private convertToCSV(users: UserSummary[]): string {
    const headers = [
      'ID', 'Email', 'Nombre', 'Apellido', 'Tipo de Usuario',
      'Activo', 'Verificado', 'Email Verificado', 'Teléfono Verificado',
      'Fecha de Creación', 'Último Login', 'Estado Vendor', 'Nivel Seguridad'
    ];

    const csvContent = [
      headers.join(','),
      ...users.map(user => [
        user.id,
        user.email,
        user.nombre || '',
        user.apellido || '',
        user.user_type,
        user.is_active ? 'Sí' : 'No',
        user.is_verified ? 'Sí' : 'No',
        user.email_verified ? 'Sí' : 'No',
        user.phone_verified ? 'Sí' : 'No',
        new Date(user.created_at).toLocaleDateString(),
        user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Nunca',
        user.vendor_status || 'N/A',
        user.security_clearance_level || 'N/A'
      ].join(','))
    ].join('\n');

    return csvContent;
  }

  // Health check
  async healthCheck(): Promise<{ status: string; module: string }> {
    try {
      const response = await superuserApi.get('/api/v1/superuser-admin/health');
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const superuserService = new SuperuserService();
export default superuserService;