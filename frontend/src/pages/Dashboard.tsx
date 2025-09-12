// ~/MeStore/frontend/src/pages/Dashboard.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Dashboard Page
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: Dashboard.tsx
// Ruta: ~/MeStore/frontend/src/pages/Dashboard.tsx
// Autor: Jairo
// Fecha de Creación: 2025-08-14
// Última Actualización: 2025-08-14
// Versión: 1.1.1
// Propósito: Página principal del dashboard del vendedor con QuickActions integrado
//
// Modificaciones:
// 2025-08-14 - Integración de QuickActions en ubicación estratégica
// 2025-08-14 - Corrección de propiedades TypeScript (missingFields, activeProducts)
//
// ---------------------------------------------------------------------------------------------

import React from 'react';
import { useAuthStore } from '../stores/authStore';
import VendorDashboard from '../components/dashboard/VendorDashboard';

const Dashboard: React.FC = () => {
  const { user } = useAuthStore();

  return (
    <div className='p-4 md:p-6 lg:p-8 max-w-7xl mx-auto'>
      <VendorDashboard vendorId={user?.id} className="" />
    </div>
  );
};

export default Dashboard;
