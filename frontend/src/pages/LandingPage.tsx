import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthContext } from '../contexts/AuthContext';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuthContext();
  const [email, setEmail] = useState('');
  const [isScrolled, setIsScrolled] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [scrollY, setScrollY] = useState(0);
  
  // Estados para loading de CTAs
  const [isLoadingEmpezar, setIsLoadingEmpezar] = useState(false);
  const [isLoadingDemo, setIsLoadingDemo] = useState(false);
  
  // Refs para ripple effect
  const empezarButtonRef = useRef<HTMLButtonElement>(null);
  const demoButtonRef = useRef<HTMLButtonElement>(null);
  
  // Typewriter effect state
  const [currentText, setCurrentText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);
  
  const typewriterTexts = [
    'Almacenamos tus productos de forma segura',
    'Gestionamos tu inventario automáticamente',
    'Enviamos a tus clientes en tiempo récord',
    'Hacemos crecer tu negocio sin complicaciones'
  ];

  // Efecto parallax y scroll detection
  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      setIsScrolled(currentScrollY > 50);
      setScrollY(currentScrollY);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Typewriter effect implementation
  useEffect(() => {
    const timeout = setTimeout(() => {
      const current = typewriterTexts[currentIndex];
      
      if (!isDeleting && currentText !== current) {
        setCurrentText(current.substring(0, currentText.length + 1));
      } else if (isDeleting && currentText !== '') {
        setCurrentText(current.substring(0, currentText.length - 1));
      } else if (!isDeleting && currentText === current) {
        setTimeout(() => setIsDeleting(true), 2000);
      } else if (isDeleting && currentText === '') {
        setIsDeleting(false);
        setCurrentIndex((currentIndex + 1) % typewriterTexts.length);
      }
    }, isDeleting ? 50 : 100);

    return () => clearTimeout(timeout);
  }, [currentText, currentIndex, isDeleting, typewriterTexts]);

  // Función para crear efecto ripple
  const createRipple = (event: React.MouseEvent<HTMLButtonElement>) => {
    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    const ripple = document.createElement('span');
    ripple.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      left: ${x}px;
      top: ${y}px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.6);
      pointer-events: none;
      transform: scale(0);
      animation: ripple-animation 600ms ease-out;
      z-index: 1;
    `;
    
    button.appendChild(ripple);
    
    setTimeout(() => {
      ripple.remove();
    }, 600);
  };

  const handleEmailSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) {
      navigate('/register', { state: { email } });
    }
  };

  // FUNCIÓN INTELIGENTE: Empezar en 5 Min con loading state
  const handleEmpezarWithRipple = async (e: React.MouseEvent<HTMLButtonElement>) => {
    createRipple(e);
    setIsLoadingEmpezar(true);
    
    // Simular delay de redirección para mostrar loading
    setTimeout(() => {
      if (!isAuthenticated) {
        navigate('/register');
      } else {
        // Redirigir según rol usando lógica existente
        if (user?.user_type === 'ADMIN' || user?.user_type === 'SUPERUSER') {
          navigate('/admin');
        } else if (user?.user_type === 'VENDEDOR') {
          navigate('/vendor');
        } else {
          navigate('/dashboard');
        }
      }
      setIsLoadingEmpezar(false);
    }, 800);
  };

  // FUNCIÓN INTELIGENTE: Ver Demo Live con loading state
  const handleDemoWithAnimation = async (e: React.MouseEvent<HTMLButtonElement>) => {
    setIsLoadingDemo(true);
    
    // Simular delay de redirección para mostrar loading
    setTimeout(() => {
      if (!isAuthenticated) {
        navigate('/login');
      } else {
        // Redirigir según rol usando lógica existente
        if (user?.user_type === 'ADMIN' || user?.user_type === 'SUPERUSER') {
          navigate('/admin');
        } else if (user?.user_type === 'VENDEDOR') {
          navigate('/vendor');
        } else {
          navigate('/dashboard');
        }
      }
      setIsLoadingDemo(false);
    }, 800);
  };

  return (
    <div className='min-h-screen bg-white dark:bg-gray-900'>
      {/* Estilos para animaciones incluyendo efectos premium CTAs */}
      <style jsx>{`
        @keyframes float-slow {
          0%, 100% { 
            transform: translate3d(0, 0, 0) scale(1); 
            opacity: 0.3; 
          }
          50% { 
            transform: translate3d(10px, -20px, 0) scale(1.2); 
            opacity: 0.7; 
          }
        }
        
        @keyframes float-medium {
          0%, 100% { 
            transform: translate3d(0, 0, 0) scale(1); 
            opacity: 0.4; 
          }
          33% { 
            transform: translate3d(-15px, -10px, 0) scale(1.3); 
            opacity: 0.8; 
          }
          66% { 
            transform: translate3d(15px, -25px, 0) scale(0.9); 
            opacity: 0.5; 
          }
        }
        
        @keyframes float-fast {
          0%, 100% { 
            transform: translate3d(0, 0, 0) scale(1); 
            opacity: 0.2; 
          }
          25% { 
            transform: translate3d(20px, -15px, 0) scale(1.1); 
            opacity: 0.6; 
          }
          75% { 
            transform: translate3d(-10px, -30px, 0) scale(1.4); 
            opacity: 0.4; 
          }
        }

        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }

        /* EFECTOS PREMIUM PARA CTAs */
        @keyframes glow-pulse {
          0%, 100% { 
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.5), 0 0 40px rgba(147, 51, 234, 0.3), 0 0 60px rgba(59, 130, 246, 0.1);
          }
          50% { 
            box-shadow: 0 0 30px rgba(59, 130, 246, 0.8), 0 0 60px rgba(147, 51, 234, 0.6), 0 0 90px rgba(59, 130, 246, 0.3);
          }
        }

        @keyframes border-rotate {
          0% { 
            background-position: 0% 50%; 
          }
          50% { 
            background-position: 100% 50%; 
          }
          100% { 
            background-position: 0% 50%; 
          }
        }

        @keyframes ripple-animation {
          to {
            transform: scale(4);
            opacity: 0;
          }
        }

        @keyframes loading-spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .animate-float-slow { 
          animation: float-slow 8s ease-in-out infinite;
          will-change: transform, opacity;
        }
        .animate-float-medium { 
          animation: float-medium 6s ease-in-out infinite;
          will-change: transform, opacity;
        }
        .animate-float-fast { 
          animation: float-fast 4s ease-in-out infinite;
          will-change: transform, opacity;
        }
        
        .typewriter-cursor {
          animation: blink 1s infinite;
        }
        
        .parallax-bg {
          will-change: transform;
        }

        /* CLASES PREMIUM PARA CTAs */
        .btn-glow-pulse {
          animation: glow-pulse 2s ease-in-out infinite;
          will-change: transform, box-shadow;
        }

        .btn-border-animate {
          background: linear-gradient(-45deg, transparent, transparent, rgba(59, 130, 246, 0.3), transparent, transparent);
          background-size: 400% 400%;
          animation: border-rotate 3s ease infinite;
          position: relative;
          will-change: background-position;
        }

        .btn-border-animate::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          border-radius: inherit;
          padding: 2px;
          background: linear-gradient(-45deg, #3b82f6, #8b5cf6, #3b82f6, #8b5cf6);
          background-size: 400% 400%;
          animation: border-rotate 3s ease infinite;
          mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
          mask-composite: exclude;
          z-index: -1;
        }

        .loading-spinner {
          display: inline-block;
          width: 16px;
          height: 16px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-radius: 50%;
          border-top-color: white;
          animation: loading-spin 0.8s ease-in-out infinite;
        }
      `}</style>

      {/* Fixed Navigation */}
      <nav className={`fixed w-full z-50 transition-all duration-300 ${
        isScrolled 
          ? 'bg-white/95 dark:bg-gray-900/95 backdrop-blur-lg shadow-lg' 
          : 'bg-transparent'
      }`}>
        <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
          <div className='flex justify-between items-center h-20'>
            <div className='flex items-center'>
              <div className='flex items-center space-x-2'>
                <div className='w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center'>
                  <span className='text-white font-bold text-lg'>M</span>
                </div>
                <h1 className='text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent'>
                  MeStocker
                </h1>
              </div>
            </div>
            <div className='hidden md:flex items-center space-x-6'>
              <a href='#solutions' className='text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors'>
                Soluciones
              </a>
              <a href='#resources' className='text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors'>
                Recursos
              </a>
              <a href='#pricing' className='text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors'>
                Precios
              </a>
              <a href='#contact' className='text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors'>
                Contacto
              </a>
            </div>
            <div className='flex items-center space-x-4'>
              {isAuthenticated ? (
                <div className="relative">
                  <button
                    onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                    className="flex items-center space-x-2 text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                  >
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                      {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
                    </div>
                    <span className="text-sm font-medium">{user?.name || 'Usuario'}</span>
                    <svg className={`w-4 h-4 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  
                  {isDropdownOpen && (
                    <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
                      <div className="py-1">
                        <button
                          onClick={() => {
                            if (user?.user_type === 'ADMIN' || user?.user_type === 'SUPERUSER') {
                              navigate('/admin');
                            } else if (user?.user_type === 'VENDEDOR') {
                              navigate('/vendor');
                            } else {
                              navigate('/dashboard');
                            }
                            setIsDropdownOpen(false);
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                        >
                          Dashboard
                        </button>
                        <button
                          onClick={() => {
                            logout();
                            setIsDropdownOpen(false);
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                        >
                          Cerrar Sesión
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <>
                  <button
                    onClick={() => navigate('/login')}
                    className='text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-4 py-2 text-sm font-medium transition-all duration-300 border border-transparent hover:border-blue-200 dark:hover:border-blue-800 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:shadow-sm transform hover:scale-[1.02] rounded-lg'
                  >
                    Iniciar Sesión
                  </button>
                  <button
                    onClick={() => navigate('/register')}
                    className='bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-all duration-300 transform hover:scale-105 shadow-lg'
                  >
                    Registrarse
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section con Background Dinámico Avanzado */}
      <section className='pt-32 pb-20 px-4 sm:px-6 lg:px-8 relative overflow-hidden'>
        {/* Background dinámico con múltiples layers y efecto parallax */}
        <div 
          className='absolute inset-0 bg-gradient-to-br from-blue-600/10 via-violet-500/5 to-purple-600/15 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800 parallax-bg'
          style={{
            transform: `translate3d(0, ${scrollY * 0.1}px, 0)`
          }}
        ></div>
        <div 
          className='absolute inset-0 bg-gradient-to-tr from-transparent via-blue-400/5 to-violet-600/10 parallax-bg'
          style={{
            transform: `translate3d(0, ${scrollY * 0.15}px, 0)`
          }}
        ></div>
        <div 
          className='absolute inset-0 bg-gradient-to-bl from-purple-500/5 via-transparent to-blue-500/8 parallax-bg'
          style={{
            transform: `translate3d(0, ${scrollY * 0.05}px, 0)`
          }}
        ></div>
        
        {/* Partículas flotantes decorativas optimizadas */}
        <div className='absolute inset-0 overflow-hidden pointer-events-none'>
          <div className='absolute top-20 left-10 w-2 h-2 bg-blue-400/30 rounded-full animate-float-slow'></div>
          <div className='absolute top-40 right-20 w-1 h-1 bg-violet-500/40 rounded-full animate-float-medium'></div>
          <div className='absolute top-60 left-1/4 w-3 h-3 bg-purple-400/20 rounded-full animate-float-fast'></div>
          <div className='absolute bottom-40 right-10 w-2 h-2 bg-blue-500/25 rounded-full animate-float-slow'></div>
          <div className='absolute bottom-20 left-20 w-1 h-1 bg-violet-400/35 rounded-full animate-float-medium'></div>
          <div className='absolute top-32 right-1/3 w-1.5 h-1.5 bg-blue-300/25 rounded-full animate-float-fast'></div>
          <div className='absolute top-80 left-1/3 w-2 h-2 bg-purple-300/20 rounded-full animate-float-medium'></div>
          <div className='absolute bottom-60 left-1/2 w-1 h-1 bg-violet-300/30 rounded-full animate-float-slow'></div>
        </div>
        
        <div className='relative max-w-7xl mx-auto text-center'>
          <div className='inline-flex items-center px-4 py-2 bg-blue-100 dark:bg-blue-900 rounded-full text-blue-700 dark:text-blue-300 text-sm font-medium mb-8'>
            📦 Solución completa de <span className='bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent font-extrabold'>fulfillment</span>
          </div>
          <h1 className='text-6xl sm:text-7xl lg:text-8xl font-black tracking-tight mb-8 leading-tight'>
            <span className='bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent'>
              Tu Almacén Virtual
            </span>
            <br />
            <span className='text-gray-900 dark:text-white'>
              en Bucaramanga
            </span>
          </h1>
          <div className='text-xl sm:text-2xl text-gray-600 dark:text-gray-300 max-w-4xl mx-auto mb-12 leading-relaxed min-h-[4rem] flex items-center justify-center'>
            <span>
              {currentText}
              <span className='typewriter-cursor text-blue-600'>|</span>
            </span>
          </div>
          <div className='text-lg text-gray-500 dark:text-gray-400 max-w-3xl mx-auto mb-12'>
            Tú te enfocas en hacer crecer tu negocio con nuestro 
            <span className='bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent font-extrabold ml-1 mr-1'>
              Marketplace
            </span> 
            especializado.
          </div>

          {/* Email Signup Form */}
          <form onSubmit={handleEmailSubmit} className='max-w-md mx-auto mb-8'>
            <div className='flex gap-2'>
              <input
                type='email'
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder='tu@email.com'
                className='flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white'
                required
              />
              <button
                type='submit'
                className='bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg'
              >
                Comenzar
              </button>
            </div>
          </form>
          
          {/* CTAs PREMIUM CON EFECTOS VISUALES AVANZADOS */}
          <div className='flex flex-col sm:flex-row gap-4 justify-center items-center mb-12'>
            <button 
              ref={empezarButtonRef}
              onClick={handleEmpezarWithRipple}
              disabled={isLoadingEmpezar}
              className='relative overflow-hidden bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-xl btn-glow-pulse disabled:opacity-80 disabled:cursor-not-allowed'
              style={{ willChange: 'transform, box-shadow' }}
            >
              {isLoadingEmpezar ? (
                <span className="flex items-center gap-2">
                  <div className="loading-spinner"></div>
                  Redirigiendo...
                </span>
              ) : (
                'Empezar en 5 Min'
              )}
            </button>
            <button 
              ref={demoButtonRef}
              onClick={handleDemoWithAnimation}
              disabled={isLoadingDemo}
              className='relative border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-blue-500 hover:text-blue-600 px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-300 btn-border-animate disabled:opacity-80 disabled:cursor-not-allowed'
              style={{ willChange: 'background-position' }}
            >
              {isLoadingDemo ? (
                <span className="flex items-center gap-2">
                  <div className="loading-spinner" style={{ borderTopColor: 'currentColor' }}></div>
                  Redirigiendo...
                </span>
              ) : (
                'Ver Demo Live'
              )}
            </button>
          </div>
          
          <div className='text-sm text-gray-500 dark:text-gray-400'>
            ✅ Setup rápido • ✅ Sin costos ocultos • ✅ Soporte personalizado
          </div>
        </div>
      </section>

      {/* Statistics Section */}
      <section className='py-20 bg-gray-50 dark:bg-gray-800'>
        <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
          <div className='grid grid-cols-2 md:grid-cols-4 gap-8 text-center'>
            <div className='group'>
              <div className='text-4xl md:text-5xl font-bold text-blue-600 mb-2 group-hover:scale-110 transition-transform'>
                50+
              </div>
              <div className='text-gray-600 dark:text-gray-300 font-medium'>Vendedores Registrados</div>
            </div>
            <div className='group'>
              <div className='text-4xl md:text-5xl font-bold text-purple-600 mb-2 group-hover:scale-110 transition-transform'>
                1K+
              </div>
              <div className='text-gray-600 dark:text-gray-300 font-medium'>Productos Listados</div>
            </div>
            <div className='group'>
              <div className='text-4xl md:text-5xl font-bold text-green-600 mb-2 group-hover:scale-110 transition-transform'>
                95%
              </div>
              <div className='text-gray-600 dark:text-gray-300 font-medium'>Entregas a Tiempo</div>
            </div>
            <div className='group'>
              <div className='text-4xl md:text-5xl font-bold text-orange-600 mb-2 group-hover:scale-110 transition-transform'>
                24/7
              </div>
              <div className='text-gray-600 dark:text-gray-300 font-medium'>Soporte</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id='features' className='py-20'>
        <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
          <div className='text-center mb-16'>
            <h2 className='text-5xl font-bold mb-6 text-gray-900 dark:text-white'>
              Nuestros Servicios
            </h2>
            <p className='text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto'>
              Solución integral de fulfillment para vendedores online
            </p>
          </div>
          
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8'>
            <div className='group p-8 rounded-2xl bg-white dark:bg-gray-800 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 dark:border-gray-700'>
              <div className='w-16 h-16 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform'>
                <span className='text-2xl'>🏭</span>
              </div>
              <h3 className='text-2xl font-bold mb-4 text-gray-900 dark:text-white'>Almacenamiento Seguro</h3>
              <p className='text-gray-600 dark:text-gray-300 leading-relaxed'>
                Instalaciones modernas con seguridad 24/7 y control de clima para tus productos
              </p>
            </div>
            
            <div className='group p-8 rounded-2xl bg-white dark:bg-gray-800 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 dark:border-gray-700'>
              <div className='w-16 h-16 bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform'>
                <span className='text-2xl'>📊</span>
              </div>
              <h3 className='text-2xl font-bold mb-4 text-gray-900 dark:text-white'>Gestión de Inventario</h3>
              <p className='text-gray-600 dark:text-gray-300 leading-relaxed'>
                Sistema avanzado de control de stock con reportes en tiempo real
              </p>
            </div>
            
            <div className='group p-8 rounded-2xl bg-white dark:bg-gray-800 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 dark:border-gray-700'>
              <div className='w-16 h-16 bg-gradient-to-r from-green-500 to-green-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform'>
                <span className='text-2xl'>🚚</span>
              </div>
              <h3 className='text-2xl font-bold mb-4 text-gray-900 dark:text-white'>Envíos Rápidos</h3>
              <p className='text-gray-600 dark:text-gray-300 leading-relaxed'>
                Red de distribución eficiente con seguimiento completo de envíos
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id='process' className='py-20 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-900'>
        <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
          <h2 className='text-5xl font-bold text-center mb-16 text-gray-900 dark:text-white'>
            Proceso Simple
          </h2>
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8'>
            {[
              { step: '01', title: 'Registra', desc: 'Crea tu cuenta y configura tu tienda', icon: '📝', color: 'blue' },
              { step: '02', title: 'Envía', desc: 'Envía tus productos a nuestro almacén', icon: '📦', color: 'green' },
              { step: '03', title: 'Vendemos', desc: 'Listamos y promocionamos en el marketplace', icon: '🛍️', color: 'purple' },
              { step: '04', title: 'Entregamos', desc: 'Procesamos y enviamos a tus clientes', icon: '🚀', color: 'orange' }
            ].map((item, index) => (
              <div key={index} className='text-center group'>
                <div className={`w-20 h-20 bg-gradient-to-r from-${item.color}-500 to-${item.color}-600 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-all duration-300 shadow-lg`}>
                  <span className='text-3xl'>{item.icon}</span>
                </div>
                <div className='text-sm font-bold text-gray-400 mb-2'>{item.step}</div>
                <h3 className='text-2xl font-bold mb-3 text-gray-900 dark:text-white'>{item.title}</h3>
                <p className='text-gray-600 dark:text-gray-300 leading-relaxed'>{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className='py-20 bg-gradient-to-r from-blue-600 to-purple-600'>
        <div className='max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8'>
          <h2 className='text-5xl font-bold mb-6 text-white'>
            ¿Listo para Crecer?
          </h2>
          <p className='text-xl text-blue-100 mb-8 leading-relaxed'>
            Únete a MeStocker y lleva tu negocio al siguiente nivel
          </p>
          <div className='flex flex-col sm:flex-row gap-4 justify-center items-center'>
            <button 
              onClick={() => navigate('/register')}
              className='bg-white text-blue-600 hover:bg-gray-100 px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-xl'
            >
              Registrarme Ahora
            </button>
            <button 
              onClick={() => navigate('/app')}
              className='border-2 border-white text-white hover:bg-white hover:text-blue-600 px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-300'
            >
              Ver Plataforma
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer id='contact' className='bg-gray-900 dark:bg-black text-white py-16'>
        <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
          <div className='grid grid-cols-1 md:grid-cols-4 gap-8 mb-8'>
            <div>
              <div className='flex items-center space-x-2 mb-4'>
                <div className='w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center'>
                  <span className='text-white font-bold'>M</span>
                </div>
                <h3 className='text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent'>
                  MeStocker
                </h3>
              </div>
              <p className='text-gray-400 mb-4'>
                Tu socio en fulfillment y logística
              </p>
            </div>
            
            <div>
              <h4 className='font-semibold mb-4'>Servicios</h4>
              <ul className='space-y-2 text-gray-400'>
                <li><a href='#' className='hover:text-white transition-colors'>Almacenamiento</a></li>
                <li><a href='#' className='hover:text-white transition-colors'>Gestión de Inventario</a></li>
                <li><a href='#' className='hover:text-white transition-colors'>Envíos</a></li>
                <li><a href='#' className='hover:text-white transition-colors'>Marketplace</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className='font-semibold mb-4'>Empresa</h4>
              <ul className='space-y-2 text-gray-400'>
                <li><a href='#' className='hover:text-white transition-colors'>Sobre Nosotros</a></li>
                <li><a href='#' className='hover:text-white transition-colors'>Blog</a></li>
                <li><a href='#' className='hover:text-white transition-colors'>Careers</a></li>
                <li><a href='#' className='hover:text-white transition-colors'>Prensa</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className='font-semibold mb-4'>Soporte</h4>
              <ul className='space-y-2 text-gray-400'>
                <li><a href='#' className='hover:text-white transition-colors'>Centro de Ayuda</a></li>
                <li><a href='#' className='hover:text-white transition-colors'>Contacto</a></li>
                <li>
                  <button 
                    onClick={() => navigate('/register')}
                    className='bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:from-blue-700 hover:to-purple-700 transition-all mt-2'
                  >
                    Registrarse
                  </button>
                </li>
              </ul>
            </div>
          </div>
          
          <div className='border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center'>
            <p className='text-gray-400 mb-4 md:mb-0'>
              © 2024 MeStocker. Todos los derechos reservados.
            </p>
            <div className='flex space-x-6 text-gray-400'>
              <a href='#' className='hover:text-white transition-colors'>Términos</a>
              <a href='#' className='hover:text-white transition-colors'>Privacidad</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;