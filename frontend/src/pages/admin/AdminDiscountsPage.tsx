import React from 'react';
import { MOCK_DISCOUNTS } from '@/api';
import { Plus, Tag } from 'lucide-react';

export const AdminDiscountsPage: React.FC = () => {
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
            {MOCK_DISCOUNTS.map((d) => (
              <tr key={d.id} className="hover:bg-slate-50">
                <td className="p-4 font-mono font-bold text-indigo-700 flex items-center gap-1.5">
                  <Tag className="w-3.5 h-3.5 text-indigo-500" />
                  {d.code}
                </td>
                <td className="p-4 font-semibold text-slate-900">{d.name}</td>
                <td className="p-4 font-mono font-bold text-slate-800">
                  {d.type === 'percent' ? `${d.amount}%` : `$${d.amount}`}
                </td>
                <td className="p-4 font-mono text-slate-600">${d.min_purchase}</td>
                <td className="p-4 text-slate-600 font-mono">
                  {d.used_count} / {d.usage_limit}
                </td>
                <td className="p-4 uppercase text-[11px] font-mono text-slate-500">{d.scope}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
