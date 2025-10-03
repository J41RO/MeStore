import React, { useEffect } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { ShippingAddress, useCheckoutStore } from '../../stores/checkoutStore';

interface AddressFormProps {
  address?: ShippingAddress;
  onSubmit: (address: ShippingAddress) => void;
  onCancel?: () => void;
}

interface AddressFormData {
  name: string;
  phone: string;
  address: string;
  city: string;
  department: string;
  postal_code: string;
  additional_info: string;
  is_default: boolean;
}

// Colombian departments list
const COLOMBIAN_DEPARTMENTS = [
  'Amazonas', 'Antioquia', 'Arauca', 'Atlántico', 'Bolívar', 'Boyacá',
  'Caldas', 'Caquetá', 'Casanare', 'Cauca', 'Cesar', 'Chocó',
  'Córdoba', 'Cundinamarca', 'Guainía', 'Guaviare', 'Huila',
  'La Guajira', 'Magdalena', 'Meta', 'Nariño', 'Norte de Santander',
  'Putumayo', 'Quindío', 'Risaralda', 'San Andrés y Providencia',
  'Santander', 'Sucre', 'Tolima', 'Valle del Cauca', 'Vaupés', 'Vichada'
];

const AddressForm: React.FC<AddressFormProps> = ({ address, onSubmit, onCancel }) => {
  const { addSavedAddress } = useCheckoutStore();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, isValid },
    reset
  } = useForm<AddressFormData>({
    mode: 'onChange',
    reValidateMode: 'onChange',
    defaultValues: {
      name: address?.name || '',
      phone: address?.phone || '',
      address: address?.address || '',
      city: address?.city || '',
      department: address?.department || '',
      postal_code: address?.postal_code || '',
      additional_info: address?.additional_info || '',
      is_default: address?.is_default || false
    }
  });

  // Reset form if address prop changes
  useEffect(() => {
    if (address) {
      reset({
        name: address.name,
        phone: address.phone,
        address: address.address,
        city: address.city,
        department: address.department || '',
        postal_code: address.postal_code || '',
        additional_info: address.additional_info || '',
        is_default: address.is_default || false
      });
    }
  }, [address, reset]);

  const onSubmitHandler: SubmitHandler<AddressFormData> = async (data) => {
    try {
      const newAddress: ShippingAddress = {
        id: address?.id || Date.now().toString(),
        name: data.name.trim(),
        phone: data.phone.trim(),
        address: data.address.trim(),
        city: data.city.trim(),
        department: data.department,
        postal_code: data.postal_code.trim(),
        additional_info: data.additional_info.trim(),
        is_default: data.is_default
      };

      // Save to store if it's a new address
      if (!address) {
        addSavedAddress(newAddress);
      }

      onSubmit(newAddress);
    } catch (error) {
      console.error('Error saving address:', error);
    }
  };

  return (
    <div className="bg-gray-50 rounded-lg p-6">
      <form onSubmit={handleSubmit(onSubmitHandler)} className="space-y-4">
        {/* Name Field */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            Nombre completo *
          </label>
          <input
            type="text"
            id="name"
            {...register('name', {
              required: 'El nombre completo es requerido',
              minLength: {
                value: 3,
                message: 'El nombre debe tener al menos 3 caracteres'
              },
              maxLength: {
                value: 100,
                message: 'El nombre no puede exceder 100 caracteres'
              },
              pattern: {
                value: /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/,
                message: 'El nombre solo puede contener letras y espacios'
              },
              validate: {
                noMultipleSpaces: (value) =>
                  !/\s{2,}/.test(value) || 'No se permiten espacios múltiples',
                hasLastName: (value) =>
                  value.trim().split(/\s+/).length >= 2 || 'Debe incluir nombre y apellido'
              }
            })}
            placeholder="Ej: Juan Pérez García"
            className={`
              w-full px-3 py-2 border rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500
              ${errors.name ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'}
            `}
            aria-invalid={errors.name ? 'true' : 'false'}
            aria-describedby={errors.name ? 'name-error' : undefined}
          />
          {errors.name && (
            <p id="name-error" className="mt-1 text-sm text-red-600" role="alert">
              {errors.name.message}
            </p>
          )}
        </div>

        {/* Phone Field */}
        <div>
          <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
            Teléfono celular *
          </label>
          <input
            type="tel"
            id="phone"
            {...register('phone', {
              required: 'El número de teléfono es requerido',
              pattern: {
                value: /^3\d{9}$/,
                message: 'Debe ser un celular colombiano válido (10 dígitos comenzando con 3)'
              },
              validate: {
                validFormat: (value) => {
                  const cleaned = value.replace(/\D/g, '');
                  return cleaned.length === 10 && cleaned.startsWith('3') ||
                    'Formato inválido. Ej: 3001234567';
                }
              }
            })}
            placeholder="Ej: 3001234567"
            maxLength={10}
            className={`
              w-full px-3 py-2 border rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500
              ${errors.phone ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'}
            `}
            aria-invalid={errors.phone ? 'true' : 'false'}
            aria-describedby={errors.phone ? 'phone-error' : undefined}
          />
          {errors.phone && (
            <p id="phone-error" className="mt-1 text-sm text-red-600" role="alert">
              {errors.phone.message}
            </p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            Ingresa tu número celular (10 dígitos)
          </p>
        </div>

        {/* Address Field */}
        <div>
          <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-1">
            Dirección completa *
          </label>
          <input
            type="text"
            id="address"
            {...register('address', {
              required: 'La dirección es requerida',
              minLength: {
                value: 10,
                message: 'La dirección debe tener al menos 10 caracteres'
              },
              maxLength: {
                value: 200,
                message: 'La dirección no puede exceder 200 caracteres'
              },
              pattern: {
                value: /^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s#\-,.°]+$/,
                message: 'La dirección contiene caracteres no permitidos'
              },
              validate: {
                hasNumber: (value) =>
                  /\d/.test(value) || 'La dirección debe incluir números',
                notOnlySpaces: (value) =>
                  value.trim().length >= 10 || 'La dirección es muy corta'
              }
            })}
            placeholder="Ej: Carrera 15 # 93-47, Apartamento 501"
            className={`
              w-full px-3 py-2 border rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500
              ${errors.address ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'}
            `}
            aria-invalid={errors.address ? 'true' : 'false'}
            aria-describedby={errors.address ? 'address-error' : undefined}
          />
          {errors.address && (
            <p id="address-error" className="mt-1 text-sm text-red-600" role="alert">
              {errors.address.message}
            </p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            Incluye calle, número, apartamento/casa, etc.
          </p>
        </div>

        {/* City and Department */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-1">
              Ciudad *
            </label>
            <input
              type="text"
              id="city"
              {...register('city', {
                required: 'La ciudad es requerida',
                minLength: {
                  value: 3,
                  message: 'El nombre de la ciudad debe tener al menos 3 caracteres'
                },
                maxLength: {
                  value: 50,
                  message: 'El nombre de la ciudad es muy largo'
                },
                pattern: {
                  value: /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/,
                  message: 'El nombre de la ciudad solo puede contener letras y espacios'
                }
              })}
              placeholder="Ej: Bogotá"
              className={`
                w-full px-3 py-2 border rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500
                ${errors.city ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'}
              `}
              aria-invalid={errors.city ? 'true' : 'false'}
              aria-describedby={errors.city ? 'city-error' : undefined}
            />
            {errors.city && (
              <p id="city-error" className="mt-1 text-sm text-red-600" role="alert">
                {errors.city.message}
              </p>
            )}
          </div>

          <div>
            <label htmlFor="department" className="block text-sm font-medium text-gray-700 mb-1">
              Departamento *
            </label>
            <select
              id="department"
              {...register('department', {
                required: 'Debe seleccionar un departamento',
                validate: (value) =>
                  COLOMBIAN_DEPARTMENTS.includes(value) || 'Departamento inválido'
              })}
              className={`
                w-full px-3 py-2 border rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500
                ${errors.department ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'}
              `}
              aria-invalid={errors.department ? 'true' : 'false'}
              aria-describedby={errors.department ? 'department-error' : undefined}
            >
              <option value="">Seleccionar departamento</option>
              {COLOMBIAN_DEPARTMENTS.map(dept => (
                <option key={dept} value={dept}>{dept}</option>
              ))}
            </select>
            {errors.department && (
              <p id="department-error" className="mt-1 text-sm text-red-600" role="alert">
                {errors.department.message}
              </p>
            )}
          </div>
        </div>

        {/* Postal Code */}
        <div>
          <label htmlFor="postal_code" className="block text-sm font-medium text-gray-700 mb-1">
            Código postal *
          </label>
          <input
            type="text"
            id="postal_code"
            {...register('postal_code', {
              required: 'El código postal es requerido',
              pattern: {
                value: /^\d{6}$/,
                message: 'El código postal debe tener exactamente 6 dígitos'
              }
            })}
            placeholder="Ej: 110111"
            maxLength={6}
            className={`
              w-full px-3 py-2 border rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500
              ${errors.postal_code ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'}
            `}
            aria-invalid={errors.postal_code ? 'true' : 'false'}
            aria-describedby={errors.postal_code ? 'postal-code-error' : undefined}
          />
          {errors.postal_code && (
            <p id="postal-code-error" className="mt-1 text-sm text-red-600" role="alert">
              {errors.postal_code.message}
            </p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            6 dígitos numéricos
          </p>
        </div>

        {/* Additional Info */}
        <div>
          <label htmlFor="additional_info" className="block text-sm font-medium text-gray-700 mb-1">
            Información adicional (opcional)
          </label>
          <textarea
            id="additional_info"
            {...register('additional_info', {
              maxLength: {
                value: 200,
                message: 'La información adicional no puede exceder 200 caracteres'
              },
              pattern: {
                value: /^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s.,\-:;°#]+$/,
                message: 'Contiene caracteres no permitidos'
              }
            })}
            rows={2}
            placeholder="Ej: Casa de dos pisos color blanco, portón negro..."
            className={`
              w-full px-3 py-2 border rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500
              ${errors.additional_info ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'}
            `}
            aria-invalid={errors.additional_info ? 'true' : 'false'}
            aria-describedby={errors.additional_info ? 'additional-info-error' : undefined}
          />
          {errors.additional_info && (
            <p id="additional-info-error" className="mt-1 text-sm text-red-600" role="alert">
              {errors.additional_info.message}
            </p>
          )}
        </div>

        {/* Default Address */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="is_default"
            {...register('is_default')}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="is_default" className="ml-2 block text-sm text-gray-900">
            Establecer como dirección predeterminada
          </label>
        </div>

        {/* Form Validation Summary */}
        {Object.keys(errors).length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3">
            <p className="text-sm font-medium text-red-800">
              Por favor corrige los siguientes errores:
            </p>
            <ul className="mt-2 text-sm text-red-600 list-disc list-inside">
              {errors.name && <li>Nombre completo inválido</li>}
              {errors.phone && <li>Teléfono celular inválido</li>}
              {errors.address && <li>Dirección inválida</li>}
              {errors.city && <li>Ciudad inválida</li>}
              {errors.department && <li>Departamento no seleccionado</li>}
              {errors.postal_code && <li>Código postal inválido</li>}
            </ul>
          </div>
        )}

        {/* Form Actions */}
        <div className="flex justify-end space-x-3 pt-4">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              disabled={isSubmitting}
              className="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md transition-colors disabled:opacity-50"
            >
              Cancelar
            </button>
          )}

          <button
            type="submit"
            disabled={isSubmitting || !isValid}
            className={`
              px-6 py-2 rounded-md font-medium transition-colors flex items-center space-x-2
              ${!isValid || isSubmitting
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
              }
            `}
            title={!isValid ? 'Completa todos los campos correctamente para continuar' : ''}
          >
            {isSubmitting && (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            )}
            <span>{isSubmitting ? 'Guardando...' : 'Guardar Dirección'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default AddressForm;