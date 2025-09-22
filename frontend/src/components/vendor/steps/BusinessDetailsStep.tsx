import React, { useEffect } from 'react';
import { UseFormReturn } from 'react-hook-form';
import { motion } from 'framer-motion';
import { ValidationResult } from '../../../hooks/useRealTimeValidation';
import { InputWithValidation } from '../../ui/InputWithValidation';
import { Button } from '../../ui/Button';

interface BusinessDetailsFormData {
  businessType: 'persona_juridica' | 'persona_natural';
  nit?: string;
  address: string;
  city: string;
  department: string;
}

interface BusinessDetailsStepProps {
  form: UseFormReturn<BusinessDetailsFormData>;
  onNext: () => void;
  onPrev: () => void;
  isLoading: boolean;
  validateField: (fieldName: string, value: string, validationType?: string) => Promise<void>;
  validationResults: { [fieldName: string]: ValidationResult };
  isValidating: { [fieldName: string]: boolean };
}

const DEPARTMENTS = [
  { value: 'santander', label: 'Santander' },
  { value: 'cundinamarca', label: 'Cundinamarca' },
  { value: 'antioquia', label: 'Antioquia' },
  { value: 'valle', label: 'Valle del Cauca' },
  { value: 'atlantico', label: 'Atlántico' },
  { value: 'bolivar', label: 'Bolívar' },
  { value: 'boyaca', label: 'Boyacá' },
  { value: 'caldas', label: 'Caldas' },
  { value: 'casanare', label: 'Casanare' },
  { value: 'cauca', label: 'Cauca' }
];

