/**
 * Navigation Demo Component
 *
 * Simple demo to showcase the enterprise navigation system
 * with all implemented components working together.
 *
 * @version 1.0.0
 * @author React Specialist AI
 */

import React from 'react';
import { BrowserRouter } from 'react-router-dom';

import { AdminSidebar } from './AdminSidebar';
import { UserRole } from './NavigationTypes';

/**
 * Navigation Demo Component
 */
export const NavigationDemo: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = React.useState(false);

  const mockUser = {
    id: '1',
    email: 'admin@mestocker.com',
    role: UserRole.SUPERUSER,
    isActive: true
  };

  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-100">
        <AdminSidebar
          isCollapsed={isCollapsed}
          onToggleCollapse={() => setIsCollapsed(!isCollapsed)}
          userRole={UserRole.SUPERUSER}
          user={mockUser}
          title="MeStore Admin"
        />

        <main className="flex-1 p-8">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">
              Enterprise Navigation Demo
            </h1>

            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                Navigation Features
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-semibold text-blue-800 mb-2">✅ 4 Enterprise Categories</h3>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• Users (4 items)</li>
                    <li>• Vendors (5 items)</li>
                    <li>• Analytics (5 items)</li>
                    <li>• Settings (5 items)</li>
                  </ul>
                </div>

                <div className="p-4 bg-green-50 rounded-lg">
                  <h3 className="font-semibold text-green-800 mb-2">✅ Enterprise Features</h3>
                  <ul className="text-sm text-green-700 space-y-1">
                    <li>• Role-based access control</li>
                    <li>• Collapsible navigation</li>
                    <li>• Persistent state</li>
                    <li>• Performance optimized</li>
                  </ul>
                </div>

                <div className="p-4 bg-purple-50 rounded-lg">
                  <h3 className="font-semibold text-purple-800 mb-2">✅ Accessibility</h3>
                  <ul className="text-sm text-purple-700 space-y-1">
                    <li>• WCAG AA compliant</li>
                    <li>• Keyboard navigation</li>
                    <li>• Screen reader support</li>
                    <li>• Focus management</li>
                  </ul>
                </div>

                <div className="p-4 bg-orange-50 rounded-lg">
                  <h3 className="font-semibold text-orange-800 mb-2">✅ Technical</h3>
                  <ul className="text-sm text-orange-700 space-y-1">
                    <li>• TypeScript strict mode</li>
                    <li>• React 18 + Hooks</li>
                    <li>• Zustand state management</li>
                    <li>• Lazy loading support</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                Implementation Status
              </h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="text-green-800 font-medium">NavigationProvider</span>
                  <span className="text-green-600 text-sm">✅ Implemented</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="text-green-800 font-medium">CategoryNavigation</span>
                  <span className="text-green-600 text-sm">✅ Implemented</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="text-green-800 font-medium">NavigationCategory</span>
                  <span className="text-green-600 text-sm">✅ Implemented</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="text-green-800 font-medium">NavigationItem</span>
                  <span className="text-green-600 text-sm">✅ Implemented</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="text-green-800 font-medium">AdminSidebar</span>
                  <span className="text-green-600 text-sm">✅ Implemented</span>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default NavigationDemo;