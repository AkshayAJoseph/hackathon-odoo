import React, { useEffect, useState } from 'react';
import { MOCK_DISCOUNTS, apiClient } from '@/api';
import { Plus, Tag, Loader2 } from 'lucide-react';

interface DiscountItem {
  id: number;
  code?: string;
  name: string;
  type?: string;
  kind?: string;
  amount?: string;
  value?: string;
  min_purchase: string;
  used_count?: number;
  times_used?: number;
  usage_limit: number;
  scope: string;
}

export const AdminDiscountsPage: React.FC = () => {
  const [discounts, setDiscounts] = useState<DiscountItem[]>(MOCK_DISCOUNTS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    apiClient.get<any>('/discounts/')
      .then((res) => {
        const list = res.results || res || [];
        if (mounted && Array.isArray(list) && list.length > 0) {
          setDiscounts(list.map((d: any) => ({
            id: d.id,
            code: d.code || `PROMO-${d.id}`,
            name: d.name,
            type: d.kind || d.type || 'percent',
            amount: d.value ? String(d.value) : (d.amount ? String(d.amount) : '10'),
            min_purchase: d.min_purchase ? String(d.min_purchase) : '0.00',
            used_count: d.times_used ?? d.used_count ?? 0,
            usage_limit: d.usage_limit || 100,
            scope: d.scope || 'order',
          })));
        }
      })
      .catch((err) => {
        console.warn('Could not load live discounts, using default', err);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Admin Discounts</h1>
          <p className="text-xs text-slate-500 mt-1">
            Admin-only promotional campaigns and automatic discount rules.
          </p>
        </div>
        <button className="inline-flex items-center gap-1.5 px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-sm">
          <Plus className="w-4 h-4" />
          <span>New Discount</span>
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        {loading && discounts.length === 0 ? (
          <div className="p-8 flex items-center justify-center text-slate-400">
            <Loader2 className="w-6 h-6 animate-spin text-indigo-600 mr-2" />
            <span className="text-sm">Loading promotional discounts...</span>
          </div>
        ) : (
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 uppercase font-semibold">
              <tr>
                <th className="p-4">Discount Code</th>
                <th className="p-4">Campaign Name</th>
                <th className="p-4">Amount / Rate</th>
                <th className="p-4">Min Purchase</th>
                <th className="p-4">Usage (Limit)</th>
                <th className="p-4">Scope</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {discounts.map((d) => (
                <tr key={d.id} className="hover:bg-slate-50">
                  <td className="p-4 font-mono font-bold text-indigo-700 flex items-center gap-1.5">
                    <Tag className="w-3.5 h-3.5 text-indigo-500" />
                    {d.code || `DISC-${d.id}`}
                  </td>
                  <td className="p-4 font-semibold text-slate-900">{d.name}</td>
                  <td className="p-4 font-mono font-bold text-slate-800">
                    {(d.type === 'percent' || d.kind === 'percent') ? `${d.amount || d.value}%` : `$${d.amount || d.value}`}
                  </td>
                  <td className="p-4 font-mono text-slate-600">${d.min_purchase}</td>
                  <td className="p-4 text-slate-600 font-mono">
                    {d.used_count ?? d.times_used ?? 0} / {d.usage_limit}
                  </td>
                  <td className="p-4 uppercase text-[11px] font-mono text-slate-500">{d.scope}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
