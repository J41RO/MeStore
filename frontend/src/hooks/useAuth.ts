import { useCallback } from 'react';
import { useAuthStore, UserType } from '../stores/authStore';
import type {
  UseAuthReturn,
  UseLoginReturn,
  UseRegisterReturn,
  UseLogoutReturn,
  LoginRequest,
  RegisterRequest,
} from '../types';

/**
 * Enhanced Authentication Hooks
 * React Specialist AI Implementation
 *
 * Provides comprehensive auth hooks with TypeScript integration
 * Conectado directamente con FastAPI backend con tipos seguros
 */
export const useAuth = () => {
  const {
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    login,
    adminLogin,
    logout,
    register,
    checkAuth,
    validateSession,
    refreshUserInfo,
    isAdmin,
    isSuperuser,
    getUserType,
    setError,
    clearAuth,
  } = useAuthStore();

  // Métodos de conveniencia computados
  const isLoggedIn = isAuthenticated && !!token;
  const userRole = user?.user_type || 'guest';
  const userEmail = user?.email || '';
  const userName = user?.name || user?.nombre || user?.email?.split('@')[0] || 'Usuario';
  const isEmailVerified = user?.email_verified || false;
  const isPhoneVerified = user?.phone_verified || false;
  const isActive = user?.is_active !== false; // Default to true if undefined

  // Login simplificado con validaciones reales
  const signIn = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      if (!email || !password) {
        throw new Error('Email y contraseña son requeridos');
      }

      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        throw new Error('Email inválido');
      }

      if (password.length < 6) {
        throw new Error('La contraseña debe tener al menos 6 caracteres');
      }

      const success = await login(email, password);

      if (success) {
        return { success: true };
      } else {
        return {
          success: false,
          error: error || 'Error en el login'
        };
      }
    } catch (error) {
      console.error('Error en signIn:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Error desconocido',
      };
    }
  };

  // Admin login simplificado
  const signInAdmin = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      if (!email || !password) {
        throw new Error('Email y contraseña son requeridos');
      }

      const success = await adminLogin(email, password);

      if (success) {
        return { success: true };
      } else {
        return {
          success: false,
          error: error || 'Error en el login administrativo'
        };
      }
    } catch (error) {
      console.error('Error en signInAdmin:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Error desconocido',
      };
    }
  };

  // Registro simplificado
  const signUp = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      if (!email || !password) {
        throw new Error('Email y contraseña son requeridos');
      }

      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        throw new Error('Email inválido');
      }

      if (password.length < 6) {
        throw new Error('La contraseña debe tener al menos 6 caracteres');
      }

      const success = await register(email, password);

      if (success) {
        return { success: true };
      } else {
        return {
          success: false,
          error: error || 'Error en el registro'
        };
      }
    } catch (error) {
      console.error('Error en signUp:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Error desconocido',
      };
    }
  };

  // Logout simplificado
  const signOut = async (): Promise<{ success: boolean; error?: string }> => {
    try {
      await logout();
      return { success: true };
    } catch (error) {
      console.error('Error en signOut:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Error desconocido',
      };
    }
  };

  // Verificar autenticación con el backend
  const verifyAuth = async (): Promise<boolean> => {
    try {
      return await checkAuth();
    } catch (error) {
      console.error('Error verificando autenticación:', error);
      return false;
    }
  };

  // Refrescar datos del usuario
  const refreshUser = async (): Promise<boolean> => {
    try {
      return await refreshUserInfo();
    } catch (error) {
      console.error('Error refrescando usuario:', error);
      return false;
    }
  };

  // Validar sesión actual
  const validateCurrentSession = async (): Promise<boolean> => {
    try {
      return await validateSession();
    } catch (error) {
      console.error('Error validando sesión:', error);
      return false;
    }
  };

  // Helpers de rol
  const hasAdminRole = (): boolean => isAdmin();
  const hasSuperuserRole = (): boolean => isSuperuser();
  const hasVendorRole = (): boolean => userRole === UserType.VENDEDOR;
  const hasBuyerRole = (): boolean => userRole === UserType.COMPRADOR;

  // Clear error helper
  const clearError = () => setError(null);

  // Force logout helper
  const forceLogout = () => {
    clearAuth();
    window.location.href = '/auth/login';
  };

  return {
    // Estado básico
    user,
    token,
    isAuthenticated,
    isLoading,
    error,

    // Estado computado
    isLoggedIn,
    userRole,
    userEmail,
    userName,
    isEmailVerified,
    isPhoneVerified,
    isActive,

    // Métodos principales simplificados
    signIn,
    signInAdmin,
    signUp,
    signOut,

    // Métodos de verificación
    verifyAuth,
    refreshUser,
    validateCurrentSession,

    // Helpers de rol
    hasAdminRole,
    hasSuperuserRole,
    hasVendorRole,
    hasBuyerRole,

    // Métodos avanzados (acceso directo al store)
    login,
    adminLogin,
    logout,
    register,
    checkAuth,
    validateSession,
    refreshUserInfo,
    isAdmin,
    isSuperuser,
    getUserType,

    // Utilidades
    clearError,
    forceLogout,
  };
};

