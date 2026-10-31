import React from 'react';
import { MOCK_PRODUCTS } from '@/api';
import { Package, Plus } from 'lucide-react';

export const AdminProductsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Products & Variants</h1>
          <p className="text-xs text-slate-500 mt-1">
            Manage catalogue items, variant attributes, and base pricing.
          </p>
        </div>
        <button className="inline-flex items-center gap-1.5 px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-sm">
          <Plus className="w-4 h-4" />
          <span>Add Product</span>
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <span className="text-xs font-semibold text-slate-700 uppercase tracking-wider">Catalogue Items (25/page)</span>
          <span className="text-xs text-slate-500">2 Products Seeded</span>
        </div>

        <div className="divide-y divide-slate-200">
          {MOCK_PRODUCTS.map((prod) => (
            <div key={prod.id} className="p-5 hover:bg-slate-50/60 transition">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Package className="w-4 h-4 text-indigo-600" />
                    <span className="font-semibold text-slate-900 text-sm">{prod.name}</span>
                    <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600 uppercase">
                      {prod.type}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500">{prod.notes}</p>
                </div>
                <div className="text-right">
                  <span className="text-sm font-bold text-slate-900 font-mono">${prod.sales_price}</span>
                  <p className="text-[11px] text-slate-400 font-mono">Cost: ${prod.cost_price}</p>
                </div>
              </div>

              {/* Variants Sub-table */}
              {prod.variants.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-100">
                  <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-2">
                    Configured Variants
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {prod.variants.map((v) => (
                      <div
                        key={v.id}
                        className="flex items-center justify-between bg-slate-100/70 px-3 py-2 rounded-lg text-xs border border-slate-200"
                      >
                        <span className="text-slate-700">
                          <span className="font-semibold text-slate-900">{v.attribute}:</span> {v.value}
                        </span>
                        <span className="font-bold text-indigo-700 font-mono">
                          +${v.extra_price}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
