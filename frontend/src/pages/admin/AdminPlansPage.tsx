import React, { useEffect, useState } from 'react';
import { listPlans } from '@/api/plans';
import { MOCK_PLANS, type Plan } from '@/api/mockData';
import { CalendarCheck, Plus, Check, X, Loader2 } from 'lucide-react';

export const AdminPlansPage: React.FC = () => {
  const [plans, setPlans] = useState<Plan[]>(MOCK_PLANS);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let mounted = true;
    listPlans()
      .then((data) => {
        if (mounted && data && data.length > 0) {
          setPlans(data);
        }
      })
      .catch((err) => {
        console.warn('Failed to fetch live plans, using default', err);
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
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Subscription Plans</h1>
          <p className="text-xs text-slate-500 mt-1">
            Configure recurring intervals, pricing models, and policy flags.
          </p>
        </div>
        <button className="inline-flex items-center gap-1.5 px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-sm">
          <Plus className="w-4 h-4" />
          <span>New Plan</span>
        </button>
      </div>

      {loading && plans.length === 0 ? (
        <div className="flex items-center justify-center p-12 text-slate-400">
          <Loader2 className="w-6 h-6 animate-spin mr-2 text-indigo-600" />
          <span className="text-sm">Loading plans...</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {plans.map((plan) => (
            <div key={plan.id} className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <CalendarCheck className="w-5 h-5 text-indigo-600" />
                    <h2 className="font-bold text-slate-900 text-base">{plan.name}</h2>
                  </div>
                  <span className="inline-block mt-1 text-[11px] font-mono px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 uppercase">
                    {plan.billing_period}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-xl font-extrabold text-slate-900 font-mono">${plan.price}</span>
                  <p className="text-[11px] text-slate-400">/{plan.billing_period}</p>
                </div>
              </div>

              <div className="text-xs text-slate-500 flex justify-between py-2 border-y border-slate-100">
                <span>Validity: {plan.available_from} to {plan.available_to}</span>
                <span>Min Qty: {plan.min_quantity}</span>
              </div>

              {/* 4 Feature Flags switches per SPEC */}
              <div>
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-2">
                  Plan Policy Flags
                </span>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center justify-between p-2 rounded bg-slate-50 border border-slate-200">
                    <span className="text-slate-600">Auto Close</span>
                    {plan.auto_close ? (
                      <span className="flex items-center text-emerald-600 font-semibold"><Check className="w-3.5 h-3.5 mr-0.5" /> Yes</span>
                    ) : (
                      <span className="flex items-center text-slate-400"><X className="w-3.5 h-3.5 mr-0.5" /> No</span>
                    )}
                  </div>
                  <div className="flex items-center justify-between p-2 rounded bg-slate-50 border border-slate-200">
                    <span className="text-slate-600">Closable Early</span>
                    {plan.closable ? (
                      <span className="flex items-center text-emerald-600 font-semibold"><Check className="w-3.5 h-3.5 mr-0.5" /> Yes</span>
                    ) : (
                      <span className="flex items-center text-slate-400"><X className="w-3.5 h-3.5 mr-0.5" /> No</span>
                    )}
                  </div>
                  <div className="flex items-center justify-between p-2 rounded bg-slate-50 border border-slate-200">
                    <span className="text-slate-600">Pausable</span>
                    {plan.pausable ? (
                      <span className="flex items-center text-emerald-600 font-semibold"><Check className="w-3.5 h-3.5 mr-0.5" /> Yes</span>
                    ) : (
                      <span className="flex items-center text-slate-400"><X className="w-3.5 h-3.5 mr-0.5" /> No</span>
                    )}
                  </div>
                  <div className="flex items-center justify-between p-2 rounded bg-slate-50 border border-slate-200">
                    <span className="text-slate-600">Renewable</span>
                    {plan.renewable ? (
                      <span className="flex items-center text-emerald-600 font-semibold"><Check className="w-3.5 h-3.5 mr-0.5" /> Yes</span>
                    ) : (
                      <span className="flex items-center text-slate-400"><X className="w-3.5 h-3.5 mr-0.5" /> No</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
