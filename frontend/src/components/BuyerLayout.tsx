import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

interface BuyerLayoutProps {
  children: React.ReactNode;
}

const BuyerLayout: React.FC<BuyerLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, user } = useAuthStore();

  const navigationItems = [
    { name: 'Inicio', href: '/app/dashboard', icon: '🏠' },
    { name: 'Explorar Productos', href: '/marketplace/home', icon: '🛒' },
    { name: 'Mi Carrito', href: '/marketplace/cart', icon: '🛍️' },
    { name: 'Mis Compras', href: '/app/mis-compras', icon: '📦' },
    { name: 'Mi Perfil', href: '/app/mi-perfil', icon: '👤' },
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
            className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 flex items-center space-x-2 ${
              isActive
                ? 'bg-blue-100 text-blue-900 border-l-4 border-blue-500'
                : 'text-gray-700 hover:bg-blue-50 hover:text-blue-700'
            }`}
          >
            <span>{item.icon}</span>
            <span>{item.name}</span>
          </button>
        );
      })}
    </nav>
  );

  return (
    <div className='min-h-screen bg-gray-50'>
      {/* Header del comprador */}
      <header className='bg-blue-700 shadow-lg'>
        <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
          <div className='flex justify-between items-center py-4'>
            <div className='flex items-center'>
              <h1 className='text-2xl font-bold text-white'>
                MeStore
              </h1>
              <span className='ml-3 px-3 py-1 bg-blue-800 text-blue-100 text-xs font-semibold rounded-full'>
                COMPRADOR
              </span>
            </div>
            
            <div className='flex items-center space-x-4'>
              <span className='text-blue-100 text-sm hidden md:block'>
                {user?.email}
              </span>
              
              {/* Botón Logout */}
              <button 
                onClick={logout}
                className='bg-blue-600 hover:bg-blue-500 text-white px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200'
              >
                Cerrar Sesión
              </button>
              
              <button 
                className='md:hidden bg-blue-600 p-2 rounded-md text-blue-200 hover:text-white hover:bg-blue-500'
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
        {/* Sidebar */}
        <div
          className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out md:translate-x-0 md:static md:inset-0`}
        >
          <div className='flex flex-col h-full pt-16 md:pt-0'>
            <div className='flex-shrink-0 px-4 py-6 border-b border-gray-200'>
              <h2 className='text-lg font-semibold text-gray-900'>
                Panel de Comprador
              </h2>
              <p className='text-sm text-gray-500 mt-1'>
                Gestiona tus compras y perfil
              </p>
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
          <main>{children}</main>
        </div>
      </div>
    </div>
  );
};

export default BuyerLayout;