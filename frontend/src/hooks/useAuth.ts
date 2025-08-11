import { useAuthContext } from '../contexts/AuthContext';

/**
 * Hook simplificado para manejo de autenticación
 * 
 * Proporciona interfaz limpia para componentes que necesitan auth
 * Actúa como facade sobre AuthContext
 */
export const useAuth = () => {
  const {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    logout,
    checkAuth,
    getToken,
    isTokenValid
  } = useAuthContext();

  // Métodos de conveniencia
  const isLoggedIn = isAuthenticated && isTokenValid();
  const userRole = user?.role || 'guest';
  const userEmail = user?.email || '';
  const userName = user?.name || user?.email?.split('@')[0] || 'Usuario';

  // Método de login simplificado con validaciones
  const signIn = async (email: string, password: string) => {
    try {
      // TODO: Integrar con API real en futuras tareas
      // Por ahora, mantener lógica de mock
      if (!email || !password) {
        throw new Error('Email y contraseña son requeridos');
      }

      const mockUser = { 
        id: Date.now().toString(), 
        email, 
        name: email.split('@')[0],
        role: 'vendedor'
      };
      const mockToken = `jwt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      await login(mockToken, mockUser);
      return { success: true };
    } catch (error) {
      console.error('Error en signIn:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Error desconocido' };
    }
  };

  // Método de logout simplificado
  const signOut = async () => {
    try {
      await logout();
      return { success: true };
    } catch (error) {
      console.error('Error en signOut:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Error desconocido' };
    }
  };

  return {
    // Estado
    user,
    token,
    isAuthenticated,
    isLoading,
    
    // Estado computado
    isLoggedIn,
    userRole,
    userEmail,
    userName,
    
    // Métodos principales
    signIn,
    signOut,
    checkAuth,
    
    // Métodos avanzados
    login,
    logout,
    getToken,
    isTokenValid
  };
};

export type UseAuthReturn = ReturnType<typeof useAuth>;