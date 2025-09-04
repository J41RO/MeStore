import React from 'react';

const ThemeExample: React.FC = () => {
  return (
    <div className='p-8 space-y-6'>
      <h1 className='text-3xl font-heading font-bold text-primary-600'>
        Tema MeStocker
      </h1>

      <div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
        <div className='card-mestocker'>
          <h3 className='text-lg font-semibold text-neutral-800 mb-2'>
            Colores Primarios
          </h3>
          <div className='space-y-2'>
            <div className='w-full h-8 bg-primary-500 rounded'></div>
            <div className='w-full h-8 bg-primary-600 rounded'></div>
            <div className='w-full h-8 bg-primary-700 rounded'></div>
          </div>
        </div>

        <div className='card-mestocker'>
          <h3 className='text-lg font-semibold text-neutral-800 mb-2'>
            Colores Secundarios
          </h3>
          <div className='space-y-2'>
            <div className='w-full h-8 bg-secondary-500 rounded'></div>
            <div className='w-full h-8 bg-secondary-600 rounded'></div>
            <div className='w-full h-8 bg-secondary-700 rounded'></div>
          </div>
        </div>

        <div className='card-mestocker'>
          <h3 className='text-lg font-semibold text-neutral-800 mb-2'>
            Colores Accent
          </h3>
          <div className='space-y-2'>
            <div className='w-full h-8 bg-accent-500 rounded'></div>
            <div className='w-full h-8 bg-mestocker-orange rounded'></div>
            <div className='w-full h-8 bg-mestocker-red rounded'></div>
          </div>
        </div>
      </div>

      <div className='space-y-4'>
        <h3 className='text-xl font-heading font-semibold'>Componentes</h3>
        <div className='flex space-x-4'>
          <button className='btn-primary'>Primary Button</button>
          <button className='btn-secondary'>Secondary Button</button>
          <input className='input-mestocker' placeholder='Input ejemplo' />
        </div>
      </div>

      <div className='space-y-2'>
        <h3 className='text-xl font-heading font-semibold'>Typography</h3>
        <p className='font-sans text-base'>Font Sans (Inter) - Body text</p>
        <p className='font-heading text-lg'>
          Font Heading (Poppins) - Headings
        </p>
        <p className='font-mono text-sm'>Font Mono (JetBrains) - Code</p>
      </div>
    </div>
  );
};

export default ThemeExample;
