import React, { useState } from 'react';
import { vendorApi } from '../../services/api_vendor';
import { useAuthStore } from '../../stores/authStore';
import { UserType } from '../../stores/authStore';

interface VendorLoginProps {
  onLoginSuccess?: () => void;
}

const VendorLogin: React.FC<VendorLoginProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { login } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await vendorApi.auth.login({ email, password });
      const { access_token, user } = response.data;
      
      // Guardar token y usuario en el store
      login(access_token, { ...user, user_type: UserType.VENDEDOR });
      
      if (onLoginSuccess) {
        onLoginSuccess();
      }
    } catch (error: any) {
      setError(error.response?.data?.message || 'Error en el login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="vendor-login-container">
      <h2>Login Vendedor</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <div className="error">{error}</div>}
        <button type="submit" disabled={loading}>
          {loading ? 'Ingresando...' : 'Ingresar'}
        </button>
      </form>
    </div>
  );
};

export default VendorLogin;