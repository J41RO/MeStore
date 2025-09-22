import React, { useMemo } from 'react';
import { useCheckoutStore } from '../../stores/checkoutStore';

interface Step {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
}

interface CheckoutProgressProps {
  variant?: 'default' | 'mobile' | 'minimal';
  showLabels?: boolean;
}

const CheckoutProgress: React.FC<CheckoutProgressProps> = ({
  variant = 'default',
  showLabels = true
}) => {
  const { current_step, validateCurrentStep } = useCheckoutStore();

  const steps: Step[] = [
    {
      id: 'cart',
      name: 'Carrito',
      description: 'Revisar productos',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.5 5M7 13l-1.5 5m4.5-5h6m0 0v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m8 0V9a2 2 0 00-2-2H9a2 2 0 00-2-2"
          />
        </svg>
      )
    },
    {
      id: 'shipping',
      name: 'Envío',
      description: 'Dirección de entrega',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
      )
    },
    {
      id: 'payment',
      name: 'Pago',
      description: 'Método de pago',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
          />
        </svg>
      )
    },
    {
      id: 'confirmation',
      name: 'Confirmación',
      description: 'Finalizar pedido',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      )
    }
  ];

  const getStepStatus = useMemo(() => {
    return (stepId: string) => {
      const stepIndex = steps.findIndex(step => step.id === stepId);
      const currentIndex = steps.findIndex(step => step.id === current_step);

      if (stepIndex < currentIndex) {
        return 'completed';
      } else if (stepIndex === currentIndex) {
        return validateCurrentStep() ? 'current-valid' : 'current-invalid';
      } else {
        return 'upcoming';
      }
    };
  }, [current_step, validateCurrentStep, steps]);

  const getStepClasses = useMemo(() => {
    return (status: string) => {
      const baseClasses = {
        completed: {
          container: 'text-green-600',
          icon: 'bg-gradient-to-r from-green-500 to-green-600 text-white shadow-lg',
          connector: 'bg-gradient-to-r from-green-500 to-green-600',
          pulse: false
        },
        'current-valid': {
          container: 'text-blue-600',
          icon: 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg ring-4 ring-blue-100',
          connector: 'bg-gray-200',
          pulse: true
        },
        'current-invalid': {
          container: 'text-red-600',
          icon: 'bg-gradient-to-r from-red-500 to-red-600 text-white shadow-lg ring-4 ring-red-100',
          connector: 'bg-gray-200',
          pulse: true
        },
        upcoming: {
          container: 'text-gray-400',
          icon: 'bg-gray-200 text-gray-400 border-2 border-gray-300',
          connector: 'bg-gray-200',
          pulse: false
        }
      };

      return baseClasses[status as keyof typeof baseClasses] || baseClasses.upcoming;
    };
  }, []);

  const getContainerClasses = () => {
    switch (variant) {
      case 'mobile':
        return 'block';
      case 'minimal':
        return 'hidden lg:block';
      default:
        return 'hidden sm:block';
    }
  };

  const getLayoutClasses = () => {
    switch (variant) {
      case 'mobile':
        return 'flex items-center justify-between px-2';
      case 'minimal':
        return 'flex items-center space-x-2';
      default:
        return 'flex items-center';
    }
  };

  const renderMobileProgress = () => {
    const currentIndex = steps.findIndex(step => step.id === current_step);
    const progressPercentage = (currentIndex / (steps.length - 1)) * 100;

    return (
      <div className="w-full">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">
            Paso {currentIndex + 1} de {steps.length}
          </span>
          <span className="text-sm text-gray-500">
            {Math.round(progressPercentage)}% completado
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
          <div
            className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
        <div className="flex justify-between mt-2">
          {steps.map((step, index) => {
            const status = getStepStatus(step.id);
            const classes = getStepClasses(status);
            return (
              <div key={step.id} className="flex flex-col items-center">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs transition-all duration-300 ${
                  classes.icon
                } ${classes.pulse ? 'animate-pulse' : ''}`}>
                  {status === 'completed' ? (
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <span className="text-xs font-bold">{index + 1}</span>
                  )}
                </div>
                {showLabels && (
                  <span className={`text-xs mt-1 text-center max-w-16 truncate ${classes.container}`}>
                    {step.name}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  if (variant === 'mobile') {
    return (
      <div className={getContainerClasses()}>
        <nav aria-label="Progress">
          {renderMobileProgress()}
        </nav>
      </div>
    );
  }

  return (
    <div className={getContainerClasses()}>
      <nav aria-label="Progress">
        <ol className={getLayoutClasses()}>
          {steps.map((step, stepIdx) => {
            const status = getStepStatus(step.id);
            const classes = getStepClasses(status);
            const isLast = stepIdx === steps.length - 1;
            const spacing = variant === 'minimal' ? 'pr-4' : 'pr-8 sm:pr-20';

            return (
              <li
                key={step.id}
                className={`relative ${!isLast ? spacing : ''} transition-all duration-300`}
              >
                {/* Connector line */}
                {!isLast && (
                  <div
                    className={`
                      absolute top-4 left-4 -ml-px mt-0.5 h-0.5 transition-all duration-500
                      ${variant === 'minimal' ? 'w-8' : 'w-full'}
                      ${classes.connector}
                    `}
                    aria-hidden="true"
                  />
                )}

                <div className="relative flex items-start group hover:scale-105 transition-transform duration-200">
                  <span className="h-9 flex items-center">
                    <span
                      className={`
                        relative z-10 w-8 h-8 flex items-center justify-center rounded-full
                        ${classes.icon}
                        ${classes.pulse ? 'animate-pulse' : ''}
                        transition-all duration-300 transform hover:scale-110
                        ${status === 'completed' ? 'hover:rotate-12' : ''}
                      `}
                    >
                      {status === 'completed' ? (
                        <svg className="w-5 h-5 transition-transform duration-300" fill="currentColor" viewBox="0 0 20 20">
                          <path
                            fillRule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                      ) : (
                        <div className="transition-transform duration-300 group-hover:scale-110">
                          {step.icon}
                        </div>
                      )}
                    </span>
                  </span>

                  {showLabels && variant !== 'minimal' && (
                    <span className={`ml-4 min-w-0 flex flex-col transition-colors duration-200 ${classes.container}`}>
                      <span className="text-sm font-medium group-hover:font-semibold transition-all duration-200">
                        {step.name}
                      </span>
                      <span className="text-xs opacity-75 group-hover:opacity-100 transition-opacity duration-200">
                        {step.description}
                      </span>
                    </span>
                  )}
                </div>
              </li>
            );
          })}
        </ol>
      </nav>
    </div>
  );
};

export default CheckoutProgress;