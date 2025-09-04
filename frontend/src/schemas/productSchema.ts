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
import { CreateProductData } from '../types/api.types';

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

// Schema base para validación de productos
const baseProductSchema = {
  name: yup
    .string()
    .required('El nombre del producto es requerido')
    .min(3, 'El nombre debe tener al menos 3 caracteres')
    .max(100, 'El nombre no puede exceder 100 caracteres')
    .trim(),

  description: yup
    .string()
    .required('La descripción del producto es requerida')
    .min(10, 'La descripción debe tener al menos 10 caracteres')
    .max(500, 'La descripción no puede exceder 500 caracteres')
    .trim(),

  price: yup
    .number()
    .required('El precio es requerido')
    .positive('El precio debe ser un número positivo')
    .max(999999, 'El precio no puede exceder 99,999')
    .typeError('El precio debe ser un número válido'),

  stock: yup
    .number()
    .required('El stock es requerido')
    .integer('El stock debe ser un número entero')
    .min(0, 'El stock no puede ser negativo')
    .typeError('El stock debe ser un número válido'),

  category: yup
    .string()
    .required('La categoría es requerida')
    .oneOf(PRODUCT_CATEGORIES, 'Selecciona una categoría válida'),

  imageUrl: yup.string().url('Debe ser una URL válida').optional().nullable(),
};

// Schema para crear productos (todos los campos requeridos)
export const createProductSchema = yup.object(baseProductSchema);

// Schema para actualizar productos (campos opcionales)
export const updateProductSchema = yup.object({
  name: baseProductSchema.name.optional(),
  description: baseProductSchema.description.optional(),
  price: baseProductSchema.price.optional(),
  stock: baseProductSchema.stock.optional(),
  category: baseProductSchema.category.optional(),
  imageUrl: baseProductSchema.imageUrl.optional(),
});

// Tipo para los datos del formulario
export type ProductFormData = CreateProductData;

// Valores por defecto para el formulario
export const defaultProductValues: Partial<ProductFormData> = {
  name: '',
  description: '',
  price: 0,
  stock: 0,
  category: '',
  imageUrl: '',
  sku: '',
  dimensions: undefined,
  weight: undefined,
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
