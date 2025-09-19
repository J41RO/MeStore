/**
 * Authentication Store for MeStore Frontend
 * Type-safe Zustand store with consistent EntityId types
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { authApiService } from '../services/authApiService';
import type {
  EntityId,
  User,
  LoginRequest,
  RegisterRequest,
  UserType,
  AuthState,
  AuthActions,
  AuthStore,
  ValidationError,
} from '../types';

// ========================================
// EXTENDED AUTH STATE
// ========================================

/**
 * Extended auth state with UI-specific fields
 */
interface ExtendedAuthState extends AuthState {
  // Session management
  sessionExpiry: string | null;
  lastActivity: string | null;

  // UI state
  showLoginModal: boolean;
  showRegisterModal: boolean;
  loginRedirectPath: string | null;

  // Form validation
  validationErrors: ValidationError[];

  // Admin state
  adminMode: boolean;
}

/**
 * Extended auth actions with additional functionality
 */
interface ExtendedAuthActions extends AuthActions {
  // Modal management
  openLoginModal: (redirectPath?: string) => void;
  closeLoginModal: () => void;
  openRegisterModal: () => void;
  closeRegisterModal: () => void;

  // Session management
  updateLastActivity: () => void;
  checkSessionExpiry: () => boolean;
  extendSession: () => void;

  // Admin mode
  enterAdminMode: () => void;
  exitAdminMode: () => void;

  // Validation
  setValidationErrors: (errors: ValidationError[]) => void;
  clearValidationErrors: () => void;

  // Token management
  setTokens: (accessToken: string, refreshToken?: string) => void;
  getTokens: () => { accessToken: string | null; refreshToken: string | null };
}

/**
 * Complete extended auth store
 */
type ExtendedAuthStore = ExtendedAuthState & ExtendedAuthActions;

// ========================================
// STORE IMPLEMENTATION
// ========================================

/**
 * Type-safe authentication store with EntityId consistency
 */
