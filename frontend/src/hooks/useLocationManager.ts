/**
 * Hook personalizado para gestión de ubicaciones de inventario
 * 
 * Proporciona funciones para validar, actualizar y gestionar ubicaciones
 * de productos en el almacén con manejo de errores y estados de carga.
 */

import { useState, useCallback } from 'react';
import { InventoryItem, LocationInfo, InventoryStatus } from '../types/inventory.types';

// Interfaces para el hook
interface LocationValidationResult {
  isValid: boolean;
  errors: string[];
}

interface LocationUpdateResult {
  success: boolean;
  error?: string;
  updatedItem?: InventoryItem;
}

interface UseLocationManagerReturn {
  // Estados
  isLoading: boolean;
  error: string | null;
  
  // Funciones de validación
  validateLocationFormat: (location: LocationInfo) => LocationValidationResult;
  validateLocationAvailability: (location: LocationInfo, currentItemId: string) => Promise<LocationValidationResult>;
  
  // Funciones de gestión
  updateItemLocation: (itemId: string, newLocation: LocationInfo, observaciones?: string) => Promise<LocationUpdateResult>;
  getAvailableLocations: (zone?: string) => Promise<LocationInfo[]>;
  
  // Utilidades
  formatLocationCode: (location: LocationInfo) => string;
  clearError: () => void;
}

