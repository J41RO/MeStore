import { useMemo } from 'react';
import { useAuthStore, UserType } from '../stores/authStore';

export interface UseRoleAccessReturn {
  hasRole: (role: UserType) => boolean;
  hasAnyRole: (roles: UserType[]) => boolean;
  hasAllRoles: (roles: UserType[]) => boolean;
  hasMinimumRole: (minimumRole: UserType) => boolean;
  isOwner: boolean;
  isAdmin: boolean;
  isSuperUser: boolean;
  isVendor: boolean;
  isBuyer: boolean;
  canAccess: (requiredRoles: UserType[], requireAll?: boolean) => boolean;
  getCurrentRole: () => UserType | null;
  getRoleHierarchyLevel: (role: UserType) => number;
}

// Define role hierarchy levels (higher number = more permissions)
// Matches backend hierarchy: OWNER (100) > SUPERUSER (50) > ADMIN (10) > VENDOR (5) > BUYER (1)
const ROLE_HIERARCHY: Record<UserType, number> = {
  [UserType.OWNER]: 100,
  [UserType.SUPERUSER]: 50,
  [UserType.ADMIN]: 10,
  [UserType.ADMIN_SALES]: 10,
  [UserType.ADMIN_SUPPORT]: 10,
  [UserType.ADMIN_LOGISTICS]: 10,
  [UserType.ADMIN_MARKETING]: 10,
  [UserType.VENDOR]: 5,
  [UserType.BUYER]: 1,
  [UserType.CUSTOMER]: 1,
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
      isOwner: currentUserType === UserType.OWNER,
      isAdmin: currentUserType === UserType.ADMIN ||
               currentUserType === UserType.ADMIN_SALES ||
               currentUserType === UserType.ADMIN_SUPPORT ||
               currentUserType === UserType.ADMIN_LOGISTICS ||
               currentUserType === UserType.ADMIN_MARKETING,
      isSuperUser: currentUserType === UserType.SUPERUSER,
      isVendor: currentUserType === UserType.VENDOR,
      isBuyer: currentUserType === UserType.BUYER || currentUserType === UserType.CUSTOMER,
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
export const useIsAdminOrHigher = createRoleHook([
  UserType.OWNER,
  UserType.SUPERUSER,
  UserType.ADMIN,
  UserType.ADMIN_SALES,
  UserType.ADMIN_SUPPORT,
  UserType.ADMIN_LOGISTICS,
  UserType.ADMIN_MARKETING
]);
export const useIsVendorOrHigher = createRoleHook([
  UserType.OWNER,
  UserType.SUPERUSER,
  UserType.ADMIN,
  UserType.ADMIN_SALES,
  UserType.ADMIN_SUPPORT,
  UserType.ADMIN_LOGISTICS,
  UserType.ADMIN_MARKETING,
  UserType.VENDOR
]);
export const useCanManageUsers = createRoleHook([UserType.OWNER, UserType.SUPERUSER, UserType.ADMIN]);
export const useCanManageInventory = createRoleHook([
  UserType.OWNER,
  UserType.SUPERUSER,
  UserType.ADMIN,
  UserType.ADMIN_LOGISTICS,
  UserType.VENDOR
]);
export const useCanViewReports = createRoleHook([
  UserType.OWNER,
  UserType.SUPERUSER,
  UserType.ADMIN,
  UserType.ADMIN_SALES,
  UserType.ADMIN_SUPPORT,
  UserType.ADMIN_LOGISTICS,
  UserType.ADMIN_MARKETING,
  UserType.VENDOR
]);
export const useCanAccessAdmin = createRoleHook([
  UserType.OWNER,
  UserType.SUPERUSER,
  UserType.ADMIN,
  UserType.ADMIN_SALES,
  UserType.ADMIN_SUPPORT,
  UserType.ADMIN_LOGISTICS,
  UserType.ADMIN_MARKETING
]);

/**
 * Utility function to get role display name
 */
export const getRoleDisplayName = (role: UserType): string => {
  const roleNames: Record<UserType, string> = {
    [UserType.OWNER]: 'Propietario',
    [UserType.SUPERUSER]: 'Super Usuario',
    [UserType.ADMIN]: 'Administrador',
    [UserType.ADMIN_SALES]: 'Admin. Ventas',
    [UserType.ADMIN_SUPPORT]: 'Admin. Soporte',
    [UserType.ADMIN_LOGISTICS]: 'Admin. Logística',
    [UserType.ADMIN_MARKETING]: 'Admin. Marketing',
    [UserType.VENDOR]: 'Vendedor',
    [UserType.BUYER]: 'Comprador',
    [UserType.CUSTOMER]: 'Cliente',
  };
  return roleNames[role] || 'Desconocido';
};

/**
 * Utility function to get role permissions description
 */
export const getRolePermissions = (role: UserType): string[] => {
  const permissions: Record<UserType, string[]> = {
    [UserType.OWNER]: [
      'Control total del sistema',
      'Gestionar todos los usuarios y roles',
      'Configuración avanzada del sistema',
      'Asignar y revocar permisos',
      'Acceso a todas las funcionalidades',
      'Auditoría completa del sistema',
    ],
    [UserType.SUPERUSER]: [
      'Gestionar usuarios y vendedores',
      'Configuración del sistema',
      'Ver todos los reportes',
      'Auditoría del sistema',
      'Gestión de inventario global',
    ],
    [UserType.ADMIN]: [
      'Gestionar usuarios',
      'Configurar sistema',
      'Ver reportes',
      'Gestionar vendedores',
      'Configurar inventario',
    ],
    [UserType.ADMIN_SALES]: [
      'Gestionar ventas',
      'Ver reportes de ventas',
      'Gestionar productos',
      'Configurar precios',
    ],
    [UserType.ADMIN_SUPPORT]: [
      'Gestionar tickets de soporte',
      'Ver usuarios',
      'Procesar devoluciones',
      'Gestionar comunicaciones',
    ],
    [UserType.ADMIN_LOGISTICS]: [
      'Gestionar envíos',
      'Configurar transportistas',
      'Ver reportes de logística',
      'Gestionar almacenes',
    ],
    [UserType.ADMIN_MARKETING]: [
      'Gestionar campañas',
      'Ver analytics de marketing',
      'Configurar promociones',
      'Gestionar contenido',
    ],
    [UserType.VENDOR]: [
      'Gestionar inventario propio',
      'Procesar pedidos',
      'Ver reportes de ventas',
      'Gestionar productos',
    ],
    [UserType.BUYER]: [
      'Ver productos disponibles',
      'Realizar compras',
      'Gestionar perfil personal',
    ],
    [UserType.CUSTOMER]: [
      'Ver productos disponibles',
      'Realizar compras',
      'Gestionar perfil personal',
    ],
  };
  return permissions[role] || [];
};

export default useRoleAccess;