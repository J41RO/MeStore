import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthContext } from '../../contexts/AuthContext';
import { X, Play, Pause, Volume2 } from 'lucide-react';

interface ProcessSectionProps {
  className?: string;
}

interface StepData {
  number: string;
  title: string;
  desc: string;
  icon: string;
  color: string;
  hoverDetails: {
    subtitle: string;
    benefits: string[];
    metrics: string;
    advantage: string;
  };
  screenshot: string;
  videoUrl: string;
}

const ProcessSection: React.FC<ProcessSectionProps> = ({ className = '' }) => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthContext();
  const [activeStep, setActiveStep] = useState(0);
  const [hoveredStep, setHoveredStep] = useState<number | null>(null);
  const [expandedModal, setExpandedModal] = useState<number | null>(null);
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);

  // Auto-advance steps every 3 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % 4);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const steps: StepData[] = [
    {
      number: '01',
      title: 'Registra',
      desc: 'Setup en 5 min vs 15+ competencia',
      icon: '📝',
      color: 'blue',
      hoverDetails: {
        subtitle: 'Proceso Ultra-Rápido',
        benefits: ['Solo 3 campos requeridos', 'Validación automática', 'Sin papeleo físico'],
        metrics: 'MELONN: 15 min | CUBBO: 10 min | MeStocker: 5 min',
        advantage: 'Verificación IA instantánea'
      },
      screenshot: '/screenshots/proceso-registro.jpg',
      videoUrl: '/videos/proceso-registro-15s.mp4'
    },
    {
      number: '02',
      title: 'Envía',
      desc: 'A nuestro almacén Bucaramanga único',
      icon: '📦',
      color: 'green',
      hoverDetails: {
        subtitle: 'Centro Estratégico Único',
        benefits: ['Ubicación central Colombia', 'Recolección gratuita', 'Tracking 24/7'],
        metrics: 'Competencia: Solo Bogotá/Medellín | MeStocker: Bucaramanga',
        advantage: 'Cobertura nacional desde punto central'
      },
      screenshot: '/screenshots/proceso-envio.jpg',
      videoUrl: '/videos/proceso-envio-15s.mp4'
    },
    {
      number: '03',
      title: 'Vendemos',
      desc: 'Marketplace B2B+B2C integrado',
      icon: '🛍️',
      color: 'purple',
      hoverDetails: {
        subtitle: 'Doble Canal Único',
        benefits: ['Marketplace público', 'Red B2B corporativa', 'IA optimiza ventas'],
        metrics: 'Competencia: Solo B2B | MeStocker: B2B + B2C',
        advantage: 'Doble oportunidad de venta automática'
      },
      screenshot: '/screenshots/proceso-ventas.jpg',
      videoUrl: '/videos/proceso-ventas-15s.mp4'
    },
    {
      number: '04',
      title: 'Entregamos',
      desc: '95% éxito vs 80% competencia',
      icon: '🚀',
      color: 'orange',
      hoverDetails: {
        subtitle: 'Logística Superior',
        benefits: ['Red de couriers premium', 'Seguimiento tiempo real', 'Garantía entrega'],
        metrics: 'Competencia: 80% éxito | MeStocker: 95% éxito',
        advantage: 'Red exclusiva couriers verificados'
      },
      screenshot: '/screenshots/proceso-entrega.jpg',
      videoUrl: '/videos/proceso-entrega-15s.mp4'
    }
  ];

  const getStepClasses = (index: number) => {
    const baseClasses = "text-center p-6 rounded-xl transition-all duration-300 cursor-pointer relative";
    const activeClasses = "bg-white shadow-xl scale-105";
    const inactiveClasses = "bg-white/50 hover:bg-white/90 hover:shadow-lg transform hover:-translate-y-1";
    
    return `${baseClasses} ${index === activeStep ? activeClasses : inactiveClasses}`;
  };

  const getIconClasses = (color: string) => {
    const colorMap: { [key: string]: string } = {
      blue: 'from-blue-500 to-blue-600',
      green: 'from-green-500 to-green-600',
      purple: 'from-purple-500 to-purple-600',
      orange: 'from-orange-500 to-orange-600'
    };
    
    return `w-16 h-16 bg-gradient-to-r ${colorMap[color]} rounded-full flex items-center justify-center mx-auto mb-4 text-2xl`;
  };

  const handleVideoToggle = () => {
    setIsVideoPlaying(!isVideoPlaying);
  };

  const closeModal = () => {
    setExpandedModal(null);
    setIsVideoPlaying(false);
  };

  // Get current step data safely
  const currentModalStep = expandedModal !== null ? steps[expandedModal] : null;

  return (
    <section className={`py-20 bg-gradient-to-br from-gray-50 to-purple-50/30 ${className}`}>
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
              className={getStepClasses(index)}
              onClick={() => {
                setActiveStep(index);
                setExpandedModal(index);
              }}
              onMouseEnter={() => setHoveredStep(index)}
              onMouseLeave={() => setHoveredStep(null)}
            >
              <div className={getIconClasses(step.color)}>
                {step.icon}
              </div>
              <h3 className="text-xl font-bold mb-2 text-gray-900">
                {step.title}
              </h3>
              <p className="text-gray-600 mb-4">
                {step.desc}
              </p>

              {/* Hover Reveal Details - FUNCIONALIDAD 1 */}
              {hoveredStep === index && (
                <div className="absolute inset-0 bg-white/95 backdrop-blur-sm rounded-xl p-4 z-10 border-2 border-blue-200 animate-in slide-in-from-bottom-2 duration-200">
                  <div className="text-sm space-y-2">
                    <h4 className="font-bold text-blue-600">{step.hoverDetails.subtitle}</h4>
                    <div className="space-y-1">
                      {step.hoverDetails.benefits.map((benefit, idx) => (
                        <div key={idx} className="flex items-center text-xs text-gray-700">
                          <span className="w-1 h-1 bg-green-500 rounded-full mr-2"></span>
                          {benefit}
                        </div>
                      ))}
                    </div>
                    <div className="text-xs text-purple-600 font-medium">
                      {step.hoverDetails.advantage}
                    </div>
                    <div className="text-xs text-gray-500 border-t pt-2">
                      {step.hoverDetails.metrics}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Modal de Expansión con Screenshots y Video - FUNCIONALIDADES 2 y 3 */}
        {expandedModal !== null && currentModalStep && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-2xl font-bold text-gray-900">
                    {currentModalStep.title} - Proceso Detallado
                  </h3>
                  <button
                    onClick={closeModal}
                    className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Screenshot del Proceso */}
                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold text-gray-800">Vista del Proceso</h4>
                    <div className="relative">
                      <img
                        src={currentModalStep.screenshot}
                        alt={`Proceso ${currentModalStep.title}`}
                        className="w-full h-64 object-cover rounded-lg border-2 border-gray-200"
                        onError={(e) => {
                          e.currentTarget.src = `data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200" viewBox="0 0 400 200"><rect width="400" height="200" fill="%23f3f4f6"/><text x="200" y="100" text-anchor="middle" dy=".3em" fill="%236b7280" font-family="sans-serif" font-size="14">Screenshot: ${currentModalStep.title}</text></svg>`;
                        }}
                      />
                    </div>
                    <div className="space-y-2">
                      <p className="text-gray-600">{currentModalStep.desc}</p>
                      <div className="bg-blue-50 p-3 rounded-lg">
                        <p className="text-sm font-medium text-blue-800">
                          {currentModalStep.hoverDetails.advantage}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Video del Proceso (15s) */}
                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold text-gray-800">Video Proceso (15s)</h4>
                    <div className="relative bg-gray-900 rounded-lg overflow-hidden">
                      <video
                        className="w-full h-64 object-cover"
                        controls={isVideoPlaying}
                        poster={`data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="240" viewBox="0 0 400 240"><rect width="400" height="240" fill="%23111827"/><circle cx="200" cy="120" r="30" fill="%23374151"/><polygon points="190,105 190,135 215,120" fill="%23ffffff"/></svg>`}
                      >
                        <source src={currentModalStep.videoUrl} type="video/mp4" />
                        Su navegador no soporta video HTML5.
                      </video>
                      
                      {!isVideoPlaying && (
                        <div className="absolute inset-0 flex items-center justify-center">
                          <button
                            onClick={handleVideoToggle}
                            className="bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-full p-4 transition-all duration-300 group"
                          >
                            <Play className="w-8 h-8 text-white group-hover:scale-110 transition-transform" />
                          </button>
                        </div>
                      )}
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={handleVideoToggle}
                          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
                        >
                          {isVideoPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                          {isVideoPlaying ? 'Pausar' : 'Reproducir'}
                        </button>
                        <Volume2 className="w-5 h-5 text-gray-400" />
                      </div>
                      
                      <div className="bg-purple-50 p-3 rounded-lg">
                        <h5 className="font-medium text-purple-800 mb-2">Beneficios Únicos:</h5>
                        <ul className="space-y-1">
                          {currentModalStep.hoverDetails.benefits.map((benefit, idx) => (
                            <li key={idx} className="text-sm text-purple-700 flex items-center">
                              <span className="w-1.5 h-1.5 bg-purple-500 rounded-full mr-2"></span>
                              {benefit}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-6 border-t border-gray-200">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h5 className="font-medium text-gray-800 mb-2">Comparación Competencia:</h5>
                    <p className="text-sm text-gray-600">{currentModalStep.hoverDetails.metrics}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="text-center mt-12">
          <button
            onClick={() => isAuthenticated ? navigate('/dashboard') : navigate('/register')}
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-300"
          >
            {isAuthenticated ? 'Ir a Dashboard' : 'Empezar Ahora'}
          </button>
        </div>
      </div>
    </section>
  );
};

export default ProcessSection;