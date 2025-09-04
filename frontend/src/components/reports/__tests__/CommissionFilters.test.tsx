import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import CommissionFilters from '../CommissionFilters';
import {
  CommissionStatus,
  PaymentMethod,
} from '../../../types/commission.types';

describe('CommissionFilters', () => {
  const mockOnFiltersChange = jest.fn();
  const mockOnClearFilters = jest.fn();

  const defaultProps = {
    filters: {},
    onFiltersChange: mockOnFiltersChange,
    onClearFilters: mockOnClearFilters,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders filter component', () => {
    render(<CommissionFilters {...defaultProps} />);

    expect(screen.getByText('Filtros')).toBeInTheDocument();
    expect(screen.getByText('Limpiar filtros')).toBeInTheDocument();
  });

  test('renders date range filters', () => {
    render(<CommissionFilters {...defaultProps} />);

    expect(screen.getByText('Rango de fechas')).toBeInTheDocument();
    expect(screen.getByLabelText('Fecha inicio')).toBeInTheDocument();
    expect(screen.getByLabelText('Fecha fin')).toBeInTheDocument();
  });

  test('renders status checkboxes', () => {
    render(<CommissionFilters {...defaultProps} />);

    expect(screen.getByText('Estado')).toBeInTheDocument();

    Object.values(CommissionStatus).forEach(status => {
      expect(screen.getByText(status)).toBeInTheDocument();
    });
  });

  test('renders payment method checkboxes', () => {
    render(<CommissionFilters {...defaultProps} />);

    expect(screen.getByText('Método de pago')).toBeInTheDocument();

    Object.values(PaymentMethod).forEach(method => {
      const displayText = method.replace('_', ' ');
      expect(screen.getByText(displayText)).toBeInTheDocument();
    });
  });

  test('calls onFiltersChange when status checkbox is clicked', () => {
    render(<CommissionFilters {...defaultProps} />);

    const pendingCheckbox = screen.getByRole('checkbox', { name: /pending/i });
    fireEvent.click(pendingCheckbox);

    expect(mockOnFiltersChange).toHaveBeenCalledWith({
      statuses: [CommissionStatus.PENDING],
    });
  });

  test('calls onFiltersChange when payment method checkbox is clicked', () => {
    render(<CommissionFilters {...defaultProps} />);

    const cashCheckbox = screen.getByRole('checkbox', { name: /cash/i });
    fireEvent.click(cashCheckbox);

    expect(mockOnFiltersChange).toHaveBeenCalledWith({
      paymentMethods: [PaymentMethod.CASH],
    });
  });

  test('calls onFiltersChange when search term changes', () => {
    render(<CommissionFilters {...defaultProps} />);

    const searchInput = screen.getByPlaceholderText(
      'Buscar por producto, orden, cliente...'
    );
    fireEvent.change(searchInput, { target: { value: 'test search' } });

    expect(mockOnFiltersChange).toHaveBeenCalledWith({
      searchTerm: 'test search',
    });
  });

  test('calls onClearFilters when clear button is clicked', () => {
    render(<CommissionFilters {...defaultProps} />);

    const clearButton = screen.getByText('Limpiar filtros');
    fireEvent.click(clearButton);

    expect(mockOnClearFilters).toHaveBeenCalled();
  });

  test('displays current filter values correctly', () => {
    const filtersWithValues = {
      statuses: [CommissionStatus.CONFIRMED],
      paymentMethods: [PaymentMethod.CREDIT_CARD],
      searchTerm: 'test product',
    };

    render(<CommissionFilters {...defaultProps} filters={filtersWithValues} />);

    const confirmedCheckbox = screen.getByRole('checkbox', {
      name: /confirmed/i,
    });
    expect(confirmedCheckbox).toBeChecked();

    const creditCardCheckbox = screen.getByRole('checkbox', {
      name: /credit card/i,
    });
    expect(creditCardCheckbox).toBeChecked();

    const searchInput = screen.getByDisplayValue('test product');
    expect(searchInput).toBeInTheDocument();
  });
});
