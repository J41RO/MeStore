import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import VendorInfo from './VendorInfo';

const mockVendorInfo = {
  id: 1,
  business_name: 'Test Vendor',
  email: 'test@vendor.com',
  created_at: '2023-01-01T00:00:00Z'
};

const renderVendorInfo = (vendorInfo = mockVendorInfo) => {
  return render(
    <BrowserRouter>
      <VendorInfo
        vendorId={vendorInfo.id}
        vendorName={vendorInfo.business_name}
        vendorInfo={vendorInfo}
      />
    </BrowserRouter>
  );
};

describe('VendorInfo', () => {
  it('renders vendor basic information', () => {
    renderVendorInfo();
    
    expect(screen.getByText('Test Vendor')).toBeInTheDocument();
    expect(screen.getByText(/como vendedor/)).toBeInTheDocument();
  });

  it('shows vendor rating and reviews', () => {
    renderVendorInfo();
    
    expect(screen.getByText('4.2')).toBeInTheDocument();
    expect(screen.getByText('(18 reseñas)')).toBeInTheDocument();
  });

  it('displays vendor stats', () => {
    renderVendorInfo();
    
    expect(screen.getByText('42')).toBeInTheDocument();
    expect(screen.getByText('Productos')).toBeInTheDocument();
    expect(screen.getByText('96%')).toBeInTheDocument();
    expect(screen.getByText('Satisfacción')).toBeInTheDocument();
    expect(screen.getByText('24h')).toBeInTheDocument();
    expect(screen.getByText('Tiempo respuesta')).toBeInTheDocument();
  });

  it('shows action buttons', () => {
    renderVendorInfo();
    
    expect(screen.getByText('Ver más productos de este vendedor')).toBeInTheDocument();
    expect(screen.getByText('Contactar vendedor')).toBeInTheDocument();
  });

  it('shows trust badges', () => {
    renderVendorInfo();
    
    expect(screen.getByText('Vendedor verificado')).toBeInTheDocument();
    expect(screen.getByText('Responde rápido')).toBeInTheDocument();
    expect(screen.getByText('Envío confiable')).toBeInTheDocument();
  });

  it('handles vendor without email', () => {
    const vendorWithoutEmail = {
      ...mockVendorInfo,
      email: undefined
    };
    
    renderVendorInfo(vendorWithoutEmail);
    
    // Should not show contact button when no email
    expect(screen.queryByText('Contactar vendedor')).not.toBeInTheDocument();
  });

  it('calculates time as vendor correctly', () => {
    // Test with recent date (should show as days)
    const recentVendor = {
      ...mockVendorInfo,
      created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString() // 5 days ago
    };
    
    renderVendorInfo(recentVendor);
    expect(screen.getByText(/\d+ días? como vendedor/)).toBeInTheDocument();
  });

  it('handles contact vendor click', () => {
    renderVendorInfo();
    
    const contactButton = screen.getByText('Contactar vendedor');
    expect(contactButton).toBeInTheDocument();
    
    // Test that the button is clickable (does not throw)
    expect(() => fireEvent.click(contactButton)).not.toThrow();
  });

  it('shows vendor icon', () => {
    renderVendorInfo();
    
    // Check for the store icon (by checking the parent div classes)
    const iconContainer = screen.getByRole('heading', { name: 'Test Vendor' }).closest('div')
      ?.parentElement?.querySelector('.bg-blue-100');
    expect(iconContainer).toBeInTheDocument();
  });

  it('shows additional info message', () => {
    renderVendorInfo();
    
    expect(screen.getByText(/Todos los vendedores en MeStore son verificados/)).toBeInTheDocument();
  });
});