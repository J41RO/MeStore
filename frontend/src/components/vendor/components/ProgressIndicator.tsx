import React from 'react';
import { motion } from 'framer-motion';

interface Step {
  id: number;
  name: string;
  icon: string;
  estimatedTime: number;
}

interface ProgressIndicatorProps {
  steps: Step[];
  currentStep: number;
  percentage: number;
  estimatedTimeRemaining: number;
  totalTime: number;
  'data-testid'?: string;
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  steps,
  currentStep,
  percentage,
  estimatedTimeRemaining,
  totalTime,
  'data-testid': testId
}) => {
  const formatTime = (seconds: number): string => {
    if (seconds < 60) {
      return `${Math.round(seconds)}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  };

  return (
    <div className="space-y-6" data-testid={testId}>
      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-gray-600">
          <span>Progreso del registro</span>
          <span className="font-semibold">{Math.round(percentage)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
          <motion.div
            className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            data-testid="progress-bar"
          />
        </div>
      </div>

      {/* Time Estimates */}
      <div className="flex justify-between text-xs text-gray-500 bg-gray-50 rounded-lg p-3">
        <div className="text-center">
          <div className="font-semibold text-gray-700">Tiempo restante</div>
          <div data-testid="time-remaining" className="text-blue-600 font-bold">
            {formatTime(estimatedTimeRemaining)}
          </div>
        </div>
        <div className="text-center">
          <div className="font-semibold text-gray-700">Tiempo transcurrido</div>
          <div className="text-green-600 font-bold">
            {formatTime(totalTime)}
          </div>
        </div>
        <div className="text-center">
          <div className="font-semibold text-gray-700">Meta</div>
          <div className="text-purple-600 font-bold">
            &lt; 2min
          </div>
        </div>
      </div>

      {/* Step Indicators */}
      <div className="flex justify-center">
        <div className="flex items-center space-x-2">
          {steps.map((step, index) => {
            const isActive = step.id === currentStep;
            const isCompleted = step.id < currentStep;
            const isUpcoming = step.id > currentStep;

            return (
              <React.Fragment key={step.id}>
                {/* Step Circle */}
                <motion.div
                  className={`relative w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-300 ${
                    isCompleted
                      ? 'bg-green-500 text-white shadow-lg'
                      : isActive
                      ? 'bg-blue-600 text-white shadow-lg ring-4 ring-blue-100'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                  initial={false}
                  animate={{
                    scale: isActive ? 1.1 : 1,
                    boxShadow: isActive ? '0 10px 25px rgba(59, 130, 246, 0.3)' : '0 4px 6px rgba(0, 0, 0, 0.1)'
                  }}
                  data-testid={`step-${step.id}`}
                  data-class={isActive ? 'active' : isCompleted ? 'completed' : 'inactive'}
                >
                  {isCompleted ? (
                    <motion.svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ duration: 0.2 }}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </motion.svg>
                  ) : (
                    <span className="text-xl">{step.icon}</span>
                  )}

                  {/* Active pulse effect */}
                  {isActive && (
                    <motion.div
                      className="absolute inset-0 rounded-full bg-blue-600"
                      initial={{ scale: 1, opacity: 0.3 }}
                      animate={{ scale: 1.4, opacity: 0 }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  )}
                </motion.div>

                {/* Connector Line */}
                {index < steps.length - 1 && (
                  <div className="w-8 h-0.5 bg-gray-300 relative overflow-hidden">
                    {isCompleted && (
                      <motion.div
                        className="absolute inset-0 bg-green-500"
                        initial={{ scaleX: 0 }}
                        animate={{ scaleX: 1 }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                        style={{ originX: 0 }}
                      />
                    )}
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Step Names */}
      <div className="flex justify-center">
        <div className="grid grid-cols-4 gap-4 text-center max-w-lg">
          {steps.map((step) => {
            const isActive = step.id === currentStep;
            const isCompleted = step.id < currentStep;

            return (
              <div key={step.id} className="space-y-1">
                <div
                  className={`text-xs font-medium transition-colors ${
                    isCompleted
                      ? 'text-green-600'
                      : isActive
                      ? 'text-blue-600'
                      : 'text-gray-400'
                  }`}
                >
                  {step.name}
                </div>
                <div className="text-xs text-gray-400">
                  ~{step.estimatedTime}s
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Performance Warning */}
      {totalTime > 60 && (
        <motion.div
          className="bg-yellow-50 border border-yellow-200 rounded-lg p-3"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center space-x-2">
            <span className="text-yellow-500 text-sm">⚡</span>
            <span className="text-yellow-700 text-sm font-medium">
              Estamos cerca del tiempo objetivo. ¡Continuemos!
            </span>
          </div>
        </motion.div>
      )}

      {/* Success Indicator */}
      {percentage === 100 && (
        <motion.div
          className="bg-green-50 border border-green-200 rounded-lg p-3 text-center"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          data-testid="registration-success"
        >
          <div className="text-green-600 text-lg font-bold mb-1">🎉 ¡Registro Completado!</div>
          <div className="text-green-700 text-sm">
            Tiempo total: {formatTime(totalTime)}
            {totalTime < 120 && ' - ¡Excelente tiempo!'}
          </div>
        </motion.div>
      )}
    </div>
  );
};