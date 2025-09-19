import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, user } = useAuthStore();

  const navigationItems = [
    { name: 'Dashboard', href: '/app/vendor-dashboard' },
    { name: 'Productos', href: '/app/productos' },
    { name: 'Órdenes', href: '/app/ordenes' },
    { name: 'Reportes', href: '/app/reportes' },
    { name: 'Comisiones', href: '/app/reportes/comisiones' },
    { name: 'Mi Perfil', href: '/app/perfil' },
  ];

  const NavigationItems = ({ onItemClick }: { onItemClick?: () => void }) => (
    <>
      {navigationItems.map(item => {
        const isActive = location.pathname === item.href;
        return (
          <a
            key={item.name}
            href={item.href}
            className={
              isActive
                ? 'block p-2 bg-blue-100 text-blue-700 rounded mb-1'
                : 'block p-2 text-gray-600 hover:bg-gray-100 rounded mb-1'
            }
            onClick={e => {
              e.preventDefault();
              navigate(item.href);
              if (onItemClick) onItemClick();
            }}
          >
            {item.name}
          </a>
        );
      })}
    </>
  );

  return (
    <div className='min-h-screen bg-gray-50 flex'>
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className='fixed inset-0 bg-gray-600 bg-opacity-75 z-40 lg:hidden'
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}

      {/* Sidebar */}
      <div className='w-64 bg-white shadow-lg lg:block hidden'>
        <div className='h-16 bg-blue-600 flex items-center justify-center'>
          <h1 className='text-white font-bold'>MeStore</h1>
        </div>
        <nav className='p-4'>
          <NavigationItems onItemClick={() => setSidebarOpen(false)} />
        </nav>
      </div>

      {/* Mobile sidebar */}
      <div
        className={
          sidebarOpen
            ? 'fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform translate-x-0 transition-transform lg:hidden'
            : 'fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform -translate-x-full transition-transform lg:hidden'
        }
      >
        <div className='h-16 bg-blue-600 flex items-center justify-center'>
          <h1 className='text-white font-bold'>MeStore</h1>
        </div>
        <nav className='p-4'>
          <NavigationItems onItemClick={() => setSidebarOpen(false)} />
        </nav>
      </div>

      {/* Main content */}
      <div className='flex-1 flex flex-col'>
        {/* Header */}
        <header className='h-16 bg-white shadow-sm border-b flex items-center px-6'>
          {/* Mobile menu button */}
          <button
            type='button'
            className='lg:hidden mr-4 p-2 rounded-md text-gray-500 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500'
            onClick={() => setSidebarOpen(true)}
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

          <h2 className='text-lg font-semibold text-gray-900'>
            Dashboard Principal
          </h2>

          <div className='ml-auto flex items-center space-x-4'>
            <span className='text-gray-600 text-sm hidden md:block'>
              {user?.email}
            </span>
            
            <button
              onClick={logout}
              className='bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200'
            >
              Cerrar Sesión
            </button>
            
            <div className='w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center'>
              <span className='text-white text-sm font-medium'>
                {user?.email?.charAt(0).toUpperCase() || 'U'}
              </span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className='flex-1 p-6'>{children}</main>
      </div>
    </div>
  );
};

export default DashboardLayout;
