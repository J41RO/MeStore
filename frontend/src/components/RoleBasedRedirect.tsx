import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore, UserType } from '../stores/authStore';

interface RoleBasedRedirectProps {
  fallback?: string;
}

/**
 * Componente que redirige a los usuarios según su rol
 */
const RoleBasedRedirect: React.FC<RoleBasedRedirectProps> = ({ 
  fallback = '/marketplace/home' 
}) => {
  const { user, isAuthenticated } = useAuthStore();

  // Si no está autenticado, redirigir al login
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  // Redirigir según el tipo de usuario
  switch (user.user_type) {
    case UserType.COMPRADOR:
      return <Navigate to="/app/dashboard" replace />;
      
    case UserType.VENDEDOR:
      return <Navigate to="/app/vendor-dashboard" replace />;
      
    case UserType.ADMIN:
      return <Navigate to="/admin-secure-portal/dashboard" replace />;
      
    case UserType.SUPERUSER:
      return <Navigate to="/admin-secure-portal/dashboard" replace />;
      
    default:
      // Fallback para roles desconocidos
      return <Navigate to={fallback} replace />;
  }
};

export default RoleBasedRedirect;