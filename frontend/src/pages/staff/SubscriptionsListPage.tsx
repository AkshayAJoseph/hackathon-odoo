import React from 'react';
import { Link } from 'react-router-dom';
import { MOCK_SUBSCRIPTIONS } from '@/api';
import { StatusBadge } from '@/components';
import { FileSpreadsheet, Plus, ArrowRight } from 'lucide-react';

export const SubscriptionsListPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Subscriptions</h1>
          <p className="text-xs text-slate-500 mt-1">
            Active and pending recurring subscription contracts.
          </p>
        </div>
        <Link
          to="/staff/templates"
          className="inline-flex items-center gap-1.5 px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>New Subscription</span>
        </Link>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 uppercase font-semibold">
            <tr>
              <th className="p-4">Reference</th>
              <th className="p-4">Customer</th>
              <th className="p-4">Plan</th>
              <th className="p-4">Period</th>
              <th className="p-4">Total Amount</th>
              <th className="p-4">Status</th>
              <th className="p-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {MOCK_SUBSCRIPTIONS.map((sub) => (
              <tr key={sub.id} className="hover:bg-slate-50">
                <td className="p-4 font-mono font-bold text-indigo-700 flex items-center gap-1.5">
                  <FileSpreadsheet className="w-4 h-4 text-slate-400" />
                  {sub.subscription_number}
                </td>
                <td className="p-4 font-medium text-slate-900">{sub.customer_name}</td>
                <td className="p-4 text-slate-700">{sub.plan_name}</td>
                <td className="p-4 text-slate-500 font-mono text-[11px]">
                  {sub.current_period_start} &rarr; {sub.current_period_end}
                </td>
                <td className="p-4 font-mono font-bold text-slate-900">${sub.total_amount}</td>
                <td className="p-4">
                  <StatusBadge status={sub.status} kind="subscription" />
                </td>
                <td className="p-4 text-right">
                  <Link
                    to={`/staff/subscriptions/${sub.id}`}
                    className="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-800 font-semibold"
                  >
                    <span>View</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
