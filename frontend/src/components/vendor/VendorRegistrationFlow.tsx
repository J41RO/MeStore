import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { motion, AnimatePresence } from 'framer-motion';
import { useVendorRegistration } from '../../hooks/useVendorRegistration';
import { useRealTimeValidation } from '../../hooks/useRealTimeValidation';
import { useAutoSave } from '../../hooks/useAutoSave';
import { UserType } from '../../types/auth.types';
import { ProgressIndicator } from './components/ProgressIndicator';
import { BasicInfoStep } from './steps/BasicInfoStep';
import { BusinessDetailsStep } from './steps/BusinessDetailsStep';
import { VerificationStep } from './steps/VerificationStep';
import { DocumentsStep } from './steps/DocumentsStep';
import { ErrorBoundary } from '../common/ErrorBoundary';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import '../../styles/vendor-registration.css';

// Performance monitoring
const performanceMonitor = {
  startTime: 0,
  stepTimes: [] as number[],

  start() {
    this.startTime = performance.now();
  },

  stepCompleted() {
    const elapsed = performance.now() - this.startTime;
    this.stepTimes.push(elapsed);
    console.log(`Step completed in ${elapsed.toFixed(2)}ms`);
  },

  getTotalTime() {
    return (performance.now() - this.startTime) / 1000;
  }
};

// Validation schemas optimized for speed
const basicInfoSchema = yup.object({
  businessName: yup
    .string()
    .required('Nombre de empresa requerido')
    .min(3, 'Mínimo 3 caracteres')
    .max(100, 'Máximo 100 caracteres'),
  email: yup
    .string()
    .required('Email requerido')
    .email('Email inválido'),
  phone: yup
    .string()
    .required('Teléfono requerido')
    .matches(/^3\d{9}$/, 'Formato: 3001234567')
});

const businessDetailsSchema = yup.object({
  businessType: yup
    .string()
    .required('Tipo de negocio requerido')
    .oneOf(['persona_juridica', 'persona_natural']),
  nit: yup
    .string()
    .when('businessType', {
      is: 'persona_juridica',
      then: (schema) => schema
        .required('NIT requerido')
        .matches(/^\d{9}-\d$/, 'Formato: 123456789-0'),
      otherwise: (schema) => schema.notRequired()
    }),
  address: yup
    .string()
    .required('Dirección requerida')
    .min(10, 'Mínimo 10 caracteres'),
  city: yup
    .string()
    .required('Ciudad requerida'),
  department: yup
    .string()
    .required('Departamento requerido')
});

export interface VendorRegistrationData {
  // Step 1: Basic Info
  businessName: string;
  email: string;
  phone: string;

  // Step 2: Business Details
  businessType: 'persona_juridica' | 'persona_natural';
  nit?: string;
  address: string;
  city: string;
  department: string;

  // Step 3: Verification
  phoneVerified: boolean;
  emailVerified: boolean;

  // Step 4: Documents
  documents: File[];
}

const STEPS = [
  { id: 1, name: 'Información Básica', icon: '👤', estimatedTime: 20 },
  { id: 2, name: 'Detalles del Negocio', icon: '🏢', estimatedTime: 30 },
  { id: 3, name: 'Verificación', icon: '📱', estimatedTime: 40 },
  { id: 4, name: 'Documentos', icon: '📄', estimatedTime: 30 }
];

