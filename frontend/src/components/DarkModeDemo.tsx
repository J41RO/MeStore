import React from 'react';
import { useTheme } from '@/hooks/useTheme';
import { ThemeToggle, Button, Card, Input } from './ui';

const DarkModeDemo: React.FC = () => {
  const { theme, effectiveTheme, systemTheme } = useTheme();

  return (
    <div className='container-mestocker'>
      <div className='section-mestocker'>
        <h1 className='heading-mestocker text-3xl mb-8'>Dark Mode MeStocker</h1>

        {/* Theme Status */}
        <Card className='mb-8'>
          <Card.Header>
            <div className='flex items-center justify-between'>
              <h2 className='subheading-mestocker text-xl'>Theme Control</h2>
              <ThemeToggle showLabel size='md' />
            </div>
          </Card.Header>
          <Card.Body>
            <div className='grid grid-cols-1 md:grid-cols-3 gap-4 text-sm'>
              <div>
                <strong>Selected Theme:</strong> {theme}
              </div>
              <div>
                <strong>System Theme:</strong> {systemTheme}
              </div>
              <div>
                <strong>Effective Theme:</strong> {effectiveTheme}
              </div>
            </div>
          </Card.Body>
        </Card>

        {/* Components Demo in Dark Mode */}
        <div className='grid grid-cols-1 lg:grid-cols-2 gap-8'>
          {/* Buttons */}
          <Card>
            <Card.Header>
              <h3 className='subheading-mestocker text-lg'>Buttons</h3>
            </Card.Header>
            <Card.Body>
              <div className='space-y-4'>
                <div className='flex flex-wrap gap-3'>
                  <Button variant='primary'>Primary</Button>
                  <Button variant='secondary'>Secondary</Button>
                  <Button variant='outline'>Outline</Button>
                  <Button variant='ghost'>Ghost</Button>
                </div>
                <div className='flex gap-3'>
                  <ThemeToggle size='sm' />
                  <ThemeToggle size='md' />
                  <ThemeToggle size='lg' />
                </div>
              </div>
            </Card.Body>
          </Card>

          {/* Forms */}
          <Card>
            <Card.Header>
              <h3 className='subheading-mestocker text-lg'>Forms</h3>
            </Card.Header>
            <Card.Body>
              <div className='space-y-4'>
                <Input label='Email' placeholder='tu@email.com' type='email' />
                <Input label='Message' placeholder='Tu mensaje...' />
                <div className='flex justify-end'>
                  <Button variant='primary'>Send</Button>
                </div>
              </div>
            </Card.Body>
          </Card>

          {/* Alerts */}
          <Card>
            <Card.Header>
              <h3 className='subheading-mestocker text-lg'>Alerts</h3>
            </Card.Header>
            <Card.Body>
              <div className='space-y-4'>
                <div className='alert-mestocker'>
                  Primary alert in current theme
                </div>
                <div className='alert-success'>Success message</div>
                <div className='alert-error'>Error notification</div>
              </div>
            </Card.Body>
          </Card>

          {/* Badges */}
          <Card>
            <Card.Header>
              <h3 className='subheading-mestocker text-lg'>Badges</h3>
            </Card.Header>
            <Card.Body>
              <div className='flex flex-wrap gap-2'>
                <span className='badge-mestocker'>Primary</span>
                <span className='badge-secondary'>Secondary</span>
                <span className='badge-success'>Success</span>
                <span className='badge-error'>Error</span>
                <span className='badge-warning'>Warning</span>
              </div>
            </Card.Body>
          </Card>
        </div>

        {/* Dark Mode Tips */}
        <Card className='mt-8'>
          <Card.Header>
            <h3 className='subheading-mestocker text-lg'>Dark Mode Features</h3>
          </Card.Header>
          <Card.Body>
            <ul className='space-y-2 text-sm text-neutral-600 dark:text-neutral-400'>
              <li>
                ✅ <strong>Manual Toggle:</strong> Click the theme button to
                cycle through light → dark → system
              </li>
              <li>
                ✅ <strong>System Detection:</strong> Automatically follows your
                OS preference when set to 'system'
              </li>
              <li>
                ✅ <strong>Persistence:</strong> Your choice is saved in
                localStorage
              </li>
              <li>
                ✅ <strong>Smooth Transitions:</strong> CSS transitions for
                seamless theme switching
              </li>
              <li>
                ✅ <strong>Component Support:</strong> All MeStocker components
                adapt to dark mode
              </li>
            </ul>
          </Card.Body>
        </Card>
      </div>
    </div>
  );
};

export default DarkModeDemo;
