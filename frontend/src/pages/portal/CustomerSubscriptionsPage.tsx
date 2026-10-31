import React from 'react';
import { MOCK_SUBSCRIPTIONS } from '@/api';
import { StatusBadge } from '@/components';
import { FileSpreadsheet, Shield } from 'lucide-react';

export const CustomerSubscriptionsPage: React.FC = () => {
  // Customer portal: only customer's own subscriptions
  const customerSubs = MOCK_SUBSCRIPTIONS.filter((s) => s.customer_id === 3);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">My Subscriptions</h1>
          <p className="text-xs text-slate-500 mt-1">
            Customer Self-Service: Review active recurring contracts and plan details.
          </p>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1 bg-blue-50 text-blue-700 text-xs font-semibold rounded-lg border border-blue-200">
          <Shield className="w-3.5 h-3.5" />
          <span>Customer Scoped</span>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 uppercase font-semibold">
            <tr>
              <th className="p-4">Subscription</th>
              <th className="p-4">Plan</th>
              <th className="p-4">Billing Cycle</th>
              <th className="p-4">Recurring Total</th>
              <th className="p-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {customerSubs.map((sub) => (
              <tr key={sub.id} className="hover:bg-slate-50">
                <td className="p-4 font-mono font-bold text-indigo-700 flex items-center gap-1.5">
                  <FileSpreadsheet className="w-4 h-4 text-slate-400" />
                  {sub.subscription_number}
                </td>
                <td className="p-4 font-medium text-slate-900">{sub.plan_name}</td>
                <td className="p-4 font-mono text-slate-500 text-[11px]">
                  {sub.current_period_start} &rarr; {sub.current_period_end}
                </td>
                <td className="p-4 font-mono font-bold text-slate-900">${sub.total_amount}</td>
                <td className="p-4">
                  <StatusBadge status={sub.status} kind="subscription" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
