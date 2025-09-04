import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

const RegisterVendor: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    nombre: '',
    apellido: '',
    empresa: '',
    cedula: '',
    telefono: '',
    ciudad: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const navigate = useNavigate();
  const {} = useAuthStore();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/v1/vendedores/registro', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        await response.json();
        // Redirigir a verificación OTP
        navigate('/verify-otp', { state: { telefono: formData.telefono } });
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Error en registro');
      }
    } catch (error) {
      setError('Error de conexión');
    }

    setLoading(false);
  };

  return (
    <div className='min-h-screen flex items-center justify-center bg-gray-50'>
      <div className='max-w-md w-full space-y-8'>
        <div>
          <h2 className='mt-6 text-center text-3xl font-extrabold text-gray-900'>
            Registro de Vendedor
          </h2>
        </div>
        <form className='mt-8 space-y-6' onSubmit={handleSubmit}>
          {error && (
            <div className='bg-red-100 text-red-700 p-3 rounded'>{error}</div>
          )}

          <div className='grid grid-cols-2 gap-4'>
            <input
              type='text'
              name='nombre'
              required
              value={formData.nombre}
              onChange={handleChange}
              placeholder='Nombre'
              className='w-full px-3 py-2 border border-gray-300 rounded-md'
            />
            <input
              type='text'
              name='apellido'
              required
              value={formData.apellido}
              onChange={handleChange}
              placeholder='Apellido'
              className='w-full px-3 py-2 border border-gray-300 rounded-md'
            />
          </div>

          <input
            type='email'
            name='email'
            required
            value={formData.email}
            onChange={handleChange}
            placeholder='Email'
            className='w-full px-3 py-2 border border-gray-300 rounded-md'
          />

          <input
            type='password'
            name='password'
            required
            value={formData.password}
            onChange={handleChange}
            placeholder='Contraseña'
            className='w-full px-3 py-2 border border-gray-300 rounded-md'
          />

          <input
            type='text'
            name='empresa'
            required
            value={formData.empresa}
            onChange={handleChange}
            placeholder='Empresa'
            className='w-full px-3 py-2 border border-gray-300 rounded-md'
          />

          <input
            type='text'
            name='cedula'
            required
            value={formData.cedula}
            onChange={handleChange}
            placeholder='Cédula'
            className='w-full px-3 py-2 border border-gray-300 rounded-md'
          />

          <input
            type='tel'
            name='telefono'
            required
            value={formData.telefono}
            onChange={handleChange}
            placeholder='Teléfono (+57)'
            className='w-full px-3 py-2 border border-gray-300 rounded-md'
          />

          <input
            type='text'
            name='ciudad'
            required
            value={formData.ciudad}
            onChange={handleChange}
            placeholder='Ciudad'
            className='w-full px-3 py-2 border border-gray-300 rounded-md'
          />

          <button
            type='submit'
            disabled={loading}
            className='w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400'
          >
            {loading ? 'Registrando...' : 'Registrarse'}
          </button>

          <div className='text-center'>
            <button
              type='button'
              onClick={() => navigate('/login')}
              className='text-blue-600 hover:text-blue-800'
            >
              ¿Ya tienes cuenta? Inicia sesión
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RegisterVendor;
