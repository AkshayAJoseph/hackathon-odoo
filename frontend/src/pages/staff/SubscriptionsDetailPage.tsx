import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { MOCK_SUBSCRIPTIONS, Subscription } from '@/api';
import { StatusBadge, StatusStepper } from '@/components';
import { ArrowLeft, CheckCircle2, Play, Pause, XCircle, RefreshCw, Send } from 'lucide-react';

export const SubscriptionsDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const initialSub = MOCK_SUBSCRIPTIONS.find((s) => s.id === Number(id)) || MOCK_SUBSCRIPTIONS[0];
  const [sub, setSub] = useState<Subscription>(initialSub);

  // Transition helper adhering to allowed_actions
  const handleAction = (action: string) => {
    if (action === 'confirm') {
      setSub((prev) => ({
        ...prev,
        status: 'confirmed',
        allowed_actions: ['activate', 'close'],
      }));
    } else if (action === 'activate') {
      setSub((prev) => ({
        ...prev,
        status: 'active',
        allowed_actions: ['pause', 'renew', 'close'],
      }));
    } else if (action === 'pause') {
      setSub((prev) => ({
        ...prev,
        allowed_actions: ['resume', 'close'],
      }));
    } else if (action === 'resume') {
      setSub((prev) => ({
        ...prev,
        allowed_actions: ['pause', 'renew', 'close'],
      }));
    } else if (action === 'close') {
      setSub((prev) => ({
        ...prev,
        status: 'closed',
        allowed_actions: [],
      }));
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link
            to="/staff/subscriptions"
            className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-600"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                {sub.subscription_number}
              </h1>
              <StatusBadge status={sub.status} kind="subscription" />
            </div>
            <p className="text-xs text-slate-500 mt-0.5">Customer: {sub.customer_name} ({sub.customer_email})</p>
          </div>
        </div>

        {/* Action Buttons governed by allowed_actions from API */}
        <div className="flex items-center gap-2">
          {sub.allowed_actions.includes('send_quote') && (
            <button
              onClick={() => handleAction('send_quote')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Send Quote</span>
            </button>
          )}

          {sub.allowed_actions.includes('confirm') && (
            <button
              onClick={() => handleAction('confirm')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-amber-600 text-white rounded-lg text-xs font-semibold hover:bg-amber-700"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Confirm</span>
            </button>
          )}

          {sub.allowed_actions.includes('activate') && (
            <button
              onClick={() => handleAction('activate')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 text-white rounded-lg text-xs font-semibold hover:bg-emerald-700"
            >
              <Play className="w-3.5 h-3.5" />
              <span>Activate</span>
            </button>
          )}

          {sub.allowed_actions.includes('pause') && (
            <button
              onClick={() => handleAction('pause')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-700 text-white rounded-lg text-xs font-semibold hover:bg-slate-800"
            >
              <Pause className="w-3.5 h-3.5" />
              <span>Pause</span>
            </button>
          )}

          {sub.allowed_actions.includes('resume') && (
            <button
              onClick={() => handleAction('resume')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 text-white rounded-lg text-xs font-semibold hover:bg-emerald-700"
            >
              <Play className="w-3.5 h-3.5" />
              <span>Resume</span>
            </button>
          )}

          {sub.allowed_actions.includes('renew') && (
            <button
              onClick={() => handleAction('renew')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-700"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Renew</span>
            </button>
          )}

          {sub.allowed_actions.includes('close') && (
            <button
              onClick={() => handleAction('close')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-rose-600 text-white rounded-lg text-xs font-semibold hover:bg-rose-700"
            >
              <XCircle className="w-3.5 h-3.5" />
              <span>Close</span>
            </button>
          )}
        </div>
      </div>

      {/* Lifecycle StatusStepper Component */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
          Subscription State Machine
        </h2>
        <StatusStepper status={sub.status} />
      </div>

      {/* Subscription Lines Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex justify-between items-center">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-700">Contracted Products & Lines</span>
          <span className="text-xs text-slate-500">Plan: {sub.plan_name}</span>
        </div>
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50/50 text-slate-600 border-b border-slate-200 font-semibold uppercase">
            <tr>
              <th className="p-4">Product / Variant</th>
              <th className="p-4">Quantity</th>
              <th className="p-4">Unit Price</th>
              <th className="p-4">Tax Rate</th>
              <th className="p-4 text-right">Line Total</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {sub.lines.map((l) => (
              <tr key={l.id}>
                <td className="p-4">
                  <div className="font-semibold text-slate-900">{l.product_name}</div>
                  {l.variant_name && <div className="text-[11px] text-indigo-600 mt-0.5">{l.variant_name}</div>}
                </td>
                <td className="p-4 font-mono">{l.quantity}</td>
                <td className="p-4 font-mono">${l.unit_price}</td>
                <td className="p-4 font-mono">{l.tax_rate}%</td>
                <td className="p-4 text-right font-mono font-bold text-slate-900">${l.line_total}</td>
              </tr>
            ))}
          </tbody>
          <tfoot className="bg-slate-50 font-bold border-t border-slate-200">
            <tr>
              <td colSpan={4} className="p-4 text-right uppercase text-slate-600">Total Contract Value:</td>
              <td className="p-4 text-right font-mono text-base text-indigo-700">${sub.total_amount}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
};
