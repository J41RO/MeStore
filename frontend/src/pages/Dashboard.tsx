import React from 'react';

const Dashboard: React.FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Dashboard de Vendedor</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold">Ventas del día</h3>
          <p className="text-2xl font-bold text-green-600">$0</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold">Productos activos</h3>
          <p className="text-2xl font-bold text-blue-600">0</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
