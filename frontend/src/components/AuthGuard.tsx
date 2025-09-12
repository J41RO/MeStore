import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore, UserType } from '../stores/authStore';
import { useRoleAccess } from '../hooks/useRoleAccess';

interface AuthGuardProps {
  children: React.ReactNode;
  fallbackPath?: string;
  requiredRoles?: UserType[];
  requireAllRoles?: boolean;
  minimumRole?: UserType;
  unauthorizedPath?: string;
}

const AuthGuard: React.FC<AuthGuardProps> = ({
  children,
  fallbackPath = '/auth/login',
  requiredRoles,
  requireAllRoles = false,
  minimumRole,
  unauthorizedPath = '/unauthorized',
}) => {
  const { isAuthenticated, checkAuth } = useAuthStore();
  const { canAccess, hasMinimumRole, getCurrentRole } = useRoleAccess();
  const location = useLocation();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // First check: Authentication
  if (!isAuthenticated) {
    return (
      <Navigate 
        to={fallbackPath} 
        state={{ from: location.pathname }} 
        replace 
      />
    );
  }

  // Second check: Role-based authorization (if role requirements specified)
  const hasRoleRequirements = requiredRoles || minimumRole;
  
  if (hasRoleRequirements) {
    let hasPermission = true;

    // Check specific roles
    if (requiredRoles && requiredRoles.length > 0) {
      hasPermission = canAccess(requiredRoles, requireAllRoles);
    }

    // Check minimum role (hierarchical)
    if (minimumRole && hasPermission) {
      hasPermission = hasMinimumRole(minimumRole);
    }

    if (!hasPermission) {
      return (
        <Navigate 
          to={unauthorizedPath} 
          state={{ 
            from: location.pathname,
            requiredRoles,
            minimumRole,
            currentRole: getCurrentRole()
          }} 
          replace 
        />
      );
    }
  }

  return <>{children}</>;
};

export default AuthGuard;
