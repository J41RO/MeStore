import React from 'react';

const PageLoader: React.FC = () => {
  return (
    <div className="flex items-center justify-center min-h-[200px]">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <span className="ml-3 text-gray-600">Cargando página...</span>
    </div>
  );
};

export default PageLoader;
