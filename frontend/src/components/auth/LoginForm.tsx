import React, { useState } from 'react';
import { useAuthStore } from '../../stores/authStore';
import type { LoginFormProps, ApiError } from '../../types';

/**
 * Production LoginForm Component
 * React Specialist AI Implementation
 *
 * Características:
 * - Integración completa con FastAPI backend
 * - Validación en tiempo real con feedback visual
 * - Manejo robusto de errores de API
 * - Estados de loading y success/error optimizados
 * - TypeScript completo para type safety
 *
 * @component
 */

export const LoginForm: React.FC<LoginFormProps> = ({
  onLoginSuccess,
  onLoginError,
  className = '',
  redirectPath,
  showRememberMe = false,
}) => {
  // Zustand auth store
  const { login, isLoading, error: authError, clearError } = useAuthStore();

  // Estados locales del formulario
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [rememberMe, setRememberMe] = useState<boolean>(false);
  const [touched, setTouched] = useState<{ email: boolean; password: boolean }>({
    email: false,
    password: false,
  });

  // Funciones de validación mejoradas
  const validateEmail = (email: string): { isValid: boolean; message?: string } => {
    if (!email) return { isValid: false, message: 'Email es requerido' };
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email)
      ? { isValid: true }
      : { isValid: false, message: 'Formato de email inválido' };
  };

  const validatePassword = (password: string): { isValid: boolean; message?: string } => {
    if (!password) return { isValid: false, message: 'Contraseña es requerida' };
    if (password.length < 6) {
      return { isValid: false, message: 'Mínimo 6 caracteres' };
    }
    return { isValid: true };
  };

  // Validación del formulario
  const emailValidation = validateEmail(email);
  const passwordValidation = validatePassword(password);
  const isFormValid = emailValidation.isValid && passwordValidation.isValid;

  // Limpia errores cuando el usuario empieza a escribir
  React.useEffect(() => {
    if (authError && (email || password)) {
      clearError();
    }
  }, [email, password, authError, clearError]);

  // Manejo del submit del formulario
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Marcar campos como tocados para mostrar errores
    setTouched({ email: true, password: true });

    // Validar formulario antes de enviar
    if (!isFormValid) {
      return;
    }

    try {
      // Usar el store de Zustand para login
      const success = await login(email.trim(), password);

      if (success) {
        // Login exitoso
        if (onLoginSuccess) {
          onLoginSuccess({ email: email.trim() });
        }

        // Redireccionar si se especifica
        if (redirectPath) {
          window.location.href = redirectPath;
        }

        // Limpiar formulario
        setEmail('');
        setPassword('');
        setTouched({ email: false, password: false });
      } else {
        // Error manejado por el store
        if (onLoginError) {
          onLoginError({
            message: authError || 'Error al iniciar sesión',
            status: 401
          });
        }
      }
    } catch (error) {
      console.error('Error en handleSubmit:', error);
      if (onLoginError) {
        onLoginError({
          message: 'Error inesperado durante el login',
          status: 500
        });
      }
    }
  };

  // Manejadores de eventos
  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    if (touched.email && authError) {
      clearError();
    }
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value);
    if (touched.password && authError) {
      clearError();
    }
  };

  const handleBlur = (field: 'email' | 'password') => {
    setTouched(prev => ({ ...prev, [field]: true }));
  };

  return (
    <div className={`w-full max-w-md mx-auto ${className}`}>
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Email Field */}
        <div>
          <label
            htmlFor="email"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Email *
          </label>
          <div className="relative">
            <input
              type="email"
              id="email"
              value={email}
              onChange={handleEmailChange}
              onBlur={() => handleBlur('email')}
              className={`w-full px-4 py-3 rounded-lg border ${
                touched.email && !emailValidation.isValid
                  ? 'border-red-300 focus:border-red-500'
                  : emailValidation.isValid && touched.email
                  ? 'border-green-300 focus:border-green-500'
                  : 'border-gray-300 focus:border-blue-500'
              } focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white`}
              placeholder="tu@email.com"
              autoComplete="email"
            />
            {/* Validation Icon */}
            {touched.email && (
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                {emailValidation.isValid ? (
                  <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                )}
              </div>
            )}
          </div>
          {touched.email && !emailValidation.isValid && (
            <p className="mt-1 text-sm text-red-600">{emailValidation.message}</p>
          )}
        </div>

        {/* Password Field */}
        <div>
          <label
            htmlFor="password"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Contraseña *
          </label>
          <div className="relative">
            <input
              type="password"
              id="password"
              value={password}
              onChange={handlePasswordChange}
              onBlur={() => handleBlur('password')}
              className={`w-full px-4 py-3 rounded-lg border ${
                touched.password && !passwordValidation.isValid
                  ? 'border-red-300 focus:border-red-500'
                  : passwordValidation.isValid && touched.password
                  ? 'border-green-300 focus:border-green-500'
                  : 'border-gray-300 focus:border-blue-500'
              } focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 placeholder-gray-400 bg-white`}
              placeholder="Tu contraseña"
              autoComplete="current-password"
            />
            {/* Validation Icon */}
            {touched.password && (
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                {passwordValidation.isValid ? (
                  <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                )}
              </div>
            )}
          </div>
          {touched.password && !passwordValidation.isValid && (
            <p className="mt-1 text-sm text-red-600">{passwordValidation.message}</p>
          )}
        </div>

        {/* Remember Me Checkbox (opcional) */}
        {showRememberMe && (
          <div className="flex items-center">
            <input
              id="remember-me"
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700">
              Recordar sesión
            </label>
          </div>
        )}

        {/* Error Message */}
        {authError && (
          <div className="p-4 rounded-lg bg-red-100 border border-red-200">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm text-red-800">{authError}</p>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || !isFormValid}
          className={`w-full py-3 px-4 rounded-lg font-medium text-white transition-all duration-200 ${
            !isLoading && isFormValid
              ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
              : 'bg-gray-400 cursor-not-allowed'
          }`}
        >
          {isLoading ? (
            <div className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Iniciando sesión...
            </div>
          ) : (
            'Iniciar Sesión'
          )}
        </button>
      </form>
    </div>
  );
};

export default LoginForm;
