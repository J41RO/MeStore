import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Productos from './pages/Productos';
import './App.css';

// Componentes de auth existentes (preservados)
import OTPDemo from './components/OTPDemo';
import ForgotPassword from './components/auth/ForgotPassword';
import ResetPassword from './components/auth/ResetPassword';
import './components/auth/PasswordReset.css';

function App() {
  return (
    <Routes>
      {/* Rutas principales con Layout */}
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="productos" element={<Productos />} />
      </Route>
      
      {/* Rutas de auth sin Layout (preservadas del sistema actual) */}
      <Route path="/auth/otp" element={<OTPDemo />} />
      <Route path="/auth/forgot-password" element={
        <ForgotPassword onBackToLogin={() => window.history.back()} />
      } />
      <Route path="/auth/reset-password" element={<ResetPassword />} />
    </Routes>
  );
}

export default App;
