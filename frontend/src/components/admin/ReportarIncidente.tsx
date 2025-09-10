import React, { useState } from 'react';
import Button from '../ui/Button/Button';
import Modal from '../ui/Modal/Modal';
import { InventoryItem, TipoIncidente, IncidenteCreate, Incidente } from '../../types/inventory.types';

interface ReportarIncidenteProps {
  inventoryItem: InventoryItem;
  onIncidenteReportado: (incidente: Incidente) => void;
  onClose: () => void;
  isOpen: boolean;
}

export const ReportarIncidente: React.FC<ReportarIncidenteProps> = ({
  inventoryItem,
  onIncidenteReportado,
  onClose,
  isOpen,
}) => {
  const [formData, setFormData] = useState<IncidenteCreate>({
    inventory_id: inventoryItem.id,
    tipo_incidente: TipoIncidente.PERDIDO,
    descripcion: '',
    fecha_incidente: undefined,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.descripcion.trim()) {
      alert('La descripción es obligatoria');
      return;
    }

    setIsSubmitting(true);
    
    try {
      const response = await fetch('/api/v1/inventory/incidentes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al reportar incidente');
      }

      const incidente = await response.json();
      onIncidenteReportado(incidente);
      
      // Resetear formulario
      setFormData({
        inventory_id: inventoryItem.id,
        tipo_incidente: TipoIncidente.PERDIDO,
        descripcion: '',
        fecha_incidente: undefined,
      });
      
      onClose();
    } catch (error) {
      console.error('Error reportando incidente:', error);
      alert('Error al reportar incidente. Intente nuevamente.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTipoChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFormData(prev => ({
      ...prev,
      tipo_incidente: e.target.value as TipoIncidente,
    }));
  };

  const handleDescripcionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      descripcion: e.target.value,
    }));
  };

  if (!isOpen) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Reportar Incidente de Inventario">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="tipo_incidente" className="block text-sm font-medium text-gray-700">
            Tipo de Incidente *
          </label>
          <select
            id="tipo_incidente"
            value={formData.tipo_incidente}
            onChange={handleTipoChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          >
            <option value={TipoIncidente.PERDIDO}>Producto Perdido/Extraviado</option>
            <option value={TipoIncidente.DAÑADO}>Producto Dañado/Defectuoso</option>
          </select>
        </div>

        <div>
          <label htmlFor="descripcion" className="block text-sm font-medium text-gray-700">
            Descripción del Incidente *
          </label>
          <textarea
            id="descripcion"
            placeholder="Describa detalladamente lo ocurrido con el producto..."
            value={formData.descripcion}
            onChange={handleDescripcionChange}
            rows={4}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          />
        </div>

        <div className="bg-gray-50 p-3 rounded-md">
          <h4 className="font-medium text-sm mb-2">Información del Producto:</h4>
          <div className="text-sm text-gray-600 space-y-1">
            <div><strong>SKU:</strong> {inventoryItem.sku}</div>
            <div><strong>Producto:</strong> {inventoryItem.productName}</div>
            <div><strong>Cantidad Actual:</strong> {inventoryItem.quantity}</div>
            <div><strong>Ubicación:</strong> {inventoryItem.location.zone}-{inventoryItem.location.aisle}-{inventoryItem.location.shelf}</div>
          </div>
        </div>

        <div className="flex justify-end space-x-3">
          <Button variant="secondary" onClick={onClose} disabled={isSubmitting}>
            Cancelar
          </Button>
          <Button variant="primary" type="submit" loading={isSubmitting}>
            {isSubmitting ? 'Reportando...' : 'Reportar Incidente'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};