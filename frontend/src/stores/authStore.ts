import { create } from 'zustand';

import { persist } from 'zustand/middleware';

// Tipos de usuario del sistema
export enum UserType {
  COMPRADOR = 'COMPRADOR',
  VENDEDOR = 'VENDEDOR',
  ADMIN = 'ADMIN',
  SUPERUSER = 'SUPERUSER'
}

// Interface del usuario
export interface User {
  id: string;
  email: string;
  user_type: UserType;
  name: string;
  profile?: any;
  token?: string;
  full_name?: string;
  telefono?: string;
  nombre?: string;
  apellido?: string;
}

// Interface del estado de autenticación
interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  updateUser: (user: User) => void;
  isAdmin: () => boolean;
  isSuperuser: () => boolean;
  getUserType: () => UserType | null;
  checkAuth: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      login: (token: string, user: User) => {
        localStorage.setItem('auth_token', token);
        set({ token, user, isAuthenticated: true });
      },
      logout: () => {
        localStorage.removeItem('auth_token');
        set({ token: null, user: null, isAuthenticated: false });
      },
      updateUser: (user: User) => {
        set({ user });
      },
      // Funciones helper para detección de roles
      isAdmin: () => {
        const state = get();
        return (
          state.user?.user_type === UserType.ADMIN ||
          state.user?.user_type === UserType.SUPERUSER
        );
      },
      isSuperuser: () => {
        const state = get();
        return state.user?.user_type === UserType.SUPERUSER;
      },
      checkAuth: () => {
        const token = localStorage.getItem('auth_token');
        const state = get();
        if (token && state.user) {
          set({ token, isAuthenticated: true });
          return true;
        }
        set({ token: null, user: null, isAuthenticated: false });
        return false;
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