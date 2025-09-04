import React, { useState } from 'react';
import Card from './ui/Card/Card';
import Button from './ui/Button/Button';
import Input from './ui/Input/Input';

const ResponsiveDemo: React.FC = () => {
  const [inputValue, setInputValue] = useState('');

  return (
    <div className='min-h-screen bg-neutral-50 p-4 sm:p-6 lg:p-8'>
      {/* Header responsivo */}
      <div className='max-w-7xl mx-auto mb-6 sm:mb-8 lg:mb-12'>
        <h1 className='text-2xl sm:text-3xl lg:text-4xl font-bold text-neutral-900 mb-2'>
          Componentes UI Responsivos
        </h1>
        <p className='text-sm sm:text-base lg:text-lg text-neutral-600'>
          Demostración de utility-first responsive design con Tailwind CSS
        </p>
      </div>

      {/* Grid responsivo principal: 1 → 2 → 3 columnas */}
      <div className='max-w-7xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8 mb-8'>
        {/* Card Demo */}
        <Card variant='elevated'>
          <Card.Header>
            <h3 className='text-lg sm:text-xl font-semibold'>
              Card Responsivo
            </h3>
          </Card.Header>
          <Card.Body>
            <p className='text-sm sm:text-base text-neutral-600 mb-4'>
              Padding adaptativo: px-4 sm:px-6, py-3 sm:py-4
            </p>
            <div className='text-xs sm:text-sm text-neutral-500'>
              Border radius: rounded-md sm:rounded-lg
            </div>
          </Card.Body>
          <Card.Footer>
            <Button size='sm' fullWidth>
              Card Action
            </Button>
          </Card.Footer>
        </Card>

        {/* Button Demo */}
        <Card variant='outlined'>
          <Card.Header>
            <h3 className='text-lg sm:text-xl font-semibold'>
              Buttons Responsivos
            </h3>
          </Card.Header>
          <Card.Body>
            <div className='space-y-3'>
              <Button size='sm' variant='primary' fullWidth>
                Small: px-2 sm:px-3
              </Button>
              <Button size='md' variant='secondary' fullWidth>
                Medium: px-3 sm:px-4
              </Button>
              <Button size='lg' variant='outline' fullWidth>
                Large: px-4 sm:px-6
              </Button>
            </div>
          </Card.Body>
        </Card>

        {/* Input Demo */}
        <Card variant='default'>
          <Card.Header>
            <h3 className='text-lg sm:text-xl font-semibold'>
              Inputs Responsivos
            </h3>
          </Card.Header>
          <Card.Body>
            <div className='space-y-4'>
              <Input
                size='sm'
                label='Input Small'
                placeholder='text-xs sm:text-sm'
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
              />
              <Input
                size='md'
                label='Input Medium'
                placeholder='text-sm sm:text-base'
                helper='Labels y helper text también responsivos'
              />
            </div>
          </Card.Body>
        </Card>
      </div>

      {/* Grid Pattern 2: 1 → 2 → 4 columnas */}
      <div className='max-w-7xl mx-auto mb-8'>
        <h2 className='text-xl sm:text-2xl font-bold text-neutral-900 mb-4 sm:mb-6'>
          Grid Pattern: 1 → 2 → 4
        </h2>
        <div className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4'>
          {[1, 2, 3, 4].map(num => (
            <Card key={num} variant='flat'>
              <Card.Body>
                <div className='text-center py-4'>
                  <div className='text-lg sm:text-xl font-bold text-primary-600'>
                    {num}
                  </div>
                  <div className='text-xs sm:text-sm text-neutral-600'>
                    Grid Item
                  </div>
                </div>
              </Card.Body>
            </Card>
          ))}
        </div>
      </div>

      {/* Grid Pattern 3: 1 → 3 → 6 columnas */}
      <div className='max-w-7xl mx-auto mb-8'>
        <h2 className='text-xl sm:text-2xl font-bold text-neutral-900 mb-4 sm:mb-6'>
          Grid Pattern: 1 → 3 → 6
        </h2>
        <div className='grid grid-cols-1 md:grid-cols-3 xl:grid-cols-6 gap-3 sm:gap-4'>
          {[1, 2, 3, 4, 5, 6].map(num => (
            <Card key={num} variant='outlined'>
              <Card.Body>
                <div className='text-center py-2'>
                  <div className='text-sm font-semibold'>Item {num}</div>
                </div>
              </Card.Body>
            </Card>
          ))}
        </div>
      </div>

      {/* Responsive Typography Demo */}
      <div className='max-w-7xl mx-auto'>
        <Card variant='elevated'>
          <Card.Header>
            <h3 className='text-lg sm:text-xl font-semibold'>
              Typography Responsiva
            </h3>
          </Card.Header>
          <Card.Body>
            <div className='space-y-4'>
              <p className='text-xs sm:text-sm text-neutral-600'>
                Texto pequeño que se adapta: text-xs sm:text-sm
              </p>
              <p className='text-sm sm:text-base text-neutral-700'>
                Texto base que crece: text-sm sm:text-base
              </p>
              <p className='text-base sm:text-lg text-neutral-800'>
                Texto grande que escala: text-base sm:text-lg
              </p>
            </div>
          </Card.Body>
        </Card>
      </div>
    </div>
  );
};

export default ResponsiveDemo;
