import { create } from 'zustand';
import { persist } from 'zustand/middleware';


// Tipos de usuario del sistema
export enum UserType {
  COMPRADOR = 'COMPRADOR',
  VENDEDOR = 'VENDEDOR', 
  ADMIN = 'ADMIN',
  SUPERUSER = 'SUPERUSER'
}

interface User {
  id: string;
  email: string;
  name?: string;
  role?: string;
  user_type?: UserType;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  checkAuth: () => boolean;
  registerVendor: (vendorData: any) => Promise<boolean>;
  verifyOTP: (telefono: string, otp: string) => Promise<boolean>;
  isAdmin: () => boolean;
  isSuperuser: () => boolean;
  getUserType: () => UserType | null;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      login: (token: string, user: User) => {
        localStorage.setItem('auth_token', token);
        set({ token, user, isAuthenticated: true });
      },
      
      logout: () => {
        localStorage.removeItem('auth_token');
        set({ token: null, user: null, isAuthenticated: false });
      },
      
      checkAuth: () => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          set({ token, isAuthenticated: true });
          return true;
        }
        return false;
      },
              registerVendor: async (vendorData: any) => {
          try {
            const response = await fetch('/api/v1/vendedores/registro', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(vendorData)
            });
            return response.ok;
          } catch (error) {
            console.error('Error en registro:', error);
            return false;
          }
        },
        // Funciones helper para detección de roles
        isAdmin: () => {
          const state = get();
          return state.user?.user_type === UserType.ADMIN || state.user?.user_type === UserType.SUPERUSER;
        },
        isSuperuser: () => {
          const state = get();
          return state.user?.user_type === UserType.SUPERUSER;
        },
        getUserType: () => {
          const state = get();
          return state.user?.user_type || null;
        },

        verifyOTP: async (telefono: string, otp: string) => {
          try {
            const response = await fetch('/api/v1/auth/verify-phone-otp', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ telefono, otp })
            });
            if (response.ok) {
              const data = await response.json();
              set({ token: data.token, user: data.user, isAuthenticated: true });
              return true;
            }
            return false;
          } catch (error) {
            console.error('Error en verificación OTP:', error);
            return false;
          }
        },
    }),
    {
      name: 'mestore-auth',
      partialize: (state) => ({ user: state.user, token: state.token }),
    }
  )
);