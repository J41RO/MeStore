import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useApp } from '../hooks/useApp';

const Layout: React.FC = () => {
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { 
    isDarkMode, 
    toggleTheme,
    notifications,
    showSuccessNotification
  } = useApp();
  
  return (
    <div className={`min-h-screen ${isDarkMode ? 'dark bg-gray-900' : 'bg-gray-50'}`}>
      <nav className={`shadow-sm border-b ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              {/* Contador de notificaciones */}
              {notifications.hasUnread && (
                <div className="relative">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300">
                    {notifications.count}
                  </span>
                </div>
              )}
              
              {/* Botón de theme toggle */}
              <button
                onClick={toggleTheme}
                className={`p-2 rounded-md ${
                  isDarkMode 
                    ? 'text-gray-300 hover:text-white hover:bg-gray-700' 
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
                title={`Cambiar a modo ${isDarkMode ? 'claro' : 'oscuro'}`}
              >
                {isDarkMode ? '☀️' : '🌙'}
              </button>
              
              {/* Botón de test para notificaciones */}
              <button
                onClick={() => showSuccessNotification('Test Notification', 'Estado global funcionando!')}
                className="px-3 py-1 text-xs bg-green-100 text-green-800 rounded hover:bg-green-200 dark:bg-green-900 dark:text-green-300"
              >
                Test App
              </button>
              <Link to="/dashboard" className="text-xl font-bold text-gray-900">
                MeStore
              </Link>
              <div className="flex space-x-4">
                <Link
                  to="/dashboard"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    location.pathname === '/dashboard'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Dashboard
                </Link>
                <Link
                  to="/productos"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    location.pathname === '/productos'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Productos
                </Link>
              </div>
            </div>
            <div className="flex items-center">
              <button
                onClick={logout}
                className="px-3 py-2 rounded-md text-sm font-medium text-gray-500 hover:text-gray-700"
              >
                Cerrar Sesión ({user?.email})
              </button>
            </div>
          </div>
        </div>
      </nav>
      <main>
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;