import React, { createContext, useContext, ReactNode, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import { authService } from '../services/authService';

// Importamos el tipo User desde authStore
import type { User } from '../stores/authStore';

interface AuthContextType {
  // Estado
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Métodos principales REAL
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<boolean>;

  // Métodos adicionales para JWT
  getToken: () => string | null;
  refreshToken: () => Promise<boolean>;
  isTokenValid: () => boolean;
  validateSession: () => Promise<boolean>;
}

interface AuthProviderProps {
  children: ReactNode;
}

// Crear contexto
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * AuthProvider real - conectado con FastAPI backend
 * Frontend Security AI Implementation
 *
 * Proporciona contexto de autenticación real sin mocks
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  // Usar Zustand store real
  const {
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    login: storeLogin,
    logout: storeLogout,
    checkAuth: storeCheckAuth,
    validateSession: storeValidateSession,
  } = useAuthStore();

  // Listener para logout automático desde interceptores
  useEffect(() => {
    const handleAutoLogout = () => {
      storeLogout();
    };

    window.addEventListener('auth:logout', handleAutoLogout);

    return () => {
      window.removeEventListener('auth:logout', handleAutoLogout);
    };
  }, [storeLogout]);

  // Verificar autenticación al cargar la aplicación
  useEffect(() => {
    const verifyAuth = async () => {
      const token = authService.getToken();
      if (token) {
        await storeCheckAuth();
      }
    };

    verifyAuth();
  }, [storeCheckAuth]);

  // Wrapper methods conectados con API real
  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      if (!email || !password) {
        throw new Error('Email y contraseña son requeridos');
      }

      const success = await storeLogin(email, password);

      if (success) {
        console.log('Usuario autenticado exitosamente:', email);
      }

      return success;
    } catch (error) {
      console.error('Error en login context:', error);
      throw error;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      console.log('Cerrando sesión...');
      await storeLogout();
    } catch (error) {
      console.error('Error en logout context:', error);
      throw error;
    }
  };

  const checkAuth = async (): Promise<boolean> => {
    try {
      return await storeCheckAuth();
    } catch (error) {
      console.error('Error verificando autenticación:', error);
      return false;
    }
  };

  // Métodos adicionales para JWT management real
  const getToken = (): string | null => {
    return authService.getToken();
  };

  const refreshToken = async (): Promise<boolean> => {
    try {
      const refreshTokenValue = authService.getRefreshToken();
      if (!refreshTokenValue) {
        return false;
      }

      await authService.refreshToken(refreshTokenValue);
      return true;
    } catch (error) {
      console.error('Error refrescando token:', error);
      return false;
    }
  };

  const isTokenValid = (): boolean => {
    const currentToken = getToken();
    if (!currentToken) return false;

    try {
      // Verificar si el token no está expirado
      const payload = JSON.parse(atob(currentToken.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      return payload.exp > currentTime;
    } catch (error) {
      console.error('Error validando token:', error);
      return false;
    }
  };

  const validateSession = async (): Promise<boolean> => {
    try {
      return await storeValidateSession();
    } catch (error) {
      console.error('Error validando sesión:', error);
      return false;
    }
  };

  const contextValue: AuthContextType = {
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    checkAuth,
    getToken,
    refreshToken,
    isTokenValid,
    validateSession,
  };

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
};

// Hook personalizado para usar el contexto
export const useAuthContext = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext debe usarse dentro de AuthProvider');
  }
  return context;
};

export { AuthContext };
export type { AuthContextType };
