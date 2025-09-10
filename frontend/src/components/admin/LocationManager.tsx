/**
 * LocationManager - Componente para gestión de ubicaciones de inventario
 * 
 * Permite asignar y reasignar ubicaciones de productos en el almacén
 * con validaciones de capacidad y disponibilidad.
 */

import React, { useState, useCallback } from 'react';
import { 
  MapPin, 
  Package, 
  AlertTriangle, 
  CheckCircle, 
  Save, 
  X,
  Move,
  Eye,
  Info
} from 'lucide-react';
import { InventoryItem, LocationInfo, LocationZone } from '../../types/inventory.types';

// Interfaces específicas para LocationManager
// LocationUpdateRequest interface removed - not used in component

interface LocationManagerProps {
  inventoryItem: InventoryItem;
  onLocationUpdate: (itemId: string, newLocation: LocationInfo, observaciones?: string) => Promise<boolean>;
  availableLocations: LocationInfo[];
  isLoading?: boolean;
  onClose?: () => void;
}

interface ValidationError {
  field: string;
  message: string;
}

export const LocationManager: React.FC<LocationManagerProps> = ({
  inventoryItem,
  onLocationUpdate,
  availableLocations,
  isLoading = false,
  onClose
}) => {
  // Estados del componente
  const [selectedLocation, setSelectedLocation] = useState<LocationInfo>({
    zone: inventoryItem.location.zone,
    aisle: inventoryItem.location.aisle,
    shelf: inventoryItem.location.shelf,
    position: inventoryItem.location.position
  });
  const [observaciones, setObservaciones] = useState('');
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);

  // Validar nueva ubicación
  const validateLocation = useCallback((location: LocationInfo): ValidationError[] => {
    const errors: ValidationError[] = [];

    // Validar zona
    if (!location.zone) {
      errors.push({ field: 'zone', message: 'La zona es requerida' });
    }

    // Validar aisle (pasillo)
    if (!location.aisle || location.aisle.trim().length === 0) {
      errors.push({ field: 'aisle', message: 'El pasillo es requerido' });
    } else if (!/^[A-Z0-9\-]{1,10}$/.test(location.aisle)) {
      errors.push({ field: 'aisle', message: 'El pasillo debe contener solo letras, números y guiones (máx. 10 caracteres)' });
    }

    // Validar shelf (estante)
    if (!location.shelf || location.shelf.trim().length === 0) {
      errors.push({ field: 'shelf', message: 'El estante es requerido' });
    } else if (!/^[A-Z0-9\-]{1,20}$/.test(location.shelf)) {
      errors.push({ field: 'shelf', message: 'El estante debe contener solo letras, números y guiones (máx. 20 caracteres)' });
    }

    // Validar position (posición)
    if (!location.position || location.position.trim().length === 0) {
      errors.push({ field: 'position', message: 'La posición es requerida' });
    } else if (!/^[A-Z0-9\-]{1,20}$/.test(location.position)) {
      errors.push({ field: 'position', message: 'La posición debe contener solo letras, números y guiones (máx. 20 caracteres)' });
    }

    // Verificar si la ubicación ya está ocupada
    const isCurrentLocation = 
      location.zone === inventoryItem.location.zone &&
      location.aisle === inventoryItem.location.aisle &&
      location.shelf === inventoryItem.location.shelf &&
      location.position === inventoryItem.location.position;

    if (!isCurrentLocation && !isLocationAvailable(location)) {
      errors.push({ field: 'location', message: 'Esta ubicación ya está ocupada por otro producto' });
    }

    return errors;
  }, [inventoryItem.location, availableLocations]);

  // Verificar si una ubicación está disponible
  const isLocationAvailable = useCallback((location: LocationInfo): boolean => {
    return availableLocations.some(available => 
      available.zone === location.zone &&
      available.aisle === location.aisle &&
      available.shelf === location.shelf &&
      available.position === location.position
    );
  }, [availableLocations]);

  // Manejar cambios en la ubicación
  const handleLocationChange = useCallback((field: keyof LocationInfo, value: string) => {
    const newLocation = { ...selectedLocation, [field]: value.toUpperCase().trim() };
    setSelectedLocation(newLocation);
    
    // Limpiar errores de validación para este campo
    setValidationErrors(prev => prev.filter(error => error.field !== field && error.field !== 'location'));
  }, [selectedLocation]);

  // Obtener error de validación para un campo
  const getFieldError = useCallback((field: string): string | null => {
    const error = validationErrors.find(err => err.field === field);
    return error ? error.message : null;
  }, [validationErrors]);

  // Verificar si la ubicación ha cambiado
  const hasLocationChanged = useCallback((): boolean => {
    return (
      selectedLocation.zone !== inventoryItem.location.zone ||
      selectedLocation.aisle !== inventoryItem.location.aisle ||
      selectedLocation.shelf !== inventoryItem.location.shelf ||
      selectedLocation.position !== inventoryItem.location.position
    );
  }, [selectedLocation, inventoryItem.location]);

  // Manejar envío del formulario
  const handleSubmit = useCallback(async () => {
    const errors = validateLocation(selectedLocation);
    setValidationErrors(errors);

    if (errors.length > 0) {
      return;
    }

    if (!hasLocationChanged() && !observaciones.trim()) {
      setValidationErrors([{ field: 'general', message: 'No se han realizado cambios' }]);
      return;
    }

    setShowConfirmation(true);
  }, [selectedLocation, validateLocation, hasLocationChanged, observaciones]);

  // Confirmar actualización
  const confirmUpdate = useCallback(async () => {
    setIsSubmitting(true);
    
    try {
      const success = await onLocationUpdate(
        inventoryItem.id,
        selectedLocation,
        observaciones.trim() || undefined
      );

      if (success) {
        onClose?.();
      } else {
        setValidationErrors([{ field: 'general', message: 'Error al actualizar la ubicación' }]);
      }
    } catch (error) {
      setValidationErrors([{ field: 'general', message: 'Error inesperado al actualizar la ubicación' }]);
    } finally {
      setIsSubmitting(false);
      setShowConfirmation(false);
    }
  }, [selectedLocation, observaciones, inventoryItem.id, onLocationUpdate, onClose]);

  // Formatear ubicación completa
  const formatLocation = useCallback((location: LocationInfo): string => {
    return `${location.zone}-${location.aisle}-${location.shelf}-${location.position}`;
  }, []);

  return (
    <div className="location-manager bg-white rounded-lg shadow-lg p-6 max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 bg-blue-100 rounded-lg">
            <Move className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Gestión de Ubicación</h2>
            <p className="text-sm text-gray-600">Cambiar ubicación física del producto</p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="flex items-center justify-center w-8 h-8 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            disabled={isSubmitting}
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Información del producto */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <div className="flex items-center gap-3 mb-3">
          <Package className="w-5 h-5 text-gray-600" />
          <div>
            <h3 className="font-medium text-gray-900">{inventoryItem.productName}</h3>
            <p className="text-sm text-gray-600">SKU: {inventoryItem.sku}</p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Ubicación actual:</span>
            <span className="ml-2 font-medium">{formatLocation(inventoryItem.location)}</span>
          </div>
          <div>
            <span className="text-gray-600">Cantidad:</span>
            <span className="ml-2 font-medium">{inventoryItem.quantity}</span>
          </div>
        </div>
      </div>

      {/* Formulario de nueva ubicación */}
      <div className="space-y-4 mb-6">
        <h4 className="font-medium text-gray-900 flex items-center gap-2">
          <MapPin className="w-4 h-4" />
          Nueva Ubicación
        </h4>

        {/* Zona */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Zona del Almacén
          </label>
          <select
            value={selectedLocation.zone}
            onChange={(e) => handleLocationChange('zone', e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              getFieldError('zone') ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'
            }`}
            disabled={isSubmitting || isLoading}
          >
            <option value="">Seleccionar zona...</option>
            {Object.values(LocationZone).map(zone => (
              <option key={zone} value={zone}>
                {zone.replace('_', ' ').toUpperCase()}
              </option>
            ))}
          </select>
          {getFieldError('zone') && (
            <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
              <AlertTriangle className="w-3 h-3" />
              {getFieldError('zone')}
            </p>
          )}
        </div>

        {/* Pasillo y Estante */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Pasillo
            </label>
            <input
              type="text"
              value={selectedLocation.aisle}
              onChange={(e) => handleLocationChange('aisle', e.target.value)}
              placeholder="Ej: A1, B2"
              maxLength={10}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                getFieldError('aisle') ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'
              }`}
              disabled={isSubmitting || isLoading}
            />
            {getFieldError('aisle') && (
              <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" />
                {getFieldError('aisle')}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Estante
            </label>
            <input
              type="text"
              value={selectedLocation.shelf}
              onChange={(e) => handleLocationChange('shelf', e.target.value)}
              placeholder="Ej: 01, 02, A-1"
              maxLength={20}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                getFieldError('shelf') ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'
              }`}
              disabled={isSubmitting || isLoading}
            />
            {getFieldError('shelf') && (
              <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" />
                {getFieldError('shelf')}
              </p>
            )}
          </div>
        </div>

        {/* Posición */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Posición
          </label>
          <input
            type="text"
            value={selectedLocation.position}
            onChange={(e) => handleLocationChange('position', e.target.value)}
            placeholder="Ej: 01, A1-01"
            maxLength={20}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              getFieldError('position') ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'
            }`}
            disabled={isSubmitting || isLoading}
          />
          {getFieldError('position') && (
            <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
              <AlertTriangle className="w-3 h-3" />
              {getFieldError('position')}
            </p>
          )}
        </div>

        {/* Observaciones */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Observaciones (Opcional)
          </label>
          <textarea
            value={observaciones}
            onChange={(e) => setObservaciones(e.target.value)}
            placeholder="Motivo del cambio de ubicación..."
            rows={3}
            maxLength={500}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={isSubmitting || isLoading}
          />
          <p className="mt-1 text-xs text-gray-500">
            {observaciones.length}/500 caracteres
          </p>
        </div>

        {/* Vista previa de nueva ubicación */}
        {hasLocationChanged() && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Eye className="w-4 h-4 text-blue-600" />
              <span className="font-medium text-blue-900">Vista Previa del Cambio</span>
            </div>
            <div className="text-sm space-y-1">
              <div>
                <span className="text-gray-600">De:</span>
                <span className="ml-2 font-mono">{formatLocation(inventoryItem.location)}</span>
              </div>
              <div>
                <span className="text-gray-600">A:</span>
                <span className="ml-2 font-mono">{formatLocation(selectedLocation)}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Errores generales */}
      {getFieldError('general') && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center gap-2 text-red-700">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-sm font-medium">{getFieldError('general')}</span>
          </div>
        </div>
      )}

      {getFieldError('location') && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center gap-2 text-red-700">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-sm font-medium">{getFieldError('location')}</span>
          </div>
        </div>
      )}

      {/* Botones de acción */}
      <div className="flex items-center justify-end gap-3 pt-4 border-t">
        {onClose && (
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            disabled={isSubmitting}
          >
            Cancelar
          </button>
        )}
        <button
          onClick={handleSubmit}
          disabled={isSubmitting || isLoading || (!hasLocationChanged() && !observaciones.trim())}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg flex items-center gap-2 transition-colors"
        >
          {isSubmitting ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <Save className="w-4 h-4" />
          )}
          {isSubmitting ? 'Guardando...' : 'Actualizar Ubicación'}
        </button>
      </div>

      {/* Modal de confirmación */}
      {showConfirmation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex items-center justify-center w-10 h-10 bg-blue-100 rounded-lg">
                <Info className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Confirmar Cambio de Ubicación</h3>
                <p className="text-sm text-gray-600">Esta acción se registrará en el historial</p>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 mb-4 space-y-2 text-sm">
              <div>
                <span className="text-gray-600">Producto:</span>
                <span className="ml-2 font-medium">{inventoryItem.productName}</span>
              </div>
              <div>
                <span className="text-gray-600">De:</span>
                <span className="ml-2 font-mono">{formatLocation(inventoryItem.location)}</span>
              </div>
              <div>
                <span className="text-gray-600">A:</span>
                <span className="ml-2 font-mono">{formatLocation(selectedLocation)}</span>
              </div>
              {observaciones && (
                <div>
                  <span className="text-gray-600">Observaciones:</span>
                  <p className="mt-1 text-gray-800">{observaciones}</p>
                </div>
              )}
            </div>

            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setShowConfirmation(false)}
                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                disabled={isSubmitting}
              >
                Cancelar
              </button>
              <button
                onClick={confirmUpdate}
                disabled={isSubmitting}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg flex items-center gap-2 transition-colors"
              >
                {isSubmitting ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <CheckCircle className="w-4 h-4" />
                )}
                {isSubmitting ? 'Actualizando...' : 'Confirmar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LocationManager;