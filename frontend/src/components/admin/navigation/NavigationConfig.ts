/**
 * Enterprise Navigation Configuration
 *
 * Defines the complete hierarchical navigation structure for MeStore admin panel
 * with 4 main categories and their respective items as per enterprise requirements.
 *
 * @version 1.0.0
 * @author System Architect AI
 */

import {
  Users,
  UserCheck,
  UserPlus,
  Shield,
  Store,
  Package,
  ShoppingCart,
  Truck,
  TrendingUp,
  BarChart3,
  FileBarChart,
  Activity,
  DollarSign,
  Settings,
  Lock,
  Database,
  Bell,
  Globe
} from 'lucide-react';

import type { NavigationCategory, CategoryTheme } from './NavigationTypes';
import { UserRole } from './NavigationTypes';

/**
 * Category themes for visual consistency
 */
const categoryThemes: Record<string, CategoryTheme> = {
  users: {
    primary: '#3B82F6', // Blue
    secondary: '#1D4ED8',
    text: '#1E40AF',
    background: '#EFF6FF'
  },
  vendors: {
    primary: '#10B981', // Emerald
    secondary: '#047857',
    text: '#065F46',
    background: '#ECFDF5'
  },
  analytics: {
    primary: '#8B5CF6', // Violet
    secondary: '#7C3AED',
    text: '#6D28D9',
    background: '#F3E8FF'
  },
  settings: {
    primary: '#6B7280', // Gray
    secondary: '#4B5563',
    text: '#374151',
    background: '#F9FAFB'
  }
};

/**
 * USERS Category - Gestión de Usuarios (4 items)
 * Comprehensive user management with enterprise features
 */
const usersCategory: NavigationCategory = {
  id: 'users',
  title: 'Users',
  icon: Users,
  isCollapsed: false,
  order: 1,
  description: 'Comprehensive user management and access control',
  theme: categoryThemes.users,
  requiredRole: UserRole.ADMIN,
  items: [
    {
      id: 'user-list',
      title: 'User Management',
      path: '/admin-secure-portal/users',
      icon: Users,
      description: 'View, create, edit and manage all system users',
      requiredRole: UserRole.ADMIN,
      metadata: {
        keywords: ['users', 'management', 'accounts'],
        analyticsId: 'nav_users_list',
        priority: 1
      }
    },
    {
      id: 'user-roles',
      title: 'Roles & Permissions',
      path: '/admin-secure-portal/roles',
      icon: Shield,
      description: 'Configure user roles and permission levels',
      requiredRole: UserRole.SUPERUSER,
      metadata: {
        keywords: ['roles', 'permissions', 'access'],
        analyticsId: 'nav_user_roles',
        priority: 2
      }
    },
    {
      id: 'user-registration',
      title: 'User Registration',
      path: '/admin-secure-portal/user-registration',
      icon: UserPlus,
      description: 'Register new users and manage registration process',
      requiredRole: UserRole.ADMIN,
      metadata: {
        keywords: ['registration', 'new users', 'signup'],
        analyticsId: 'nav_user_registration',
        priority: 3
      }
    },
    {
      id: 'user-authentication',
      title: 'Authentication Logs',
      path: '/admin-secure-portal/auth-logs',
      icon: UserCheck,
      description: 'Monitor user authentication and security events',
      requiredRole: UserRole.SUPERUSER,
      metadata: {
        keywords: ['authentication', 'security', 'logs'],
        analyticsId: 'nav_auth_logs',
        priority: 4
      }
    }
  ]
};

/**
 * VENDORS Category - Gestión de Vendors (5 items)
 * Complete vendor lifecycle management
 */
