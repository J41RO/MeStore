import React, { useEffect, useRef } from 'react';
import { UseFormReturn } from 'react-hook-form';
import { motion } from 'framer-motion';
import { ValidationResult } from '../../../hooks/useRealTimeValidation';
import { InputWithValidation } from '../../ui/InputWithValidation';
import { Button } from '../../ui/Button';
import { screenReader, reducedMotion } from '../../../utils/accessibility';

interface BasicInfoFormData {
  businessName: string;
  email: string;
  phone: string;
}

interface BasicInfoStepProps {
  form: UseFormReturn<BasicInfoFormData>;
  onNext: () => void;
  onPrev: () => void;
  isLoading: boolean;
  validateField: (fieldName: string, value: string, validationType?: string) => Promise<void>;
  validationResults: { [fieldName: string]: ValidationResult };
  isValidating: { [fieldName: string]: boolean };
}

export const BasicInfoStep: React.FC<BasicInfoStepProps> = ({
  form,
  onNext,
  onPrev,
  isLoading,
  validateField,
  validationResults,
  isValidating
}) => {
  const { register, handleSubmit, formState: { errors, isValid }, watch } = form;
  const stepRef = useRef<HTMLDivElement>(null);
  const firstInputRef = useRef<HTMLInputElement>(null);

  const watchedValues = watch();

  // Focus management on mount
  useEffect(() => {
    if (firstInputRef.current) {
      firstInputRef.current.focus();
      screenReader.announce('Paso 1 de 4: Información Básica. Completa los datos básicos de tu empresa.');
    }
  }, []);

  // Real-time validation effect
  useEffect(() => {
    if (watchedValues.businessName?.length >= 3) {
      validateField('businessName', watchedValues.businessName, 'businessName');
    }
  }, [watchedValues.businessName, validateField]);

  useEffect(() => {
    if (watchedValues.email?.includes('@')) {
      validateField('email', watchedValues.email, 'email');
    }
  }, [watchedValues.email, validateField]);

  useEffect(() => {
    if (watchedValues.phone?.length >= 10) {
      validateField('phone', watchedValues.phone, 'phone');
    }
  }, [watchedValues.phone, validateField]);

  const onSubmit = (data: BasicInfoFormData) => {
    console.log('Basic info submitted:', data);
    onNext();
  };

  const isStepValid = isValid &&
    validationResults.businessName?.isValid &&
    validationResults.email?.isValid &&
    validationResults.phone?.isValid;

  return (
    <motion.div
      ref={stepRef}
      initial={reducedMotion.prefersReducedMotion() ? { opacity: 0 } : { opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: reducedMotion.prefersReducedMotion() ? 0 : 0.3 }}
      className="space-y-6"
      role="tabpanel"
      aria-labelledby="step-1-heading"
      aria-describedby="step-1-description"
      tabIndex={-1}
    >
      {/* Step Header */}
      <header className="text-center mb-6">
        <h2
          id="step-1-heading"
          className="text-xl font-semibold text-gray-900 mb-2"
        >
          Información Básica
        </h2>
        <p
          id="step-1-description"
          className="text-gray-600 text-sm"
        >
          Completa los datos básicos de tu empresa. Todos los campos marcados con asterisco (*) son obligatorios.
        </p>
      </header>

      {/* Form */}
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="space-y-6"
        noValidate
        aria-label="Formulario de información básica"
      >
        {/* Business Name */}
        <div>
          <label
            htmlFor="business-name"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Nombre de la Empresa <span aria-label="obligatorio" className="text-red-500">*</span>
          </label>
          <InputWithValidation
            {...register('businessName')}
            ref={firstInputRef}
            id="business-name"
            type="text"
            placeholder="Mi Empresa SAS"
            data-testid="business-name-input"
            error={errors.businessName?.message}
            validationResult={validationResults.businessName}
            isValidating={isValidating.businessName}
            tooltip="Ingresa el nombre completo de tu empresa tal como aparece en los documentos legales"
            tooltipTestId="business-name-tooltip"
            aria-describedby="business-name-help business-name-error"
            aria-required="true"
            aria-invalid={errors.businessName ? 'true' : 'false'}
            autoComplete="organization"
          />
          <div id="business-name-help" className="sr-only">
            Campo obligatorio. Ingresa el nombre completo de tu empresa tal como aparece en los documentos legales.
          </div>
          {errors.businessName && (
            <div
              id="business-name-error"
              className="sr-only"
              aria-live="polite"
            >
              Error: {errors.businessName.message}
            </div>
          )}
        </div>

        {/* Email */}
        <div>
          <label
            htmlFor="email"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Correo Electrónico <span aria-label="obligatorio" className="text-red-500">*</span>
          </label>
          <InputWithValidation
            {...register('email')}
            id="email"
            type="email"
            placeholder="contacto@miempresa.com"
            data-testid="email-input"
            error={errors.email?.message}
            validationResult={validationResults.email}
            isValidating={isValidating.email}
            tooltip="Este será tu email de acceso a la plataforma"
            aria-describedby="email-help email-error"
            aria-required="true"
            aria-invalid={errors.email ? 'true' : 'false'}
            autoComplete="email"
          />
          <div id="email-help" className="sr-only">
            Campo obligatorio. Este será tu email de acceso a la plataforma.
          </div>
          {errors.email && (
            <div
              id="email-error"
              className="sr-only"
              aria-live="polite"
            >
              Error: {errors.email.message}
            </div>
          )}
        </div>

        {/* Phone */}
        <fieldset>
          <legend className="block text-sm font-medium text-gray-700 mb-2">
            Teléfono Móvil <span aria-label="obligatorio" className="text-red-500">*</span>
          </legend>
          <div className="flex" role="group" aria-labelledby="phone-legend">
            <div
              className="flex items-center bg-gray-50 border border-r-0 border-gray-300 rounded-l-lg px-3 py-3"
              aria-label="Código de país Colombia"
            >
              <span className="text-sm font-medium text-gray-700 mr-2" aria-hidden="true">🇨🇴</span>
              <span className="text-sm text-gray-600">+57</span>
            </div>
            <InputWithValidation
              {...register('phone')}
              id="phone"
              type="tel"
              placeholder="3001234567"
              data-testid="phone-input"
              error={errors.phone?.message}
              validationResult={validationResults.phone}
              isValidating={isValidating.phone}
              className="flex-1 rounded-l-none"
              maxLength={10}
              onInput={(e) => {
                const target = e.target as HTMLInputElement;
                // Only allow numbers
                target.value = target.value.replace(/\D/g, '');
              }}
              tooltip="Número móvil donde te enviaremos el código de verificación"
              aria-describedby="phone-help phone-error phone-format"
              aria-required="true"
              aria-invalid={errors.phone ? 'true' : 'false'}
              autoComplete="tel"
            />
          </div>
          <div id="phone-help" className="sr-only">
            Campo obligatorio. Número móvil donde te enviaremos el código de verificación.
          </div>
          <div id="phone-format" className="text-xs text-gray-500 mt-1">
            Formato: 10 dígitos sin espacios ni guiones (ejemplo: 3001234567)
          </div>
          {errors.phone && (
            <div
              id="phone-error"
              className="sr-only"
              aria-live="polite"
            >
              Error: {errors.phone.message}
            </div>
          )}
        </fieldset>

        {/* Progress Tips */}
        <aside
          className="bg-blue-50 border border-blue-200 rounded-lg p-4"
          aria-labelledby="tips-heading"
          role="complementary"
        >
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <svg
                className="w-5 h-5 text-blue-600 mt-0.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="flex-1">
              <h4 id="tips-heading" className="text-sm font-medium text-blue-900 mb-1">
                <span aria-hidden="true">💡</span> Consejos para un registro rápido
              </h4>
              <ul className="text-sm text-blue-700 space-y-1" role="list">
                <li role="listitem">Ten a mano el RUT o NIT de tu empresa</li>
                <li role="listitem">Usa un email que revises frecuentemente</li>
                <li role="listitem">Asegúrate de tener tu teléfono cerca para verificación</li>
              </ul>
            </div>
          </div>
        </aside>

        {/* Navigation Buttons */}
        <nav className="flex space-x-4 pt-4" aria-label="Navegación del formulario">
          <Button
            type="button"
            variant="outline"
            onClick={() => window.history.back()}
            className="flex-1"
            disabled={isLoading}
            aria-describedby="cancel-help"
          >
            Cancelar
          </Button>
          <div id="cancel-help" className="sr-only">
            Cancela el registro y regresa a la página anterior
          </div>

          <Button
            type="submit"
            disabled={!isStepValid || isLoading}
            className="flex-1"
            data-testid="continue-step-1"
            aria-describedby="continue-help"
            aria-live="polite"
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span aria-live="polite">Validando información...</span>
              </div>
            ) : (
              'Continuar al paso 2'
            )}
          </Button>
          <div id="continue-help" className="sr-only">
            {isStepValid
              ? 'Continúa al siguiente paso del registro'
              : 'Completa todos los campos obligatorios para continuar'
            }
          </div>
        </nav>
      </form>

      {/* Real-time Feedback */}
      <div
        className="text-xs text-gray-500 space-y-1"
        aria-label="Progreso del formulario"
        role="status"
        aria-live="polite"
      >
        <div className="flex items-center justify-between">
          <span>Progreso del paso:</span>
          <span className="font-medium">
            {Object.values(validationResults).filter(r => r?.isValid).length} de 3 campos válidos
          </span>
        </div>
        <div
          className="w-full bg-gray-200 rounded-full h-1"
          role="progressbar"
          aria-label="Progreso del formulario"
          aria-valuenow={Object.values(validationResults).filter(r => r?.isValid).length}
          aria-valuemin={0}
          aria-valuemax={3}
          aria-valuetext={`${Object.values(validationResults).filter(r => r?.isValid).length} de 3 campos completados`}
        >
          <div
            className="bg-blue-600 h-1 rounded-full transition-all duration-300"
            style={{
              width: `${(Object.values(validationResults).filter(r => r?.isValid).length / 3) * 100}%`
            }}
          />
        </div>
        <div className="sr-only" aria-live="polite">
          Progreso del formulario: {Object.values(validationResults).filter(r => r?.isValid).length} de 3 campos completados correctamente.
        </div>
      </div>
    </motion.div>
  );
};