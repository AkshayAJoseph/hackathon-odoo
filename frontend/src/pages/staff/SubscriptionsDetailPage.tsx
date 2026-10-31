import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  getSubscription,
  sendQuote,
  confirmSubscription,
  activateSubscription,
  pauseSubscription,
  resumeSubscription,
  renewSubscription,
  closeSubscription,
  Subscription,
} from '@/api';
import { StatusBadge, StatusStepper } from '@/components';
import { ArrowLeft, CheckCircle2, Play, Pause, XCircle, RefreshCw, Send, AlertCircle } from 'lucide-react';

export const SubscriptionsDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [sub, setSub] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const fetchSub = async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getSubscription(Number(id));
      setSub(data);
    } catch (e: any) {
      setError(e?.message ?? 'Failed to load subscription details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSub();
  }, [id]);

  const handleAction = async (action: string) => {
    if (!sub) return;
    setActionLoading(true);
    setError(null);
    setSuccessMsg(null);
    try {
      let updated: Subscription;
      if (action === 'send_quote') updated = await sendQuote(sub.id);
      else if (action === 'confirm') updated = await confirmSubscription(sub.id);
      else if (action === 'activate') updated = await activateSubscription(sub.id);
      else if (action === 'pause') updated = await pauseSubscription(sub.id);
      else if (action === 'resume') updated = await resumeSubscription(sub.id);
      else if (action === 'renew') updated = await renewSubscription(sub.id);
      else if (action === 'close') updated = await closeSubscription(sub.id);
      else throw new Error(`Unknown action: ${action}`);

      setSub(updated);
      setSuccessMsg(`Transition to '${updated.status}' succeeded!`);
    } catch (e: any) {
      setError(e?.data?.detail || e?.message || `Failed to execute ${action}`);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading && !sub) {
    return (
      <div className="p-12 text-center text-slate-500 text-xs flex flex-col items-center justify-center gap-2">
        <RefreshCw className="w-6 h-6 animate-spin text-indigo-600" />
        <span>Loading subscription from live database...</span>
      </div>
    );
  }

  if (!sub) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700">
        {error || 'Subscription not found.'}
        <div className="mt-3">
          <Link to="/staff/subscriptions" className="text-indigo-600 font-semibold hover:underline">
            &larr; Back to Subscriptions List
          </Link>
        </div>
      </div>
    );
  }

  const allowedActions = sub.allowed_actions || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link
            to="/staff/subscriptions"
            className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 cursor-pointer"
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
            <p className="text-xs text-slate-500 mt-0.5">
              Customer: {sub.customer_name} ({sub.customer_email})
            </p>
          </div>
        </div>

        {/* Action Buttons governed by allowed_actions from API */}
        <div className="flex items-center gap-2">
          {actionLoading && <RefreshCw className="w-4 h-4 animate-spin text-slate-500 mr-2" />}

          {allowedActions.includes('send_quote') && (
            <button
              onClick={() => handleAction('send_quote')}
              disabled={actionLoading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 disabled:opacity-50 cursor-pointer"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Send Quote</span>
            </button>
          )}

          {allowedActions.includes('confirm') && (
            <button
              onClick={() => handleAction('confirm')}
              disabled={actionLoading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-amber-600 text-white rounded-lg text-xs font-semibold hover:bg-amber-700 disabled:opacity-50 cursor-pointer"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Confirm</span>
            </button>
          )}

          {allowedActions.includes('activate') && (
            <button
              onClick={() => handleAction('activate')}
              disabled={actionLoading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 text-white rounded-lg text-xs font-semibold hover:bg-emerald-700 disabled:opacity-50 cursor-pointer"
            >
              <Play className="w-3.5 h-3.5" />
              <span>Activate</span>
            </button>
          )}

          {allowedActions.includes('pause') && (
            <button
              onClick={() => handleAction('pause')}
              disabled={actionLoading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-700 text-white rounded-lg text-xs font-semibold hover:bg-slate-800 disabled:opacity-50 cursor-pointer"
            >
              <Pause className="w-3.5 h-3.5" />
              <span>Pause</span>
            </button>
          )}

          {allowedActions.includes('resume') && (
            <button
              onClick={() => handleAction('resume')}
              disabled={actionLoading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 text-white rounded-lg text-xs font-semibold hover:bg-emerald-700 disabled:opacity-50 cursor-pointer"
            >
              <Play className="w-3.5 h-3.5" />
              <span>Resume</span>
            </button>
          )}

          {allowedActions.includes('renew') && (
            <button
              onClick={() => handleAction('renew')}
              disabled={actionLoading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-700 disabled:opacity-50 cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Renew</span>
            </button>
          )}

          {allowedActions.includes('close') && (
            <button
              onClick={() => handleAction('close')}
              disabled={actionLoading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-rose-600 text-white rounded-lg text-xs font-semibold hover:bg-rose-700 disabled:opacity-50 cursor-pointer"
            >
              <XCircle className="w-3.5 h-3.5" />
              <span>Close</span>
            </button>
          )}
        </div>
      </div>

      {successMsg && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-700 font-medium">
          {successMsg}
        </div>
      )}

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-600 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Lifecycle StatusStepper Component */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
          Subscription State Machine
        </h2>
        <StatusStepper status={sub.status} />
      </div>

      {/* Subscription Details Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs text-slate-500 uppercase tracking-wide block">Contract Start</span>
          <span className="text-sm font-semibold text-slate-800">{sub.current_period_start || 'N/A'}</span>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs text-slate-500 uppercase tracking-wide block">Contract End / Expiry</span>
          <span className="text-sm font-semibold text-slate-800">{sub.current_period_end || 'Never'}</span>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs text-slate-500 uppercase tracking-wide block">Plan</span>
          <span className="text-sm font-semibold text-indigo-700">{sub.plan_name}</span>
        </div>
      </div>

      {/* Subscription Lines Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex justify-between items-center">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-700">Contracted Products &amp; Lines</span>
          <span className="text-xs text-slate-500">{sub.plan_name}</span>
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