const vendorsCategory: NavigationCategory = {
  id: 'vendors',
  title: 'Vendors',
  icon: Store,
  isCollapsed: false,
  order: 2,
  description: 'Complete vendor management and marketplace operations',
  theme: categoryThemes.vendors,
  requiredRole: UserRole.MANAGER,
  items: [
    {
      id: 'vendor-list',
      title: 'Vendor Directory',
      path: '/admin-secure-portal/vendors',
      icon: Store,
      description: 'View and manage all registered vendors',
      requiredRole: UserRole.MANAGER,
      metadata: {
        keywords: ['vendors', 'sellers', 'directory'],
        analyticsId: 'nav_vendor_list',
        priority: 1
      }
    },
    {
      id: 'vendor-applications',
      title: 'Vendor Applications',
      path: '/admin-secure-portal/vendor-applications',
      icon: Package,
      description: 'Review and approve new vendor registration applications',
      requiredRole: UserRole.ADMIN,
      metadata: {
        keywords: ['applications', 'approval', 'registration'],
        analyticsId: 'nav_vendor_applications',
        priority: 2
      }
    },
    {
      id: 'vendor-products',
      title: 'Product Catalog',
      path: '/admin-secure-portal/vendor-products',
      icon: ShoppingCart,
      description: 'Manage vendor products and inventory oversight',
      requiredRole: UserRole.MANAGER,
      metadata: {
        keywords: ['products', 'catalog', 'inventory'],
        analyticsId: 'nav_vendor_products',
        priority: 3
      }
    },
    {
      id: 'vendor-orders',
      title: 'Vendor Orders',
      path: '/admin-secure-portal/vendor-orders',
      icon: Truck,
      description: 'Monitor and manage vendor order fulfillment',
      requiredRole: UserRole.MANAGER,
      metadata: {
        keywords: ['orders', 'fulfillment', 'shipping'],
        analyticsId: 'nav_vendor_orders',
        priority: 4
      }
    },
    {
      id: 'vendor-commissions',
      title: 'Commission Management',
      path: '/admin-secure-portal/vendor-commissions',
      icon: DollarSign,
      description: 'Manage vendor commissions and payout schedules',
      requiredRole: UserRole.ADMIN,
      metadata: {
        keywords: ['commissions', 'payouts', 'earnings'],
        analyticsId: 'nav_vendor_commissions',
        priority: 5
      }
    }
  ]
};

/**
 * ANALYTICS Category - Analytics y Reportes (5 items)
 * Comprehensive business intelligence and reporting
 */
const analyticsCategory: NavigationCategory = {
  id: 'analytics',
  title: 'Analytics',
  icon: TrendingUp,
  isCollapsed: false,
  order: 3,
  description: 'Business intelligence, analytics and comprehensive reporting',
  theme: categoryThemes.analytics,
  requiredRole: UserRole.MANAGER,
  items: [
    {
      id: 'analytics-dashboard',
      title: 'Analytics Dashboard',
      path: '/admin-secure-portal/analytics',
      icon: BarChart3,
      description: 'Main analytics dashboard with key performance indicators',
      requiredRole: UserRole.MANAGER,
      metadata: {
        keywords: ['analytics', 'dashboard', 'kpi'],
        analyticsId: 'nav_analytics_dashboard',
        priority: 1
      }
    },
    {
      id: 'sales-reports',
      title: 'Sales Reports',
      path: '/admin-secure-portal/sales-reports',
      icon: TrendingUp,
      description: 'Comprehensive sales analytics and performance reports',
      requiredRole: UserRole.MANAGER,
      metadata: {
        keywords: ['sales', 'reports', 'revenue'],
        analyticsId: 'nav_sales_reports',
        priority: 2
      }
    },
    {
      id: 'financial-reports',
      title: 'Financial Reports',
      path: '/admin-secure-portal/financial-reports',
      icon: DollarSign,
      description: 'Financial statements, P&L and accounting reports',
      requiredRole: UserRole.ADMIN,
      metadata: {
        keywords: ['financial', 'accounting', 'profit'],
        analyticsId: 'nav_financial_reports',
        priority: 3
      }
    },
    {
      id: 'performance-metrics',
      title: 'Performance Metrics',
      path: '/admin-secure-portal/performance',
      icon: Activity,
      description: 'System performance and operational metrics',
      requiredRole: UserRole.MANAGER,
      metadata: {
        keywords: ['performance', 'metrics', 'operations'],
        analyticsId: 'nav_performance_metrics',
        priority: 4
      }
    },
    {
      id: 'custom-reports',
      title: 'Custom Reports',
      path: '/admin-secure-portal/custom-reports',
      icon: FileBarChart,
      description: 'Create and manage custom business reports',
      requiredRole: UserRole.ADMIN,
      metadata: {
        keywords: ['custom', 'reports', 'business'],
        analyticsId: 'nav_custom_reports',
        priority: 5
      }
    }
  ]
};

/**
 * SETTINGS Category - Configuración (5 items)
 * System configuration and administrative settings
 */
