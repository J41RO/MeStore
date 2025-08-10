import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Button from '../Button';

describe('Button Component', () => {
  test('should render button with text content', () => {
    render(<Button>Click me</Button>);
    
    const button = screen.getByRole('button', { name: 'Click me' });
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent('Click me');
  });

  test('should handle onClick events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('should be disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(button).toHaveClass('disabled:opacity-50', 'disabled:cursor-not-allowed');
  });

  test('should not trigger onClick when disabled', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick} disabled>Disabled Button</Button>);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(handleClick).not.toHaveBeenCalled();
  });

  test('should apply primary variant styles by default', () => {
    render(<Button>Primary Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('btn-primary', 'focus:ring-primary-500');
  });

  test('should apply secondary variant styles', () => {
    render(<Button variant="secondary">Secondary Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('btn-secondary', 'focus:ring-secondary-500');
  });

  test('should apply outline variant styles', () => {
    render(<Button variant="outline">Outline Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('btn-outline-primary', 'focus:ring-primary-500');
  });

  test('should apply ghost variant styles', () => {
    render(<Button variant="ghost">Ghost Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('btn-ghost', 'focus:ring-primary-500');
  });

  test('should apply danger variant styles', () => {
    render(<Button variant="danger">Danger Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('bg-red-600', 'hover:bg-red-700', 'text-white', 'focus:ring-red-500');
  });

  test('should apply small size styles', () => {
    render(<Button size="sm">Small Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('px-3', 'py-1.5', 'text-sm', 'gap-1.5');
  });

  test('should apply medium size styles by default', () => {
    render(<Button>Medium Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('px-4', 'py-2', 'text-base', 'gap-2');
  });

  test('should apply large size styles', () => {
    render(<Button size="lg">Large Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('px-6', 'py-3', 'text-lg', 'gap-2.5');
  });

  test('should apply fullWidth styles', () => {
    render(<Button fullWidth>Full Width Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('w-full');
  });

  test('should apply custom className', () => {
    render(<Button className="custom-class">Custom Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('custom-class');
  });

  test('should handle loading state with spinner', () => {
    render(<Button loading>Loading Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    
    // Verificar que el spinner existe
    const spinner = button.querySelector('svg.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  test('should not show icon when loading', () => {
    const TestIcon = () => <span data-testid="test-icon">Icon</span>;
    render(<Button loading icon={<TestIcon />}>Loading Button</Button>);
    
    expect(screen.queryByTestId('test-icon')).not.toBeInTheDocument();
    expect(screen.getByRole('button').querySelector('svg.animate-spin')).toBeInTheDocument();
  });

  test('should render with icon when provided', () => {
    const TestIcon = () => <span data-testid="test-icon">Icon</span>;
    render(<Button icon={<TestIcon />}>Button with Icon</Button>);
    
    expect(screen.getByTestId('test-icon')).toBeInTheDocument();
    expect(screen.getByText('Button with Icon')).toBeInTheDocument();
  });

  test('should apply base classes for accessibility', () => {
    render(<Button>Accessible Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass(
      'inline-flex',
      'items-center', 
      'justify-center',
      'font-medium',
      'rounded-md',
      'transition-all',
      'focus:outline-none',
      'focus:ring-2',
      'focus:ring-offset-2'
    );
  });

  test('should support different button types', () => {
    render(<Button type="submit">Submit Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('type', 'submit');
  });

  test('should pass through HTML button attributes', () => {
    render(
      <Button 
        aria-label="Accessible button"
        aria-describedby="button-description"
        data-testid="custom-button"
      >
        Button with attributes
      </Button>
    );
    
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-label', 'Accessible button');
    expect(button).toHaveAttribute('aria-describedby', 'button-description');
    expect(button).toHaveAttribute('data-testid', 'custom-button');
  });
});
