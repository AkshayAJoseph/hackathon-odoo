import React, { useState, useEffect } from 'react';
import { StatusBadge } from '@/components';
import { FileSpreadsheet, Shield, RefreshCw } from 'lucide-react';
import { apiClient } from '@/api';

interface SubscriptionItem {
  id: number;
  number?: string;
  subscription_number?: string;
  plan_name?: string;
  billing_period?: string;
  start_date: string;
  expiry_date?: string | null;
  next_billing_date?: string | null;
  current_period_start?: string;
  current_period_end?: string;
  total_amount?: string;
  recurring_total?: string;
  status: string;
  lines?: Array<{
    id: number;
    product_name: string;
    quantity: number;
    unit_price: string;
    line_total: string;
  }>;
}

export const CustomerSubscriptionsPage: React.FC = () => {
  const [subscriptions, setSubscriptions] = useState<SubscriptionItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchSubscriptions = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get<any>('/portal/subscriptions/');
      const list = res.results || res || [];
      if (Array.isArray(list)) {
        setSubscriptions(list);
      }
    } catch (err) {
      console.error('Failed to load portal subscriptions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubscriptions();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">My Subscriptions</h1>
          <p className="text-xs text-slate-500 mt-1">
            Customer Self-Service: Review active recurring contracts, plans, and next renewal dates.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-3 py-1 bg-blue-50 text-blue-700 text-xs font-semibold rounded-lg border border-blue-200">
            <Shield className="w-3.5 h-3.5" />
            <span>Customer Scoped</span>
          </div>
          <button
            onClick={fetchSubscriptions}
            className="p-1.5 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-600 transition"
            title="Refresh Subscriptions"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 uppercase font-semibold">
            <tr>
              <th className="p-4">Subscription</th>
              <th className="p-4">Plan</th>
              <th className="p-4">Billing Cycle</th>
              <th className="p-4">Next Billing Date</th>
              <th className="p-4">Recurring Total</th>
              <th className="p-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {subscriptions.length === 0 ? (
              <tr>
                <td colSpan={6} className="p-6 text-center text-slate-400">
                  {loading ? 'Loading subscriptions...' : 'No subscriptions found.'}
                </td>
              </tr>
            ) : (
              subscriptions.map((sub) => {
                const subNum = sub.number || sub.subscription_number || `SUB-${sub.id}`;
                const linesTotal = sub.lines?.reduce((sum, l) => sum + Number(l.line_total || 0), 0);
                const recurringTotal = sub.recurring_total || sub.total_amount || (linesTotal ? linesTotal.toFixed(2) : '0.00');

                return (
                  <tr key={sub.id} className="hover:bg-slate-50">
                    <td className="p-4 font-mono font-bold text-indigo-700 flex items-center gap-1.5">
                      <FileSpreadsheet className="w-4 h-4 text-slate-400" />
                      {subNum}
                    </td>
                    <td className="p-4 font-medium text-slate-900">{sub.plan_name || 'Standard'}</td>
                    <td className="p-4 capitalize font-mono text-slate-600 text-[11px]">
                      {sub.billing_period || 'Monthly'}
                    </td>
                    <td className="p-4 font-mono text-slate-500 text-[11px]">
                      {sub.next_billing_date || sub.current_period_end || '—'}
                    </td>
                    <td className="p-4 font-mono font-bold text-slate-900">${recurringTotal}</td>
                    <td className="p-4">
                      <StatusBadge status={sub.status} kind="subscription" />
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
