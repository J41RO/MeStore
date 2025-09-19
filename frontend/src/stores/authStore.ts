import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService } from '../services/authService';
import type { UserInfo } from '../services/authService';
import { UserType } from '../types/auth.types';

// Re-export UserType from types for consistency
export { UserType } from '../types/auth.types';

// Interface del usuario (actualizada con backend data)
export interface User {
  id: string;
  email: string;
  user_type: UserType;
  name: string;
  nombre?: string;
  email_verified?: boolean;
  phone_verified?: boolean;
  is_active?: boolean;
  // Legacy fields for backward compatibility
  profile?: any;
  token?: string;
  full_name?: string;
  telefono?: string;
  apellido?: string;
}

// Interface del estado de autenticación (actualizada con async methods)
interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Métodos principales
  login: (email: string, password: string) => Promise<boolean>;
  adminLogin: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  register: (email: string, password: string) => Promise<boolean>;

  // Métodos de verificación
  checkAuth: () => Promise<boolean>;
  validateSession: () => Promise<boolean>;
  refreshUserInfo: () => Promise<boolean>;

  // Métodos de estado
  updateUser: (user: User) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearAuth: () => void;

  // Métodos de utilidad
  isAdmin: () => boolean;
  isSuperuser: () => boolean;
  getUserType: () => UserType | null;
}

