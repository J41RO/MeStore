// ~/frontend/src/hooks/index.ts
// ---------------------------------------------------------------------------------------------
// MESTOCKER - Hooks Index
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
/**
 * Hooks Index - Exportación centralizada de custom hooks
 *
 * Permite imports como:
 * import { useAuth, useVendor, useProducts, useCart } from '@/hooks'
 */

export { useTheme } from './useTheme';
export type { Theme, UseThemeReturn } from './useTheme';

export { useAuth } from './useAuth';
export type { UseAuthReturn } from './useAuth';

export { useVendor } from './useVendor';
export type { UseVendorReturn } from './useVendor';

// Hook para manejo automático de API requests con loading y error handling
export { useApiRequest, default as useApiRequestDefault } from './useApiRequest';