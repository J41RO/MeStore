import { Routes, Route, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import Layout from './components/Layout';
import AuthGuard from './components/AuthGuard';
import ErrorBoundary from './components/ErrorBoundary';
import PageLoader from './components/ui/Loading/PageLoader';
import './App.css';

// Lazy loading de páginas principales
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Productos = lazy(() => import('./pages/Productos'));
const Login = lazy(() => import('./pages/Login'));
const NotFound = lazy(() => import("./pages/NotFound"));

// Componentes de auth con lazy loading
const OTPDemo = lazy(() => import('./components/OTPDemo'));

function App() {
  return (
    <ErrorBoundary>
      <Routes>
        {/* Rutas protegidas con Layout */}
        <Route path="/" element={
          <AuthGuard>
            <Layout />
          </AuthGuard>
        }>
          <Route index element={<Navigate to="/dashboard" replace />} />
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
