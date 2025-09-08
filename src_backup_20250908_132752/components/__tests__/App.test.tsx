import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../../App';

describe('App Component', () => {
  test('renders without crashing', () => {
    render(<App />);
  });

  test('displays Vite + React heading', () => {
    render(<App />);
    const heading = screen.getByText('Vite + React');
    expect(heading).toBeInTheDocument();
  });

  test('displays initial count button', () => {
    render(<App />);
    const button = screen.getByText('count is 0');
    expect(button).toBeInTheDocument();
  });

  test('displays edit instruction text', () => {
    render(<App />);
    const instruction = screen.getByText(/Edit.*src\/App\.tsx.*and save to test HMR/);
    expect(instruction).toBeInTheDocument();
  });

  test('displays read-the-docs text', () => {
    render(<App />);
    const docsText = screen.getByText('Click on the Vite and React logos to learn more');
    expect(docsText).toBeInTheDocument();
  });
});
