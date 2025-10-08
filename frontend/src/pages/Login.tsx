import React, { useState } from 'react';
import { UserType } from '../stores/authStore';
import { Navigate, useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { ShoppingCart, Lock, Mail } from 'lucide-react';
import GoogleSignInButton from '../components/auth/GoogleSignInButton';
import axios from 'axios';
import { validateEmail, validatePassword } from '../utils/formValidation';

// Función de redirección inteligente basada en UserType y portal_type
const getRedirectPath = (userType: UserType, portalType?: string, returnTo?: string): string => {
  // If there's a returnTo URL, use it (for checkout flow)
  if (returnTo) {
    return returnTo;
  }

  switch (userType) {
    case UserType.VENDOR:
      return '/app/vendor-dashboard'; // FIXED: Vendors go to vendor dashboard
    case UserType.BUYER:
      return '/app/dashboard'; // Buyers go to buyer dashboard
    case UserType.ADMIN:
    case UserType.SUPERUSER:
      // Portal oculto para admins con credenciales específicas
      if (portalType === 'secure') {
        return '/admin-secure-portal/dashboard';
      }
      return '/admin/dashboard';
    default:
      return '/dashboard'; // Default: use RoleBasedRedirect to determine correct path
  }
};

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { login, isAuthenticated, error, setError } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();

  // Form validation errors
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [touched, setTouched] = useState({ email: false, password: false });

  // Get returnTo from query params (for checkout flow)
  const returnTo = searchParams.get('returnTo');
  const from = (location.state as any)?.from || returnTo || '/dashboard';

  if (isAuthenticated) {
    return <Navigate to={from} replace />;
  }

  // Real-time email validation
  const handleEmailChange = (value: string) => {
    setEmail(value);
    if (touched.email) {
      const validation = validateEmail(value);
      setEmailError(validation.isValid ? null : validation.error || null);
    }
  };

  // Real-time password validation
  const handlePasswordChange = (value: string) => {
    setPassword(value);
    if (touched.password) {
      const validation = validatePassword(value);
      setPasswordError(validation.isValid ? null : validation.error || null);
    }
  };

  // Mark field as touched on blur
  const handleBlur = (field: 'email' | 'password') => {
    setTouched({ ...touched, [field]: true });

    // Trigger validation
    if (field === 'email') {
      const validation = validateEmail(email);
      setEmailError(validation.isValid ? null : validation.error || null);
    } else if (field === 'password') {
      const validation = validatePassword(password);
      setPasswordError(validation.isValid ? null : validation.error || null);
    }
  };

  // Check if form is valid
  const isFormValid = () => {
    const emailValidation = validateEmail(email);
    const passwordValidation = validatePassword(password);
    return emailValidation.isValid && passwordValidation.isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched
    setTouched({ email: true, password: true });

    // Validate all fields
    const emailValidation = validateEmail(email);
    const passwordValidation = validatePassword(password);

    setEmailError(emailValidation.isValid ? null : emailValidation.error || null);
    setPasswordError(passwordValidation.isValid ? null : passwordValidation.error || null);

    // Don't submit if validation fails
    if (!emailValidation.isValid || !passwordValidation.isValid) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Attempt login using Zustand auth store (which calls real API)
      const success = await login(email, password);

      if (success) {
        // Get user data from the auth store after successful login
        const { user } = useAuthStore.getState();

        if (user) {
          // REDIRECCIÓN INTELIGENTE usando getRedirectPath with returnTo support
          const redirectPath = getRedirectPath(user.user_type, undefined, returnTo || undefined);
          navigate(redirectPath);

          // Clear checkout intent after successful login
          localStorage.removeItem('pendingCheckout');
          localStorage.removeItem('checkoutReturnUrl');
        } else {
          // Fallback redirect to role-based redirect or returnTo
          navigate(returnTo || '/dashboard');
        }
      } else {
        // Handle login error - the error will be shown by the auth store error state
        console.error('Login failed');
      }
    } catch (error) {
      console.error('Error during login:', error);
      setError('Error de conexión. Verifica tu conexión a internet.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse: any) => {
    setIsLoading(true);
    setError(null);

    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

      // Enviar el token de Google al backend
      const response = await axios.post(`${API_BASE_URL}/api/v1/auth/google/login`, {
        id_token: credentialResponse.credential,
        user_type: 'BUYER' // Por defecto, puede ser cambiado según la lógica de negocio
      });

      if (response.data.success && response.data.access_token) {
        // Guardar el token y datos de usuario en el store
        const { setToken, setUser } = useAuthStore.getState();
        setToken(response.data.access_token);
        setUser(response.data.user);

        // Redireccionar según el tipo de usuario con returnTo support
        const redirectPath = getRedirectPath(response.data.user.user_type, undefined, returnTo || undefined);
        navigate(redirectPath);

        // Clear checkout intent after successful login
        localStorage.removeItem('pendingCheckout');
        localStorage.removeItem('checkoutReturnUrl');
      } else {
        setError(response.data.message || 'Error en login con Google');
      }
    } catch (error: any) {
      console.error('Error en Google login:', error);
      setError(error.response?.data?.detail || 'Error en login con Google');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleError = () => {
    setError('Error en login con Google. Inténtalo de nuevo.');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Layout dividido: Grid responsivo */}
      <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2">

        {/* LADO IZQUIERDO: Formulario (50%) */}
        <div className="flex items-center justify-center p-6 lg:p-12 relative">

          {/* Mobile brand message - solo visible en mobile */}
          <div className="absolute top-6 left-0 right-0 text-center lg:hidden px-6">
            <div className="inline-flex items-center gap-2 bg-white/80 backdrop-blur-sm px-4 py-2 rounded-full shadow-sm border border-gray-200">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <span className="text-sm font-bold text-gray-900">MeStocker</span>
            </div>
          </div>

          <div className="w-full max-w-md space-y-8 mt-16 lg:mt-0">

            {/* Header del formulario */}
            <div className="text-center">
              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-3">
                Iniciar Sesión
              </h1>
              <p className="text-base text-gray-600 font-medium">
                Accede a tu cuenta MeStocker
              </p>

              {/* Contextual message for checkout flow */}
              {returnTo === '/checkout' && (
                <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-xl" role="status" aria-live="polite">
                  <div className="flex items-center gap-2 mb-2">
                    <ShoppingCart className="w-5 h-5 text-blue-600 flex-shrink-0" aria-hidden="true" />
                    <p className="text-sm font-semibold text-blue-900">
                      Inicia sesión para completar tu compra
                    </p>
                  </div>
                  <p className="text-xs text-blue-700 leading-relaxed">
                    Tu carrito está guardado. Después de iniciar sesión, podrás continuar con el checkout.
                  </p>
                </div>
              )}
            </div>

            {/* Formulario de login */}
            <form className="space-y-6" onSubmit={handleSubmit}>

              {/* Error Display */}
              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg" role="alert">
                  <p className="text-sm text-red-700 font-medium">{error}</p>
                </div>
              )}

              {/* Campo Email */}
              <div className="space-y-2">
                <label htmlFor="email-input" className="block text-sm font-semibold text-gray-700">
                  <Mail className="inline w-4 h-4 mr-2" aria-hidden="true" />
                  Email *
                </label>
                <div className="relative">
                  <input
                    id="email-input"
                    type="email"
                    required
                    value={email}
                    onChange={e => handleEmailChange(e.target.value)}
                    onBlur={() => handleBlur('email')}
                    placeholder="tu@email.com"
                    aria-invalid={emailError ? 'true' : 'false'}
                    aria-describedby={emailError ? 'email-error' : undefined}
                    className={`w-full px-4 py-3 rounded-lg border ${
                      emailError
                        ? 'border-red-500 focus:ring-red-500/20'
                        : touched.email && email
                        ? 'border-green-500 focus:ring-green-500/20'
                        : 'border-gray-300 focus:ring-blue-500/20'
                    } focus:outline-none focus:ring-2 transition-all duration-200 text-gray-900 placeholder-gray-500 bg-white font-medium`}
                  />
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                    {emailError ? (
                      <svg className="w-5 h-5 text-red-500 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    ) : touched.email && email ? (
                      <svg className="w-5 h-5 text-green-500 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <Mail className="w-5 h-5 text-gray-400 transition-all" aria-hidden="true" />
                    )}
                  </div>
                </div>
                {emailError && (
                  <p id="email-error" className="text-sm text-red-600 font-medium" role="alert">{emailError}</p>
                )}
              </div>

              {/* Campo Contraseña */}
              <div className="space-y-2">
                <label htmlFor="password-input" className="block text-sm font-semibold text-gray-700">
                  <Lock className="inline w-4 h-4 mr-2" aria-hidden="true" />
                  Contraseña *
                </label>
                <div className="relative">
                  <input
                    id="password-input"
                    type="password"
                    required
                    value={password}
                    onChange={e => handlePasswordChange(e.target.value)}
                    onBlur={() => handleBlur('password')}
                    placeholder="Tu contraseña"
                    aria-invalid={passwordError ? 'true' : 'false'}
                    aria-describedby={passwordError ? 'password-error' : undefined}
                    className={`w-full px-4 py-3 rounded-lg border ${
                      passwordError
                        ? 'border-red-500 focus:ring-red-500/20'
                        : touched.password && password
                        ? 'border-green-500 focus:ring-green-500/20'
                        : 'border-gray-300 focus:ring-blue-500/20'
                    } focus:outline-none focus:ring-2 transition-all duration-200 text-gray-900 placeholder-gray-500 bg-white font-medium`}
                  />
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                    {passwordError ? (
                      <svg className="w-5 h-5 text-red-500 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    ) : touched.password && password ? (
                      <svg className="w-5 h-5 text-green-500 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <Lock className="w-5 h-5 text-gray-400 transition-all" aria-hidden="true" />
                    )}
                  </div>
                </div>
                {passwordError && (
                  <p id="password-error" className="text-sm text-red-600 font-medium" role="alert">{passwordError}</p>
                )}
              </div>

              {/* Recordar sesión */}
              <div className="flex items-center pt-2">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={e => setRememberMe(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 border-gray-300 rounded transition-colors"
                  aria-label="Recordar mi sesión en este dispositivo"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700 font-medium">
                  Recordar sesión
                </label>
              </div>

              {/* Botón de Login */}
              <button
                type="submit"
                disabled={isLoading || !isFormValid()}
                aria-busy={isLoading}
                className={`w-full py-4 px-6 rounded-xl font-semibold text-base transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 shadow-lg ${
                  isLoading || !isFormValid()
                    ? 'bg-gray-400 text-gray-200 cursor-not-allowed border border-gray-500'
                    : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 hover:shadow-xl transform hover:-translate-y-0.5 focus:ring-blue-500 border border-blue-600'
                }`}
              >
                {isLoading ? (
                  <div className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Iniciando sesión...
                  </div>
                ) : (
                  'Iniciar Sesión'
                )}
              </button>

              {/* Divider */}
              <div className="relative" aria-hidden="true">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-3 bg-white text-gray-500 font-medium">O continúa con</span>
                </div>
              </div>

              {/* Botones OAuth */}
              <div className="space-y-3" role="group" aria-label="Opciones de inicio de sesión con redes sociales">
                <GoogleSignInButton
                  onSuccess={handleGoogleSuccess}
                  onError={handleGoogleError}
                  text="signin_with"
                  theme="outline"
                  size="large"
                  width="100%"
                />

                <button
                  type="button"
                  className="w-full inline-flex justify-center items-center py-3.5 px-4 border border-gray-300 rounded-lg shadow-sm bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
                  style={{ height: '48px' }}
                  aria-label="Continuar con Facebook"
                >
                  <svg className="w-5 h-5 mr-3" fill="#1877F2" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                  </svg>
                  Continuar con Facebook
                </button>
              </div>

              {/* Link al registro */}
              <div className="text-center pt-2">
                <p className="text-sm text-gray-600 font-medium">
                  ¿No tienes cuenta?{' '}
                  <a
                    href={returnTo ? `/register?returnTo=${encodeURIComponent(returnTo)}` : '/register'}
                    className="font-semibold text-blue-600 hover:text-blue-700 hover:underline transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded px-1"
                  >
                    Regístrate aquí
                  </a>
                </p>
                {returnTo === '/checkout' && (
                  <p className="text-xs text-gray-500 mt-2 leading-relaxed">
                    Crear una cuenta es rápido y te permitirá hacer seguimiento a tus pedidos
                  </p>
                )}
              </div>

            </form>

            {/* Forgot password link - OUTSIDE form to prevent submit conflicts */}
            <div className="mt-6 text-center border-t border-gray-200 pt-6">
              <button
                type="button"
                onClick={() => navigate('/login/forgot-password')}
                className="text-sm text-blue-600 hover:text-blue-700 hover:underline transition-colors font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded px-2 py-1"
                aria-label="Recuperar contraseña olvidada"
              >
                ¿Olvidaste tu contraseña?
              </button>
            </div>
          </div>
        </div>

        {/* LADO DERECHO: Visual 3D con branding MeStocker (50%) */}
        <div className="hidden lg:flex items-center justify-center bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 relative overflow-hidden">
          {/* Elementos de fondo 3D */}
          <div className="absolute inset-0">
            <div className="absolute top-20 left-20 w-32 h-32 bg-white/10 rounded-full blur-xl animate-pulse"></div>
            <div className="absolute bottom-32 right-16 w-24 h-24 bg-white/15 rounded-full blur-lg animate-pulse delay-300"></div>
            <div className="absolute top-1/2 left-16 w-16 h-16 bg-white/20 rounded-full blur-md animate-pulse delay-700"></div>
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:50px_50px]"></div>
          </div>

          {/* Contenido principal 3D */}
          <div className="relative z-10 text-center text-white p-12 max-w-lg">
            <div className="mb-8">
              <div className="mx-auto w-24 h-24 bg-white/20 backdrop-blur rounded-3xl flex items-center justify-center mb-6 shadow-2xl transform rotate-3 hover:rotate-0 transition-transform duration-500">
                <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <h1 className="text-4xl font-bold mb-2">MeStocker</h1>
              <p className="text-xl text-blue-100">Tu almacén digital</p>
            </div>

            <div className="space-y-6">
              <div className="flex justify-center space-x-4 mb-8">
                <div className="w-16 h-16 bg-gradient-to-br from-white/30 to-white/10 rounded-lg transform rotate-12 shadow-2xl backdrop-blur border border-white/20 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                  </svg>
                </div>
                <div className="w-16 h-16 bg-gradient-to-br from-white/25 to-white/5 rounded-lg transform -rotate-6 shadow-xl backdrop-blur border border-white/20 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div className="w-16 h-16 bg-gradient-to-br from-white/20 to-white/5 rounded-lg transform rotate-3 shadow-lg backdrop-blur border border-white/20 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
              </div>

              <div className="space-y-4">
                <div className="bg-white/10 backdrop-blur rounded-lg p-4 border border-white/20">
                  <h3 className="text-lg font-semibold mb-2">Bienvenido de vuelta</h3>
                  <p className="text-blue-100 text-sm">
                    Accede a tu dashboard personalizado y gestiona tu inventario con facilidad.
                  </p>
                </div>

                <div className="bg-white/5 backdrop-blur rounded-lg p-4 border border-white/10">
                  <h3 className="text-lg font-semibold mb-2">Sincronización en tiempo real</h3>
                  <p className="text-blue-100 text-sm">
                    Tus datos están seguros y sincronizados en la nube.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default Login;