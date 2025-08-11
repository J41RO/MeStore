import React, { createContext, useContext, ReactNode } from 'react';
import { useAuthStore } from '../stores/authStore';

// Tipos para el contexto
interface User {
  id: string;
  email: string;
  name?: string;
  role?: string;
}

interface AuthContextType {
  // Estado
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Métodos principales
  login: (token: string, user: User) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => boolean;
  
  // Métodos adicionales para JWT
  getToken: () => string | null;
  refreshToken: () => Promise<boolean>;
  isTokenValid: () => boolean;
}

interface AuthProviderProps {
  children: ReactNode;
}

// Crear contexto
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider que actúa como wrapper sobre Zustand
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  // Usar Zustand store internamente
  const {
    user,
    token,
    isAuthenticated,
    login: zustandLogin,
    logout: zustandLogout,
    checkAuth: zustandCheckAuth
  } = useAuthStore();

  // Listener para logout automático desde interceptores
  React.useEffect(() => {
    const handleAutoLogout = () => {
      logout();
    };

    window.addEventListener('auth:logout', handleAutoLogout);
    
    return () => {
      window.removeEventListener('auth:logout', handleAutoLogout);
    };
  }, []);

  // Wrapper methods para agregar funcionalidad adicional
  const login = async (token: string, user: User): Promise<void> => {
    try {
      // Validar token antes de guardar
      if (!token || token.trim() === '') {
        throw new Error('Token inválido');
      }

      // Usar método de Zustand
      zustandLogin(token, user);
      
      // Lógica adicional
      console.log('Usuario autenticado:', user.email);
    } catch (error) {
      console.error('Error en login:', error);
      throw error;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      console.log('Cerrando sesión...');
      zustandLogout();
    } catch (error) {
      console.error('Error en logout:', error);
      throw error;
    }
  };

  const checkAuth = (): boolean => {
    return zustandCheckAuth();
  };

  // Métodos adicionales para JWT management
  const getToken = (): string | null => {
    return token || localStorage.getItem('auth_token');
  };

  const refreshToken = async (): Promise<boolean> => {
    console.log('Token refresh - pendiente implementación');
    return false;
  };

  const isTokenValid = (): boolean => {
    const currentToken = getToken();
    if (!currentToken) return false;
    return currentToken.length > 10;
  };

  const isLoading = false;

  const contextValue: AuthContextType = {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    logout,
    checkAuth,
    getToken,
    refreshToken,
    isTokenValid
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
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