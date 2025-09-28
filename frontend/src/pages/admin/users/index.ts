/**
 * Admin Users Pages Index
 *
 * Centralized export for all user management pages.
 * Provides easy imports and consistent API access.
 *
 * @version 1.0.0
 * @author UX Specialist AI
 */

// User Management Pages
export { default as UsersPage } from './UsersPage';
export { default as RolesPage } from './RolesPage';
export { default as UserRegistrationPage } from './UserRegistrationPage';
export { default as AuthenticationLogsPage } from './AuthenticationLogsPage';

/**
 * Page metadata for routing and navigation
 */
export const usersPagesMetadata = {
  users: {
    path: '/admin-secure-portal/users',
    title: 'User Management',
    description: 'Manage users, view profiles, and handle user operations',
    component: 'UsersPage'
  },
  roles: {
    path: '/admin-secure-portal/roles',
    title: 'Roles & Permissions',
    description: 'Configure user roles and permission levels',
    component: 'RolesPage'
  },
  registration: {
    path: '/admin-secure-portal/user-registration',
    title: 'User Registration',
    description: 'Manage user invitations and registration workflow',
    component: 'UserRegistrationPage'
  },
  authLogs: {
    path: '/admin-secure-portal/auth-logs',
    title: 'Authentication Logs',
    description: 'Monitor authentication events and security incidents',
    component: 'AuthenticationLogsPage'
  }
};

/**
 * Required permissions for each page
 */
export const usersPagePermissions = {
  users: ['users.view'],
  roles: ['roles.view'],
  registration: ['users.create'],
  authLogs: ['system.audit']
};