// ~/MeStore/frontend/src/components/Verifyform.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Verifyform Component
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: Verifyform.tsx
// Ruta: ~/MeStore/frontend/src/components/Verifyform.tsx
// Autor: Jairo
// Fecha de Creación: 2025-09-09 01:35:04
// Última Actualización: 2025-09-09 01:35:04
// Versión: 1.0.0
// Propósito: Auto-generated file
//
// ---------------------------------------------------------------------------------------------
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

interface VerifyformProps {
  mode: 'create' | 'edit';
  initialData?: any;
  onSubmit?: (data: any) => void;
  onCancel?: () => void;
  onSuccess?: () => void;
}

interface MessageState {
  text: string;
  type: 'success' | 'error' | 'info';
}

interface FormData {
  name: string;
  description: string;
  // Add more fields as needed
}

const validationSchema = yup.object({
  name: yup.string().required('Name is required'),
  description: yup.string().required('Description is required'),
});

const Verifyform: React.FC<VerifyformProps> = ({
  mode,
  initialData,
  onSubmit,
  onCancel,
  onSuccess,
}) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<MessageState | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    reset,
  } = useForm<FormData>({
    resolver: yupResolver(validationSchema),
    defaultValues: initialData || {
      name: '',
      description: '',
    },
  });

  const handleFormSubmit = async (data: FormData) => {
    setLoading(true);
    setMessage(null);

    try {
      // Handle form submission
      if (onSubmit) {
        await onSubmit(data);
      }

      setMessage({
        text: mode === 'create' ? 'Created successfully!' : 'Updated successfully!',
        type: 'success',
      });

      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      setMessage({
        text: 'An error occurred. Please try again.',
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        {mode === 'create' ? 'Create' : 'Edit'} Verifyform
      </h2>

      {message && (
        <div className={`mb-4 p-3 rounded-md ${
          message.type === 'success'
            ? 'bg-green-100 text-green-700 border border-green-300'
            : message.type === 'error'
            ? 'bg-red-100 text-red-700 border border-red-300'
            : 'bg-blue-100 text-blue-700 border border-blue-300'
        }`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Name
          </label>
          <input
            type="text"
            id="name"
            {...register('name')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.name.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Description
          </label>
          <textarea
            id="description"
            {...register('description')}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
          {errors.description && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.description.message}</p>
          )}
        </div>

        <div className="flex space-x-3 pt-4">
          <button
            type="submit"
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Saving...' : mode === 'create' ? 'Create' : 'Update'}
          </button>
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="flex-1 bg-gray-500 text-white py-2 px-4 rounded-md hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default Verifyform;
