import type { Metadata } from 'next';
import './globals.css';
import Link from 'next/link';
import {
  Activity,
  Database,
  FileText,
  Home,
  Settings,
  Shield,
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'MeStore Monitoring Dashboard',
  description: 'Real-time monitoring dashboard for MeStore backend',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-gray-900 text-gray-100 min-h-screen">
        <div className="flex min-h-screen">
          {/* Sidebar */}
          <aside className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
            <div className="p-6 border-b border-gray-700">
              <h1 className="text-2xl font-bold text-blue-400 flex items-center gap-2">
                <Activity className="w-6 h-6" />
                MeStore Monitor
              </h1>
              <p className="text-xs text-gray-400 mt-1">
                Real-time System Monitoring
              </p>
            </div>

            <nav className="flex-1 p-4 space-y-2">
              <NavLink href="/" icon={<Home className="w-5 h-5" />}>
                Dashboard
              </NavLink>

              <NavLink href="/logs" icon={<FileText className="w-5 h-5" />}>
                Logs
              </NavLink>

              <NavLink href="/database" icon={<Database className="w-5 h-5" />}>
                Database
              </NavLink>

              <div className="pt-4 mt-4 border-t border-gray-700">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide px-3 mb-2">
                  System
                </p>

                <NavLink href="/api" icon={<Shield className="w-5 h-5" />}>
                  API Health
                </NavLink>

                <NavLink
                  href="/settings"
                  icon={<Settings className="w-5 h-5" />}
                >
                  Settings
                </NavLink>
              </div>
            </nav>

            <div className="p-4 border-t border-gray-700">
              <div className="bg-gray-700/50 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-400">System Status</span>
                  <span className="flex items-center gap-1.5">
                    <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                    <span className="text-xs text-green-400 font-medium">
                      Operational
                    </span>
                  </span>
                </div>
                <p className="text-xs text-gray-500">
                  Last update: {new Date().toLocaleTimeString()}
                </p>
              </div>
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 overflow-auto">{children}</main>
        </div>
      </body>
    </html>
  );
}

function NavLink({
  href,
  icon,
  children,
}: {
  href: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-gray-700 hover:text-white transition-colors duration-200"
    >
      {icon}
      <span className="font-medium">{children}</span>
    </Link>
  );
}
