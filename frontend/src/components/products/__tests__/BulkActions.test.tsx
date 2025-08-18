// ~/frontend/src/components/products/__tests__/BulkActions.test.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Tests para Componente BulkActions
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import BulkActions from '../BulkActions';

// Mock básico del servicio
jest.mock('../../../services/productBulkService', () => ({
  bulkDeleteProducts: jest.fn(),
  bulkUpdateProductStatus: jest.fn(),
  getBulkErrorMessage: jest.fn().mockReturnValue('Error simulado'),
}));

describe('BulkActions Component', () => {
  const defaultProps = {
    selectedProducts: ['product-1', 'product-2', 'product-3'],
    selectedCount: 3,
    onBulkComplete: jest.fn(),
    onClearSelection: jest.fn(),
    onShowNotification: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderizado Básico', () => {
    it('no debe renderizar cuando selectedCount es 0', () => {
      render(
        <BulkActions
          {...defaultProps}
          selectedCount={0}
          selectedProducts={[]}
        />
      );
      
      expect(screen.queryByText(/productos seleccionados/)).not.toBeInTheDocument();
    });

    it('debe renderizar correctamente con productos seleccionados', () => {
      render(<BulkActions {...defaultProps} />);
      
      expect(screen.getByText('3 productos seleccionados')).toBeInTheDocument();
      expect(screen.getByText('Cambiar Estado')).toBeInTheDocument();
      expect(screen.getByText('Eliminar')).toBeInTheDocument();
      expect(screen.getByText('✕')).toBeInTheDocument();
    });

    it('debe mostrar singular cuando hay 1 producto', () => {
      render(
        <BulkActions
          {...defaultProps}
          selectedCount={1}
          selectedProducts={['product-1']}
        />
      );
      
      expect(screen.getByText('1 producto seleccionado')).toBeInTheDocument();
    });
  });

  describe('Interacciones UI', () => {
    it('debe mostrar modal de confirmación al hacer click en Eliminar', () => {
      render(<BulkActions {...defaultProps} />);
      
      fireEvent.click(screen.getByText('Eliminar'));
      
      expect(screen.getByText('Confirmar Eliminación')).toBeInTheDocument();
      expect(screen.getByText(/¿Estás seguro de que deseas eliminar 3 productos?/)).toBeInTheDocument();
    });

    it('debe mostrar modal de estado al hacer click en Cambiar Estado', () => {
      render(<BulkActions {...defaultProps} />);
      
      fireEvent.click(screen.getByText('Cambiar Estado'));
      
      expect(screen.getByText('Cambiar Estado de Productos')).toBeInTheDocument();
      expect(screen.getByText('Activo')).toBeInTheDocument();
      expect(screen.getByText('Inactivo')).toBeInTheDocument();
    });

    it('debe limpiar selección al hacer click en X', () => {
      render(<BulkActions {...defaultProps} />);
      
      fireEvent.click(screen.getByText('✕'));
      
      expect(defaultProps.onClearSelection).toHaveBeenCalled();
    });

    it('debe cancelar eliminación correctamente', () => {
      render(<BulkActions {...defaultProps} />);
      
      fireEvent.click(screen.getByText('Eliminar'));
      fireEvent.click(screen.getByText('Cancelar'));
      
      expect(screen.queryByText('Confirmar Eliminación')).not.toBeInTheDocument();
    });

    it('debe cancelar cambio de estado correctamente', () => {
      render(<BulkActions {...defaultProps} />);
      
      fireEvent.click(screen.getByText('Cambiar Estado'));
      fireEvent.click(screen.getByText('Cancelar'));
      
      expect(screen.queryByText('Cambiar Estado de Productos')).not.toBeInTheDocument();
    });
  });

  describe('Props y Estados', () => {
    it('debe manejar diferentes counts correctamente', () => {
      const { rerender } = render(<BulkActions {...defaultProps} selectedCount={5} />);
      expect(screen.getByText('5 productos seleccionados')).toBeInTheDocument();
      
      rerender(<BulkActions {...defaultProps} selectedCount={1} />);
      expect(screen.getByText('1 producto seleccionado')).toBeInTheDocument();
    });

    it('debe manejar lista vacía de productos', () => {
      render(
        <BulkActions
          {...defaultProps}
          selectedProducts={[]}
          selectedCount={0}
        />
      );
      
      expect(screen.queryByText(/productos seleccionados/)).not.toBeInTheDocument();
    });
  });

  describe('Casos Edge', () => {
    it('debe renderizar con props mínimas', () => {
      const minimalProps = {
        selectedProducts: ['product-1'],
        selectedCount: 1,
        onBulkComplete: jest.fn(),
        onClearSelection: jest.fn(),
        onShowNotification: jest.fn(),
      };

      render(<BulkActions {...minimalProps} />);
      
      expect(screen.getByText('1 producto seleccionado')).toBeInTheDocument();
    });
  });
});
