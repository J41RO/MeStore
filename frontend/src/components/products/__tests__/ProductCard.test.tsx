// ~/src/components/products/__tests__/ProductCard.test.tsx
// ---------------------------------------------------------------------------------------------
// MeStore - Tests Unitarios ProductCard Genérico
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: ProductCard.test.tsx
// Ruta: ~/src/components/products/__tests__/ProductCard.test.tsx
// Autor: Jairo
// Fecha de Creación: 2025-08-16
// Última Actualización: 2025-08-16
// Versión: 1.0.0
// Propósito: Tests unitarios para ProductCard genérico (grid/lista)
//
// Modificaciones:
// 2025-08-16 - Creación inicial de tests
//
// ---------------------------------------------------------------------------------------------

/**
 * Tests unitarios para ProductCard genérico
 *
 * Cobertura de tests:
 * - Vista Grid: Layout vertical, hover effects
 * - Vista Lista: Layout horizontal, responsive
 * - Props opcionales: showSKU, onProductClick
 * - Estados: Con/sin imagen, stock disponible/agotado
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProductCard from '../ProductCard';
import { Product } from '../../../types/api.types';

// Mock product data para tests
const mockProduct: Product = {
  id: 'test-product-1',
  name: 'Producto de Prueba',
  description: 'Descripción del producto de prueba para testing',
  price: 99999,
  stock: 15,
  category: 'Electrónicos',
  imageUrl: 'https://example.com/product-image.jpg',
  createdAt: '2025-01-01T00:00:00Z',
  updatedAt: '2025-01-01T00:00:00Z',
};

const mockProductWithoutImage: Product = {
  ...mockProduct,
  id: 'test-product-2',
  imageUrl: undefined,
};

const mockProductOutOfStock: Product = {
  ...mockProduct,
  id: 'test-product-3',
  stock: 0,
};

const mockProductLowStock: Product = {
  ...mockProduct,
  id: 'test-product-4',
  stock: 5,
};

describe('ProductCard Component', () => {
  describe('Vista Grid', () => {
    it('debería renderizar correctamente en vista grid', () => {
      render(<ProductCard product={mockProduct} viewMode='grid' />);

      expect(screen.getByText('Producto de Prueba')).toBeInTheDocument();
      expect(screen.getByText('$99,999')).toBeInTheDocument();
      expect(screen.getByText('15 disponibles')).toBeInTheDocument();
      expect(screen.getByText('Electrónicos')).toBeInTheDocument();
    });

    it('debería mostrar imagen en vista grid', () => {
      render(<ProductCard product={mockProduct} viewMode='grid' />);

      const image = screen.getByAltText('Producto de Prueba');
      expect(image).toBeInTheDocument();
      expect(image).toHaveAttribute(
        'src',
        'https://example.com/product-image.jpg'
      );
    });

    it('debería mostrar placeholder cuando no hay imagen en vista grid', () => {
      render(<ProductCard product={mockProductWithoutImage} viewMode='grid' />);

      expect(screen.getByText('📦')).toBeInTheDocument();
    });

    it('debería mostrar SKU cuando showSKU es true en vista grid', () => {
      render(
        <ProductCard product={mockProduct} viewMode='grid' showSKU={true} />
      );

      expect(screen.getByText('SKU: test-product-1')).toBeInTheDocument();
    });

    it('debería manejar estados de stock correctamente en vista grid', () => {
      // Stock alto (verde)
      const { rerender } = render(
        <ProductCard product={mockProduct} viewMode='grid' />
      );
      expect(screen.getByText('15 disponibles')).toHaveClass(
        'bg-green-100',
        'text-green-800'
      );

      // Stock bajo (amarillo)
      rerender(<ProductCard product={mockProductLowStock} viewMode='grid' />);
      expect(screen.getByText('5 disponibles')).toHaveClass(
        'bg-yellow-100',
        'text-yellow-800'
      );

      // Sin stock (rojo)
      rerender(<ProductCard product={mockProductOutOfStock} viewMode='grid' />);
      expect(screen.getByText('Agotado')).toHaveClass(
        'bg-red-100',
        'text-red-800'
      );
    });
  });

  describe('Vista Lista', () => {
    it('debería renderizar correctamente en vista lista', () => {
      render(<ProductCard product={mockProduct} viewMode='list' />);

      expect(screen.getByText('Producto de Prueba')).toBeInTheDocument();
      expect(
        screen.getByText('Descripción del producto de prueba para testing')
      ).toBeInTheDocument();
      expect(screen.getByText('$99,999')).toBeInTheDocument();
      expect(screen.getByText('15 disponibles')).toBeInTheDocument();
      expect(screen.getByText('Electrónicos')).toBeInTheDocument();
    });

    it('debería mostrar imagen en vista lista', () => {
      render(<ProductCard product={mockProduct} viewMode='list' />);

      const image = screen.getByAltText('Producto de Prueba');
      expect(image).toBeInTheDocument();
      expect(image).toHaveAttribute(
        'src',
        'https://example.com/product-image.jpg'
      );
    });

    it('debería mostrar placeholder cuando no hay imagen en vista lista', () => {
      render(<ProductCard product={mockProductWithoutImage} viewMode='list' />);

      expect(screen.getByText('📦')).toBeInTheDocument();
    });

    it('debería mostrar SKU cuando showSKU es true en vista lista', () => {
      render(
        <ProductCard product={mockProduct} viewMode='list' showSKU={true} />
      );

      expect(screen.getByText('SKU: test-product-1')).toBeInTheDocument();
    });
  });

  describe('Interacciones', () => {
    it('debería llamar onProductClick cuando se hace click en el card', () => {
      const mockOnProductClick = jest.fn();

      render(
        <ProductCard
          product={mockProduct}
          viewMode='grid'
          onProductClick={mockOnProductClick}
        />
      );

      // Buscar cualquier elemento clickeable y hacer click
      const productName = screen.getByText('Producto de Prueba');
      fireEvent.click(productName);
      expect(mockOnProductClick).toHaveBeenCalledWith(mockProduct);
    });

    it('debería aplicar hover effects en ambas vistas', () => {
      const { rerender } = render(
        <ProductCard product={mockProduct} viewMode='grid' />
      );

      // Vista grid - verificar que el componente se renderiza
      expect(screen.getByText('Producto de Prueba')).toBeInTheDocument();

      // Vista lista - verificar que el componente se renderiza
      rerender(<ProductCard product={mockProduct} viewMode='list' />);

      expect(screen.getByText('Producto de Prueba')).toBeInTheDocument();
    });
  });

  describe('Props Opcionales', () => {
    it('debería aplicar className personalizado', () => {
      render(
        <ProductCard
          product={mockProduct}
          viewMode='grid'
          className='custom-class'
        />
      );

      // Verificar que se puede aplicar className personalizado
      expect(screen.getByText('Producto de Prueba')).toBeInTheDocument();
    });

    it('no debería mostrar SKU por defecto', () => {
      render(<ProductCard product={mockProduct} viewMode='grid' />);

      expect(screen.queryByText('SKU: test-product-1')).not.toBeInTheDocument();
    });

    it('no debería llamar onProductClick si no se proporciona', () => {
      // No debería crashear sin onProductClick
      render(<ProductCard product={mockProduct} viewMode='grid' />);

      const productName = screen.getByText('Producto de Prueba');
      expect(() => fireEvent.click(productName)).not.toThrow();
    });
  });

  describe('Formateo de Datos', () => {
    it('debería formatear precios correctamente', () => {
      const expensiveProduct: Product = {
        ...mockProduct,
        price: 1234567,
      };

      render(<ProductCard product={expensiveProduct} viewMode='grid' />);

      expect(screen.getByText('$1,234,567')).toBeInTheDocument();
    });

    it('debería manejar descripciones largas en vista lista', () => {
      const longDescProduct: Product = {
        ...mockProduct,
        description:
          'Esta es una descripción muy larga que debería ser truncada correctamente en la vista lista para mantener el diseño limpio y legible',
      };

      render(<ProductCard product={longDescProduct} viewMode='list' />);

      const description = screen.getByText(/Esta es una descripción muy larga/);
      expect(description).toHaveClass('line-clamp-2');
    });
  });
});
