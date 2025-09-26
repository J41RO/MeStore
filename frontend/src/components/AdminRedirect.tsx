import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore, UserType } from '../stores/authStore';
import AdminRestricted from '../pages/AdminRestricted';

/**
 * AdminRedirect Component
 *
 * Inteligently redirects admin users to secure portal or shows restriction page
 * - ADMIN/SUPERUSER users: Redirect to /admin-secure-portal/dashboard
 * - Other users: Show AdminRestricted page
 * - Unauthenticated users: Show AdminRestricted page
 */
const AdminRedirect: React.FC = () => {
  const { user, isAuthenticated } = useAuthStore();

  // DEBUG logging for troubleshooting
  console.log('🔍 AdminRedirect DEBUG:');
  console.log('📊 isAuthenticated:', isAuthenticated);
  console.log('👤 user:', user);
  console.log('🎭 user?.user_type:', user?.user_type);

  // If not authenticated, show restricted access page
  if (!isAuthenticated || !user) {
    console.log('❌ Not authenticated - showing AdminRestricted');
    return <AdminRestricted />;
  }

  // Check if user has admin privileges
  const isAdminUser = user.user_type === UserType.ADMIN || user.user_type === UserType.SUPERUSER;

  if (isAdminUser) {
    console.log('✅ Admin user detected - redirecting to secure portal');
    return <Navigate to="/admin-secure-portal/dashboard" replace />;
  }

  // For any other user type, show restriction page
  console.log('❌ Non-admin user - showing AdminRestricted');
  return <AdminRestricted />;
};

export default AdminRedirect;