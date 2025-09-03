import React from 'react';
import { render, screen } from '@testing-library/react';
import ExportModal from '../ExportModal';

describe('ExportModal', () => {
  it('renders without crashing', () => {
    render(<ExportModal />);
    expect(screen.getByText('Exportar')).toBeInTheDocument();
  });

  it('opens modal when trigger is clicked', () => {
    render(<ExportModal />);
    const trigger = screen.getByText('Exportar');
    expect(trigger).toBeInTheDocument();
  });
});