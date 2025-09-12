import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { UserType } from '../stores/authStore';
import { useRoleAccess, getRoleDisplayName } from '../hooks/useRoleAccess';

export type RoleStrategy = 'exact' | 'minimum' | 'any' | 'all';

interface RoleGuardProps {
  children: React.ReactNode;
  roles: UserType[];
  strategy?: RoleStrategy;
  fallback?: React.ReactNode;
  redirectTo?: string;
  showRoleInfo?: boolean;
}

/**
 * RoleGuard component for fine-grained role-based access control
 * Assumes user is already authenticated - use after AuthGuard
 */
const RoleGuard: React.FC<RoleGuardProps> = ({
  children,
  roles,
  strategy = 'any',
  fallback,
  redirectTo,
  showRoleInfo = false,
}) => {
  const { 
    hasRole, 
    hasAnyRole, 
    hasAllRoles, 
    hasMinimumRole, 
    getCurrentRole 
  } = useRoleAccess();
  const location = useLocation();
  const currentRole = getCurrentRole();
  

  // Validate props
  if (!roles || roles.length === 0) {
    console.warn('RoleGuard: No roles specified');
    return <>{children}</>;
  }

  // Determine access based on strategy
  const hasAccess = (() => {
    switch (strategy) {
      case 'exact':
        // User must have exactly one of the specified roles
        return roles.some(role => hasRole(role));

      case 'minimum':
        // User must have at least the minimum role level
        if (roles.length !== 1) {
          console.warn('RoleGuard: minimum strategy requires exactly one role');
          return false;
        }
        return currentRole && roles[0] ? hasMinimumRole(roles[0]) : false;

      case 'any':
        // User must have any of the specified roles
        return hasAnyRole(roles);

      case 'all':
        // User must have all specified roles (usually not applicable for single-role users)
        return hasAllRoles(roles);

      default:
        console.warn(`RoleGuard: Unknown strategy "${strategy}"`);
        return false;
    }
  })();

  // If access denied, handle accordingly
  if (!hasAccess) {
    // Redirect if path specified
    if (redirectTo) {
      return (
        <Navigate 
          to={redirectTo} 
          state={{ 
            from: location.pathname,
            requiredRoles: roles,
            strategy,
            currentRole
          }} 
          replace 
        />
      );
    }

    // Show custom fallback if provided
    if (fallback) {
      return <>{fallback}</>;
    }

    // Default fallback with role information
    return (
      <div className="flex items-center justify-center min-h-64 bg-gray-50 rounded-lg border border-gray-200">
        <div className="text-center p-8">
          <div className="text-6xl mb-4">🔒</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Acceso Restringido
          </h3>
          <p className="text-gray-600 mb-4">
            No tienes permisos suficientes para ver este contenido.
          </p>
          
          {showRoleInfo && (
            <div className="text-sm text-gray-500 space-y-1">
              <p>
                <strong>Tu rol actual:</strong> {currentRole ? getRoleDisplayName(currentRole) : 'Desconocido'}
              </p>
              <p>
                <strong>Roles requeridos:</strong> {roles.map(getRoleDisplayName).join(', ')}
              </p>
              <p>
                <strong>Estrategia:</strong> {getStrategyDescription(strategy)}
              </p>
            </div>
          )}
          
          <button
            onClick={() => window.history.back()}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Regresar
          </button>
        </div>
      </div>
    );
  }

  // Access granted
  return <>{children}</>;
};

/**
 * Get human-readable description of strategy
 */
const getStrategyDescription = (strategy: RoleStrategy): string => {
  const descriptions: Record<RoleStrategy, string> = {
    exact: 'Rol exacto requerido',
    minimum: 'Nivel mínimo de rol',
    any: 'Cualquiera de los roles',
    all: 'Todos los roles requeridos'
  };
  return descriptions[strategy] || strategy;
};

/**
 * Higher-order component for role-based rendering
 */
export const withRoleGuard = <P extends object>(
  Component: React.ComponentType<P>,
  roles: UserType[],
  strategy: RoleStrategy = 'any'
) => {
  return React.forwardRef<any, P>((props, _ref) => (
    <RoleGuard roles={roles} strategy={strategy}>
      <Component {...(props as P)} />
    </RoleGuard>
  ));
};

/**
 * Predefined role guard components for common scenarios
 */
export const AdminOnlyGuard: React.FC<{ children: React.ReactNode; fallback?: React.ReactNode }> = ({ children, fallback }) => (
  <RoleGuard roles={[UserType.ADMIN, UserType.SUPERUSER]} strategy="any" fallback={fallback}>
    {children}
  </RoleGuard>
);

export const VendorOrHigherGuard: React.FC<{ children: React.ReactNode; fallback?: React.ReactNode }> = ({ children, fallback }) => (
  <RoleGuard roles={[UserType.VENDEDOR]} strategy="minimum" fallback={fallback}>
    {children}
  </RoleGuard>
);

export const SuperUserOnlyGuard: React.FC<{ children: React.ReactNode; fallback?: React.ReactNode }> = ({ children, fallback }) => (
  <RoleGuard roles={[UserType.SUPERUSER]} strategy="exact" fallback={fallback}>
    {children}
  </RoleGuard>
);

/**
 * Conditional role-based rendering hook
 */
export const useRoleConditionalRender = (
  roles: UserType[], 
  strategy: RoleStrategy = 'any'
) => {
  const { hasRole, hasAnyRole, hasAllRoles, hasMinimumRole } = useRoleAccess();

  const canRender = (() => {
    switch (strategy) {
      case 'exact':
        return roles.some(role => hasRole(role));
      case 'minimum':
        return roles.length === 1 && roles[0] ? hasMinimumRole(roles[0]) : false;
      case 'any':
        return hasAnyRole(roles);
      case 'all':
        return hasAllRoles(roles);
      default:
        return false;
    }
  })();

  return canRender;
};

export default RoleGuard;