import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthContext } from '../../contexts/AuthContext';

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
    'Setup en Solo 5 Minutos'
  ];

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (charIndex < typewriterTexts[textIndex].length) {
        setCurrentText(prev => prev + typewriterTexts[textIndex][charIndex]);
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
    if (isAuthenticated) {
      if (user?.roles?.includes('admin')) {
        navigate('/admin');
      } else if (user?.roles?.includes('vendedor')) {
        navigate('/dashboard/vendedor');
      } else {
        navigate('/dashboard');
      }
    } else {
      navigate('/register');
    }
  };

  return (
    <section className={}>
      <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-800">
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent"></div>
      </div>

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

        <div className="h-16 mb-8">
          <p className="text-xl md:text-2xl text-white/90 font-medium">
            {currentText}
            <span className="inline-block w-1 h-6 bg-white/90 ml-1 animate-pulse"></span>
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16">
          <button
            onClick={handlePrimaryCTA}
            className="px-8 py-4 bg-gradient-to-r from-yellow-400 to-orange-500 text-black font-bold text-lg rounded-xl hover:from-yellow-300 hover:to-orange-400 transform hover:scale-105 transition-all duration-300 shadow-2xl"
          >
            {isAuthenticated ? 'Ir a Dashboard' : 'Empezar en 5 Min'}
          </button>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;