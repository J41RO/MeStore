// ~/frontend/src/schemas/productSchema.ts
// ---------------------------------------------------------------------------------------------
// MESTORE - Schema de Validación para Productos
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: productSchema.ts
// Ruta: ~/frontend/src/schemas/productSchema.ts
// Autor: Jairo
// Fecha de Creación: 2025-08-16
// Última Actualización: 2025-08-16
// Versión: 1.0.0
// Propósito: Schema de validación Yup para crear y editar productos
//            Incluye validaciones completas para todos los campos requeridos
//
// Modificaciones:
// 2025-08-16 - Creación inicial del schema con validaciones completas
//
// ---------------------------------------------------------------------------------------------

/**
 * Schema de validación Yup para productos
 *
 * Valida todos los campos requeridos para crear y editar productos:
 * - name: Nombre del producto (requerido, 3-100 caracteres)
 * - description: Descripción del producto (requerida, 10-500 caracteres)
 * - price: Precio del producto (requerido, número positivo, máx 999999)
 * - stock: Stock disponible (requerido, entero positivo)
 * - category: Categoría del producto (requerida, enum de categorías válidas)
 * - imageUrl: URL de imagen (opcional, formato URL válido)
 */

import * as yup from 'yup';
// import { CreateProductData } from '../types/api.types';

// Enum de categorías válidas
export const PRODUCT_CATEGORIES = [
  'electronics',
  'clothing',
  'books',
  'home',
  'sports',
  'toys',
  'beauty',
  'food',
  'automotive',
  'other',
] as const;

export type ProductCategory = (typeof PRODUCT_CATEGORIES)[number];

// Schema base robusto para validación de productos
const baseProductSchema = {
  // Campos básicos con validaciones avanzadas
  name: yup
    .string()
    .required('Nombre del producto es obligatorio')
    .min(3, 'Nombre debe tener al menos 3 caracteres')
    .max(100, 'Nombre no puede exceder 100 caracteres')
    .matches(/^[a-zA-Z0-9\s\-_áéíóúÁÉÍÓÚñÑ]+$/, 'Nombre contiene caracteres no válidos')
    .trim(),

  description: yup
    .string()
    .required('Descripción es obligatoria')
    .min(10, 'Descripción debe tener al menos 10 caracteres')
    .max(1000, 'Descripción no puede exceder 1000 caracteres')
    .trim(),

  category: yup
    .string()
    .required('Categoría es obligatoria')
    .oneOf(PRODUCT_CATEGORIES, 'Categoría no válida'),

  // Campos de pricing con validaciones complejas
  precio_venta: yup
    .number()
    .required('Precio de venta es obligatorio')
    .positive('Precio debe ser positivo')
    .min(1000, 'Precio mínimo es $1,000 COP')
    .max(50000000, 'Precio máximo es $50,000,000 COP')
    .typeError('Precio debe ser un número válido'),

  precio_costo: yup
    .number()
    .required('Precio de costo es obligatorio')
    .positive('Precio de costo debe ser positivo')
    .typeError('Precio de costo debe ser un número válido')
    .test('cost-validation', 'Precio de costo debe ser menor que precio de venta', 
      function(value) {
        const { precio_venta } = this.parent;
        return !value || !precio_venta || value < precio_venta;
      }),

  stock: yup
    .number()
    .required('Stock inicial es obligatorio')
    .integer('Stock debe ser un número entero')
    .min(0, 'Stock no puede ser negativo')
    .max(100000, 'Stock máximo es 100,000 unidades')
    .typeError('Stock debe ser un número válido'),

  // Campos físicos con validaciones de coherencia
  peso: yup
    .number()
    .required('Peso es obligatorio')
    .positive('Peso debe ser positivo')
    .min(0.01, 'Peso mínimo 0.01 kg')
    .max(1000, 'Peso máximo 1000 kg')
    .typeError('Peso debe ser un número válido'),

  largo: yup
    .number()
    .required('Largo es obligatorio')
    .positive('Largo debe ser positivo')
    .min(1, 'Largo mínimo 1 cm')
    .max(500, 'Largo máximo 500 cm')
    .typeError('Largo debe ser un número válido'),

  ancho: yup
    .number()
    .required('Ancho es obligatorio')
    .positive('Ancho debe ser positivo')
    .min(1, 'Ancho mínimo 1 cm')
    .max(500, 'Ancho máximo 500 cm')
    .typeError('Ancho debe ser un número válido'),

  alto: yup
    .number()
    .required('Alto es obligatorio')
    .positive('Alto debe ser positivo')
    .min(1, 'Alto mínimo 1 cm')
    .max(500, 'Alto máximo 500 cm')
    .typeError('Alto debe ser un número válido'),

  // SKU con validación de formato
  sku: yup
    .string()
    .optional()
    .matches(/^[A-Z0-9\-_]+$/, 'SKU solo puede contener letras mayúsculas, números, guiones y guiones bajos')
    .min(3, 'SKU debe tener al menos 3 caracteres')
    .max(20, 'SKU no puede exceder 20 caracteres'),

  // Tags y características
  tags: yup
    .array()
    .of(yup.string().min(2, 'Tag debe tener al menos 2 caracteres'))
    .max(10, 'Máximo 10 tags permitidos')
    .optional(),

  // Campos de producto específicos
  marca: yup
    .string()
    .optional()
    .min(2, 'Marca debe tener al menos 2 caracteres')
    .max(50, 'Marca no puede exceder 50 caracteres'),

  modelo: yup
    .string()
    .optional()
    .min(1, 'Modelo debe tener al menos 1 caracter')
    .max(50, 'Modelo no puede exceder 50 caracteres'),

  color: yup
    .string()
    .optional()
    .min(3, 'Color debe tener al menos 3 caracteres')
    .max(30, 'Color no puede exceder 30 caracteres'),

  material: yup
    .string()
    .optional()
    .min(3, 'Material debe tener al menos 3 caracteres')
    .max(50, 'Material no puede exceder 50 caracteres'),

  // Campos de inventario avanzados
  stock_minimo: yup
    .number()
    .optional()
    .min(0, 'Stock mínimo no puede ser negativo')
    .max(1000, 'Stock mínimo máximo es 1000')
    .typeError('Stock mínimo debe ser un número válido'),

  stock_maximo: yup
    .number()
    .optional()
    .min(1, 'Stock máximo debe ser al menos 1')
    .max(100000, 'Stock máximo no puede exceder 100,000')
    .typeError('Stock máximo debe ser un número válido')
    .test('stock-range', 'Stock máximo debe ser mayor que stock mínimo',
      function(value) {
        const { stock_minimo } = this.parent;
        return !value || !stock_minimo || value > stock_minimo;
      }),

  // Estado del producto
  estado: yup
    .string()
    .optional()
    .oneOf(['nuevo', 'usado', 'reacondicionado'], 'Estado del producto no válido'),

  // Campos de imagen (cuando se integre completamente)
  imageUrl: yup
    .string()
    .optional()
    .url('Debe ser una URL válida')
    .nullable(),

  // Campos de garantía
  garantia_meses: yup
    .number()
    .optional()
    .min(0, 'Garantía no puede ser negativa')
    .max(120, 'Garantía máxima es 120 meses (10 años)')
    .integer('Garantía debe ser un número entero de meses')
    .typeError('Garantía debe ser un número válido'),

  // Validación compleja de dimensiones vs peso (densidad razonable)
  _dimensionsWeight: yup
    .mixed()
    .test('dimensions-weight-coherence', 'Las dimensiones y peso no son coherentes',
      function() {
        const { largo, ancho, alto, peso } = this.parent;
        if (!largo || !ancho || !alto || !peso) return true;
        
        const volumen = largo * ancho * alto; // cm³
        const densidad = peso / (volumen / 1000000); // kg/m³
        
        // Rango razonable de densidad: 0.1 a 10000 kg/m³
        return densidad >= 0.1 && densidad <= 10000;
      }),
};

