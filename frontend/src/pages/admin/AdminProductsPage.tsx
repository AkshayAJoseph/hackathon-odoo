// Admin Products page – connected to real backend (fallback to mock mode)
import React, { useEffect, useState } from 'react';
import { listProducts, createProduct, addVariant } from '@/api/catalog';
import type { Product } from '@/api/mockData';
import { Package, Plus, X } from 'lucide-react';

export const AdminProductsPage: React.FC = () => {
  // ---------- State ----------
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Add‑product modal state
  const [showAddProduct, setShowAddProduct] = useState<boolean>(false);
  const [newProd, setNewProd] = useState<{
    name: string;
    type: 'service' | 'software' | 'addon';
    sales_price: string;
    cost_price: string;
    notes: string;
    is_active: boolean;
  }>({
    name: '',
    type: 'service',
    sales_price: '0.00',
    cost_price: '0.00',
    notes: '',
    is_active: true,
  });

  // Add‑variant modal state
  const [showAddVariant, setShowAddVariant] = useState<boolean>(false);
  const [variantProdId, setVariantProdId] = useState<number | null>(null);
  const [newVariant, setNewVariant] = useState<{
    attribute: string;
    value: string;
    extra_price: string;
  }>({ attribute: '', value: '', extra_price: '0.00' });

  // ---------- Helpers ----------
  const fetchProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listProducts();
      setProducts(data);
    } catch (e: any) {
      setError(e?.message ?? 'Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const resetProductForm = () => {
    setNewProd({
      name: '',
      type: 'service',
      sales_price: '0.00',
      cost_price: '0.00',
      notes: '',
      is_active: true,
    });
    setShowAddProduct(false);
  };

  const resetVariantForm = () => {
    setNewVariant({ attribute: '', value: '', extra_price: '0.00' });
    setShowAddVariant(false);
    setVariantProdId(null);
  };

  // ---------- Effects ----------
  useEffect(() => {
    fetchProducts();
  }, []);

  // ---------- Event Handlers ----------
  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createProduct({
        name: newProd.name,
        type: newProd.type,
        sales_price: newProd.sales_price,
        cost_price: newProd.cost_price,
        notes: newProd.notes,
        is_active: newProd.is_active,
      });
      await fetchProducts();
      resetProductForm();
    } catch (e: any) {
      setError(e?.message ?? 'Failed to create product');
    }
  };

  const handleAddVariant = async (e: React.FormEvent) => {
    e.preventDefault();
    if (variantProdId === null) return;
    try {
      await addVariant(variantProdId, {
        attribute: newVariant.attribute,
        value: newVariant.value,
        extra_price: newVariant.extra_price,
      });
      await fetchProducts();
      resetVariantForm();
    } catch (e: any) {
      setError(e?.message ?? 'Failed to add variant');
    }
  };

  // ---------- Render ----------
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Products &amp; Variants
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Manage catalogue items, variant attributes, and base pricing.
          </p>
        </div>
        <button
          className="inline-flex items-center gap-1.5 px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-sm"
          onClick={() => setShowAddProduct(true)}
        >
          <Plus className="w-4 h-4" />
          <span>Add Product</span>
        </button>
      </div>

      {/* Content Card */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <span className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
            Catalogue Items
          </span>
          {loading && <span className="text-xs text-slate-500">Loading…</span>}
          {error && <span className="text-xs text-red-600">{error}</span>}
        </div>

        {/* List */}
        <div className="divide-y divide-slate-200">
          {loading ? (
            // Simple skeleton rows – repeat 3 times
            Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="p-5 animate-pulse">
                <div className="flex items-start justify-between">
                  <div className="space-y-2">
                    <div className="h-4 bg-slate-200 rounded w-40" />
                    <div className="h-3 bg-slate-200 rounded w-24" />
                  </div>
                  <div className="space-y-2 text-right">
                    <div className="h-4 bg-slate-200 rounded w-20" />
                    <div className="h-3 bg-slate-200 rounded w-24" />
                  </div>
                </div>
              </div>
            ))
          ) : (
            products.length === 0 ? (
              <div className="p-8 text-center text-slate-500">No products found.</div>
            ) : (
              products.map((prod) => (
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
                      <button
                        className="mt-2 text-xs text-indigo-600 hover:underline"
                        onClick={() => {
                          setVariantProdId(prod.id);
                          setShowAddVariant(true);
                        }}
                      >
                        + Add Variant
                      </button>
                    </div>
                  </div>

                  {/* Variants Sub‑table */}
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
                              <span className="font-semibold text-slate-900">{v.attribute}:</span>{' '}
                              {v.value}
                            </span>
                            <span className="font-bold text-indigo-700 font-mono">+${v.extra_price}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))
            )
          )}
        </div>
      </div>

      {/* ---------- Add Product Modal ---------- */}
      {showAddProduct && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 space-y-4 border border-slate-200">
            <h2 className="text-base font-bold text-slate-900">Create Product</h2>
            <form onSubmit={handleCreateProduct} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Name *</label>
                <input
                  required
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                  value={newProd.name}
                  onChange={(e) => setNewProd({ ...newProd, name: e.target.value })}
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Type *</label>
                <select
                  required
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-white"
                  value={newProd.type}
                  onChange={(e) => setNewProd({ ...newProd, type: e.target.value as any })}
                >
                  <option value="service">Service</option>
                  <option value="software">Software</option>
                  <option value="addon">Addon</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Sales Price *</label>
                  <input
                    required
                    type="number"
                    step="0.01"
                    min="0"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                    value={newProd.sales_price}
                    onChange={(e) => setNewProd({ ...newProd, sales_price: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Cost Price *</label>
                  <input
                    required
                    type="number"
                    step="0.01"
                    min="0"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                    value={newProd.cost_price}
                    onChange={(e) => setNewProd({ ...newProd, cost_price: e.target.value })}
                  />
                </div>
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Notes</label>
                <textarea
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                  rows={2}
                  value={newProd.notes}
                  onChange={(e) => setNewProd({ ...newProd, notes: e.target.value })}
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={newProd.is_active}
                  onChange={(e) => setNewProd({ ...newProd, is_active: e.target.checked })}
                />
                <span className="text-sm text-slate-700">Active</span>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button type="button" className="px-4 py-2 text-xs text-slate-600 border border-slate-300 rounded" onClick={resetProductForm}>
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 text-xs text-white bg-indigo-600 rounded hover:bg-indigo-700">
                  Save
                </button>
              </div>
            </form>
            <button className="absolute top-3 right-3 text-slate-400 hover:text-slate-600" onClick={resetProductForm}>
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* ---------- Add Variant Modal ---------- */}
      {showAddVariant && variantProdId !== null && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 space-y-4 border border-slate-200">
            <h2 className="text-base font-bold text-slate-900">Add Variant</h2>
            <form onSubmit={handleAddVariant} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Attribute *</label>
                <input
                  required
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                  value={newVariant.attribute}
                  onChange={(e) => setNewVariant({ ...newVariant, attribute: e.target.value })}
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Value *</label>
                <input
                  required
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                  value={newVariant.value}
                  onChange={(e) => setNewVariant({ ...newVariant, value: e.target.value })}
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Extra Price *</label>
                <input
                  required
                  type="number"
                  step="0.01"
                  min="0"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                  value={newVariant.extra_price}
                  onChange={(e) => setNewVariant({ ...newVariant, extra_price: e.target.value })}
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button type="button" className="px-4 py-2 text-xs text-slate-600 border border-slate-300 rounded" onClick={resetVariantForm}>
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 text-xs text-white bg-indigo-600 rounded hover:bg-indigo-700">
                  Save
                </button>
              </div>
            </form>
            <button className="absolute top-3 right-3 text-slate-400 hover:text-slate-600" onClick={resetVariantForm}>
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
