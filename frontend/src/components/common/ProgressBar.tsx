/**
 * ProgressBar Component
 *
 * Animated progress bar for long-running operations.
 * Shows visual feedback for upload, download, processing tasks.
 *
 * Features:
 * - Animated progress indication (0-100%)
 * - Multiple color themes
 * - Optional label and percentage display
 * - Size variants
 * - Indeterminate mode for unknown duration
 *
 * Usage:
 * ```tsx
 * <ProgressBar progress={45} label="Uploading..." showPercentage />
 * <ProgressBar progress={100} color="green" label="Complete!" />
 * <ProgressBar indeterminate label="Processing..." />
 * ```
 */

import React from 'react';

interface ProgressBarProps {
  progress?: number; // 0-100
  label?: string;
  showPercentage?: boolean;
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'gray';
  size?: 'sm' | 'md' | 'lg';
  indeterminate?: boolean;
  className?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  progress = 0,
  label,
  showPercentage = false,
  color = 'blue',
  size = 'md',
  indeterminate = false,
  className = '',
}) => {
  // Ensure progress is within 0-100 range
  const normalizedProgress = Math.min(Math.max(progress, 0), 100);

  // Color mappings
  const colorClasses = {
    blue: 'bg-blue-600',
    green: 'bg-green-600',
    yellow: 'bg-yellow-500',
    red: 'bg-red-600',
    purple: 'bg-purple-600',
    gray: 'bg-gray-600',
  };

  const bgColorClasses = {
    blue: 'bg-blue-100',
    green: 'bg-green-100',
    yellow: 'bg-yellow-100',
    red: 'bg-red-100',
    purple: 'bg-purple-100',
    gray: 'bg-gray-100',
  };

  // Size mappings
  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Label and percentage */}
      {(label || showPercentage) && (
        <div className="flex justify-between items-center mb-2">
          {label && (
            <span className="text-sm font-medium text-gray-700">{label}</span>
          )}
          {showPercentage && !indeterminate && (
            <span className="text-sm font-medium text-gray-600">
              {normalizedProgress}%
            </span>
          )}
        </div>
      )}

      {/* Progress bar container */}
      <div
        className={`w-full ${bgColorClasses[color]} rounded-full overflow-hidden ${sizeClasses[size]}`}
        role="progressbar"
        aria-valuenow={indeterminate ? undefined : normalizedProgress}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label || 'Progress'}
      >
        {indeterminate ? (
          // Indeterminate animation
          <div
            className={`${colorClasses[color]} h-full rounded-full animate-indeterminate-progress`}
            style={{ width: '30%' }}
          />
        ) : (
          // Determinate progress
          <div
            className={`${colorClasses[color]} h-full rounded-full transition-all duration-300 ease-out`}
            style={{ width: `${normalizedProgress}%` }}
          />
        )}
      </div>
    </div>
  );
};

export default ProgressBar;

/**
 * Circular Progress Component
 * Circular/ring-style progress indicator
 */
export const CircularProgress: React.FC<{
  progress?: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
  showPercentage?: boolean;
}> = ({
  progress = 0,
  size = 120,
  strokeWidth = 8,
  color = '#3B82F6',
  showPercentage = true,
}) => {
  const normalizedProgress = Math.min(Math.max(progress, 0), 100);
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (normalizedProgress / 100) * circumference;

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#E5E7EB"
          strokeWidth={strokeWidth}
          fill="none"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-300 ease-out"
        />
      </svg>
      {showPercentage && (
        <span className="absolute text-xl font-bold text-gray-700">
          {Math.round(normalizedProgress)}%
        </span>
      )}
    </div>
  );
};

/**
 * Step Progress Component
 * Multi-step progress indicator
 */
export const StepProgress: React.FC<{
  steps: string[];
  currentStep: number;
}> = ({ steps, currentStep }) => {
  return (
    <div className="w-full">
      <div className="flex justify-between mb-2">
        {steps.map((step, index) => {
          const isCompleted = index < currentStep;
          const isCurrent = index === currentStep;

          return (
            <div
              key={index}
              className="flex flex-col items-center flex-1"
            >
              {/* Step circle */}
              <div
                className={`
                  w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm
                  transition-colors duration-200
                  ${
                    isCompleted
                      ? 'bg-green-600 text-white'
                      : isCurrent
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-600'
                  }
                `}
              >
                {isCompleted ? (
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                ) : (
                  index + 1
                )}
              </div>

              {/* Step label */}
              <span
                className={`
                  mt-2 text-xs text-center
                  ${isCurrent ? 'text-blue-600 font-semibold' : 'text-gray-600'}
                `}
              >
                {step}
              </span>

              {/* Connector line (except for last step) */}
              {index < steps.length - 1 && (
                <div
                  className={`
                    absolute h-1 top-5 left-1/2 right-0
                    transition-colors duration-200
                    ${isCompleted ? 'bg-green-600' : 'bg-gray-200'}
                  `}
                  style={{
                    width: `calc(100% / ${steps.length})`,
                    marginLeft: '1.25rem',
                  }}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

/**
 * Upload Progress Component
 * Specialized progress bar for file uploads
 */
export const UploadProgress: React.FC<{
  fileName: string;
  progress: number;
  onCancel?: () => void;
}> = ({ fileName, progress, onCancel }) => {
  const normalizedProgress = Math.min(Math.max(progress, 0), 100);
  const isComplete = normalizedProgress >= 100;

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-3 flex-1">
          {/* File icon */}
          <div className="flex-shrink-0">
            {isComplete ? (
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
            ) : (
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
            )}
          </div>

          {/* File info */}
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">{fileName}</p>
            <p className="text-xs text-gray-500">
              {isComplete ? 'Upload complete' : `Uploading... ${normalizedProgress}%`}
            </p>
          </div>
        </div>

        {/* Cancel button */}
        {!isComplete && onCancel && (
          <button
            onClick={onCancel}
            className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Cancel upload"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        )}
      </div>

      {/* Progress bar */}
      <ProgressBar
        progress={normalizedProgress}
        color={isComplete ? 'green' : 'blue'}
        size="sm"
      />
    </div>
  );
};
