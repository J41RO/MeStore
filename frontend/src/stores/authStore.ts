import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name?: string;
  role?: string;
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