export const useLocationManager = (): UseLocationManagerReturn => {
  // Estados del hook
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Obtener token de autenticación
  const getAuthToken = useCallback((): string | null => {
    return localStorage.getItem('access_token') || localStorage.getItem('token');
  }, []);

  // Validar formato de ubicación (cliente)
  const validateLocationFormat = useCallback((location: LocationInfo): LocationValidationResult => {
    const errors: string[] = [];

    // Validar zona
    if (!location.zone || !location.zone.trim()) {
      errors.push('La zona es requerida');
    }

    // Validar aisle (pasillo)
    if (!location.aisle || !location.aisle.trim()) {
      errors.push('El pasillo es requerido');
    } else if (!/^[A-Z0-9\-]{1,10}$/i.test(location.aisle)) {
      errors.push('El pasillo debe contener solo letras, números y guiones (máx. 10 caracteres)');
    }

    // Validar shelf (estante)
    if (!location.shelf || !location.shelf.trim()) {
      errors.push('El estante es requerido');
    } else if (!/^[A-Z0-9\-]{1,20}$/i.test(location.shelf)) {
      errors.push('El estante debe contener solo letras, números y guiones (máx. 20 caracteres)');
    }

    // Validar position (posición)
    if (!location.position || !location.position.trim()) {
      errors.push('La posición es requerida');
    } else if (!/^[A-Z0-9\-]{1,20}$/i.test(location.position)) {
      errors.push('La posición debe contener solo letras, números y guiones (máx. 20 caracteres)');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }, []);

  // Validar disponibilidad de ubicación (servidor)
  const validateLocationAvailability = useCallback(async (
    location: LocationInfo, 
    currentItemId: string
  ): Promise<LocationValidationResult> => {
    try {
      setIsLoading(true);
      setError(null);

      const token = getAuthToken();
      if (!token) {
        return {
          isValid: false,
          errors: ['Token de autenticación no encontrado']
        };
      }

      // Llamar al endpoint de validación del backend
      const response = await fetch('/api/v1/inventory/validate-location', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'User-Agent': 'Mozilla/5.0 (compatible; API-Client/1.0)'
        },
        body: JSON.stringify({
          zona: location.zone.toUpperCase(),
          estante: location.aisle.toUpperCase(),
          posicion: location.position.toUpperCase(),
          exclude_inventory_id: currentItemId
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          isValid: false,
          errors: [errorData.detail || 'Error al validar la ubicación']
        };
      }

      const validationResult = await response.json();
      
      return {
        isValid: validationResult.available,
        errors: validationResult.available ? [] : [validationResult.error]
      };

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error de conexión';
      setError(errorMessage);
      
      return {
        isValid: false,
        errors: [errorMessage]
      };
    } finally {
      setIsLoading(false);
    }
  }, [getAuthToken]);

  // Actualizar ubicación de un item
  const updateItemLocation = useCallback(async (
    itemId: string,
    newLocation: LocationInfo,
    observaciones?: string
  ): Promise<LocationUpdateResult> => {
    try {
      setIsLoading(true);
      setError(null);

      const token = getAuthToken();
      if (!token) {
        return {
          success: false,
          error: 'Token de autenticación no encontrado'
        };
      }

      // Validar formato antes de enviar
      const formatValidation = validateLocationFormat(newLocation);
      if (!formatValidation.isValid) {
        return {
          success: false,
          error: formatValidation.errors.join(', ')
        };
      }

      // Llamar al endpoint de actualización
      const response = await fetch(`/api/v1/inventory/${itemId}/location`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'User-Agent': 'Mozilla/5.0 (compatible; API-Client/1.0)'
        },
        body: JSON.stringify({
          zona: newLocation.zone.toUpperCase(),
          estante: newLocation.aisle.toUpperCase(),
          posicion: newLocation.position.toUpperCase(),
          observaciones: observaciones || undefined
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.detail || 'Error al actualizar la ubicación'
        };
      }

      const updatedInventory = await response.json();
      
      // Convertir la respuesta del backend al formato del frontend
      const updatedItem: InventoryItem = {
        id: updatedInventory.id,
        productId: updatedInventory.product_id,
        productName: updatedInventory.product_name || 'Producto',
        sku: updatedInventory.sku || '',
        quantity: updatedInventory.cantidad,
        minStock: 0, // No viene del backend
        maxStock: 0, // No viene del backend
        status: updatedInventory.status === 'DISPONIBLE' ? InventoryStatus.IN_STOCK : InventoryStatus.OUT_OF_STOCK,
        location: {
          zone: updatedInventory.zona,
          aisle: updatedInventory.estante,
          shelf: updatedInventory.estante, // Mapeo para compatibilidad
          position: updatedInventory.posicion
        },
        lastUpdated: new Date(updatedInventory.updated_at),
        cost: 0 // No viene del backend
      };

      return {
        success: true,
        updatedItem
      };

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error de conexión';
      setError(errorMessage);
      
      return {
        success: false,
        error: errorMessage
      };
    } finally {
      setIsLoading(false);
    }
  }, [getAuthToken, validateLocationFormat]);

  // Obtener ubicaciones disponibles
  const getAvailableLocations = useCallback(async (zone?: string): Promise<LocationInfo[]> => {
    try {
      setIsLoading(true);
      setError(null);

      const token = getAuthToken();
      if (!token) {
        throw new Error('Token de autenticación no encontrado');
      }

      const url = zone 
        ? `/api/v1/inventory/available-locations?zone=${encodeURIComponent(zone)}`
        : '/api/v1/inventory/available-locations';

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'User-Agent': 'Mozilla/5.0 (compatible; API-Client/1.0)'
        }
      });

      if (!response.ok) {
        throw new Error('Error al obtener ubicaciones disponibles');
      }

      const locations = await response.json();
      
      // Convertir formato del backend al frontend
      return locations.map((loc: any) => ({
        zone: loc.zone,
        aisle: loc.aisle,
        shelf: loc.shelf,
        position: loc.position
      }));

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error de conexión';
      setError(errorMessage);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, [getAuthToken]);

  // Formatear código de ubicación
  const formatLocationCode = useCallback((location: LocationInfo): string => {
    return `${location.zone}-${location.aisle}-${location.shelf}-${location.position}`;
  }, []);

  // Limpiar error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    // Estados
    isLoading,
    error,
    
    // Funciones de validación
    validateLocationFormat,
    validateLocationAvailability,
    
    // Funciones de gestión
    updateItemLocation,
    getAvailableLocations,
    
    // Utilidades
    formatLocationCode,
    clearError
  };
};