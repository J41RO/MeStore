import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore, UserType } from '../stores/authStore';
import { getRoleDisplayName, getRolePermissions } from '../hooks/useRoleAccess';
import { ShieldX, Home, ArrowLeft, User, Mail } from 'lucide-react';

interface LocationState {
  from?: string;
  requiredRoles?: UserType[];
  minimumRole?: UserType;
  currentRole?: UserType;
}

const Unauthorized: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuthStore();
  
  const state = location.state as LocationState;
  const fromPath = state?.from || '/';
  const requiredRoles = state?.requiredRoles || [];
  const minimumRole = state?.minimumRole;
  const currentRole = user?.user_type || state?.currentRole;

  const handleGoBack = () => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate('/');
    }
  };

  const handleGoHome = () => {
    if (user?.user_type === UserType.ADMIN || user?.user_type === UserType.SUPERUSER) {
      navigate('/admin-secure-portal/dashboard');
    } else if (user?.user_type === UserType.VENDEDOR) {
      navigate('/app/dashboard');
    } else if (user?.user_type === UserType.COMPRADOR) {
      navigate('/marketplace');
    } else {
      navigate('/');
    }
  };

  const getRequiredRolesText = () => {
    if (minimumRole) {
      return `${getRoleDisplayName(minimumRole)} o superior`;
    }
    if (requiredRoles.length > 0) {
      return requiredRoles.map(getRoleDisplayName).join(', ');
    }
    return 'Roles específicos';
  };

  const getContactInfo = () => {
    const contactEmails: Record<UserType, string> = {
      [UserType.COMPRADOR]: 'soporte@mestocker.com',
      [UserType.VENDEDOR]: 'vendedores@mestocker.com',
      [UserType.ADMIN]: 'admin@mestocker.com',
      [UserType.SUPERUSER]: 'tech@mestocker.com'
    };

    if (currentRole) {
      return contactEmails[currentRole] || 'soporte@mestocker.com';
    }
    return 'soporte@mestocker.com';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12 text-center">
          {/* Icon */}
          <div className="inline-flex items-center justify-center w-20 h-20 bg-red-100 rounded-full mb-6">
            <ShieldX className="w-10 h-10 text-red-600" />
          </div>

          {/* Main Message */}
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Acceso Denegado
          </h1>
          
          <p className="text-lg text-gray-600 mb-8">
            No tienes los permisos necesarios para acceder a esta sección del sistema.
          </p>

          {/* Role Information */}
          <div className="bg-gray-50 rounded-xl p-6 mb-8 text-left space-y-4">
            <div className="flex items-center space-x-3">
              <User className="w-5 h-5 text-gray-500" />
              <div>
                <p className="text-sm font-medium text-gray-700">Tu rol actual:</p>
                <p className="text-lg font-semibold text-blue-600">
                  {currentRole ? getRoleDisplayName(currentRole) : 'Desconocido'}
                </p>
              </div>
            </div>

            <div className="border-t border-gray-200 pt-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Rol requerido:</p>
              <p className="text-lg font-semibold text-red-600">
                {getRequiredRolesText()}
              </p>
            </div>

            {fromPath && (
              <div className="border-t border-gray-200 pt-4">
                <p className="text-sm font-medium text-gray-700 mb-1">Página solicitada:</p>
                <p className="text-sm text-gray-600 font-mono bg-gray-100 rounded px-2 py-1">
                  {fromPath}
                </p>
              </div>
            )}
          </div>

          {/* Current Role Permissions */}
          {currentRole && (
            <div className="bg-blue-50 rounded-xl p-6 mb-8 text-left">
              <h3 className="text-lg font-semibold text-blue-900 mb-3">
                Tus permisos actuales:
              </h3>
              <ul className="space-y-2">
                {getRolePermissions(currentRole).map((permission, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <span className="text-blue-600 mt-1">✓</span>
                    <span className="text-blue-800 text-sm">{permission}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Contact Information */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 mb-8">
            <div className="flex items-center justify-center space-x-2 mb-3">
              <Mail className="w-5 h-5 text-yellow-600" />
              <h3 className="text-lg font-semibold text-yellow-900">
                ¿Necesitas más permisos?
              </h3>
            </div>
            <p className="text-yellow-800 text-sm mb-3">
              Si crees que deberías tener acceso a esta sección, contacta a tu administrador o envía un correo a:
            </p>
            <a 
              href={`mailto:${getContactInfo()}`}
              className="inline-flex items-center space-x-2 text-yellow-700 hover:text-yellow-900 font-medium"
            >
              <Mail className="w-4 h-4" />
              <span>{getContactInfo()}</span>
            </a>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={handleGoBack}
              className="inline-flex items-center justify-center space-x-2 px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Regresar</span>
            </button>
            
            <button
              onClick={handleGoHome}
              className="inline-flex items-center justify-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Home className="w-4 h-4" />
              <span>Ir al Dashboard</span>
            </button>
          </div>

          {/* Support Text */}
          <p className="text-xs text-gray-500 mt-8">
            MeStocker - Sistema de control de acceso basado en roles
          </p>
        </div>
      </div>
    </div>
  );
};

export default Unauthorized;