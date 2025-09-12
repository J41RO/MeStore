import { render, screen, fireEvent } from '@testing-library/react';
import ProductImageGallery from './ProductImageGallery';

const mockImages = [
  {
    id: 1,
    image_url: 'https://example.com/image1.jpg',
    is_primary: true
  },
  {
    id: 2,
    image_url: 'https://example.com/image2.jpg',
    is_primary: false
  },
  {
    id: 3,
    image_url: 'https://example.com/image3.jpg',
    is_primary: false
  }
];

describe('ProductImageGallery', () => {
  it('renders without images', () => {
    render(<ProductImageGallery images={[]} productName="Test Product" />);
    expect(screen.getByText('Sin imagen')).toBeInTheDocument();
  });

  it('renders single image correctly', () => {
    const singleImage = [mockImages[0]];
    render(<ProductImageGallery images={singleImage} productName="Test Product" />);
    
    const image = screen.getByRole('img');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('alt', 'Test Product - Imagen 1');
  });

  it('renders multiple images with thumbnails', () => {
    render(<ProductImageGallery images={mockImages} productName="Test Product" />);
    
    // Should show main image
    const mainImage = screen.getByAltText('Test Product - Imagen 1');
    expect(mainImage).toBeInTheDocument();
    
    // Should show thumbnails
    const thumbnails = screen.getAllByAltText(/Test Product - Miniatura/);
    expect(thumbnails).toHaveLength(3);
    
    // Should show navigation indicators
    expect(screen.getByText('1 / 3')).toBeInTheDocument();
  });

  it('changes image when thumbnail is clicked', () => {
    render(<ProductImageGallery images={mockImages} productName="Test Product" />);
    
    // Initially shows first image
    expect(screen.getByText('1 / 3')).toBeInTheDocument();
    
    // Click second thumbnail
    const thumbnails = screen.getAllByAltText(/Test Product - Miniatura/);
    fireEvent.click(thumbnails[1]);
    
    // Should show second image
    expect(screen.getByText('2 / 3')).toBeInTheDocument();
  });

  it('navigates with arrow buttons', () => {
    render(<ProductImageGallery images={mockImages} productName="Test Product" />);
    
    // Initially shows first image
    expect(screen.getByText('1 / 3')).toBeInTheDocument();
    
    // Click next button
    const nextButton = screen.getByTitle('Siguiente imagen');
    fireEvent.click(nextButton);
    
    // Should show second image
    expect(screen.getByText('2 / 3')).toBeInTheDocument();
    
    // Click previous button
    const prevButton = screen.getByTitle('Imagen anterior');
    fireEvent.click(prevButton);
    
    // Should go back to first image
    expect(screen.getByText('1 / 3')).toBeInTheDocument();
  });

  it('shows zoom functionality', () => {
    render(<ProductImageGallery images={mockImages} productName="Test Product" />);
    
    const zoomButton = screen.getByTitle('Zoom in');
    expect(zoomButton).toBeInTheDocument();
    
    fireEvent.click(zoomButton);
    
    // After clicking, title should change to "Zoom out"
    expect(screen.getByTitle('Zoom out')).toBeInTheDocument();
  });

  it('handles image load errors', () => {
    const imageWithError = [
      {
        id: 1,
        image_url: 'invalid-url.jpg',
        is_primary: true
      }
    ];
    
    render(<ProductImageGallery images={imageWithError} productName="Test Product" />);
    
    const image = screen.getByRole('img');
    expect(image).toBeInTheDocument();
    
    // Test error handling - after error, the img should be replaced with placeholder
    fireEvent.error(image);
    
    // After error, component should show placeholder text instead of img
    expect(screen.getByText('Sin imagen')).toBeInTheDocument();
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  it('sorts images with primary first', () => {
    const unsortedImages = [
      {
        id: 2,
        image_url: 'https://example.com/image2.jpg',
        is_primary: false
      },
      {
        id: 1,
        image_url: 'https://example.com/image1.jpg',
        is_primary: true
      }
    ];
    
    render(<ProductImageGallery images={unsortedImages} productName="Test Product" />);
    
    // Primary image should be shown first
    const mainImage = screen.getByAltText('Test Product - Imagen 1');
    expect(mainImage).toHaveAttribute('src', expect.stringContaining('image1.jpg'));
  });
});