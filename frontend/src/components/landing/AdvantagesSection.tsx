import React from 'react';

interface AdvantagesSectionProps {
  className?: string;
}

const AdvantagesSection: React.FC<AdvantagesSectionProps> = ({ className = '' }) => {
  const advantages = [
    { 
      title: 'IA Especializada Real', 
      desc: 'Agentes IA que optimizan precios y ventas automáticamente', 
      icon: '🤖', 
      unique: 'vs promesas vacías competencia',
      roi: 'ROI: +35% en ventas promedio'
    },
    { 
      title: 'Marketplace Público', 
      desc: 'B2B + B2C integrado - Vendedores y Compradores unidos', 
      icon: '🏪', 
      unique: 'vs solo B2B como MELONN',
      roi: 'Acceso: 500+ compradores activos'
    },
    { 
      title: 'Fulfillment Bucaramanga', 
      desc: 'Único centro logístico especializado en la región', 
      icon: '📍', 
      unique: 'vs solo Bogotá/Medellín',
      roi: 'Ahorro: -60% en tiempos de entrega'
    },
    { 
      title: 'Canvas Interactivo', 
      desc: 'Visualiza tu almacén en tiempo real con mapas 3D', 
      icon: '🎨', 
      unique: 'vs reportes estáticos',
      roi: 'Eficiencia: +45% optimización espacial'
    },
    { 
      title: 'Setup en 5 Minutos', 
      desc: 'Onboarding automatizado sin complejidades técnicas', 
      icon: '⚡', 
      unique: 'vs semanas de implementación',
      roi: 'Tiempo: 95% reducción en setup'
    },
    { 
      title: 'Análisis Predictivo', 
      desc: 'Predicción de demanda con ML avanzado', 
      icon: '📊', 
      unique: 'vs análisis básicos manuales',
      roi: 'Precisión: 87% en predicciones'
    },
    { 
      title: 'Automatización 24/7', 
      desc: 'Gestión completa sin intervención humana', 
      icon: '🔄', 
      unique: 'vs procesos manuales',
      roi: 'Ahorro: -40% costos operativos'
    },
    { 
      title: 'Soporte Local', 
      desc: 'Equipo técnico especializado en Bucaramanga', 
      icon: '🤝', 
      unique: 'vs call centers genéricos',
      roi: 'Respuesta: <30min tiempo promedio'
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
              <div className="text-sm text-purple-600 font-medium mb-2">
                {advantage.unique}
              </div>
              <div className="text-xs bg-green-100 text-green-700 px-3 py-1 rounded-full font-semibold">
                {advantage.roi}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default AdvantagesSection;