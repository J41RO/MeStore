import React from 'react';

interface AdvantagesSectionProps {
  className?: string;
}

const AdvantagesSection: React.FC<AdvantagesSectionProps> = ({ className = '' }) => {
  const advantages = [
    { 
      title: 'IA Especializada Real', 
      desc: 'Agentes IA que optimizan precios y ventas', 
      icon: '🤖', 
      unique: 'vs promesas vacías competencia' 
    },
    { 
      title: 'Marketplace Público', 
      desc: 'B2B + B2C integrado en una plataforma', 
      icon: '🏪', 
      unique: 'vs solo B2B como MELONN' 
    },
    { 
      title: 'Fulfillment Bucaramanga', 
      desc: 'Único centro logístico en la región', 
      icon: '📍', 
      unique: 'vs solo Bogotá/Medellín' 
    },
    { 
      title: 'Canvas Interactivo', 
      desc: 'Visualiza tu almacén en tiempo real', 
      icon: '🎨', 
      unique: 'vs reportes estáticos' 
    }
  ];

  return (
    <section className={`py-20 bg-white ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-6">
            <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              Ventajas Exclusivas
            </span>
          </h2>
          <p className="text-xl text-gray-600">
            Funciones que ningún competidor puede copiar
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {advantages.map((advantage, index) => (
            <div 
              key={index} 
              className="text-center p-6 rounded-xl bg-gradient-to-br from-gray-50 to-purple-50 hover:shadow-xl transition-all duration-300 group"
            >
              <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">
                {advantage.icon}
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900">
                {advantage.title}
              </h3>
              <p className="text-gray-600 mb-3">
                {advantage.desc}
              </p>
              <div className="text-sm text-purple-600 font-medium">
                {advantage.unique}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default AdvantagesSection;