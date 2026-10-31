
import React, { useState } from 'react';
import { MOCK_TAXES, addMockTax, Tax } from '@/api/mockData';
import { Receipt, Plus, X } from 'lucide-react';

export const AdminTaxesPage: React.FC = () => {
  const [taxes, setTaxes] = useState<Tax[]>([...MOCK_TAXES]);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState('');

  const [name, setName] = useState('');
  const [rate, setRate] = useState('');
  const [type, setType] = useState<'percent' | 'fixed'>('percent');
  const [appliesTo, setAppliesTo] = useState('');
  const [isActive, setIsActive] = useState(true);

  const resetForm = () => {
    setName('');
    setRate('');
    setType('percent');
    setAppliesTo('');
    setIsActive(true);
    setError('');
    setShowForm(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const numericRate = Number(rate);

    if (!name.trim()) {
      setError('Please enter a tax name.');
      return;
    }

    if (!rate.trim() || !Number.isFinite(numericRate) || numericRate < 0) {
      setError('Enter a valid non-negative tax rate.');
      return;
    }

    if (type === 'percent' && numericRate > 100) {
      setError('Percentage tax cannot exceed 100%.');
      return;
    }

    addMockTax({
      name: name.trim(),
      rate_percent: numericRate.toFixed(2),
      type,
      is_active: isActive,
      applies_to: appliesTo.trim() ? Number(appliesTo) : null,
    });

    setTaxes([...MOCK_TAXES]);
    resetForm();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Tax Configuration
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Define system-wide or product-specific tax computation rules.
          </p>
        </div>

        <button
          onClick={() => setShowForm(true)}
          className="inline-flex items-center gap-1.5 px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-sm"
        >
          <Plus className="w-4 h-4" />
          New Tax Rule
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-sm font-bold text-slate-900">
              Create Tax Rule
            </h2>
            <button onClick={resetForm} className="text-slate-400 hover:text-slate-700">
              <X className="w-4 h-4" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Tax Name *
                </label>
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Standard GST"
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Rate *
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={rate}
                  onChange={(e) => setRate(e.target.value)}
                  placeholder="e.g. 18"
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Calculation Type
                </label>
                <select
                  value={type}
                  onChange={(e) => setType(e.target.value as 'percent' | 'fixed')}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="percent">Percentage (%)</option>
                  <option value="fixed">Fixed Amount (₹)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Product ID (optional)
                </label>
                <input
                  type="number"
                  min="1"
                  value={appliesTo}
                  onChange={(e) => setAppliesTo(e.target.value)}
                  placeholder="Leave empty for all products"
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>

            <label className="flex items-center gap-2 text-xs text-slate-700">
              <input
                type="checkbox"
                checked={isActive}
                onChange={(e) => setIsActive(e.target.checked)}
                className="rounded border-slate-300"
              />
              Active tax rule
            </label>

            {error && (
              <p className="text-xs text-red-600">{error}</p>
            )}

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={resetForm}
                className="px-4 py-2 text-xs font-semibold text-slate-600 border border-slate-300 rounded-lg hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg"
              >
                Save Tax Rule
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
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
              {taxes.map((tax) => (
                <tr key={tax.id} className="hover:bg-slate-50">
                  <td className="p-4 font-semibold text-slate-900">
                    <div className="flex items-center gap-2">
                      <Receipt className="w-4 h-4 text-slate-400" />
                      {tax.name}
                    </div>
                  </td>
                  <td className="p-4 font-mono font-bold text-indigo-700">
                    {tax.type === 'percent' ? `${tax.rate_percent}%` : `₹${tax.rate_percent}`}
                  </td>
                  <td className="p-4 uppercase font-mono text-slate-500">
                    {tax.type}
                  </td>
                  <td className="p-4 text-slate-600">
                    {tax.applies_to ? `Product #${tax.applies_to}` : 'All Products'}
                  </td>
                  <td className="p-4">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold border ${
                      tax.is_active
                        ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                        : 'bg-slate-100 text-slate-600 border-slate-200'
                    }`}>
                      {tax.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                </tr>
              ))}

              {taxes.length === 0 && (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-slate-500">
                    No tax rules found. Create your first tax rule.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