export const BusinessDetailsStep: React.FC<BusinessDetailsStepProps> = ({
  form,
  onNext,
  onPrev,
  isLoading,
  validateField,
  validationResults,
  isValidating
}) => {
  const { register, handleSubmit, formState: { errors, isValid }, watch, setValue } = form;

  const watchedValues = watch();

  // Real-time validation effects
  useEffect(() => {
    if (watchedValues.nit && watchedValues.businessType === 'persona_juridica') {
      validateField('nit', watchedValues.nit, 'nit');
    }
  }, [watchedValues.nit, watchedValues.businessType, validateField]);

  const onSubmit = (data: BusinessDetailsFormData) => {
    console.log('Business details submitted:', data);
    onNext();
  };

  const isStepValid = isValid && (
    watchedValues.businessType === 'persona_natural' ||
    (watchedValues.businessType === 'persona_juridica' && validationResults.nit?.isValid)
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* Step Header */}
      <div className="text-center mb-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Detalles del Negocio
        </h3>
        <p className="text-gray-600 text-sm">
          Información legal y fiscal de tu empresa
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Business Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Tipo de Negocio *
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Persona Natural */}
            <motion.div
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setValue('businessType', 'persona_natural')}
              className={`p-6 rounded-lg border-2 cursor-pointer transition-all ${
                watchedValues.businessType === 'persona_natural'
                  ? 'border-green-500 bg-green-50 shadow-lg'
                  : 'border-gray-300 hover:border-green-300 hover:shadow-md bg-white'
              }`}
            >
              <div className="text-center">
                <div className={`w-12 h-12 mx-auto mb-3 rounded-full flex items-center justify-center ${
                  watchedValues.businessType === 'persona_natural' ? 'bg-green-100' : 'bg-gray-100'
                }`}>
                  <span className="text-2xl">👤</span>
                </div>
                <h4 className="font-bold text-gray-900 text-base mb-1">Persona Natural</h4>
                <p className="text-sm text-gray-600 font-medium">Vendo como independiente</p>
              </div>
            </motion.div>

            {/* Persona Jurídica */}
            <motion.div
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setValue('businessType', 'persona_juridica')}
              className={`p-6 rounded-lg border-2 cursor-pointer transition-all ${
                watchedValues.businessType === 'persona_juridica'
                  ? 'border-blue-500 bg-blue-50 shadow-lg'
                  : 'border-gray-300 hover:border-blue-300 hover:shadow-md bg-white'
              }`}
            >
              <div className="text-center">
                <div className={`w-12 h-12 mx-auto mb-3 rounded-full flex items-center justify-center ${
                  watchedValues.businessType === 'persona_juridica' ? 'bg-blue-100' : 'bg-gray-100'
                }`}>
                  <span className="text-2xl">🏢</span>
                </div>
                <h4 className="font-bold text-gray-900 text-base mb-1">Persona Jurídica</h4>
                <p className="text-sm text-gray-600 font-medium">Tengo empresa constituida</p>
              </div>
            </motion.div>
          </div>
          <input type="hidden" {...register('businessType')} data-testid="business-type-select" />
        </div>

        {/* NIT Field (only for Persona Jurídica) */}
        {watchedValues.businessType === 'persona_juridica' && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <label className="block text-sm font-medium text-gray-700 mb-2">
              NIT *
            </label>
            <InputWithValidation
              {...register('nit')}
              type="text"
              placeholder="123456789-0"
              data-testid="nit-input"
              error={errors.nit?.message}
              validationResult={validationResults.nit}
              isValidating={isValidating.nit}
              onInput={(e) => {
                const target = e.target as HTMLInputElement;
                let value = target.value.replace(/[^\d-]/g, '');

                // Auto-format NIT
                if (value.length === 9 && !value.includes('-')) {
                  value = value + '-';
                }

                target.value = value;
              }}
              maxLength={11}
              tooltip="NIT de la empresa con dígito de verificación"
              suggestionTestId="nit-suggestion"
            />
          </motion.div>
        )}

        {/* Address */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Dirección Fiscal *
          </label>
          <InputWithValidation
            {...register('address')}
            type="text"
            placeholder="Carrera 27 #123-45, Centro"
            data-testid="address-input"
            error={errors.address?.message}
            tooltip="Dirección registrada en documentos legales"
          />
        </div>

        {/* City and Department */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* City */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Ciudad *
            </label>
            <InputWithValidation
              {...register('city')}
              type="text"
              placeholder="Bucaramanga"
              data-testid="city-input"
              error={errors.city?.message}
            />
          </div>

          {/* Department */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Departamento *
            </label>
            <select
              {...register('department')}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors text-gray-900 bg-white font-medium"
              data-testid="department-select"
            >
              <option value="">Seleccionar departamento</option>
              {DEPARTMENTS.map((dept) => (
                <option key={dept.value} value={dept.value}>
                  {dept.label}
                </option>
              ))}
            </select>
            {errors.department && (
              <p className="mt-1 text-sm text-red-600">{errors.department.message}</p>
            )}
          </div>
        </div>

        {/* Legal Notice */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <svg className="w-5 h-5 text-yellow-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 18.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div className="flex-1">
              <h4 className="text-sm font-medium text-yellow-900 mb-1">
                📋 Información importante
              </h4>
              <p className="text-sm text-yellow-700">
                Los datos deben coincidir exactamente con los documentos legales de tu empresa.
                Esto es necesario para la verificación y cumplimiento normativo.
              </p>
            </div>
          </div>
        </div>

        {/* Navigation Buttons */}
        <div className="flex space-x-4 pt-4">
          <Button
            type="button"
            variant="outline"
            onClick={onPrev}
            className="flex-1"
            disabled={isLoading}
            data-testid="back-to-step-1"
          >
            Atrás
          </Button>
          <Button
            type="submit"
            disabled={!isStepValid || isLoading}
            className="flex-1"
            data-testid="continue-step-2"
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Validando...
              </div>
            ) : (
              'Continuar'
            )}
          </Button>
        </div>
      </form>

      {/* Progress Indicator */}
      <div className="text-xs text-gray-500 space-y-1">
        <div className="flex items-center justify-between">
          <span>Campos completados:</span>
          <span className="font-medium">
            {Object.values(watchedValues).filter(v => v && v !== '').length}/
            {watchedValues.businessType === 'persona_juridica' ? 5 : 4}
          </span>
        </div>
      </div>
    </motion.div>
  );
};