// Schema para crear productos (todos los campos requeridos)
export const createProductSchema = yup.object(baseProductSchema);

// Schema para actualizar productos (campos opcionales excepto los críticos)
export const updateProductSchema = yup.object({
  name: baseProductSchema.name.optional(),
  description: baseProductSchema.description.optional(),
  category: baseProductSchema.category.optional(),
  precio_venta: baseProductSchema.precio_venta.optional(),
  precio_costo: baseProductSchema.precio_costo.optional(),
  stock: baseProductSchema.stock.optional(),
  peso: baseProductSchema.peso.optional(),
  largo: baseProductSchema.largo.optional(),
  ancho: baseProductSchema.ancho.optional(),
  alto: baseProductSchema.alto.optional(),
  sku: baseProductSchema.sku.optional(),
  tags: baseProductSchema.tags.optional(),
  marca: baseProductSchema.marca.optional(),
  modelo: baseProductSchema.modelo.optional(),
  color: baseProductSchema.color.optional(),
  material: baseProductSchema.material.optional(),
  stock_minimo: baseProductSchema.stock_minimo.optional(),
  stock_maximo: baseProductSchema.stock_maximo.optional(),
  estado: baseProductSchema.estado.optional(),
  imageUrl: baseProductSchema.imageUrl.optional(),
  garantia_meses: baseProductSchema.garantia_meses.optional(),
  _dimensionsWeight: baseProductSchema._dimensionsWeight.optional(),
});

// Tipo extendido para los datos del formulario
export interface ProductFormData {
  id?: string;
  name: string;
  description: string;
  category: ProductCategory;
  precio_venta: number;
  precio_costo: number;
  stock: number;
  peso: number;
  largo: number;
  ancho: number;
  alto: number;
  sku?: string;
  tags?: string[];
  marca?: string;
  modelo?: string;
  color?: string;
  material?: string;
  stock_minimo?: number;
  stock_maximo?: number;
  estado?: string;
  imageUrl?: string;
  garantia_meses?: number;
  // Campos calculados
  volumen?: number;
  densidad?: number;
  margen_ganancia?: number;
  _dimensionsWeight?: any;
}

// Valores por defecto para el formulario (mejorados para UX)
export const defaultProductValues: Partial<ProductFormData> = {
  name: '',
  description: '',
  category: undefined,
  precio_venta: 1000, // Valor mínimo aceptable
  precio_costo: 800,  // Precio de costo menor que venta
  stock: 1,           // Stock inicial positivo
  peso: 0.1,          // Peso positivo inicial
  largo: 10,          // Dimensiones básicas
  ancho: 10,
  alto: 5,
  sku: '',
  tags: [],
  marca: '',
  modelo: '',
  color: '',
  material: '',
  stock_minimo: 0,
  stock_maximo: 100,
  estado: 'nuevo',
  imageUrl: '',
  garantia_meses: 0,
};

// Función helper para validar una categoría
export const isValidCategory = (
  category: string
): category is ProductCategory => {
  return PRODUCT_CATEGORIES.includes(category as ProductCategory);
};

// Función helper para obtener las opciones de categoría para el select
export const getCategoryOptions = () => {
  return PRODUCT_CATEGORIES.map(category => ({
    value: category,
    label: category.charAt(0).toUpperCase() + category.slice(1),
  }));
};
