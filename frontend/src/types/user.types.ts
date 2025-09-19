// ~/frontend/src/types/user.types.ts
// ---------------------------------------------------------------------------------------------
// MESTOCKER - User Types
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: user.types.ts
// Ruta: ~/frontend/src/types/user.types.ts
// Autor: Jairo
// Fecha de Creación: 2025-08-11
// Última Actualización: 2025-08-11
// Versión: 1.0.0
// Propósito: Definir tipos TypeScript para usuarios y vendedores del sistema
//            Separar claramente tipos de autenticación vs datos específicos del vendedor
//
// Modificaciones:
// 2025-08-11 - Creación inicial con interfaces completas
//
// ---------------------------------------------------------------------------------------------

import type { EntityId, BaseEntity } from './core.types';

/**
 * Tipos específicos para vendedores y usuarios
 *
 * Este archivo define la estructura de datos para:
 * - Usuario básico (autenticación)
 * - Perfil del vendedor (datos específicos)
 * - Estado del contexto de usuario
 * - Tipos de actualización
 */

// Tipos específicos para vendedores y usuarios
export interface BaseUser extends BaseEntity {
  id: EntityId;
  email: string;
  name?: string;
  role?: string;
}

export interface VendorProfile {
  // Información básica del vendedor
  userId: EntityId;
  storeName: string;
  storeDescription: string;
  storeSlug: string;

  // Información de contacto y ubicación
  contactInfo: {
    phone?: string;
    address?: string;
    city?: string;
    state?: string;
    zipCode?: string;
  };

  // Métricas de negocio
  businessMetrics: {
    totalSales: number;
    totalRevenue: number;
    totalCommissions: number;
    stockLevel: number;
    lowStockItems: number;
    activeProducts: number;
    totalOrders: number;
    averageRating: number;
    joinDate: string;
    lastActivity: string;
  };

  // Configuraciones del vendedor
  settings: {
    notifications: {
      email: boolean;
      push: boolean;
      orderUpdates: boolean;
      promotions: boolean;
    };
    preferences: {
      theme: 'light' | 'dark' | 'auto';
      language: string;
      currency: string;
      timezone: string;
    };
    business: {
      autoAcceptOrders: boolean;
      minimumOrderAmount: number;
      processingTime: string;
      returnPolicy: string;
    };
  };

  // Estado del perfil
  profileStatus: {
    isVerified: boolean;
    isActive: boolean;
    completionPercentage: number;
    lastUpdated: string;
  };
}

export interface UserContextState {
  // Estado del perfil
  vendorProfile: VendorProfile | null;
  isLoading: boolean;
  error: string | null;

  // Métricas computadas
  completionPercentage: number;
  isProfileComplete: boolean;
  recentActivity: any[];
}

export type VendorUpdateData = Partial<
  Omit<VendorProfile, 'userId' | 'businessMetrics' | 'profileStatus'>
>;
