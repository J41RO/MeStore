import React from 'react';

const PageLoader: React.FC = () => {
  return (
    <div className='flex items-center justify-center min-h-[200px] p-4'>
      <div className='flex flex-col items-center'>
        <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-3'></div>
        <span className='text-gray-600 text-sm'>Cargando página...</span>
      </div>
    </div>
  );
};

export default PageLoader;