const settingsCategory: NavigationCategory = {
  id: 'settings',
  title: 'Settings',
  icon: Settings,
  isCollapsed: false,
  order: 4,
  description: 'System configuration and administrative settings',
  theme: categoryThemes.settings,
  requiredRole: UserRole.ADMIN,
  items: [
    {
      id: 'system-config',
      title: 'System Configuration',
      path: '/admin-secure-portal/system-config',
      icon: Settings,
      description: 'Core system settings and configuration management',
      requiredRole: UserRole.SUPERUSER,
      metadata: {
        keywords: ['system', 'configuration', 'settings'],
        analyticsId: 'nav_system_config',
        priority: 1
      }
    },
    {
      id: 'security-settings',
      title: 'Security Settings',
      path: '/admin-secure-portal/security',
      icon: Lock,
      description: 'Security policies, authentication and access control',
      requiredRole: UserRole.SUPERUSER,
      metadata: {
        keywords: ['security', 'authentication', 'policies'],
        analyticsId: 'nav_security_settings',
        priority: 2
      }
    },
    {
      id: 'database-management',
      title: 'Database Management',
      path: '/admin-secure-portal/database',
      icon: Database,
      description: 'Database administration and data management tools',
      requiredRole: UserRole.SUPERUSER,
      metadata: {
        keywords: ['database', 'data', 'administration'],
        analyticsId: 'nav_database_management',
        priority: 3
      }
    },
    {
      id: 'notification-settings',
      title: 'Notifications',
      path: '/admin-secure-portal/notifications',
      icon: Bell,
      description: 'Configure system notifications and alert preferences',
      requiredRole: UserRole.ADMIN,
      metadata: {
        keywords: ['notifications', 'alerts', 'messaging'],
        analyticsId: 'nav_notifications',
        priority: 4
      }
    },
    {
      id: 'integration-settings',
      title: 'Integrations',
      path: '/admin-secure-portal/integrations',
      icon: Globe,
      description: 'Third-party integrations and API configurations',
      requiredRole: UserRole.ADMIN,
      metadata: {
        keywords: ['integrations', 'api', 'third-party'],
        analyticsId: 'nav_integrations',
        priority: 5
      }
    }
  ]
};

/**
 * Complete navigation configuration
 * Array of all enterprise categories in priority order
 */
export const enterpriseNavigationConfig: NavigationCategory[] = [
  usersCategory,
  vendorsCategory,
  analyticsCategory,
  settingsCategory
];

/**
 * Navigation configuration metadata
 */
export const navigationMetadata = {
  version: '1.0.0',
  totalCategories: enterpriseNavigationConfig.length,
  totalItems: enterpriseNavigationConfig.reduce((sum, category) => sum + category.items.length, 0),
  supportedRoles: Object.values(UserRole),
  lastUpdated: new Date().toISOString(),
  features: [
    'Role-based access control',
    'Category collapse/expand',
    'Lazy loading support',
    'Performance optimization',
    'Accessibility compliance (WCAG AA)',
    'Analytics integration',
    'Theme customization',
    'Keyboard navigation',
    'Search functionality',
    'Mobile responsive'
  ]
};

/**
 * Utility functions for navigation configuration
 */
export const navigationConfigUtils = {
  /**
   * Get navigation category by ID
   */
  getCategoryById: (id: string): NavigationCategory | undefined => {
    return enterpriseNavigationConfig.find(category => category.id === id);
  },

  /**
   * Get navigation item by ID across all categories
   */
  getItemById: (itemId: string): { category: NavigationCategory; item: any } | undefined => {
    for (const category of enterpriseNavigationConfig) {
      const item = category.items.find(item => item.id === itemId);
      if (item) {
        return { category, item };
      }
    }
    return undefined;
  },

  /**
   * Get categories accessible by user role
   */
  getCategoriesByRole: (userRole: UserRole): NavigationCategory[] => {
    const roleHierarchy = {
      [UserRole.VIEWER]: 0,
      [UserRole.OPERATOR]: 1,
      [UserRole.MANAGER]: 2,
      [UserRole.ADMIN]: 3,
      [UserRole.SUPERUSER]: 4
    };

    return enterpriseNavigationConfig.filter(category => {
      if (!category.requiredRole) return true;
      return roleHierarchy[userRole] >= roleHierarchy[category.requiredRole];
    });
  },

  /**
   * Get items in category accessible by user role
   */
  getItemsByRole: (category: NavigationCategory, userRole: UserRole): any[] => {
    const roleHierarchy = {
      [UserRole.VIEWER]: 0,
      [UserRole.OPERATOR]: 1,
      [UserRole.MANAGER]: 2,
      [UserRole.ADMIN]: 3,
      [UserRole.SUPERUSER]: 4
    };

    return category.items.filter(item => {
      if (!item.requiredRole) return true;
      return roleHierarchy[userRole] >= roleHierarchy[item.requiredRole];
    });
  },

  /**
   * Validate navigation configuration
   */
  validateConfig: (): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];

    // Check for unique category IDs
    const categoryIds = new Set();
    for (const category of enterpriseNavigationConfig) {
      if (categoryIds.has(category.id)) {
        errors.push(`Duplicate category ID: ${category.id}`);
      }
      categoryIds.add(category.id);

      // Check for unique item IDs within category
      const itemIds = new Set();
      for (const item of category.items) {
        if (itemIds.has(item.id)) {
          errors.push(`Duplicate item ID in category ${category.id}: ${item.id}`);
        }
        itemIds.add(item.id);
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }
};

/**
 * Default export for easy consumption
 */
export default enterpriseNavigationConfig;