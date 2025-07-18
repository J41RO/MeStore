import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../../App';

describe('App Component', () => {
  test('renders App component without crashing', () => {
    render(<App />);
  });

  test('displays "Vite + React" heading', () => {
    render(<App />);
    const heading = screen.getByText('Vite + React');
    expect(heading).toBeInTheDocument();
  });

  test('displays initial count button with text "count is 0"', () => {
    render(<App />);
    const button = screen.getByText('count is 0');
    expect(button).toBeInTheDocument();
  });

  test('displays code filename in edit instruction', () => {
    render(<App />);
    const codeElement = screen.getByText('src/App.tsx');
    expect(codeElement).toBeInTheDocument();
  });

  test('displays "and save to test HMR" text', () => {
    render(<App />);
    const hmrText = screen.getByText(/and save to test HMR/);
    expect(hmrText).toBeInTheDocument();
  });

  test('displays read-the-docs text', () => {
    render(<App />);
    const docsText = screen.getByText('Click on the Vite and React logos to learn more');
    expect(docsText).toBeInTheDocument();
  });
});

import { fireEvent, waitFor } from '@testing-library/react';

describe('App Component - User Interactions', () => {
  test('increments count when button is clicked', async () => {
    render(<App />);
    
    // Encontrar el botón inicial con "count is 0"
    const countButton = screen.getByRole('button', { name: /count is 0/i });
    expect(countButton).toBeInTheDocument();
    
    // Simular click en el botón
    fireEvent.click(countButton);
    
    // Verificar que el texto cambió a "count is 1"
    await waitFor(() => {
      const updatedButton = screen.getByRole('button', { name: /count is 1/i });
      expect(updatedButton).toBeInTheDocument();
    });
  });

  test('count increases multiple times with multiple clicks', async () => {
    render(<App />);
    
    // Obtener el botón inicial
    let countButton = screen.getByRole('button', { name: /count is 0/i });
    
    // Hacer 3 clicks
    fireEvent.click(countButton);
    fireEvent.click(countButton);
    fireEvent.click(countButton);
    
    // Verificar que llegó a count is 3
    await waitFor(() => {
      const finalButton = screen.getByRole('button', { name: /count is 3/i });
      expect(finalButton).toBeInTheDocument();
    });
  });

  test('button maintains functionality after multiple interactions', async () => {
    render(<App />);
    
    // Verificar estado inicial
    expect(screen.getByRole('button', { name: /count is 0/i })).toBeInTheDocument();
    
    // Hacer varios clicks y verificar cada estado
    const button = screen.getByRole('button', { name: /count is 0/i });
    
    fireEvent.click(button);
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /count is 1/i })).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByRole('button', { name: /count is 1/i }));
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /count is 2/i })).toBeInTheDocument();
    });
    
    // Verificar que el componente sigue siendo interactivo
    const finalButton = screen.getByRole('button', { name: /count is 2/i });
    expect(finalButton).toBeEnabled();
  });
});
