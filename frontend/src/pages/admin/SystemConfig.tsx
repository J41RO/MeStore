import React from 'react';

const SystemConfig: React.FC = () => {
  return (
    <div className='space-y-6'>
      <div className='bg-white shadow rounded-lg p-6'>
        <h1 className='text-2xl font-bold text-gray-900 mb-4'>
          Configuración del Sistema
        </h1>
        <p className='text-gray-600 mb-6'>
          Administra configuraciones generales del sistema MeStore.
        </p>

        <div className='grid grid-cols-1 md:grid-cols-2 gap-6 mb-6'>
          <div className='border rounded-lg p-4'>
            <h3 className='font-semibold text-gray-900 mb-2'>
              Configuraciones Generales
            </h3>
            <ul className='space-y-2 text-sm text-gray-600'>
              <li>• Nombre del sistema</li>
              <li>• Configuración de email</li>
              <li>• Políticas de seguridad</li>
              <li>• Límites de sistema</li>
            </ul>
          </div>

          <div className='border rounded-lg p-4'>
            <h3 className='font-semibold text-gray-900 mb-2'>
              Configuraciones Avanzadas
            </h3>
            <ul className='space-y-2 text-sm text-gray-600'>
              <li>• Base de datos</li>
              <li>• APIs externas</li>
              <li>• Logs del sistema</li>
              <li>• Backup automático</li>
            </ul>
          </div>
        </div>

        <div className='bg-gray-50 p-4 rounded-lg'>
          <p className='text-gray-500 text-center'>
            Panel de configuración del sistema en desarrollo
          </p>
        </div>
      </div>
    </div>
  );
};

export default SystemConfig;
