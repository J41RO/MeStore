// ~/frontend/src/services/productValidationService.ts
// ---------------------------------------------------------------------------------------------
// MESTORE - Servicio de validación de productos con backend
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

import { ProductFormData } from '../schemas/productSchema';

interface ValidationError {
  field: string;
  message: string;
}

interface ValidationWarning {
  field: string;
  message: string;
}

interface ValidationSuggestion {
  field: string;
  message: string;
}

interface ValidationResponse {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  suggestions: ValidationSuggestion[];
}

interface NameCheckResponse {
  available: boolean;
  name: string;
  similar_count: number;
}

class ProductValidationService {
  private baseURL = '/api/v1/productos';

  /**
   * Obtener token de autenticación del localStorage
   */
  private getAuthToken(): string | null {
    return localStorage.getItem('authToken') || localStorage.getItem('token');
  }

  /**
   * Validar datos completos del producto en el backend
   */
  async validateProductData(productData: Partial<ProductFormData>): Promise<ValidationResponse> {
    try {
      const token = this.getAuthToken();
      const response = await fetch(`${this.baseURL}/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(productData)
      });

      if (!response.ok) {
        throw new Error(`Validation request failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error validating product data:', error);
      // Return a default validation response on error
      return {
        valid: true,
        errors: [],
        warnings: [],
        suggestions: []
      };
    }
  }

  /**
   * Verificar disponibilidad de nombre de producto
   */
  async checkNameAvailability(name: string): Promise<NameCheckResponse> {
    try {
      const token = this.getAuthToken();
      const response = await fetch(
        `${this.baseURL}/check-name?name=${encodeURIComponent(name)}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Name check failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error checking name availability:', error);
      // Return a default response on error
      return {
        available: true,
        name,
        similar_count: 0
      };
    }
  }

  /**
   * Validar coherencia de precio vs costo
   */
  validatePriceCoherence(precioVenta: number, precioCosto: number): {
    valid: boolean;
    margen: number;
    message?: string;
  } {
    if (!precioVenta || !precioCosto || precioVenta <= 0 || precioCosto <= 0) {
      return { valid: false, margen: 0, message: 'Precios inválidos' };
    }

    if (precioCosto >= precioVenta) {
      return { 
        valid: false, 
        margen: 0, 
        message: 'El precio de costo debe ser menor al precio de venta' 
      };
    }

    const margen = ((precioVenta - precioCosto) / precioVenta) * 100;

    if (margen < 10) {
      return { 
        valid: false, 
        margen, 
        message: `Margen muy bajo (${margen.toFixed(1)}%). Recomendado: 10-80%` 
      };
    }

    if (margen > 80) {
      return { 
        valid: true, // Still valid, but warning
        margen, 
        message: `Margen muy alto (${margen.toFixed(1)}%). Podría afectar competitividad` 
      };
    }

    return { valid: true, margen };
  }

  /**
   * Validar coherencia de dimensiones vs peso (densidad)
   */
  validateDimensionsWeight(
    largo: number, 
    ancho: number, 
    alto: number, 
    peso: number
  ): {
    valid: boolean;
    volumen: number;
    densidad: number;
    message?: string;
  } {
    if (!largo || !ancho || !alto || !peso || 
        largo <= 0 || ancho <= 0 || alto <= 0 || peso <= 0) {
      return { 
        valid: false, 
        volumen: 0, 
        densidad: 0, 
        message: 'Dimensiones o peso inválidos' 
      };
    }

    const volumen = largo * ancho * alto; // cm³
    const densidad = peso / (volumen / 1000000); // kg/m³

    // Rango razonable de densidad: 0.1 a 10000 kg/m³
    if (densidad < 0.1) {
      return {
        valid: false,
        volumen,
        densidad,
        message: 'El producto parece demasiado ligero para sus dimensiones'
      };
    }

    if (densidad > 10000) {
      return {
        valid: false,
        volumen,
        densidad,
        message: 'El producto parece demasiado pesado para sus dimensiones'
      };
    }

    return { valid: true, volumen, densidad };
  }

  /**
   * Generar sugerencias de optimización
   */
  generateOptimizationSuggestions(productData: Partial<ProductFormData>): ValidationSuggestion[] {
    const suggestions: ValidationSuggestion[] = [];

    // Sugerencias de descripción
    if (productData.description && productData.description.length < 50) {
      suggestions.push({
        field: 'description',
        message: 'Una descripción más detallada puede aumentar las ventas'
      });
    }

    // Sugerencias de SKU
    if (!productData.sku || productData.sku.trim() === '') {
      suggestions.push({
        field: 'sku',
        message: 'Agregar un SKU ayuda con el control de inventario'
      });
    }

    // Sugerencias de marca
    if (!productData.marca || productData.marca.trim() === '') {
      suggestions.push({
        field: 'marca',
        message: 'Especificar la marca puede aumentar la confianza del cliente'
      });
    }

    // Sugerencias de garantía
    if (!productData.garantia_meses || productData.garantia_meses === 0) {
      suggestions.push({
        field: 'garantia_meses',
        message: 'Ofrecer garantía puede ser un diferenciador competitivo'
      });
    }

    return suggestions;
  }
}

// Crear instancia del servicio
export const productValidationService = new ProductValidationService();

// Helper functions para uso directo en componentes
export const validateProductData = (productData: Partial<ProductFormData>) =>
  productValidationService.validateProductData(productData);

export const checkNameAvailability = (name: string) =>
  productValidationService.checkNameAvailability(name);

export const validatePriceCoherence = (precioVenta: number, precioCosto: number) =>
  productValidationService.validatePriceCoherence(precioVenta, precioCosto);

export const validateDimensionsWeight = (largo: number, ancho: number, alto: number, peso: number) =>
  productValidationService.validateDimensionsWeight(largo, ancho, alto, peso);

export const generateOptimizationSuggestions = (productData: Partial<ProductFormData>) =>
  productValidationService.generateOptimizationSuggestions(productData);

// Types exports
export type { 
  ValidationResponse, 
  ValidationError, 
  ValidationWarning, 
  ValidationSuggestion,
  NameCheckResponse 
};