const VendorRegistrationFlow: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  // Initialize performance monitoring
  useEffect(() => {
    performanceMonitor.start();
  }, []);

  // Hooks
  const {
    submitRegistration,
    isLoading,
    error: registrationError,
    progress
  } = useVendorRegistration();

  const { savedData, autoSave, clearSavedData } = useAutoSave<VendorRegistrationData>('vendor-registration-draft');

  // Form state for each step
  const basicInfoForm = useForm({
    resolver: yupResolver(basicInfoSchema),
    mode: 'onChange',
    defaultValues: {
      businessName: savedData?.businessName || '',
      email: savedData?.email || '',
      phone: savedData?.phone || ''
    }
  });

  const businessDetailsForm = useForm({
    resolver: yupResolver(businessDetailsSchema),
    mode: 'onChange',
    defaultValues: {
      businessType: savedData?.businessType || 'persona_natural',
      nit: savedData?.nit || '',
      address: savedData?.address || '',
      city: savedData?.city || '',
      department: savedData?.department || ''
    }
  });

  // Real-time validation
  const {
    validateField,
    validationResults,
    isValidating
  } = useRealTimeValidation();

  // Watch form values for auto-save
  const basicInfoValues = basicInfoForm.watch();
  const businessDetailsValues = businessDetailsForm.watch();

  // Auto-save effect
  useEffect(() => {
    const formData = {
      ...basicInfoValues,
      ...businessDetailsValues,
      phoneVerified: false,
      emailVerified: false,
      documents: []
    };

    autoSave(formData);
  }, [basicInfoValues, businessDetailsValues, autoSave]);

  // Network status monitoring
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Calculate progress and time estimates
  const progressData = useMemo(() => {
    const completedSteps = currentStep - 1;
    const totalSteps = STEPS.length;
    const percentage = (completedSteps / totalSteps) * 100;

    const remainingSteps = STEPS.slice(currentStep - 1);
    const estimatedTimeRemaining = remainingSteps.reduce((total, step) => total + step.estimatedTime, 0);

    return {
      percentage,
      estimatedTimeRemaining,
      currentStepTime: STEPS[currentStep - 1]?.estimatedTime || 0
    };
  }, [currentStep]);

  // Step navigation with validation
  const nextStep = useCallback(async () => {
    let isValid = false;

    if (currentStep === 1) {
      isValid = await basicInfoForm.trigger();
    } else if (currentStep === 2) {
      isValid = await businessDetailsForm.trigger();
    } else {
      isValid = true; // Steps 3 and 4 have custom validation
    }

    if (isValid && currentStep < STEPS.length) {
      performanceMonitor.stepCompleted();
      setCurrentStep(prev => prev + 1);
    }
  }, [currentStep, basicInfoForm, businessDetailsForm]);

  const prevStep = useCallback(() => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1);
    }
  }, [currentStep]);

  // Submit registration
  const handleSubmitRegistration = useCallback(async () => {
    try {
      const formData = {
        ...basicInfoForm.getValues(),
        ...businessDetailsForm.getValues(),
        userType: UserType.VENDOR,
        phoneVerified: true,
        emailVerified: true,
        documents: []
      };

      const success = await submitRegistration(formData);

      if (success) {
        clearSavedData();
        navigate('/vendor/dashboard');
      }
    } catch (error) {
      console.error('Registration failed:', error);
    }
  }, [basicInfoForm, businessDetailsForm, submitRegistration, clearSavedData, navigate]);

  // Step components
  const renderStep = () => {
    const stepProps = {
      onNext: nextStep,
      onPrev: prevStep,
      isLoading,
      validateField,
      validationResults,
      isValidating
    };

    switch (currentStep) {
      case 1:
        return (
          <BasicInfoStep
            {...stepProps}
            form={basicInfoForm}
            data-testid="basic-info-step"
          />
        );
      case 2:
        return (
          <BusinessDetailsStep
            {...stepProps}
            form={businessDetailsForm}
            data-testid="business-details-step"
          />
        );
      case 3:
        return (
          <VerificationStep
            {...stepProps}
            email={basicInfoForm.getValues('email')}
            phone={basicInfoForm.getValues('phone')}
            data-testid="verification-step"
          />
        );
      case 4:
        return (
          <DocumentsStep
            {...stepProps}
            onComplete={handleSubmitRegistration}
            data-testid="documents-step"
          />
        );
      default:
        return null;
    }
  };

  const totalTime = performanceMonitor.getTotalTime();

  return (
    <ErrorBoundary>
      {/* Skip to main content link for screen readers */}
      <a
        href="#main-content"
        className="skip-link enhanced-focus"
        tabIndex={0}
      >
        Saltar al contenido principal
      </a>

      <div
        className="vendor-registration-container"
        role="main"
        aria-labelledby="registration-title"
      >
        {/* Offline indicator */}
        {!isOnline && (
          <div
            className="bg-yellow-500 text-white text-center py-2 text-sm font-medium"
            data-testid="offline-indicator"
            role="alert"
            aria-live="assertive"
          >
            ⚠️ Conexión perdida. Los datos se guardarán localmente.
          </div>
        )}

        {/* Error banner */}
        {registrationError && (
          <div
            className="bg-red-500 text-white p-4 text-center"
            data-testid="error-banner"
            role="alert"
            aria-live="assertive"
          >
            <div className="flex items-center justify-center space-x-2">
              <span>{registrationError}</span>
              <button
                onClick={() => window.location.reload()}
                className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm enhanced-focus touch-target"
                data-testid="retry-button"
                aria-label="Reintentar registro"
              >
                Reintentar
              </button>
            </div>
          </div>
        )}

        <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2">
          {/* Left Side: Form */}
          <div className="flex items-center justify-center mobile-step-container lg:p-12">
            <div className="w-full max-w-md tablet-form-width spacing-lg">
              {/* Progress Indicator */}
              <ProgressIndicator
                steps={STEPS}
                currentStep={currentStep}
                percentage={progressData.percentage}
                estimatedTimeRemaining={progressData.estimatedTimeRemaining}
                totalTime={totalTime}
                data-testid="step-indicator"
              />

              {/* Performance Info (Development only) */}
              {process.env.NODE_ENV === 'development' && (
                <div className="perf-indicator text-xs">
                  <div data-testid="estimated-time">
                    Tiempo estimado: {progressData.estimatedTimeRemaining}s
                  </div>
                  <div data-testid="time-remaining">
                    Tiempo transcurrido: {totalTime.toFixed(1)}s
                  </div>
                  <div data-testid="progress-bar">
                    Progreso: {progressData.percentage.toFixed(0)}%
                  </div>
                </div>
              )}

              {/* Header */}
              <header className="text-center" id="main-content">
                <div
                  className="mx-auto w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg gpu-accelerated"
                  aria-hidden="true"
                >
                  <span className="text-2xl" role="img" aria-label={`Paso ${currentStep}: ${STEPS[currentStep - 1]?.name}`}>
                    {STEPS[currentStep - 1]?.icon}
                  </span>
                </div>
                <h1
                  id="registration-title"
                  className="mobile-title lg:text-3xl font-bold text-gray-900 mb-2"
                >
                  Registro de Vendedor
                </h1>
                <p className="mobile-subtitle lg:text-base text-gray-600" aria-describedby="step-description">
                  <span id="step-description">
                    Paso {currentStep} de {STEPS.length}: {STEPS[currentStep - 1]?.name}
                  </span>
                </p>
              </header>

              {/* Loading Overlay */}
              {isLoading && (
                <div
                  className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
                  data-testid="loading-spinner"
                >
                  <div className="bg-white rounded-lg p-6 flex items-center space-x-3">
                    <LoadingSpinner />
                    <span>Procesando registro...</span>
                  </div>
                </div>
              )}

              {/* Step Content */}
              <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={currentStep}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.15 }}
                  >
                    {renderStep()}
                  </motion.div>
                </AnimatePresence>
              </div>

              {/* Login link */}
              <div className="text-center mt-6 pt-6 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => navigate('/login')}
                  className="text-blue-600 hover:text-blue-800 font-medium transition-colors"
                >
                  ¿Ya tienes cuenta? Inicia sesión
                </button>
              </div>
            </div>
          </div>

          {/* Right Side: Visual */}
          <div className="hidden lg:flex items-center justify-center bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 relative overflow-hidden">
            {/* 3D Background Elements */}
            <div className="absolute inset-0">
              <div className="absolute top-20 left-20 w-32 h-32 bg-white/10 rounded-full blur-xl animate-pulse"></div>
              <div className="absolute bottom-32 right-16 w-24 h-24 bg-white/15 rounded-full blur-lg animate-pulse delay-300"></div>
              <div className="absolute top-1/2 left-16 w-16 h-16 bg-white/20 rounded-full blur-md animate-pulse delay-700"></div>
              <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:50px_50px]"></div>
            </div>

            {/* Main Content */}
            <div className="relative z-10 text-center text-white p-12 max-w-lg">
              <div className="mb-8">
                <div className="mx-auto w-24 h-24 bg-white/20 backdrop-blur rounded-3xl flex items-center justify-center mb-6 shadow-2xl transform rotate-3 hover:rotate-0 transition-transform duration-500">
                  <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                  </svg>
                </div>
                <h1 className="text-4xl font-bold mb-2">MeStocker</h1>
                <p className="text-xl text-blue-100">Tu plataforma de ventas</p>
              </div>

              {/* Features */}
              <div className="space-y-4 text-left">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-white/90">Registro rápido en 2 minutos</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <span className="text-white/90">Validación en tiempo real</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                  <span className="text-white/90">Datos guardados automáticamente</span>
                </div>
              </div>

              {/* Stats */}
              <div className="mt-8 p-4 bg-white/10 backdrop-blur rounded-xl border border-white/20">
                <p className="text-white/90 text-sm">
                  Únete a más de <span className="font-bold text-white">2,000+</span> vendedores exitosos
                </p>
              </div>
            </div>

            {/* Floating particles */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
              <div className="absolute top-10 left-10 w-2 h-2 bg-white/30 rounded-full animate-ping"></div>
              <div className="absolute top-1/3 right-20 w-1 h-1 bg-white/40 rounded-full animate-ping delay-1000"></div>
              <div className="absolute bottom-20 left-1/3 w-1.5 h-1.5 bg-white/35 rounded-full animate-ping delay-500"></div>
            </div>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default VendorRegistrationFlow;