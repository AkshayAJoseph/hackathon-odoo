import React from 'react';
import { MOCK_TAXES } from '@/api';
import { Receipt, Plus } from 'lucide-react';

export const AdminTaxesPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Tax Configuration</h1>
          <p className="text-xs text-slate-500 mt-1">
            Define system-wide or product-specific tax computation rules.
          </p>
        </div>
        <button className="inline-flex items-center gap-1.5 px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-sm">
          <Plus className="w-4 h-4" />
          <span>New Tax Rule</span>
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 uppercase font-semibold">
            <tr>
              <th className="p-4">Tax Name</th>
              <th className="p-4">Rate</th>
              <th className="p-4">Calculation Type</th>
              <th className="p-4">Scope</th>
              <th className="p-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {MOCK_TAXES.map((tax) => (
              <tr key={tax.id} className="hover:bg-slate-50">
                <td className="p-4 font-semibold text-slate-900 flex items-center gap-2">
                  <Receipt className="w-4 h-4 text-slate-400" />
                  {tax.name}
                </td>
                <td className="p-4 font-mono font-bold text-indigo-700">{tax.rate_percent}%</td>
                <td className="p-4 uppercase font-mono text-slate-500">{tax.type}</td>
                <td className="p-4 text-slate-600">{tax.applies_to ? `Product #${tax.applies_to}` : 'All Products'}</td>
                <td className="p-4">
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    Active
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
