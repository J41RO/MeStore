/**
 * PaymentSettingsPage Component - Payment methods and financial settings
 */

import React, { useState, useCallback, useEffect } from 'react';
import { CreditCard, DollarSign, Settings, CheckCircle } from 'lucide-react';
import { DashboardCard, StatusBadge, DataTable } from '../../../components/admin/common';

export const PaymentSettingsPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [paymentMethods, setPaymentMethods] = useState<any[]>([]);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 600));
    setPaymentMethods([
      { id: '1', name: 'Wompi', type: 'Gateway', status: 'active', fees: '3.9%' },
      { id: '2', name: 'PSE', type: 'Bank Transfer', status: 'active', fees: '1.5%' },
      { id: '3', name: 'PayPal', type: 'Digital Wallet', status: 'inactive', fees: '4.2%' }
    ]);
    setIsLoading(false);
  }, []);

  const columns = [
    { id: 'name', header: 'Payment Method', accessor: 'name', sortable: true },
    { id: 'type', header: 'Type', accessor: 'type', sortable: true },
    { id: 'status', header: 'Status', accessor: 'status', sortable: true, cell: (value: any) => <StatusBadge variant={value === 'active' ? 'success' : 'inactive'} size="sm">{value}</StatusBadge> },
    { id: 'fees', header: 'Fees', accessor: 'fees', sortable: true }
  ];

  useEffect(() => { loadData(); }, [loadData]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Payment Settings</h1>
        <p className="text-sm text-gray-500 mt-1">Configure payment methods and financial settings</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <DashboardCard title="Active Methods" value={paymentMethods.filter(p => p.status === 'active').length} icon={CreditCard} theme="success" isLoading={isLoading} />
        <DashboardCard title="Total Methods" value={paymentMethods.length} icon={Settings} theme="primary" isLoading={isLoading} />
        <DashboardCard title="Avg. Processing Fee" value="3.2%" icon={DollarSign} theme="warning" isLoading={isLoading} formatValue={(val) => String(val)} />
        <DashboardCard title="Payment Success Rate" value="98.5%" icon={CheckCircle} theme="info" isLoading={isLoading} formatValue={(val) => String(val)} />
      </div>

      <div className="bg-white rounded-lg border">
        <div className="p-6 border-b">
          <h3 className="text-lg font-medium">Payment Methods</h3>
        </div>
        <DataTable data={paymentMethods} columns={columns} isLoading={isLoading} searchable={true} emptyMessage="No payment methods configured." />
      </div>
    </div>
  );
};

export default PaymentSettingsPage;