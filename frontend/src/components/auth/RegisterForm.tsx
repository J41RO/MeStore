import React, { useState } from 'react';

/**
 * Componente RegisterForm para usuarios colombianos
 *
 * Características:
 * - Campos específicos para Colombia: cédula, teléfono +57
 * - Validación en tiempo real de todos los campos
 * - Integración con API /api/v1/auth/register
 * - Manejo de estados loading/success/error
 * - Callback opcional onRegisterSuccess
 */

interface RegisterFormProps {
  onRegisterSuccess?: () => void;
}

interface ApiResponse {
  success: boolean;
  message: string;
  data?: any;
}

const RegisterForm: React.FC<RegisterFormProps> = ({ onRegisterSuccess }) => {
  // Estados para campos colombianos
  const [nombre, setNombre] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');
  const [cedula, setCedula] = useState<string>('');
  const [telefono, setTelefono] = useState<string>('');
  
  // Estados de control
  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');
  const [messageType, setMessageType] = useState<'success' | 'error'>('error');

  // Validaciones específicas para campos colombianos
  const validateNombre = (value: string): boolean => {
    const words = value.trim().split(/\s+/);
    return words.length >= 2 && /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(value);
  };

  const validateEmail = (value: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value);
  };

  const validatePassword = (value: string): boolean => {
    return value.length >= 8 && /(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value);
  };

  const validateConfirmPassword = (value: string): boolean => {
    return value === password && value.length > 0;
  };

  const validateCedula = (value: string): boolean => {
    const numericValue = value.replace(/\D/g, '');
    return numericValue.length >= 8 && numericValue.length <= 10 && /^\d+$/.test(numericValue);
  };

  const validateTelefono = (value: string): boolean => {
    const phoneRegex = /^\+57\s?\d{3}\s?\d{3}\s?\d{4}$/;
    return phoneRegex.test(value);
  };

  const isFormValid = (): boolean => {
    return validateNombre(nombre) &&
           validateEmail(email) &&
           validatePassword(password) &&
           validateConfirmPassword(confirmPassword) &&
           validateCedula(cedula) &&
           validateTelefono(telefono);
  };

  // Implementación del handleSubmit con API integration
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isFormValid()) {
      setMessage('Por favor complete todos los campos correctamente');
      setMessageType('error');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          nombre,
          email,
          cedula: cedula.replace(/\D/g, ''), // Solo números para la API
          telefono,
          password,
        }),
      });

      const data: ApiResponse = await response.json();

      if (data.success) {
        setMessage('¡Registro exitoso! Bienvenido/a a MeStore');
        setMessageType('success');
        
        // Limpiar formulario
        setNombre('');
        setEmail('');
        setPassword('');
        setConfirmPassword('');
        setCedula('');
        setTelefono('');
        
        // Llamar callback si existe
        if (onRegisterSuccess) {
          setTimeout(() => onRegisterSuccess(), 2000);
        }
      } else {
        setMessage(data.message || 'Error en el registro');
        setMessageType('error');
      }
    } catch (error) {
      setMessage('Error de conexión. Intente nuevamente');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto', padding: '20px' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '30px', color: '#333' }}>
        Registro - Usuario Colombiano
      </h2>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* Nombre Completo */}
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Nombre Completo *
          </label>
          <input
            type="text"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            placeholder="ejemplo: Juan Carlos Pérez"
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '16px'
            }}
          />
          {nombre && !validateNombre(nombre) && (
            <div style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
              Debe tener al menos 2 nombres y solo letras
            </div>
          )}
        </div>

        {/* Email */}
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Correo Electrónico *
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="ejemplo: juan@correo.com"
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '16px'
            }}
          />
          {email && !validateEmail(email) && (
            <div style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
              Formato de email inválido
            </div>
          )}
        </div>

        {/* Cédula */}
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Cédula de Ciudadanía *
          </label>
          <input
            type="text"
            value={cedula}
            onChange={(e) => setCedula(e.target.value)}
            placeholder="ejemplo: 12345678"
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '16px'
            }}
          />
          {cedula && !validateCedula(cedula) && (
            <div style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
              Cédula debe tener entre 8-10 dígitos numéricos
            </div>
          )}
        </div>

        {/* Teléfono */}
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Teléfono Móvil *
          </label>
          <input
            type="tel"
            value={telefono}
            onChange={(e) => setTelefono(e.target.value)}
            placeholder="ejemplo: +57 300 123 4567"
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '16px'
            }}
          />
          {telefono && !validateTelefono(telefono) && (
            <div style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
              Formato: +57 300 123 4567
            </div>
          )}
        </div>

        {/* Password */}
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Contraseña *
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Mínimo 8 caracteres, mayúscula, minúscula y número"
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '16px'
            }}
          />
          {password && !validatePassword(password) && (
            <div style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
              Mínimo 8 caracteres con mayúscula, minúscula y número
            </div>
          )}
        </div>

        {/* Confirmar Password */}
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Confirmar Contraseña *
          </label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Repetir la contraseña"
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '16px'
            }}
          />
          {confirmPassword && !validateConfirmPassword(confirmPassword) && (
            <div style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
              Las contraseñas no coinciden
            </div>
          )}
        </div>

        {/* Mensaje de estado */}
        {message && (
          <div style={{
            color: messageType === 'success' ? 'green' : 'red',
            fontSize: '14px',
            textAlign: 'center',
            padding: '10px',
            backgroundColor: messageType === 'success' ? '#f0f8f0' : '#fef0f0',
            borderRadius: '4px'
          }}>
            {message}
          </div>
        )}

        {/* Botón de registro */}
        <button
          type="submit"
          disabled={!isFormValid() || loading}
          style={{
            padding: '12px',
            backgroundColor: isFormValid() && !loading ? '#007bff' : '#ccc',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: isFormValid() && !loading ? 'pointer' : 'not-allowed'
          }}
        >
          {loading ? 'Registrando...' : 'Registrarse'}
        </button>
      </form>
    </div>
  );
};

export default RegisterForm;