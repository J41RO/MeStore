import React from 'react';
import VendorLogin from '../components/auth/VendorLogin';
import VendorDashboard from '../components/dashboard/VendorDashboard';
import { useAuthStore } from '../stores/authStore';

const VendorTest: React.FC = () => {
  const { isAuthenticated, logout, user } = useAuthStore();

  const handleLoginSuccess = () => {
    console.log('Login exitoso');
  };

  const handleLogout = () => {
    logout();
  };

  if (!isAuthenticated) {
    return (
      <div className="vendor-test-page">
        <h1>Test Vendedor - MeStocker</h1>
        <h2>Prueba de Login</h2>
        <p>Usa las credenciales: test@mestore.com / 123456</p>
        <VendorLogin onLoginSuccess={handleLoginSuccess} />
      </div>
    );
  }

  return (
    <div className="vendor-test-page">
      <h1>Test Vendedor - MeStocker</h1>
      <div className="user-info">
        <p>Usuario: {user?.email}</p>
        <button onClick={handleLogout}>Cerrar Sesion</button>
      </div>
      <VendorDashboard />
    </div>
  );
};

export default VendorTest;