// ~/frontend/src/components/EditProductModal.tsx
// Copyright (c) 2025 Jairo. Todos los derechos reservados.

import React, { useMemo } from 'react';
import { X, Edit } from 'lucide-react';
import ProductForm from './forms/ProductForm';
import { Product, UpdateProductData } from '../types/api.types';

interface EditProductModalProps {
  isOpen: boolean;
  onClose: () => void;
  product: Product;
  onProductUpdated?: () => void;
}

const EditProductModal: React.FC<EditProductModalProps> = ({
  isOpen,
  onClose,
  product,
  onProductUpdated,
}) => {
  console.log('🔄 [EditProductModal] Component renderizado');

  const handleProductSubmit = (data: UpdateProductData) => {
    console.log('Producto actualizado:', data);
    // El ProductForm ya maneja la actualización vía API
  };

  const handleSuccess = () => {
    // Notificar al componente padre que se actualizó un producto
    if (onProductUpdated) {
      onProductUpdated();
    }
    onClose();
  };

  if (!isOpen) return null;

  // FIX: Memoizar initialData para evitar crear nuevo objeto en cada render
  // Esto previene infinite re-renders en ProductForm useEffect
  const initialData = useMemo(() => ({
    id: product.id,
    name: product.name,
    description: product.description,
    price: product.price,
    stock: product.stock,
    category: product.category as any,
    imageUrl: product.imageUrl || '',
  }), [product.id, product.name, product.description, product.price, product.stock, product.category, product.imageUrl]);

  return (
    <div className='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4'>
      <div className='bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto'>
        <div className='flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700'>
          <div className='flex items-center space-x-3'>
            <Edit className='w-6 h-6 text-blue-600' />
            <h2 className='text-xl font-semibold text-gray-900 dark:text-white'>
              Editar Producto: {product.name}
            </h2>
          </div>
          <button
            onClick={onClose}
            aria-label='Cerrar modal'
            className='text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors'
          >
            <X className='w-6 h-6' />
          </button>
        </div>

        <div className='p-6'>
          <ProductForm
            mode='edit'
            initialData={initialData}
            onSubmit={handleProductSubmit}
            onCancel={onClose}
            onSuccess={handleSuccess}
          />
        </div>
      </div>
    </div>
  );
};

export default EditProductModal;
