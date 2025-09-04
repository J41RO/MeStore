import React, { useState } from 'react';
import { Button, Input, Card, Modal } from './ui';

const BaseComponentsDemo: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');

  return (
    <div className='container-mestocker'>
      <div className='section-mestocker'>
        <h1 className='heading-mestocker text-3xl mb-8'>
          Componentes Base MeStocker
        </h1>

        {/* Buttons Demo */}
        <Card className='mb-8'>
          <Card.Header>
            <h2 className='subheading-mestocker text-xl'>Componente Button</h2>
          </Card.Header>
          <Card.Body>
            <div className='grid grid-cols-2 md:grid-cols-3 gap-4'>
              <Button variant='primary'>Primary</Button>
              <Button variant='secondary'>Secondary</Button>
              <Button variant='outline'>Outline</Button>
              <Button variant='ghost'>Ghost</Button>
              <Button variant='danger'>Danger</Button>
              <Button variant='primary' loading>
                Loading
              </Button>
              <Button variant='primary' size='sm'>
                Small
              </Button>
              <Button variant='primary' size='lg'>
                Large
              </Button>
              <Button variant='primary' fullWidth>
                Full Width
              </Button>
            </div>
          </Card.Body>
        </Card>

        {/* Input Demo */}
        <Card className='mb-8'>
          <Card.Header>
            <h2 className='subheading-mestocker text-xl'>Componente Input</h2>
          </Card.Header>
          <Card.Body>
            <div className='space-y-4 max-w-md'>
              <Input
                label='Email'
                type='email'
                placeholder='tu@email.com'
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
              />
              <Input
                label='Contraseña'
                type='password'
                placeholder='••••••••'
                helper='Mínimo 8 caracteres'
              />
              <Input
                label='Campo con error'
                error='Este campo es requerido'
                placeholder='Campo obligatorio'
              />
              <Input
                label='Campo exitoso'
                state='success'
                placeholder='Datos correctos'
              />
              <Input size='sm' placeholder='Input pequeño' />
              <Input size='lg' placeholder='Input grande' />
            </div>
          </Card.Body>
        </Card>

        {/* Card Demo */}
        <div className='grid grid-cols-1 md:grid-cols-2 gap-6 mb-8'>
          <Card variant='default'>
            <Card.Header>
              <h3 className='text-lg font-semibold'>Card Default</h3>
            </Card.Header>
            <Card.Body>
              <p>Este es el contenido de una card con estilo default.</p>
            </Card.Body>
            <Card.Footer>
              <Button size='sm'>Acción</Button>
            </Card.Footer>
          </Card>

          <Card variant='outlined'>
            <Card.Header>
              <h3 className='text-lg font-semibold'>Card Outlined</h3>
            </Card.Header>
            <Card.Body>
              <p>Esta card tiene borde pero sin sombra.</p>
            </Card.Body>
          </Card>

          <Card variant='elevated'>
            <Card.Body>
              <h3 className='text-lg font-semibold mb-2'>Card Elevated</h3>
              <p>Card con sombra elevada, sin header ni footer.</p>
            </Card.Body>
          </Card>

          <Card variant='flat'>
            <Card.Body>
              <h3 className='text-lg font-semibold mb-2'>Card Flat</h3>
              <p>Card plana con fondo neutral.</p>
            </Card.Body>
          </Card>
        </div>

        {/* Modal Demo */}
        <Card>
          <Card.Header>
            <h2 className='subheading-mestocker text-xl'>Componente Modal</h2>
          </Card.Header>
          <Card.Body>
            <div className='flex gap-4'>
              <Button onClick={() => setIsModalOpen(true)}>Abrir Modal</Button>
            </div>
          </Card.Body>
        </Card>

        {/* Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title='Modal de Ejemplo'
          size='md'
        >
          <div className='p-6'>
            <p className='text-neutral-600 mb-4'>
              Este es un modal de ejemplo con el componente Modal de MeStocker.
            </p>
            <Input
              label='Campo en modal'
              placeholder='Escribe algo...'
              className='mb-4'
            />
            <div className='flex justify-end gap-3'>
              <Button variant='ghost' onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant='primary' onClick={() => setIsModalOpen(false)}>
                Guardar
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </div>
  );
};

export default BaseComponentsDemo;
