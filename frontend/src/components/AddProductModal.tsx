// ~/MeStore/frontend/src/components/AddProductModal.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - AddProductModal Component
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: AddProductModal.tsx
// Ruta: ~/MeStore/frontend/src/components/AddProductModal.tsx
// Autor: Jairo
// Fecha de Creación: 2025-08-14
// Última Actualización: 2025-08-16
// Versión: 2.0.0
// Propósito: Modal para añadir productos usando ProductForm robusto
//
// Modificaciones:
// 2025-08-14 - Creación inicial del modal
// 2025-08-16 - Actualizado para usar ProductForm con validaciones completas
//
// ---------------------------------------------------------------------------------------------

import React from 'react';
import { X, Package } from 'lucide-react';
import ProductForm from './forms/ProductForm';

interface AddProductModalProps {
  isOpen: boolean;
  onClose: () => void;
  onProductCreated?: () => void;
}

const AddProductModal: React.FC<AddProductModalProps> = ({
  isOpen,
  onClose,
  onProductCreated,
}) => {
  const handleProductSubmit = (data: any) => {
    console.log('Producto creado:', data);
    // El ProductForm ya maneja la creación vía API
  };

  const handleSuccess = () => {
    console.log('🎉 AddProductModal.handleSuccess ejecutado');
    console.log('🔍 onProductCreated type:', typeof onProductCreated);

    // Notificar al componente padre que se creó un producto
    if (onProductCreated) {
      console.log('✅ Llamando a onProductCreated()...');
      onProductCreated();
      console.log('✅ onProductCreated() completado');
    } else {
      console.warn('⚠️ onProductCreated no está definido en props');
    }

    console.log('🚪 Cerrando modal...');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4'>
      <div className='bg-slate-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto'>
        <div className='flex items-center justify-between p-6 border-b border-slate-700 bg-slate-800'>
          <div className='flex items-center space-x-3'>
            <Package className='w-6 h-6 text-blue-400' />
            <h2 className='text-xl font-semibold text-white'>
              Añadir Producto
            </h2>
          </div>
          <button
            onClick={onClose}
            aria-label='Cerrar modal'
            className='text-slate-400 hover:text-slate-200 transition-colors'
          >
            <X className='w-6 h-6' />
          </button>
        </div>

        <div className='p-6'>
          <ProductForm
            mode='create'
            onSubmit={handleProductSubmit}
            onCancel={onClose}
            onSuccess={handleSuccess}
          />
        </div>
      </div>
    </div>
  );
};

export default AddProductModal;
