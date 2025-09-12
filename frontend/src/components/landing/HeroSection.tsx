import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthContext } from '../../contexts/AuthContext';
import EarlyAccessForm from '../forms/EarlyAccessForm';
import { trackButtonClick, trackPageView, trackEvent } from '../../services/analytics';

interface HeroSectionProps {
  className?: string;
}

const HeroSection: React.FC<HeroSectionProps> = ({ className = '' }) => {
  const { isAuthenticated, user } = useAuthContext();
  const navigate = useNavigate();
  const [currentText, setCurrentText] = useState('');
  const [textIndex, setTextIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);

  const typewriterTexts = [
    'Fulfillment Inteligente en Bucaramanga',
    'Marketplace Público Integrado',
    'IA Real para tu Negocio',
    'Setup en Solo 5 Minutos',
    'Reduce Costos Operativos hasta 40%',
    'Automatiza tu Inventario 24/7',
    'Conecta con 500+ Compradores Locales',
    'ROI Positivo desde el Primer Mes',
    'Gestión Inteligente de Stock',
    'Expansión de Ventas Garantizada',
    'Optimización Espacial Automática',
    'Análisis Predictivo de Demanda'
  ];

  // Track page view on component mount
  useEffect(() => {
    trackPageView('/landing', 'MeStocker - Landing Page');
    
    // Track scroll depth
    const handleScroll = () => {
      const scrollPercentage = Math.round(
        ((window.scrollY + window.innerHeight) / document.body.scrollHeight) * 100
      );
      
      if (scrollPercentage >= 25 && scrollPercentage < 30) {
        trackEvent('scroll_depth', { depth: 25, page: 'landing' });
      } else if (scrollPercentage >= 50 && scrollPercentage < 55) {
        trackEvent('scroll_depth', { depth: 50, page: 'landing' });
      } else if (scrollPercentage >= 75 && scrollPercentage < 80) {
        trackEvent('scroll_depth', { depth: 75, page: 'landing' });
      } else if (scrollPercentage >= 95) {
        trackEvent('scroll_depth', { depth: 100, page: 'landing' });
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Typewriter effect with proper bounds checking
  useEffect(() => {
    const timeout = setTimeout(() => {
      const currentTypewriterText = typewriterTexts[textIndex];

      if (textIndex < typewriterTexts.length &&
          currentTypewriterText &&
          charIndex < currentTypewriterText.length) {
        setCurrentText(prev => prev + currentTypewriterText[charIndex]);
        setCharIndex(prev => prev + 1);
      } else {
        setTimeout(() => {
          setCurrentText('');
          setCharIndex(0);
          setTextIndex(prev => (prev + 1) % typewriterTexts.length);
        }, 2000);
      }
    }, 100);

    return () => clearTimeout(timeout);
  }, [charIndex, textIndex]);

  const handlePrimaryCTA = () => {
    const destination = isAuthenticated 
      ? (user?.user_type === 'ADMIN' ? '/admin' : 
         user?.user_type === 'VENDEDOR' ? '/dashboard/vendedor' : '/dashboard')
      : '/register';
    
    // Track CTA button click
    trackButtonClick(
      isAuthenticated ? 'ir_dashboard' : 'empezar_5_min', 
      'hero_section', 
      {
        user_authenticated: isAuthenticated,
        user_type: user?.user_type || 'anonymous',
        destination: destination
      }
    );

    if (isAuthenticated) {
      if (user?.user_type === 'ADMIN') {
        navigate('/admin');
      } else if (user?.user_type === 'VENDEDOR') {
        navigate('/dashboard/vendedor');
      } else {
        navigate('/dashboard');
      }
    } else {
      navigate('/register');
    }
  };

  return (
    <section className={`pt-32 pb-20 px-4 sm:px-6 lg:px-8 relative overflow-hidden ${className}`}>
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-800">
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto text-center">
        <h1 className="text-5xl md:text-7xl font-extrabold mb-6">
          <span className="bg-gradient-to-r from-white via-blue-100 to-purple-100 bg-clip-text text-transparent">
            Tu Almacén Virtual
          </span>
          <br />
          <span className="bg-gradient-to-r from-yellow-300 via-orange-300 to-red-300 bg-clip-text text-transparent">
            en Bucaramanga
          </span>
        </h1>

        {/* Subtítulo explicativo */}
        <div className="mb-6">
          <p className="text-lg md:text-xl text-white/80 max-w-3xl mx-auto leading-relaxed">
            La plataforma de fulfillment más avanzada de Colombia. Conectamos vendedores y compradores
            con IA, automatización total y marketplace integrado.
          </p>
        </div>

        {/* Typewriter effect */}
        <div className="h-16 mb-8">
          <p className="text-xl md:text-2xl text-white/90 font-medium">
            {currentText}
            <span className="inline-block w-1 h-6 bg-white/90 ml-1 animate-pulse"></span>
          </p>
        </div>

        {/* Beneficios cuantificados */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 max-w-4xl mx-auto">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="text-3xl font-bold text-yellow-300 mb-2">40%</div>
            <div className="text-white/90 text-sm">Reducción en costos operativos promedio</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="text-3xl font-bold text-green-300 mb-2">24/7</div>
            <div className="text-white/90 text-sm">Automatización completa de inventario</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="text-3xl font-bold text-blue-300 mb-2">500+</div>
            <div className="text-white/90 text-sm">Compradores activos en la red</div>
          </div>
        </div>

        {/* BOTÓN CTA CENTRADO PERFECTO */}
        <div className="flex justify-center items-center mb-8">
          <button
            onClick={handlePrimaryCTA}
            className="mx-auto block text-center px-8 py-4 bg-gradient-to-r from-yellow-400 to-orange-500 text-black font-bold text-lg rounded-xl hover:from-yellow-300 hover:to-orange-400 transform hover:scale-105 transition-all duration-300 shadow-2xl"
          >
            {isAuthenticated ? 'Ir a Dashboard' : 'Empezar en 5 Min'}
          </button>
        </div>

        {/* BENEFICIOS CENTRADOS */}
        <div className="flex items-center justify-center space-x-4 text-white/80 mb-12">
          <div className="flex items-center">
            <span className="text-green-400 mr-2">✓</span>
            <span className="text-sm">Setup gratuito</span>
          </div>
          <div className="flex items-center">
            <span className="text-green-400 mr-2">✓</span>
            <span className="text-sm">Sin compromisos</span>
          </div>
          <div className="flex items-center">
            <span className="text-green-400 mr-2">✓</span>
            <span className="text-sm">Soporte 24/7</span>
          </div>
        </div>

        {/* FORMULARIO CENTRADO PERFECTAMENTE */}
        <div className="flex justify-center items-center w-full">
          <div className="w-full max-w-md mx-auto">
            <EarlyAccessForm
              className="mx-auto"
              onSuccess={(data) => {
                console.log('Lead captured:', data);
                
                // Track successful lead capture
                trackEvent('lead_conversion', {
                  conversion_type: 'early_access',
                  lead_type: data.tipo_negocio,
                  source: 'hero_section',
                  value: 10, // Higher value for completed leads
                  currency: 'COP'
                });
              }}
            />
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;