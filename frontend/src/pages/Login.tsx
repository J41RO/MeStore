import React, { useState } from 'react';
import { UserType } from '../stores/authStore';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, isAuthenticated } = useAuthStore();
  const location = useLocation();

  const from = (location.state as any)?.from || '/dashboard';

  if (isAuthenticated) {
    return <Navigate to={from} replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // 🔧 CREDENCIALES FICTICIAS PARA DESARROLLO
    if (email === 'test@mestore.com' && password === '123456') {
      const fakeUser = {
        id: 'dev-user-001',
        email: 'test@mestore.com',
        name: 'Usuario de Prueba',
        user_type: 'ADMIN' as UserType,
        profile: null,
      };
      const fakeToken = 'dev-token-' + Date.now();

      login(fakeToken, fakeUser);
      return;
    }
    // Conectar con API real de vendedores
    try {
      const response = await fetch('/api/v1/vendedores/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        login(data.token, data.user);
      } else {
        console.error('Error de autenticación');
      }
    } catch (error) {
      console.error('Error de conexión:', error);
    }
  };

  return (
    <div className='min-h-screen flex items-center justify-center bg-gray-50'>
      <div className='max-w-md w-full space-y-8'>
        <div>
          <h2 className='mt-6 text-center text-3xl font-extrabold text-gray-900'>
            Iniciar Sesión
          </h2>
        </div>
        <form className='mt-8 space-y-6' onSubmit={handleSubmit}>
          <div>
            <input
              type='email'
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder='Email'
              className='w-full px-3 py-2 border border-gray-300 rounded-md'
            />
          </div>
          <div>
            <input
              type='password'
              required
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder='Contraseña'
              className='w-full px-3 py-2 border border-gray-300 rounded-md'
            />
          </div>
          <button
            type='submit'
            className='w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700'
          >
            Ingresar
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;