import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import Input from '../Input';

describe('Input Component', () => {
  test('should render input with placeholder', () => {
    render(<Input placeholder='Enter your email' />);

    const input = screen.getByPlaceholderText('Enter your email');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('placeholder', 'Enter your email');
  });

  test('should handle text input and onChange events', async () => {
    const user = userEvent.setup();
    const handleChange = jest.fn();

    render(<Input onChange={handleChange} placeholder='Type here' />);

    const input = screen.getByPlaceholderText('Type here');
    await user.type(input, 'Hello World');

    expect(input).toHaveValue('Hello World');
    expect(handleChange).toHaveBeenCalled();
  });

  test('should render with default value', () => {
    render(<Input defaultValue='Default text' />);

    const input = screen.getByDisplayValue('Default text');
    expect(input).toBeInTheDocument();
    expect(input).toHaveValue('Default text');
  });

  test('should be disabled when disabled prop is true', () => {
    render(<Input disabled placeholder='Disabled input' />);

    const input = screen.getByPlaceholderText('Disabled input');
    expect(input).toBeDisabled();
  });

  test('should apply error styles when error prop is provided', () => {
    render(<Input error='This field is required' placeholder='Error input' />);

    const input = screen.getByPlaceholderText('Error input');
    expect(input).toHaveClass(
      'border-red-500',
      'focus:border-red-500',
      'focus:ring-red-500'
    );
  });

  test('should display error message when error prop is provided', () => {
    render(<Input error='Email is required' placeholder='Email' />);

    expect(screen.getByText('Email is required')).toBeInTheDocument();
    const errorMsg = screen.getByText('Email is required');
    expect(errorMsg).toHaveClass('text-red-600');
  });

  test('should render different input types', () => {
    const { rerender } = render(
      <Input type='email' data-testid='email-input' />
    );
    expect(screen.getByTestId('email-input')).toHaveAttribute('type', 'email');

    rerender(<Input type='password' data-testid='password-input' />);
    expect(screen.getByTestId('password-input')).toHaveAttribute(
      'type',
      'password'
    );

    rerender(<Input type='number' data-testid='number-input' />);
    expect(screen.getByTestId('number-input')).toHaveAttribute(
      'type',
      'number'
    );
  });

  test('should be required when required prop is true', () => {
    render(<Input required placeholder='Required field' />);

    const input = screen.getByPlaceholderText('Required field');
    expect(input).toBeRequired();
  });

  test('should render with label when provided', () => {
    render(<Input label='Email Address' placeholder='Enter email' />);

    expect(screen.getByText('Email Address')).toBeInTheDocument();
    expect(screen.getByLabelText('Email Address')).toBeInTheDocument();
  });

  test('should apply small size styles', () => {
    render(<Input size='sm' placeholder='Small input' />);

    const input = screen.getByPlaceholderText('Small input');
    expect(input).toHaveClass(
      'px-2',
      'sm:px-2.5',
      'py-1',
      'sm:py-1.5',
      'text-xs',
      'sm:text-sm'
    );
  });

  test('should apply medium size styles by default', () => {
    render(<Input placeholder='Medium input' />);

    const input = screen.getByPlaceholderText('Medium input');
    expect(input).toHaveClass(
      'px-2.5',
      'sm:px-3',
      'py-1.5',
      'sm:py-2',
      'text-sm',
      'sm:text-base'
    );
  });

  test('should apply large size styles', () => {
    render(<Input size='lg' placeholder='Large input' />);

    const input = screen.getByPlaceholderText('Large input');
    expect(input).toHaveClass(
      'px-3',
      'sm:px-4',
      'py-2',
      'sm:py-3',
      'text-base',
      'sm:text-lg'
    );
  });

  test('should handle focus and blur events', async () => {
    const user = userEvent.setup();
    const handleFocus = jest.fn();
    const handleBlur = jest.fn();

    render(
      <Input
        onFocus={handleFocus}
        onBlur={handleBlur}
        placeholder='Focus test'
      />
    );

    const input = screen.getByPlaceholderText('Focus test');

    await user.click(input);
    expect(handleFocus).toHaveBeenCalledTimes(1);

    await user.tab();
    expect(handleBlur).toHaveBeenCalledTimes(1);
  });

  test('should apply custom className', () => {
    render(<Input className='custom-input-class' placeholder='Custom input' />);

    const input = screen.getByPlaceholderText('Custom input');
    expect(input).toHaveClass('custom-input-class');
  });

  test('should render with helper text when provided', () => {
    render(
      <Input
        placeholder='Password'
        helper='Password must be at least 8 characters'
      />
    );

    expect(
      screen.getByText('Password must be at least 8 characters')
    ).toBeInTheDocument();
    const helperText = screen.getByText(
      'Password must be at least 8 characters'
    );
    expect(helperText).toHaveClass('text-neutral-500');
  });

  test('should handle controlled input with value prop', async () => {
    const user = userEvent.setup();
    const handleChange = jest.fn();

    const ControlledInput = () => {
      const [value, setValue] = React.useState('');
      return (
        <Input
          value={value}
          onChange={e => {
            setValue(e.target.value);
            handleChange(e);
          }}
          placeholder='Controlled input'
        />
      );
    };

    render(<ControlledInput />);

    const input = screen.getByPlaceholderText('Controlled input');
    await user.type(input, 'Test');

    expect(input).toHaveValue('Test');
    expect(handleChange).toHaveBeenCalled();
  });

  test('should apply success state styles', () => {
    render(<Input state='success' placeholder='Success input' />);

    const input = screen.getByPlaceholderText('Success input');
    expect(input).toHaveClass(
      'border-green-500',
      'focus:border-green-500',
      'focus:ring-green-500'
    );
  });

  test('should apply default state styles', () => {
    render(<Input state='default' placeholder='Default input' />);

    const input = screen.getByPlaceholderText('Default input');
    expect(input).toHaveClass(
      'border-neutral-300',
      'focus:border-primary-500',
      'focus:ring-primary-500'
    );
  });

  test('should render with icon when provided', () => {
    const TestIcon = () => <span data-testid='input-icon'>📧</span>;
    render(<Input icon={<TestIcon />} placeholder='Input with icon' />);

    expect(screen.getByTestId('input-icon')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Input with icon')).toBeInTheDocument();
  });

  test('should apply icon padding when icon is provided', () => {
    const TestIcon = () => <span data-testid='input-icon'>📧</span>;
    render(<Input icon={<TestIcon />} placeholder='Input with icon' />);

    const input = screen.getByPlaceholderText('Input with icon');
    expect(input).toHaveClass('pl-10');
  });

  test('should apply fullWidth styles by default', () => {
    const { container } = render(<Input placeholder='Full width input' />);

    const wrapper = container.firstChild;
    expect(wrapper).toHaveClass('w-full');
  });

  test('should not show helper text when error is present', () => {
    render(
      <Input
        error='This field is required'
        helper='This is helper text'
        placeholder='Input with error and helper'
      />
    );

    expect(screen.getByText('This field is required')).toBeInTheDocument();
    expect(screen.queryByText('This is helper text')).not.toBeInTheDocument();
  });

  test('should generate unique ID when not provided', () => {
    render(<Input label='Test Label' placeholder='Auto ID input' />);

    const input = screen.getByPlaceholderText('Auto ID input');
    const label = screen.getByText('Test Label');

    expect(input).toHaveAttribute('id');
    expect(label).toHaveAttribute('for', input.getAttribute('id'));
  });

  test('should use provided ID when given', () => {
    render(
      <Input
        id='custom-id'
        label='Custom ID Label'
        placeholder='Custom ID input'
      />
    );

    const input = screen.getByPlaceholderText('Custom ID input');
    const label = screen.getByText('Custom ID Label');

    expect(input).toHaveAttribute('id', 'custom-id');
    expect(label).toHaveAttribute('for', 'custom-id');
  });
});