/**
 * Specialized hook for login operations
 */
export const useLogin = (): UseLoginReturn => {
  const { login, isLoading, error, setError } = useAuthStore();

  const loginUser = useCallback(
    async (credentials: LoginRequest): Promise<boolean> => {
      return await login(credentials.email, credentials.password);
    },
    [login]
  );

  const clearError = useCallback(() => {
    setError(null);
  }, [setError]);

  return {
    login: loginUser,
    isLoading,
    error,
    clearError,
  };
};

/**
 * Specialized hook for registration operations
 */
export const useRegister = (): UseRegisterReturn => {
  const { register, isLoading, error, setError } = useAuthStore();

  const registerUser = useCallback(
    async (userData: RegisterRequest): Promise<boolean> => {
      return await register(userData.email, userData.password);
    },
    [register]
  );

  const clearError = useCallback(() => {
    setError(null);
  }, [setError]);

  return {
    register: registerUser,
    isLoading,
    error,
    clearError,
  };
};

/**
 * Specialized hook for logout operations
 */
export const useLogout = (): UseLogoutReturn => {
  const { logout, isLoading } = useAuthStore();

  const logoutUser = useCallback(async (): Promise<void> => {
    await logout();
  }, [logout]);

  return {
    logout: logoutUser,
    isLoading,
  };
};

/**
 * Hook for checking user permissions
 */
export const usePermissions = () => {
  const { isAdmin, isSuperuser, getUserType, user } = useAuthStore();

  const hasRole = useCallback(
    (role: string): boolean => {
      const userType = getUserType();
      return userType === role;
    },
    [getUserType]
  );

  const hasAnyRole = useCallback(
    (roles: string[]): boolean => {
      const userType = getUserType();
      return userType ? roles.includes(userType) : false;
    },
    [getUserType]
  );

  const canAccess = useCallback(
    (resource: string): boolean => {
      if (!user) return false;

      const userType = getUserType();

      switch (resource) {
        case 'admin':
          return isAdmin();
        case 'vendor':
          return userType === 'VENDEDOR' || isAdmin();
        case 'buyer':
          return userType === 'COMPRADOR' || isAdmin();
        case 'superuser':
          return isSuperuser();
        default:
          return false;
      }
    },
    [user, getUserType, isAdmin, isSuperuser]
  );

  return {
    hasRole,
    hasAnyRole,
    canAccess,
    isAdmin: isAdmin(),
    isSuperuser: isSuperuser(),
    isVendor: hasRole('VENDEDOR'),
    isBuyer: hasRole('COMPRADOR'),
    userType: getUserType(),
  };
};

export type UseAuthReturn = ReturnType<typeof useAuth>;