// Helper function to convert backend UserInfo to frontend User
const convertUserInfo = (userInfo: UserInfo): User => {
  console.log('🔍 convertUserInfo DEBUG:');
  console.log('📥 Backend userInfo:', userInfo);
  console.log('🎭 userInfo.user_type:', userInfo.user_type);
  console.log('🎯 typeof userInfo.user_type:', typeof userInfo.user_type);

  // VALIDATION: Ensure userInfo is valid
  if (!userInfo || !userInfo.email || !userInfo.user_type) {
    console.error('❌ INVALID USER INFO:', userInfo);
    console.error('Missing required fields:', {
      hasUserInfo: !!userInfo,
      hasEmail: !!userInfo?.email,
      hasUserType: !!userInfo?.user_type,
      hasId: !!userInfo?.id
    });
    throw new Error('Invalid user information received from backend');
  }

  // TEMPORARY: Handle missing ID gracefully (backend issue)
  if (!userInfo.id) {
    console.warn('⚠️ Backend returned null ID, using email as fallback identifier');
  }

  // FIX: Backend está enviando UPPERCASE values pero frontend espera lowercase
  // Mapear correctamente todos los valores posibles del backend:
  const mapBackendUserType = (backendType: string): UserType => {
    console.log('🔍 mapBackendUserType input:', backendType, typeof backendType);

    const typeMapping: Record<string, UserType> = {
      // Backend UPPERCASE values (CRITICAL FIX)
      'VENDOR': UserType.VENDOR,
      'BUYER': UserType.BUYER,
      'ADMIN': UserType.ADMIN,
      'SUPERUSER': UserType.SUPERUSER,

      // Legacy string literals (if any)
      'UserType.VENDOR': UserType.VENDOR,
      'UserType.BUYER': UserType.BUYER,
      'UserType.ADMIN': UserType.ADMIN,
      'UserType.SUPERUSER': UserType.SUPERUSER,

      // Frontend lowercase values (compatibility)
      'vendor': UserType.VENDOR,
      'buyer': UserType.BUYER,
      'admin': UserType.ADMIN,
      'superuser': UserType.SUPERUSER
    };

    const mappedType = typeMapping[backendType];

    if (!mappedType) {
      console.error('❌ UNKNOWN USER TYPE from backend:', backendType);
      console.error('🔍 Available mappings:', Object.keys(typeMapping));
      console.warn('⚠️ Defaulting to BUYER role for safety');
      return UserType.BUYER;
    }

    console.log('🔧 ROLE MAPPING:', backendType, '→', mappedType);
    return mappedType;
  };

  const mappedUserType = mapBackendUserType(userInfo.user_type);

  const convertedUser: User = {
    id: userInfo.id || userInfo.email, // Fallback to email if ID is null
    email: userInfo.email,
    user_type: mappedUserType,
    name: userInfo.nombre || userInfo.email.split('@')[0],
    nombre: userInfo.nombre,
    email_verified: userInfo.email_verified,
    phone_verified: userInfo.phone_verified,
    is_active: userInfo.is_active
  };

  // FINAL VALIDATION: Ensure critical fields are set
  console.log('✅ FINAL USER CONVERSION:', convertedUser);
  console.log('🎯 Final user_type:', convertedUser.user_type);
  console.log('🔍 user_type validation:', {
    isString: typeof convertedUser.user_type === 'string',
    value: convertedUser.user_type,
    validValues: Object.values(UserType)
  });

  return convertedUser;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Login real con API backend
      login: async (email: string, password: string): Promise<boolean> => {
        set({ isLoading: true, error: null });

        try {
          const result = await authService.login({ email, password });

          if (result.success && result.data) {
            // Obtener información del usuario después del login
            const userResult = await authService.getCurrentUser();

            if (userResult.success && userResult.data) {
              const user = convertUserInfo(userResult.data);
              const token = result.data.access_token;

              set({
                token,
                user,
                isAuthenticated: true,
                isLoading: false,
                error: null
              });

              return true;
            }
          }

          set({
            isLoading: false,
            error: result.error || 'Error en login',
            isAuthenticated: false
          });

          return false;
        } catch (error) {
          console.error('Error en login store:', error);
          set({
            isLoading: false,
            error: 'Error de conexión',
            isAuthenticated: false
          });
          return false;
        }
      },

      // Admin login con endpoint específico
      adminLogin: async (email: string, password: string): Promise<boolean> => {
        set({ isLoading: true, error: null });

        try {
          const result = await authService.adminLogin({ email, password });

          if (result.success && result.data) {
            const userResult = await authService.getCurrentUser();

            if (userResult.success && userResult.data) {
              const user = convertUserInfo(userResult.data);
              const token = result.data.access_token;

              set({
                token,
                user,
                isAuthenticated: true,
                isLoading: false,
                error: null
              });

              return true;
            }
          }

          set({
            isLoading: false,
            error: result.error || 'Error en admin login',
            isAuthenticated: false
          });

          return false;
        } catch (error) {
          console.error('Error en admin login store:', error);
          set({
            isLoading: false,
            error: 'Error de conexión',
            isAuthenticated: false
          });
          return false;
        }
      },

      // Logout real con cleanup
      logout: async (): Promise<void> => {
        set({ isLoading: true });

        try {
          await authService.logout();
        } catch (error) {
          console.error('Error en logout:', error);
        } finally {
          // Limpiar estado local siempre
          set({
            token: null,
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null
          });
        }
      },

      // Registro de nuevos usuarios
      register: async (email: string, password: string): Promise<boolean> => {
        set({ isLoading: true, error: null });

        try {
          const result = await authService.register({ email, password });

          if (result.success && result.data) {
            const userResult = await authService.getCurrentUser();

            if (userResult.success && userResult.data) {
              const user = convertUserInfo(userResult.data);
              const token = result.data.access_token;

              set({
                token,
                user,
                isAuthenticated: true,
                isLoading: false,
                error: null
              });

              return true;
            }
          }

          set({
            isLoading: false,
            error: result.error || 'Error en registro',
            isAuthenticated: false
          });

          return false;
        } catch (error) {
          console.error('Error en registro store:', error);
          set({
            isLoading: false,
            error: 'Error de conexión',
            isAuthenticated: false
          });
          return false;
        }
      },

      // Verificar autenticación con backend
      checkAuth: async (): Promise<boolean> => {
        const token = authService.getToken();

        if (!token) {
          set({ isAuthenticated: false, user: null, token: null });
          return false;
        }

        try {
          const isValid = await authService.validateToken();

          if (isValid) {
            const userResult = await authService.getCurrentUser();

            if (userResult.success && userResult.data) {
              const user = convertUserInfo(userResult.data);

              set({
                token,
                user,
                isAuthenticated: true,
                error: null
              });

              return true;
            }
          }

          // Token inválido, limpiar estado
          await get().logout();
          return false;
        } catch (error) {
          console.error('Error en checkAuth:', error);
          await get().logout();
          return false;
        }
      },

      // Validar sesión actual
      validateSession: async (): Promise<boolean> => {
        if (!get().isAuthenticated) {
          return false;
        }

        try {
          const isValid = await authService.validateToken();
          if (!isValid) {
            await get().logout();
          }
          return isValid;
        } catch (error) {
          console.error('Error validando sesión:', error);
          await get().logout();
          return false;
        }
      },

      // Refrescar información del usuario
      refreshUserInfo: async (): Promise<boolean> => {
        if (!get().isAuthenticated) {
          return false;
        }

        try {
          const userResult = await authService.getCurrentUser();

          if (userResult.success && userResult.data) {
            const user = convertUserInfo(userResult.data);
            set({ user });
            return true;
          }

          return false;
        } catch (error) {
          console.error('Error refrescando usuario:', error);
          return false;
        }
      },

      // Métodos de estado
      updateUser: (user: User) => {
        set({ user });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      setError: (error: string | null) => {
        set({ error });
      },

      clearAuth: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('auth_token'); // Legacy cleanup
        set({
          token: null,
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: null
        });
      },

      // Métodos de utilidad - funciones helper para detección de roles
      isAdmin: () => {
        const state = get();
        return (
          state.user?.user_type === UserType.ADMIN ||
          state.user?.user_type === UserType.SUPERUSER
        );
      },

      isVendor: () => {
        const state = get();
        return state.user?.user_type === UserType.VENDOR;
      },

      isBuyer: () => {
        const state = get();
        return state.user?.user_type === UserType.BUYER;
      },

      isSuperuser: () => {
        const state = get();
        return state.user?.user_type === UserType.SUPERUSER;
      },

      getUserType: () => {
        const state = get();
        return state.user?.user_type || null;
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state: AuthState) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated
      }),
    }
  )
);