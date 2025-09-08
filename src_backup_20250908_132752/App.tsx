import { Routes, Route, Navigate, lazy, Suspense } from 'react-router-dom';
import Layout from './components/Layout';
import AuthGuard from './components/AuthGuard';
import ErrorBoundary from './components/ErrorBoundary';
import PageLoader from './components/ui/Loading/PageLoader';
import './App.css';

// Lazy loading de páginas principales
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Productos = lazy(() => import('./pages/Productos'));
const Login = lazy(() => import('./pages/Login'));

// Componentes de auth con lazy loading
const OTPDemo = lazy(() => import('./components/OTPDemo'));
const ForgotPassword = lazy(() => import('./components/auth/ForgotPassword'));
const ResetPassword = lazy(() => import('./components/auth/ResetPassword'));

import './components/auth/PasswordReset.css';

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
        <Route path="/auth/forgot-password" element={
          <Suspense fallback={<PageLoader />}>
            <ForgotPassword onBackToLogin={() => window.history.back()} />
          </Suspense>
        } />
        <Route path="/auth/reset-password" element={
          <Suspense fallback={<PageLoader />}>
            <ResetPassword />
          </Suspense>
        } />
      </Routes>
    </ErrorBoundary>
  );
}

export default App;
