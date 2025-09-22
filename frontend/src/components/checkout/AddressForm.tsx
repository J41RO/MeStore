import React, { useState } from 'react';
import { ShippingAddress, useCheckoutStore } from '../../stores/checkoutStore';

interface AddressFormProps {
  address?: ShippingAddress;
  onSubmit: (address: ShippingAddress) => void;
  onCancel?: () => void;
}

const AddressForm: React.FC<AddressFormProps> = ({ address, onSubmit, onCancel }) => {
  const { addSavedAddress, setValidationErrors, validation_errors } = useCheckoutStore();

  const [formData, setFormData] = useState<Partial<ShippingAddress>>({
    name: address?.name || '',
    phone: address?.phone || '',
    address: address?.address || '',
    city: address?.city || '',
    department: address?.department || '',
    postal_code: address?.postal_code || '',
    additional_info: address?.additional_info || '',
    is_default: address?.is_default || false
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Colombian departments
  const colombianDepartments = [
    'Amazonas', 'Antioquia', 'Arauca', 'Atlántico', 'Bolívar', 'Boyacá',
    'Caldas', 'Caquetá', 'Casanare', 'Cauca', 'Cesar', 'Chocó',
    'Córdoba', 'Cundinamarca', 'Guainía', 'Guaviare', 'Huila',
    'La Guajira', 'Magdalena', 'Meta', 'Nariño', 'Norte de Santander',
    'Putumayo', 'Quindío', 'Risaralda', 'San Andrés y Providencia',
    'Santander', 'Sucre', 'Tolima', 'Valle del Cauca', 'Vaupés', 'Vichada'
  ];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;

    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    // Clear validation error for this field
    if (validation_errors[name]) {
      setValidationErrors({
        ...validation_errors,
        [name]: ''
      });
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.name?.trim()) {
      errors.name = 'El nombre completo es requerido';
    }

    if (!formData.phone?.trim()) {
      errors.phone = 'El número de teléfono es requerido';
    } else if (!/^[\d\s\-\+\(\)]{7,15}$/.test(formData.phone.trim())) {
      errors.phone = 'Formato de teléfono inválido';
    }

    if (!formData.address?.trim()) {
      errors.address = 'La dirección es requerida';
    }

    if (!formData.city?.trim()) {
      errors.city = 'La ciudad es requerida';
    }

    if (formData.postal_code && !/^\d{5,6}$/.test(formData.postal_code.trim())) {
      errors.postal_code = 'Código postal inválido (5-6 dígitos)';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const newAddress: ShippingAddress = {
        id: address?.id || Date.now().toString(),
        name: formData.name!.trim(),
        phone: formData.phone!.trim(),
        address: formData.address!.trim(),
        city: formData.city!.trim(),
        department: formData.department || '',
        postal_code: formData.postal_code?.trim() || '',
        additional_info: formData.additional_info?.trim() || '',
        is_default: formData.is_default || false
      };

      // Save to store if it's a new address
      if (!address) {
        addSavedAddress(newAddress);
      }

      onSubmit(newAddress);
    } catch (error) {
      console.error('Error saving address:', error);
      setValidationErrors({
        general: 'Error al guardar la dirección. Inténtalo de nuevo.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-gray-50 rounded-lg p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* General error */}
        {validation_errors.general && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3">
            <p className="text-sm text-red-600">{validation_errors.general}</p>
          </div>
        )}

        {/* Name */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            Nombre completo *
          </label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            placeholder="Ej: Juan Pérez"
            className={`
              w-full px-3 py-2 border rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500
              ${validation_errors.name ? 'border-red-300' : 'border-gray-300'}
            `}
          />
          {validation_errors.name && (
            <p className="mt-1 text-sm text-red-600">{validation_errors.name}</p>
          )}
        </div>

        {/* Phone */}
        <div>
          <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
            Número de teléfono *
          </label>
          <input
            type="tel"
            id="phone"
            name="phone"
            value={formData.phone}
            onChange={handleInputChange}
            placeholder="Ej: 3001234567"
            className={`
              w-full px-3 py-2 border rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500
              ${validation_errors.phone ? 'border-red-300' : 'border-gray-300'}
            `}
          />
          {validation_errors.phone && (
            <p className="mt-1 text-sm text-red-600">{validation_errors.phone}</p>
          )}
        </div>

        {/* Address */}
        <div>
          <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-1">
            Dirección completa *
          </label>
          <input
            type="text"
            id="address"
            name="address"
            value={formData.address}
            onChange={handleInputChange}
            placeholder="Ej: Carrera 15 # 93-47, Apartamento 501"
            className={`
              w-full px-3 py-2 border rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500
              ${validation_errors.address ? 'border-red-300' : 'border-gray-300'}
            `}
          />
          {validation_errors.address && (
            <p className="mt-1 text-sm text-red-600">{validation_errors.address}</p>
          )}
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
              name="city"
              value={formData.city}
              onChange={handleInputChange}
              placeholder="Ej: Bogotá"
              className={`
                w-full px-3 py-2 border rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500
                ${validation_errors.city ? 'border-red-300' : 'border-gray-300'}
              `}
            />
            {validation_errors.city && (
              <p className="mt-1 text-sm text-red-600">{validation_errors.city}</p>
            )}
          </div>

          <div>
            <label htmlFor="department" className="block text-sm font-medium text-gray-700 mb-1">
              Departamento
            </label>
            <select
              id="department"
              name="department"
              value={formData.department}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Seleccionar departamento</option>
              {colombianDepartments.map(dept => (
                <option key={dept} value={dept}>{dept}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Postal Code */}
        <div>
          <label htmlFor="postal_code" className="block text-sm font-medium text-gray-700 mb-1">
            Código postal (opcional)
          </label>
          <input
            type="text"
            id="postal_code"
            name="postal_code"
            value={formData.postal_code}
            onChange={handleInputChange}
            placeholder="Ej: 110111"
            className={`
              w-full px-3 py-2 border rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500
              ${validation_errors.postal_code ? 'border-red-300' : 'border-gray-300'}
            `}
          />
          {validation_errors.postal_code && (
            <p className="mt-1 text-sm text-red-600">{validation_errors.postal_code}</p>
          )}
        </div>

        {/* Additional Info */}
        <div>
          <label htmlFor="additional_info" className="block text-sm font-medium text-gray-700 mb-1">
            Información adicional (opcional)
          </label>
          <textarea
            id="additional_info"
            name="additional_info"
            rows={2}
            value={formData.additional_info}
            onChange={handleInputChange}
            placeholder="Ej: Portería 24/7, casa de color blanco, segundo piso..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Default Address */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="is_default"
            name="is_default"
            checked={formData.is_default}
            onChange={handleInputChange}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="is_default" className="ml-2 block text-sm text-gray-900">
            Establecer como dirección predeterminada
          </label>
        </div>

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
            disabled={isSubmitting}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors disabled:opacity-50 flex items-center space-x-2"
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