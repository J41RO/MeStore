import React, { useState } from 'react';
import { Download, DollarSign, Calendar, BarChart3 } from 'lucide-react';
import { useCommissions } from '../../hooks/useCommissions';
import CommissionTable from './CommissionTable';
import CommissionCharts from './CommissionCharts';
import { CommissionReportProps } from '../../types/commission.types';

const CommissionReport: React.FC<CommissionReportProps> = ({
 className = '',

 defaultFilters = {}
}) => {
 const { commissions, isLoading, totalCommissions, totalSales, breakdown } = useCommissions(defaultFilters);
 const [currentView, setCurrentView] = useState<'summary' | 'table' | 'charts'>('summary');

 const handleExport = () => {
   console.log('Exportando reporte de comisiones...');
 };

 if (isLoading) {
   return (
     <div className="p-6">
       <div className="animate-pulse space-y-4">
         <div className="h-8 bg-gray-200 rounded w-1/4"></div>
         <div className="h-32 bg-gray-200 rounded"></div>
       </div>
     </div>
   );
 }

 return (
   <div className={['space-y-6', className].filter(Boolean).join(' ')}>
     <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
       <div className="flex items-center justify-between mb-4">
         <div>
           <h1 className="text-2xl font-bold text-gray-900">Reporte de Comisiones</h1>
           <p className="text-gray-600">Análisis detallado de tus comisiones</p>
         </div>
         <button
           onClick={handleExport}
           className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
         >
           <Download size={16} />
           Exportar
         </button>
       </div>

       <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
         <div className="bg-green-50 p-4 rounded-lg border border-green-200">
           <div className="flex items-center justify-between">
             <div>
               <p className="text-sm text-green-600 font-medium">Total Comisiones</p>
               <p className="text-2xl font-bold text-green-800">${totalCommissions.toFixed(2)}</p>
             </div>
             <DollarSign className="text-green-600" size={24} />
           </div>
         </div>
         <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
           <div className="flex items-center justify-between">
             <div>
               <p className="text-sm text-blue-600 font-medium">Total Ventas</p>
               <p className="text-2xl font-bold text-blue-800">${totalSales.toFixed(2)}</p>
             </div>
             <BarChart3 className="text-blue-600" size={24} />
           </div>
         </div>
         <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
           <div className="flex items-center justify-between">
             <div>
               <p className="text-sm text-purple-600 font-medium">Comisiones</p>
               <p className="text-2xl font-bold text-purple-800">{commissions.length}</p>
             </div>
             <Calendar className="text-purple-600" size={24} />
           </div>
         </div>
       </div>

       <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
         <button
           onClick={() => setCurrentView('summary')}
           className={currentView === 'summary' ? 'bg-white shadow-sm text-blue-600 font-medium px-4 py-2 rounded-md' : 'text-gray-600 hover:text-gray-900 px-4 py-2 rounded-md'}
         >
           Resumen
         </button>
         <button
           onClick={() => setCurrentView('table')}
           className={currentView === 'table' ? 'bg-white shadow-sm text-blue-600 font-medium px-4 py-2 rounded-md' : 'text-gray-600 hover:text-gray-900 px-4 py-2 rounded-md'}
         >
           Detalle
         </button>
         <button
           onClick={() => setCurrentView('charts')}
           className={currentView === 'charts' ? 'bg-white shadow-sm text-blue-600 font-medium px-4 py-2 rounded-md' : 'text-gray-600 hover:text-gray-900 px-4 py-2 rounded-md'}
         >
           Gráficos
         </button>
       </div>
     </div>

     <div className="bg-white rounded-lg shadow-sm border p-6">
       {currentView === 'summary' && (
         <div>
           <h2 className="text-lg font-semibold mb-4">Resumen de Comisiones</h2>           
           {/* Métricas de Breakdown Detallado */}
           <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
             <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
               <h3 className="text-sm font-medium text-blue-800 mb-1">Comisión Promedio</h3>
               <p className="text-2xl font-bold text-blue-900">
                 ${commissions.length > 0 ? (totalCommissions / commissions.length).toFixed(2) : '0.00'}
               </p>
               <p className="text-xs text-blue-600">Por producto vendido</p>
             </div>
             
             <div className="bg-green-50 border border-green-200 rounded-lg p-4">
               <h3 className="text-sm font-medium text-green-800 mb-1">Total por Categorías</h3>
               <p className="text-2xl font-bold text-green-900">
                 {Object.keys(breakdown.byCategory).length}
               </p>
               <p className="text-xs text-green-600">Categorías activas</p>
             </div>
             
             <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
               <h3 className="text-sm font-medium text-yellow-800 mb-1">Status Breakdown</h3>
               <p className="text-2xl font-bold text-yellow-900">
                 {commissions.filter(c => c.status === 'confirmed').length}
               </p>
               <p className="text-xs text-yellow-600">Confirmadas de {commissions.length}</p>
             </div>
           </div>
           <div className="space-y-4">
             {commissions.map((commission) => (
               <div key={commission.id} className="border p-4 rounded-lg hover:bg-gray-50">
                 <div className="flex justify-between items-start">
                   <div>
                     <h3 className="font-medium">{commission.productName}</h3>
                     <p className="text-sm text-gray-600">{commission.productCategory}</p>
                     <p className="text-sm text-gray-500">Orden: {commission.orderId}</p>
                   </div>
                   <div className="text-right">
                     <p className="text-lg font-bold text-green-600">${commission.commissionAmount.toFixed(2)}</p>
                     <p className="text-sm text-gray-500">{(commission.commissionRate * 100).toFixed(1)}%</p>
                     <span className="inline-block px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                       {commission.status}
                     </span>
                   </div>
                 </div>
               </div>
             ))}
           </div>
         </div>
       )}
       
       {currentView === 'table' && (
         <div>
           <h2 className="text-lg font-semibold mb-4">Detalle de Comisiones</h2>
           <CommissionTable commissions={commissions} />
         </div>
       )}
       
       {currentView === 'charts' && (
         <div>
           <h2 className="text-lg font-semibold mb-4">Gráficos y Análisis</h2>
           <CommissionCharts breakdown={breakdown} />
         </div>
       )}
     </div>
   </div>
 );
};

export default CommissionReport;