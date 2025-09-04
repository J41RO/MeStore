// ~/frontend/src/services/productBulkService.ts
// ---------------------------------------------------------------------------------------------
// MESTORE - Servicio de Operaciones Bulk para Productos
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: productBulkService.ts
// Ruta: ~/frontend/src/services/productBulkService.ts
// Autor: Jairo
// Fecha de Creación: 2025-08-18
// Última Actualización: 2025-08-18
// Versión: 1.0.0
// Propósito: Servicio para operaciones bulk (masivas) de productos
//            Conecta con endpoints backend /api/v1/products/bulk
//            Manejo de errores HTTP y tipos TypeScript
//
// Modificaciones:
// 2025-08-18 - Implementación inicial con DELETE y PATCH bulk
//
// ---------------------------------------------------------------------------------------------

/**
 * Servicio para operaciones bulk de productos
 *
 * Funciones disponibles:
 * - bulkDeleteProducts: Eliminar múltiples productos
 * - bulkUpdateProductStatus: Actualizar estado de múltiples productos
 * - Manejo de errores HTTP estructurado
 * - Tipos TypeScript completos
 */

import { AxiosResponse } from 'axios';
import { apiClient } from './authInterceptors';

// Tipos para las operaciones bulk
export interface BulkDeleteRequest {
  product_ids: string[];
}

export interface BulkStatusUpdateRequest {
  product_ids: string[];
  status: 'active' | 'inactive' | 'pending' | 'archived';
}

export interface BulkOperationResponse {
  success: boolean;
  message: string;
  affected_count: number;
  errors: Array<{
    type: string;
    message: string;
    product_ids?: string[];
  }>;
}

export interface BulkOperationError {
  message: string;
  statusCode: number;
  errors?: Array<{
    type: string;
    message: string;
    product_ids?: string[];
  }>;
}

/**
 * Eliminar múltiples productos en una sola operación
 *
 * @param productIds - Array de IDs de productos a eliminar
 * @returns Promise con el resultado de la operación
 * @throws BulkOperationError si la operación falla
 */
export const bulkDeleteProducts = async (
  productIds: string[]
): Promise<BulkOperationResponse> => {
  try {
    if (!productIds || productIds.length === 0) {
      throw new Error('La lista de IDs de productos no puede estar vacía');
    }

    if (productIds.length > 100) {
      throw new Error('No se pueden eliminar más de 100 productos a la vez');
    }

    const request: BulkDeleteRequest = {
      product_ids: productIds,
    };

    const response: AxiosResponse<BulkOperationResponse> =
      await apiClient.delete('/api/v1/products/bulk', { data: request });

    return response.data;
  } catch (error: any) {
    // Transformar error para la UI
    const bulkError: BulkOperationError = {
      message: 'Error al eliminar productos',
      statusCode: error.response?.status || 500,
      errors: error.response?.data?.errors || [],
    };

    if (error.response?.data?.message) {
      bulkError.message = error.response.data.message;
    } else if (error.message) {
      bulkError.message = error.message;
    }

    throw bulkError;
  }
};

/**
 * Actualizar estado de múltiples productos en una sola operación
 *
 * @param productIds - Array de IDs de productos a actualizar
 * @param status - Nuevo estado para los productos
 * @returns Promise con el resultado de la operación
 * @throws BulkOperationError si la operación falla
 */
export const bulkUpdateProductStatus = async (
  productIds: string[],
  status: 'active' | 'inactive' | 'pending' | 'archived'
): Promise<BulkOperationResponse> => {
  try {
    if (!productIds || productIds.length === 0) {
      throw new Error('La lista de IDs de productos no puede estar vacía');
    }

    if (productIds.length > 100) {
      throw new Error('No se pueden actualizar más de 100 productos a la vez');
    }

    const validStatuses = ['active', 'inactive', 'pending', 'archived'];
    if (!validStatuses.includes(status)) {
      throw new Error(
        `Estado inválido: ${status}. Estados válidos: ${validStatuses.join(', ')}`
      );
    }

    const request: BulkStatusUpdateRequest = {
      product_ids: productIds,
      status,
    };

    const response: AxiosResponse<BulkOperationResponse> =
      await apiClient.patch('/api/v1/products/bulk/status', request);

    return response.data;
  } catch (error: any) {
    // Transformar error para la UI
    const bulkError: BulkOperationError = {
      message: 'Error al actualizar estado de productos',
      statusCode: error.response?.status || 500,
      errors: error.response?.data?.errors || [],
    };

    if (error.response?.data?.message) {
      bulkError.message = error.response.data.message;
    } else if (error.message) {
      bulkError.message = error.message;
    }

    throw bulkError;
  }
};

/**
 * Validar lista de IDs de productos
 *
 * @param productIds - Array de IDs a validar
 * @returns true si todos los IDs son válidos
 * @throws Error si algún ID es inválido
 */
export const validateProductIds = (productIds: string[]): boolean => {
  if (!Array.isArray(productIds)) {
    throw new Error('productIds debe ser un array');
  }

  if (productIds.length === 0) {
    throw new Error('Debe proporcionar al menos un ID de producto');
  }

  if (productIds.length > 100) {
    throw new Error('No se pueden procesar más de 100 productos a la vez');
  }

  // Validar formato UUID básico
  const uuidRegex =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

  for (const id of productIds) {
    if (typeof id !== 'string' || !id.trim()) {
      throw new Error(`ID de producto inválido: ${id}`);
    }

    if (!uuidRegex.test(id)) {
      throw new Error(`Formato de ID inválido: ${id}. Debe ser un UUID válido`);
    }
  }

  return true;
};

/**
 * Obtener mensaje de error legible para el usuario
 *
 * @param error - Error de la operación bulk
 * @returns Mensaje legible para mostrar al usuario
 */
export const getBulkErrorMessage = (error: BulkOperationError): string => {
  if (error.statusCode === 400) {
    return 'Datos inválidos en la solicitud. Verifica los IDs de productos.';
  }

  if (error.statusCode === 401) {
    return 'No tienes autorización para realizar esta operación.';
  }

  if (error.statusCode === 404) {
    return 'Algunos productos no fueron encontrados.';
  }

  if (error.statusCode >= 500) {
    return 'Error del servidor. Intenta nuevamente en unos momentos.';
  }

  return error.message || 'Error desconocido en la operación.';
};

// Export por defecto del servicio completo
export default {
  bulkDeleteProducts,
  bulkUpdateProductStatus,
  validateProductIds,
  getBulkErrorMessage,
};
