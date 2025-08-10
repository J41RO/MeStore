import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import AuthGuard from './components/AuthGuard';
import Dashboard from './pages/Dashboard';
import Productos from './pages/Productos';
import Login from './pages/Login';
import './App.css';

// Componentes de auth existentes (preservados)
import OTPDemo from './components/OTPDemo';
import ForgotPassword from './components/auth/ForgotPassword';
import ResetPassword from './components/auth/ResetPassword';
import './components/auth/PasswordReset.css';

function App() {
  return (
    <Routes>
      {/* Rutas protegidas con Layout */}
      <Route path="/" element={
        <AuthGuard>
          <Layout />
        </AuthGuard>
      }>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="productos" element={<Productos />} />
      </Route>
      
      {/* Rutas públicas de autenticación */}
      <Route path="/auth/login" element={<Login />} />
      <Route path="/auth/otp" element={<OTPDemo />} />
      <Route path="/auth/forgot-password" element={
        <ForgotPassword onBackToLogin={() => window.history.back()} />
      } />
      <Route path="/auth/reset-password" element={<ResetPassword />} />
    </Routes>
  );
}

export default App;
