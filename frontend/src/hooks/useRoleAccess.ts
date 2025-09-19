import { useMemo } from 'react';
import { useAuthStore, UserType } from '../stores/authStore';

export interface UseRoleAccessReturn {
  hasRole: (role: UserType) => boolean;
  hasAnyRole: (roles: UserType[]) => boolean;
  hasAllRoles: (roles: UserType[]) => boolean;
  hasMinimumRole: (minimumRole: UserType) => boolean;
  isAdmin: boolean;
  isSuperUser: boolean;
  isVendor: boolean;
  isBuyer: boolean;
  canAccess: (requiredRoles: UserType[], requireAll?: boolean) => boolean;
  getCurrentRole: () => UserType | null;
  getRoleHierarchyLevel: (role: UserType) => number;
}

// Define role hierarchy levels (higher number = more permissions)
const ROLE_HIERARCHY: Record<UserType, number> = {
  [UserType.BUYER]: 1,
  [UserType.VENDOR]: 2,
  [UserType.ADMIN]: 3,
  [UserType.SUPERUSER]: 4,
};

/**
 * Custom hook for role-based access control
 * Provides comprehensive role verification functions with caching for performance
 */
export const useRoleAccess = (): UseRoleAccessReturn => {
  const { user, isAuthenticated } = useAuthStore();

  // Memoize computations for performance
  const roleAccessUtils = useMemo(() => {
    const currentUserType = user?.user_type || null;
    const currentRoleLevel = currentUserType ? ROLE_HIERARCHY[currentUserType] : 0;

    // DEBUG: Logging detallado
    console.log('🔍 useRoleAccess DEBUG:');
    console.log('👤 user:', user);
    console.log('🎭 currentUserType:', currentUserType);
    console.log('🎯 typeof currentUserType:', typeof currentUserType);
    console.log('📊 currentRoleLevel:', currentRoleLevel);
    console.log('🏗️ ROLE_HIERARCHY:', ROLE_HIERARCHY);
    console.log('🔑 ROLE_HIERARCHY keys:', Object.keys(ROLE_HIERARCHY));
    console.log('🎯 ROLE_HIERARCHY[currentUserType]:', ROLE_HIERARCHY[currentUserType as UserType]);

    return {
      /**
       * Check if user has specific role
       */
      hasRole: (role: UserType): boolean => {
        if (!isAuthenticated || !currentUserType) return false;
        return currentUserType === role;
      },

      /**
       * Check if user has any of the specified roles
       */
      hasAnyRole: (roles: UserType[]): boolean => {
        if (!isAuthenticated || !currentUserType || roles.length === 0) return false;
        return roles.includes(currentUserType);
      },

      /**
       * Check if user has all of the specified roles
       * Note: Since users have only one role, this returns true only if
       * the user's role is in the required roles array and array has length 1
       */
      hasAllRoles: (roles: UserType[]): boolean => {
        if (!isAuthenticated || !currentUserType || roles.length === 0) return false;
        if (roles.length > 1) return false; // User can't have multiple roles
        return roles.includes(currentUserType);
      },

      /**
       * Check if user has minimum role level (hierarchical check)
       */
      hasMinimumRole: (minimumRole: UserType): boolean => {
        if (!isAuthenticated || !currentUserType) return false;
        const minimumLevel = ROLE_HIERARCHY[minimumRole];
        return currentRoleLevel >= minimumLevel;
      },

      /**
       * Generic access control function
       */
      canAccess: (requiredRoles: UserType[], requireAll: boolean = false): boolean => {
        if (!isAuthenticated || !currentUserType || requiredRoles.length === 0) return false;
        
        if (requireAll) {
          // Since users have single role, requireAll only works for single role arrays
          return requiredRoles.length === 1 && requiredRoles.includes(currentUserType);
        } else {
          // Check if user has any of the required roles
          return requiredRoles.includes(currentUserType);
        }
      },

      /**
       * Get current user role
       */
      getCurrentRole: (): UserType | null => {
        return currentUserType;
      },

      /**
       * Get role hierarchy level for comparison
       */
      getRoleHierarchyLevel: (role: UserType): number => {
        return ROLE_HIERARCHY[role];
      },

      // Convenience boolean properties
      isAdmin: currentUserType === UserType.ADMIN,
      isSuperUser: currentUserType === UserType.SUPERUSER,
      isVendor: currentUserType === UserType.VENDOR,
      isBuyer: currentUserType === UserType.BUYER,
    };
  }, [user, isAuthenticated]);

  return roleAccessUtils;
};

/**
 * Higher-order function to create role-specific hooks
 */
export const createRoleHook = (allowedRoles: UserType[]) => {
  return (): boolean => {
    const { hasAnyRole } = useRoleAccess();
    return hasAnyRole(allowedRoles);
  };
};

/**
 * Predefined role hooks for common use cases
 */
export const useIsAdminOrHigher = createRoleHook([UserType.ADMIN, UserType.SUPERUSER]);
export const useIsVendorOrHigher = createRoleHook([UserType.VENDOR, UserType.ADMIN, UserType.SUPERUSER]);
export const useCanManageUsers = createRoleHook([UserType.ADMIN, UserType.SUPERUSER]);
export const useCanManageInventory = createRoleHook([UserType.VENDOR, UserType.ADMIN, UserType.SUPERUSER]);
export const useCanViewReports = createRoleHook([UserType.VENDOR, UserType.ADMIN, UserType.SUPERUSER]);
export const useCanAccessAdmin = createRoleHook([UserType.ADMIN, UserType.SUPERUSER]);

/**
 * Utility function to get role display name
 */
export const getRoleDisplayName = (role: UserType): string => {
  const roleNames: Record<UserType, string> = {
    [UserType.BUYER]: 'Comprador',
    [UserType.VENDOR]: 'Vendedor',
    [UserType.ADMIN]: 'Administrador',
    [UserType.SUPERUSER]: 'Super Usuario',
  };
  return roleNames[role] || 'Desconocido';
};

/**
 * Utility function to get role permissions description
 */
export const getRolePermissions = (role: UserType): string[] => {
  const permissions: Record<UserType, string[]> = {
    [UserType.BUYER]: [
      'Ver productos disponibles',
      'Realizar compras',
      'Gestionar perfil personal',
    ],
    [UserType.VENDOR]: [
      'Gestionar inventario',
      'Procesar pedidos',
      'Ver reportes de ventas',
      'Gestionar productos',
    ],
    [UserType.ADMIN]: [
      'Gestionar usuarios',
      'Configurar sistema',
      'Ver todos los reportes',
      'Gestionar vendedores',
      'Configurar inventario',
    ],
    [UserType.SUPERUSER]: [
      'Acceso completo al sistema',
      'Gestionar administradores',
      'Configuración avanzada',
      'Auditoría del sistema',
      'Backup y restauración',
    ],
  };
  return permissions[role] || [];
};

export default useRoleAccess;