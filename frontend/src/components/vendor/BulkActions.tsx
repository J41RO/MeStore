/**
 * BulkActions - Bulk operations component for selected products
 *
 * Features:
 * - Bulk delete with confirmation
 * - Bulk status changes (active/inactive)
 * - Bulk featured toggle
 * - Bulk category assignment
 * - Bulk price adjustments
 * - Progress tracking for bulk operations
 * - Colombian localization
 */

import React, { useState } from 'react';
import { useProductStore, productSelectors } from '../../stores/productStore.new';
import { useCategoryStore } from '../../stores/categoryStore';
import {
  TrashIcon,
  EyeIcon,
  EyeSlashIcon,
  StarIcon,
  TagIcon,
  CurrencyDollarIcon,
  ExclamationTriangleIcon,
  CheckIcon,
  XMarkIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

interface BulkActionsProps {
  onRefresh?: () => void;
}

/**
 * Bulk operation confirmation modal
 */
interface ConfirmationModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText: string;
  cancelText: string;
  isDestructive?: boolean;
  isLoading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  isOpen,
  title,
  message,
  confirmText,
  cancelText,
  isDestructive = false,
  isLoading = false,
  onConfirm,
  onCancel,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-end sm:items-center justify-center min-h-full p-4 text-center sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        <div className="relative bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:max-w-lg sm:w-full sm:p-6">
          <div className="sm:flex sm:items-start">
            <div className={`mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full sm:mx-0 sm:h-10 sm:w-10 ${
              isDestructive ? 'bg-red-100' : 'bg-blue-100'
            }`}>
              {isDestructive ? (
                <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
              ) : (
                <CheckIcon className="h-6 w-6 text-blue-600" />
              )}
            </div>
            <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                {title}
              </h3>
              <div className="mt-2">
                <p className="text-sm text-gray-500">
                  {message}
                </p>
              </div>
            </div>
          </div>
          <div className="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
            <button
              onClick={onConfirm}
              disabled={isLoading}
              className={`w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 text-base font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 sm:ml-3 sm:w-auto sm:text-sm ${
                isDestructive
                  ? 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
                  : 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'
              } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {isLoading && <ArrowPathIcon className="w-4 h-4 mr-2 animate-spin" />}
              {confirmText}
            </button>
            <button
              onClick={onCancel}
              disabled={isLoading}
              className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:w-auto sm:text-sm"
            >
              {cancelText}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Bulk category assignment modal
 */
interface BulkCategoryModalProps {
  isOpen: boolean;
  onAssign: (categoryId: string) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

const BulkCategoryModal: React.FC<BulkCategoryModalProps> = ({
  isOpen,
  onAssign,
  onCancel,
  isLoading = false,
}) => {
  const { categories } = useCategoryStore();
  const [selectedCategory, setSelectedCategory] = useState('');

  const handleAssign = () => {
    if (selectedCategory) {
      onAssign(selectedCategory);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-end sm:items-center justify-center min-h-full p-4 text-center sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        <div className="relative bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:max-w-lg sm:w-full sm:p-6">
          <div className="sm:flex sm:items-start">
            <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 sm:mx-0 sm:h-10 sm:w-10">
              <TagIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left flex-1">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Asignar Categoría
              </h3>
              <div className="mt-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Selecciona una categoría para asignar a los productos seleccionados:
                </label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Selecciona una categoría</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
          <div className="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
            <button
              onClick={handleAssign}
              disabled={!selectedCategory || isLoading}
              className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading && <ArrowPathIcon className="w-4 h-4 mr-2 animate-spin" />}
              Asignar Categoría
            </button>
            <button
              onClick={onCancel}
              disabled={isLoading}
              className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:w-auto sm:text-sm"
            >
              Cancelar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Main BulkActions component
 */
const BulkActions: React.FC<BulkActionsProps> = ({ onRefresh }) => {
  // Store hooks
  const {
    bulkDeleteProducts,
    bulkUpdateProducts,
    clearSelection,
    getSelectedProducts,
  } = useProductStore();

  // Selectors
  const selectedProductIds = useProductStore(productSelectors.selectedProductIds);
  const selectedProducts = useProductStore(productSelectors.selectedProducts);

  // Local state
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showActivateConfirm, setShowActivateConfirm] = useState(false);
  const [showDeactivateConfirm, setShowDeactivateConfirm] = useState(false);
  const [showFeatureConfirm, setShowFeatureConfirm] = useState(false);
  const [showUnfeatureConfirm, setShowUnfeatureConfirm] = useState(false);
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Handle bulk delete
   */
  const handleBulkDelete = async () => {
    setIsLoading(true);
    try {
      const success = await bulkDeleteProducts();
      if (success) {
        clearSelection();
        if (onRefresh) {
          onRefresh();
        }
      }
    } catch (error) {
      console.error('Bulk delete failed:', error);
    } finally {
      setIsLoading(false);
      setShowDeleteConfirm(false);
    }
  };

  /**
   * Handle bulk status changes
   */
  const handleBulkActivate = async () => {
    setIsLoading(true);
    try {
      const success = await bulkUpdateProducts({ is_active: true });
      if (success) {
        clearSelection();
        if (onRefresh) {
          onRefresh();
        }
      }
    } catch (error) {
      console.error('Bulk activate failed:', error);
    } finally {
      setIsLoading(false);
      setShowActivateConfirm(false);
    }
  };

  const handleBulkDeactivate = async () => {
    setIsLoading(true);
    try {
      const success = await bulkUpdateProducts({ is_active: false });
      if (success) {
        clearSelection();
        if (onRefresh) {
          onRefresh();
        }
      }
    } catch (error) {
      console.error('Bulk deactivate failed:', error);
    } finally {
      setIsLoading(false);
      setShowDeactivateConfirm(false);
    }
  };

  /**
   * Handle bulk featured changes
   */
  const handleBulkFeature = async () => {
    setIsLoading(true);
    try {
      const success = await bulkUpdateProducts({ is_featured: true });
      if (success) {
        clearSelection();
        if (onRefresh) {
          onRefresh();
        }
      }
    } catch (error) {
      console.error('Bulk feature failed:', error);
    } finally {
      setIsLoading(false);
      setShowFeatureConfirm(false);
    }
  };

  const handleBulkUnfeature = async () => {
    setIsLoading(true);
    try {
      const success = await bulkUpdateProducts({ is_featured: false });
      if (success) {
        clearSelection();
        if (onRefresh) {
          onRefresh();
        }
      }
    } catch (error) {
      console.error('Bulk unfeature failed:', error);
    } finally {
      setIsLoading(false);
      setShowUnfeatureConfirm(false);
    }
  };

  /**
   * Handle bulk category assignment
   */
  const handleBulkCategoryAssignment = async (categoryId: string) => {
    setIsLoading(true);
    try {
      const success = await bulkUpdateProducts({ category_id: categoryId });
      if (success) {
        clearSelection();
        if (onRefresh) {
          onRefresh();
        }
      }
    } catch (error) {
      console.error('Bulk category assignment failed:', error);
    } finally {
      setIsLoading(false);
      setShowCategoryModal(false);
    }
  };

  if (selectedProductIds.length === 0) {
    return null;
  }

  return (
    <>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        {/* Selection Info */}
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-blue-900">
            {selectedProductIds.length} producto{selectedProductIds.length !== 1 ? 's' : ''} seleccionado{selectedProductIds.length !== 1 ? 's' : ''}
          </span>
          <button
            onClick={clearSelection}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            Deseleccionar todo
          </button>
        </div>

        {/* Bulk Action Buttons */}
        <div className="flex flex-wrap gap-2">
          {/* Activate */}
          <button
            onClick={() => setShowActivateConfirm(true)}
            className="inline-flex items-center px-3 py-2 border border-green-300 text-sm font-medium rounded-md text-green-700 bg-green-50 hover:bg-green-100 transition-colors"
          >
            <EyeIcon className="w-4 h-4 mr-2" />
            Activar
          </button>

          {/* Deactivate */}
          <button
            onClick={() => setShowDeactivateConfirm(true)}
            className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-gray-50 hover:bg-gray-100 transition-colors"
          >
            <EyeSlashIcon className="w-4 h-4 mr-2" />
            Desactivar
          </button>

          {/* Feature */}
          <button
            onClick={() => setShowFeatureConfirm(true)}
            className="inline-flex items-center px-3 py-2 border border-yellow-300 text-sm font-medium rounded-md text-yellow-700 bg-yellow-50 hover:bg-yellow-100 transition-colors"
          >
            <StarIcon className="w-4 h-4 mr-2" />
            Destacar
          </button>

          {/* Category */}
          <button
            onClick={() => setShowCategoryModal(true)}
            className="inline-flex items-center px-3 py-2 border border-blue-300 text-sm font-medium rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100 transition-colors"
          >
            <TagIcon className="w-4 h-4 mr-2" />
            Categoría
          </button>

          {/* Delete */}
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="inline-flex items-center px-3 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-red-50 hover:bg-red-100 transition-colors"
          >
            <TrashIcon className="w-4 h-4 mr-2" />
            Eliminar
          </button>
        </div>
      </div>

      {/* Confirmation Modals */}
      <ConfirmationModal
        isOpen={showDeleteConfirm}
        title="Eliminar Productos"
        message={`¿Estás seguro de que quieres eliminar ${selectedProductIds.length} producto${selectedProductIds.length !== 1 ? 's' : ''}? Esta acción no se puede deshacer.`}
        confirmText="Eliminar"
        cancelText="Cancelar"
        isDestructive={true}
        isLoading={isLoading}
        onConfirm={handleBulkDelete}
        onCancel={() => setShowDeleteConfirm(false)}
      />

      <ConfirmationModal
        isOpen={showActivateConfirm}
        title="Activar Productos"
        message={`¿Quieres activar ${selectedProductIds.length} producto${selectedProductIds.length !== 1 ? 's' : ''}? Los productos estarán visibles para los compradores.`}
        confirmText="Activar"
        cancelText="Cancelar"
        isLoading={isLoading}
        onConfirm={handleBulkActivate}
        onCancel={() => setShowActivateConfirm(false)}
      />

      <ConfirmationModal
        isOpen={showDeactivateConfirm}
        title="Desactivar Productos"
        message={`¿Quieres desactivar ${selectedProductIds.length} producto${selectedProductIds.length !== 1 ? 's' : ''}? Los productos no estarán visibles para los compradores.`}
        confirmText="Desactivar"
        cancelText="Cancelar"
        isLoading={isLoading}
        onConfirm={handleBulkDeactivate}
        onCancel={() => setShowDeactivateConfirm(false)}
      />

      <ConfirmationModal
        isOpen={showFeatureConfirm}
        title="Destacar Productos"
        message={`¿Quieres destacar ${selectedProductIds.length} producto${selectedProductIds.length !== 1 ? 's' : ''}? Los productos aparecerán en las secciones destacadas.`}
        confirmText="Destacar"
        cancelText="Cancelar"
        isLoading={isLoading}
        onConfirm={handleBulkFeature}
        onCancel={() => setShowFeatureConfirm(false)}
      />

      <ConfirmationModal
        isOpen={showUnfeatureConfirm}
        title="Quitar Destacado"
        message={`¿Quieres quitar el destacado de ${selectedProductIds.length} producto${selectedProductIds.length !== 1 ? 's' : ''}?`}
        confirmText="Quitar Destacado"
        cancelText="Cancelar"
        isLoading={isLoading}
        onConfirm={handleBulkUnfeature}
        onCancel={() => setShowUnfeatureConfirm(false)}
      />

      {/* Category Assignment Modal */}
      <BulkCategoryModal
        isOpen={showCategoryModal}
        onAssign={handleBulkCategoryAssignment}
        onCancel={() => setShowCategoryModal(false)}
        isLoading={isLoading}
      />
    </>
  );
};

export default BulkActions;