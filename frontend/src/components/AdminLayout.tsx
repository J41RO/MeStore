import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

interface AdminLayoutProps {
  children: React.ReactNode;
}

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const navigationItems = [
    { name: 'Panel Admin', href: '/admin-secure-portal/dashboard' },
    { name: 'Gestión de Usuarios', href: '/admin-secure-portal/users' },
    { name: 'Cola de Productos Entrantes', href: '/admin-secure-portal/cola-productos-entrantes' },
    { name: 'Alertas e Incidentes', href: '/admin-secure-portal/alertas-incidentes' },
    { name: 'Movement Tracker', href: '/admin-secure-portal/movement-tracker' },
    { name: 'Reportes de Discrepancias', href: '/admin-secure-portal/reportes-discrepancias' },
    { name: 'Logs y Auditoría', href: '/admin-secure-portal/auditoria' },
    { name: 'Mapa del Almacén', href: '/admin-secure-portal/warehouse-map' },
    { name: 'Configuración del Sistema', href: '/admin-secure-portal/system-config' },
    { name: 'Reportes Administrativos', href: '/admin-secure-portal/reports' },
    { name: 'Configuración de Roles', href: '/admin-secure-portal/roles' },
  ];

  const NavigationItems = ({ onItemClick }: { onItemClick?: () => void }) => (
    <nav className='space-y-1'>
      {navigationItems.map(item => {
        const isActive = location.pathname === item.href;
        return (
          <button
            key={item.name}
            onClick={() => {
              navigate(item.href);
              onItemClick?.();
            }}
            className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
              isActive
                ? 'bg-red-100 text-red-900 border-l-4 border-red-500'
                : 'text-gray-700 hover:bg-red-50 hover:text-red-700'
            }`}
          >
            {item.name}
          </button>
        );
      })}
    </nav>
  );

  return (
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
                SUPERUSER
              </span>
            </div>
            <button className='md:hidden bg-red-600 p-2 rounded-md text-red-200 hover:text-white hover:bg-red-500'>
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
      </header>

      <div className='flex'>
        {/* Sidebar */}
        <div
          className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out md:translate-x-0 md:static md:inset-0`}
        >
          <div className='flex flex-col h-full pt-16 md:pt-0'>
            <div className='flex-shrink-0 px-4 py-6 border-b border-gray-200'>
              <h2 className='text-lg font-semibold text-gray-900'>
                Administración
              </h2>
            </div>
            <div className='flex-1 px-4 py-6 overflow-y-auto'>
              <NavigationItems onItemClick={() => setSidebarOpen(false)} />
            </div>
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
        <div className='flex-1 md:ml-0'>
          <main className='py-6 px-4 sm:px-6 lg:px-8'>{children}</main>
        </div>
      </div>
    </div>
  );
};

export default AdminLayout;