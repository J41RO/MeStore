// ---------------------------------------------------------------------------------------------
// ImageGallery.test.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - ImageGallery Component Tests
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: ImageGallery.test.tsx
// Ruta: ~/src/components/ui/ImageGallery/__tests__/ImageGallery.test.tsx
// Autor: IA Desarrolladora Universal
// Fecha de Creación: 2025-08-19
// Última Actualización: 2025-08-19
// Versión: 1.0.0
// Propósito: Tests unitarios para el componente ImageGallery
//            Cobertura de funcionalidad selección múltiple, drag & drop y filtros
//
// Modificaciones:
// 2025-08-19 - Creación inicial con tests básicos de render y funcionalidad
//
// ---------------------------------------------------------------------------------------------

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import ImageGallery from '../ImageGallery';
import { ImageGalleryProps, GalleryImage } from '../ImageGallery.types';

// Mock data para tests
const mockImages: GalleryImage[] = [
  {
    id: '1',
    url: 'https://example.com/image1.jpg',
    thumbnail: 'https://example.com/thumb1.jpg',
    name: 'Imagen 1',
    size: 1024000,
    createdAt: new Date('2025-01-01'),
    selected: false,
    favorite: false,
    metadata: { width: 800, height: 600, type: 'image/jpeg' },
  },
  {
    id: '2',
    url: 'https://example.com/image2.jpg',
    thumbnail: 'https://example.com/thumb2.jpg',
    name: 'Imagen 2',
    size: 2048000,
    createdAt: new Date('2025-01-02'),
    selected: false,
    favorite: true,
    metadata: { width: 1200, height: 800, type: 'image/png' },
  },
];

describe('ImageGallery', () => {
  let defaultProps: ImageGalleryProps;

  beforeEach(() => {
    defaultProps = {
      images: mockImages,
      viewMode: 'grid',
      allowMultiSelect: true,
      allowReorder: true,
      onSelectionChange: jest.fn(),
      onReorder: jest.fn(),
      onDelete: jest.fn(),
      onToggleFavorite: jest.fn(),
      onSearch: jest.fn(),
    };
  });

  it('renderiza correctamente con imágenes', () => {
    render(<ImageGallery {...defaultProps} />);

    // Verificar que las imágenes se renderizan
    expect(screen.getByAltText('Imagen 1')).toBeInTheDocument();
    expect(screen.getByAltText('Imagen 2')).toBeInTheDocument();

    // Verificar que el toolbar está presente
    expect(
      screen.getByPlaceholderText('Buscar imágenes...')
    ).toBeInTheDocument();

    // Verificar botones de vista
    expect(screen.getByText('Grid')).toBeInTheDocument();
    expect(screen.getByText('List')).toBeInTheDocument();
    expect(screen.getByText('Masonry')).toBeInTheDocument();
  });

  it('permite búsqueda de imágenes', () => {
    const mockOnSearch = jest.fn();
    render(<ImageGallery {...defaultProps} onSearch={mockOnSearch} />);

    const searchInput = screen.getByPlaceholderText('Buscar imágenes...');
    fireEvent.change(searchInput, { target: { value: 'Imagen 1' } });

    expect(mockOnSearch).toHaveBeenCalledWith('Imagen 1');
  });

  it('permite selección múltiple cuando está habilitada', () => {
    const mockOnSelectionChange = jest.fn();
    render(
      <ImageGallery
        {...defaultProps}
        onSelectionChange={mockOnSelectionChange}
      />
    );

    // Buscar checkboxes de selección
    const checkboxes = screen.getAllByRole('checkbox');
    expect(checkboxes).toHaveLength(2);

    // Simular click en checkbox
    fireEvent.click(checkboxes[0]);

    expect(mockOnSelectionChange).toHaveBeenCalled();
  });

  it('muestra botones de acción masiva cuando hay selección múltiple', () => {
    render(<ImageGallery {...defaultProps} />);

    expect(screen.getByText('Seleccionar Todo')).toBeInTheDocument();
    expect(screen.getByText('Limpiar')).toBeInTheDocument();
  });

  it('cambia modo de vista correctamente', () => {
    render(<ImageGallery {...defaultProps} />);

    const listButton = screen.getByText('List');
    fireEvent.click(listButton);

    // Verificar que el botón List está activo (debería tener clase bg-blue-500)
    expect(listButton).toHaveClass('bg-blue-500');
  });

  it('muestra mensaje cuando no hay imágenes', () => {
    render(<ImageGallery {...defaultProps} images={[]} />);

    expect(
      screen.getByText('No hay imágenes para mostrar')
    ).toBeInTheDocument();
  });

  it('muestra mensaje cuando no hay resultados de búsqueda', () => {
    render(<ImageGallery {...defaultProps} />);

    const searchInput = screen.getByPlaceholderText('Buscar imágenes...');
    fireEvent.change(searchInput, { target: { value: 'imagen inexistente' } });

    expect(
      screen.getByText(
        'No se encontraron imágenes que coincidan con la búsqueda'
      )
    ).toBeInTheDocument();
  });

  it('no muestra checkboxes cuando selección múltiple está deshabilitada', () => {
    render(<ImageGallery {...defaultProps} allowMultiSelect={false} />);

    const checkboxes = screen.queryAllByRole('checkbox');
    expect(checkboxes).toHaveLength(0);
  });
});