export const useAuthStore = create<ExtendedAuthStore>()(
  persist(
    immer((set, get) => ({
      // ========================================
      // STATE
      // ========================================

      // Core auth state
      token: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Extended state
      sessionExpiry: null,
      lastActivity: null,
      showLoginModal: false,
      showRegisterModal: false,
      loginRedirectPath: null,
      validationErrors: [],
      adminMode: false,

      // ========================================
      // CORE AUTH ACTIONS
      // ========================================

      /**
       * Login user with email and password
       */
      login: async (credentials: LoginRequest): Promise<boolean> => {
        set((state) => {
          state.isLoading = true;
          state.error = null;
          state.validationErrors = [];
        });

        try {
          const response = await authApiService.login(credentials);
          const tokenData = 'data' in response ? response.data : response;

          if (tokenData) {
            set((state) => {
              state.token = tokenData.access_token;
              state.refreshToken = tokenData.refresh_token || null;
              state.user = tokenData.user || null;
              state.isAuthenticated = true;
              state.isLoading = false;
              state.sessionExpiry = new Date(Date.now() + tokenData.expires_in * 1000).toISOString();
              state.lastActivity = new Date().toISOString();
              state.showLoginModal = false;
            });

            // Auto-fetch user info if not provided
            if (!tokenData.user) {
              get().getCurrentUser();
            }

            return true;
          }

          throw new Error('Invalid response from server');
        } catch (error: any) {
          set((state) => {
            state.isLoading = false;
            state.error = error.message || 'Login failed';
            state.isAuthenticated = false;
            state.token = null;
            state.refreshToken = null;
            state.user = null;
          });
          return false;
        }
      },

      /**
       * Admin login with enhanced security
       */
      adminLogin: async (credentials: LoginRequest): Promise<boolean> => {
        set((state) => {
          state.isLoading = true;
          state.error = null;
          state.adminMode = true;
        });

        try {
          const response = await authApiService.adminLogin(credentials);
          const tokenData = 'data' in response ? response.data : response;

          if (tokenData && tokenData.user) {
            // Verify admin role
            const userType = tokenData.user.user_type;
            if (userType !== UserType.ADMIN && userType !== UserType.SUPERUSER) {
              throw new Error('Unauthorized: Admin access required');
            }

            set((state) => {
              state.token = tokenData.access_token;
              state.refreshToken = tokenData.refresh_token || null;
              state.user = tokenData.user;
              state.isAuthenticated = true;
              state.isLoading = false;
              state.adminMode = true;
              state.sessionExpiry = new Date(Date.now() + tokenData.expires_in * 1000).toISOString();
              state.lastActivity = new Date().toISOString();
              state.showLoginModal = false;
            });

            return true;
          }

          throw new Error('Invalid admin credentials');
        } catch (error: any) {
          set((state) => {
            state.isLoading = false;
            state.error = error.message || 'Admin login failed';
            state.adminMode = false;
          });
          return false;
        }
      },

      /**
       * Register new user
       */
      register: async (userData: RegisterRequest): Promise<boolean> => {
        set((state) => {
          state.isLoading = true;
          state.error = null;
          state.validationErrors = [];
        });

        try {
          const response = await authApiService.register(userData);
          const tokenData = 'data' in response ? response.data : response;

          if (tokenData) {
            set((state) => {
              state.token = tokenData.access_token;
              state.refreshToken = tokenData.refresh_token || null;
              state.user = tokenData.user || null;
              state.isAuthenticated = true;
              state.isLoading = false;
              state.sessionExpiry = new Date(Date.now() + tokenData.expires_in * 1000).toISOString();
              state.lastActivity = new Date().toISOString();
              state.showRegisterModal = false;
            });

            return true;
          }

          throw new Error('Registration failed');
        } catch (error: any) {
          set((state) => {
            state.isLoading = false;
            state.error = error.message || 'Registration failed';
          });
          return false;
        }
      },

      /**
       * Logout user
       */
      logout: async (): Promise<void> => {
        try {
          await authApiService.logout();
        } catch (error) {
          console.warn('Logout API call failed:', error);
        } finally {
          set((state) => {
            state.token = null;
            state.refreshToken = null;
            state.user = null;
            state.isAuthenticated = false;
            state.isLoading = false;
            state.error = null;
            state.sessionExpiry = null;
            state.lastActivity = null;
            state.adminMode = false;
            state.validationErrors = [];
          });
        }
      },

      /**
       * Refresh authentication token
       */
      refreshToken: async (): Promise<boolean> => {
        try {
          const response = await authApiService.refreshToken();
          const tokenData = 'data' in response ? response.data : response;

          if (tokenData) {
            set((state) => {
              state.token = tokenData.access_token;
              state.refreshToken = tokenData.refresh_token || state.refreshToken;
              state.sessionExpiry = new Date(Date.now() + tokenData.expires_in * 1000).toISOString();
              state.lastActivity = new Date().toISOString();
            });
            return true;
          }

          return false;
        } catch (error) {
          get().clearAuth();
          return false;
        }
      },

      // ========================================
      // USER INFORMATION
      // ========================================

      /**
       * Get current user information
       */
      getCurrentUser: async (): Promise<User | null> => {
        try {
          const user = await authApiService.getCurrentUser();
          set((state) => {
            state.user = user;
            state.lastActivity = new Date().toISOString();
          });
          return user;
        } catch (error) {
          return null;
        }
      },

      /**
       * Update user information
       */
      updateUser: (user: User): void => {
        set((state) => {
          state.user = user;
          state.lastActivity = new Date().toISOString();
        });
      },

      // ========================================
      // SESSION MANAGEMENT
      // ========================================

      /**
       * Check authentication status
       */
      checkAuth: (): boolean => {
        const { token, sessionExpiry } = get();

        if (!token) return false;

        // Check session expiry
        if (sessionExpiry && new Date() > new Date(sessionExpiry)) {
          get().refreshToken();
          return false;
        }

        return true;
      },

      /**
       * Clear authentication data
       */
      clearAuth: (): void => {
        set((state) => {
          state.token = null;
          state.refreshToken = null;
          state.user = null;
          state.isAuthenticated = false;
          state.error = null;
          state.sessionExpiry = null;
          state.lastActivity = null;
          state.adminMode = false;
          state.validationErrors = [];
        });
      },

      // ========================================
      // ROLE HELPERS
      // ========================================

      /**
       * Check if user is admin
       */
      isAdmin: (): boolean => {
        const { user } = get();
        return user?.user_type === UserType.ADMIN || user?.user_type === UserType.SUPERUSER;
      },

      /**
       * Check if user is superuser
       */
      isSuperuser: (): boolean => {
        const { user } = get();
        return user?.user_type === UserType.SUPERUSER;
      },

      /**
       * Check if user is vendor
       */
      isVendor: (): boolean => {
        const { user } = get();
        return user?.user_type === UserType.VENDEDOR;
      },

      /**
       * Check if user is buyer
       */
      isBuyer: (): boolean => {
        const { user } = get();
        return user?.user_type === UserType.COMPRADOR;
      },

      /**
       * Get user type
       */
      getUserType: (): UserType | null => {
        const { user } = get();
        return user?.user_type || null;
      },

      // ========================================
      // LOADING AND ERROR STATES
      // ========================================

      /**
       * Set loading state
       */
      setLoading: (loading: boolean): void => {
        set((state) => {
          state.isLoading = loading;
        });
      },

      /**
       * Set error message
       */
      setError: (error: string | null): void => {
        set((state) => {
          state.error = error;
        });
      },

      /**
       * Clear error message
       */
      clearError: (): void => {
        set((state) => {
          state.error = null;
        });
      },

      // ========================================
      // EXTENDED ACTIONS
      // ========================================

      /**
       * Open login modal
       */
      openLoginModal: (redirectPath?: string): void => {
        set((state) => {
          state.showLoginModal = true;
          state.loginRedirectPath = redirectPath || null;
        });
      },

      /**
       * Close login modal
       */
      closeLoginModal: (): void => {
        set((state) => {
          state.showLoginModal = false;
          state.loginRedirectPath = null;
        });
      },

      /**
       * Open register modal
       */
      openRegisterModal: (): void => {
        set((state) => {
          state.showRegisterModal = true;
        });
      },

      /**
       * Close register modal
       */
      closeRegisterModal: (): void => {
        set((state) => {
          state.showRegisterModal = false;
        });
      },

      /**
       * Update last activity timestamp
       */
      updateLastActivity: (): void => {
        set((state) => {
          state.lastActivity = new Date().toISOString();
        });
      },

      /**
       * Check if session is expired
       */
      checkSessionExpiry: (): boolean => {
        const { sessionExpiry } = get();
        return sessionExpiry ? new Date() > new Date(sessionExpiry) : false;
      },

      /**
       * Extend session
       */
      extendSession: (): void => {
        set((state) => {
          state.sessionExpiry = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(); // 24 hours
          state.lastActivity = new Date().toISOString();
        });
      },

      /**
       * Enter admin mode
       */
      enterAdminMode: (): void => {
        set((state) => {
          state.adminMode = true;
        });
      },

      /**
       * Exit admin mode
       */
      exitAdminMode: (): void => {
        set((state) => {
          state.adminMode = false;
        });
      },

      /**
       * Set validation errors
       */
      setValidationErrors: (errors: ValidationError[]): void => {
        set((state) => {
          state.validationErrors = errors;
        });
      },

      /**
       * Clear validation errors
       */
      clearValidationErrors: (): void => {
        set((state) => {
          state.validationErrors = [];
        });
      },

      /**
       * Set tokens manually
       */
      setTokens: (accessToken: string, refreshToken?: string): void => {
        set((state) => {
          state.token = accessToken;
          state.refreshToken = refreshToken || state.refreshToken;
          state.isAuthenticated = true;
        });
      },

      /**
       * Get current tokens
       */
      getTokens: () => {
        const { token, refreshToken } = get();
        return { accessToken: token, refreshToken };
      },
    })),
    {
      name: 'auth-store',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        sessionExpiry: state.sessionExpiry,
        lastActivity: state.lastActivity,
        adminMode: state.adminMode,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          // Check session validity on rehydration
          const isExpired = state.sessionExpiry && new Date() > new Date(state.sessionExpiry);
          if (isExpired) {
            state.clearAuth();
          } else if (state.token) {
            // Set token in API service
            authApiService.setAuthToken(state.token);
          }
        }
      },
    }
  )
);

