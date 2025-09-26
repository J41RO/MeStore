/**
 * Admin Sidebar Component
 *
 * Main sidebar component that integrates the complete navigation system
 * with header, user information, and enterprise navigation categories.
 *
 * Features:
 * - Complete navigation integration
 * - Collapsible sidebar functionality
 * - User profile display
 * - Role-based access control
 * - Performance optimization
 * - Accessibility compliance
 *
 * @version 1.0.0
 * @author React Specialist AI
 */

import React, {
  memo,
  useCallback,
  useMemo,
  useState,
  useEffect
} from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  MenuIcon,
  XIcon,
  UserIcon,
  LogOutIcon,
  SettingsIcon
} from 'lucide-react';

import type {
  UserRole,
  NavigationItem
} from './NavigationTypes';

import { NavigationProvider } from './NavigationProvider';
import { CategoryNavigation } from './CategoryNavigation';
import { enterpriseNavigationConfig } from './NavigationConfig';

/**
 * AdminSidebar component props
 */
export interface AdminSidebarProps {
  /** Whether the sidebar is collapsed */
  isCollapsed?: boolean;

  /** Callback when collapse state changes */
  onToggleCollapse?: () => void;

  /** Additional CSS classes */
  className?: string;

  /** User role for access control */
  userRole?: UserRole;

  /** User information */
  user?: {
    id: string;
    email: string;
    role: UserRole;
    isActive: boolean;
  };

  /** Custom logo URL */
  logoUrl?: string;

  /** Sidebar title */
  title?: string;
}

/**
 * AdminSidebar Component
 */
export const AdminSidebar: React.FC<AdminSidebarProps> = memo(({
  isCollapsed = false,
  onToggleCollapse,
  className = '',
  userRole = UserRole.ADMIN,
  user,
  logoUrl,
  title = 'MeStore Admin'
}) => {
  const location = useLocation();
  const navigate = useNavigate();

  // Internal state for sidebar if not controlled externally
  const [internalCollapsed, setInternalCollapsed] = useState(isCollapsed);
  const isControlled = onToggleCollapse !== undefined;
  const collapsed = isControlled ? isCollapsed : internalCollapsed;

  /**
   * Handle collapse toggle
   */
  const handleToggleCollapse = useCallback(() => {
    if (isControlled) {
      onToggleCollapse?.();
    } else {
      setInternalCollapsed(prev => !prev);
    }
  }, [isControlled, onToggleCollapse]);

  /**
   * Handle navigation item clicks
   */
  const handleItemClick = useCallback((item: NavigationItem) => {
    // Navigation will be handled by the NavigationItem component
    // This is just for additional tracking or logic if needed
    console.log(`Navigating to: ${item.title} (${item.path})`);
  }, []);

  /**
   * Handle category toggle
   */
  const handleCategoryToggle = useCallback((categoryId: string) => {
    console.log(`Toggled category: ${categoryId}`);
  }, []);

  /**
   * Handle user profile click
   */
  const handleProfileClick = useCallback(() => {
    navigate('/admin-secure-portal/profile');
  }, [navigate]);

  /**
   * Handle logout
   */
  const handleLogout = useCallback(() => {
    // This would typically call an auth service
    console.log('Logout clicked');
  }, []);

  /**
   * Get user display name
   */
  const userDisplayName = useMemo(() => {
    if (!user) return 'Admin User';
    return user.email.split('@')[0] || 'Admin User';
  }, [user]);

  /**
   * Sidebar container classes
   */
  const sidebarClasses = useMemo(() => `
    flex flex-col h-full bg-white border-r border-gray-200 shadow-lg
    transition-all duration-300 ease-in-out
    ${collapsed ? 'w-16' : 'w-64'}
    ${className}
  `.trim(), [collapsed, className]);

  /**
   * Header classes
   */
  const headerClasses = useMemo(() => `
    flex items-center justify-between px-4 py-3 border-b border-gray-200
    ${collapsed ? 'px-2' : 'px-4'}
  `.trim(), [collapsed]);

  return (
    <NavigationProvider
      categories={enterpriseNavigationConfig}
      userRole={userRole}
      onError={(error) => console.error('Navigation Error:', error)}
    >
      <div className={sidebarClasses} data-testid="admin-sidebar">
        {/* Header Section */}
        <div className={headerClasses}>
          {/* Logo and Title */}
          <div className="flex items-center min-w-0">
            {logoUrl ? (
              <img
                src={logoUrl}
                alt={title}
                className={`flex-shrink-0 ${collapsed ? 'w-8 h-8' : 'w-10 h-10'}`}
              />
            ) : (
              <div
                className={`
                  flex-shrink-0 bg-blue-600 text-white rounded-lg
                  flex items-center justify-center font-bold
                  ${collapsed ? 'w-8 h-8 text-sm' : 'w-10 h-10 text-lg'}
                `}
              >
                {collapsed ? 'M' : 'MS'}
              </div>
            )}

            {!collapsed && (
              <h1 className="ml-3 text-lg font-semibold text-gray-900 truncate">
                {title}
              </h1>
            )}
          </div>

          {/* Collapse Toggle Button */}
          <button
            type="button"
            onClick={handleToggleCollapse}
            className={`
              p-1.5 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
              transition-colors duration-150
            `}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            data-testid="collapse-toggle"
          >
            {collapsed ? (
              <MenuIcon className="w-5 h-5" />
            ) : (
              <XIcon className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* Navigation Section */}
        <div className="flex-1 overflow-y-auto py-4">
          <CategoryNavigation
            categories={enterpriseNavigationConfig}
            userRole={userRole}
            onItemClick={handleItemClick}
            onCategoryToggle={handleCategoryToggle}
            className="px-2"
          />
        </div>

        {/* User Profile Section */}
        <div className="border-t border-gray-200 p-4">
          {collapsed ? (
            <button
              type="button"
              onClick={handleProfileClick}
              className={`
                w-full p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                transition-colors duration-150
              `}
              aria-label={`User profile: ${userDisplayName}`}
              data-testid="user-profile-collapsed"
            >
              <UserIcon className="w-6 h-6 mx-auto" />
            </button>
          ) : (
            <div className="space-y-2">
              {/* User Info */}
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <UserIcon className="w-8 h-8 text-gray-400" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {userDisplayName}
                  </p>
                  <p className="text-xs text-gray-500 truncate">
                    {userRole.charAt(0).toUpperCase() + userRole.slice(1)}
                  </p>
                </div>
              </div>

              {/* User Actions */}
              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={handleProfileClick}
                  className={`
                    flex-1 flex items-center justify-center px-3 py-2 text-xs
                    text-gray-600 bg-gray-50 rounded-md hover:bg-gray-100
                    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                    transition-colors duration-150
                  `}
                  data-testid="user-profile-button"
                >
                  <SettingsIcon className="w-3 h-3 mr-1" />
                  Profile
                </button>

                <button
                  type="button"
                  onClick={handleLogout}
                  className={`
                    flex-1 flex items-center justify-center px-3 py-2 text-xs
                    text-red-600 bg-red-50 rounded-md hover:bg-red-100
                    focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2
                    transition-colors duration-150
                  `}
                  data-testid="logout-button"
                >
                  <LogOutIcon className="w-3 h-3 mr-1" />
                  Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </NavigationProvider>
  );
});

/**
 * Display name for debugging
 */
AdminSidebar.displayName = 'AdminSidebar';

/**
 * Default export
 */
export default AdminSidebar;