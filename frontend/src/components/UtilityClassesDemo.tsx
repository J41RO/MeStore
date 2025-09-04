import React from 'react';

const UtilityClassesDemo: React.FC = () => {
  return (
    <div className='container-mestocker'>
      <div className='section-mestocker'>
        <h1 className='heading-mestocker text-3xl mb-8'>
          Utility Classes MeStocker
        </h1>

        {/* Buttons */}
        <div className='mb-8'>
          <h2 className='subheading-mestocker text-xl mb-4'>Botones</h2>
          <div className='flex flex-wrap gap-4'>
            <button className='btn-primary'>Primary</button>
            <button className='btn-secondary'>Secondary</button>
            <button className='btn-outline-primary'>Outline Primary</button>
            <button className='btn-outline-secondary'>Outline Secondary</button>
            <button className='btn-ghost'>Ghost</button>
            <button className='btn-disabled'>Disabled</button>
          </div>
        </div>

        {/* Badges */}
        <div className='mb-8'>
          <h2 className='subheading-mestocker text-xl mb-4'>Badges</h2>
          <div className='flex flex-wrap gap-4'>
            <span className='badge-mestocker'>Primary Badge</span>
            <span className='badge-secondary'>Secondary Badge</span>
            <span className='badge-success'>Success</span>
            <span className='badge-error'>Error</span>
            <span className='badge-warning'>Warning</span>
          </div>
        </div>

        {/* Alerts */}
        <div className='mb-8'>
          <h2 className='subheading-mestocker text-xl mb-4'>Alertas</h2>
          <div className='space-y-4'>
            <div className='alert-mestocker'>
              Esta es una alerta principal de MeStocker
            </div>
            <div className='alert-success'>
              ¡Operación completada exitosamente!
            </div>
            <div className='alert-error'>
              Ha ocurrido un error en el proceso
            </div>
            <div className='alert-warning'>
              Advertencia: Revisa los datos antes de continuar
            </div>
          </div>
        </div>

        {/* Cards */}
        <div className='mb-8'>
          <h2 className='subheading-mestocker text-xl mb-4'>Tarjetas</h2>
          <div className='grid-mestocker grid-cols-1 md:grid-cols-3'>
            <div className='card-mestocker'>
              <h3 className='text-mestocker-primary text-lg mb-2'>Card 1</h3>
              <p className='text-neutral-600'>
                Contenido de la primera tarjeta
              </p>
            </div>
            <div className='card-mestocker loading-mestocker'>
              <h3 className='text-mestocker-secondary text-lg mb-2'>Card 2</h3>
              <p className='text-neutral-600'>Tarjeta con efecto loading</p>
            </div>
            <div className='card-mestocker'>
              <h3 className='heading-mestocker text-lg mb-2'>Card 3</h3>
              <p className='text-neutral-600'>Tarjeta con heading branded</p>
            </div>
          </div>
        </div>

        {/* Forms */}
        <div className='mb-8'>
          <h2 className='subheading-mestocker text-xl mb-4'>Formularios</h2>
          <div className='card-mestocker max-w-md'>
            <div className='space-y-4'>
              <input
                className='input-mestocker w-full'
                placeholder='Input text'
              />
              <textarea
                className='textarea-mestocker w-full'
                placeholder='Textarea example'
              />
              <select className='select-mestocker w-full'>
                <option>Selecciona una opción</option>
                <option>Opción 1</option>
                <option>Opción 2</option>
              </select>
              <div className='flex items-center space-x-2'>
                <input
                  type='checkbox'
                  className='checkbox-mestocker'
                  id='checkbox-demo'
                />
                <label htmlFor='checkbox-demo' className='text-neutral-700'>
                  Acepto los términos
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Typography */}
        <div className='mb-8'>
          <h2 className='subheading-mestocker text-xl mb-4'>Typography</h2>
          <div className='space-y-2'>
            <p className='text-mestocker-primary'>Texto primario MeStocker</p>
            <p className='text-mestocker-secondary'>
              Texto secundario MeStocker
            </p>
            <h3 className='heading-mestocker text-xl'>Heading MeStocker</h3>
            <h4 className='subheading-mestocker text-lg'>
              Subheading MeStocker
            </h4>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UtilityClassesDemo;
