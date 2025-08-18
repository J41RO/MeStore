// ~/src/components/products/BulkActions.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Componente de acciones bulk para productos seleccionados
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: BulkActions.tsx
// Ruta: ~/src/components/products/BulkActions.tsx
// Autor: Jairo
// Fecha de Creación: 2025-08-16
// Última Actualización: 2025-08-18
// Versión: 2.0.0
// Propósito: Componente de acciones bulk integrado con servicios backend
//            Incluye confirmaciones, loading states y manejo de errores
//
// Modificaciones:
// 2025-08-16 - Implementación inicial del componente UI
// 2025-08-18 - Integración con servicios bulk reales y manejo de estados
//
// ---------------------------------------------------------------------------------------------

import React, { useState } from 'react';
import { Trash2, Edit3, Loader2 } from 'lucide-react';
import { bulkDeleteProducts, bulkUpdateProductStatus, getBulkErrorMessage, BulkOperationError } from '../../services/productBulkService';

interface BulkActionsProps {
  selectedProducts: string[]; // Array de IDs de productos seleccionados
  selectedCount: number;
  onBulkComplete: () => void; // Callback para actualizar la lista después de operaciones
  onClearSelection: () => void;
  onShowNotification: (message: string, type: 'success' | 'error') => void;
}

interface ConfirmationModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText: string;
  cancelText: string;
  onConfirm: () => void;
  onCancel: () => void;
  type: 'danger' | 'warning';
}

const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  isOpen,
  title,
  message,
  confirmText,
  cancelText,
  onConfirm,
  onCancel,
  type
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 className={`text-lg font-medium mb-4 ${type === 'danger' ? 'text-red-800' : 'text-yellow-800'}`}>
          {title}
        </h3>
        <p className="text-gray-600 mb-6">{message}</p>
        <div className="flex space-x-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            className={`px-4 py-2 text-sm font-medium text-white rounded-md ${
              type === 'danger' 
                ? 'bg-red-600 hover:bg-red-700' 
                : 'bg-yellow-600 hover:bg-yellow-700'
            }`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};

interface StatusModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (status: string) => void;
}

const StatusModal: React.FC<StatusModalProps> = ({ isOpen, onClose, onConfirm }) => {
  const [selectedStatus, setSelectedStatus] = useState<string>('active');

  if (!isOpen) return null;

  const statusOptions = [
    { value: 'active', label: 'Activo', color: 'text-green-600' },
    { value: 'inactive', label: 'Inactivo', color: 'text-gray-600' },
    { value: 'pending', label: 'Pendiente', color: 'text-yellow-600' },
    { value: 'archived', label: 'Archivado', color: 'text-red-600' }
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 className="text-lg font-medium mb-4 text-gray-800">
          Cambiar Estado de Productos
        </h3>
        <p className="text-gray-600 mb-4">
          Selecciona el nuevo estado para los productos seleccionados:
        </p>
        <div className="space-y-2 mb-6">
          {statusOptions.map((option) => (
            <label key={option.value} className="flex items-center">
              <input
                type="radio"
                name="status"
                value={option.value}
                checked={selectedStatus === option.value}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="mr-3"
              />
              <span className={`font-medium ${option.color}`}>
                {option.label}
              </span>
            </label>
          ))}
        </div>
        <div className="flex space-x-3 justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cancelar
          </button>
          <button
            onClick={() => onConfirm(selectedStatus)}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
          >
            Aplicar Cambio
          </button>
        </div>
      </div>
    </div>
  );
};

const BulkActions: React.FC<BulkActionsProps> = ({
  selectedProducts,
  selectedCount,
  onBulkComplete,
  onClearSelection,
  onShowNotification,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showStatusModal, setShowStatusModal] = useState(false);

  if (selectedCount === 0) return null;

  const handleBulkDelete = async () => {
    setIsLoading(true);
    try {
      const result = await bulkDeleteProducts(selectedProducts);
      
      onShowNotification(
        `${result.affected_count} productos eliminados exitosamente`,
        'success'
      );
      
      if (result.errors && result.errors.length > 0) {
        const errorMessage = result.errors.map(e => e.message).join(', ');
        onShowNotification(`Advertencias: ${errorMessage}`, 'error');
      }
      
      onBulkComplete();
      onClearSelection();
      
    } catch (error) {
      const bulkError = error as BulkOperationError;
      const errorMessage = getBulkErrorMessage(bulkError);
      onShowNotification(`Error al eliminar productos: ${errorMessage}`, 'error');
    } finally {
      setIsLoading(false);
      setShowDeleteConfirm(false);
    }
  };

  const handleBulkStatusChange = async (newStatus: string) => {
    setIsLoading(true);
    try {
      const result = await bulkUpdateProductStatus(
        selectedProducts, 
        newStatus as 'active' | 'inactive' | 'pending' | 'archived'
      );
      
      onShowNotification(
        `${result.affected_count} productos actualizados a "${newStatus}" exitosamente`,
        'success'
      );
      
      if (result.errors && result.errors.length > 0) {
        const errorMessage = result.errors.map(e => e.message).join(', ');
        onShowNotification(`Advertencias: ${errorMessage}`, 'error');
      }
      
      onBulkComplete();
      onClearSelection();
      
    } catch (error) {
      const bulkError = error as BulkOperationError;
      const errorMessage = getBulkErrorMessage(bulkError);
      onShowNotification(`Error al cambiar estado: ${errorMessage}`, 'error');
    } finally {
      setIsLoading(false);
      setShowStatusModal(false);
    }
  };

  return (
    <>
      <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-white shadow-lg rounded-lg border border-gray-200 p-4 z-40">
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700">
            {selectedCount} producto{selectedCount > 1 ? 's' : ''} seleccionado{selectedCount > 1 ? 's' : ''}
          </span>
          
          <div className="flex space-x-2">
            <button
              onClick={() => setShowStatusModal(true)}
              disabled={isLoading}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Edit3 className="h-4 w-4 mr-2" />
              )}
              Cambiar Estado
            </button>
            
            <button
              onClick={() => setShowDeleteConfirm(true)}
              disabled={isLoading}
              className="inline-flex items-center px-3 py-2 border border-transparent shadow-sm text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Trash2 className="h-4 w-4 mr-2" />
              )}
              Eliminar
            </button>
          </div>
          
          <button
            onClick={onClearSelection}
            disabled={isLoading}
            className="text-sm text-gray-500 hover:text-gray-700 disabled:opacity-50"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Modal de confirmación para eliminación */}
      <ConfirmationModal
        isOpen={showDeleteConfirm}
        title="Confirmar Eliminación"
        message={`¿Estás seguro de que deseas eliminar ${selectedCount} producto${selectedCount > 1 ? 's' : ''}? Esta acción no se puede deshacer.`}
        confirmText="Eliminar"
        cancelText="Cancelar"
        onConfirm={handleBulkDelete}
        onCancel={() => setShowDeleteConfirm(false)}
        type="danger"
      />

      {/* Modal de selección de estado */}
      <StatusModal
        isOpen={showStatusModal}
        onClose={() => setShowStatusModal(false)}
        onConfirm={handleBulkStatusChange}
      />
    </>
  );
};

export default BulkActions;
