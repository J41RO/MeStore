import React from 'react';
import { ShoppingCart, Truck, CheckCircle } from 'lucide-react';

interface Step {
  number: 1 | 2 | 3;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  status: 'completed' | 'current' | 'pending';
}

interface CheckoutTimelineProps {
  currentStep?: 1 | 2 | 3;
}

const CheckoutTimeline: React.FC<CheckoutTimelineProps> = ({ currentStep = 2 }) => {
  const steps: Step[] = [
    {
      number: 1,
      label: 'Carrito',
      icon: ShoppingCart,
      status: currentStep > 1 ? 'completed' : currentStep === 1 ? 'current' : 'pending'
    },
    {
      number: 2,
      label: 'Datos de Envío',
      icon: Truck,
      status: currentStep > 2 ? 'completed' : currentStep === 2 ? 'current' : 'pending'
    },
    {
      number: 3,
      label: 'Confirmación',
      icon: CheckCircle,
      status: currentStep === 3 ? 'current' : 'pending'
    }
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const Icon = step.icon;
          const isCompleted = step.status === 'completed';
          const isCurrent = step.status === 'current';
          const isPending = step.status === 'pending';

          return (
            <React.Fragment key={step.number}>
              {/* Step Circle */}
              <div className="flex flex-col items-center flex-1">
                <div
                  className={`
                    w-12 h-12 rounded-full flex items-center justify-center mb-2 transition-all duration-300
                    ${isCompleted ? 'bg-green-500 text-white' : ''}
                    ${isCurrent ? 'bg-blue-600 text-white ring-4 ring-blue-100' : ''}
                    ${isPending ? 'bg-gray-200 text-gray-400' : ''}
                  `}
                >
                  {isCompleted ? (
                    <CheckCircle className="w-6 h-6" />
                  ) : (
                    <Icon className="w-6 h-6" />
                  )}
                </div>

                {/* Step Label */}
                <div className="text-center">
                  <p
                    className={`
                      text-sm font-medium
                      ${isCompleted ? 'text-green-600' : ''}
                      ${isCurrent ? 'text-blue-600' : ''}
                      ${isPending ? 'text-gray-400' : ''}
                    `}
                  >
                    {step.label}
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">Paso {step.number}</p>
                </div>
              </div>

              {/* Connecting Line */}
              {index < steps.length - 1 && (
                <div className="flex-1 h-0.5 mx-4 mb-8">
                  <div
                    className={`
                      h-full transition-all duration-300
                      ${step.status === 'completed' ? 'bg-green-500' : 'bg-gray-200'}
                    `}
                  />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Mobile-Responsive: Smaller text on mobile */}
      <style>{`
        @media (max-width: 640px) {
          .flex-col p {
            font-size: 0.75rem;
          }
        }
      `}</style>
    </div>
  );
};

export default CheckoutTimeline;
