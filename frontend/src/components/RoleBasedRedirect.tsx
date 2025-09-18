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

  // ENHANCED DEBUG: Verificar datos del usuario
  console.log('🔍 RoleBasedRedirect ENHANCED DEBUG:');
  console.log('📋 isAuthenticated:', isAuthenticated);
  console.log('👤 user:', user);
  console.log('🎭 user.user_type:', user.user_type);
  console.log('🎯 typeof user.user_type:', typeof user.user_type);

  // VALIDATION: Critical user data checks
  if (user && !user.user_type) {
    console.error('❌ CRITICAL: User exists but user_type is missing!');
    console.error('📋 User data:', user);
    return <Navigate to="/login" replace />;
  }

  if (user && !user.id) {
    console.warn('⚠️ User ID missing, but this might be expected (backend issue)');
    console.log('📋 User data (ID check):', user);
    // Don't redirect to login if only ID is missing - other fields might be valid
  }

  // ENHANCED: Redirigir según el tipo de usuario con validación robusta
  const userType = user.user_type;
  console.log('🎯 REDIRECT LOGIC - userType value:', userType);
  console.log('🔍 REDIRECT LOGIC - userType comparison:');
  console.log('  userType === UserType.BUYER:', userType === UserType.BUYER);
  console.log('  userType === UserType.VENDOR:', userType === UserType.VENDOR);
  console.log('  userType === UserType.ADMIN:', userType === UserType.ADMIN);
  console.log('  userType === UserType.SUPERUSER:', userType === UserType.SUPERUSER);

  // Use string comparison for additional safety
  const userTypeString = String(userType).toLowerCase();
  console.log('🔄 REDIRECT LOGIC - normalized userType:', userTypeString);

  switch (userType) {
    case UserType.BUYER:
      console.log('✅ Redirigiendo BUYER a /app/dashboard');
      return <Navigate to="/app/dashboard" replace />;

    case UserType.VENDOR:
      console.log('✅ Redirigiendo VENDOR a /app/vendor-dashboard');
      return <Navigate to="/app/vendor-dashboard" replace />;

    case UserType.ADMIN:
      console.log('✅ Redirigiendo ADMIN a /admin-secure-portal/dashboard');
      return <Navigate to="/admin-secure-portal/dashboard" replace />;

    case UserType.SUPERUSER:
      console.log('✅ Redirigiendo SUPERUSER a /admin-secure-portal/dashboard');
      return <Navigate to="/admin-secure-portal/dashboard" replace />;

    default:
      // Enhanced fallback with string-based comparison
      console.log('🚨 SWITCH FAILED - Trying string-based fallback');

      if (userTypeString === 'buyer') {
        console.log('🔄 FALLBACK: Redirigiendo BUYER via string match');
        return <Navigate to="/app/dashboard" replace />;
      } else if (userTypeString === 'vendor') {
        console.log('🔄 FALLBACK: Redirigiendo VENDOR via string match');
        return <Navigate to="/app/vendor-dashboard" replace />;
      } else if (userTypeString === 'admin') {
        console.log('🔄 FALLBACK: Redirigiendo ADMIN via string match');
        return <Navigate to="/admin-secure-portal/dashboard" replace />;
      } else if (userTypeString === 'superuser') {
        console.log('🔄 FALLBACK: Redirigiendo SUPERUSER via string match');
        return <Navigate to="/admin-secure-portal/dashboard" replace />;
      }

      // Ultimate fallback para roles completamente desconocidos
      console.log('🚨 USER TYPE COMPLETAMENTE NO RECONOCIDO:', user.user_type);
      console.log('👤 Usuario completo:', user);
      console.log('🔍 Enum values para debug:');
      console.log('  UserType.BUYER:', UserType.BUYER);
      console.log('  UserType.VENDOR:', UserType.VENDOR);
      console.log('  UserType.ADMIN:', UserType.ADMIN);
      console.log('  UserType.SUPERUSER:', UserType.SUPERUSER);
      return <Navigate to={fallback} replace />;
  }
};

export default RoleBasedRedirect;