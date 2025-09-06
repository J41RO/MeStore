import { Routes, Route, Navigate } from 'react-router-dom';
import TestImageUpload from './pages/TestImageUpload';
import TestInventory from './pages/TestInventory';
import TestStockMovements from './pages/TestStockMovements';
import { lazy, Suspense } from 'react';
import Layout from './components/Layout';
import AuthGuard from './components/AuthGuard';
import ErrorBoundary from './components/ErrorBoundary';
import PageLoader from './components/ui/Loading/PageLoader';
import VendorLanding from './pages/VendorLanding';
import './App.css';

// Lazy loading de páginas principales
const Dashboard = lazy(() => import('./pages/Dashboard'));
const DashboardLayout = lazy(() => import('./components/DashboardLayout'));
const AdminLayout = lazy(() => import('./components/AdminLayout'));
const AdminDashboard = lazy(() => import('./pages/admin/AdminDashboard'));
const UserManagement = lazy(() => import('./pages/admin/UserManagement'));
const SystemConfig = lazy(() => import('./pages/admin/SystemConfig'));
const Productos = lazy(() => import('./pages/Productos'));
const CommissionReport = lazy(
  () => import('./components/reports/CommissionReport')
);
const Login = lazy(() => import('./pages/Login'));
const NotFound = lazy(() => import('./pages/NotFound'));
const RegisterVendor = lazy(() => import('./pages/RegisterVendor'));
const OTPVerification = lazy(() => import('./components/OTPVerification'));

// Componentes de auth con lazy loading
const OTPDemo = lazy(() => import('./components/OTPDemo'));
const VendorTest = lazy(() => import('./pages/VendorTest'));

function App() {
  return (
    <ErrorBoundary>
      <Routes>
        {/* Ruta principal pública - Landing Page */}
        <Route path='/' element={<VendorLanding />} />
        <Route path='/test-imageupload' element={<TestImageUpload />} />
        <Route path='/test-inventory' element={<TestInventory />} />
        <Route path='/test-stock-movements' element={<TestStockMovements />} />
        <Route path='/vendor-test' element={
          <Suspense fallback={<PageLoader />}>
            <VendorTest />
          </Suspense>
        } />

        {/* Rutas protegidas con Layout */}
        <Route
          path='/app'
          element={
            <AuthGuard>
              <Layout />
            </AuthGuard>
          }
        >
          <Route index element={<Navigate to='/app/dashboard' replace />} />
          <Route
            path='dashboard'
            element={
              <Suspense fallback={<PageLoader />}>
                <DashboardLayout>
                  <Dashboard />
                </DashboardLayout>
              </Suspense>
            }
          />
          <Route
            path='productos'
            element={
              <Suspense fallback={<PageLoader />}>
                <Productos />
              </Suspense>
            }
          />{' '}
          <Route
            path='reportes/comisiones'
            element={
              <Suspense fallback={<PageLoader />}>
                <DashboardLayout>
                  <CommissionReport />
                </DashboardLayout>
              </Suspense>
            }
          />
        </Route>

        {/* Rutas públicas de autenticación */}
        <Route
          path='/auth/login'
          element={
            <Suspense fallback={<PageLoader />}>
              <Login />
            </Suspense>
          }
        />
        <Route
          path='/register'
          element={
            <Suspense fallback={<PageLoader />}>
              <RegisterVendor />
            </Suspense>
          }
        />
        <Route
          path='/verify-otp'
          element={
            <Suspense fallback={<PageLoader />}>
              <OTPVerification />
            </Suspense>
          }
        />
        <Route
          path='/auth/otp'
          element={
            <Suspense fallback={<PageLoader />}>
              <OTPDemo />
            </Suspense>
          }
        />
        {/* Rutas administrativas protegidas */}
        <Route
          path='/admin/*'
          element={
            <AuthGuard>
              <Suspense fallback={<PageLoader />}>
                <AdminLayout>
                  <Routes>
                    <Route path='dashboard' element={<AdminDashboard />} />
                    <Route path='users' element={<UserManagement />} />
                    <Route path='system-config' element={<SystemConfig />} />
                    <Route
                      index
                      element={<Navigate to='dashboard' replace />}
                    />
                  </Routes>
                </AdminLayout>
              </Suspense>
            </AuthGuard>
          }
        />

        {/* Ruta 404 - DEBE IR AL FINAL */}
        <Route
          path='*'
          element={
            <Suspense fallback={<PageLoader />}>
              <NotFound />
            </Suspense>
          }
        />
      </Routes>
    </ErrorBoundary>
  );
}

export default App;