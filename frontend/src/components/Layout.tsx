import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useApp } from '../hooks/useApp';
import HamburgerIcon from './ui/HamburgerIcon/HamburgerIcon';
import MobileMenu from './ui/MobileMenu/MobileMenu';

const Layout: React.FC = () => {
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { isDarkMode, toggleTheme, notifications, showSuccessNotification } =
    useApp();

  // Mobile menu state
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const closeMobileMenu = () => setIsMobileMenuOpen(false);
  const toggleMobileMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen);

  return (
    <div
      className={`min-h-screen ${isDarkMode ? 'dark bg-gray-900' : 'bg-gray-50'}`}
    >
      {/* MICRO-FASE 1 COMPLETADA: Header adaptativo con múltiples breakpoints */}
      <nav
        className={`shadow-sm border-b py-1 sm:py-2 md:py-3 lg:py-4 xl:py-4 2xl:py-5 ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white'}`}
      >
        <div className='max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8 xl:px-10 2xl:px-12'>
          <div className='flex justify-between h-14 sm:h-16 lg:h-18 xl:h-20'>
            {/* Left Section - Navigation and Controls */}
            <div className='flex items-center space-x-2 sm:space-x-4 md:space-x-6 lg:space-x-8'>
              {/* Hamburger Icon para mobile */}
              <HamburgerIcon
                isOpen={isMobileMenuOpen}
                onClick={toggleMobileMenu}
                className='block sm:hidden'
              />

              {/* Logo - Responsive Text Size */}
              <Link
                to='/app/dashboard'
                className='text-lg sm:text-xl md:text-2xl font-bold text-gray-900 dark:text-white'
              >
                MeStore
              </Link>

              {/* Desktop Navigation - Hidden on mobile */}
              <div className='hidden md:flex space-x-2 lg:space-x-4'>
                <Link
                  to='/app/dashboard'
                  className={`px-2 sm:px-3 py-1 sm:py-2 rounded-md text-xs sm:text-sm font-medium transition-colors ${
                    location.pathname === '/app/dashboard'
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                      : 'text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white'
                  }`}
                >
                  Dashboard
                </Link>
                <Link
                  to='/app/productos'
                  className={`px-2 sm:px-3 py-1 sm:py-2 rounded-md text-xs sm:text-sm font-medium transition-colors ${
                    location.pathname === '/app/productos'
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                      : 'text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white'
                  }`}
                >
                  Productos
                </Link>
              </div>
            </div>

            {/* Right Section - User Controls */}
            <div className='flex items-center space-x-1 sm:space-x-2 md:space-x-3 lg:space-x-4'>
              {/* Contador de notificaciones - Responsive */}
              {notifications.hasUnread && (
                <div className='relative'>
                  <span className='inline-flex items-center px-1.5 sm:px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'>
                    {notifications.count}
                  </span>
                </div>
              )}

              {/* Theme Toggle - Responsive Size */}
              <button
                onClick={toggleTheme}
                className={`p-1 sm:p-2 rounded-md transition-colors ${
                  isDarkMode
                    ? 'text-gray-300 hover:text-white hover:bg-gray-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
                title={`Cambiar a modo ${isDarkMode ? 'claro' : 'oscuro'}`}
              >
                <span className='text-sm sm:text-base'>
                  {isDarkMode ? '☀️' : '🌙'}
                </span>
              </button>

              {/* Test Button - Hide on very small screens */}
              <button
                onClick={() =>
                  showSuccessNotification(
                    'Test Notification',
                    'Estado global funcionando!'
                  )
                }
                className='hidden sm:block px-2 sm:px-3 py-1 text-xs bg-green-100 text-green-800 rounded hover:bg-green-200 dark:bg-green-900 dark:text-green-300 transition-colors'
              >
                Test App
              </button>

              {/* Logout Button - Responsive Text */}
              <button
                onClick={logout}
                className='px-2 sm:px-3 py-1 sm:py-2 rounded-md text-xs sm:text-sm font-medium text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white transition-colors'
                title={`Cerrar sesión - ${user?.email}`}
              >
                <span className='hidden md:inline'>
                  Cerrar Sesión ({user?.email})
                </span>
                <span className='md:hidden'>Salir</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Menu - Enhanced with proper transitions */}
      <MobileMenu isOpen={isMobileMenuOpen} onClose={closeMobileMenu} />

      {/* Main Content Area */}
      <main className='relative'>
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
