import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useAuth } from '../hooks/useAuth';
import type { AuthGuardProps } from '../types';
import { UserType } from '../types';

/**
 * Enhanced AuthGuard with Real Token Validation
 * React Specialist AI Implementation
 *
 * Provides route protection with backend verification
 * Includes role management and session validation
 */
const AuthGuard: React.FC<AuthGuardProps> = ({
  children,
  requiredRoles,
  fallback,
  redirectTo = '/auth/login',
}) => {
  const { isAuthenticated, isLoading, token, user, checkAuth, validateSession } = useAuthStore();
  const location = useLocation();

  const [isValidating, setIsValidating] = useState(false);
  const [validationComplete, setValidationComplete] = useState(false);

  // Verificar autenticación al montar el componente
  useEffect(() => {
    const verifyAuthentication = async () => {
      setIsValidating(true);

      try {
        if (!token) {
          setValidationComplete(true);
          setIsValidating(false);
          return;
        }

        // Validar sesión con backend
        const isValid = await validateSession();
        if (!isValid) {
          // Sesión inválida, redirigir a login
          setValidationComplete(true);
          setIsValidating(false);
          return;
        }

        setValidationComplete(true);
      } catch (error) {
        console.error('Error en validación de AuthGuard:', error);
        setValidationComplete(true);
      } finally {
        setIsValidating(false);
      }
    };

    verifyAuthentication();
  }, [token, validateSession, checkAuth]);

  // Función helper para verificar roles
  const checkRoleAccess = (): boolean => {
    if (!user) return false;

    // Si no hay requerimientos de rol, permitir acceso
    if (!requiredRoles || requiredRoles.length === 0) return true;

    // Verificar si el usuario tiene al menos uno de los roles requeridos
    return requiredRoles.includes(user.user_type);
  };

  // Mostrar loading durante validación
  if (isLoading || (isValidating && !validationComplete)) {
    if (fallback) {
      return <>{fallback}</>;
    }

    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Verificando autenticación...</span>
      </div>
    );
  }

  // Primera verificación: Autenticación
  if (!isAuthenticated || !token || !user) {
    return (
      <Navigate
        to={redirectTo}
        state={{ from: location.pathname }}
        replace
      />
    );
  }

  // Segunda verificación: Autorización basada en roles
  if (requiredRoles && requiredRoles.length > 0) {
    const hasPermission = checkRoleAccess();

    if (!hasPermission) {
      return (
        <Navigate
          to="/unauthorized"
          state={{
            from: location.pathname,
            requiredRoles,
            currentRole: user.user_type,
            reason: 'insufficient_permissions'
          }}
          replace
        />
      );
    }
  }

  // Tercera verificación: Usuario activo
  if (user.is_active === false) {
    return (
      <Navigate
        to="/unauthorized"
        state={{
          from: location.pathname,
          reason: 'account_disabled'
        }}
        replace
      />
    );
  }

  // Todas las verificaciones pasaron, mostrar contenido
  return <>{children}</>;
};

// Specialized guard components
export const AdminGuard: React.FC<Omit<AuthGuardProps, 'requiredRoles'>> = (props) => (
  <AuthGuard
    {...props}
    requiredRoles={[UserType.ADMIN, UserType.SUPERUSER]}
  />
);

export const VendorGuard: React.FC<Omit<AuthGuardProps, 'requiredRoles'>> = (props) => (
  <AuthGuard
    {...props}
    requiredRoles={[UserType.VENDOR, UserType.ADMIN, UserType.SUPERUSER]}
  />
);

export const BuyerGuard: React.FC<Omit<AuthGuardProps, 'requiredRoles'>> = (props) => (
  <AuthGuard
    {...props}
    requiredRoles={[UserType.BUYER, UserType.ADMIN, UserType.SUPERUSER]}
  />
);

export default AuthGuard;
