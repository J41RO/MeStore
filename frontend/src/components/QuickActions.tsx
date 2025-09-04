// ~/MeStore/frontend/src/components/QuickActions.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - QuickActions Component
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: QuickActions.tsx
// Ruta: ~/MeStore/frontend/src/components/QuickActions.tsx
// Autor: Jairo
// Fecha de Creación: 2025-08-14
// Última Actualización: 2025-08-14
// Versión: 1.1.0
// Propósito: Componente de acciones rápidas para el dashboard principal
//            Incluye: Añadir Producto, Ver Comisiones, Contactar Soporte
//
// Modificaciones:
// 2025-08-14 - Creación inicial con tres quick actions
// 2025-08-14 - Integración con modales específicos funcionales
//
// ---------------------------------------------------------------------------------------------

import React, { useState } from 'react';
import { Package, DollarSign, HelpCircle } from 'lucide-react';
import AddProductModal from './AddProductModal';
import ComisionesModal from './ComisionesModal';
import SoporteModal from './SoporteModal';

interface QuickActionsProps {
  className?: string;
}

const QuickActions: React.FC<QuickActionsProps> = ({ className = '' }) => {
  const [isAddProductOpen, setIsAddProductOpen] = useState(false);
  const [isComisionesOpen, setIsComisionesOpen] = useState(false);
  const [isSoporteOpen, setIsSoporteOpen] = useState(false);

  const quickActionItems = [
    {
      id: 'add-product',
      title: 'Añadir Producto',
      description: 'Registra un nuevo producto rápidamente',
      icon: Package,
      bgColor: 'bg-blue-50 hover:bg-blue-100',
      iconColor: 'text-blue-600',
      onClick: () => setIsAddProductOpen(true),
    },
    {
      id: 'view-comisions',
      title: 'Ver Comisiones',
      description: 'Consulta tus comisiones ganadas',
      icon: DollarSign,
      bgColor: 'bg-green-50 hover:bg-green-100',
      iconColor: 'text-green-600',
      onClick: () => setIsComisionesOpen(true),
    },
    {
      id: 'contact-support',
      title: 'Contactar Soporte',
      description: 'Obtén ayuda técnica inmediata',
      icon: HelpCircle,
      bgColor: 'bg-purple-50 hover:bg-purple-100',
      iconColor: 'text-purple-600',
      onClick: () => setIsSoporteOpen(true),
    },
  ];

  return (
    <>
      <div
        className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}
      >
        <h2 className='text-lg font-semibold text-gray-900 mb-4'>
          Acciones Rápidas
        </h2>

        <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
          {quickActionItems.map(item => {
            const IconComponent = item.icon;
            return (
              <button
                key={item.id}
                onClick={item.onClick}
                className={`${item.bgColor} p-4 rounded-lg border border-gray-200 transition-all duration-200 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2`}
              >
                <div className='flex flex-col items-center text-center space-y-2'>
                  <IconComponent className={`w-8 h-8 ${item.iconColor}`} />
                  <h3 className='font-medium text-gray-900 text-sm'>
                    {item.title}
                  </h3>
                  <p className='text-xs text-gray-600 hidden sm:block'>
                    {item.description}
                  </p>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Modales funcionales */}
      <AddProductModal
        isOpen={isAddProductOpen}
        onClose={() => setIsAddProductOpen(false)}
      />
      <ComisionesModal
        isOpen={isComisionesOpen}
        onClose={() => setIsComisionesOpen(false)}
      />
      <SoporteModal
        isOpen={isSoporteOpen}
        onClose={() => setIsSoporteOpen(false)}
      />
    </>
  );
};

export default QuickActions;
