import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthContext } from '../../contexts/AuthContext';

interface ProcessSectionProps {
  className?: string;
}

const ProcessSection: React.FC<ProcessSectionProps> = ({ className = '' }) => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthContext();
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % 4);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const steps = [
    { number: '01', title: 'Registra', desc: 'Setup en 5 min vs 15+ competencia', icon: '📝', color: 'blue' },
    { number: '02', title: 'Envía', desc: 'A nuestro almacén Bucaramanga único', icon: '📦', color: 'green' },
    { number: '03', title: 'Vendemos', desc: 'Marketplace B2B+B2C integrado', icon: '🛍️', color: 'purple' },
    { number: '04', title: 'Entregamos', desc: '95% éxito vs 80% competencia', icon: '🚀', color: 'orange' }
  ];

  return (
    <section className={}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Proceso Simple
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Más rápido que MELONN, CUBBO y ENVIA
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <div 
              key={index} 
              className={}
              onClick={() => setActiveStep(index)}
            >
              <div className={}>
                {step.icon}
              </div>
              <h3 className="text-xl font-bold mb-2">{step.title}</h3>
              <p className="text-gray-600">{step.desc}</p>
            </div>
          ))}
        </div>

        <div className="text-center mt-12">
          <button
            onClick={() => isAuthenticated ? navigate('/dashboard') : navigate('/register')}
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all"
          >
            {isAuthenticated ? 'Ir a Dashboard' : 'Empezar Ahora'}
          </button>
        </div>
      </div>
    </section>
  );
};

export default ProcessSection;