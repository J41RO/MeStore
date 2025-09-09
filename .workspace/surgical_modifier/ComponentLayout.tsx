// ~/MeStore/frontend/src/components/Componentlayout.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Componentlayout Component
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: Componentlayout.tsx
// Ruta: ~/MeStore/frontend/src/components/Componentlayout.tsx
// Autor: Jairo
// Fecha de Creación: 2025-09-09 01:33:10
// Última Actualización: 2025-09-09 01:33:10
// Versión: 1.0.0
// Propósito: Auto-generated file
//
// ---------------------------------------------------------------------------------------------
import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

interface ComponentlayoutProps {
  children: React.ReactNode;
}

const Componentlayout: React.FC<ComponentlayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const navigationItems = [
    { name: 'Dashboard', href: '/dashboard' },
    { name: 'Settings', href: '/settings' },
    { name: 'Profile', href: '/profile' },
    { name: 'Reports', href: '/reports' },
  ];

  const NavigationItems = ({ onItemClick }: { onItemClick?: () => void }) => (
    <nav className="space-y-1">
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
                ? 'bg-blue-600 text-white'
                : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
            }`}
          >
            {item.name}
          </button>
        );
      })}
    </nav>
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 transform transition-transform duration-300 ease-in-out ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } md:translate-x-0`}>
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">Componentlayout</h1>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            <NavigationItems onItemClick={() => setSidebarOpen(false)} />
          </div>
        </div>
      </div>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="md:ml-64">
        <div className="sticky top-0 z-10 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between p-4">
            <button
              className="md:hidden text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <h2 className="text-lg font-medium text-gray-900 dark:text-white">Content Area</h2>
          </div>
        </div>
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Componentlayout;
