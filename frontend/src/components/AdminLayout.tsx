import React, { useState, useEffect, useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { AdminSidebar } from './admin/navigation/AdminSidebar';
import { NavigationProvider } from './admin/navigation/NavigationProvider';
import { RouteSync } from './admin/navigation/RouteSync';
import { UserRole } from './admin/navigation/NavigationTypes';
import { AccessibilityProvider } from './admin/navigation/AccessibilityProvider';
import { enterpriseNavigationConfig } from './admin/navigation/NavigationConfig';

interface AdminLayoutProps {
  children: React.ReactNode;
}

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, user } = useAuthStore();

  // Función para cerrar sidebar (para móvil)
  const closeSidebar = () => setSidebarOpen(false);

  // Función para toggle collapsed state
  const toggleSidebarCollapse = () => setSidebarCollapsed(prev => !prev);

  // Map user type to navigation role
  const userRole = useMemo(() => {
    switch (user?.user_type) {
      case 'SUPERUSER':
        return UserRole.SUPERUSER;
      case 'ADMIN':
        return UserRole.ADMIN;
      case 'MANAGER':
        return UserRole.MANAGER;
      case 'OPERATOR':
        return UserRole.OPERATOR;
      default:
        return UserRole.ADMIN; // Default fallback
    }
  }, [user?.user_type]);

  // Auto-close mobile sidebar on route change
  useEffect(() => {
    setSidebarOpen(false);
  }, [location.pathname]);

  return (
    <AccessibilityProvider>
      <NavigationProvider
        categories={enterpriseNavigationConfig}
        userRole={userRole}
        onError={(error) => console.error('Navigation Error:', error)}
      >
        {/* Route Synchronization */}
        <RouteSync enableBreadcrumbs={true} enableAnalytics={true} />

        <div className='min-h-screen bg-gray-50'>
          {/* Header administrativo */}
          <header className='bg-red-700 shadow-lg'>
            <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
              <div className='flex justify-between items-center py-4'>
                <div className='flex items-center'>
                  <h1 className='text-2xl font-bold text-white'>
                    Panel Administrativo
                  </h1>
                  <span className='ml-3 px-3 py-1 bg-red-800 text-red-100 text-xs font-semibold rounded-full'>
                    {user?.user_type || 'ADMIN'}
                  </span>
                </div>

                <div className='flex items-center space-x-4'>
                  <span className='text-red-100 text-sm hidden md:block'>
                    {user?.email}
                  </span>

                  {/* Botón Logout */}
                  <button
                    onClick={logout}
                    className='bg-red-600 hover:bg-red-500 text-white px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200'
                  >
                    Cerrar Sesión
                  </button>

                  <button
                    className='md:hidden bg-red-600 p-2 rounded-md text-red-200 hover:text-white hover:bg-red-500'
                    onClick={() => setSidebarOpen(!sidebarOpen)}
                  >
                    <svg
                      className='h-6 w-6'
                      fill='none'
                      viewBox='0 0 24 24'
                      stroke='currentColor'
                    >
                      <path
                        strokeLinecap='round'
                        strokeLinejoin='round'
                        strokeWidth={2}
                        d='M4 6h16M4 12h16M4 18h16'
                      />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </header>

          <div className='flex'>
            {/* Enterprise Navigation Sidebar */}
            <div
              className={`${
                sidebarOpen ? 'translate-x-0' : '-translate-x-full'
              } fixed inset-y-0 left-0 z-50 ${sidebarCollapsed ? 'w-16' : 'w-64'} bg-white shadow-lg transform transition-all duration-300 ease-in-out md:translate-x-0 md:static md:inset-0`}
            >
              <div className='flex flex-col h-full pt-16 md:pt-0'>
                <AdminSidebar
                  isCollapsed={sidebarCollapsed}
                  onToggleCollapse={toggleSidebarCollapse}
                  userRole={userRole}
                  user={{
                    id: user?.id || '',
                    email: user?.email || '',
                    role: userRole,
                    isActive: user?.is_active || true
                  }}
                  className='h-full'
                />
              </div>
            </div>

            {/* Overlay móvil */}
            {sidebarOpen && (
              <div
                className='fixed inset-0 z-40 bg-gray-600 bg-opacity-75 md:hidden'
                onClick={() => setSidebarOpen(false)}
              />
            )}

            {/* Contenido principal */}
            <div className={`flex-1 transition-all duration-300 ${sidebarCollapsed ? 'md:ml-16' : 'md:ml-64'}`}>
              <main className='py-6 px-4 sm:px-6 lg:px-8'>{children}</main>
            </div>
          </div>
        </div>
      </NavigationProvider>
    </AccessibilityProvider>
  );
};

export default AdminLayout;