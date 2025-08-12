import React, { useState } from 'react';

/**
 * Componente LoginForm con validación completa
 * 
 * Características:
 * - Validación en tiempo real de email y password
 * - Integración con API /api/v1/auth/login
 * - Manejo de estados loading/success/error
 * - Callback opcional onLoginSuccess
 * 
 * @component
 * @example
 * 
 */
// Interface para props del componente
export interface LoginFormProps {
  onLoginSuccess?: (data: any) => void;
  className?: string;
}

// Interface para respuesta de la API
interface ApiResponse {
  success: boolean;
  message: string;
  data?: any;
  error?: string;
}

// Componente funcional LoginForm
export const LoginForm: React.FC<LoginFormProps> = ({
  onLoginSuccess,
  className = ""
}) => {
  // Estados locales
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');
  const [messageType, setMessageType] = useState<'success' | 'error' | ''>('');

  // Funciones de validación
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validatePassword = (password: string): boolean => {
    // Mínimo 8 caracteres, al menos 1 número, 1 mayúscula
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/;
    return passwordRegex.test(password);
  };

  // Estado de validación del formulario
  const isFormValid = validateEmail(email) && validatePassword(password);

  // Función handleSubmit con integración API
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    // Validar formulario antes de enviar
    if (!isFormValid) {
      setMessage('Por favor corrige los errores antes de enviar');
      setMessageType('error');
      return;
    }

    setLoading(true);
    setMessage('');
    
    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email.trim(),
          password: password,
        }),
      });

      const data: ApiResponse = await response.json();

      if (data.success) {
        setMessage('Inicio de sesión exitoso');
        setMessageType('success');
        
        // Llamar callback si se proporciona
        if (onLoginSuccess) {
          onLoginSuccess(data.data);
        }
        
        // Limpiar formulario
        setEmail('');
        setPassword('');
      } else {
        setMessage(data.message || 'Error al iniciar sesión');
        setMessageType('error');
      }
    } catch (error) {
      console.error('Error en login:', error);
      setMessage('Error de conexión. Intenta nuevamente.');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`login-form ${className}`}>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          {email.length > 0 && !validateEmail(email) && (
            <span className="error-message" style={{color: 'red', fontSize: '12px', display: 'block', marginTop: '4px'}}>
              Por favor ingresa un email válido
            </span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {password.length > 0 && !validatePassword(password) && (
            <span className="error-message" style={{color: 'red', fontSize: '12px', display: 'block', marginTop: '4px'}}>
              Mínimo 8 caracteres, 1 mayúscula y 1 número
            </span>
          )}
        </div>

        <button type="submit" disabled={loading || !isFormValid}>
          {loading ? 'Logging in...' : 'Login'}
        </button>

        {message && (
          <div className={`message ${messageType}`}>
            {message}
          </div>
        )}
      </form>
    </div>
  );
};

export default LoginForm;