// ========================================
// SELECTORS
// ========================================

/**
 * Auth store selectors for optimized component subscriptions
 */
export const authSelectors = {
  // User information
  user: (state: ExtendedAuthStore) => state.user,
  userId: (state: ExtendedAuthStore) => state.user?.id,
  userEmail: (state: ExtendedAuthStore) => state.user?.email,
  userType: (state: ExtendedAuthStore) => state.user?.user_type,
  userName: (state: ExtendedAuthStore) => state.user?.nombre || state.user?.email?.split('@')[0],

  // Authentication status
  isAuthenticated: (state: ExtendedAuthStore) => state.isAuthenticated,
  isLoading: (state: ExtendedAuthStore) => state.isLoading,
  error: (state: ExtendedAuthStore) => state.error,

  // Role checks
  isAdmin: (state: ExtendedAuthStore) => state.isAdmin(),
  isSuperuser: (state: ExtendedAuthStore) => state.isSuperuser(),
  isVendor: (state: ExtendedAuthStore) => state.isVendor(),
  isBuyer: (state: ExtendedAuthStore) => state.isBuyer(),

  // UI state
  showLoginModal: (state: ExtendedAuthStore) => state.showLoginModal,
  showRegisterModal: (state: ExtendedAuthStore) => state.showRegisterModal,
  adminMode: (state: ExtendedAuthStore) => state.adminMode,

  // Session
  sessionExpiry: (state: ExtendedAuthStore) => state.sessionExpiry,
  lastActivity: (state: ExtendedAuthStore) => state.lastActivity,
  isSessionExpired: (state: ExtendedAuthStore) => state.checkSessionExpiry(),

  // Validation
  validationErrors: (state: ExtendedAuthStore) => state.validationErrors,
  hasValidationErrors: (state: ExtendedAuthStore) => state.validationErrors.length > 0,
};

// ========================================
// HOOKS
// ========================================

/**
 * Hook for user information
 */
export const useUser = () => useAuthStore(authSelectors.user);

/**
 * Hook for authentication status
 */
export const useIsAuthenticated = () => useAuthStore(authSelectors.isAuthenticated);

/**
 * Hook for admin status
 */
export const useIsAdmin = () => useAuthStore(authSelectors.isAdmin);

/**
 * Hook for vendor status
 */
export const useIsVendor = () => useAuthStore(authSelectors.isVendor);

/**
 * Hook for loading state
 */
export const useAuthLoading = () => useAuthStore(authSelectors.isLoading);

/**
 * Hook for error state
 */
export const useAuthError = () => useAuthStore(authSelectors.error);

// ========================================
// EXPORTS
// ========================================

export type { ExtendedAuthState, ExtendedAuthActions, ExtendedAuthStore };
export default useAuthStore;