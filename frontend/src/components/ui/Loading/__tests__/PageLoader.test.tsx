import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import PageLoader from '../PageLoader';

describe('PageLoader', () => {
  test('should render loading message', () => {
    render(<PageLoader />);
    expect(screen.getByText('Cargando página...')).toBeInTheDocument();
  });

  test('should have correct CSS classes for styling', () => {
    const { container } = render(<PageLoader />);
    const loadingContainer = container.firstChild as HTMLElement;
    expect(loadingContainer).toHaveClass(
      'flex',
      'items-center',
      'justify-center'
    );
  });

  test('should render spinner element', () => {
    const { container } = render(<PageLoader />);
    const spinner = container.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });
});
