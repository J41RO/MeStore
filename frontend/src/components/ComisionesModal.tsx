// ~/MeStore/frontend/src/components/ComisionesModal.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - ComisionesModal Component
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: ComisionesModal.tsx
// Ruta: ~/MeStore/frontend/src/components/ComisionesModal.tsx
// Autor: Jairo
// Fecha de Creación: 2025-08-14
// Última Actualización: 2025-08-14
// Versión: 1.0.0
// Propósito: Modal para ver comisiones y ganancias del vendedor
//
// Modificaciones:
// 2025-08-14 - Creación inicial del modal
//
// ---------------------------------------------------------------------------------------------

import React from 'react';
import { X, DollarSign, TrendingUp, Calendar } from 'lucide-react';

interface ComisionesModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ComisionesModal: React.FC<ComisionesModalProps> = ({
  isOpen,
  onClose,
}) => {
  // Mock data - en producción vendrá del hook useVendor
  const mockComisions = [
    {
      id: 1,
      producto: 'Laptop Gaming',
      venta: 1200,
      comision: 120,
      fecha: '2025-08-10',
    },
    {
      id: 2,
      producto: 'Mouse Inalámbrico',
      venta: 45,
      comision: 4.5,
      fecha: '2025-08-12',
    },
    {
      id: 3,
      producto: 'Teclado RGB',
      venta: 89,
      comision: 8.9,
      fecha: '2025-08-13',
    },
  ];

  const totalComisiones = mockComisions.reduce(
    (sum, item) => sum + item.comision,
    0
  );

  if (!isOpen) return null;

  return (
    <div className='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4'>
      <div className='bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto'>
        <div className='flex items-center justify-between p-6 border-b border-gray-200'>
          <div className='flex items-center space-x-3'>
            <DollarSign className='w-6 h-6 text-green-600' />
            <h2 className='text-xl font-semibold text-gray-900'>
              Mis Comisiones
            </h2>
          </div>
          <button
            onClick={onClose}
            className='text-gray-400 hover:text-gray-600 transition-colors'
          >
            <X className='w-6 h-6' />
          </button>
        </div>

        <div className='p-6'>
          {/* Resumen de comisiones */}
          <div className='grid grid-cols-1 md:grid-cols-3 gap-4 mb-6'>
            <div className='bg-green-50 p-4 rounded-lg'>
              <div className='flex items-center space-x-2'>
                <DollarSign className='w-5 h-5 text-green-600' />
                <span className='text-sm font-medium text-green-800'>
                  Total Comisiones
                </span>
              </div>
              <p className='text-2xl font-bold text-green-900 mt-1'>
                ${totalComisiones.toFixed(2)}
              </p>
            </div>

            <div className='bg-blue-50 p-4 rounded-lg'>
              <div className='flex items-center space-x-2'>
                <TrendingUp className='w-5 h-5 text-blue-600' />
                <span className='text-sm font-medium text-blue-800'>
                  Este Mes
                </span>
              </div>
              <p className='text-2xl font-bold text-blue-900 mt-1'>
                ${(totalComisiones * 0.7).toFixed(2)}
              </p>
            </div>

            <div className='bg-purple-50 p-4 rounded-lg'>
              <div className='flex items-center space-x-2'>
                <Calendar className='w-5 h-5 text-purple-600' />
                <span className='text-sm font-medium text-purple-800'>
                  Última Semana
                </span>
              </div>
              <p className='text-2xl font-bold text-purple-900 mt-1'>
                ${(totalComisiones * 0.3).toFixed(2)}
              </p>
            </div>
          </div>

          {/* Lista de comisiones */}
          <div className='space-y-4'>
            <h3 className='text-lg font-medium text-gray-900'>
              Historial de Comisiones
            </h3>

            {mockComisions.length > 0 ? (
              <div className='space-y-3'>
                {mockComisions.map(comision => (
                  <div
                    key={comision.id}
                    className='flex items-center justify-between p-4 bg-gray-50 rounded-lg'
                  >
                    <div className='flex-1'>
                      <h4 className='font-medium text-gray-900'>
                        {comision.producto}
                      </h4>
                      <p className='text-sm text-gray-600'>
                        Venta: ${comision.venta}
                      </p>
                      <p className='text-xs text-gray-500'>{comision.fecha}</p>
                    </div>
                    <div className='text-right'>
                      <p className='font-semibold text-green-600'>
                        +${comision.comision}
                      </p>
                      <p className='text-xs text-gray-500'>Comisión</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className='text-center py-8'>
                <DollarSign className='w-12 h-12 text-gray-400 mx-auto mb-4' />
                <p className='text-gray-600'>
                  No tienes comisiones registradas aún
                </p>
              </div>
            )}
          </div>

          <div className='flex justify-end mt-6'>
            <button
              onClick={onClose}
              className='px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md transition-colors'
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComisionesModal;
