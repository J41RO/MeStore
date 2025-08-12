import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Card from '../Card';

describe('Card Component', () => {
  test('should render card with children content', () => {
    render(
      <Card>
        <h3>Card Title</h3>
        <p>Card content goes here</p>
      </Card>
    );
    
    expect(screen.getByText('Card Title')).toBeInTheDocument();
    expect(screen.getByText('Card content goes here')).toBeInTheDocument();
  });

  test('should apply default card styles', () => {
    render(
      <Card data-testid="default-card">
        <p>Default card</p>
      </Card>
    );
    
    const card = screen.getByTestId('default-card');
    expect(card).toHaveClass('rounded-md', 'sm:rounded-lg', 'overflow-hidden', 'card-mestocker');
  });

  test('should apply outlined variant styles', () => {
    render(
      <Card variant="outlined" data-testid="outlined-card">
        <p>Outlined card</p>
      </Card>
    );
    
    const card = screen.getByTestId('outlined-card');
    expect(card).toHaveClass('border-2', 'border-neutral-200', 'bg-white');
  });

  test('should apply elevated variant styles', () => {
    render(
      <Card variant="elevated" data-testid="elevated-card">
        <p>Elevated card</p>
      </Card>
    );
    
    const card = screen.getByTestId('elevated-card');
    expect(card).toHaveClass('shadow-mestocker-lg', 'bg-white', 'border', 'border-neutral-100');
  });

  test('should apply flat variant styles', () => {
    render(
      <Card variant="flat" data-testid="flat-card">
        <p>Flat card</p>
      </Card>
    );
    
    const card = screen.getByTestId('flat-card');
    expect(card).toHaveClass('bg-neutral-50');
  });

  test('should apply custom className', () => {
    render(
      <Card className="custom-card-class" data-testid="custom-card">
        <p>Custom styled card</p>
      </Card>
    );
    
    const card = screen.getByTestId('custom-card');
    expect(card).toHaveClass('custom-card-class');
    expect(card).toHaveClass('card-mestocker'); // Should keep default classes
  });

  test('should pass through HTML div attributes', () => {
    render(
      <Card 
        role="article"
        aria-label="Product card"
        data-testid="accessible-card"
      >
        <p>Accessible card content</p>
      </Card>
    );
    
    const card = screen.getByTestId('accessible-card');
    expect(card).toHaveAttribute('role', 'article');
    expect(card).toHaveAttribute('aria-label', 'Product card');
  });

  test('should render Card.Header with proper styles', () => {
    render(
      <Card>
        <Card.Header data-testid="card-header">
          <h3>Card Header</h3>
        </Card.Header>
      </Card>
    );
    
    const header = screen.getByTestId('card-header');
    expect(header).toBeInTheDocument();
    expect(header).toHaveClass('px-4', 'sm:px-6', 'py-3', 'sm:py-4', 'border-b', 'border-neutral-200');
    expect(screen.getByText('Card Header')).toBeInTheDocument();
  });

  test('should render Card.Body with proper styles', () => {
    render(
      <Card>
        <Card.Body data-testid="card-body">
          <p>Card body content</p>
        </Card.Body>
      </Card>
    );
    
    const body = screen.getByTestId('card-body');
    expect(body).toBeInTheDocument();
    expect(body).toHaveClass('px-4', 'sm:px-6', 'py-3', 'sm:py-4');
    expect(screen.getByText('Card body content')).toBeInTheDocument();
  });

  test('should render Card.Footer with proper styles', () => {
    render(
      <Card>
        <Card.Footer data-testid="card-footer">
          <button>Save</button>
          <button>Cancel</button>
        </Card.Footer>
      </Card>
    );
    
    const footer = screen.getByTestId('card-footer');
    expect(footer).toBeInTheDocument();
    expect(footer).toHaveClass('px-4', 'sm:px-6', 'py-3', 'sm:py-4', 'border-t', 'border-neutral-200', 'bg-neutral-50');
    expect(screen.getByText('Save')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  test('should render complete card with all compound components', () => {
    render(
      <Card data-testid="complete-card">
        <Card.Header data-testid="header">
          <h3>Product Card</h3>
        </Card.Header>
        <Card.Body data-testid="body">
          <p>Product description goes here</p>
        </Card.Body>
        <Card.Footer data-testid="footer">
          <button>Buy Now</button>
        </Card.Footer>
      </Card>
    );
    
    expect(screen.getByTestId('complete-card')).toBeInTheDocument();
    expect(screen.getByTestId('header')).toBeInTheDocument();
    expect(screen.getByTestId('body')).toBeInTheDocument();
    expect(screen.getByTestId('footer')).toBeInTheDocument();
    expect(screen.getByText('Product Card')).toBeInTheDocument();
    expect(screen.getByText('Product description goes here')).toBeInTheDocument();
    expect(screen.getByText('Buy Now')).toBeInTheDocument();
  });

  test('should allow custom className on Header component', () => {
    render(
      <Card>
        <Card.Header className="custom-header-class" data-testid="custom-header">
          <h3>Custom Header</h3>
        </Card.Header>
      </Card>
    );
    
    const header = screen.getByTestId('custom-header');
    expect(header).toHaveClass('custom-header-class');
    expect(header).toHaveClass('px-4', 'sm:px-6', 'py-3', 'sm:py-4'); // Should keep default classes
  });

  test('should allow custom className on Body component', () => {
    render(
      <Card>
        <Card.Body className="custom-body-class" data-testid="custom-body">
          <p>Custom body</p>
        </Card.Body>
      </Card>
    );
    
    const body = screen.getByTestId('custom-body');
    expect(body).toHaveClass('custom-body-class');
    expect(body).toHaveClass('px-4', 'sm:px-6', 'py-3', 'sm:py-4'); // Should keep default classes
  });

  test('should allow custom className on Footer component', () => {
    render(
      <Card>
        <Card.Footer className="custom-footer-class" data-testid="custom-footer">
          <p>Custom footer</p>
        </Card.Footer>
      </Card>
    );
    
    const footer = screen.getByTestId('custom-footer');
    expect(footer).toHaveClass('custom-footer-class');
    expect(footer).toHaveClass('px-4', 'sm:px-6', 'py-3', 'sm:py-4'); // Should keep default classes
  });

  test('should handle click events when passed to main Card', () => {
    const handleClick = jest.fn();
    
    render(
      <Card onClick={handleClick} data-testid="clickable-card">
        <Card.Body>
          <p>Clickable card</p>
        </Card.Body>
      </Card>
    );
    
    const card = screen.getByTestId('clickable-card');
    fireEvent.click(card);
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('should pass HTML attributes to compound components', () => {
    render(
      <Card>
        <Card.Header 
          role="banner" 
          aria-label="Card header"
          data-testid="attr-header"
        >
          <h3>Header with attributes</h3>
        </Card.Header>
        <Card.Body 
          role="main"
          aria-label="Card content"
          data-testid="attr-body"
        >
          <p>Body with attributes</p>
        </Card.Body>
        <Card.Footer 
          role="contentinfo"
          aria-label="Card footer"
          data-testid="attr-footer"
        >
          <p>Footer with attributes</p>
        </Card.Footer>
      </Card>
    );
    
    const header = screen.getByTestId('attr-header');
    const body = screen.getByTestId('attr-body');
    const footer = screen.getByTestId('attr-footer');
    
    expect(header).toHaveAttribute('role', 'banner');
    expect(header).toHaveAttribute('aria-label', 'Card header');
    expect(body).toHaveAttribute('role', 'main');
    expect(body).toHaveAttribute('aria-label', 'Card content');
    expect(footer).toHaveAttribute('role', 'contentinfo');
    expect(footer).toHaveAttribute('aria-label', 'Card footer');
  });

  test('should work with mixed content and compound components', () => {
    render(
      <Card data-testid="mixed-card">
        <Card.Header>
          <h3>Mixed Card</h3>
        </Card.Header>
        <div className="custom-content">
          <p>Custom content outside compound components</p>
        </div>
        <Card.Footer>
          <button>Action</button>
        </Card.Footer>
      </Card>
    );
    
    expect(screen.getByTestId('mixed-card')).toBeInTheDocument();
    expect(screen.getByText('Mixed Card')).toBeInTheDocument();
    expect(screen.getByText('Custom content outside compound components')).toBeInTheDocument();
    expect(screen.getByText('Action')).toBeInTheDocument();
  });

  test('should render empty compound components gracefully', () => {
    render(
      <Card>
        <Card.Header data-testid="empty-header" />
        <Card.Body data-testid="empty-body" />
        <Card.Footer data-testid="empty-footer" />
      </Card>
    );
    
    expect(screen.getByTestId('empty-header')).toBeInTheDocument();
    expect(screen.getByTestId('empty-body')).toBeInTheDocument();
    expect(screen.getByTestId('empty-footer')).toBeInTheDocument();
  });
});