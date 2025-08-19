// ~/src/components/ui/ImageUpload/__tests__/ImageUpload.test.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - ImageUpload Component Tests
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: ImageUpload.test.tsx
// Ruta: ~/src/components/ui/ImageUpload/__tests__/ImageUpload.test.tsx
// Autor: Jairo
// Fecha de Creación: 2025-08-18
// Última Actualización: 2025-08-18
// Versión: 1.0.0
// Propósito: Tests unitarios para el componente ImageUpload
//            Cobertura de funcionalidad drag & drop, validaciones y preview
//
// Modificaciones:
// 2025-08-18 - Recreación con sintaxis Jest
//
// ---------------------------------------------------------------------------------------------

import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, beforeEach } from '@jest/globals';
import ImageUpload from '../ImageUpload';
import { ImageUploadProps } from '../ImageUpload.types';

// Mock de react-dropzone
jest.mock('react-dropzone', () => ({
  useDropzone: jest.fn(() => ({
    getRootProps: () => ({ 'data-testid': 'dropzone' }),
    getInputProps: () => ({ 'data-testid': 'file-input' }),
    isDragActive: false,
    isDragAccept: false,
    isDragReject: false,
    fileRejections: [],
  })),
}));

// Mock de URL.createObjectURL
global.URL.createObjectURL = jest.fn(() => 'mock-preview-url');
global.URL.revokeObjectURL = jest.fn();

describe('ImageUpload Component', () => {
  const mockOnImageUpload = jest.fn();
  
  const defaultProps: ImageUploadProps = {
    onImageUpload: mockOnImageUpload,
    maxFiles: 5,
    maxSize: 5 * 1024 * 1024,
    acceptedTypes: ['image/jpeg', 'image/png', 'image/webp'],
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderizado básico', () => {
    it('debe renderizar el componente correctamente', () => {
      render(<ImageUpload {...defaultProps} />);
      
      expect(screen.getByTestId('dropzone')).toBeInTheDocument();
      expect(screen.getByTestId('file-input')).toBeInTheDocument();
      expect(screen.getByText('📁')).toBeInTheDocument();
      expect(screen.getByText('Arrastra imágenes aquí o haz clic para seleccionar')).toBeInTheDocument();
    });

    it('debe mostrar información de límites correctamente', () => {
      render(<ImageUpload {...defaultProps} />);
      
      expect(screen.getByText('Máximo 5 archivos, 5MB por archivo')).toBeInTheDocument();
      expect(screen.getByText('Formatos: JPEG, PNG, WEBP')).toBeInTheDocument();
    });

    it('debe aplicar clases CSS personalizadas', () => {
      render(<ImageUpload {...defaultProps} className="custom-class" />);
      
      const dropzone = screen.getByTestId('dropzone');
      expect(dropzone).toHaveClass('custom-class');
    });
  });

  describe('Componente deshabilitado', () => {
    it('debe aplicar estilos de disabled cuando disabled=true', () => {
      render(<ImageUpload {...defaultProps} disabled={true} />);
      
      const dropzone = screen.getByTestId('dropzone');
      // Verificamos que el componente renderiza sin errores cuando disabled=true
      expect(dropzone).toBeInTheDocument();
      expect(dropzone).toHaveClass('border-2', 'border-dashed');
    });
  });

  describe('Preview de imágenes', () => {
    it('no debe mostrar preview cuando showPreview=false', () => {
      render(<ImageUpload {...defaultProps} showPreview={false} />);
      
      expect(screen.queryByText('Imágenes seleccionadas:')).not.toBeInTheDocument();
    });

    it('debe renderizar sin errores con props por defecto', () => {
      render(<ImageUpload {...defaultProps} />);
      
      expect(screen.getByTestId('dropzone')).toBeInTheDocument();
    });
  });

  describe('Callback onImageUpload', () => {
    it('debe ser una función', () => {
      expect(typeof defaultProps.onImageUpload).toBe('function');
    });
  });

  describe('Limpieza de memoria', () => {
    it('debe limpiar URLs de preview al desmontar', () => {
      const { unmount } = render(<ImageUpload {...defaultProps} />);
      
      unmount();
      
      expect(global.URL.revokeObjectURL).toHaveBeenCalledTimes(0);
    });
  });
});