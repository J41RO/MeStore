import { Routes, Route, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import Layout from './components/Layout';
import AuthGuard from './components/AuthGuard';
import ErrorBoundary from './components/ErrorBoundary';
import PageLoader from './components/ui/Loading/PageLoader';
import VendorLanding from './pages/VendorLanding';
import './App.css';

// Lazy loading de páginas principales
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Productos = lazy(() => import('./pages/Productos'));
const Login = lazy(() => import('./pages/Login'));
const NotFound = lazy(() => import("./pages/NotFound"));
const RegisterVendor = lazy(() => import('./pages/RegisterVendor'));
const OTPVerification = lazy(() => import('./components/OTPVerification'));

// Componentes de auth con lazy loading
const OTPDemo = lazy(() => import('./components/OTPDemo'));

function App() {
  return (
    <ErrorBoundary>
      <Routes>
        {/* Ruta principal pública - Landing Page */}
        <Route path="/" element={<VendorLanding />} />
        
        {/* Rutas protegidas con Layout */}
        <Route path="/app" element={
          <AuthGuard>
            <Layout />
          </AuthGuard>
        }>
          <Route index element={<Navigate to="/app/dashboard" replace />} />
          <Route path="dashboard" element={
            <Suspense fallback={<PageLoader />}>
              <Dashboard />
            </Suspense>
          } />
          <Route path="productos" element={
            <Suspense fallback={<PageLoader />}>
              <Productos />
            </Suspense>
          } />
        </Route>
        
        {/* Rutas públicas de autenticación */}
        <Route path="/auth/login" element={
          <Suspense fallback={<PageLoader />}>
            <Login />
          </Suspense>
        } />
        <Route path="/register" element={
          <Suspense fallback={<PageLoader />}>
            <RegisterVendor />
          </Suspense>
        } />
        <Route path="/verify-otp" element={
          <Suspense fallback={<PageLoader />}>
            <OTPVerification />
          </Suspense>
        } />
        <Route path="/auth/otp" element={
          <Suspense fallback={<PageLoader />}>
            <OTPDemo />
          </Suspense>
        } />
        {/* Ruta 404 - DEBE IR AL FINAL */}
        <Route path="*" element={
          <Suspense fallback={<PageLoader />}>
            <NotFound />
          </Suspense>
        } />
      </Routes>
    </ErrorBoundary>
  );
}

export default App;
