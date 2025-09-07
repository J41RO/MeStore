import { useState, useCallback } from 'react';

export interface GoogleAuthResponse {
  credential?: string;
  clientId?: string;
  select_by?: string;
}

export interface GoogleUserInfo {
  id: string;
  email: string;
  name: string;
  picture?: string;
  given_name?: string;
  family_name?: string;
}

export interface UseGoogleAuthReturn {
  isLoading: boolean;
  error: string | null;
  userInfo: GoogleUserInfo | null;
  login: (credentialResponse: GoogleAuthResponse) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

export const useGoogleAuth = (): UseGoogleAuthReturn => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userInfo, setUserInfo] = useState<GoogleUserInfo | null>(null);

  const login = useCallback(async (credentialResponse: GoogleAuthResponse) => {
    setIsLoading(true);
    setError(null);

    try {
      // TODO: Reemplazar con integración real de Google OAuth
      console.log('Google OAuth Credential Response:', credentialResponse);

      // Simulación de decodificación del JWT token de Google
      if (credentialResponse.credential) {
        // En producción, aquí decodificarías el JWT token
        // const decoded = jwt_decode(credentialResponse.credential);
        
        // Simulación de datos del usuario desde Google
        const mockUserInfo: GoogleUserInfo = {
          id: 'google_user_' + Date.now(),
          email: 'usuario@gmail.com',
          name: 'Usuario Google',
          picture: 'https://via.placeholder.com/150',
          given_name: 'Usuario',
          family_name: 'Google'
        };

        // Simulación de validación con backend
        const backendResponse = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/v1/auth/google/verify`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            credential: credentialResponse.credential,
            clientId: credentialResponse.clientId
          })
        });

        if (backendResponse.ok) {
          // const realUserInfo = await backendResponse.json();
          // setUserInfo(realUserInfo);
          
          // Por ahora usar datos simulados
          setUserInfo(mockUserInfo);
          
          console.log('✅ Google OAuth: Usuario autenticado exitosamente');
        } else {
          throw new Error('Error al verificar credenciales con el servidor');
        }
      } else {
        throw new Error('No se recibió credential de Google');
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido en autenticación con Google';
      setError(errorMessage);
      console.error('❌ Google OAuth Error:', errorMessage);
      
      // En modo desarrollo, continuar con datos mock
      if (import.meta.env.VITE_APP_ENV === 'development') {
        console.log('🔧 Modo desarrollo: Usando datos mock para Google OAuth');
        const mockUserInfo: GoogleUserInfo = {
          id: 'dev_google_user',
          email: 'dev@gmail.com',
          name: 'Usuario Desarrollo Google',
          picture: 'https://via.placeholder.com/150',
          given_name: 'Usuario',
          family_name: 'Desarrollo'
        };
        setUserInfo(mockUserInfo);
        setError(null);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    setUserInfo(null);
    setError(null);
    console.log('🔐 Google OAuth: Usuario desconectado');
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    isLoading,
    error,
    userInfo,
    login,
    logout,
    clearError
  };
};

export default useGoogleAuth;